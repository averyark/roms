# @fileName: signup.py
# @creation_date: 14/09/2024
# @authors: averyark

from user import User
import user
from icecream import ic
import credentials

# TODO: USE SQLITE3
import shelve

userdataPath = "mock-database/userdata"

def signup(data) -> User:
    try:
        user.validateUserData(data)
    except Exception as err:
        print("Error occurred during signup:")
        print("-"*15, " Exception ", "-"*15)
        print(err)
        print("-"*40)
    else:
        # add to database
        ic(data)
        with shelve.open(userdataPath) as userdata:
            if userdata[data.email]:
                print(f"{data.email} already exist in the userdata database")
                pass

            credentials.setCredentials(data.email, data.password)

            userdata[data.email] = {
                "firstName": data.firstName,
                "lastName": data.lastName,
                "birthday": data.birthday,
                "email": data.email
            }

# signup({
#     "firstName": "alwin",
#     "lastName": "ting",
#     "birthday": "2005-09-21",
#     "email": "alwin@gmail.com"
# })
