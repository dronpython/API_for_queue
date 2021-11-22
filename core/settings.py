from typing import Set
import os

from pydantic import (
    BaseModel,
    BaseSettings,
    PyObject,
    RedisDsn,
    PostgresDsn,
    Field,
)


class SubModel(BaseModel):
    foo = 'bar'
    apple = 1


class Settings(BaseSettings):
    def from_environ(self, name, default=None, allow_none=True):
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

        # raise Exception

    except Exception as EE:
        try:
            print('>>>INTEGRATION EXCEPTION!!!')
            print('>>>', EE)
            print('>>>INTEGRATION TRY TO LOAD LOCAL ENV!!!')
            # from integration_local import *

        except Exception as EE1:
            print('>>>INTEGRATION_LOCAL EXCEPTION!!!')
            print('>>>', EE1)

    auth_key: str = 'qe'
    # api_key: str = Field(..., env='my_api_key')
    api_key: str = 'qwe'

    redis_dsn: RedisDsn = 'redis://user:pass@localhost:6379/1'
    pg_dsn: PostgresDsn = 'postgres://user:pass@localhost:5432/foobar'

    special_function: PyObject = 'math.cos'
    DATABASE_CONFIG = {
        "host": '127.0.0.1',
        "database": "a19333690",
        "user": "a19333690",
        "password": "1234"
    }
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
    # to override domains:
    # export my_prefix_domains='["foo.com", "bar.com"]'
    domains: Set[str] = set()

    # to override more_settings:
    # export my_prefix_more_settings='{"foo": "x", "apple": 1}'
    more_settings: SubModel = SubModel()

    class Config:
        env_prefix = '.env'  # defaults to no prefix, i.e. ""
        fields = {
            'auth_key': {
                'env': 'my_auth_key',
            },
            'redis_dsn': {
                'env': ['service_redis_dsn', 'redis_url']
            },
            'secret_for_token': {
                'env': 'OUTSECRETKEY'.encode()
            },
            'salt_for_token': {
                'env': 'SALTAGE'.encode()
            }
        }

settings = Settings()
config = Settings().Config()


print(Settings().dict())
