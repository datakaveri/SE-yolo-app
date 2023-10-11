import PPDX_SDK
import json
import subprocess
import sys

'''
def measure_memory_usage():
    memory_info = psutil.virtual_memory()
    total_memory_usage = memory_info.percent  # Total memory usage percentage
    return total_memory_usage

def measure_memory_usage(process):
    try:
        # Get the process associated with the given PID
        #process = psutil.Process(pid)
        #process_info = psutil.Process(process.pid)
        # Measure memory usage using psutil
        memory_info = process.memory_info() # in bytes  
        # Convert bytes to megabytes (MB)
        total_memory_usage = memory_info.rss / (1024 * 1024)  # Total memory usage in MB (using RSS)
        return total_memory_usage
    except psutil.NoSuchProcess or psutil.AccessDenied :
        return None
'''

def secureApp():

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
    
    #step 9
    print("step 9")
    mem_start=PPDX_SDK.measure_memory_usage()
    print("Memory usage: ",mem_start," MB")
    PPDX_SDK.setState("Executing application","Executing application",9,10,address)

    print("YOLO invoked...")
    subprocess.run("./runyolo5.sh",shell=True,stderr=subprocess.STDOUT)
    print("YOLO completed.")

    #step 9 ends
    print("step 9 ends")
    mem_end=PPDX_SDK.measure_memory_usage()
    print("Memory usage: ",mem_end," MB")
    total_mem=mem_end-mem_start
    print("Step 9 memory usage: ",total_mem," MB")
    PPDX_SDK.profiling_steps("Executing application", 9, total_mem)
    

    '''
    process = subprocess.Popen(["./runyolo5.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    max_memory=0
    pid = process.pid
    memory_data = []
    print(f"Process ID: {pid}")
    while process.poll() is None:
        # Measure memory usage using the PID
        print("Measuring memory usage...")
        memory_usage= measure_memory_usage(process)

        if memory_usage is not None:
            print(f"Memory usage: {memory_usage:.2f} MB")
            memory_data.append({"timestamp": time.time(), "memory_usage_mb": memory_usage})
        else:
            print("Memory usage: N/A")

        # Write memory data to a JSON file
        with open('memory_data.json', 'w') as json_file:
            json.dump(memory_data, json_file)
        print("Memory data written to memory_data.json.")

        # Sleep for 10 seconds
        print("Sleeping for 10 seconds...")
        time.sleep(10)

    # Print the maximum memory usage
    #print(f"Maximum memory usage: {max_memory:.2f} MB")
    print("Process finished. Memory data written to memory_data.json.")
    '''


if len(sys.argv) > 1:
        memory_usage_step5_start = float(sys.argv[1])

with open("config.json", "r") as file:
        config= json.load(file)
address=config["enclaveManagerAddress"]

print("Now I am starting...")
secureApp()
PPDX_SDK.profiling_steps("Execution Completed", 10, 0)
PPDX_SDK.profiling_totalTime()
PPDX_SDK.setState("Execution Complete","Execution Complete",10,10,address)
print("Now I am done..")


