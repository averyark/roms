from sqlalchemy.orm import class_mapper
from sqlalchemy.exc import NoResultFound

from .models import *
from .schemas import *
from .session import session
from ..credentials import pwd_context, SECRET_KEY, USE_ALGORITHM, JWT_EXPIRATION_MINUTES

from datetime import datetime, timezone, timedelta
from jwt import encode as jwt_encode, decode as jwt_decode, ExpiredSignatureError

def get_user_data_in_dict(user_id: int) -> dict:
    try:
        user = session.query(UserModel).filter(UserModel.user_id == user_id).one()
        return {
            'user_id': user_id,
            'session_tokens': [token.token for token in user.session_tokens],
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'birthday': user.birthday,
            'permission_level': user.permission_level,
            'hashed_password': user.hashed_password
        }
    except NoResultFound:
        return None

def to_dict(obj):
    """
    Convert SQLAlchemy model instance into a dictionary.
    """
    if not obj:
        return None

    # Get the columns of the model
    columns = [column.key for column in class_mapper(obj.__class__).columns]

    # Create a dictionary with column names as keys and their values
    return {column: getattr(obj, column) for column in columns}
