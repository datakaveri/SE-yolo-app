#!/usr/bin/env python3
import os 
import json

input_dir = "runs/detect/exp2/labels/"
output_file = "labels.json"
input_dir2 = "./runOutput.txt"

with open(input_dir2, "r") as runOutput_file:
    outputContent = runOutput_file.read()

output_data = {
    "inference": {
        "inference": {
            "runOutput": outputContent,
            "labels": []
        }
    }
}

for file_name in os.listdir(input_dir):
    if file_name.endswith(".txt"):
        file_path = os.path.join(input_dir, file_name)
        
        with open(file_path, "r") as input_file:
            content = input_file.read()
            
        output_data["inference"]["inference"]["labels"].append({
            "filename": file_name,
            "content": content
        })

with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=4)