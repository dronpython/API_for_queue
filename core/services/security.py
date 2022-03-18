from base64 import urlsafe_b64encode, b64decode, b64encode
import hashlib
import logging
from typing import Tuple, Union
import requests

from fastapi import Request, HTTPException, status
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.settings import config
from core.connectors.LDAP import ldap
from core.connectors.DB import DB

logger = logging.getLogger(__name__)


async def get_fenec():
    """Получить ключ шифрования."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, salt=config.fields.get("salt_for_token").get("env"), iterations=390000,
        backend=default_backend()
    )
    key = urlsafe_b64encode(kdf.derive(config.fields.get("secret_for_token").get("env")))
    return Fernet(key)


async def encrypt_password(password: str):
    """Зашифровать пароль."""
    f = await get_fenec()
    token = f.encrypt(bytes(password, encoding="utf-8"))
    return token.decode()


async def decrypt_password(token: str):
    """Расшифровать пароль."""
    f = await get_fenec()
    encrypted_token = f.decrypt(bytes(token, encoding="utf-8"))
    return encrypted_token.decode()


async def get_creds(headers: Request.headers) -> Union[Tuple, bool]:
    """Получить учетку по заголовку авторизации."""
    if headers.get("authorization"):
        creds_from_headers = headers["authorization"]
        creds = b64decode(creds_from_headers.replace("Basic ", "")).decode().split(":")

        try:
            username, password = creds
        except ValueError:
            return False

        return username, password
    return False


async def old_api_token(username: str, password: str):
    """Получить токен авторизации для старой API."""
    creds = f"{username}:{password}"
    user_and_pass = b64encode(bytes(creds, encoding="utf8")).decode("ascii")
    basic_auth = "Basic %s" % user_and_pass
    hashed_token = await get_hash(basic_auth)
    api_token = "AToken:" + hashed_token
    return api_token


async def get_hash(text):
    """Получить хэш."""
    m = hashlib.md5()
    for x in range(10):
        m.update(text.encode())
    return m.hexdigest()


async def get_token(headers):
    """Запрос на получение токена."""
    try:
        response = requests.post(config.fields.get("api_server") + "/api/v3/svc/get_token",
                                 json={}, headers=headers)
        token = response.json().get("token")
    except Exception as e:
        print(e)
        token = ""
    return token


async def verify_request(headers: Request.headers):
    """Авторизоация запроса."""
    username = ""
    if headers.get("authorization"):
        if "Basic" in headers.get("authorization"):
            credentials_answer = await get_creds(headers)
            logger.info("GOT BASIC AUTH")
            if not credentials_answer:
                logger.info("NO CREDENTIALS IN HEADER")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can not find auth header",
                )
            username, password = credentials_answer
            logger.info("GOT USERNAME AND PASSWORD")
        else:
            logger.info("GOT NO AUTH")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token or Basic authorize required",
            )
        result: bool = ldap._check_auth(server=config.fields.get("servers").get("ldap"), domain="SIGMA",
                                        login=username, password=password)
        if not result:
            logger.info("USER NOT AUTHORIZED IN LDAP")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authorized in ldap",
            )
    elif headers.get("token"):
        token: str = headers["token"]
        token_db: dict = DB.select_data("tokens", param_name="token", param_value=token, fetch_one=True)
        if token_db:
            username = token_db.get("user")
        else:
            logger.info("NO SUCH TOKEN IN DB")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorize required",
            )
    else:
        logger.info("GOT NO AUTH")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token or Basic auth required",
        )
    if username:
        return username
