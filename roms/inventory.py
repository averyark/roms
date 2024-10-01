# @fileName: inventory.py
# @creation_date: 01/10/2024
# @authors: averyark

from typing import Annotated, Literal, Optional
from fastapi import Depends
from pydantic import BaseModel

from .account import authenticate, validate_role
from .api import app
from .user import User

category = Literal["All", "Beverage", "Rice", "Noodle", "Snacks"]

class InventoryItem(BaseModel):
    item_id: int
    price: float
    name: str
    picture_id: str
    description: str
    category: category

class InventoryItemUpdate(BaseModel):
    item_id: Optional[int] = None
    price: Optional[float] = None
    name: Optional[str] = None
    picture_id: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

@app.post("/inventory/add", tags=["inventory"])
def inventory_add(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
):
    pass

@app.patch("/inventory/update", tags=["inventory"])
def inventory_update(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
    item_id: int,
    update_fields: InventoryItemUpdate
):
    pass

@app.delete("/inventory/delete", tags=["inventory"])
def inventory_delete(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
):
    pass
