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
from uuid import uuid4

from .table import verify_table_session
from ..database import session, to_dict
from ..database.models import ItemModel, IngredientModel, ItemIngredientModel, InventoryStockModel, InventoryStockBatchModel
from ..database.schemas import IngredientItem, IngredientItemCreate, Ingredient, IngredientCreate, Item, ItemCreate, ItemBase, IngredientItemCreateNoItemIdKnowledge, Stock, StockCreate, StockBatchCreate, StockBatch
from ..account import authenticate, authenticate_optional, validate_role
from ..api import app
from ..user import User
from fastapi_pagination.utils import disable_installed_extensions_check

disable_installed_extensions_check()

class ItemPage(ItemBase):
    item_id: str

class ItemGetIngredient(BaseModel):
    name: str
    ingredient_id: str

class ItemGet(ItemBase):
    item_id: str
    ingredients: List[ItemGetIngredient] = None

def create_item(item: ItemCreate):
    in_db_item = session.query(ItemModel).filter(ItemModel.name == item.name).one_or_none()

    # check if the item ingredients is in the itemingredient db table
    if in_db_item is None:
        # create the item because it doesn't exist
        in_db_item = ItemModel(
            item_id=item.item_id,
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

        print(ingredient_item)

        # continue if the ingredient already exist
        if in_db_ingredient_item:
            print(f'[Warn] This ingredient already exist for Item of {in_db_item.item_id} and Ingredient of {ingredient_item.ingredient_id}')
            continue

        in_db_ingredient_item = ItemIngredientModel(
            item_ingredient_id=str(uuid4()),
            ingredient_id=ingredient_item.ingredient_id,
            item_id = in_db_item.item_id,
        )

        session.add(in_db_ingredient_item)
        session.commit()
        session.refresh(in_db_ingredient_item)

    return in_db_item

def get_item(item_id: str):
    return session.query(ItemModel).filter(ItemModel.item_id == item_id).one_or_none()

@app.get('/inventory/items/get', tags=['items'])
async def inventory_get(
    user: Annotated[
        Optional[User], Depends(authenticate_optional)
    ],
    table_session_id: str = None,
    search_keyword: str = None
) -> List[ItemGet]:
    '''
    Authenticating is optional, which means a client that is not login to any account is allowed to use this api (IF) table_id is specified (for security)
    '''

    if not user and not table_session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    if not table_session_id is None:
        verify_table_session(table_session_id)

    if search_keyword:
        search_keyword = f"%{search_keyword}%"
        query = session.query(ItemModel).where(
            ItemModel.name.ilike(search_keyword) |
            ItemModel.description.ilike(search_keyword) |
            ItemModel.category.ilike(search_keyword)
        )
    else:
        query = session.query(ItemModel)

    if not user is None and user.get_role() in ['Manager', 'Chef']:
        items = []

        for row in query.all():
            if row.is_deleted:
                continue

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

        for item in query.order_by(ItemModel.item_id).all():
            if item.is_deleted:
                continue

            items.append(ItemGet(
                item_id = item.item_id,
                name = item.name,
                price = item.price,
                description = item.description,
                category = item.category,
                picture_link = item.picture_link
            ))

        return items

class IngredientItemName(BaseModel):
    ingredient_name: str

@app.post('/inventory/items/add', tags=['items'])
async def inventory_add_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    item_id: str,
    price: float,
    name: str,
    picture_link: str,
    description: str,
    category: Literal['All', 'Beverage', 'Rice', 'Noodle', 'Snacks'],
    ingredients: List[IngredientItemName]
):
    'Add a new recipe and item, new ingredients should be created ahead using /inventory/ingredients/add'

    in_db_item = session.query(ItemModel).filter(
        ItemModel.item_id==item_id
    ).one_or_none()

    in_db_item_ingredients = session.query(ItemIngredientModel).filter(
        ItemIngredientModel.item_id==item_id
    ).all()

    if in_db_item:
        if in_db_item.is_deleted:
            session.delete(in_db_item)
            for item_ingredient in in_db_item_ingredients:
                session.delete(item_ingredient)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='An item with this id already exist')

    new_ingredients = []

    for ingredient in ingredients:
        # translate to ids
        in_db_ingredient = session.query(IngredientModel).filter(
            IngredientModel.name==ingredient.ingredient_name
        ).one_or_none()

        if in_db_ingredient:
            new_ingredients.append(IngredientItemCreateNoItemIdKnowledge(
                ingredient_id=in_db_ingredient.ingredient_id
            ))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"This ingredient '{ingredient.ingredient_name}' does not exist")

    try:
        new_item = create_item(ItemCreate(
            item_id=item_id,
            price=price,
            name=name,
            picture_link=picture_link,
            description=description,
            category=category,
            ingredients=new_ingredients
        ))

        return {"msg": "Item added successfully", "item": to_dict(new_item)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to add Item: {str(e)}")

#TODO: @YandreZzz done and tested
@app.patch('/inventory/items/edit', tags=['items'])
async def inventory_edit_item(
    user: Annotated[User, Depends(validate_role(roles=['Manager', 'Chef']))],
    item_id: str,
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
# REWORKED to mark as Delete instead of deleting the instance
# This is because entries inside OrderItem/InventoryStock will lose
# the dependency if it is deleted from db, causing errors
@app.delete('/inventory/items/delete', tags=['items'])
async def inventory_delete_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    item_id: str
):
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    #session.delete(item)
    item.is_deleted = True
    session.commit()
    session.refresh(item)

    return {"msg": f"Item with ID {item_id} deleted successfully"}

def get_ingredient(ingredient_id: str):
    return session.query(IngredientModel).filter(IngredientModel.ingredient_id == ingredient_id).one_or_none()

@app.post('/inventory/ingredients/get', tags=['ingredients'])
async def get_ingredient(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    search_keyword: str = None
):
    if search_keyword:
        search_keyword = f"%{search_keyword}%"
        query = session.query(IngredientModel).where(
            IngredientModel.name.ilike(search_keyword) |
            IngredientModel.ingredient_id.ilike(search_keyword)
        )
    else:
        query = session.query(IngredientModel)


    ingredients = query.all()

    return ingredients

def create_ingredient(ingredient: IngredientCreate):
    in_db_ingredient = session.query(IngredientModel).filter(
        IngredientModel.name == ingredient.name
    ).one_or_none()

    # soft error
    if in_db_ingredient:
        print('[Warn] Attempting to create ingredient with overlapping name')
        return

    db_ingredient = IngredientModel(
        ingredient_id=str(uuid4()),
        name=ingredient.name,
    )
    session.add(db_ingredient)
    session.commit()
    session.refresh(db_ingredient)
    return db_ingredient

#TODO: @YandreZzz Done and tested
@app.post('/inventory/ingredients/add', tags=['ingredients'])
async def add_ingredient(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    name: str
):
    try:
        new_ingredient = create_ingredient(IngredientCreate(
            name=name
        ))
        return {"msg": "Ingredient added successfully", "ingredient": to_dict(new_ingredient)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to add ingredient: {str(e)}")

@app.post('/inventory/ingredients/bulk_add', tags=['ingredients'])
async def bulk_add_ingredient(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    ingredients: List[IngredientCreate]
):
    try:
        new_ingredients = []

        for ingredient in ingredients:
            new_ingredient = create_ingredient(ingredient)

            if not new_ingredient is None:
                new_ingredients.append(to_dict(new_ingredient))

        return {"msg": "Ingredients added successfully", "ingredients": new_ingredients}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to add ingredients: {str(e)}")

#TODO: @YandreZzz Done and tested
@app.patch('/inventory/ingredients/edit', tags=['ingredients'])
async def ingredients_edit_ingredient(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    ingredient_id: str,
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
# REWORKED to mark as Delete instead of deleting the instance
# This is because entries inside Item will lose
# the dependency if it is deleted from db, causing errors
@app.delete('/inventory/ingredients/delete', tags=['ingredients'])
async def delete_ingredient(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    ingredient_id: str
):
    ingredient = get_ingredient(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    #session.delete(ingredient)
    ingredient.is_deleted = False
    session.commit()
    session.refresh(ingredient)

    return {"msg": f"Item with ID {ingredient_id} deleted successfully"}

def get_stock(stock_id: str):
    return session.query(InventoryStockModel).filter(InventoryStockModel.stock_id == stock_id).one_or_none()

def create_stock(stock: StockCreate):
    db_stock = InventoryStockModel(
        stock_id = str(uuid4()),
        stock_batch_id = str(stock.stock_batch_id),
        ingredient_id = str(stock.ingredient_id),
        expiry_date = stock.expiry_date,
        status = stock.status
    )
    session.add(db_stock)
    session.commit()
    session.refresh(db_stock)
    return db_stock

@app.get('/inventory/stock/get', tags=['stock'])
async def stock_get_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_id: str = None
):
    if stock_id:

        stock = get_stock(stock_id)
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

        return stock

    return session.query(InventoryStockModel).all()

@app.post('/inventory/stock/add', tags=['stock'])
async def stock_add_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_batch_id: str,
    ingredient_id: str,
    expiry_date: date,
    stock_status: Literal["Ready to Use", "Open", "Used"]
):

    try:
        new_stock = create_stock(StockCreate(
            stock_batch_id=stock_batch_id,
            ingredient_id=ingredient_id,
            expiry_date=expiry_date,
            status=stock_status
        ))
        return {"msg": "Stock added successfully", "stock": to_dict(new_stock)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to add stock: {str(e)}")

@app.patch('/inventory/stock/edit', tags=['stock'])
async def stock_edit_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_id: str,
    stock_batch_id: Optional[str] = None,
    ingredient_id: Optional[str] = None,
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

@app.delete('/inventory/stock/delete', tags=['stock'])
async def stock_delete_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_id: str
):
    stock = get_stock(stock_id)
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    session.delete(stock)
    session.commit()

    return {"msg": f"Stock with ID {stock_id} deleted successfully"}

def get_stock_batch(stock_batch_id: str):
    return session.query(InventoryStockBatchModel).filter(InventoryStockBatchModel.stock_batch_id == stock_batch_id).one_or_none()

def create_stock_batch(stock_batch: StockBatchCreate):
    session.rollback()
    db_stock_batch = InventoryStockBatchModel(
        stock_batch_id=str(uuid4()),
        acquisition_date=stock_batch.acquisition_date,
    )
    session.add(db_stock_batch)
    session.commit()
    session.refresh(db_stock_batch)
    print(db_stock_batch)
    return db_stock_batch

@app.get('/inventory/stock_batch/get', tags=['stock'])
async def stock_batch_get_item(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_batch_id: str = None
):
    if stock_batch_id:

        stock_batch = get_stock_batch(stock_batch_id)
        if not stock_batch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

        return stock_batch

    return session.query(InventoryStockBatchModel).all()

@app.post('/inventory/stock_batch/add', tags=['stock'])
async def stock_batch_add(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    acquisition_date: date
):
    try:
        new_stock_batch = create_stock_batch(StockBatchCreate(acquisition_date=acquisition_date))
        return {"msg": "Stock batch added successfully", "stock_batch": new_stock_batch}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Failed to add stock batch: {str(e)}")

@app.patch('/inventory/stock_batch/edit', tags=['stock'])
async def stock_batch_edit(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_batch_id: str,
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

@app.delete('/inventory/stock_batch/delete', tags=['stock'])
async def stock_batch_delete(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    stock_batch_id: str
):
    stock_batch = get_stock_batch(stock_batch_id)

    if not stock_batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock batch not found")

    # delete stock
    stocks = session.query(InventoryStockModel).filter(
        stock_batch_id==stock_batch.stock_batch_id
    ).all()

    for stock in stocks:
        session.delete(stock)

    session.delete(stock_batch)
    session.commit()

    return {"msg": f"Stock batch with ID {stock_batch_id} deleted successfully"}

@app.get('/inventory/items/available', tags=['items'])
async def is_item_available(
    user: Annotated[
        User, Depends(authenticate)
    ],
    item_id: str
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
        print(to_dict(ingredient))

        in_db_ingredient = session.query(IngredientModel).filter(IngredientModel.ingredient_id == ingredient.ingredient_id).one_or_none()

        for stock in ingredient_stock:
            if stock.status in ['Ready to Use', "Open"] and today_date < stock.expiry_date:
                has_stock = True
                break

        if not has_stock:
            missing.append({
                "id": in_db_ingredient.ingredient_id,
                "name": in_db_ingredient.name
            })

    if len(missing) > 0:
        return {
            "available": False,
            "missing": missing
        }

    return {
        "available": True
    }
