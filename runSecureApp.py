import PPDX_SDK
import SecureApp
import json

def runSecureApp():
    with open("config.json") as file:
        config=json.load(file)
    address=config["enclaveManagerAddress"]
    rs_url=config["rs_url"]
    
    #step 6
    print("step 6")
    PPDX_SDK.setState("Generating quote & obtaining token","Generating quote & obtaining token",6,10,address)
    PPDX_SDK.profiling_steps("Generating quote & obtaining token", 6)

    quote, b64publicKey, key= PPDX_SDK.generateQuote()    
    token=PPDX_SDK.getTokenFromAPD(quote, b64publicKey, config)

    #step 7
    print("step 7")
    PPDX_SDK.setState("Getting encrypted data from resource server","Getting encrypted data from resource server",7,10,address)
    PPDX_SDK.profiling_steps("Getting encrypted data from resource server", 7)

    loadedDict=PPDX_SDK.getFileFromResourceServer(token, rs_url)

    #step 8
    print("step 8")
    PPDX_SDK.setState("Decrypting files","Decrypting files",8,10,address)
    PPDX_SDK.profiling_steps("Decrypting files", 8)

    PPDX_SDK.decryptFile(loadedDict, key)
    PPDX_SDK.profiling_inputImages()    #input file size/number of files

    #step 9
    print("step 9")
    PPDX_SDK.setState("Executing application","Executing application",9,10,address)
    PPDX_SDK.profiling_steps("Executing application", 9)
    
    SecureApp.secureApp()

with open("config.json", "r") as file:
        config= json.load(file)
address=config["enclaveManagerAddress"]

print("Now I am starting...")
runSecureApp()
PPDX_SDK.profiling_steps("Execution Completed", 10)
PPDX_SDK.profiling_totalTime()
PPDX_SDK.setState("Execution Complete","Execution Complete",10,10,address)
print("Now I am done..")


