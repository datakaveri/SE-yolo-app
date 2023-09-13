import PPDX_SDK
import json
import datetime
import os

def secureApp():
    with open("config.json") as file:
        config=json.load(file)
    address=config["enclaveManagerAddress"]

    data = {
        "input":{
            "images": 0
        },
        "stepsProfile": [],
        "totalTime": 0
    }
    
    timestamp_str = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    step6 = {
        "step6": {
            "description": "Enclave booted",
            "timestamp": timestamp_str
        }
    }
    data["stepsProfile"].append(step6)
    PPDX_SDK.setState("Enclave booted","Enclave booted",6,10,address)

    quote, b64publicKey, key= PPDX_SDK.generateQuote()    
    token=PPDX_SDK.getTokenFromAPD(quote, b64publicKey, config)
    loadedDict=PPDX_SDK.getFileFromResourceServer(token, config)

    #input data
    extracted_directory = '/inputdata'
    files_in_directory = os.listdir(extracted_directory)
    image_extensions = ['.jpg', '.jpeg']
    image_count = 0
    for file_name in files_in_directory:
        if any(file_name.lower().endswith(ext) for ext in image_extensions):
            image_count += 1

    data["input"]["images"] = image_count

    timestamp_str = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    step7 = {
        "step7": {
            "description": "Encrypted data recieved",
            "timestamp": timestamp_str
        }
    }
    data["stepsProfile"].append(step7)
    PPDX_SDK.setState("Encrypted data recieved","Encrypted data recieved",7,10,address)

    PPDX_SDK.decryptFile(loadedDict, key)
    timestamp_str = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    step8 = {
        "step8": {
            "description": "Decryption completed",
            "timestamp": timestamp_str
        }
    }
    data["stepsProfile"].append(step8)
    PPDX_SDK.setState("Decryption completed","Decryption completed",8,10,address)

    
    timestamp_str = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    step9 = {
        "step9": {
            "description": "Executing application",
            "timestamp": timestamp_str
        }
    }
    data["stepsProfile"].append(step9)
    PPDX_SDK.setState("Executing application","Executing application",9,10,address)
    PPDX_SDK.runYolo()
    
    timestamp_str = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    step10 = {
        "step10": {
            "description": "Execution Complete",
            "timestamp": timestamp_str
        }
    }
    data["stepsProfile"].append(step10)

    with open("profiling.json", "w") as file:
        json.dump(data, file, indent=4)

    PPDX_SDK.setState("Execution complete","Execution Complete",10,10,address)

