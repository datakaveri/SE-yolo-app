# PPML by using Intel SGX
This repository implements Secure Enclaves by Intel SGX to run YOLO machine learning model on input images which are sourced from a resource server in a privacy preserving workflow.  
## Steps
1. Create virtual environment.
    `python -m venv .env`
2. Source the virtual environment.  
    `source env/bin/activate`
3. Install requirement.txt (for tokenization flow) and yolov5/requirement.txt (for yolo).   
    `pip install -r requirements.txt -r yolov5/requirements.txt`   
4. Build the application.     
    `make SGX=1 RA_TYPE=dcap`
5. Run the application.    
    `gramine-sgx ./python ppml.py`
6. Remove the manifest, input files and output files.   
    `make clean`   


## Tokenization Flow

![Tokenization Flow](https://github.com/datakaveri/sgx/assets/51048453/f8bdc80a-113e-4f46-b081-d9e792ca5e2b)

1. The host machine with the YOLO model in it generates a SGX quote with a RSA public key embedded inside it and sends it to the APD server.
2. The APD server uses the Intel PCCS service to verify the quote. 
3. If authorised, a token with the same RSA public key embedded inside it is sent back to the SGX machine.
4. The token is then sent to the resource server. If authorised, then the resource server encrypts the files using a symmetric key and then encrypts the symmetric key using the RSA public key which was embedded inside the token. 
5. The encrypted file along with the encrypted symmetric key are loaded into a pickle and sent to the SGX machine.
6. The RSA private key is used to decrypt the encrypted symmetric key and then the decrypted symmetric key is used to decrypt the files. 
7. The decrypted files are used to run the application inside a secure enclave.

