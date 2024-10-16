# @fileName: main.py
# @creation_date: 20/09/2024
# @authors: averyark

from asyncio import run_coroutine_threadsafe
from sqlalchemy import text

from roms.account import login, signup, create_account, get_userid_from_email, swagger_login
from roms.database.models import UserModel, IngredientModel, ItemModel, ItemIngredientModel

import roms.components.order as order
from roms.database import session
import roms.account as account
import roms.components.inventory as inventory

from roms import userPermissionRanks
from roms import app
from roms.user import get_user
from roms.credentials import pwd_context

from fastapi import Depends, FastAPI, HTTPException, status
from typing import Annotated

from icecream import ic

def test_signup():
    create_account(data=account.UserCreate(
        email='customer1@gmail.com',
        birthday='20050921',
        password='somepass12',
        first_name='alan',
        last_name='beth',
        permission_level=10
    ))

def test_signup_manager():
    create_account(data=account.UserCreate(
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

def test_create_ingredients():
    ingredients = [
        inventory.IngredientCreate(name='Tea Powder', stock_quantity=1000, unit='g'),
        inventory.IngredientCreate(name='Hot Water', stock_quantity=float('inf'), unit='ml'),
        inventory.IngredientCreate(name='Milk', stock_quantity=500, unit='ml'),
        inventory.IngredientCreate(name='Milo Powder', stock_quantity=1000, unit='g'),
        inventory.IngredientCreate(name='Rose Syrup', stock_quantity=1000, unit='ml'),
        inventory.IngredientCreate(name='Coconut Rice', stock_quantity=1000, unit='g'),
        inventory.IngredientCreate(name='Sambal', stock_quantity=500, unit='g'),
        inventory.IngredientCreate(name='Anchovies', stock_quantity=200, unit='g'),
        inventory.IngredientCreate(name='Flat Rice Noodles', stock_quantity=1000, unit='g'),
        inventory.IngredientCreate(name='Prawns', stock_quantity=200, unit='g'),
        inventory.IngredientCreate(name='Egg', stock_quantity=100, unit='pcs'),
        inventory.IngredientCreate(name='Flour', stock_quantity=1000, unit='g'),
        inventory.IngredientCreate(name='Dhal Curry', stock_quantity=500, unit='ml')
    ]

    for ingredient in ingredients:
        inventory.create_ingredient(ingredient)

def test_create_item():
    # Create the items
    inventory.create_item(inventory.ItemCreate(
        price=6.3,
        name='Kopi Beng',
        picture_link='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgYbqhuVAja_fGSBITWC7qCKjCsa0jcN5_0w&s',
        description='yummy kopi mmmm',
        category='Beverage',
        ingredients=[
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=1,
                quantity=10
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=2,
                quantity=200
            )
        ]
    ))

    inventory.create_item(inventory.ItemCreate(
        price=5.0,
        name='Teh Tarik',
        picture_link='https://example.com/teh_tarik.jpg',
        description='Traditional Malaysian pulled tea',
        category='Beverage',
        ingredients=[
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=3,
                quantity=10
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=2,
                quantity=150
            )
        ]
    ))

    inventory.create_item(inventory.ItemCreate(
        price=4.5,
        name='Milo Ais',
        picture_link='https://example.com/milo_ais.jpg',
        description='Iced chocolate malt drink',
        category='Beverage',
        ingredients=[
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=4,
                quantity=20
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=2,
                quantity=200
            )
        ]
    ))

    inventory.create_item(inventory.ItemCreate(
        price=12.0,
        name='Nasi Lemak',
        picture_link='https://example.com/nasi_lemak.jpg',
        description='Coconut rice with sambal, anchovies, and egg',
        category='Rice',
        ingredients=[
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=6,
                quantity=200
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=7,
                quantity=50
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=8,
                quantity=1
            )
        ]
    ))

    inventory.create_item(inventory.ItemCreate(
        price=15.0,
        name='Char Kway Teow',
        picture_link='https://example.com/char_kway_teow.jpg',
        description='Stir-fried flat rice noodles with prawns and egg',
        category='Noodle',
        ingredients=[
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=9,
                quantity=200
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=10,
                quantity=100
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=11,
                quantity=2
            )
        ]
    ))

    inventory.create_item(inventory.ItemCreate(
        price=10.0,
        name='Roti Canai',
        picture_link='https://example.com/roti_canai.jpg',
        description='Flaky flatbread served with dhal curry',
        category='Snacks',
        ingredients=[
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=12,
                quantity=100
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=13,
                quantity=50
            )
        ]
    ))

if __name__ == '__main__':

    #session.query(UserModel).delete()
    #session.commit()

    #test_signup_manager()
    #test_signup()

    #order.delete_all_orders()

    #test_viewall()

    test_create_ingredients()
    test_create_item()

    #test_create_item()
    pass
