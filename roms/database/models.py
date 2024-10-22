from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, literal, Float, DATE, Enum, TIME, DATETIME
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

class ItemModel(Base):
    __tablename__ = 'item'

    item_id = Column(Integer, primary_key=True)
    price = Column(Float)
    name = Column(String)
    picture_link = Column(String)
    description = Column(String)
    category = Column(Enum('All', 'Beverage', 'Rice', 'Noodle', 'Snacks'))

    ingredients = relationship('ItemIngredientModel',back_populates="item")

class ItemIngredientModel(Base):
    __tablename__ = 'item_ingredient'

    item_ingredient_id = Column(Integer, primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredient.ingredient_id'))
    item_id = Column(Integer, ForeignKey('item.item_id'))

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
    order_status = Column(Enum('Shopping Cart', 'Ordered', 'Preparing', 'Serving', 'Served'))
    price = Column(String)

    order = relationship('OrderModel', back_populates='orders')

class InventoryStockModel(Base):
    __tablename__ = 'inventory_stock'

    stock_id = Column(Integer, primary_key=True)
    stock_batch_id = Column(Integer, ForeignKey('inventory_stock_batch.stock_batch_id'))
    expiry_date = Column(DATE)
    ingredient_id = Column(Integer, ForeignKey('ingredient.ingredient_id'))

    status = Column(Enum('Ready to Use', 'Open', 'Used'))

    stock_batch = relationship('InventoryStockBatchModel', back_populates='stocks')

class InventoryStockBatchModel(Base):
    __tablename__ = 'inventory_stock_batch'

    stock_batch_id = Column(Integer, primary_key=True)
    acquisition_date = Column(DATE)

    stocks = relationship('InventoryStockModel', back_populates='stock_batch')

class VoucherModel(Base):
    __tablename__ = 'voucher'

    voucher_id = Column(Integer, primary_key=True)
    voucher_code = Column(String, nullable=False)
    expiry_date = Column(DATE, nullable=True)
    begin_date = Column(DATE, nullable=True)

    # A voucher can have multiple requirements
    requirements = relationship('VoucherRequirementModel', back_populates='voucher')

class VoucherRequirementModel(Base):
    __tablename__ = 'voucher_requirement'

    voucher_requirement_id = Column(Integer, primary_key=True)
    voucher_id = Column(Integer, ForeignKey('voucher.voucher_id'))
    voucher = relationship('VoucherModel', back_populates='requirements')

    # Require certain item in the receipt
    requirement_item_id = Column(Integer, nullable=True)

    # Voucher can only be used in certain time of the day
    requirement_time = Column(TIME, nullable=True)

    # Voucher can only be used with a minimum spend
    requirement_minimum_spend = Column(Float, nullable=True)

class UserVoucherModel(Base):
    __tablename__ = 'user_voucher'

    user_id = Column(Integer, primary_key=True)
    voucher_id = Column(Integer, ForeignKey("voucher.voucher_id"), primary_key=True)
    use_date = Column(DATE)

class EquipmentRemarkModel(Base):
    __tablename__ = 'equipment_remarks'

    remark_id = Column(Integer, primary_key=True)
    equipment_name = Column(String)
    remark = Column(String)
    submit_date = Column(DATE)
    status = Column(Enum('Submitted', 'Completed'))

class ReviewModel(Base):
    __tablename__ = 'review'

    review_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    item_id = Column(Integer, ForeignKey("item.item_id"))
    remark = Column(String, nullable=True)
    value = Column(Integer)
    review_datetime = Column(DATETIME)

# Create tables
Base.metadata.create_all(engine)
