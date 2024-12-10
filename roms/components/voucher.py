# @fileName: voucher.py
# @creation_date: 08/11/2024
# @authors: averyark

from typing import Annotated, Literal, Optional, List

from datetime import datetime, time
from fastapi import Depends, HTTPException, status
from uuid import uuid4

from ..account import authenticate_optional, validate_role
from ..api import app
from ..user import User
from ..database import session, to_dict
from ..database.models import VoucherModel, VoucherRequirementModel, VoucherUsesModel

from .order import get_session_orders
from .table import verify_table_session

def get_total_after_voucher(
    total: int,
    vouchers_uses: List[VoucherUsesModel]
):
    deduct_percentage = 0
    deduct_amount = 0
    for voucher_use in vouchers_uses:
        voucher = session.query(VoucherModel).filter(
            VoucherModel.voucher_id == voucher_use.voucher_id
        ).one()

        if voucher.discount_type == 'Percentage':
            deduct_percentage += voucher.discount_amount
        elif voucher.discount_type == 'Fixed':
            deduct_amount += voucher.discount_amount

    reduction = total * deduct_percentage/100 - deduct_amount

    return total - reduction, reduction

@app.patch('/voucher/use', tags=['voucher'])
async def apply_voucher(
    user: Annotated[
        User, Depends(authenticate_optional)
    ],
    table_session_id: str,
    voucher_code: str
):
    verify_table_session(table_session_id)

    voucher = session.query(VoucherModel).filter(
        VoucherModel.voucher_code == voucher_code
    ).one_or_none()

    if voucher is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid voucher code')

    now_datetime = datetime.now()

    orders, order_items = get_session_orders(table_session_id)

    if voucher.begin_datetime and now_datetime < voucher.begin_datetime:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Voucher not started yet')

    if voucher.expiry_datetime and now_datetime > voucher.expiry_datetime:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Voucher expired')

    if voucher.requirement_time:
        current_time = now_datetime.time()
        if current_time < voucher.requirement_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Voucher cannot be used at this time')

    if voucher.requirement_minimum_spend:
        # Assuming you have a way to get the current spend, replace `current_spend` with actual value
        current_spend = 0

        for order_item in order_items:
            current_spend += order_item['price']

        if current_spend < voucher.requirement_minimum_spend:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Minimum spend not met')

    if (voucher.requirement_member or voucher.max_uses != 0) and user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Voucher requires user to be logged in')

    if voucher.max_uses:
        user_voucher_uses = session.query(VoucherUsesModel).filter(
            VoucherUsesModel.voucher_id == voucher.voucher_id,
            VoucherUsesModel.user_id == user.user_id,
        ).all()

        if len(user_voucher_uses) >= voucher.max_uses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Too much uses')

    # Check the voucher already applied to the session
    session_voucher_uses = session.query(VoucherUsesModel).filter(
        VoucherUsesModel.voucher_id == voucher.voucher_id,
        VoucherUsesModel.table_session_id == table_session_id
    ).one_or_none()

    if not session_voucher_uses is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This voucher is already applied to this session')

    voucher_requirements = session.query(VoucherRequirementModel).filter(
        VoucherModel.voucher_id == voucher.voucher_id
    ).all()

    for requirement in voucher_requirements:
        if requirement.requirement_item_id not in [item['item_id'] for item in order_items]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Required item not in order')

    # Passed all requirement checks

    db_voucher_uses = VoucherUsesModel(
        voucher_use_id=str(uuid4()),
        voucher_id=voucher.voucher_id,
        user_id=user.user_id,
        table_session_id=table_session_id,
        use_datetime=now_datetime
    )

    session.add(db_voucher_uses)
    session.commit()
    session.refresh(db_voucher_uses)

    return {
        'msg': 'Voucher applied successfully'
    }

@app.patch('/voucher/add', tags=['voucher'])
async def new_voucher(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', "Chef", "Cashier"]))
    ],
    voucher_code: str,
    discount_type: Literal['Percentage', 'Fixed'],
    discount_amount: float,
    requirement_time: Optional[time] = None,
    requirement_minimum_spend: Optional[float] = None,
    requirement_member: Optional[bool] = None,
    max_uses: Optional[int] = None,
    expiry_datetime: Optional[datetime] = None,
    begin_datetime: Optional[datetime] = None,
    required_item_ids: Optional[List[str]] = None
):

    in_db_voucher = session.query(VoucherModel).filter(
        VoucherModel.voucher_code == voucher_code
    ).one_or_none()

    if in_db_voucher:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='A voucher with this voucher code already exist')

    voucher_id = str(uuid4())
    voucher_requirements = []

    try:
        voucher = VoucherModel(
            voucher_id=voucher_id,
            voucher_code=voucher_code,
            discount_type=discount_type,
            discount_amount=discount_amount,
            requirement_time=requirement_time,
            requirement_minimum_spend=requirement_minimum_spend,
            requirement_member=requirement_member,
            max_uses=max_uses,
            expiry_datetime=expiry_datetime,
            begin_datetime=begin_datetime
        )

        if required_item_ids:
            for required_item_id in required_item_ids:
                voucher_requirement = VoucherRequirementModel(
                    voucher_requirement_id=str(uuid4()),
                    voucher_id=voucher_id,

                    requirement_item_id=required_item_id
                )
                session.add(voucher_requirement)
                voucher_requirements.append(to_dict(voucher_requirement))

        session.add(voucher)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    else:
        session.commit()


    voucher_dict = to_dict(voucher)
    voucher_dict.update({'requirements': voucher_requirements})

    return {
        'msg': 'Voucher created successfully',
        'voucher': voucher_dict,
    }


@app.delete('/voucher/delete/', tags=['voucher'])
async def delete_voucher(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', "Chef", "Cashier"]))
    ],
    voucher_code: str
):
    try:
        voucher = session.query(VoucherModel).filter(
            VoucherModel.voucher_code == voucher_code
        ).one_or_none()

        if voucher is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Voucher not found')

        session.query(VoucherRequirementModel).filter(
            VoucherRequirementModel.voucher_id == voucher.voucher_id
        ).delete()

        session.query(VoucherUsesModel).filter(
            VoucherUsesModel.voucher_id == voucher.voucher_id
        ).delete()

        session.delete(voucher)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    else:
        session.commit()

    return {
        'msg': 'Voucher deleted successfully'
    }
