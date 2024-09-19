# @fileName: login.py
# @creation_date: 19/09/2024
# @authors:

"""
This module provides functionality for user login and retrieval of user ID based on email.

Functions:
    login(userId: int, credential: str) -> user.User:
        Authenticates a user based on user ID and credential, and returns a User object with session ID.

    getUserIdForEmail(email: str) -> int:
        Retrieves the user ID associated with the given email address.
"""

from icecream import ic
import sqlite3
import uuid
import credentials
import user

credentialsPath = "mock-database.db"
db = sqlite3.connect(credentialsPath)
cursor = db.cursor()

def login(userId: int, credential: str):
    sessionId = uuid.uuid1()

    # validate credentials
    if credentials.validateCredentials(userId, credential):
        raise RuntimeError("Invalid credentials")

    userdata = None
    try:
        cursor.execute(
            f'''
                SELECT
                    firstName,
                    lastName,
                    email,
                    birthday,
                    userPermission
                FROM Userdata WHERE id IS {userId}
            '''
        )
        row = cursor.fetchone()
        userdata = {
            ["firstName"]: row[0],
            ["lastName"]: row[1],
            ["email"]: row[2],
            ["birthday"]: row[3],
            ["userPermission"]: row[4]
        }
    except Exception as err:
        userdata = None
        print(f"Unable to load userdata {err}")

    if not userdata:
        raise RuntimeError("Unable to load userdata")

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

    return user.User(userdata, sessionId)

def getUserIdForEmail(email: str):
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

#login(getUserIdForEmail("email@gmail.com"), "SomePassword@12345")
