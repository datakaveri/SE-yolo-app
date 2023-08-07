#!/bin/bash

set -x # to echo the command being executed

#cp /home/iudx/sgx-yolo-app/yolov5 ./yolov5/

#gramine-sgx terminate-enclave --all
#sh /home/iudx/sgx-enclave-manager/cl.sh

#./memsmall.sh

#1.Create Docker (Edit "Dockerfile" for any changes)
#docker build -t secureapp-nitro .

#2. Build nitro enclave
make clean
make SGX=1 RA_type=dcap
#nitro-cli build-enclave --docker-uri secureapp-nitro:latest --output-file secureapp-nitro.eif

#mv secureapp-nitro.eif /home/ubuntu/cached/secureapp-nitro.eif

#3. Terminate any previously running enclave
#nitro-cli terminate-enclave --all
