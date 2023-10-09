import PPDX_SDK
import json
import subprocess
import time
import psutil

def measure_memory_usage(pid):
    try:
        # Get the process associated with the given PID
        process = psutil.Process(pid)
        # Measure memory usage using psutil
        memory_info = process.memory_info()
        # Convert bytes to megabytes (MB)
        total_memory_usage = memory_info.rss / (1024 * 1024)  # Total memory usage in MB (using RSS)
        return total_memory_usage
    except psutil.NoSuchProcess:
        return None

def secureApp():
    PPDX_SDK.measure_memory_usage()
    with open("config.json") as file:
        config=json.load(file)
    address=config["enclaveManagerAddress"]
    rs_url=config["rs_url"]
    
    #step 6
    PPDX_SDK.profiling_steps("Generating quote & obtaining token", 6)
    PPDX_SDK.setState("Generating quote & obtaining token","Generating quote & obtaining token",6,10,address)
    PPDX_SDK.measure_memory_usage()
    quote, b64publicKey, key= PPDX_SDK.generateQuote()    
    token=PPDX_SDK.getTokenFromAPD(quote, b64publicKey, config)
    PPDX_SDK.measure_memory_usage()

    #step 7
    PPDX_SDK.measure_memory_usage()
    PPDX_SDK.profiling_steps("Getting encrypted data from resource server", 7)
    PPDX_SDK.setState("Getting encrypted data from resource server","Getting encrypted data from resource server",7,10,address)
    loadedDict=PPDX_SDK.getFileFromResourceServer(token, rs_url)
    PPDX_SDK.measure_memory_usage()
    

    #step 8
    PPDX_SDK.measure_memory_usage()
    PPDX_SDK.profiling_steps("Decrypting files", 8)
    PPDX_SDK.setState("Decrypting files","Decrypting files",8,10,address)
    PPDX_SDK.decryptFile(loadedDict, key)
    PPDX_SDK.measure_memory_usage()

    PPDX_SDK.profiling_input()
    
    #step 9
    PPDX_SDK.measure_memory_usage()
    PPDX_SDK.profiling_steps("Executing application", 9)
    PPDX_SDK.setState("Executing application","Executing application",9,10,address)
    print("YOLO invoked...")
    #subprocess.run("./runyolo5.sh",shell=True,stderr=subprocess.STDOUT)
    process = subprocess.Popen(["./runyolo5.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    max_memory=0
    pid = process.pid
    memory_data = []
    print(f"Process ID: {pid}")
    while process.poll() is None:
        # Measure memory usage using the PID
        print("Measuring memory usage...")
        memory_usage= measure_memory_usage(pid)

        if memory_usage is not None:
            memory_data.append(memory_usage)

        # Write memory data to a JSON file
        with open('memory_data.json', 'w') as json_file:
            json.dump(memory_usage, json_file)
        print("Memory data written to memory_data.json.")

        # Sleep for 10 seconds
        print("Sleeping for 10 seconds...")
        time.sleep(10)

    # Print the maximum memory usage
    #print(f"Maximum memory usage: {max_memory:.2f} MB")
    print("Process finished. Memory data written to memory_data.json.")
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


