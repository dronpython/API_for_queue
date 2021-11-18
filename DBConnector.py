import psycopg2
from configparser import ConfigParser
from psycopg2.extras import RealDictCursor


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


def insert_data(table, *args):
    """Добавление записи в базу данных.
    """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # join all the arguments
        insert_arguments = "','".join(args)

        # compose into string with args
        insert_string = "INSERT INTO {} VALUES(DEFAULT,'{}')"

        # make it sql understandable
        insert_query = insert_string.format(table, insert_arguments)

        # execute a statement
        cur.execute(insert_query)

        # display the PostgreSQL database server version
        conn.commit()

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def get_request_by_uuid(uuid: str):
    """Получение данных по uuid."""
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"SELECT * from queue WHERE uuid = '{uuid}'")
        data = cur.fetchone()
        cur.close()
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def update_request_by_uuid(uuid: str, field: str, value: str):
    """Обновление данных по uuid."""
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(f"UPDATE queue SET {field} = '{value}' WHERE uuid = '{uuid}'")
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def get_queue_statistics(**kwargs):
    """Получение данных за период"""
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        paramlist = list()
        if kwargs.get('period'):
            paramlist.append(
                f"SELECT * FROM queue WHERE timestamp >= NOW()::timestamp - INTERVAL '{kwargs['period']} minutes'")
        else:
            paramlist.append(f"SELECT * FROM queue WHERE timestamp < NOW()::timestamp")
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
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
