from fastapi import FastAPI
from fastapi_pagination import add_pagination

app = FastAPI()

add_pagination(app)
