#!/bin/bash
python ./yolov5/detect.py --source './examples/sample_input_images/*.*' --weights ./yolov5/yolov5x.pt --save-txt --nosave  > ./yolov5/runOutput.txt 2>&1 
cd ./yolov5/

echo Saving labels..

python3 ./savelabels.py

echo Labels saved in yolov5/labels.json

