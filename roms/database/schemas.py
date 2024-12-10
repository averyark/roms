from pydantic import BaseModel, Field, EmailStr, AfterValidator, StringConstraints, UUID4
from typing import List, Annotated, Literal, Optional
from .session import session
from .models import SessionTokenModel, UserModel
from datetime import datetime, date
import re

# Pydantic Schemas
class SessionTokenBase(BaseModel):
    token: str

class SessionTokenCreate(SessionTokenBase):
    user_id: int

def parse_birthday(value: str) -> str:
        # Parse the date from yyyymmdd format
    try:
        date = datetime.strptime(value, '%Y%m%d').date()
    except ValueError:
        raise ValueError('Invalid date format. Use yyyymmdd.')
    else:
        year = date.year
        now_year = datetime.now().year
        if year < 1900 or year > now_year:
            raise ValueError(f'Invalid date format. Year must be between 1900 and {now_year}.')

        return value

class UserBase(BaseModel):
    email: EmailStr
    first_name: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    last_name: Annotated[str, StringConstraints(min_length=1,max_length=256)]
    birthday: Annotated[str, AfterValidator(parse_birthday)]
    permission_level: int = Field(default=1)  # Default permission level for new users

def validate_password(value):
    if len(value) < 8 or len(value) > 256:
        raise ValueError('Password must be between 8 and 256 characters')
    if not re.search(r'^[a-zA-Z0-9\!\'\#\$\%\&\(\)\*\+\,\-\:\;\<\=\>\?\@\[\]\^\_\`\{\|\}\~\.\/]+$', value):
        raise ValueError('Password must only contain alphabets numbers and !\'#$%&()*+,-:;<=>?@[]^_`{|}~/.')
    if not re.search(r'[A-Za-z]', value):
        raise ValueError('Password must contain at least one alphabet')
    if not re.search(r'\d', value):
        raise ValueError('Password must contain at least one number')
    return value
# Extra parameters required for user creation

class UserCreate(UserBase):
    password: Annotated[str, AfterValidator(validate_password)]

class UserData(UserBase):
    is_guest_user: bool = False
    user_id: int
    hashed_password: str
    session_tokens: List[str] = Field(default_factory=list)

    class ConfigDict:
        from_attributes = True

    def commit(self):
        # Fetch existing tokens from the database
        existing_tokens = session.query(SessionTokenModel.token).filter_by(user_id=self.user_id).all()
        in_db_session_tokens = [token[0] for token in existing_tokens]

        # Prepare lists for tokens to add and remove
        add_session_tokens = []
        remove_session_tokens = []

        # Identify tokens to add
        for token in self.session_tokens:
            if token not in in_db_session_tokens:
                add_session_tokens.append(SessionTokenModel(user_id=self.user_id, token=token))

        # Identify tokens to remove
        for token in in_db_session_tokens:
            if token not in self.session_tokens:
                remove_session_tokens.append(token)

        # Insert new tokens
        if add_session_tokens:
            session.add_all(add_session_tokens)

        # Remove old tokens
        if remove_session_tokens:
            session.query(SessionTokenModel).filter(
                SessionTokenModel.user_id == self.user_id,
                SessionTokenModel.token.in_(remove_session_tokens)
            ).delete(synchronize_session=False)

        columns = [field for field in self.model_fields.keys() if field != 'user_id' and field != 'session_tokens']
        values = [getattr(self, field) for field in columns]

        # Create a dictionary of columns and values
        update_data = dict(zip(columns, values))

        # Update the user in the database
        session.query(UserModel).filter(UserModel.user_id == self.user_id).update(update_data)

        # Commit the changes to the database
        session.commit()

class IngredientBase(BaseModel):
    name: str

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    ingredient_id: UUID4
    is_deleted: bool = None

    class ConfigDict:
        from_attributes = True

class IngredientItemBase(BaseModel):
    item_id: str
    item_ingredient_id: str
    ingredient_id: int

class IngredientItemCreateNoItemIdKnowledge(BaseModel):
    ingredient_id: str

class IngredientItemCreate(IngredientItemBase):
    pass

class IngredientItem(IngredientItemBase):
    pass

class ItemBase(BaseModel):
    item_id: str
    price: float
    name: str
    picture_link: str
    description: str
    category: Literal['All', 'Beverage', 'Rice', 'Noodle', 'Snacks']

class ItemCreate(ItemBase):
    ingredients: List[IngredientItemCreateNoItemIdKnowledge]
    pass

class Item(ItemBase):
    is_deleted: bool = None
    ingredients: Optional[List[IngredientItem]] = Field(default_factory=list)

    class ConfigDict:
        from_attributes = True

class OrderItemBase(BaseModel):
    item_id: str
    quantity: int = Field(..., ge=1)
    remark: str = None
    pass

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    order_item_id: int
    order_id: str
    order_status: Literal["Ordered", "Preparing", "Serving", "Served"]

    order: Optional['Order'] = None

    class ConfigDict:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int = None
    table_session_id: str
    pass

class OrderCreate(OrderBase):
    orders: List[OrderItemCreate]

class Order(OrderBase):
    order_id: str
    user_id: int = None
    table_session_id: str
    orders: Optional[List[OrderItem]] = Field(default_factory=list)

    class ConfigDict:
        from_attributes = True

class StockBase(BaseModel):
    stock_batch_id: UUID4
    ingredient_id: UUID4
    expiry_date: date
    status: Literal['Ready to Use', 'Open', 'Used']
    pass

class StockCreate(StockBase):
    pass

class Stock(StockBase):
    stock_id: UUID4

    stock_batch: Optional['StockBatch']

    class ConfigDict:
        from_attributes = True

class StockBatchBase(BaseModel):
    acquisition_date: date
    pass

class StockBatchCreate(StockBatchBase):
    pass

class StockBatch(StockBatchBase):
    stock_batch_id: UUID4

    stocks: Optional[List[Stock]] = Field(default_factory=list)

    class ConfigDict:
        from_attributes = True

class EquipmentRemarkBase(BaseModel):
    equipment_name: str
    submit_date: date
    remark: str
    status: Literal['Submitted', 'Completed']
    pass

class EquipmentRemarkCreate(EquipmentRemarkBase):
    pass

class EquipmentRemark(EquipmentRemarkBase):
    remark_id: int

    class ConfigDict:
        from_attributes = True

class ReviewBase(BaseModel):
    user_id: int
    item_id: str
    remark: str
    value: int = Field(..., ge=1, le=10)
    review_datetime: datetime
    pass

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    review_id: int

    class ConfigDict:
        from_attributes = True

# Refer to the TableModel synbol in models.py for comments
class TableBase(BaseModel):
    table_id: str
    status: Literal['Available', 'Occupied', 'Unavailable']
    seats: int
    pass

class TableCreate(TableBase):
    pass

class Table(TableBase):

    class ConfigDict:
        from_attributes = True

class TableSessionBase(BaseModel):
    session_id: UUID4
    table_id: str
    headcount: int = None
    status: Literal['Active', 'Completed']

    start_datetime: datetime

class TableSessionCreate(TableSessionBase):
    pass

class TableSession(TableSessionBase):

    class ConfigDict:
        from_attributes = True
