import PPDX_SDK
import json
import subprocess

def secureApp():
    with open("config.json") as file:
        config=json.load(file)
    address=config["enclaveManagerAddress"]
    rs_url=config["rs_url"]

    PPDX_SDK.profiling_steps("Enclave Booted", 6)
    PPDX_SDK.setState("Enclave booted","Enclave booted",6,10,address)

    quote, b64publicKey, key= PPDX_SDK.generateQuote()    
    token=PPDX_SDK.getTokenFromAPD(quote, b64publicKey, config)
    loadedDict=PPDX_SDK.getFileFromResourceServer(token, rs_url)

    PPDX_SDK.profiling_steps("Encrypted data recieved", 7)
    PPDX_SDK.setState("Encrypted data recieved","Encrypted data recieved",7,10,address)

    PPDX_SDK.decryptFile(loadedDict, key)

    PPDX_SDK.profiling_steps("Decryption completed", 8)
    PPDX_SDK.setState("Decryption completed","Decryption completed",8,10,address)

    PPDX_SDK.profiling_input()
    
    PPDX_SDK.profiling_steps("Executing application", 9)
    PPDX_SDK.setState("Executing application","Executing application",9,10,address)
    
    print("YOLO invoked...")
    subprocess.run("./runyolo5.sh",shell=True,stderr=subprocess.STDOUT)
    print("YOLO completed.")

with open("config.json", "r") as file:
        config= json.load(file)
address=config["enclaveManagerAddress"]

print("Now I am starting...")
secureApp()
PPDX_SDK.profiling_steps("Execution Completed", 10)
PPDX_SDK.profiling_totalTime()
PPDX_SDK.setState("Execution Complete","Execution Complete",10,10,address)
print("Now I am done..")