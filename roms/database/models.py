from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, literal, Float
from sqlalchemy.orm import relationship
from .session import Base, session, engine

engine = create_engine('sqlite:///mock_database.db', isolation_level="READ UNCOMMITTED")

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

    item = relationship('ItemModel', back_populates='ingredients')

class OrderModel(Base):
    __tablename__ = 'order'

    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    orders = relationship('OrderItemModel', back_populates='order')

class OrderItemModel(Base):
    __tablename__ = 'order_item'

    order_item_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.order_id'))
    item_id = Column(Integer, ForeignKey('item.item_id'))
    quantity = Column(Integer, default=1)
    remark = Column(String, nullable=True)
    order_status = Column(String)

    order = relationship('OrderModel', back_populates='orders')

# Create tables
Base.metadata.create_all(engine)
