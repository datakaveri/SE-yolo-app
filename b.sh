#!/bin/bash
chmod +x b.sh
chmod a+x ./setState.sh
. ./setState.sh
. ./profilingStep.sh

cp /home/iudx/sgx-enclave-manager/profiling.json ./


set -x # to echo the command being executed

cp ~/yoloHelper/config.json ./
cp ~/yoloHelper/yolov5x.pt ./yolov5/
cp ~/yoloHelper/runOutput.txt ./yolov5/


