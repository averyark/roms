from sqlalchemy import create_engine, and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship, sessionmaker, declarative_base, class_mapper

from .models import *
from .schemas import UserBase, UserData, UserCreate, IngredientItem, IngredientItemCreate, Ingredient, IngredientCreate, Item, ItemCreate
from .models import UserModel, SessionTokenModel, ItemModel, IngredientModel, ItemIngredientModel
from .session import session
from ..credentials import pwd_context, SECRET_KEY, USE_ALGORITHM, JWT_EXPIRATION_MINUTES

from datetime import datetime, timezone, timedelta
from jwt import encode as jwt_encode, decode as jwt_decode, ExpiredSignatureError

def create_user(user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = UserModel(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birthday=user.birthday,
        hashed_password=hashed_password,
        permission_level=user.permission_level
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def create_item_ingredient(item_ingredient: IngredientItemCreate):
    db_item_ingredient = ItemIngredientModel(
        item_id=item_ingredient.item_id,
        ingredient_id=item_ingredient.ingredient_id,
        quantity=item_ingredient.quantity
    )
    session.add(db_item_ingredient)
    session.commit()
    session.refresh(db_item_ingredient)
    return db_item_ingredient

def create_item(item: ItemCreate):
    in_db_item = session.query(ItemModel).filter(ItemModel.name == item.name).one_or_none()

    # check if the item ingredients is in the itemingredient db table
    if in_db_item is None:
        # create the item because it doesn't exist
        in_db_item = ItemModel(
            price=item.price,
            name=item.name,
            picture_link=item.picture_link,
            description=item.description,
            category=item.category,
        )
        session.add(in_db_item)
        session.commit()
        session.refresh(in_db_item)

    for ingredient_item in item.ingredients:
        in_db_ingredient_item = session.query(ItemIngredientModel).filter(
            and_(
                ItemIngredientModel.item_id == in_db_item.item_id,
                ItemIngredientModel.ingredient_id == ingredient_item.ingredient_id
            )
        ).one_or_none()

        # continue if the ingredient already exist
        if in_db_ingredient_item:
            continue

        db_ingredient_item = ItemIngredientModel(
            ingredient_id=ingredient_item.ingredient_id,
            item_id = in_db_item.item_id,
            quantity=ingredient_item.quantity
        )

        session.add(db_ingredient_item)
        session.commit()
        session.refresh(db_ingredient_item)

    return in_db_item

def create_ingredient(ingredient: IngredientCreate):
    db_ingredient = IngredientModel(
        name=ingredient.name,
        stock_quantity=ingredient.stock_quantity,
        unit=ingredient.unit
    )
    session.add(db_ingredient)
    session.commit()
    session.refresh(db_ingredient)
    return db_ingredient

def get_item(item_id: int):
    return session.query(ItemModel).filter(ItemModel.item_id == item_id).one()

def get_ingredient(ingredient_id: int):
    return session.query(IngredientModel).filter(IngredientModel.ingredient_id == ingredient_id).one()

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

def create_session_token(user_id: int) -> str:
    # Generate JWT token
    expiration = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    token = jwt_encode({
        'sub': user_id,
        'exp': expiration
    }, SECRET_KEY, algorithm=USE_ALGORITHM)

    # Store the token in the database
    session_token = SessionTokenModel(user_id=user_id, token=token)
    session.add(session_token)
    session.commit()

    return token

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
