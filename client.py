#Author: Michael Elgin (melgin@uwyo.edu)

#File which a citizen would use to vote.
#Both the voting client and the votes database must use the same padding scheme and hash function.
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import socket

class Client:
    def __init__(self, pseudonym:str, private_key_file):
        self.pseudonym = pseudonym
        with open(private_key_file, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
            )
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#SOCK_STREAM is TCP
    
    def vote(self, choice:str, address:str, port:int):
        """
        choice: The client needs to specify the choice for the vote made.
        address: The address of the which votes database to send the vote to.
        port: The port of the votes database.
        """
        delimeter = "<sep>"
        vote = (self.pseudonym + delimeter + choice).encode()
        signature = self.private_key.sign(
            vote,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        vote = vote + delimeter.encode() + signature
        self.client_socket.connect((address, port))
        self.client_socket.sendall(vote)
        self.client_socket.close()

def main():
    client = Client("voter0", "private_key_Alice.pem")
    client.vote("yessir1", "127.0.0.1", 8081)

if __name__ == "__main__":
    main()