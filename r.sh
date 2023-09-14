#call set state endpoint
call_setstate_endpoint "Starting Application in SGX Enclave" 10 4 "Starting Application in SGX Enclave"

data=$(cat profiling.json)
#calling profiling_func (step 5)
data = profiling_func 5 "Starting Application in SGX Enclave" "$data"
# Run new enclave
gramine-sgx ./python SecureApp.py