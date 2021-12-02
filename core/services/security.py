import base64

from fastapi import Request
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.settings import config


async def get_fenec():
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, salt=config.fields.get('salt_for_token').get('env'), iterations=390000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(config.fields.get('secret_for_token').get('env')))
    return Fernet(key)


async def encrypt_password(password: str):
    f = await get_fenec()
    token = f.encrypt(bytes(password, encoding='utf-8'))
    return token.decode()


async def decrypt_password(token: str):
    f = await get_fenec()
    encrypted_token = f.decrypt(bytes(token, encoding='utf-8'))
    return encrypted_token.decode()


async def get_creds(request: Request):
    if request.headers.get('authorization'):
        creds_from_headers = request.headers['authorization']
        creds = base64.b64decode(creds_from_headers.replace('Basic ', '')).decode().split(":")

        try:
            username, password = creds
        except ValueError:
            return False

        return username, password
    else:
        return False
