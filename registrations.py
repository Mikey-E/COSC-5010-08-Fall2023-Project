#Author: Michael Elgin (melgin@uwyo.edu)

#This is the 1st file to run.
#It simulates the process of citizens registering public keys and pseudonym with the government,
#and should only be done once.
#You could delete the registration file and then run this Python file again,
#and it would reappear as it should be. Keep in mind this will generate new public+private keys for all citizens,
#which is no problem.

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

#1st, the registration file must be created, if it is not already.
registration_file = "registrations.csv"
if registration_file not in os.listdir():
    with open(registration_file, "w") as f:
        f.write("pseudonym,public_key_file\n")#Just the column headers
    #Example citizens
    citizens = ["Alice", "Bob", "Oscar"]
    for citizen_idx, citizen in enumerate(citizens): #Each will generate a private key, save (for themselves), and register the public key + pseudonym
        #Private key creation and storage
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open("private_key_" + citizen + ".pem", "wb") as f:#Stays in repo for this prototype, in reality it would stay with the citizen
            f.write(pem)
        #Pseudonym and public key creation
        pseudonym = "voter" + str(citizen_idx)
        public_key = private_key.public_key()#Can be freely given to the government
        public_key_file = "public_key_" + pseudonym +".pem"
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(public_key_file, "wb") as f:
            f.write(pem)
        #Registrations must now connect the pseudonym and public key (by storing the public key file name)
        with open(registration_file, "a") as f:
            f.write(pseudonym + "," + public_key_file + "\n")#Just the column headers