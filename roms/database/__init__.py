from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

from .schemas import UserBase, UserData, UserCreate, IngredientItem, IngredientItemCreate, Ingredient, IngredientCreate, Item, ItemCreate
from .models import UserModel, SessionTokenModel, ItemModel, IngredientModel, ItemIngredientModel
from .session import session
from ..credentials import pwd_context, SECRET_KEY, USE_ALGORITHM, JWT_EXPIRATION_MINUTES

from datetime import datetime, timezone, timedelta
from jwt import encode as jwt_encode, decode as jwt_decode, ExpiredSignatureError

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine('sqlite:///mock_database.db')
Session = sessionmaker(bind=engine)
session = Session()

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
        item_id=item_ingredient.ingredient_id,
        quantity=item_ingredient.stock_quantity
    )
    session.add(db_item_ingredient)
    session.commit()
    session.refresh(db_item_ingredient)
    return db_item_ingredient

def create_item(item: ItemCreate):
    db_item = ItemModel(
        price=item.price,
        name=item.name,
        picture_link=item.picture_link,
        description=item.description,
        category=item.category,
    )

    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def create_ingredient(ingredient: IngredientCreate):
    db_ingredient = ItemModel(
        name=ingredient.name,
        stock_quantity=ingredient.stock_quantity,
        unit=ingredient.unit
    )
    session.add(db_ingredient)
    session.commit()
    session.refresh(db_ingredient)
    return db_ingredient

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

# Create tables
Base.metadata.create_all(engine)
