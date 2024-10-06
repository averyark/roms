from pydantic import BaseModel, Field, EmailStr
from typing import List
from .session import session
from .models import SessionTokenModel, UserModel

# Pydantic Schemas
class SessionTokenBase(BaseModel):
    token: str

class SessionTokenCreate(SessionTokenBase):
    user_id: int

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    birthday: str
    permission_level: int = Field(default=1)  # Default permission level for new users

# Extra parameters required for user creation
class UserCreate(UserBase):
    password: str

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
