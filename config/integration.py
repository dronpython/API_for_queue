import os
import base64
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status, Request
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import InvalidToken

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
        'SECRET_FOR_TOKEN': from_environ('SECRET_FOR_TOKEN'),
        'SALT_FOR_TOKEN': from_environ('SALT_FOR_TOKEN')
    }

    DATABASE_CONFIG = {
        "host": '127.0.0.1',
        "database": "localdatabase",
        "user": "localuser",
        "password": "localpassword"
    }

    # raise Exception

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
SECRET_FOR_TOKEN = cred['SECRET_FOR_TOKEN'].encode()
SALT_FOR_TOKEN =cred['SALT_FOR_TOKEN'].encode()

dt = {"johndoe":0}

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
        "password": '123'
    }
}
