# @fileName: main.py
# @creation_date: 20/09/2024
# @authors: averyark

from asyncio import run_coroutine_threadsafe
from roms.account import login, signup, create_account, get_userid_from_email, swagger_login
from roms.database import UserCreate, session, UserModel

from roms import userPermissionRanks
from roms import app
from roms.user import get_user
from roms.database import UserData, get_user_data_in_dict
from roms.credentials import pwd_context

from fastapi import Depends, FastAPI, HTTPException, status
from typing import Annotated

from icecream import ic

def test_signup():
    create_account(data=UserCreate(
        email='customer1@gmail.com',
        birthday='20050921',
        password='somepass12',
        first_name='alan',
        last_name='beth',
        permission_level=10
    ))

def test_signup_manager():
    create_account(data=UserCreate(
        email='manager@roms.com',
        birthday='20050921',
        password='manager%password122',
        first_name='ger',
        last_name='mana',
        permission_level=255
    ))

def test_viewall():

    for dat in session.query(UserModel).all():
        ic(dat.user_id, dat.email, dat.first_name, dat.last_name, dat.birthday, dat.permission_level)

def test_login():
    login(get_userid_from_email('manager@roms.com'), 'manager%password122')
if __name__ == '__main__':

    #session.query(UserModel).delete()
    #session.commit()

    #test_signup_manager()
    #test_signup()

    test_viewall()
