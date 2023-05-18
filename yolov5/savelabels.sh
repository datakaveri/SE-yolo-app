#!/bin/bash

# Set the input and output directories
input_dir="/yolov5/runs/detect/exp/labels/"
output_file="/yolov5/labels.json"

# Create an empty output file
> "$output_file"

# Add the opening square bracket of the JSON array
echo "[" >> "$output_file"

# Loop through each text file in the input directory
first_file=true
for file in "$input_dir"/*.txt; do
  # Get the name of the input file
  filename=$(basename "$file")
  
  # Add a comma before each object, except for the first one
  if $first_file ; then
    first_file=false
  else
    echo "," >> "$output_file"
  fi
  
  # Add the object to the output file
  echo "{ \"filename\": \"$filename\", \"content\": \"" >> "$output_file"
  cat "$file" >> "$output_file"
  echo "\" }" >> "$output_file"
done

# Add the closing square bracket of the JSON array
echo "]" >> "$output_file"

