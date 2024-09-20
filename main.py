from roms import login, get_userid_from_email
from roms import signup
from roms import userPermissionRanks

import sqlite3
credentialsPath = "mock-database.db"
db = sqlite3.connect(credentialsPath)
cursor = db.cursor()

def test_viewall():
    for row in cursor.execute('SELECT * FROM Userdata'):
        print(row)

    for row in cursor.execute('SELECT * FROM UserSessionTokens'):
        print(row)

    for row in cursor.execute('SELECT * FROM Credentials'):
        print(row)

def test_signup():
    signup({
        'firstName': 'first',
        'lastName': 'last',
        'email': 'email@gmail.com',
        'birthday': '2005-09-21',
        'password': "SomePassword@123456",
    }, userPermissionRanks.get("Manager"))

def test_login():
    login(get_userid_from_email("email@gmail.com"), "SomePassword@12345")

if __name__ == '__main__':
    test_viewall()
