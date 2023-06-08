#!/usr/bin/env python3
import os 
import json

input_dir="runs/detect/exp/labels/"
output_file="labels.json"

with open(output_file, "a") as f:
    f.write("[")

first_file=True
for file_name in os.listdir(input_dir):
    if file_name.endswith(".txt"):
        file_path=os.path.join(input_dir,file_name)
    if not first_file:
        with open(output_file,"a") as f:
            f.write(",")

    with open(file_path, "r") as input_file, open(output_file,"a") as f:
        content= input_file.read()
        f.write(json.dumps({"filename": file_name, "content": content}))

    first_file=False

with open(output_file, "a") as f:
    f.write("]")
