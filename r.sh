. ./setState.sh
. ./profilingStep.sh

#step 5
python3 -c 'import PPDX_SDK; PPDX_SDK.measure_memory_usage()'

#call set state endpoint
call_setstate_endpoint "Starting Application in SGX Enclave" 10 5 "Starting Application in SGX Enclave"

#calling profiling_func (step 5)
profiling_func 5 "Starting Application in SGX Enclave" 
# Run new enclave
gramine-sgx ./python SecureApp.py