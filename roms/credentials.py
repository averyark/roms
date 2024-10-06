# @fileName: credentials.py
# @creation_date: 18/09/2024
# @authors: averyark

import sqlite3
from icecream import ic

from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

# run "openssl rand -hex 32" in terminal to generate a new secret!
# NOTE: This secret is exposed and only intended for demonstrating purposes!
SECRET_KEY = "74faf15b3edd4a5d863ebc89d548cf5b19e5a84dd3817f7fb70dcefad009c208"
USE_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 259200

pwd_context = CryptContext(schemes=["bcrypt"])
