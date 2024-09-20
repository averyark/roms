# @fileName: credentials.py

"""
This module provides functions to manage user credentials using an SQLite database.

Functions:
    validateCredentials(userId: str, input: str) -> bool:
        Validates the provided credentials against the stored credentials in the database.

    setCredentials(userId: int, password: str):
        Stores the provided user ID and password in the database.

Database Schema:
    Table: Credentials
        id: INTEGER PRIMARY KEY AUTOINCREMENT
        userId: INTEGER NOT NULL
        password: NVARCHAR(50) NOT NULL
"""
# @creation_date: 18/09/2024
# @authors: averyark

import sqlite3
from icecream import ic

credentialsPath = "mock-database.db"
db = sqlite3.connect(credentialsPath)
cursor = db.cursor()

cursor.execute(
    '''
        CREATE TABLE IF NOT EXISTS Credentials(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER NOT NULL,
            password NVARCHAR(50) NOT NULL
        )
    '''
)
db.commit()

def validateCredentials(userId: str, input: str):
    cursor.execute(
        f'''
            SELECT DISTINCT password FROM Credentials WHERE userId IS '{userId}'
        '''
    )
    row = cursor.fetchone()

    ic(row)

    if row and row[0] == input:
        return True
    else:
        return False

def setCredentials(userId: int, password: str):
    cursor.execute(
        f'''
            INSERT INTO Credentials(
                id, userId, password
            ) VALUES (
                NULL, '{userId}', '{password}'
            )
        '''
    )
    db.commit()
