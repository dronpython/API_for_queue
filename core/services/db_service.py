from core.connectors.DB import DB, RealDictCursor, DatabaseError


# def insert_data(table, *args):
#     """Добавление записи в базу данных.
#     """
#     try:
#         # create a cursor
#         cur = DB.conn.cursor(cursor_factory=RealDictCursor)
#
#         # join all the arguments
#         insert_arguments = "','".join(args)
#
#         # compose into string with args
#         insert_string = "INSERT INTO {} VALUES(DEFAULT,'{}')"
#
#         # make it sql understandable
#         insert_query = insert_string.format(table, insert_arguments)
#
#         # execute a statement
#         cur.execute(insert_query)
#
#         # display the PostgreSQL database server version
#         DB.conn.commit()
#
#         # close the communication with the PostgreSQL
#         cur.close()
#     except (Exception, DatabaseError) as error:
#         print(error)
#
#
# def get_request_by_uuid(uuid: str):
#     """Получение данных по uuid."""
#     try:
#         cur = DB.conn.cursor(cursor_factory=RealDictCursor)
#         cur.execute(f"SELECT * from queue_main WHERE uuid = '{uuid}'")
#         data = cur.fetchone()
#         cur.close()
#         return data
#     except (Exception, DatabaseError) as error:
#         print(error)
#
#
# def update_request_by_uuid(uuid: str, field: str, value: str):
#     """Обновление данных по uuid."""
#     try:
#         cur = DB.conn.cursor(cursor_factory=RealDictCursor)
#         cur.execute(f"UPDATE queue_main SET {field} = '{value}' WHERE uuid = '{uuid}'")
#         DB.conn.commit()
#         cur.close()
#     except (Exception, DatabaseError) as error:
#         print(error)


def get_queue_statistics(**kwargs):
    """Получение данных за период"""
    try:
        cur = DB.conn.cursor(cursor_factory=RealDictCursor)
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
