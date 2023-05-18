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
    global publicKey, key
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
    print("Quote Generated.")
    return quote,b64publicKey

def getTokenFromAPD(quote,b64publicKey):
    url='https://authvertx.iudx.io/auth/v1/token'
    headers={'clientId': '73599b23-6550-4f01-882d-a2db75ba24ba', 'clientSecret': '15a874120135e4eed4782c8b51385649fee55562', 'Content-Type': 'application/json'}
    b64quote=base64.b64encode(quote)
    context={
                "sgxQuote":b64quote.decode("utf-8"),
                "publicKey":b64publicKey.decode("utf-8")
            }


    data={
            "itemId": "iisc.ac.in/89a36273d77dac4cf38114fca1bbe64392547f86/rs.iudx.io/nitro-enclave-test-rsg",
            "itemType": "resource_group",
            "role": "consumer",
            "context": context
         }
    dataJson=json.dumps(data)
    r= requests.post(url,headers=headers,data=dataJson)
    if(r.status_code==200):
        print("Quote Verified.")
        jsonResponse=r.json()
        token=jsonResponse.get('results').get('accessToken')
        return token
    else:
        print("Quote Verification failed.", r.text)
    
def getFileFromAAA(token):
    rs_headers={'Authorization': f'Bearer {token}'}
    rs_url='https://authenclave.iudx.io/resource_server/encrypted.store'
    rs=requests.get(rs_url,headers=rs_headers)
    if(rs.status_code==200):
        print("Token Authenticated.")
        loadedDict=pickle.loads(rs.content)
        return loadedDict

def decryptFile(loadedDict):
    b64encryptedKey=loadedDict["encryptedKey"]
    encData=loadedDict["encData"]
    fileName=loadedDict["tarName"]
    encryptedKey=base64.b64decode(b64encryptedKey)
    decryptor = PKCS1_OAEP.new(key)
    plainKey=decryptor.decrypt(encryptedKey)
    fernetKey = Fernet(plainKey)
    decryptedData = fernetKey.decrypt(encData)
    with open('decryptedData.tar.gz', "wb") as f:
        f.write(decryptedData)
    flag= tarfile.is_tarfile('decryptedData.tar.gz')
    tar=tarfile.open("decryptedData.tar.gz")
    tar.extractall('/inputdata')


             
def runYolo():
    output=subprocess.check_output("./yolov5/runyolo5.sh",shell=True,stderr=subprocess.STDOUT)
    print(output)


def main():
    quote, b64publicKey= generateQuote()    
    token=getTokenFromAPD(quote, b64publicKey)
    loadedDict=getFileFromAAA(token)
    decryptFile(loadedDict)
    runYolo()



if __name__ == "__main__":

    main()
