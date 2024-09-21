from typing import Annotated
from fastapi import Depends

from .login import authenticate, validate_role
from .api import app
from .user import User

# APIS
@app.post("/account/edit/credentials/")
def edit_credentials(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
        ],
    user_id: int,
    new_credentials: str
):
    pass

if __name__ == '__main__':
    pass
