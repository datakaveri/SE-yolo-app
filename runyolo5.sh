#!/bin/bash
env/bin/python ./yolov5/detect.py --source './inputdata/*.*' --weights ./yolov5/yolov5x.pt --save-txt --nosave
cd ./yolov5/

echo Saving labels..

../env/bin/python ./savelabels.py

echo Labels saved in yolov5/labels.json
ls

