. ./setState.sh
. ./profilingStep.sh

#start of step 5
echo "Step 5"

#call set state endpoint
call_setstate_endpoint "Starting Application in SGX Enclave" 10 5 "Starting Application in SGX Enclave"

echo "Starting Application in SGX Enclave"
# Run new enclave
gramine-sgx ./python runSecureApp.py
