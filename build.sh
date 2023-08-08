#!/bin/bash

set -x # to echo the command being executed

#cp /home/iudx/sgx-yolo-app/yolov5 ./yolov5/

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
