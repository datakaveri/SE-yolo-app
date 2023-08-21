#!/bin/bash
source setState.sh

#calling setState endpoint (step 3)
call_setstate_endpoint "Setting up the virtual environment(if not present) & installing dependencies for application" 10 3 "Setting up the environment"
echo "setting up environment"

#virtual environment 
DIR=/home/iudx/.env/sgx-yolo-app
if [ -d "$DIR" ];
then
    echo 'Virtual environment exists'
else
    echo 'Creating virtual environment'
    python3 -m venv $DIR
fi

#source the virtual environment
. $DIR/bin/activate

#install dependencies
pip3 install -r requirements.txt -r yolov5/requirements.txt

set -x # to echo the command being executed

cp /home/iudx/yoloHelper/config.json ./

cp /home/iudx/yoloHelper/yolov5x.pt ./yolov5/

cp /home/iudx/yoloHelper/runOutput.txt ./yolov5/

#calling setState endpoint (step 4)
call_setstate_endpoint "Building manifest" 10 4 "Building manifest"
make clean
make SGX=1 RA_TYPE=dcap