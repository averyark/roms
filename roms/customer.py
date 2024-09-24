# @fileName: customer.py
# @creation_date: 24/09/2024
# @author: yandreZzz

from typing import Annotated, Literal, Optional
from fastapi import Depends
from pydantic import BaseModel

from .login import authenticate, validate_role
from .api import app
from .user import User

if __name__ == '__main__':
    pass

category = Literal["All", "Beverage", "Rice", "Noodle", "Snacks"]
order_status = Literal["Preparing", "Ready to Serve", "Served"]

@app.post("/account/edit/personal_information/")
def update_information(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
    first_name: str,
    last_name: str,
    birthday: str,
    email:str
):
    pass

class ProductQueryResults(BaseModel):
    item_id: int
    price: float
    name: str
    picture_id: str
    description: str
    category: category

@app.get("/products")
def get_products(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
    category: category
) -> ProductQueryResults:
    pass
#print for all

@app.post("/cart/edit/add")
def add_cart(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
    quantity,
    item_id: int,
    remark: Optional[str]
) -> int:
    pass

@app.post("/cart/edit/remove")
def remove_cart(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
    quantity,
    item_in_cart_id: int
):
    pass
    
@app.post("/cart/edit/update")
def update_cart(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
    quantity,
    remark: Optional[str],
    item_in_cart_id: int
):
    pass

@app.get("order/track")
def order_status(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ],
)-> order_status:
    pass

@app.post("review/add")
def review(
    user: Annotated[
        User, Depends(validate_role(roles=["Customer","Manager","Chef","Cashier"]))
    ], 
    ratings: int,
    feedback: Optional[str]
):
    pass