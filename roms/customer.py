# @fileName: customer.py
# @creation_date: 24/09/2024
# @author: yandreZzz

from typing import Annotated, Literal, Optional, List
from fastapi import Depends, Path
from pydantic import BaseModel, conint

from .account import authenticate, validate_role
from .api import app
from .user import User

if __name__ == '__main__':
    pass

category = Literal["All", "Beverage", "Rice", "Noodle", "Snacks"]
order_status = Literal["Preparing", "Ready to Serve", "Served"]

@app.post("/account/edit/personal_information/", tags=["account"])
def update_information(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
    first_name: str,
    last_name: str,
    birthday: str,
    email: str
):
    pass

# TODO: import from inventory
class Item(BaseModel):
    item_id: int
    price: float
    name: str
    picture_id: str
    description: str
    category: category

@app.get("/products", tags=["product"])
def get_products(
    category: category
) -> List[Item]:
    pass
#print for all

@app.post("/cart/edit/add", tags=["cart"])
def add_cart(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
    quantity,
    item_id: int,
    remark: Optional[str]
) -> int:
    pass

@app.post("/cart/edit/remove" , tags=["cart"])
def remove_cart(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
    quantity,
    item_in_cart_id: int
):
    pass

@app.post("/cart/edit/update", tags=["cart"])
def update_cart(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
    quantity,
    item_in_cart_id: int,
    remark: Optional[str] = None,
):
    pass

@app.get("order/track", tags=["order"])
def order_status(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
)-> order_status:
    pass

@app.post("review/add", tags=["review"])
def review(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
    ratings: Annotated[int, Path(title="Rating between 1-5", ge=1, le=5)],
    feedback: str = None
):
    pass
