#call set state endpoint
call_setstate_endpoint "Starting Application in SGX Enclave" 10 4 "Starting Application in SGX Enclave"

#calling profiling_func (step 5)
profiling_func 5 "Starting Application in SGX Enclave" 
# Run new enclave
gramine-sgx ./python SecureApp.py