# @fileName: inventory.py
# @creation_date: 01/10/2024
# @authors: averyark

from typing import Annotated, Literal, Optional, List
from fastapi import Depends
from pydantic import BaseModel

from .account import authenticate, validate_role
from .api import app
from .user import User

class InventoryIngredient(BaseModel):
    ingredient_id: int
    name: str
    quantity: float

class InventoryItemIngredient(BaseModel):
    ingredient_id: int
    quantity: float

class InventoryItem(BaseModel):
    item_id: int
    price: float
    name: str
    picture_link: str
    description: str
    category: Literal["All", "Beverage", "Rice", "Noodle", "Snacks"]

    # Only accessible by Chef / Manager
    ingredients: Optional[List[InventoryItemIngredient]] = None

class InventoryItemUpdate(BaseModel):
    item_id: Optional[int] = None
    price: Optional[float] = None
    name: Optional[str] = None
    picture_link: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

TEMPORARY_INGREDIENTS = [InventoryIngredient(
    name="Kopi Powder",
    ingredient_id=1,
    quantity=1252 #gram
)]

TEMPORARY_INVENTORY = [InventoryItem(
    item_id=1,
    price=6.3,
    name="Kopi Beng",
    picture_link="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgYbqhuVAja_fGSBITWC7qCKjCsa0jcN5_0w&s",
    description="yummy kopi mmmm",
    category="Beverage",
    ingredients=[
        InventoryItemIngredient(ingredient_id=1, quantity=9)
    ]
)]

@app.post("/inventory/items/get", tags=["inventory"])
def inventory_add(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager", "Chef", "Cashier", "Customer"]))
    ],
) -> List[InventoryItem]:
    if user.get_role() in ["Manager", "Chef"]:
        return TEMPORARY_INVENTORY
    else:
        copy = TEMPORARY_INVENTORY.copy()
        for dict in copy:
            try:
                del dict.ingredients
                pass
            except: pass # swallow error

        return copy

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
