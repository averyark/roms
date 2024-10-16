# @fileName: order.py
# @creation_date: 15/10/2024
# @authors: averyark

# Manager: Order Management: Oversee order details, including viewing and updating order status.
# Customer: Order Tracking: Monitor the status of placed orders.

from typing import Annotated, Literal, Optional, List

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import paginate as api_pagiante
from fastapi_pagination import Page, set_page
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ..database import session
from ..database.models import OrderModel, OrderItemModel
from ..database.schemas import OrderCreate, OrderItemCreate, Order, OrderItem, OrderCreateNoUserIdKnowledge
from ..account import authenticate, validate_role
from ..api import app
from ..user import User

def create_order_item(order: OrderItemCreate, order_id):
    db_order_item = OrderItemModel(
        order_id=order_id,
        item_id=order.item_id,
        remark=order.remark,
        quantity=order.quantity,
        order_status="Ordered"
    )

    session.add(db_order_item)
    session.commit()
    session.refresh(db_order_item)
    return db_order_item

def create_order(order: OrderCreate):
    db_order = OrderModel(
        user_id=order.user_id
    )

    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    for order_item in order.orders:
        create_order_item(order_item, db_order.order_id)

    return db_order

def get_order(order_id: int):
    return session.query(OrderModel).filter(
        OrderModel.order_id == order_id
    ).one()

def delete_all_orders():
    session.query(OrderModel).delete()
    session.query(OrderItemModel).delete()
    session.commit()

@app.post('/order/get/', tags=['order'])
async def order_get(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef', 'Cashier', 'Customer']))
    ],
    user_id: int = None
):
    '''
    Retrieve all orders belonging to the user that is currently authenticated if user_id is not specified. Otherwise, the orders for the user of {user_id} is returned
    '''

    if user_id and user.get_role() in ["Manager"]:
        return session.query(OrderModel).filter(
        OrderModel.user_id == user_id)
    else:
        return session.query(OrderModel).filter(
        OrderModel.user_id == user.user_id)

@app.post('/order/add/', tags=['order'])
async def order_add(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef', 'Cashier', 'Customer']))
    ],
    order_create: OrderCreateNoUserIdKnowledge,
    user_id: int = None
):
    '''
    Add order to belonging user that is currently authenticated if user_id is not speicified. Otherwise, the order is added for the user of {user_id}.
    '''

    if user_id:
        if not user.get_role() in ["Manager"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Insufficient permission")

        create_order(OrderCreate(
            user_id=user_id,
            **order_create.model_dump()
        ))
    else:
        create_order(OrderCreate(
            user_id=user.user_id,
            **order_create.model_dump()
        ))

    return {"message": "Order created successfully"}
