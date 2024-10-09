from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, literal, Float
from sqlalchemy.orm import relationship
from .session import Base, session, engine

engine = create_engine('sqlite:///mock_database.db')

# SQLAlchemy models
class UserModel(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    birthday = Column(String)
    permission_level = Column(Integer)
    hashed_password = Column(String)

    session_tokens = relationship('SessionTokenModel', back_populates='user')

class SessionTokenModel(Base):
    __tablename__ = 'UserSessionTokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    token = Column(String, unique=True)

    user = relationship('UserModel', back_populates='session_tokens')

class IngredientModel(Base):
    __tablename__ = 'ingredient'

    ingredient_id = Column(Integer, primary_key=True)
    name = Column(String)
    stock_quantity = Column(Float)
    unit = Column(String)

class ItemModel(Base):
    __tablename__ = 'item'

    item_id = Column(Integer, primary_key=True)
    price = Column(Float)
    name = Column(String)
    picture_link = Column(String)
    description = Column(String)
    category = Column(String) #literal(['All', 'Beverage', 'Rice', 'Noodle', 'Snacks'])

    ingredients = relationship('ItemIngredientModel',back_populates="item")

class ItemIngredientModel(Base):
    __tablename__ = 'item_ingredient'

    item_ingredient_id = Column(Integer, primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredient.ingredient_id'))
    item_id = Column(Integer, ForeignKey('item.item_id'))
    quantity = Column(Float)

    item = relationship('ItemModel', back_populates="ingredients")

# Create tables
Base.metadata.create_all(engine)
