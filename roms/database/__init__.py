from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

from .schemas import UserBase, UserData, UserCreate
from .models import UserModel, SessionTokenModel
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

def get_user_data_in_dict(user_id: int) -> dict:
    try:
        user = session.query(UserModel).filter(UserModel.user_id == user_id).one()
        return {
            "user_id": user_id,
            "session_tokens": [token.token for token in user.session_tokens],
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "birthday": user.birthday,
            "permission_level": user.permission_level,
            "hashed_password": user.hashed_password
        }
    except NoResultFound:
        return None

def create_session_token(user_id: int) -> str:
    # Generate JWT token
    expiration = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    token = jwt_encode({
        "sub": user_id,
        "exp": expiration
    }, SECRET_KEY, algorithm=USE_ALGORITHM)

    # Store the token in the database
    session_token = SessionTokenModel(user_id=user_id, token=token)
    session.add(session_token)
    session.commit()

    return token

# Create tables
Base.metadata.create_all(engine)
