from psycopg2 import connect, DatabaseError
from configparser import ConfigParser
from psycopg2.extras import RealDictCursor
from core.settings import settings


def config(filename='db.ini', section='postgresql'):
    """Загрузка конфига для базы данных.
    """
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


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
