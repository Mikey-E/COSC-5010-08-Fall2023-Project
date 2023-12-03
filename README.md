# Distributed Algorithms Project - Asynchronous Secure Voting

This repository contains a prototype of the distributed voting system. A full overview of the project can be seen in the report file.

## Example run of the prototype:

Note that to run, the following dependencies are recommended:

| Dependency | Version |
|-----|---------|
| Windows | 11 |
| Python | 3.11.2 |   
| cryptography | 39.0.0 |
| pandas | 1.5.3 |

From there, the simulation can be run by the simulate.bat file on the command line.

`>simulate.bat`

In this simulation, first the state of the directory is reset by reset.py, i.e. there are no databases, election results, registrations, or keys made.
Second, the registrations of each citizen are made by registrations.py. This means the process of the government creating a registrations file wherein each citizen's
pseudonym (not real name, for privacy) are linked to the citizens's public key. Third, a network of three database instances are created with fully
connected topology by database.py. The output of these databases is redirected to a file for each one so the chain of events can be examined after the simulation
is over. Fourth, the three fictional characters Alice, Bob, and Oscar cast votes to the system via client.py.
Each casts a vote to *only* one of the databases. The votes databases timeout after 20 seconds of not receiving any more votes, at which point
the election is considered to be over.
Now, the results files can be examined to see that each database, despite receiving a vote from only one of the 3 characters,
does indeed contain the records of *all* votes because each database communicates new votes to the rest of the network. The results files will also
show the events that preceded the final state of the database, as well as the final vote tallies.