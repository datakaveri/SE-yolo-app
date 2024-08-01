import subprocess
import json

def secureApp():
    print("YOLO invoked...")
    subprocess.run("./runyolo5.sh",shell=True,stderr=subprocess.STDOUT)
    print("Writing in output file")
    outputfile = "output/results.json"
    originalfile = "yolov5/labels.json"
    try:
        with open(originalfile, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: file1 does not exist.")
    try:
        with open(outputfile, 'w') as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        print(f"Error: file2 does not exist.")
    print("YOLO completed.")


secureApp()