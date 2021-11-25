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
    auth_key: str = 'qe'
    # api_key: str = Field(..., env='my_api_key')
    api_key: str = 'qwe'

    redis_dsn: RedisDsn = 'redis://user:pass@localhost:6379/1'
    pg_dsn: PostgresDsn = 'postgres://user:pass@localhost:5432/foobar'

    special_function: PyObject = 'math.cos'
    DATABASE_CONFIG = {
        'host': os.environ['db_host'],
        'port': os.environ['db_port'],
        'database': os.environ['db_name'],
        'user': os.environ['db_user'],
        'password': os.environ['db_password']
    }
    fake_users_db = {
        'qwe': {
            'username': 'qwe',
            'full_name': 'John Doe',
            'email': 'johndoe@example.com',
            'hashed_password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
            'disabled': False,
            'password': '123',
            'dt': 10000,
        },
        os.environ['old_api_user']: {
            'username': os.environ['old_api_user'],
            'full_name': 'John Doe',
            'email': 'johndoe@example.com',
            'hashed_password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
            'disabled': False,
            'password': os.environ['old_api_password'],
            'dt': 0
        }
    }
    # to override domains:
    # export my_prefix_domains='['foo.com', 'bar.com']'
    domains: Set[str] = set()

    # to override more_settings:
    # export my_prefix_more_settings='{'foo': 'x', 'apple': 1}'
    more_settings: SubModel = SubModel()

    class Config:
        env_prefix = '.env'  # defaults to no prefix, i.e. ''
        fields = {
            'auth_key': {
                'env': 'my_auth_key',
            },
            'redis_dsn': {
                'env': ['service_redis_dsn', 'redis_url']
            },
            'secret_for_token': {
                'env': os.environ['secret_for_token'].encode()
            },
            'salt_for_token': {
                'env': os.environ['salt_for_token'].encode()
            },
            'servers': {
                'ldap': os.environ['ldap_server']
            },
            'cred': {
                'domain_auth': {
                    'login': os.environ['old_api_user'],
                    'password': os.environ['old_api_password']
                }
            },
            'ldap': {
                'search_tree': os.environ['ldap_search_tree'],
                'search_tree_ca': os.environ['ldap_search_tree_ca']
            }
        }


settings = Settings()
config = Settings().Config()
