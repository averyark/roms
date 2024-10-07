from fastapi import Depends, FastAPI, HTTPException, status
from typing import Annotated
from fastapi_pagination import add_pagination

app = FastAPI()

add_pagination(app)
