from typing import Annotated, Literal, Optional
from datetime import date

from fastapi import HTTPException, status, Depends

from ..database import session
from ..database.schemas import EquipmentRemark, EquipmentRemarkCreate
from ..database.models import EquipmentRemarkModel
from ..api import app
from ..account import validate_role
from ..user import User

@app.get('/equipment/remark/get', tags=['equipment'])
async def get_remark(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef'])),
    ],
    remark_id: int = None,
    equipment_name: str = None,
    submit_date: date = None,
    remark: str = None,
    remark_status: Literal['Submitted', 'Completed'] = None
):
    query = session.query(EquipmentRemarkModel)

    if remark_id:
        query = query.filter(
            EquipmentRemarkModel.remark_id == remark_id,
        )
    if equipment_name:
        query = query.filter(
            EquipmentRemarkModel.equipment_name == equipment_name,
        )
    if submit_date:
        query = query.filter(
            EquipmentRemarkModel.submit_date == submit_date,
        )
    if remark:
        query = query.filter(
            EquipmentRemarkModel.remark == remark
        )
    if remark_status:
        query = query.filter(
            EquipmentRemarkModel.status == remark_status
        )

    return query.all()

@app.post('/equipment/remark/add', tags=['equipment'])
async def add_remark(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef'])),
    ],
    equipment_name: str,
    submit_date: date,
    remark: str,
    status: Literal['Submitted', 'Completed']
):
    in_db_remark = EquipmentRemarkModel(
        equipment_name=equipment_name,
        submit_date=submit_date,
        remark=remark,
        status=status
    )

    session.add(in_db_remark)
    session.commit()
    session.refresh(in_db_remark)

    return {
        'msg': 'Remark added successfully', 'remark': in_db_remark
    }

@app.patch('/equipment/remark/edit', tags=['equipment'])
async def edit_remark(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef'])),
    ],
    remark_id: int,
    equipment_name: str = None,
    submit_date: date = None,
    remark: str = None,
    remark_status: Literal['Submitted', 'Completed'] = None
):
    in_db_remark = session.query(EquipmentRemarkModel).filter(EquipmentRemarkModel.remark_id == remark_id).one_or_none()

    if not in_db_remark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Remark not found')

    if equipment_name:
        in_db_remark.equipment_name = equipment_name
    if submit_date:
        in_db_remark.submit_date = submit_date
    if remark:
        in_db_remark.remark = remark
    if remark_status:
        in_db_remark.status = remark_status

    session.commit()
    session.refresh(in_db_remark)

    return {
        'msg': 'Remark edited successfully', 'remark': in_db_remark
    }

@app.delete('/equipment/remark/delete', tags=['equipment'])
async def delete_remark(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef']))
    ],
    remark_id: int
):
    item = session.query(EquipmentRemarkModel).filter(EquipmentRemarkModel.remark_id == remark_id).one()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Remark not found")

    session.delete(item)
    session.commit()

    return {"msg": f"Remark with ID {remark_id} deleted successfully"}
