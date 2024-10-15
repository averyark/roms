# @fileName: login.py
# @creation_date: 19/09/2024
# @authors: averyark

from typing import Annotated, Optional
from asyncio import run_coroutine_threadsafe

from .credentials import SECRET_KEY, USE_ALGORITHM, pwd_context, JWT_EXPIRATION_MINUTES
from .api import app
from .database import session, UserModel, UserCreate, UserBase, SessionTokenModel
from .user import get_user, User

from datetime import datetime, timezone, timedelta
from jwt import encode as jwt_encode, decode as jwt_decode, ExpiredSignatureError
from pydantic import BaseModel
from fastapi import HTTPException, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/account/swagger_login')

# NOTE: Annotated[str, Depends(oauth2_scheme)] is for swagger interface
async def authenticate(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        # NOTE: Ignore _bcrypt.__about_ Error
        payload = jwt_decode(token, SECRET_KEY, algorithms=[USE_ALGORITHM])
        user_id = payload.get('sub')
        if user_id is None:
            raise credentials_exception

        # Check if the session token is still valid
        # Users can invalidate tokens by logging out
        user = get_user(user_id)

        if user is None:
            raise credentials_exception

        if not token in user.session_tokens:
            raise credentials_exception

    except ExpiredSignatureError:
        # Remove the session token from the database because it has expired
        if token in user.session_tokens:
            user.session_tokens.remove(token)

        raise credentials_exception

    return user

class validate_role:
    def __init__(self, roles):
        self.roles = roles

    def __call__(self, user: Annotated[User, Depends(authenticate)]):
        if user.get_role() in self.roles:
            return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Insufficient permissions'
        )

class UserInfoUpdate(BaseModel):
    birthday: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

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

@app.get(path='/account/get_token', tags=['account'])
async def login(email: str, password: str) -> Token:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Incorrect email or password',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    # validate credentials
    # TODO: timing attack fix
    if email is None or password is None:
        raise credentials_exception

    try:
        user = get_user(get_userid_from_email(email))
    except LookupError as err:
        raise  credentials_exception

    if user is None:
        raise credentials_exception

    if not pwd_context.verify(password, user.hashed_password):
        raise credentials_exception

    try:
        session_token = create_session_token(user_id=user.user_id)
        # NOTE: Ignore _bcrypt.__about_ Error
    except Exception as err:
        session_token = None
        print(f'Unable to load userdata: {err}')

    # Check for expired tokens by trying to authenticate, do cleanup.
    for token in user.session_tokens:
        try:
            authenticate(token)
        except: pass

    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error occurred'
        )

    return Token(access_token=session_token, token_type='bearer')

@app.delete(path='/account/expire_token', tags=['account'])
async def logout(user: Annotated[User, Depends(authenticate)], token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Unable to expire token',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        user = get_user(user.user_id)
    except:
        raise credentials_exception

    if not user.session_tokens.index(token):
        raise credentials_exception

    # commit after modifying
    user.session_tokens.remove(token)
    user.commit()

# Login interface for swagger
@app.post(path='/account/swagger_login', tags=['account'])
async def swagger_login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    # retrieve the user_id
    token = await login(form.username, form.password)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return token

# NOTE: You cannot input permissionLevel from this api
@app.post(path='/account/signup', tags=['account'])
async def signup(data: UserCreate):
    # redundant, already checked by pydantic but just putting it here for now
    #validate_user_data(data)

    user = session.query(UserModel).filter(UserModel.email == data.email).one_or_none()

    if user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='This email already exists in the database'
        )

    # Overwrite permission_level
    data.permission_level = 10
    create_user(data)

def get_userid_from_email(email: str) -> int:
    user_id = None
    try:
       user = session.query(UserModel).filter(UserModel.email == email).one()
       user_id = user.user_id
    except Exception as err:
        pass

    return user_id

def create_account(data: UserCreate):
    user = session.query(UserModel).filter(UserModel.email == data.email).one_or_none()

    if user:
        raise LookupError('This email already exist in the database')

    create_user(data)

# NOTE: This is used to create account with different permissionLevel, it is inaccessible at customer level. Requries authentication.
@app.post('/account/add/', tags=['account'])
async def create_account_async(user: Annotated[User, Depends(validate_role(roles=['Manager']))], data: UserCreate):
    create_account(data)

@app.patch('/account/edit/credentials/', tags=['account'])
async def edit_credentials(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    user_id: int,
    new_credentials: str
):
    try:
        edited_user = get_user(user_id)
        edited_user.hashed_password = pwd_context.hash(new_credentials)
        edited_user.commit()
    except: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.delete('/account/edit/delete/', tags=['account'])
async def delete_account(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager']))
    ],
    user_id: int,
):
    try:

        pass
    except: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.patch('/account/edit/user_info', tags=['account'])
async def update_user_info(
    user: Annotated[
        User, Depends(authenticate)
    ],
    update_fields: UserInfoUpdate,
    user_id: int = None
):
    target_user = user
    if not user_id is None:
        if not user.get_role() in ['Manager']:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        else:
            target_user = get_user(user_id)

    target_user.first_name = update_fields.first_name
    target_user.last_name = update_fields.last_name
    target_user.birthday = update_fields.birthday

    # Check unique email
    target_user.email = update_fields.email

    target_user.commit()

@app.get('/users', tags=['account'])
async def get_users(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ]
) -> Page[UserBase]:

    return paginate(session, select(UserModel, UserModel.email, UserModel.first_name, UserModel.last_name, UserModel.birthday, UserModel.permission_level).order_by(UserModel.permission_level))
