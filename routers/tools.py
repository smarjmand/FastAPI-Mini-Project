from fastapi import Depends, HTTPException
from database import SessionLocal
from starlette import status
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from passlib.context import CryptContext  # to hash password
from fastapi.security import OAuth2PasswordBearer
from models import Users
from jose import jwt, JWTError
from datetime import timedelta, datetime


# Token : ==========================================================================================
SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


#--------------------------------------------
# to check if :
    # 1- user exists in db
    # 2- password is correct
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


#--------------------------------------------
# to create an access token includes : user_name, user_id, user_role and an expiry time for token
def create_access_token(
        username: str, user_id: int, role: str, expires_delta: timedelta
):
    expire = datetime.utcnow() + expires_delta
    encode = {'sub': username, 'id': user_id, 'role': role, 'exp': expire}
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


#--------------------------------------------
# to decode jwt and get user_name, user_id and user_role
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        if not user_id or not username:
            user_exception()
        return {'username': username, 'id': user_id, 'user_role': role}
    except JWTError:
        user_exception()


# Database : ==============================================================

# to open a connection to db, use it and then close the connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# Exceptions : ==============================================================
def user_exception():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate user')


def not_found_exception():
    raise HTTPException(status_code=404, detail='Item Not Found')


# Validation Models : ======================================================
class CreateUserRequest(BaseModel):
    user_name: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class TokenClass(BaseModel):
    access_token: str
    token_type: str


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=4)