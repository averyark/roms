# @fileName: inventory.py
# @creation_date: 01/10/2024
# @authors: averyark

from typing import Annotated, Literal, Optional, List, TypeVar
from fastapi import Depends, Query
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import paginate as api_pagiante
from fastapi_pagination import Page, set_page
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from fastapi_pagination.customization import CustomizedPage, UseParamsFields, UseIncludeTotal

from ..database import session, to_dict

from ..database.models import ItemModel, IngredientModel, ItemIngredientModel
from ..database.schemas import IngredientItem, IngredientItemCreate, Ingredient, IngredientCreate, Item, ItemCreate, ItemBase, IngredientItemCreateNoItemIdKnowledge
from ..account import authenticate, validate_role
from ..api import app
from ..user import User
from fastapi_pagination.utils import disable_installed_extensions_check

disable_installed_extensions_check()

class InventoryItemUpdate(BaseModel):
    price: Optional[float] = None
    name: Optional[str] = None
    picture_link: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [{}]
        }
    }

class InventoryIngredientUpdate(BaseModel):
    name: Optional[str] = None
    stock_quantity: Optional[float] = None
    unit: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [{}]
        }
    }

class ItemGetIngredient(BaseModel):
    name: str
    quantity: int
    unit: str

class ItemGet(ItemBase):
    item_id: int
    ingredients: List[ItemGetIngredient] = None

class ItemPage(ItemBase):
    item_id: int

def create_item_ingredient(item_ingredient: IngredientItemCreate):
    db_item_ingredient = ItemIngredientModel(
        item_id=item_ingredient.item_id,
        ingredient_id=item_ingredient.ingredient_id,
        quantity=item_ingredient.quantity
    )
    session.add(db_item_ingredient)
    session.commit()
    session.refresh(db_item_ingredient)
    return db_item_ingredient

def create_item(item: ItemCreate):
    in_db_item = session.query(ItemModel).filter(ItemModel.name == item.name).one_or_none()

    # check if the item ingredients is in the itemingredient db table
    if in_db_item is None:
        # create the item because it doesn't exist
        in_db_item = ItemModel(
            price=item.price,
            name=item.name,
            picture_link=item.picture_link,
            description=item.description,
            category=item.category,
        )
        session.add(in_db_item)
        session.commit()
        session.refresh(in_db_item)

    for ingredient_item in item.ingredients:
        in_db_ingredient_item = session.query(ItemIngredientModel).filter(
            and_(
                ItemIngredientModel.item_id == in_db_item.item_id,
                ItemIngredientModel.ingredient_id == ingredient_item.ingredient_id
            )
        ).one_or_none()

        # continue if the ingredient already exist
        if in_db_ingredient_item:
            continue

        db_ingredient_item = ItemIngredientModel(
            ingredient_id=ingredient_item.ingredient_id,
            item_id = in_db_item.item_id,
            quantity=ingredient_item.quantity
        )

        session.add(db_ingredient_item)
        session.commit()
        session.refresh(db_ingredient_item)

    return in_db_item

def create_ingredient(ingredient: IngredientCreate):
    in_db_ingredient = session.query(IngredientModel).filter(
        IngredientModel.name == ingredient.name
    ).one_or_none()

    if in_db_ingredient:
        return

    db_ingredient = IngredientModel(
        name=ingredient.name,
        stock_quantity=ingredient.stock_quantity,
        unit=ingredient.unit
    )
    session.add(db_ingredient)
    session.commit()
    session.refresh(db_ingredient)
    return db_ingredient

def get_item(item_id: int):
    return session.query(ItemModel).filter(ItemModel.item_id == item_id).one()

def get_ingredient(ingredient_id: int):
    return session.query(IngredientModel).filter(IngredientModel.ingredient_id == ingredient_id).one()

T = TypeVar("T")

CustomPage = CustomizedPage[
    Page[T],
    UseIncludeTotal(False),
]

