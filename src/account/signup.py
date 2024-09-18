# @fileName: signup.py
# @creation_date: 14/09/2024
# @authors: averyark

from user import User
import user
from icecream import ic

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

# signup({
#     "firstName": "alwin",
#     "lastName": "ting",
#     "birthday": "2005-09-21",
#     "email": "alwin@gmail.com"
# })
