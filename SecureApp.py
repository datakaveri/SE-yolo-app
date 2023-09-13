import PPDX_SDK
import json
import subprocess

def secureApp():
    with open("config.json") as file:
        config=json.load(file)
    address=config["enclaveManagerAddress"]
    rs_url=config["rs_url"]

    data = {
        "input":{
            "images": 0
        },
        "stepsProfile": [],
        "totalTime": 0
    }

    PPDX_SDK.profiling_endpoint("Enclave Booted", 6, data)
    PPDX_SDK.setState("Enclave booted","Enclave booted",6,10,address)

    quote, b64publicKey, key= PPDX_SDK.generateQuote()    
    token=PPDX_SDK.getTokenFromAPD(quote, b64publicKey, config)
    loadedDict=PPDX_SDK.getFileFromResourceServer(token, rs_url)

    PPDX_SDK.profiling_endpoint("Encrypted data recieved", 7, data)
    PPDX_SDK.setState("Encrypted data recieved","Encrypted data recieved",7,10,address)

    PPDX_SDK.decryptFile(loadedDict, key)

    PPDX_SDK.profiling_endpoint("Decryption completed", 8, data)
    PPDX_SDK.setState("Decryption completed","Decryption completed",8,10,address)

    PPDX_SDK.profiling_input(data)
    
    PPDX_SDK.profiling_endpoint("Executing application", 9, data)
    PPDX_SDK.setState("Executing application","Executing application",9,10,address)
    
    print("YOLO invoked...")
    subprocess.run("./runyolo5.sh",shell=True,stderr=subprocess.STDOUT)
    print("YOLO completed.")
    
    PPDX_SDK.profiling_endpoint("Execution Completed", 10, data)