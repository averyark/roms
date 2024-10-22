# @fileName: main.py
# @creation_date: 20/09/2024
# @authors: averyark

from PIL import Image
import zpl
from escpos import cli, printer
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
        inventory.IngredientCreate(name='Tea Powder'),
        inventory.IngredientCreate(name='Hot Water'),
        inventory.IngredientCreate(name='Milk'),
        inventory.IngredientCreate(name='Milo Powder'),
        inventory.IngredientCreate(name='Rose Syrup'),
        inventory.IngredientCreate(name='Coconut Rice'),
        inventory.IngredientCreate(name='Sambal'),
        inventory.IngredientCreate(name='Anchovies'),
        inventory.IngredientCreate(name='Flat Rice Noodles'),
        inventory.IngredientCreate(name='Prawns'),
        inventory.IngredientCreate(name='Egg'),
        inventory.IngredientCreate(name='Flour'),
        inventory.IngredientCreate(name='Dhal Curry')
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
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=2,
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
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=2,
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
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=2,
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
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=7,
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=8,
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
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=10,
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=11,
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
            ),
            inventory.IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=13,
            )
        ]
    ))

if __name__ == '__main__':
    # instance = printer.Dummy()
    # instance.text(txt="Hello World")
    # instance.cut()
    # with open("./test.bin", "wb") as file:
    #      file.write(instance.output)

    # l = zpl.Label(100,60, dpmm=6)
    # l.origin(0, 4)
    # l.write_text('Abu Bhavin Calvin', char_height=6, char_width=4, line_width=60, justification='C')
    # l.endorigin()
    # l.origin(0, 12)
    # l.write_text('(Owned by Abu Bhavin Calvin Sdn Bhd)', char_height=3, char_width=2, line_width=60, justification='C', font='A')
    # l.endorigin()
    # l.origin(0, 15)
    # l.write_text('Co.No: 123456-A', char_height=3, char_width=2, line_width=60, justification='C', font='A')
    # l.endorigin()
    # l.origin(0, 18)
    # l.write_text('SST.No: W-12-3456-78900000', char_height=3, char_width=2, line_width=60, justification='C', font='A')
    # l.endorigin()

    # l.origin(0, 21)
    # l.write_text('INVOICE', char_height=3, char_width=2, line_width=60, justification='C', font='A')
    # l.endorigin()

    # with open("./test.zpl", "w") as file:
    #     file.write(l.dumpZPL())

    #session.query(UserModel).delete()
    #session.commit()

    #test_signup_manager()
    #test_signup()

    #order.delete_all_orders()

    #test_viewall()

    test_create_ingredients()
    test_create_item()
    pass
