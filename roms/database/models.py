from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, literal, Float, DATE, Enum, TIME, DATETIME, Boolean
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

    ingredient_id = Column(String, primary_key=True)
    is_deleted = Column(Boolean, nullable=True)
    name = Column(String)

class ItemModel(Base):
    __tablename__ = 'item'

    item_id = Column(String, primary_key=True)
    price = Column(Float)
    name = Column(String)
    picture_link = Column(String)
    description = Column(String)
    category = Column(Enum('All', 'Beverage', 'Rice', 'Noodle', 'Snacks'))

    is_deleted = Column(Boolean, nullable=True) # ItemModel is not actually deleted but marked as deleted, otherwise it might break dependencies that rely on the ItemModel

    ingredients = relationship('ItemIngredientModel',back_populates="item")

class ItemIngredientModel(Base):
    __tablename__ = 'item_ingredient'

    item_ingredient_id = Column(String, primary_key=True)
    ingredient_id = Column(String, ForeignKey('ingredient.ingredient_id'))
    item_id = Column(String, ForeignKey('item.item_id'))

    item = relationship('ItemModel', back_populates='ingredients')

class OrderModel(Base):
    __tablename__ = 'order'

    order_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    session_id = Column(String, ForeignKey('table_session.session_id'))
    order_datetime = Column(DATETIME)

    orders = relationship('OrderItemModel', back_populates='order')

class OrderItemModel(Base):
    __tablename__ = 'order_item'

    order_item_id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey('order.order_id'))
    item_id = Column(Integer, ForeignKey('item.item_id'))

    quantity = Column(Integer, default=1)
    remark = Column(String, nullable=True)
    order_status = Column(Enum('Shopping Cart', 'Ordered', 'Preparing', 'Serving', 'Served'))
    price = Column(Float)

    order = relationship('OrderModel', back_populates='orders')

class InventoryStockModel(Base):
    __tablename__ = 'inventory_stock'

    stock_id = Column(String, primary_key=True)
    stock_batch_id = Column(String, ForeignKey('inventory_stock_batch.stock_batch_id'))
    expiry_date = Column(DATE)
    ingredient_id = Column(String, ForeignKey('ingredient.ingredient_id'))

    status = Column(Enum('Ready to Use', 'Open', 'Used'))

    stock_batch = relationship('InventoryStockBatchModel', back_populates='stocks')

class InventoryStockBatchModel(Base):
    __tablename__ = 'inventory_stock_batch'

    stock_batch_id = Column(String, primary_key=True)
    acquisition_date = Column(DATE)

    stocks = relationship('InventoryStockModel', back_populates='stock_batch')

class VoucherModel(Base):
    __tablename__ = 'voucher'

    voucher_id = Column(String, primary_key=True)
    voucher_code = Column(String, nullable=False)

    expiry_datetime = Column(DATETIME, nullable=True)

    begin_datetime = Column(DATETIME, nullable=True)

    discount_type = Column(Enum('Percentage', 'Fixed'))
    discount_amount = Column(Float)

    # A voucher can have multiple requirements
    requirements = relationship('VoucherRequirementModel', back_populates='voucher')

    # Voucher can only be used in certain time of the day
    requirement_time = Column(TIME, nullable=True)

    # Voucher can only be used with a minimum spend
    requirement_minimum_spend = Column(Float, nullable=True)

    # Require user to login to an account
    requirement_member = Column(Boolean, nullable=True)

    #Voucher can only be used a number of times amount by the user (Automatically enables member requirement)
    max_uses = Column(Integer, nullable=True)

class VoucherRequirementModel(Base):
    __tablename__ = 'voucher_requirement'

    voucher_requirement_id = Column(String, primary_key=True)
    voucher_id = Column(Integer, ForeignKey('voucher.voucher_id'))
    voucher = relationship('VoucherModel', back_populates='requirements')

    # Require certain item in the receipt
    requirement_item_id = Column(Integer, nullable=True)

class VoucherUsesModel(Base):
    __tablename__ = 'voucher_uses'

    voucher_use_id = Column(String, primary_key=True)
    voucher_id = Column(String, ForeignKey("voucher.voucher_id"))
    user_id = Column(Integer)
    table_session_id = Column(String, ForeignKey("table_session.session_id"))

    use_datetime = Column(DATETIME)

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

# TableModel is currently abstract and it may seem redundant,
# but this is to forward compaible new features that will get implemented in the near future
# TODO: For release, implement dimension, position to identify table location for better representations
class TableModel(Base):
    __tablename__ = 'table'

    table_id = Column(String, primary_key=True)
    status = Column(Enum('Available', 'Occupied', "Unavailable"))
    seats = Column(Integer)

# TableSession begins the moment a QR receipt is printed and ends when the occupant checkout the bill, then the cycle repeats.
# TableSession contributes massively to analytic features
# TODO: For release, track individual requst/visit to be able to identify the time user will use to complete a order and checkout.
class TableSessionModel(Base):
    __tablename__ = 'table_session'

    # Session id is uniquely generated using UUID insetad of using incremental integer based Id.
    session_id = Column(String, primary_key=True)
    table_id = Column(String, ForeignKey('table.table_id'))

    # Signifies the true begin of the session
    # Detected when an occupant request/visits the ordering interface with the specific table_id attached to the session model
    start_datetime = Column(DATETIME, nullable=True)
    status = Column(Enum('Active', 'Completed'))
    head_count = Column(Integer, nullable=True)

    # Used to identify the number of visits from a specific user. Should be part of release TODO
    #occupant_user_id = Column(Integer, nullable=True)

# Create tables
Base.metadata.create_all(engine)
