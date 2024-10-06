# @fileName: test_user.py
# @creation_date: 18/09/2024
# @authors: averyark

from pydantic import BaseModel
from roms.validate import validate_user_data
import unittest
import pytest

class UserInfo(BaseModel):
    birthday: str
    first_name: str
    last_name: str
    email: str
    password: str

# birthday constraint test
def test_validateBirthday():
    validate_user_data(UserInfo(
        birthday='2005-09-21',
        email='first@gmail.com',
        password='somepassword@12345678',
        first_name='first',
        last_name='last'
    ))

    # This is not valid in py 3.9
    # reference to test: https://github.com/averyark/roms/actions/runs/10922064922/job/30315543710
    # validate_user_data(UserInfo(
    #     'birthday': '20050921',
    #     email='first@gmail.com',
    #     first_name='first',
    #     last_name='last'
    # ))

    try:
        validate_user_data(UserInfo(
            birthday='09-21-2005',
            email='first@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid birthday")

    try:
        validate_user_data(UserInfo(
            birthday='09-2005-21',
            email='first@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid birthday")

# email constraint test
def test_validateEmail():

    validate_user_data(UserInfo(
        birthday='2005-09-21',
        email='first@gmail.com',
        password='somepassword@12345678',
        first_name='first',
        last_name='last'
    ))
    validate_user_data(UserInfo(
        birthday='2005-09-21',
        email='first.last@gmail.com',
        password='somepassword@12345678',
        first_name='first',
        last_name='last'
    ))

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email=f'{"a"*50}@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        validate_user_data(UserInfo(
            birthday= '2005-09-21',
            email=1,
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first_last@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first@gmail',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

# name constraint test
def test_validateName():
    validate_user_data(UserInfo(
        birthday='2005-09-21',
        email='first.last@gmail.com',
        password='somepassword@12345678',
        first_name='first',
        last_name='last'
    ))
    validate_user_data(UserInfo(
        birthday='2005-09-21',
        email='first.last@gmail.com',
        password='somepassword@12345678',
        first_name='first middle',
        last_name='last'
    ))

    validate_user_data(UserInfo(
        birthday='2005-09-21',
        email='first.last@gmail.com',
        password='somepassword@12345678',
        first_name='first middle',
        last_name='last last2'
    ))

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email=1,
            password='somepassword@12345678',
            first_name='first.',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first.last@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last.'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first.last@gmail.com',
            password='somepassword@12345678',
            first_name='a'*51,
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first.last@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='a'*51
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")
    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first.last@gmail.com',
            password='somepassword@12345678',
            first_name=1,
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first.last@gmail.com',
            password='somepassword@12345678',
            first_name=1,
            last_name=2,
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

# password constraint test
def test_validatePassword():
    validate_user_data(UserInfo(
        birthday='2005-09-21',
        email='first.last@gmail.com',
        password='somepassword@12345678',
        first_name='first',
        last_name='last'
    ))
    validate_user_data(UserInfo(
        birthday='2005-09-21',
        email='first.last@gmail.com',
        password='somepassword12345678',
        first_name='first middle',
        last_name='last'
    ))

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            password='abc123',
            email='first.last@gmail.com',
            first_name='first middle',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid password")

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first.last@gmail.com',
            password='somepass@123XÆ ',
            first_name='first middle',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid password")

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first.last@gmail.com',
            password="a"*51,
            first_name='first middle',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid password")

    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first.last@gmail.com',
            password="12345678",
            first_name='first middle',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid password")


    try:
        validate_user_data(UserInfo(
            birthday='2005-09-21',
            email='first.last@gmail.com',
            password="abcdefgh",
            first_name='first middle',
            last_name='last'
        ))
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid password")
