#!/bin/bash
python3 ./yolov5/detect.py --source './inputdata/*.*' --weights ./yolov5/yolov5x.pt 
: '--save-txt

cd ./yolov5/

echo Saving labels..

./savelabels.sh
'
