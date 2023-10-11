#!/bin/bash
chmod +x b.sh
chmod a+x ./setState.sh
. ./setState.sh
. ./profilingStep.sh

cp /home/iudx/sgx-enclave-manager/profiling.json ./

#start of step 3
echo "Step 3"
memory_usage=$(python3 -c 'import PPDX_SDK; print(PPDX_SDK.measure_memory_usage())')
echo "Memory usage: $memory_usage"

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

#step 3 done
echo "Step 3 done"
memory_usage_2=$(python3 -c 'import PPDX_SDK; print(PPDX_SDK.measure_memory_usage())')
echo "Memory usage: $memory_usage_2"
total_memory_usage=$(($memory_usage_2 - $memory_usage))
echo "Total memory usage: $total_memory_usage "
#calling profiling function
profiling_func 3 "Setting up the virtual environment(if not present) & installing dependencies for application" "$total_memory_usage"

#start of step 4
echo "Step 4"
memory_usage=$(python3 -c 'import PPDX_SDK; print(PPDX_SDK.measure_memory_usage())')
echo "Memory usage: $memory_usage"

#calling setState endpoint (step 4)
call_setstate_endpoint "Building manifest" 10 4 "Building manifest"

echo "Building manifest"
make clean
make SGX=1 RA_TYPE=dcap

#step 4 done
echo "Step 4 done"
memory_usage_2=$(python3 -c 'import PPDX_SDK; print(PPDX_SDK.measure_memory_usage())')
echo "Memory usage: $memory_usage_2"
total_memory_usage=$(($memory_usage_2 - $memory_usage))
echo "Total memory usage: $total_memory_usage "
#calling profiling function
profiling_func 4 "Building manifest" "$total_memory_usage"
