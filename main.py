# @fileName: main.py
# @creation_date: 20/09/2024
# @authors: averyark

from asyncio import run_coroutine_threadsafe
from roms.account import login, signup, create_account, get_userid_from_email, swagger_login
from roms.database.models import UserModel, IngredientModel, ItemModel, ItemIngredientModel
from roms.database import session, UserCreate, ItemCreate, IngredientCreate, IngredientItemCreate, create_item, create_item_ingredient, create_ingredient, get_item, get_ingredient, to_dict

from roms import userPermissionRanks
from roms import app
from roms.user import get_user
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

def test_create_item():
    # Create the ingredients
    create_ingredient(IngredientCreate(
        name='Kopi Powder',
        stock_quantity=1252,
        unit='g',
    ))
    create_ingredient(IngredientCreate(
        name='Hot Water',
        stock_quantity=float('inf'),
        unit='ml'
    ))
    # Create the items
    item_id = create_item(ItemCreate(
        price=6.3,
        name='Kopi Beng',
        picture_link='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgYbqhuVAja_fGSBITWC7qCKjCsa0jcN5_0w&s',
        description='yummy kopi mmmm',
        category='Beverage',
    )).item_id
    # Create ingredient-item correlation
    create_item_ingredient(IngredientItemCreate(
        item_id=item_id,
        ingredient_id=1,
        quantity=10
    ))
    create_item_ingredient(IngredientItemCreate(
        item_id=item_id,
        ingredient_id=2,
        quantity=200
    ))

    print(get_item(1))

if __name__ == '__main__':

    #session.query(UserModel).delete()
    #session.commit()

    #test_signup_manager()
    #test_signup()

    #test_viewall()

    #test_create_item()
    #print(to_dict(get_item(1)))
    #print(to_dict(get_item(1)))
    pass
