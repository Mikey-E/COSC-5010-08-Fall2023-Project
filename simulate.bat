::Author: Michael Elgin (melgin@uwyo.edu)
::Batch file to simulate a run of the voting process

::0. Envrionment reset. This will get rid of old databases, keys, results records, etc.
py reset.py

::1. Citizens register.
::This creates their private keys, their public keys, pseudonyms, and registrations.csv record
::which all votes databases are assumed to have. (If these things don't already exist)
py registrations.py

::2. The votes databases are launched, with their respective neighbors.
::This assumes a fully connected topology, ie each database must include all other
::databases in its set of neighbors.
::Command line arguments following "database.py" match the order of the class __init__
::DB1 with neighbors 2 and 3, server socket 8081, client socket 8084
::DB2 with neighbors 1 and 3, server socket 8082, client socket 8085
::DB3 with neighbors 1 and 2, server socket 8083, client socket 8086
::Notice that output is redirected to a file. This is to save results, and also to help with debugging.
::For a real run of the system, 127.0.0.1 would of course be replaced by the real IP addresses of the databases.
start cmd /c "py database.py vDB1 127.0.0.1 8081 8084 20 127.0.0.1:8082:8085 127.0.0.1:8083:8086 > results1.txt" 
start cmd /c "py database.py vDB2 127.0.0.1 8082 8085 20 127.0.0.1:8081:8084 127.0.0.1:8083:8086 > results2.txt"
start cmd /c "py database.py vDB3 127.0.0.1 8083 8086 20 127.0.0.1:8081:8084 127.0.0.1:8082:8085 > results3.txt"

::3. Now the fictional characters Alice, Bob, and Oscar will try to cast their votes to a database.
::It is assumed that Alice is closest to DB1, Bob to DB2, Oscar to DB3.
::By the end, because of the distributed database synchronization, all 3 databases will reflect
::the same overall votes and vote totals in their results files.
py client.py voter0 private_key_Alice.pem yes 127.0.0.1 8081
py client.py voter1 private_key_Bob.pem yes 127.0.0.1 8082
py client.py voter2 private_key_Oscar.pem no 127.0.0.1 8083
