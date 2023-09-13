import SecureApp
import json
import PPDX_SDK

with open("config.json", "r") as file:
        config= json.load(file)
address=config["enclaveManagerAddress"]

print("Now I am starting...")
SecureApp.secureApp()
print("Now I am done..")
PPDX_SDK.setState("Execution Complete","Execution Complete",10,10,address)
