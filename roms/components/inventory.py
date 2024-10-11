# @fileName: inventory.py
# @creation_date: 01/10/2024
# @authors: averyark

from typing import Annotated, Literal, Optional, List
from fastapi import Depends
from pydantic import BaseModel
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import paginate as api_pagiante
from fastapi_pagination import Page, set_page
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ..database import session, to_dict, create_item
from ..database.models import ItemModel, IngredientModel, ItemIngredientModel
from ..database.schemas import IngredientItem, IngredientItemCreate, Ingredient, IngredientCreate, Item, ItemCreate, ItemBase
from ..account import authenticate, validate_role
from ..api import app
from ..user import User

from fastapi_pagination.utils import disable_installed_extensions_check
disable_installed_extensions_check()

class InventoryItemUpdate(BaseModel):
    item_id: Optional[int] = None
    price: Optional[float] = None
    name: Optional[str] = None
    picture_link: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class ItemGetIngredient(BaseModel):
    name: str
    quantity: float
    unit: str

class ItemGet(ItemBase):
    item_id: int
    ingredients: List[ItemGetIngredient] = None

class ItemPage(ItemBase):
    item_id: int

@app.post('/inventory/items/get', tags=['inventory'])
async def inventory_get(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef', 'Cashier', 'Customer']))
    ],
    filter: str = None,
) -> Page[ItemGet]:
    if user.get_role() in ['Manager', 'Chef']:
        query = select(
            ItemModel.item_id,
            ItemModel.name,
            ItemModel.price,
            ItemModel.description,
            ItemModel.category,
            ItemModel.picture_link,
        ).order_by(ItemModel.item_id)

        set_page(Page[ItemPage])
        results = paginate(session, query) #session.execute(query)

        items = []

        for row in results.items:

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
                    )).all():

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

        set_page(Page[ItemGet])
        return api_pagiante(items)
    else:
        return paginate(session, select(
            ItemModel,
        ).order_by(ItemModel.item_id))


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

#TODO: @YandreZzz
@app.patch('/inventory/items/update', tags=['inventory'])
async def inventory_update_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    item_id: int,
    update_fields: InventoryItemUpdate
):
    pass

#TODO: @YandreZzz
@app.delete('/inventory/items/delete', tags=['inventory'])
async def inventory_delete_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    ingredient_id: int
):
    pass

#TODO: @YandreZzz
@app.post('/inventory/ingredients/add', tags=['inventory'])
async def ingredients_add_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    fields: IngredientCreate
):
    pass

#TODO: @YandreZzz
@app.patch('/inventory/ingredients/update', tags=['inventory'])
async def ingredients_update_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    ingredient_id: int,
    update_fields: InventoryItemUpdate
):
    pass

#TODO: @YandreZzz
@app.delete('/inventory/ingredients/delete', tags=['inventory'])
async def ingredients_delete_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    ingredient_id: int
):
    pass
