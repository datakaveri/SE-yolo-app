#!/bin/bash

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

cp /home/iudx/yoloHelper/inference.txt ./yolov5/

#gramine-sgx terminate-enclave --all
#sh /home/iudx/sgx-enclave-manager/cl.sh

#./memsmall.sh

echo 'Building Gramine SGX'
echo 'Removing all files initially present'
make clean

echo 'Setting Remote Attestation type as DCAP'
make SGX=1 RA_TYPE=dcap

#3. Terminate any previously running enclave
#nitro-cli terminate-enclave --all
