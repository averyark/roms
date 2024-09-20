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

from . import credentials, user

credentialsPath = "mock-database.db"
db = sqlite3.connect(credentialsPath)
cursor = db.cursor()

cursor.execute(
    '''
        CREATE TABLE IF NOT EXISTS UserSessionTokens(
            userId INTEGER PRIMARY KEY,
            token NVARCHAR(50)
        )
    '''
)
db.commit()

def login(userId: int, credential: str) -> None:
    # validate credentials
    if credentials.validateCredentials(userId, credential):
        raise RuntimeError("Invalid credentials")

    # attempt to session lock
    # sessionLockSuccessful = False

    # try:
    #     cursor.execute(
    #         f'''
    #             UPDATE Userdata
    #             SET ACTIVE_SESSION = {sessionId}
    #             WHERE id IS {userId}
    #         '''
    #     )
    # except Exception as err:
    #     db.rollback()
    #     sessionLockSuccessful = False
    #     print(f"Login failed: {err}")
    # else:
    #     sessionLockSuccessful = True

    # if not sessionLockSuccessful:
    #     raise RuntimeError("Unable to lock session")

    sessionToken = None

    try:
        cursor.execute(
            f'''
                SELECT * FROM UserSessionTokens
                WHERE userId IS {userId}
            '''
        )
        row = cursor.fetchone()

        if row != None:
            sessionToken = row[0]
        else:
            sessionToken = uuid.uuid1()
    except Exception as err:
        print(f"Unable to load userdata: {err}")

    return user.beginSession(userId, sessionToken)

def getUserIdForEmail(email: str) -> int:
    userid = None
    try:
        cursor.execute(
            f'''
                SELECT
                    id
                FROM Userdata WHERE email IS '{email}'
            '''
        )
    except Exception as err:
        raise RuntimeError(f"Failed to retrieve userId: {err}")

    return userid

#login(getUserIdForEmail("email@gmail.com"), "SomePassword@12345")
