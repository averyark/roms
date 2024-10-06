# @fileName: test_user.py
# @creation_date: 18/09/2024
# @authors: averyark

from pydantic import BaseModel
#from roms.validate import validate_user_data
import unittest
import pytest
from roms.database import UserCreate

class UserInfo(BaseModel):
    birthday: str
    first_name: str
    last_name: str
    email: str
    password: str

# birthday constraint test
def test_validateBirthday():
    UserCreate(
        birthday='20050921',
        email='first@gmail.com',
        password='somepassword@12345678',
        first_name='first',
        last_name='last'
    )

    # This is not valid in py 3.9
    # reference to test: https://github.com/averyark/roms/actions/runs/10922064922/job/30315543710
    # UserCreate(
    #     'birthday': '20050921',
    #     email='first@gmail.com',
    #     first_name='first',
    #     last_name='last'
    # )

    try:
        UserCreate(
            birthday='18991205',
            email='first@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid birthday')

    try:
        UserCreate(
            birthday='29991205',
            email='first@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid birthday')

    try:
        UserCreate(
            birthday='09212005',
            email='first@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid birthday')

    try:
        UserCreate(
            birthday='09200521',
            email='first@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid birthday')

# email constraint test
def test_validateEmail():

    UserCreate(
        birthday='20050921',
        email='first@gmail.com',
        password='somepassword@12345678',
        first_name='first',
        last_name='last'
    )
    UserCreate(
        birthday='20050921',
        email='first.last@gmail.com',
        password='somepassword@12345678',
        first_name='first',
        last_name='last'
    )

    #max 64
    try:
        UserCreate(
            birthday='20050921',
            email=f'{"a"*65}@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid email')

    try:
        UserCreate(
            birthday= '20050921',
            email=1,
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid email')

    # NOTE: Now valid in #2
    # try:
    #     UserCreate(
    #         birthday='20050921',
    #         email='first_last@gmail.com',
    #         password='somepassword@12345678',
    #         first_name='first',
    #         last_name='last'
    #     )
    # except:
    #     pass
    # else:
    #     raise ValueError('Validation passed for invalid email')

    try:
        UserCreate(
            birthday='20050921',
            email='@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid email')

    try:
        UserCreate(
            birthday='20050921',
            email='first@gmail',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid email')

    try:
        UserCreate(
            birthday='20050921',
            email='first.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid email')

# name constraint test
def test_validateName():
    UserCreate(
        birthday='20050921',
        email='first.last@gmail.com',
        password='somepassword@12345678',
        first_name='first',
        last_name='last'
    )
    UserCreate(
        birthday='20050921',
        email='first.last@gmail.com',
        password='somepassword@12345678',
        first_name='first middle',
        last_name='last'
    )

    UserCreate(
        birthday='20050921',
        email='first.last@gmail.com',
        password='somepassword@12345678',
        first_name='first middle',
        last_name='last last2'
    )

    try:
        UserCreate(
            birthday='20050921',
            email=1,
            password='somepassword@12345678',
            first_name='first.',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid name')

    # NOTE: This is now valid in #2
    # try:
    #     UserCreate(
    #         birthday='20050921',
    #         email='first.last@gmail.com',
    #         password='somepassword@12345678',
    #         first_name='first',
    #         last_name='last.'
    #     )
    # except:
    #     pass
    # else:
    #     raise ValueError('Validation passed for invalid name')
    try:
        UserCreate(
            birthday='20050921',
            email='first.last@gmail.com',
            password='somepassword@12345678',
            first_name="",
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid name')

    try:
        UserCreate(
            birthday='20050921',
            email='first.last@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name=""
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid name')
    try:
        UserCreate(
            birthday='20050921',
            email='first.last@gmail.com',
            password='somepassword@12345678',
            first_name='a'*257,
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid name')

    try:
        UserCreate(
            birthday='20050921',
            email='first.last@gmail.com',
            password='somepassword@12345678',
            first_name='first',
            last_name='a'*257
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid name')
    try:
        UserCreate(
            birthday='20050921',
            email='first.last@gmail.com',
            password='somepassword@12345678',
            first_name=1,
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid name')

    try:
        UserCreate(
            birthday='20050921',
            email='first.last@gmail.com',
            password='somepassword@12345678',
            first_name=1,
            last_name=2,
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid name')

# password constraint test
def test_validatePassword():
    UserCreate(
        birthday='20050921',
        email='first.last@gmail.com',
        password='somepassword@12345678',
        first_name='first',
        last_name='last'
    )
    UserCreate(
        birthday='20050921',
        email='first.last@gmail.com',
        password='somepassword12345678',
        first_name='first middle',
        last_name='last'
    )

    try:
        UserCreate(
            birthday='20050921',
            password='abc123',
            email='first.last@gmail.com',
            first_name='first middle',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid password')

    try:
        UserCreate(
            birthday='20050921',
            email='first.last@gmail.com',
            password='somepass@123XÆ ',
            first_name='first middle',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid password')

    try:
        UserCreate(
            birthday='20050921',
            email='first.last@gmail.com',
            password='a'*51,
            first_name='first middle',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid password')

    try:
        UserCreate(
            birthday='20050921',
            email='first.last@gmail.com',
            password='12345678',
            first_name='first middle',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid password')


    try:
        UserCreate(
            birthday='20050921',
            email='first.last@gmail.com',
            password='abcdefgh',
            first_name='first middle',
            last_name='last'
        )
    except:
        pass
    else:
        raise ValueError('Validation passed for invalid password')
