#!/bin/bash

#virtual environment 
DIR=/home/iudx/.env/sgx-yolo-app
if [ -d "$DIR" ];
then
    echo 'Virtual environment exists'
else
    echo 'Creating virtual environment'
    python3 -m venv .env/sgx-yolo-app

    #source the virtual environment
    source .env/sgx-yolo-app/bin/activate

    #install dependencies
    pip3 install -r requirements.txt -r yolov5/requirements.txt
fi

set -x # to echo the command being executed

cp /home/iudx/yolov5x.pt ./yolov5/

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
