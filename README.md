# YOLO APP on AMD CVM
Using Docker, this is how Yolo App can be run locally on AMD CVM.

1. Clone repo into VM
       `git clone git@github.com:datakaveri/sgx-yolo-app.git`
2. Switch to AMD branch
       `git checkout amd_yolo`
3. Build docker image
       `sudo docker build -t <name of image> .`
4. Run
       `sudo docker run <name of image>`


## Tokenization Flow

![Tokenization Flow](https://github.com/datakaveri/sgx/assets/51048453/f8bdc80a-113e-4f46-b081-d9e792ca5e2b)

1. The host machine with the YOLO model in it generates a SGX quote with a RSA public key embedded inside it and sends it to the APD server.
2. The APD server uses the Intel PCCS service to verify the quote. 
3. If authorised, a token with the same RSA public key embedded inside it is sent back to the SGX machine.
4. The token is then sent to the resource server. If authorised, then the resource server encrypts the files using a symmetric key and then encrypts the symmetric key using the RSA public key which was embedded inside the token. 
5. The encrypted file along with the encrypted symmetric key are loaded into a pickle and sent to the SGX machine.
6. The RSA private key is used to decrypt the encrypted symmetric key and then the decrypted symmetric key is used to decrypt the files. 
7. The decrypted files are used to run the application inside a secure enclave.

