# @fileName: table.py
# @creation_date: 04/11/2024
# @authors: averyark

from datetime import datetime
from typing import Annotated, Literal, List
from fastapi import Depends
from fastapi import HTTPException, status
from uuid import UUID, uuid4

from ..database import session, to_dict
from ..database.models import TableModel, TableSessionModel
from ..database.schemas import TableCreate
from ..account import validate_role
from ..api import app
from ..user import User

def verify_table_session(table_session_id: str = None):
    if not table_session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid table session")

    table_session = session.query(TableSessionModel).filter(
        TableSessionModel.session_id == table_session_id
    ).one_or_none()

    # Check if the table session is in db and Active
    if not table_session or table_session.status != 'Active':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid table session")

    return True

@app.post('/table/add', tags=['table'])
async def table_add(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    table_id: str,
    table_status: Literal['Available', 'Occupied', 'Unavailable'],
    seats: int
):

    in_db_table = session.query(TableModel).filter(
        TableModel.table_id == table_id
    ).one_or_none()

    if in_db_table:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This table id already exist')

    table = TableModel(
        table_id=table_id,
        status=table_status,
        seats=seats
    )

    session.add(table)
    session.commit()
    session.refresh(table)

    return {'msg': f'Table was added successfuly', 'table': table}

@app.post('/table/bulk_add', tags=['table'])
async def table_bulk_add(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    tables: List[TableCreate]
):
    new_tables = []

    try:
        for table in tables:
            in_db_table = session.query(TableModel).filter(
                TableModel.table_id == table.table_id
            ).one_or_none()

            if in_db_table:
                continue

            table = TableModel(
                table_id=table.table_id,
                seats=table.seats,
                status=table.status
            )

            session.add(table)

            if table:
                new_tables.append(to_dict(table))

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e
        )
    else:
        session.commit()

    return {'msg': f'Table was added successfuly', 'tables': new_tables}

@app.delete('/table/delete', tags=['table'])
async def table_delete(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    id: str
):
    in_db_table = session.query(TableModel).filter(
        TableModel.table_id == id
    ).one_or_none()

    if not in_db_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    session.delete(in_db_table)
    session.commit()

    return {"msg": f"Table with ID {id} deleted successfully"}

# Note: you cannot manually change table_status to Occupied as it is automatically managed by table session
@app.patch('/table/edit', tags=['table'])
async def table_edit(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    table_id: str,
    table_status: Literal['Available', 'Unavailable', 'Occupied'] = None,
    seats: int = None
):
    in_db_table = session.query(TableModel).filter(
        TableModel.table_id == table_id
    ).one_or_none()

    if not in_db_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if not table_status is None:
        if not session.query(TableSessionModel).filter(
            TableSessionModel.table_id == table_id,
            TableSessionModel.status == 'Active'
        ).one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This table has active sessions. Check-out before changing status.')
        in_db_table.status = table_status

    if not seats is None:
        in_db_table.seats = seats

    session.commit()
    session.refresh(in_db_table)

    return {"msg": f"Table updated successfully", "table": to_dict(in_db_table)}

@app.get('/table/is_available', tags=['table'])
async def is_table_available(
        user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    table_id: str,
):
    in_db_table = session.query(TableModel).filter(
        TableModel.table_id == table_id
    ).one_or_none()

    if not in_db_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    return {"msg": f"Fetched successfully", "is_available": in_db_table.status == "Available", "table_status": in_db_table.status}

@app.post('/table/session/add', tags=['table'])
async def table_session_add(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef', 'Cashier']))
    ],
    table_id: str,
    head_count: int = None
):
    # Lookup Table
    table = session.query(TableModel).filter(
        TableModel.table_id == table_id
    ).one_or_none()

    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    # Check if the table is available
    if table.status != "Available":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Table is not available")

    # uuid4 is generated based on timestamp and host mac address
    new_session_id = uuid4()
    now_datetime = datetime.now()

    table_session = TableSessionModel(
        table_id=table_id,
        session_id=str(new_session_id),

        start_datetime=now_datetime,
        head_count=head_count,
        status='Active'
    )

    table.status = "Occupied"

    session.add(table_session)
    session.commit()
    session.refresh(table_session)
    session.refresh(table)

    return {
        "msg": "Table session created successfully",
        "table_session": to_dict(table_session),
        "table": to_dict(table)
    }

@app.patch('/table/session/edit', tags=['table'])
async def table_session_edit(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef', 'Cashier']))
    ],
    table_session_id: str,
    table_id: str = None,
    start_datetime: datetime = None,
    session_status: Literal['Active', 'Completed'] = None,
    head_count: int = None
):
    table_session = session.query(TableSessionModel).filter(
        TableSessionModel.session_id == table_session_id
    ).one_or_none()

    if table_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table session not found")

    in_db_table = session.query(TableModel).filter(
        TableModel.table_id == table_session.table_id
    ).one_or_none()

    if in_db_table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if table_id:
        table_session.table_id = table_id

    if start_datetime:
        table_session.start_datetime = start_datetime

    if session_status:
        if in_db_table and session_status != "Active":
            if in_db_table.status != "Unavailable":
                in_db_table.status = "Available"

        table_session.status = session_status

    if head_count:
        table_session.head_count = head_count

    session.commit()
    session.refresh(table_session)
    session.refresh(in_db_table)

    #75f1ce0b-6ad0-4755-9ca9-8205aa77801d

    return {"msg": f"Table session updated", "table_session": table_session}

@app.delete('/table/session/delete', tags=['table'])
async def table_session_delete(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', 'Chef', 'Cashier']))
    ],
    session_id: UUID
):
    table_session = session.query(TableSessionModel).filter(
        TableSessionModel.session_id == session_id
    ).one_or_none()

    if not table_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table session not found")

    session.delete(table_session)
    session.commit()

    return {"msg": f"Table session with ID {session_id} deleted successfully"}
