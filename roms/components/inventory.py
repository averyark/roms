# @fileName: inventory.py
# @creation_date: 01/10/2024
# @authors: averyark

from datetime import date, time
from typing import Annotated, Literal, Optional, List, TypeVar
from fastapi import Depends, Query
from pydantic import BaseModel
from fastapi import HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import paginate as api_pagiante
from fastapi_pagination import Page, set_page
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from fastapi_pagination.customization import CustomizedPage, UseParamsFields, UseIncludeTotal

from ..database import session, to_dict

from ..database.models import ItemModel, IngredientModel, ItemIngredientModel, InventoryStockModel, InventoryStockBatchModel
from ..database.schemas import IngredientItem, IngredientItemCreate, Ingredient, IngredientCreate, Item, ItemCreate, ItemBase, IngredientItemCreateNoItemIdKnowledge, Stock, StockCreate, StockBatchCreate, StockBatch
from ..account import authenticate, validate_role
from ..api import app
from ..user import User
from fastapi_pagination.utils import disable_installed_extensions_check

disable_installed_extensions_check()

class ItemPage(ItemBase):
    item_id: int

class ItemGetIngredient(BaseModel):
    name: str
    ingredient_id: int

class ItemGet(ItemBase):
    item_id: int
    ingredients: List[ItemGetIngredient] = None

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
        )

        session.add(db_ingredient_item)
        session.commit()
        session.refresh(db_ingredient_item)

    return in_db_item

def get_item(item_id: int):
    return session.query(ItemModel).filter(ItemModel.item_id == item_id).one()

@app.get('/inventory/items/get', tags=['inventory'])
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
                        ItemIngredientModel.ingredient_id
                    ).where(
                        row.item_id == ItemIngredientModel.item_id
                    )) .all():

                ingredient_row = session.execute(
                    select(
                        IngredientModel.name,
                    ).where(
                        IngredientModel.ingredient_id == ingredient.ingredient_id
                    )).one()

                row_dict["ingredients"].append({
                    "name": ingredient_row[0],
                    "ingredient_id": ingredient.ingredient_id
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
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    fields: ItemCreate
):
    'Add a new recipe and item, new ingredients should be created ahead using /inventory/ingredients/add'
    try:
        new_item = create_item(fields)
        return {"msg": "Item added successfully", "item": new_item}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to add Item: {str(e)}")

#TODO: @YandreZzz done and tested
@app.patch('/inventory/items/edit', tags=['inventory'])
async def inventory_edit_item(
    user: Annotated[User, Depends(validate_role(roles=['Manager', 'Chef']))],
    item_id: int,
    price: Optional[float] = None,
    name: Optional[str] = None,
    picture_link: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None
):
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if name:
        item.name = name
    if price:
        item.price = price
    if description:
        item.description = description
    if category:
        item.category = category
    if picture_link:
        item.picture_link = picture_link

    session.commit()
    session.refresh(item)
    return {"msg": "Item edited successfully"}

#TODO: @YandreZzz done and tested
@app.delete('/inventory/items/delete', tags=['inventory'])
async def inventory_delete_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    item_id: int
):
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    session.delete(item)
    session.commit()

    return {"msg": f"Item with ID {item_id} deleted successfully"}

def get_ingredient(ingredient_id: int):
    return session.query(IngredientModel).filter(IngredientModel.ingredient_id == ingredient_id).one()

def create_ingredient(ingredient: IngredientCreate):
    in_db_ingredient = session.query(IngredientModel).filter(
        IngredientModel.name == ingredient.name
    ).one_or_none()

    if in_db_ingredient:
        return

    db_ingredient = IngredientModel(
        name=ingredient.name,
    )
    session.add(db_ingredient)
    session.commit()
    session.refresh(db_ingredient)
    return db_ingredient

#TODO: @YandreZzz Done and tested
@app.post('/inventory/ingredients/add', tags=['inventory'])
async def ingredients_add_ingredient(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    fields: IngredientCreate
):
    try:
        new_ingredient = create_ingredient(fields)
        return {"msg": "Ingredient added successfully", "ingredient": new_ingredient}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_status.HTTP_400_BAD_REQUEST_BAD_REQUEST, detail=f"Failed to add ingredient: {str(e)}")

