import subprocess

def secureApp():
    print("YOLO invoked...")
    subprocess.run("./runyolo5.sh",shell=True,stderr=subprocess.STDOUT)
    print("YOLO completed.")