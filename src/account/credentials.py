# @fileName: credentials.py
# @creation_date: 18/09/2024
# @authors: averyark

# TODO: SWITCH TO SQLITE3
import shelve

credentialsPath = "mock-database/credentials"

def validateCredentials(email: str, input: str):
    matched = False
    with shelve.open(credentialsPath) as credentials:
        if credentials[email] == input:
            matched = True

    return matched

def setCredentials(email: str, password: str):
    with shelve.open(credentialsPath) as credentials:
        credentials[email] = password
