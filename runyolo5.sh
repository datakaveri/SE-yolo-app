#!/bin/bash
echo started..
python ./yolov5/detect.py --source '/app/input/*.*' --weights ./yolov5/yolov5x.pt --save-txt --nosave  > ./yolov5/runOutput.txt 2>&1 
cd ./yolov5/

echo Saving labels..

python3 ./savelabels.py
cd ..
echo Labels saved in yolov5/labels.json