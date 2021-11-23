from psycopg2 import connect, DatabaseError
from configparser import ConfigParser
from psycopg2.extras import RealDictCursor
from core.settings import settings
from psycopg2.extras import NamedTupleCursor
from typing import Union

query_dict = {"insert_into_queue_main": "INSERT INTO queue_main(rqid, endpoint, domain, author, status, priority, work_count) "
                                        "VALUES('{uuid}', '{endpoint}', '{domain}', "
                                        "'{author}', '{status}', '{priority}', '{work_count}')",
              "insert_into_queue_requests": "INSERT INTO queue_requests(rqid, request_type, request_url, request_body, request_headers, request_file) "
                                            "VALUES('{uuid}', '{request_type}', '{request_url}', "
                                            "'{request_body}', '{request_headers}', '{request_file}')",
              "select_info_by_uuid": "select qm.rqid, qm.status, qr.response_status_code, qr.response_status, qr.response_body from queue_main qm "
                                     "join queue_responses qr on qm.rqid = qr.rqid "
                                     "WHERE qm.rqid = '{uid}'",
              }


def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def insert_data(query):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        params = config()
        conn = connect(**params)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()
    except (Exception, DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def universal_select(query):
    """Выборка записей из базы данных."""
    conn = None
    try:
        params = config()
        conn = connect(**params)
        cur = conn.cursor(cursor_factory=NamedTupleCursor)
        cur.execute(query)
        data = cur.fetchall()
        cur.close()
        return data
    except (Exception, DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def get_response_by_uuid(query: str):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        params = config()
        conn = connect(**params)
        cur = conn.cursor(cursor_factory=NamedTupleCursor)
        cur.execute(query)
        data = cur.fetchone()
        cur.close()
        return data
    except (Exception, DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


class DataBase:
    def __init__(self, database_config: dict):
        self.config = database_config
        self.conn = self._connect()

    def _connect(self):
        try:
            return connect(**self.config)
        except Exception as error:
            print(error)
            print(error.__traceback__)
            return None

    def select_data(self, table, *args, param_name: Union[str, int] = 1, param_value: Union[str, int] = 1):
        """Выборка записей из базы данных."""
        with self._connect() as conn:
            try:
                cur = conn.cursor(cursor_factory=NamedTupleCursor)
                select_arguments = '","'.join(args)
                select_string = 'SELECT "{}" FROM {} WHERE {}={}' if isinstance(param_name, int) \
                    else 'SELECT "{}" FROM {} WHERE "{}"=\'{}\''
                select_query = select_string.format(select_arguments, table, param_name, param_value)
                cur.execute(select_query)
                query_result = cur.fetchall()
                cur.close()
            except (Exception, DatabaseError) as error:
                print(error)
                query_result = None
            return query_result

    def insert_data(self, table, *args):
        """Добавление записи в базу данных."""
        with self._connect() as conn:
            try:
                cur = conn.cursor()
                insert_arguments = "','".join(args)
                insert_string = "INSERT INTO {} VALUES(DEFAULT,'{}')"
                insert_query = insert_string.format(table, insert_arguments)
                cur.execute(insert_query)
                conn.commit()
                cur.close()
            except (Exception, DatabaseError) as error:
                print(error)
                
db = DataBase(settings.DATABASE_CONFIG)


# def config(filename='db.ini', section='postgresql'):
#     """Загрузка конфига для базы данных.
#     """
#     # create a parser
#     parser = ConfigParser()
#     # read config file
#     parser.read(filename)
# 
#     # get section, default to postgresql
#     db = {}
#     if parser.has_section(section):
#         params = parser.items(section)
#         for param in params:
#             db[param[0]] = param[1]
#     else:
#         raise Exception('Section {0} not found in the {1} file'.format(section, filename))
# 
#     return db
# 
# 
# class DataBase:
#     def __init__(self, DATABASE_CONFIG:dict):
#         self.config = DATABASE_CONFIG
#         self.conn = None
#         self.conn = self._connect()
# 
#     def _connect(self):    
#         try:
#             return connect(**self.config)
#         except Exception as ERROR:
#             print(ERROR)
#             print(ERROR.__traceback__)
#             return None
# 
#     def _close(self):
#         try:
#             return connect(**self.config).close()
#         except Exception as ERROR:
#             print(ERROR)
#             print(ERROR.__traceback__)
#             return None
# 
# 
# DB = DataBase(settings.DATABASE_CONFIG)
