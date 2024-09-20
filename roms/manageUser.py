# @fileName: manageUser.py
# @creation_date: 20/09/2024
# @authors: averyark

import sqlite3
from icecream import ic
import login

credentialsPath = "mock-database.db"
db = sqlite3.connect(credentialsPath)
cursor = db.cursor()

def editUserCredentials(email: str, newPassword: str):
    try:
        userId = login.get_userid_from_email(email)
        cursor.execute(
            f'''
                UPDATE Credentials
                    SET password = {newPassword}
                    WHERE userId = {userId}
            '''
        )
    except Exception as err:
        print(f"EditUserCredentials Failed: {err}")
