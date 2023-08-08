#gramine-sgx terminate-enclave --all

#./membig.sh

# Run new enclave
gramine-sgx ./python ppml.py

#5. Get inside the read only console of enclave(as it is in debug mode)
#ENCLAVE_ID=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")

#6. Finally run the server.py program inside the enclave
#nitro-cli console --enclave-id ${ENCLAVE_ID}
#~