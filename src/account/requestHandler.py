# @fileName: requestHandler.py
# @creation_date: 20/09/2024
# @authors: averyark

"""
Handles user requests by validating session tokens and executing the corresponding user request.

This function first checks if the session token is active. If not, it queries the database to validate the session token and retrieve the user ID. If the session token is valid, it begins a new session for the user. Once the session is validated, it executes the user request.

Args:
    sessionToken (str): The session token to validate.
    requestKind: The type of request to execute.
    *arg: Additional arguments for the request.

Raises:
    LookupError: If the session token is invalid.
    Exception: If there is an error loading user data from the database.
"""

import user
import login
from icecream import ic
import sqlite3

credentialsPath = "mock-database.db"
db = sqlite3.connect(credentialsPath)
cursor = db.cursor()

def handleRequest(sessionToken: str, requestKind, *arg):
    # Validate SessionToken
    userObject = None

    if not user.activeSessions[sessionToken]:
        # Check database
        try:
            cursor.execute(
                f'''
                    SELECT userId FROM UserSessionTokens
                    WHERE token IS {sessionToken}
                '''
            )
            row = cursor.fetchone()

            if row != None:
                userId = row[0]
                userObject = login.beginSession(userId, sessionToken)
            else:
                raise LookupError("Invalid session token")
        except Exception as err:
            print(f"Unable to load userdata: {err}")
    else:
        userObject = user.activeSessions[sessionToken]

    userObject.execute_user_request(requestKind, *arg)
