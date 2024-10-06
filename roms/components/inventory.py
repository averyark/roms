# @fileName: inventory.py
# @creation_date: 01/10/2024
# @authors: averyark

from typing import Annotated, Literal, Optional, List
from fastapi import Depends
from pydantic import BaseModel

from ..account import authenticate, validate_role
from ..api import app
from ..user import User

class InventoryIngredient(BaseModel):
    ingredient_id: int
    name: str
    quantity: float
    unit: str

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
    quantity=1252,
    unit="g",
), InventoryIngredient(
    name="Hot Water",
    ingredient_id=2,
    quantity=float("inf"),
    unit="ml"
)]

TEMPORARY_INVENTORY = [InventoryItem(
    item_id=1,
    price=6.3,
    name="Kopi Beng",
    picture_link="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgYbqhuVAja_fGSBITWC7qCKjCsa0jcN5_0w&s",
    description="yummy kopi mmmm",
    category="Beverage",
    ingredients=[
        # Kopi Powder
        InventoryItemIngredient(ingredient_id=1, quantity=10),
        # Water
        InventoryItemIngredient(ingredient_id=2, quantity=200)
    ]
), InventoryItem(
    item_id=2,
    price=12,
    name="Super Fried Rice",
    picture_link="https://www.gimmesomeoven.com/wp-content/uploads/2017/07/How-To-Make-Fried-Rice-Recipe-2-1.jpg",
    description="better than uncle roger fried rice",
    category="Rice",
    ingredients=[

    ]
)]

@app.post("/inventory/items/get", tags=["inventory"])
def inventory_get(
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

@app.post("/inventory/items/add", tags=["inventory"])
def inventory_add_item(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
    fields: InventoryItemIngredient
):
    pass

@app.patch("/inventory/items/update", tags=["inventory"])
def inventory_update_item(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
    item_id: int,
    update_fields: InventoryItemUpdate
):
    pass

@app.delete("/inventory/items/delete", tags=["inventory"])
def inventory_delete_item(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
    ingredient_id: int
):
    pass

@app.post("/inventory/ingredients/add", tags=["inventory"])
def inventory_add_item(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
    fields: InventoryIngredient
):
    pass

@app.patch("/inventory/ingredients/update", tags=["inventory"])
def inventory_update_item(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
    ingredient_id: int,
    update_fields: InventoryItemUpdate
):
    pass

@app.delete("/inventory/ingredients/delete", tags=["inventory"])
def inventory_delete_item(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
    ingredient_id: int
):
    pass
