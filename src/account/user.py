# @fileName: user.py
# @creation_date: 14/09/2024
# @authors: averyark

import pendulum
import datetime
import re
from icecream import ic

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

class User:
    def __init__(self, data):
        self.firstName = data.firstName
        self.lastName = data.lastName
        self.email = data.email
        self.birthday = data.birthday

    def __str__(self):
        return f"{self.getName()}"

    def getBirthday(self):
        return pendulum.from_format(self.birthday, "YYYY-MM-DD")

    def getName(self):
        return f"{self.lastName} {self.firstName}"

# jianyi = User("Jian Yi", "Ting", "alwin@gmail.com", "2005-09-21")

def validateUserData(data: dict):
    if not dict(data):
        raise TypeError("data must be a dictionary")

    validatePassword(data.get("password"))
    validateName(data.get("firstName"))
    validateName(data.get("lastName"))
    validateDate(data.get("birthday"))
    validateEmail(data.get("email"))

def __init__():
     print("loaded")
