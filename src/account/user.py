# @fileName: user.py
# @creation_date: 14/09/2024
# @authors: averyark

"""
This module provides functionality for user account management, including validation of user data and synchronization with a SQLite database.

Classes:
    User: Represents a user with attributes and methods for managing user data.

Functions:
    validateDate(date_text): Validates if the provided date string is in the correct format (YYYY-MM-DD).
    validateName(name): Validates if the provided name is a string with 1-50 characters and contains only alphabets, numbers, and spaces.
    validateEmail(email): Validates if the provided email is a string with 1-50 characters and follows the format of a valid email address.
    validatePassword(password): Validates if the provided password is a string with 8-50 characters, contains at least one number and one alphabet, and includes only allowed special characters.
    validateUserData(data): Validates a dictionary of user data by checking the password, first name, last name, birthday, and email.

User Class:
    Methods:
        __init__(self, data, sessionId): Initializes a User object with provided data and session ID.
        syncdata(self): Synchronizes the user data with the database.
        destruct(self): Destructor method that calls syncdata to save user data.
        __str__(self): Returns the user's full name as a string.
        set_permission(self, newPermission): Sets the user's permission level based on the provided role.
        get_birthday(self): Returns the user's birthday as a Pendulum date object.
        get_name(self): Returns the user's full name in "lastName firstName" format.
"""

import pendulum
import datetime
import re
from icecream import ic
import sqlite3

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

UserPermissionClass = {
    'Manager': 255,
    'Chef': 100,
    'Cashier': 50,
    'Customer': 10
}
class User:
    # Contruct
    def __init__(self, data, sessionId):
        self.userId = data.id
        self.firstName = data.firstName
        self.lastName = data.lastName
        self.email = data.email
        self.birthday = data.birthday
        self.userPermission = data.userPermission or 1
        #self.sessionId = sessionId

    def syncdata(self):
        # Save data
        try:
            # Verify sessionId
            # cursor.execute(
            #     f'''
            #         SELECT
            #             ACTIVE_SESSION
            #         FROM Userdata WHERE id IS {self.userId}
            #     '''
            # )
            # if cursor.fetchone()[0] == self.sessionId:
            #     # Rejected: Uhh another session is active
            #     return

            cursor.execute(
                f'''
                    UPDATE Userdata
                    SET firstName = {self.firstName},
                        lastName = {self.lastName},
                        email = {self.email},
                        birthday = {self.birthday},
                        userPermission = {self.userPermission}
                    WHERE id IS {self.userId}
                '''
            )
            db.commit()
        except Exception as err:
            print(f"Update data failed: {err}")
            db.rollback()

    # Destruct
    def destruct(self):
        self.syncdata()

    def __str__(self):
        return f"{self.getname()}"

    def set_permission(self, newPermission):
        assert type(UserPermissionClass[newPermission])!= None
        self.userPermission = UserPermissionClass.get(newPermission)
        self.syncdata()

    def get_birthday(self):
        return pendulum.from_format(self.birthday, "YYYY-MM-DD")

    def get_name(self):
        return f"{self.lastName} {self.firstName}"

# jianyi = User("Jian Yi", "Ting", "alwin@gmail.com", "2005-09-21")

def __init__():
     print("loaded")
