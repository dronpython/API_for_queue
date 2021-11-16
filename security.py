from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status, Request
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

from models import TokenData, User, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def from_environ(name, default=None, allow_none=True):
    envname = f"[{name}]"
    try:
        var = os.environ[name]
        return var
    except:
        if not allow_none:
            raise Exception("ENV variable not found: " + envname)
        else:
            return default


try:
    cred = {
        'SECRET_KEY': from_environ('SECRET_KEY'),
        'ALGORITHM': from_environ('ALGORITHM'),
        'ACCESS_TOKEN_EXPIRE_MINUTES': from_environ('ACCESS_TOKEN_EXPIRE_MINUTES'),
    }

    raise Exception

except Exception as EE:
    try:
        print('>>>INTEGRATION EXCEPTION!!!')
        print('>>>', EE)
        print('>>>INTEGRATION TRY TO LOAD LOCAL ENV!!!')
        from integration_local import *

    except Exception as EE1:
        print('>>>INTEGRATION_LOCAL EXCEPTION!!!')
        print('>>>', EE1)

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = cred['SECRET_KEY']
ALGORITHM = cred['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = cred['ACCESS_TOKEN_EXPIRE_MINUTES']

dt = {"johndoe":0}

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

