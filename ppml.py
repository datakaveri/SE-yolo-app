#!/usr/bin/env python3

import os
import sys
import Crypto
from Crypto.PublicKey import RSA
import base64
import hashlib
import json
import requests
import _pickle as pickle
from Crypto.Cipher import PKCS1_OAEP
from cryptography.fernet import Fernet
import tarfile
import subprocess

def generateQuote():
    key = RSA.generate(2048)
    publicKey=key.publickey().export_key(format='DER')
    privateKey=key.export_key(format='DER')
    b64publicKey=base64.b64encode(publicKey)
    sha= hashlib.sha512(publicKey).hexdigest()
    shaBytes=bytearray.fromhex(sha)
    with open("/dev/attestation/user_report_data", "wb") as f:
        f.write(shaBytes)
    with open("/dev/attestation/quote", "rb") as f:
        quote = f.read()
    print("Quote generated.")
    return quote,b64publicKey, key

def getTokenFromAPD(quote,b64publicKey,config):
    apd_url=config["apd_url"]
    headers={'clientId': config["clientId"], 'clientSecret': config["clientSecret"], 'Content-Type': config["Content-Type"]}
    b64quote=base64.b64encode(quote)
    context={
                "sgxQuote":b64quote.decode("utf-8"),
                "publicKey":b64publicKey.decode("utf-8")
            }


    data={
            "itemId": config["itemId"],
            "itemType": config["itemType"],
            "role": config["role"],
            "context": context
         }
    dataJson=json.dumps(data)
    r= requests.post(apd_url,headers=headers,data=dataJson)
    if(r.status_code==200):
        print("Quote verified and Token recieved.")
        jsonResponse=r.json()
        token=jsonResponse.get('results').get('accessToken')
        return token
    else:
        print("Quote verification failed.", r.text)
        sys.exit() 
def getFileFromResourceServer(token,config):
    rs_headers={'Authorization': f'Bearer {token}'}
    rs_url=config["rs_url"]
    rs=requests.get(rs_url,headers=rs_headers)
    if(rs.status_code==200):
        print("Token authenticated and Encrypted images recieved.")
        loadedDict=pickle.loads(rs.content)
        return loadedDict
    else:
        print("Token authentication failed.",rs.text)
        sys.exit()

def decryptFile(loadedDict,key):
    b64encryptedKey=loadedDict["encryptedKey"]
    encData=loadedDict["encData"]
    fileName=loadedDict["tarName"]
    encryptedKey=base64.b64decode(b64encryptedKey)
    decryptor = PKCS1_OAEP.new(key)
    plainKey=decryptor.decrypt(encryptedKey)
    print("Symmetric key decrypted using the enclave's private RSA key.")
    fernetKey = Fernet(plainKey)
    decryptedData = fernetKey.decrypt(encData)
    with open('/tmp/decryptedData.tar.gz', "wb") as f:
        f.write(decryptedData)
    tar=tarfile.open("/tmp/decryptedData.tar.gz")
    tar.extractall('/inputdata')
    print("Images decrypted.",os.listdir('/inputdata'))


def runYolo():
    print("YOLO invoked...")
    output=subprocess.run("./runyolo5.sh",shell=True,stderr=subprocess.STDOUT)


def setState(title,description,step,maxSteps):
    state= {"title":title,"description":description,"step":step,"maxSteps":maxSteps}
    call_set_state_endpoint(state)


def call_set_state_endpoint(state):
    #define enpoint url
    endpoint_url="http://192.168.1.199:4000/enclave/setstate"

    #create Json payload
    payload = { "state": state }

    #create POST request
    r = requests.post(endpoint_url, json=payload)

    #print response
    print(r.text)


def main():
    with open("config.json") as file:
        config=json.load(file)
    setState("Enclave booted","Enclave booted",6,10)
    quote, b64publicKey, key= generateQuote()    
    token=getTokenFromAPD(quote, b64publicKey, config)
    loadedDict=getFileFromResourceServer(token, config)
    setState("Encrypted data recieved","Encrypted data recieved",7,10)
    decryptFile(loadedDict, key)
    setState("Decryption completed","Decryption completed",8,10)
    setState("Executing application","Executing application",9,10)
    runYolo()
    setState("Execution completed","Execution completed",10,10)



if __name__ == "__main__":

    main()
