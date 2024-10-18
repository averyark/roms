from pydantic import BaseModel, Field, EmailStr, AfterValidator, StringConstraints, field_validator, SecretStr
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
    stock_quantity: float
    unit: str

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    pass

class IngredientItemBase(BaseModel):
    item_id: int
    ingredient_id: int
    quantity: float

class IngredientItemCreateNoItemIdKnowledge(BaseModel):
    ingredient_id: int
    quantity: float

class IngredientItemCreate(IngredientItemBase):
    pass

class IngredientItem(IngredientItemBase):
    pass

class ItemBase(BaseModel):
    price: float
    name: str
    picture_link: str
    description: str
    category: Literal['All', 'Beverage', 'Rice', 'Noodle', 'Snacks']

class ItemCreate(ItemBase):
    ingredients: List[IngredientItemCreateNoItemIdKnowledge]
    pass

class Item(ItemBase):
    item_id: int

    ingredients: Optional[List[IngredientItem]] = Field(default_factory=list)

    class ConfigDict:
        from_attributes = True

class OrderItemBase(BaseModel):
    item_id: int
    quantity: int
    remark: Optional[str]
    pass

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    order_item_id: int
    order_id: int
    order_status: Literal["Ordered", "Preparing", "Serving", "Served"]

    order: Optional['Order'] = None

    class ConfigDict:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int
    pass

class OrderCreate(OrderBase):
    orders: List[OrderItemCreate]

class OrderCreateNoUserIdKnowledge(BaseModel):
    orders: List[OrderItemCreate]

class Order(OrderBase):
    order_id: int
    user_id: int
    orders: Optional[List[OrderItem]] = Field(default_factory=list)

    class ConfigDict:
        from_attributes = True

class StockBase(BaseModel):
    stock_batch_id: int
    ingredient_id: int
    expiry_date: date
    status: Literal['Ready to Use', 'Open', 'Used']
    pass

class StockCreate(StockBase):
    stock_batch_id: int

class Stock(StockBase):
    stock_id: int
    stock_batch_id: int

    stock_batch: Optional['StockBatch']

    class ConfigDict:
        from_attributes = True

class StockBatchBase(BaseModel):
    acquisition_date: date
    pass

class StockBatchCreate(StockBatchBase):
    pass

class StockBatch(StockBatchBase):
    stock_batch_id: int

    stocks: Optional[List[Stock]] = Field(default_factory=list)

    class ConfigDict:
        from_attributes = True
