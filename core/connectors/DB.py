import logging
from typing import Union
from psycopg2 import connect, DatabaseError, sql
from psycopg2.extras import NamedTupleCursor, RealDictCursor

from core.settings import settings

select_done_req_with_response = """SELECT qm.request_id, qm.status, qr.response_body FROM queue_main qm
JOIN queue_responses qr on qm.request_id = qr.request_id
WHERE qm.request_id = \'{}\' AND (qm.status = 'done' OR qm.status = 'error')"""

logger = logging.getLogger()


class DataBase:
    def __init__(self, database_config: dict):
        self.config = database_config
        self.conn = self._connect()

    def _connect(self):
        try:
            return connect(**self.config)
        except Exception as error:
            logger.info(error)
            logger.info(error.__traceback__)
            return None

    def select_data(self, table, *args, param_name: Union[str, int] = 1, param_value: Union[str, int] = 1):
        """Выборка записей из базы данных."""
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    select_string = 'SELECT * FROM {} WHERE {}=%s'
                    select_query = sql.SQL(select_string).format(sql.Identifier(table), sql.Identifier(param_name)
                    if isinstance(param_name, str)
                    else sql.Literal(param_name)
                                                                 )
                    cur.execute(select_query, (param_value,))
                    query_result = cur.fetchall()
                except (Exception, DatabaseError) as error:
                    logger.info(error)
                    query_result = None
                return query_result

    def insert_data(self, table, *args):
        """Добавление записи в базу данных."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                try:
                    insert_string = "INSERT INTO {} VALUES(DEFAULT, {})"
                    query = sql.SQL(insert_string).format(sql.Identifier(table),
                                                          sql.SQL(', ').join(sql.Placeholder() * len(args)))
                    cur.execute(query, args)
                    conn.commit()
                    logger.info('DATA INSERTED')
                except (Exception, DatabaseError) as error:
                    logger.info(error)

    def update_data(self, table, **kwargs):
        """ Обновленме записи в базе данных."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                try:
                    insert_string = 'UPDATE {} SET {}=%s WHERE {}=%s'
                    query = sql.SQL(insert_string).format(sql.Identifier(table), sql.Identifier(kwargs['field_name']),
                                                          sql.Identifier(kwargs['param_name']))
                    cur.execute(query, (kwargs['field_value'], kwargs['param_value'])
                                )
                    conn.commit()
                    logger.info('DATA UPDATED')
                except (Exception, DatabaseError) as error:
                    logger.info(error)

    def universal_select(self, query):
        """Выборка записей из базы данных."""
        with self._connect() as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
                try:
                    cur.execute(query)
                    data = cur.fetchall()
                    return data
                except (Exception, DatabaseError) as error:
                    logger.info(error)

    def get_queue_statistics(self, **kwargs):
        """Получение данных за период"""
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    paramlist = list()
                    if kwargs.get('period'):
                        paramlist.append(
                            f"SELECT * FROM queue_main WHERE timestamp >= NOW()::timestamp - INTERVAL '%(period)s minutes'", )
                    else:
                        paramlist.append(f"SELECT * FROM queue_main WHERE timestamp < NOW()::timestamp")
                    if kwargs.get('status'):
                        paramlist.append(f"and status = %(status)s")
                    if kwargs.get('directory'):
                        paramlist.append(f"and endpoint ~ %(directory)s")
                    if kwargs.get('endpoint'):
                        paramlist.append(f"and endpoint = %(endpoint)s")
                    string_param = ' '.join(paramlist)

                    logger.info(string_param)
                    cur.execute(string_param, kwargs)
                    data = cur.fetchall()
                    return data
                except (Exception, DatabaseError) as error:
                    logger.info(error)


DB = DataBase(settings.DATABASE_CONFIG)
