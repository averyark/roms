# @fileName: manager.py
# @creation_date: 22/09/2024
# @authors: averyark

from typing import Annotated
from fastapi import Depends
from pydantic import BaseModel

from .credentials import pwd_context
from .login import authenticate, validate_role
from .api import app
from .user import User

# APIS

'''
    What is annotated and depends
    -----------------------------------
    Annotated[] enables explicit type annotating
    Depends() injects the returned values into the argument
    t: Annotated[a, Depends(b)] means the argument "t" is type of "a" and it is injected by the method b
    It is useful for making explicit arguments.
    -----------------------------------

    NOTE:
    -----------------------------------
    The first argument should always be the "user" if the api requires authentication for role validation.
    Use validate_role(roles=[ROLES]) to validate user role.

    Following arguments should be specified with the type of the argument like int, str, float, and dictionary should be represented using Pydantic BaseModel class!
    -----------------------------------
'''

# NOTE: authenticate is generally the same as validate_role, but without the option to specify expected roles
@app.post("/account/edit/credentials/", tags=["account"])
def edit_credentials(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
    user_id: int,
    new_credentials: str
):
    user.hashed_password = pwd_context.hash(new_credentials)
    user.commit()

    pass
