import os

from pydantic import (
    BaseSettings,
)


class Settings(BaseSettings):
    auth_key: str = 'unusable_key'
    api_key: str = 'sw.api'

    DATABASE_CONFIG = {
        'host': os.environ['db_host'],
        'port': os.environ['db_port'],
        'database': os.environ['db_name'],
        'user': os.environ['db_user'],
        'password': os.environ['db_password']
    }

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
            },
            'path': {
                'config': os.environ['config_path']
            },
            'default_dt': {
                'env': os.environ['default_dt']
            }
        }


settings = Settings()
config = Settings().Config()
