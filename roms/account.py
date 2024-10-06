# @fileName: login.py
# @creation_date: 19/09/2024
# @authors: averyark

from icecream import ic
from .credentials import SECRET_KEY, USE_ALGORITHM, pwd_context
from .api import app
from .database import session, create_session_token, create_user, UserModel, UserCreate
from .user import get_user, User
from .validate import validate_user_data
from asyncio import run_coroutine_threadsafe

from jwt import encode as jwt_encode, decode as jwt_decode, ExpiredSignatureError
from pydantic import BaseModel
from fastapi import HTTPException, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/account/swagger_login")

from typing import Annotated, Optional

# NOTE: Annotated[str, Depends(oauth2_scheme)] is for swagger interface
async def authenticate(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # NOTE: Ignore _bcrypt.__about_ Error
        payload = jwt_decode(token, SECRET_KEY, algorithms=[USE_ALGORITHM])
        user_id = payload.get("sub")
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
            detail="Insufficient permissions"
        )

class UserInfoUpdate(BaseModel):
    birthday: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

@app.get(path="/account/get_token", tags=["account"])
async def login(email: str, password: str) -> Token:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
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
        print(f"Unable to load userdata: {err}")

    # Check for expired tokens by trying to authenticate, do cleanup.
    for token in user.session_tokens:
        try:
            authenticate(token)
        except: pass

    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred"
        )

    return Token(access_token=session_token, token_type="bearer")

@app.delete(path="/account/expire_token", tags=["account"])
async def logout(user: Annotated[User, Depends(authenticate)], token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to expire token",
        headers={"WWW-Authenticate": "Bearer"},
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
@app.post(path="/account/swagger_login", tags=["account"])
async def swagger_login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    # retrieve the user_id
    token = await login(form.username, form.password)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return token

# NOTE: You cannot input permissionLevel from this api
@app.post(path="/account/signup", tags=["account"])
async def signup(data: UserCreate):
    try:
        # redundant, already checked by pydantic but just putting it here for now
        validate_user_data(data)

        user = session.query(UserModel).filter(UserModel.email == data.email).one_or_none()

        if user:
            raise LookupError("This email already exist in the database")

        try:
            # Overwrite permission_level
            data.permission_level = 10
            create_user(data)
        except Exception as err:
            raise err
    except LookupError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=err
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err
        )

def get_userid_from_email(email: str) -> int:
    user_id = None
    try:
       user = session.query(UserModel).filter(UserModel.email == email).one()
       user_id = user.user_id
    except Exception as err:
        pass

    return user_id

def create_account(data: UserCreate):
    # redundant, already checked by pydantic but just putting it here for now
    validate_user_data(data)

    user = session.query(UserModel).filter(UserModel.email == data.email).one_or_none()

    if user:
        raise LookupError("This email already exist in the database")

    create_user(data)

# NOTE: This is used to create account with different permissionLevel, it is inaccessible at customer level. Requries authentication.
@app.post("/account/add/", tags=["account"])
async def create_account_async(user: Annotated[User, Depends(validate_role(roles=["Manager"]))], data: UserCreate):
    create_account(data)

@app.patch("/account/edit/credentials/", tags=["account"])
def edit_credentials(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
    user_id: int,
    new_credentials: str
):
    try:
        edited_user = get_user(user_id)
        edited_user.hashed_password = pwd_context.hash(new_credentials)
        edited_user.commit()
    except: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.delete("/account/edit/delete/", tags=["account"])
def delete_account(
    user: Annotated[
        User, Depends(validate_role(roles=["Manager"]))
    ],
    user_id: int,
):
    try:

        pass
    except: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.patch("/account/edit/user_info", tags=["account"])
def update_user_info(
    user: Annotated[
        User, Depends(authenticate)
    ],
    update_fields: UserInfoUpdate,
    user_id: int = None
):
    target_user = user
    if not user_id is None:
        if not user.get_role() in ["Manager"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        else:
            target_user = get_user(user_id)

    target_user.first_name = update_fields.first_name
    target_user.last_name = update_fields.last_name
    target_user.birthday = update_fields.birthday

    # Check unique email
    target_user.email = update_fields.email

    target_user.commit()
