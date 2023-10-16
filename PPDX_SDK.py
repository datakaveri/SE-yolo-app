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
import psutil

#generate quote to be sent to APD for verification
def generateQuote():
    key = RSA.generate(2048)
    publicKey=key.publickey().export_key(format='DER')
    #print("Public key generated: " ,publicKey)
    #privateKey=key.export_key(format='DER')
    b64publicKey=base64.b64encode(publicKey)
    sha= hashlib.sha512(publicKey).hexdigest()
    shaBytes=bytearray.fromhex(sha)
    with open("/dev/attestation/user_report_data", "wb") as f:
        f.write(shaBytes)
    with open("/dev/attestation/quote", "rb") as f:
        quote = f.read()
    print("Quote generated.")
    #print("Quote: ",quote)
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
        #print(token)
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

#profiling function: timestamp, memory usage, step description
def profiling_steps(description, stepno, memory):
    with open("profiling.json", "r") as file:
        data = json.load(file)
    timestamp_str = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    memory_mb = f"{memory} MB"
    step = {
        "step"+str(stepno): {
            "description": description,
            "timestamp": timestamp_str,
            "memory_usage": memory_mb
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

def profiling_totalTimeandMemory():
    print("Profiling total time and memory usage...")
    with open("profiling.json", "r") as file:
        data = json.load(file)
    timestamp_step1 = None
    timestamp_step10 = None
    total_memory_usage = 0  

    for i in range(1, 9):
        step_label = f"step{i}"
        step_data = next((step for step in data["stepsProfile"] if step.get(step_label)), None)
        if(i==1):
            timestamp_step1 = step_data[step_label]["timestamp"]
        if step_data:
            memory_usage_str = step_data[step_label]["memory_usage"]
            memory_usage_value = float(memory_usage_str.split()[0])
            total_memory_usage += memory_usage_value
            
    from datetime import datetime
    timestamp_step10=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    data["totalMemory"] = f"{total_memory_usage} MB"

    # Check if both timestamps were found
    if timestamp_step1 is not None and timestamp_step10 is not None:
        # Convert timestamps to datetime objects (you'll need to import datetime)
        from datetime import datetime
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        
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

    print("Final Profiling completed.")


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

def measure_memory_usage():
    process = psutil.Process()
    memory = process.memory_info().rss / (1024 * 1024)  # in MB
    return memory