from psycopg2 import connect, DatabaseError
from configparser import ConfigParser
from psycopg2.extras import NamedTupleCursor, RealDictCursor
from core.settings import settings
from typing import Union

select_done_req_with_response = """SELECT qm.rqid, qm.status, qr.response_body FROM queue_main qm
JOIN queue_responses qr on qm.rqid = qr.rqid
WHERE qm.rqid = \'{}\' AND (qm.status = 'DONE' OR qm.status = 'ERROR')"""



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

    def update_data(self, table, **kwargs):
        """ Обновленме записи в базе данных."""
        with self._connect() as conn:
            try:
                cur = conn.cursor()
                insert_string = 'UPDATE {} SET "{}"=\'{}\' WHERE "{}"=\'{}\''
                insert_query = insert_string.format(table, kwargs['field_name'], kwargs['field_value'],
                                                    kwargs['param_name'], kwargs['param_value'])
                cur.execute(insert_query)
                conn.commit()
                cur.close()
            except (Exception, DatabaseError) as error:
                print(error)

    def universal_select(self, query):
        """Выборка записей из базы данных."""
        with self._connect() as conn:
            try:
                cur = conn.cursor(cursor_factory=NamedTupleCursor)
                cur.execute(query)
                data = cur.fetchall()
                cur.close()
                return data
            except (Exception, DatabaseError) as error:
                print(error)

    def get_queue_statistics(self, **kwargs):
        """Получение данных за период"""
        with self._connect() as conn:
            try:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                paramlist = list()
                if kwargs.get('period'):
                    paramlist.append(
                        f"SELECT * FROM queue_main WHERE timestamp >= NOW()::timestamp - INTERVAL '{kwargs['period']} minutes'")
                else:
                    paramlist.append(f"SELECT * FROM queue_main WHERE timestamp < NOW()::timestamp")
                if kwargs['status']:
                    paramlist.append(f"and status = '{kwargs['status']}'")
                if kwargs['directory']:
                    paramlist.append(f"and endpoint ~ '{kwargs['directory']}'")
                if kwargs['endpoint']:
                    paramlist.append(f"and endpoint = '{kwargs['endpoint']}'")
                string_param = ' '.join(paramlist)
                print(string_param)
                cur.execute(string_param)
                data = cur.fetchall()
                cur.close()
                return data
            except (Exception, DatabaseError) as error:
                print(error)

    def get_request_by_uuid(self, uuid: str):
        """Получение данных по uuid."""
        with self._connect() as conn:
            try:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute(f"SELECT * from queue_main WHERE rqid = '{uuid}'")
                data = cur.fetchone()
                cur.close()
                return data
            except (Exception, DatabaseError) as error:
                print(error)

    def update_request_by_uuid(self, uuid: str, field: str, value: str):
        """Обновление данных по uuid."""
        with self._connect() as conn:
            try:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute(f"UPDATE queue_main SET {field} = '{value}' WHERE rqid = '{uuid}'")
                DB.conn.commit()
                cur.close()
            except (Exception, DatabaseError) as error:
                print(error)


DB = DataBase(settings.DATABASE_CONFIG)
