# @fileName: main.py
# @creation_date: 20/09/2024
# @authors: averyark

from roms import login, get_userid_from_email
from roms import signup, create_account, UserInfo, edit_credentials

from roms.account import swagger_login, login, logout
from roms import userPermissionRanks
from roms import app
from roms.user import get_user
from roms.database import UserData, get_user_data_in_dict
from roms.credentials import pwd_context

from fastapi import Depends, FastAPI, HTTPException, status
from typing import Annotated

from icecream import ic
import sqlite3
credentialsPath = "mock-database.db"
db = sqlite3.connect(credentialsPath)
cursor = db.cursor()

def test_viewall():
    print(f"{'-'*20} Userdata {'-'*19}")
    for row in cursor.execute('SELECT * FROM Userdata'):
        ic(row)

    print(f"{'-'*15} UserSessionTokens {'-'*15}")
    for row in cursor.execute('SELECT * FROM UserSessionTokens'):
        ic(row)

    print(f"{'-'*18} Credentials {'-'*18}")
    for row in cursor.execute('SELECT * FROM Credentials'):
        ic(row)

def test_signup():
    create_account(data=UserInfo(
        email="customer1@gmail.com",
        birthday="2005-09-21",
        password="somepass12",
        first_name="alan",
        last_name="beth"
    ), permissionLevel=10)

def test_signup_manager():
    create_account(data=UserInfo(
        email="manager@roms.com",
        birthday="2005-09-21",
        password="manager%password122",
        first_name="ger",
        last_name="mana"
    ), permissionLevel=255)

def test_login():
    login(get_userid_from_email("manager@roms.com"), "manager%password122")

def create_database_tables():
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS Userdata(
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email NVARCHAR(50) NOT NULL UNQIUE,
                first_name NVARCHAR(50) NOT NULL,
                last_name NVARCHAR(50) NOT NULL,
                birthday NVARCHAR(50) NOT NULL,
                permission_level INTEGER
            )
        '''
    )
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS UserSessionTokens(
                user_id INTEGER NOT NULL,
                token NVARCHAR(255) NOT NULL,

                PRIMARY KEY (user_id, token)
            )
        '''
    )
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS Credentials(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                password NVARCHAR(50) NOT NULL
            )
        '''
    )
    db.commit()

if __name__ == '__main__':

    create_database_tables()
    db.commit()
    # Create management account

    #test_signup_manager()
    #test_signup()
    #test_login()

    dat = get_user(get_userid_from_email("manager@roms.com"))
    dat.first_name = "sabii"
    dat.commit()


    test_viewall()
    #get_user(1).get_birthday_object()
