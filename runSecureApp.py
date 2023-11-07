import PPDX_SDK
import SecureApp
import json
import sys

def runSecureApp(memory_usage_step5_start):
    with open("config.json") as file:
        config=json.load(file)
    address=config["enclaveManagerAddress"]
    rs_url=config["rs_url"]
    
    #step 5 ends
    print("step 5 ends")
    mem_end=PPDX_SDK.measure_memory_usage()
    print("Memory usage: ",mem_end," MB")
    total_mem=mem_end-memory_usage_step5_start
    print("Step 5 memory usage: ",total_mem," MB")
    PPDX_SDK.profiling_steps("Starting Application in SGX Enclave", 5, total_mem)

    mem_end,mem_start,total_mem=0,0,0

    #step 6
    print("step 6")
    mem_start=PPDX_SDK.measure_memory_usage()
    print("Memory usage: ",mem_start," MB")
    PPDX_SDK.setState("Generating quote & obtaining token","Generating quote & obtaining token",6,10,address)

    quote, b64publicKey, key= PPDX_SDK.generateQuote()    
    token=PPDX_SDK.getTokenFromAPD(quote, b64publicKey, config)

    #step 6 ends
    print("step 6 ends")
    mem_end=PPDX_SDK.measure_memory_usage()
    print("Memory usage: ",mem_end," MB")
    total_mem=mem_end-mem_start
    print("Step 6 memory usage: ",total_mem," MB")
    PPDX_SDK.profiling_steps("Generating quote & obtaining token", 6, total_mem)

    mem_end,mem_start,total_mem=0,0,0

    #step 7
    print("step 7")
    mem_start=PPDX_SDK.measure_memory_usage()
    print("Memory usage: ",mem_start," MB")
    PPDX_SDK.setState("Getting encrypted data from resource server","Getting encrypted data from resource server",7,10,address)

    loadedDict=PPDX_SDK.getFileFromResourceServer(token, rs_url)

    #step 7 ends
    print("step 7 ends")
    mem_end=PPDX_SDK.measure_memory_usage()
    print("Memory usage: ",mem_end," MB")
    total_mem=mem_end-mem_start
    print("Step 7 memory usage: ",total_mem," MB")
    PPDX_SDK.profiling_steps("Getting encrypted data from resource server", 7, total_mem)

    mem_end,mem_start,total_mem=0,0,0

    #step 8
    print("step 8")
    mem_start=PPDX_SDK.measure_memory_usage()
    print("Memory usage: ",mem_start," MB")
    PPDX_SDK.setState("Decrypting files","Decrypting files",8,10,address)

    PPDX_SDK.decryptFile(loadedDict, key)
    PPDX_SDK.profiling_input()    #input file size/number of files

    #step 8 ends
    print("step 8 ends")
    mem_end=PPDX_SDK.measure_memory_usage()
    print("Memory usage: ",mem_end," MB")
    total_mem=mem_end-mem_start
    print("Step 8 memory usage: ",total_mem," MB")
    PPDX_SDK.profiling_steps("Decrypting files", 8, total_mem)
    
    mem_end,mem_start,total_mem=0,0,0

    #step 9
    print("step 9")
    mem_start=PPDX_SDK.measure_memory_usage()
    print("Memory usage: ",mem_start," MB")
    PPDX_SDK.setState("Executing application","Executing application",9,10,address)

    SecureApp.secureApp()

    #step 9 ends
    print("step 9 ends")
    mem_end=PPDX_SDK.measure_memory_usage()
    print("Memory usage: ",mem_end," MB")
    total_mem=mem_end-mem_start
    print("Step 9 memory usage: ",total_mem," MB")
    PPDX_SDK.profiling_steps("Executing application", 9, total_mem)
    
    mem_end,mem_start,total_mem=0,0,0

if len(sys.argv) > 1:
        memory_usage_step5_start = float(sys.argv[1])
        print("Memory usage at start of step 5: ",memory_usage_step5_start," MB")

with open("config.json", "r") as file:
        config= json.load(file)
address=config["enclaveManagerAddress"]

print("Now I am starting...")
runSecureApp(memory_usage_step5_start)
PPDX_SDK.profiling_steps("Execution Completed", 10, 0)
PPDX_SDK.profiling_totalTimeandMemory()
PPDX_SDK.setState("Execution Complete","Execution Complete",10,10,address)
print("Now I am done..")


