# @fileName: signup.py
# @creation_date: 14/09/2024
# @authors: averyark

"""
@fileName: signup.py
@creation_date: 14/09/2024
@authors: averyark

This module handles the signup process for new users. It includes the following functionalities:
- Validating user data
- Checking for existing users in the database
- Inserting new user data into the database
- Setting user credentials

Functions:
    signup(data: dict, permission: int) -> User:
        Validates user data, checks for existing users, inserts new user data into the database, and sets user credentials.

Usage:
    Call the signup function with a dictionary containing user data and a permission level to register a new user.
"""

from user import User
import user
from icecream import ic
import credentials

import sqlite3

credentialsPath = 'mock-database.db'
db = sqlite3.connect(credentialsPath)
cursor = db.cursor()

cursor.execute(
    '''
        CREATE TABLE IF NOT EXISTS Userdata(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email NVARCHAR(50) NOT NULL,
            firstName NVARCHAR(50) NOT NULL,
            lastName NVARCHAR(50) NOT NULL,
            birthday NVARCHAR(50) NOT NULL,
            permission INTEGER
        )
    '''
)
db.commit()

def signup(data: dict, permission: int) -> User:
    try:
        user.validateUserData(data)
    except Exception as err:
        print('Error occurred during signup:')
        print('-'*15, ' Exception ', '-'*15)
        print(err)
        print('-'*40)
    else:
        # add to database
        try:
            cursor.execute(
                f'''
                    SELECT DISTINCT * FROM Userdata WHERE email IS '{data.get("email")}'
                '''
            )
            row = cursor.fetchone()
            if row:
                raise LookupError("This email already exist in the database")
        except Exception as err:
            print(f"Error occurred: {err}")
        else:
            cursor.execute(
                f'''
                    INSERT INTO Userdata(
                        id, email, firstName, lastName, birthday, permission
                    ) VALUES (
                        NULL,
                        '{data.get('email')}',
                        '{data.get('firstName')}',
                        '{data.get('lastName')}',
                        '{data.get('birthday')}',
                        {permission}
                    )
                '''
            )

            cursor.execute(
                f'''
                    SELECT DISTINCT id FROM Userdata WHERE email IS '{data.get('email')}'
                '''
            )

            row = cursor.fetchone()

            if row:
                db.commit()
                credentials.setCredentials(row[0], data.get('password'))
            else:
                db.rollback()

# signup({
#      'firstName': 'first',
#      'lastName': 'last',
#      'email': 'email@gmail.com',
#      'birthday': '2005-09-21',
#      'password': "SomePassword@123456",
#  }, user.UserPermissionClass.get("Manager"))

# for row in cursor.execute('SELECT * FROM Userdata'):
#     print(row)
