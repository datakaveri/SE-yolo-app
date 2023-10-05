import PPDX_SDK
import json
import subprocess
import time

def measure_memory_usage_subprocess():
    # Run the YOLO subprocess and obtain its PID
    p = subprocess.Popen(["./runyolo5.sh"], stdout=subprocess.PIPE)
    yolo_pid = p.pid
    
    max_memory_usage = 0  # Initialize max memory usage
    
    # Measure memory usage of the YOLO subprocess every 10 seconds
    while p.poll() is None:
        output = subprocess.check_output(["ps", "-o", "rss", "-p", str(yolo_pid)])
        memory_usage = int(output.decode().strip()) / 1024  # Convert to MB
        
        # Update maximum memory usage if needed
        if memory_usage > max_memory_usage:
            max_memory_usage = memory_usage
        
        print(f"Current memory usage of YOLO subprocess: {memory_usage:.2f} MB")
        time.sleep(10)  # Sleep for 10 seconds between measurements
    
    print(f"Maximum memory usage of YOLO subprocess: {max_memory_usage:.2f} MB")

def secureApp():
    #step 6
    PPDX_SDK.measure_memory_usage()
    with open("config.json") as file:
        config=json.load(file)
    address=config["enclaveManagerAddress"]
    rs_url=config["rs_url"]
    
    PPDX_SDK.profiling_steps("Enclave Booted", 6)
    PPDX_SDK.setState("Enclave booted","Enclave booted",6,10,address)

    #step 7
    PPDX_SDK.measure_memory_usage()
    quote, b64publicKey, key= PPDX_SDK.generateQuote()    
    token=PPDX_SDK.getTokenFromAPD(quote, b64publicKey, config)
    loadedDict=PPDX_SDK.getFileFromResourceServer(token, rs_url)
    PPDX_SDK.measure_memory_usage()
    PPDX_SDK.profiling_steps("Encrypted data recieved", 7)
    PPDX_SDK.setState("Encrypted data recieved","Encrypted data recieved",7,10,address)

    #step 8
    PPDX_SDK.measure_memory_usage()
    PPDX_SDK.decryptFile(loadedDict, key)
    PPDX_SDK.profiling_steps("Decryption completed", 8)
    PPDX_SDK.setState("Decryption completed","Decryption completed",8,10,address)
    PPDX_SDK.measure_memory_usage()

    PPDX_SDK.profiling_input()
    
    #step 9
    PPDX_SDK.measure_memory_usage()
    PPDX_SDK.profiling_steps("Executing application", 9)
    PPDX_SDK.setState("Executing application","Executing application",9,10,address)
    print("YOLO invoked...")
    #subprocess.run("./runyolo5.sh",shell=True,stderr=subprocess.STDOUT)
    measure_memory_usage_subprocess()
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


