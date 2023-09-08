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
import urllib.parse
import datetime

#generate quote to be sent to APD for verification
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

#APD verifies quote and releases token
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

#Send token to resource server for verification & get encrypted images  
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

#Decrypt images recieved using enclave's private key
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

#run YOLO application inside enclave
def runYolo():
    print("YOLO invoked...")
    subprocess.run("./runyolo5.sh",shell=True,stderr=subprocess.STDOUT)

#function to set state of enclave
def setState(title,description,step,maxSteps,address):
    state= {"title":title,"description":description,"step":step,"maxSteps":maxSteps}
    call_set_state_endpoint(state, address)

#function to call set state endpoint
def call_set_state_endpoint(state, address):
    #define enpoint url
    endpoint_url=urllib.parse.urljoin(address, '/enclave/setstate')

    #create Json payload
    payload = { "state": state }

    #create POST request
    r = requests.post(endpoint_url, json=payload)

    #print response
    print(r.text)

#main function
def main():
    with open("config.json") as file:
        config=json.load(file)
    address=config["enclaveManagerAddress"]
    data = {
        "steps": [],
        "totalTime": 0
    }
    timestamp_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    step6 = {
        "step6": {
            "timestamp": timestamp_str,
        }
    }
    data["steps"].append(step6)
    setState("Enclave booted","Enclave booted",6,10,address)
    quote, b64publicKey, key= generateQuote()    
    token=getTokenFromAPD(quote, b64publicKey, config)
    loadedDict=getFileFromResourceServer(token, config)
    timestamp_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    step7 = {
        "step7": {
            "timestamp": timestamp_str,
        }
    }
    data["steps"].append(step7)
    setState("Encrypted data recieved","Encrypted data recieved",7,10,address)
    decryptFile(loadedDict, key)
    timestamp_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    step8 = {
        "step8": {
            "timestamp": timestamp_str,
        }
    }
    data["steps"].append(step8)
    setState("Decryption completed","Decryption completed",8,10,address)
    setState("Executing application","Executing application",9,10,address)
    timestamp_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    step9 = {
        "step9": {
            "timestamp": timestamp_str,
        }
    }
    data["steps"].append(step9)
    runYolo()
    timestamp_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    step10 = {
        "step10": {
            "timestamp": timestamp_str,
        }
    }
    data["steps"].append(step10)

    with open("profiling.json", "w") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    main()