@app.post('/inventory/items/get', tags=['inventory'])
async def inventory_get(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef', 'Cashier', 'Customer']))
    ],
    search_keyword: str = None
) -> List[ItemGet]:

    if user.get_role() in ['Manager', 'Chef']:
        if search_keyword:
            search_keyword = f"%{search_keyword}%"
            query = session.query(ItemModel).where(
                ItemModel.name.ilike(search_keyword) |
                ItemModel.description.ilike(search_keyword) |
                ItemModel.category.ilike(search_keyword)
            )
        else:
            query = session.query(ItemModel)

        items = []

        for row in query.all():

            row_dict = {}
            row_dict["ingredients"] = []

            row_dict["item_id"] = row.item_id
            row_dict["name"] = row.name
            row_dict["price"] = row.price
            row_dict["description"] = row.description
            row_dict["category"] = row.category
            row_dict["picture_link"] = row.picture_link

            for ingredient in session.execute(
                    select(
                        ItemIngredientModel.ingredient_id, ItemIngredientModel.quantity
                    ).where(
                        row.item_id == ItemIngredientModel.item_id
                    )) .all():

                ingredient_row = session.execute(
                    select(
                        IngredientModel.name,
                        IngredientModel.unit
                    ).where(
                        IngredientModel.ingredient_id == ingredient.ingredient_id
                    )).one()

                row_dict["ingredients"].append({
                    "name": ingredient_row[0],
                    "unit": ingredient_row[1],
                    "quantity": ingredient.quantity
                })

            items.append(ItemGet(**row_dict))

        return items
    else:
        items = []

        for item in session.query(ItemModel).order_by(ItemModel.item_id).all():
            items.append(ItemGet(
                item_id = item.item_id,
                name = item.name,
                price = item.price,
                description = item.description,
                category = item.category,
                picture_link = item.picture_link
            ))

        return items



@app.post('/inventory/items/add', tags=['inventory'])
async def inventory_add_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    fields: ItemCreate
):
    'Add a new recipe and item, new ingredients should be created ahead using /inventory/ingredients/add'
    create_item(fields)
    pass

#TODO: @YandreZzz done and tested
@app.patch('/inventory/items/update', tags=['inventory'])
async def inventory_update_item(
    user: Annotated[User, Depends(validate_role(roles=['Manager']))],
    item_id: int,
    update_fields: InventoryItemUpdate
):
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if update_fields.name:
        item.name = update_fields.name
    if update_fields.price:
        item.price = update_fields.price
    if update_fields.description:
        item.description = update_fields.description
    if update_fields.category:
        item.category = update_fields.category
    if update_fields.picture_link:
        item.picture_link = update_fields.picture_link

    session.commit()
    session.refresh(item)
    return {"msg": "Item updated successfully"}

#TODO: @YandreZzz done and tested
@app.delete('/inventory/items/delete', tags=['inventory'])
async def inventory_delete_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    item_id: int
):
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    session.delete(item)
    session.commit()

    return {"msg": f"Item with ID {item_id} deleted successfully"}

#Helper function for deleting an item
#async def delete_item(item_id: int):
    #await database.delete_item(item_id)

#TODO: @YandreZzz Done and tested
@app.post('/inventory/ingredients/add', tags=['inventory'])
async def ingredients_add_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    fields: IngredientCreate
):
    try:
        new_ingredient = create_ingredient(fields)
        return {"msg": "Ingredient added successfully", "ingredient": new_ingredient}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add ingredient: {str(e)}")

#TODO: @YandreZzz Done and tested
@app.patch('/inventory/ingredients/update', tags=['inventory'])
async def ingredients_update_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    ingredient_id: int,
    update_fields: InventoryIngredientUpdate
):
    ingredient = get_ingredient(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    if update_fields.name:
        ingredient.name = update_fields.name
    if update_fields.stock_quantity:
        ingredient.stock_quantity = update_fields.stock_quantity
    if update_fields.unit:
        ingredient.unit = update_fields.unit

    session.commit()
    session.refresh(ingredient)
    return {"msg": "Ingredient updated successfully"}


#TODO: @YandreZzz Done and tested
@app.delete('/inventory/ingredients/delete', tags=['inventory'])
async def ingredients_delete_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    ingredient_id: int
):
    ingredient = get_ingredient(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    session.delete(ingredient)
    session.commit()

    return {"msg": f"Item with ID {ingredient_id} deleted successfully"}
