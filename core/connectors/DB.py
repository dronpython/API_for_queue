from psycopg2 import connect, DatabaseError
from configparser import ConfigParser
from psycopg2.extras import RealDictCursor
from core.settings import settings


class DataBase:
    def __init__(self, DATABASE_CONFIG:dict):
        self.config = DATABASE_CONFIG
        self.conn = None
        self.conn = self._connect()

    def _connect(self):    
        try:
            return connect(**self.config)
        except Exception as ERROR:
            print(ERROR)
            print(ERROR.__traceback__)
            return None

    def _close(self):
        try:
            return connect(**self.config).close()
        except Exception as ERROR:
            print(ERROR)
            print(ERROR.__traceback__)
            return None


DB = DataBase(settings.DATABASE_CONFIG)
