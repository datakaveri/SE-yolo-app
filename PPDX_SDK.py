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
        print(token)
        return token
    else:
        print("Quote verification failed.", r.text)
        sys.exit() 

#Send token to resource server for verification & get encrypted images  
def getFileFromResourceServer(token,rs_url):
    rs_headers={'Authorization': f'Bearer {token}'}
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

#profiling function: timestamp, memory & CPU
def profiling_steps(description, stepno):
    with open("profiling.json", "r") as file:
        data = json.load(file)
    timestamp_str = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    step = {
        "step"+str(stepno): {
            "description": description,
            "timestamp": timestamp_str
        }   
    }
    data["stepsProfile"].append(step)
    with open("profiling.json", "w") as file:
        json.dump(data, file, indent=4)

#profiling: input data
def profiling_input():
    with open("profiling.json", "r") as file:
        data = json.load(file)
    extracted_directory = '/inputdata'
    files_in_directory = os.listdir(extracted_directory)
    image_extensions = ['.jpg', '.jpeg']
    image_count = 0
    for file_name in files_in_directory:
        if any(file_name.lower().endswith(ext) for ext in image_extensions):
            image_count += 1

    data["input"]["images"] = image_count
    with open("profiling.json", "w") as file:
        json.dump(data, file, indent=4)

def profiling_totalTime():
    with open("profiling.json", "r") as file:
        data = json.load(file)
    timestamp_step1 = None
    timestamp_step10 = None

    # Iterate through the list of steps to find "step1" and "step10"
    for step in data["stepsProfile"]:
        step_label = list(step.keys())[0]  # Extract the step label, e.g., "step1"
        step_data = list(step.values())[0]  # Extract the step data

        if step_label == "step1":
            timestamp_step1 = step_data["timestamp"]
        elif step_label == "step10":
            timestamp_step10 = step_data["timestamp"]

    # Check if both timestamps were found
    if timestamp_step1 is not None and timestamp_step10 is not None:
        # Convert timestamps to datetime objects (you'll need to import datetime)
        from datetime import datetime
        time_format = "%Y-%m-%d %H:%M:%S.%f"
        dt_step1 = datetime.strptime(timestamp_step1, time_format)
        dt_step10 = datetime.strptime(timestamp_step10, time_format)

        # Calculate the time difference in seconds
        time_difference_seconds = (dt_step10 - dt_step1).total_seconds()

        # Convert seconds to minutes and seconds
        minutes = int(time_difference_seconds // 60)
        seconds = int(time_difference_seconds % 60)

        # Add the total time to the data dictionary
        data["totalTime"] = {"minutes": minutes, "seconds": seconds}

        # Write the updated data back to "profiling.json"
        with open("profiling.json", "w") as output_file:
            json.dump(data, output_file, indent=4)
#Chunk Functions:

def dataChunkN(n, url, access_token, key):
    loadedDict=getChunkFromResourceServer(n, url, access_token)
    if loadedDict:
        decryptChunk(loadedDict, key)
        return 1
    else:
        return 0 
    
def getChunkFromResourceServer (n,url,token):
    print("Getting chunk from the resource server..")
    rs_headers={'Authorization': f'Bearer {token}'}
    rs_url = f"{url}{n}"
    print(rs_url)
    rs=requests.get(rs_url,headers=rs_headers)
    if(rs.status_code==200):
        print("Token authenticated and Encrypted images recieved.")
        loadedDict=pickle.loads(rs.content)
        print(loadedDict.keys())
        return loadedDict
    else:
        print(rs.text)
        return None

def decryptChunk(loadedDict,key):
    print("Decrypting chunk..")
    b64encryptedKey=loadedDict["encryptedKey"]
    encData=loadedDict["encData"]
    encryptedKey=base64.b64decode(b64encryptedKey)
    decryptor = PKCS1_OAEP.new(key)
    plainKey=decryptor.decrypt(encryptedKey)
    print("Symmetric key decrypted using the enclave's private RSA key.")
    fernetKey = Fernet(plainKey)
    decryptedData = fernetKey.decrypt(encData)
    print(os.listdir("../"))
    with open('../inputdata/outfile.gz', "wb") as f:
        f.write(decryptedData)
    print("Chunk decrypted and saved in /inputdata/outfile.gz.")