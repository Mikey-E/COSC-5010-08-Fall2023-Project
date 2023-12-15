#Author: Michael Elgin (melgin@uwyo.edu)

#Database file to create multiple instances of voting records which will synchronize

import sqlite3
import pandas as pd
import socket #For TCP
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import os
import sys

class VoteDatabase():
    def __init__(self, name:str, addr:str, s_port:int, c_port:int, timeout:float=600, neighbors:list=[]):
        self.name = name + (".db" if ".db" not in name else "")
        self.addr = addr
        self.s_port = s_port
        self.registrations = pd.read_csv("registrations.csv") #All dbs are assumed to have knowledge of this
        self.create_database()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#SOCK_STREAM is TCP
        self.timeout = timeout
        self.server_socket.settimeout(timeout) #In seconds
        self.server_socket.bind((addr, s_port))
        self.server_socket.listen(6) #Listen to up to this many clients at once. In practice this will be much bigger.
        self.neighbors = neighbors #of the form [('IP', s_port, c_port), ...]

        #Important - vote databases are identified as a neighbor by their client_socket addr and port, not server_socket.
        #This is because the client_socket addr and port is what a vote database expects to see when it receives a vote
        #from another vote database for the purpose of distributed synchronization.
        self.addr = addr
        self.c_port = c_port

    def create_database(self):
        if self.name in os.listdir(): return #Because this should only be done once
        connection = sqlite3.connect(self.name)
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE votes(pseudonym text, choice text)")
        for _, pseudonym in self.registrations['pseudonym'].items():
            cursor.execute("INSERT INTO votes VALUES ('" + pseudonym + "', 'null')")
        connection.commit()

    def receive_votes(self, delimeter="<sep>"):
        ip_port_neighbors = [(item[0], item[2]) for item in self.neighbors]#for recognizing neighbors
        while True:
            try:
                client_socket, ip_port = self.server_socket.accept()
                print("Received vote from " + str(ip_port) + \
                    (", vote is from a recognized neighbor so it will not be forwarded." \
                    if ip_port in ip_port_neighbors else "")
                )
            except TimeoutError:
                print("Timed out after " + str(self.timeout) + " seconds")
                return
            vote = client_socket.recv(512) #is generous
            client_socket.close()
            #If the vote came from a neighbor database for syncing, the port in ip_port will be the neighbor database's client socket port.
            #i.e. no need to forward votes that are already being forwarded.
            if ip_port not in ip_port_neighbors:#Vote came from the original source so must sync it with neighbors
                self.sync_vote(vote)
            sections = vote.split(delimeter.encode())
            pseudonym = sections[0]
            choice = sections[1]
            signature = sections[2]
            if self.verify_signature(pseudonym, choice, signature): #Then record the vote
                connection = sqlite3.connect(self.name)
                cursor = connection.cursor()
                cursor.execute("UPDATE votes SET choice = '" + choice.decode() + "' WHERE pseudonym = '" + pseudonym.decode() + "'")
                connection.commit()
                print("Vote recorded: {0}, {1}".format(pseudonym.decode(), choice.decode()))
            else:
                print("Vote not recorded.")
    
    def verify_signature(self, pseudonym:bytes, choice:bytes, signature:bytes, delimeter="<sep>"):
        """
        Verification by the database is as follows.
        1. The database receives the message from a client, with its signature (before this)
        2. The database checks the registrations for a public key matching the message's pseudonym
        3. The database uses that public key to decrypt the message signature (encrypted hash)
        4. The database then checks to make sure the message hashes to the same decrypted hash.
        """
        try:
            with open(self.registrations.loc[self.registrations["pseudonym"] == pseudonym.decode()]["public_key_file"].iloc[0], "rb") as f:
                public_key = serialization.load_pem_public_key(f.read())
        except IndexError:
            print("Pseudonym {0} has not been registered and cannot cast a vote.".format(pseudonym.decode()))
            return False
        try:
            public_key.verify(#will throw an InvalidSignature Exception if message or signature has been altered.
                signature,
                pseudonym + delimeter.encode() + choice,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            print("Vote contents and signature do not match.")
            return False

    def sync_vote(self, vote):
        """Forwards the vote to all neighbor vote databases, achieving synchronization"""
        for neighbor in self.neighbors:
            print("Synchronizing vote with neighbor: " + str(neighbor))
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#Vote dbs are clients of each other
            self.client_socket.bind((self.addr, self.c_port))
            self.client_socket.connect((neighbor[0], neighbor[1]))
            self.client_socket.sendall(vote)
            self.client_socket.close()

    def display_results(self):
        connection = sqlite3.connect(self.name)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM votes")
        results = cursor.fetchall()
        counts = dict()
        print("----------Votes------------")
        for pseudonym, choice in results:
            print("pseudonym: {0}, choice: {1}".format(pseudonym, choice))
            if choice in counts:
                counts[choice] += 1
            else:
                counts[choice] = 1
        print("----------Totals------------")
        for choice in counts:
            print("{0}: {1}".format(choice, counts[choice]))

def main():
    #Create a vote database, receive votes until none come in for the duration of the timeout, then display the results
    #sys.argv command line arguments match the order of the class __init__
    neighbors = [tuple(neighbor.split(":")) for neighbor in sys.argv[6:]]
    neighbors = [(neighbor[0], int(neighbor[1]), int(neighbor[2])) for neighbor in neighbors]
    vDB = VoteDatabase(
        sys.argv[1],#name
        sys.argv[2],#addr
        int(sys.argv[3]),#s_port
        int(sys.argv[4]),#c_port
        timeout=float(sys.argv[5]),
        neighbors=neighbors)
    vDB.receive_votes()
    vDB.display_results()

if __name__ == "__main__":
    main()