#TODO: @YandreZzz Done and tested
@app.patch('/inventory/ingredients/edit', tags=['inventory'])
async def ingredients_edit_ingredient(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    ingredient_id: int,
    name: Optional[str] = None,
):
    ingredient = get_ingredient(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    if name:
        ingredient.name = name

    session.commit()
    session.refresh(ingredient)
    return {"msg": "Ingredient edited successfully"}

#TODO: @YandreZzz Done and tested
@app.delete('/inventory/ingredients/delete', tags=['inventory'])
async def ingredients_delete_ingredient(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    ingredient_id: int
):
    ingredient = get_ingredient(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    session.delete(ingredient)
    session.commit()

    return {"msg": f"Item with ID {ingredient_id} deleted successfully"}

def get_stock(stock_id: int):
    return session.query(InventoryStockModel).filter(InventoryStockModel.stock_id == stock_id).one()

def create_stock(stock: StockCreate):
    db_stock = InventoryStockModel(
        stock_batch_id = stock.stock_batch_id,
        ingredient_id = stock.ingredient_id,
        expiry_date = stock.expiry_date,
        status = stock.status
    )
    session.add(db_stock)
    session.commit()
    session.refresh(db_stock)
    return db_stock

@app.get('/inventory/stock/get', tags=['inventory'])
async def stock_get_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_id: int = None
):
    if stock_id:

        stock = get_stock(stock_id)
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

        return stock

    return session.query(InventoryStockModel).all()

@app.post('/inventory/stock/add', tags=['inventory'])
async def stock_add_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_batch_id: int,
    ingredient_id: int,
    expiry_date: date,
    stock_status: Literal["Ready to Use", "Open", "Used"]
):
    try:
        new_stock = create_stock(StockCreate(stock_batch_id=stock_batch_id, ingredient_id=ingredient_id, expiry_date=expiry_date, status=stock_status))
        return {"msg": "Stock added successfully", "stock": new_stock}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to add stock: {str(e)}")

@app.patch('/inventory/stock/edit', tags=['inventory'])
async def stock_edit_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_id: int,
    stock_batch_id: Optional[int] = None,
    ingredient_id: Optional[int] = None,
    expiry_date: Optional[date] = None,
    stock_status: Optional[Literal['Ready to Use', 'Open', "Used"]] = None
):
    stock = get_stock(stock_id)
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    if stock_batch_id:
        stock.stock_batch_id = stock_batch_id
    if ingredient_id:
        stock.ingredient_id = ingredient_id
    if expiry_date:
        stock.expiry_date = expiry_date
    if stock_status:
        stock.status = stock_status

    session.commit()
    session.refresh(stock)
    return {"msg": "Stock edited successfully"}

@app.delete('/inventory/stock/remove', tags=['inventory'])
async def stock_remove_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_id: int
):
    stock = get_stock(stock_id)
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    session.delete(stock)
    session.commit()

    return {"msg": f"Stock with ID {stock_id} deleted successfully"}

def get_stock_batch(stock_batch_id: int):
    return session.query(InventoryStockBatchModel).filter(InventoryStockBatchModel.stock_batch_id == stock_batch_id).one()

def create_stock_batch(stock_batch: StockBatchCreate):
    db_stock_batch = InventoryStockBatchModel(
        acquisition_date = stock_batch.acquisition_date,
    )
    session.add(db_stock_batch)
    session.commit()
    session.refresh(db_stock_batch)
    return db_stock_batch

@app.get('/inventory/stock_batch/get', tags=['inventory'])
async def stock_batch_get_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_batch_id: int = None
):
    if stock_batch_id:

        stock_batch = get_stock_batch(stock_batch_id)
        if not stock_batch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

        return stock_batch

    return session.query(InventoryStockBatchModel).all()

@app.post('/inventory/stock_batch/add', tags=['inventory'])
async def stock_batch_add_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    acquisition_date: date
):
    try:
        new_stock_batch = create_stock_batch(StockBatchCreate(acquisition_date=acquisition_date))
        return {"msg": "Stock batch added successfully", "stock_batch": new_stock_batch}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_status.HTTP_400_BAD_REQUEST_BAD_REQUEST, detail=f"Failed to add stock batch: {str(e)}")

@app.patch('/inventory/stock_batch/edit', tags=['inventory'])
async def stock_batch_edit_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_batch_id: int,
    acquisition_date: Optional[date] = None
):
    stock_batch = get_stock_batch(stock_batch_id)
    if not stock_batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock batch not found")

    if acquisition_date:
        stock_batch.acquisition_date = acquisition_date

    session.commit()
    session.refresh(stock_batch)
    return {"msg": "Stock batch edited successfully"}

@app.delete('/inventory/stock_batch/remove', tags=['inventory'])
async def stock_batch_remove_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_batch_id: int
):
    stock_batch = get_stock_batch(stock_batch_id)
    if not stock_batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock batch not found")

    session.delete(stock_batch)
    session.commit()

    return {"msg": f"Stock batch with ID {stock_batch_id} deleted successfully"}

@app.get('/inventory/items/available', tags=['inventory'])
async def is_item_available(
    user: Annotated[
        User, Depends(authenticate)
    ],
    item_id: int
):
    '''
    Check for stock availability
    '''
    item = get_item(item_id=item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    today_date = date.today()

    missing = []

    for ingredient in item.ingredients:
        # Search for stock
        ingredient_stock = session.query(InventoryStockModel).filter(InventoryStockModel.ingredient_id == ingredient.ingredient_id).all()

        has_stock = False

        ingredient = get_ingredient(ingredient_id=ingredient.ingredient_id)

        for stock in ingredient_stock:
            if stock.status in ['Ready to Use', "Open"] and today_date < stock.expiry_date:
                has_stock = True
                break

        if not has_stock:
            missing.append({
                "id": ingredient.ingredient_id,
                "name": ingredient.name
            })

    if len(missing) > 0:
        return {
            "available": False,
            "missing": missing
        }

    return {
        "available": True
    }
