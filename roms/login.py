# @fileName: login.py
# @creation_date: 19/09/2024
# @authors: averyark

"""
This module provides functionalities for user login, session management, and user data retrieval.

Functions:
    beginSession(userId: int, sessionToken: str) -> user.User:
        Begins a user session by retrieving user data and returning a User object.

    login(userId: int, credential: str) -> None:
        Logs in a user by validating credentials and managing session tokens.

    expireSession(userId: int) -> None:
        Expires a user session by deleting the session token and committing changes to the database.

    getUserIdForEmail(email: str) -> int:
        Retrieves the user ID associated with a given email address.
"""

from icecream import ic
import sqlite3
import uuid
from .credentials import validate_credentials
from .user import begin_session

credentialsPath = "mock-database.db"
db = sqlite3.connect(credentialsPath)
cursor = db.cursor()

cursor.execute(
    '''
        CREATE TABLE IF NOT EXISTS UserSessionTokens(
            userId INTEGER NOT NULL,
            token NVARCHAR(255) NOT NULL,

            PRIMARY KEY (userId, token)
        )
    '''
)
db.commit()

def login(userId: int, credential: str) -> None:
    # validate credentials
    if not validate_credentials(userId, credential):
        raise RuntimeError("Invalid credentials")

    sessionToken = None

    try:
        cursor.execute(
            f'''
                SELECT token FROM UserSessionTokens
                WHERE userId IS {userId}
            '''
        )
        row = cursor.fetchone()

        if row != None:
            sessionToken = row[0]
        else:
            sessionToken = str(uuid.uuid1())

            cursor.execute(
            f'''
                INSERT INTO UserSessionTokens(
                    userId, token
                ) VALUES (
                    {userId},
                    '{sessionToken}'
                )
            '''
        )
    except Exception as err:
        sessionToken = None
        print(f"Unable to load userdata: {err}")

    ic(sessionToken)

    if not sessionToken:
        print("User doesn't have a sessionToken")
        return

    return begin_session(userId, sessionToken)

def get_userid_from_email(email: str) -> int:
    userId = None
    try:
        cursor.execute(
            f'''
                SELECT
                    id
                FROM Userdata WHERE email IS '{email}'
            '''
        )
        userId = cursor.fetchone()[0]
    except Exception as err:
        pass

    return userId
