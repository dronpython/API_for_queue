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


def insert_data(uuid, endpoint, data, author, status, date, time, timestamp):
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

        # execute a statement
        cur.execute(f"INSERT INTO queue VALUES('{uuid}', '{endpoint}', '{data}', '{author}', '{status}', '{date}', '{time}', '{timestamp}')")

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
