# @fileName: signup.py
# @creation_date: 14/09/2024
# @authors: averyark

from user import User

def signup(*arg) -> User:
    try:
        User(*arg)
    except ValueError as err:
        print(err.args[0])

signup("Alwin", "Ting", "alwin@gmail.com", "21092005")
