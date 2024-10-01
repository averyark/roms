# @fileName: analytics.py
# @creation_date: 01/10/2024
# @authors: averyark

from typing import Annotated
from fastapi import Depends
from pydantic import BaseModel

from .credentials import pwd_context
from .account import authenticate, validate_role
from .api import app
from .user import User

# Analytic API

@app.get("/analytics/view/", tags=["analytics"])
def view_analytics(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
):
    pass
