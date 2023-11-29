# Distributed Algorithms Project - Asynchronous Secure Voting

This repository contains a prototype of the distributed voting system. A full overview of the project can be seen in the powerpoint file: Presentation.pptx

## Example run of the prototype:

There is a client program, with access to the private key of a citizen, that will allow a citizen to cast a vote matching the following attributes:

| name (encrypted) | vote choice (A/B/C/Yes/No) | HMAC |
|------------|------------|------------|
| Row 1 Data | Data       | Data       |
| Row 2 Data | Data       | Data       |

Correspondingly there are multiple distributed databases, each of which will contain the following schema:

| name (encrypted) | vote choice (A/B/C/Yes/No) |
|------------|------------|
| Row 1 Data | Data       |
| Row 2 Data | Data       |

Since citizens already have a public key registered with the government, there is a record for each citizen in each database, with no vote cast yet. When a citizen sends their vote, the receiver first verifies that the signature is correct via the stored public keys, and then uses the encrypted name as a primary key in the database, updating the row for that citizen with the vote. These distributed databases then synchronize.