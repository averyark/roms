# @fileName: user.py
# @creation_date: 14/09/2024
# @authors: averyark
"""
    This module provides user account management functionalities including validation,
    user session handling, and permission management.

    Classes:
        User: Represents a user with methods for data synchronization, session management,
            and permission handling.

    Functions:
        validateDate(date_text): Validates if the given date is in the correct format (YYYY-MM-DD).
        validateName(name): Validates if the given name is a string with 1-50 characters and
                            contains only alphabets, numbers, and spaces.
        validateEmail(email): Validates if the given email is a string with 1-50 characters and
                            follows the correct email format.
        validatePassword(password): Validates if the given password is a string with 8-50 characters,
                                    contains at least one number and one alphabet, and includes
                                    allowed special characters.
        validateUserData(data): Validates user data dictionary for required fields.
        getUserClass(userPermission): Returns the user class based on the user's permission rank.
        cleanupSessions(): Cleans up inactive user sessions.

    Constants:
        credentialsPath: Path to the mock database file.
        db: SQLite database connection object.
        cursor: SQLite database cursor object.
        userPermissionRanks: Dictionary mapping user roles to their permission ranks.
        PermissionClass: Dictionary mapping user roles to their respective classes.
        activeSessions: Dictionary to keep track of active user sessions.
        EXPIRE_INTERVAL: Time interval (in seconds) after which inactive sessions are expired.

    Notes:
        - The `User` class handles user data synchronization with the database, session management,
        and permission updates.
        - The `cleanupSessions` function is scheduled to run every 60 seconds to clean up inactive sessions.
"""


import importlib.util
import pendulum
import datetime
import re
from icecream import ic
import sqlite3
import threading
import time
#from . import session
import importlib

credentialsPath = "mock-database.db"
db = sqlite3.connect(credentialsPath)
cursor = db.cursor()

def validateDate(date_text):
    try:
        datetime.date.fromisoformat(date_text)
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def validateName(name):
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    elif len(name) < 1 or len(name) > 50:
        raise ValueError("name must have 1-50 characters")
    elif re.search("^[a-zA-Z0-9 ]*", name).end() != len(name):
        raise ValueError("name must be alphabets, numbers, and space only")

def validateEmail(email: str):
    matched = re.search(r"^[a-zA-Z0-9\.]+@[a-zA-Z0-9]*.com$", email)
    if not isinstance(email, str):
        raise TypeError("email must be a string")
    elif len(email) < 1 or len(email) > 50:
        raise ValueError("email must have 1-50 characters")
    elif not matched or matched.end() != len(email):
        raise ValueError("invalid email format")

def validatePassword(password: str):
    matched = re.search(r"^[a-zA-Z0-9!\"#\$%\&'\(\)\*\+,\-:;<=>\?@\[\]\^_`\{\|\}~\.]*", password)

    if not isinstance(password, str):
        raise TypeError("password must be a string")
    elif len(password) < 8 or len(password) > 50:
        raise ValueError("password must have 8-50 characters")
    elif len(re.findall(r"[0-9]", password)) < 1:
        raise ValueError("password must have at least 1 number")
    elif len(re.findall(r"[a-zA-Z]", password)) < 1:
        raise ValueError("password must have at least 1 alphabet")
    elif not matched or matched.end() != len(password):
        raise ValueError("password must be alphabet, number or #~`!.@#$%^&*()_-+={[}]|:;\"'<,>?")

def validateUserData(data: dict):
    if not dict(data):
        raise TypeError("data must be a dictionary")

    validatePassword(data.get("password"))
    validateName(data.get("firstName"))
    validateName(data.get("lastName"))
    validateDate(data.get("birthday"))
    validateEmail(data.get("email"))

userPermissionRanks = {
    'Manager': 255,
    'Chef': 100,
    'Cashier': 50,
    'Customer': 10
}

from ..user_classes import cashier, chef, customer, manager

userPermissionModules = {
    'Manager': manager,
    'Chef': chef,
    'Cashier': cashier,
    'Customer': customer
}

def getUserClass(userPermission):
    userClassName = None
    for className, classRank in userPermissionRanks.items():
        if userPermission < classRank:
            continue

        userClassName = className
        return userPermissionModules.get(className)

    if userClassName != None:
        return

    return None

