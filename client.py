#Author: Michael Elgin (melgin@uwyo.edu)

#File which a citizen would use to vote.
#Both the voting client and the votes database must use the same padding scheme and hash function.
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import socket
import sys

class Client:
    def __init__(self, pseudonym:str, private_key_file, choice:str, target_addr:str, target_port:int):
        self.pseudonym = pseudonym
        with open(private_key_file, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
            )
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#SOCK_STREAM is TCP
        self.choice = choice
        self.target_addr = target_addr
        self.target_port = target_port
    
    def vote(self):
        delimeter = "<sep>"
        vote = (self.pseudonym + delimeter + self.choice).encode()
        signature = self.private_key.sign(
            vote,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        vote = vote + delimeter.encode() + signature
        self.client_socket.connect((self.target_addr, self.target_port))
        self.client_socket.sendall(vote)
        self.client_socket.close()

def main():
    client = Client(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))
    client.vote()

if __name__ == "__main__":
    main()