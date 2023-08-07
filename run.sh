#gramine-sgx terminate-enclave --all

#./membig.sh

#4. Run new enclave
gramine-sgx ./python ppml.py
#nitro-cli run-enclave --cpu-count 2 --memory 14000 --eif-path /home/ubuntu/cached/secureapp-nitro.eif --debug-mode

#5. Get inside the read only console of enclave(as it is in debug mode)
#ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")

#6. Finally run the server.py program inside the enclave
#nitro-cli console --enclave-id ${ENCLAVE_ID}
#~