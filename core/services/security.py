import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.settings import settings
from core.settings import config


async def get_fenec():
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, salt=config.fields.get('salt_for_token').get('env'), iterations=390000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(config.fields.get('secret_for_token').get('env')))
    return Fernet(key)


async def encrypt_password(password):
    f = await get_fenec()
    token = f.encrypt(bytes(password, encoding='utf-8'))
    return token.decode()


async def decrypt_password(tek):
    f = await get_fenec()
    encrypted_token = f.decrypt(bytes(tek, encoding='utf-8'))
    return encrypted_token.decode()
