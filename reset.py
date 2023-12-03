#Author: Michael Elgin (melgin@uwyo.edu)

#File to reset the environment before running simulations

import os

for file_name in os.listdir():
    if  (".db" in file_name) or \
        ("results" in file_name) or \
        ("registrations.csv" in file_name) or \
        (".pem" in file_name):
        os.remove(file_name)