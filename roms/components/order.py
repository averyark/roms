# @fileName: order.py
# @creation_date: 15/10/2024
# @authors: averyark

# Manager: Order Management: Oversee order details, including viewing and updating order status.
# Customer: Order Tracking: Monitor the status of placed orders.

from typing import Annotated, Literal, Optional, List

from fastapi import Depends, HTTPException, status
from uuid import uuid4
from datetime import datetime

from .table import verify_table_session
from ..database import session, to_dict
from ..database.models import OrderModel, OrderItemModel, ItemModel
from ..database.schemas import OrderCreate, OrderItemCreate
from ..account import authenticate_optional, validate_role
from ..api import app
from ..user import User

def create_order_item(order: OrderItemCreate, order_id):

    in_db_item = session.query(ItemModel).filter(
        ItemModel.item_id==order.item_id
    ).one_or_none()

    if in_db_item is None:
        # SHOULD ERROR
        return

    db_order_item = OrderItemModel(
        order_item_id = str(uuid4()),
        order_id=order_id,
        item_id=order.item_id,
        remark=order.remark,
        quantity=order.quantity,
        order_status="Ordered",
        price=in_db_item.price
    )

    session.add(db_order_item)
    session.commit()
    session.refresh(db_order_item)
    return db_order_item

def create_order(order: OrderCreate):
    order_id = uuid4()

    db_order = OrderModel(
        user_id=order.user_id,
        session_id=order.table_session_id,
        order_datetime=datetime.now(),
        order_id=str(order_id)
    )

    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    order_items = []

    for order_item in order.orders:
        new_order_item = create_order_item(order_item, db_order.order_id)

        if not new_order_item is None:
            order_items.append(to_dict(new_order_item))

    return db_order, order_items

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
        User, Depends(validate_role(roles=['Guest','Manager', 'Chef', 'Cashier', 'Customer']))
    ],
    user_id: int = None
):
    '''
    Retrieve all orders belonging to the user that is currently authenticated if user_id is not specified. Otherwise, the orders for the user of {user_id} is returned
    '''

    if user_id and user.get_role() in ["Manager", "Chef", "Cashier"]:
        return to_dict(session.query(OrderModel).filter(
        OrderModel.user_id == user_id))
    else:
        return to_dict(session.query(OrderModel).filter(
        OrderModel.user_id == user.user_id))

@app.post('/order/add/', tags=['order'])
async def order_add(
    user: Annotated[
        Optional[User], Depends(authenticate_optional)
    ],
    table_session_id: str,
    orders: List[OrderItemCreate],
    user_id: int = None
):
    '''
    Add order to belonging user that is currently authenticated if user_id is not speicified. Otherwise, the order is added for the user of user_id.

    Authenticating is optional if user_id is not provided.
'''

    verify_table_session(table_session_id)

    if user_id:
        if not user.get_role() in ["Manager"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Insufficient permission")

        new_order, order_items = create_order(OrderCreate(
            user_id=user_id,
            table_session_id=table_session_id,
            orders=orders
        ))
    else:
        if user:
            new_order, order_items = create_order(OrderCreate(
                user_id=user.user_id,
                table_session_id=table_session_id,
                orders=orders
            ))
        else:
            new_order, order_items = create_order(OrderCreate(
                table_session_id=table_session_id,
                orders=orders
            ))

    if new_order:
        new_order = to_dict(new_order)

    return {"msg": "Order created successfully", "order": new_order, "order_items": order_items or []}

@app.delete('/order/item/delete', tags=['order'])
async def order_item_delete(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    order_item_id: str
):
    '''
    Remove order item
    '''

    session.query(OrderItemModel).filter(
        OrderItemModel.order_item_id == order_item_id
    ).delete()
    session.commit()

    return {"message": "Order item deleted successfully"}

@app.delete('/order/delete', tags=['order'])
async def order_item_delete(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    order_id: str
):
    '''
    Remove order
    '''

    in_db_order_item = session.query(OrderModel).filter(
        OrderItemModel.order_id == order_id
    )

    if in_db_order_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order item not found')

    session.delete(in_db_order_item)
    session.commit()

    return {"message": "Order deleted successfully"}

@app.patch('/order/item/edit', tags=['order'])
async def order_item_edit(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef', 'Cashier']))
    ],
    order_item_id: str,
    item_id: Optional[int] = None,
    quantity: Optional[int] = None,
    remark: Optional[str] = None
):
    '''
    Update order item details
    '''

    in_db_order_item = session.query(OrderItemModel).filter(
        OrderItemModel.order_item_id == order_item_id
    ).one_or_none()

    if not in_db_order_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This order item does not exist")

    if item_id:
        in_db_order_item.item_id = item_id
    if quantity:
        in_db_order_item.quantity = quantity
    if remark:
        in_db_order_item.remark = remark

    session.commit()
    session.refresh(in_db_order_item)

    return {"message": "Order item edited successfully"}

@app.patch('/order/item/edit_status', tags=['order'])
async def order_item_edit_status(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', "Chef", "Cashier"]))
    ],
    order_item_id: str,
    new_status: Literal["Ordered", "Preparing", "Serving", "Served"]
):
    '''
    Edit item status
    '''

    in_db_order_item = session.query(OrderItemModel).filter(
        OrderItemModel.order_item_id == order_item_id
    ).one_or_none()

    if not in_db_order_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This order item does not exist")

    in_db_order_item.order_status = new_status
    session.commit()

    return {"message": "Order item status updated successfully"}

def get_session_orders(session_id: str):
    orders = session.query(OrderModel).filter(
        OrderModel.session_id == session_id
    ).all()

    order_items = []
    orders_dict = []

    for order in orders:
        for order_item in order.orders:
            order_items.append(
                to_dict(order_item)
            )
        orders_dict.append(
            to_dict(order)
        )

    return orders_dict, order_items

@app.get('/order/session_orders', tags=['order'])
async def get_session_orders_async(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', "Chef", "Cashier"]))
    ],
    table_session_id = str
):

    orders, order_items = get_session_orders(table_session_id)

    return {
        'msg': 'Order fetched successfully',
        'order_items': order_items or [],
        'orders': orders
    }
