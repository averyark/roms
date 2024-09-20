# @fileName: main.py
# @creation_date: 20/09/2024
# @authors: averyark

from roms import login, get_userid_from_email
from roms import signup
from roms import userPermissionRanks

from icecream import ic
import sqlite3
credentialsPath = "mock-database.db"
db = sqlite3.connect(credentialsPath)
cursor = db.cursor()

def test_viewall():
    for row in cursor.execute('SELECT * FROM Userdata'):
        ic(row)

    for row in cursor.execute('SELECT * FROM UserSessionTokens'):
        ic(row)

    for row in cursor.execute('SELECT * FROM Credentials'):
        ic(row)

def test_signup():
    signup({
        'firstName': 'first',
        'lastName': 'last',
        'email': 'email@gmail.com',
        'birthday': '2005-09-21',
        'password': "SomePassword@123456",
    }, userPermissionRanks.get("Manager"))

def test_login():
    login(get_userid_from_email("email@gmail.com"), "SomePassword@123456")

def create_database_tables():
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
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS UserSessionTokens(
                userId INTEGER NOT NULL,
                token NVARCHAR(255) NOT NULL,

                PRIMARY KEY (userId, token)
            )
        '''
    )
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

if __name__ == '__main__':
    create_database_tables()
    #test_signup()
    #test_login()
    test_viewall()
