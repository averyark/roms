from sqlalchemy.orm import class_mapper

from .models import *
from .schemas import *
from .session import session

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