"""
    Logout is different from destruct!
    Logging out always trigger destruct but destruct doesn't mean the user is logout'd.
"""
# active user classes

activeSessions = {}

class User:
    # Contruct
    def __init__(self, data, sessionToken):
        self.userId = data.get("id")
        self.firstName = data.get("firstName")
        self.lastName = data.get("lastName")
        self.email = data.get("data.email")
        self.birthday = data.get("data.birthday")
        self.permission = data.get("permission") or 1
        self.sessionToken = sessionToken
        self.destructing = False
        self.lastActive = time.time()

        self.userClass = getUserClass(self.permission)

        activeSessions[self.sessionToken] = self

        print(activeSessions)

    def syncdata(self):
        # Save data
        try:
            # Verify sessionToken
            # cursor.execute(
            #     f'''
            #         SELECT
            #             ACTIVE_SESSION
            #         FROM Userdata WHERE id IS {self.userId}
            #     '''
            # )
            # if cursor.fetchone()[0] == self.sessionToken:
            #     # Rejected: Uhh another session is active
            #     return

            cursor.execute(
                f'''
                    UPDATE Userdata
                    SET firstName = {self.firstName},
                        lastName = {self.lastName},
                        email = {self.email},
                        birthday = {self.birthday},
                        permission = {self.permission}
                    WHERE id IS {self.userId}
                '''
            )
            db.commit()
        except Exception as err:
            print(f"Update data failed: {err}")
            db.rollback()

    def destruct(self):
        if self.destructing:
            return

        self.destructing = True
        self.syncdata()

        if activeSessions[self.sessionToken]:
            del activeSessions[self.sessionToken]

    def logout(self):
        if self.destructing:
            return

        expireSession(self.userId)

        self.destruct()

    def set_permission(self, newPermission):
        assert type(userPermissionRanks[newPermission])!= None
        self.userPermission = userPermissionRanks.get(newPermission)
        self.userClass = getUserClass(newPermission)
        self.syncdata()

    def get_birthday(self):
        return pendulum.from_format(self.birthday, "YYYY-MM-DD")

    def get_name(self):
        return f"{self.lastName} {self.firstName}"

    def execute_user_request(self, requestKind, *arg):
        if self.userClass.functions.index(requestKind) == None:
            raise ValueError(f'RequestKind "{requestKind}" does not exist for permission rank: {self.userPermission}')

        self.lastActive = time.time

        self.userClass[requestKind](*arg)

    def __str__(self):
        return f"{self.getname()}"

def beginSession(userId: int, sessionToken: str) -> User:
    userdata = None
    try:
        cursor.execute(
            f'''
                SELECT
                    id,
                    firstName,
                    lastName,
                    email,
                    birthday,
                    permission
                FROM Userdata WHERE id IS {userId}
            '''
        )
        row = cursor.fetchone()
        ic(row)
        userdata = {
            "id": row[0],
            "firstName": row[1],
            "lastName": row[2],
            "email": row[3],
            "birthday": row[4],
            "permission": row[5]
        }
    except Exception as err:
        userdata = None
        print(f"Unable to load userdata {err}")

    if not userdata:
        raise RuntimeError("Unable to load userdata")

    return User(userdata, sessionToken)

def expireSession(userId) -> None:
    try:
        cursor.execute(
            f'''
                SELECT token FROM UserSessionTokens
                WHERE userId IS {userId}
            '''
        )
        row = cursor.fetchone()

        if row == None:
            raise LookupError("User does not have a session token")

        cursor.execute(
            f'''
                DELETE FROM UserSessionTokens
                WHERE userId IS {userId}
            '''
        )

        activeSessions[row[0]].destruct()

    except Exception as err:
        print(f"Encountered an error: {err}")
        db.rollback()
    else:
        db.commit()

# Move to login.py
# Expire session after 1 hour of inactivity for the sake of saving memory
EXPIRE_INTERVAL = 3600 # 1 Hour
# flush
def cleanupSessions():
    now = time.time()
    for self in activeSessions.values():
        if now - self.lastActive > EXPIRE_INTERVAL:
            self.destruct()

def __init__():
    threading.Timer(60, cleanupSessions).start()
    print("loaded")
