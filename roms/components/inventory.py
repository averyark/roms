# @fileName: inventory.py
# @creation_date: 01/10/2024
# @authors: averyark

from typing import Annotated, Literal, Optional, List
from fastapi import Depends
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import paginate as api_pagiante
from fastapi_pagination import Page, set_page
from sqlalchemy import select
from sqlalchemy.orm import joinedload


from ..database import session, to_dict, create_item, create_ingredient, get_item, get_ingredient
from ..database.models import ItemModel, IngredientModel, ItemIngredientModel
from ..database.schemas import IngredientItem, IngredientItemCreate, Ingredient, IngredientCreate, Item, ItemCreate, ItemBase
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

class InventoryIngredientUpdate(BaseModel):
    name: Optional[str] = None
    stock_quantity: Optional[float] = None
    unit: Optional[str] = None

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