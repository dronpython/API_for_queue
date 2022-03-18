import pytest
from base64 import b64encode
from psycopg2 import connect

from fastapi.testclient import TestClient

from main import app
from core.settings import settings
from tests.test_auth import user, user_password

client = TestClient(app)

TEST_JSON = {"user": "asd"}
database_config = settings.DATABASE_CONFIG


@pytest.fixture(autouse=False, scope="function")
def fixture_clean_queue_main():
    with connect(**database_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE queue_main CASCADE")
            conn.commit()


@pytest.fixture(autouse=False, scope="function")
def fixture_clean_queue_request():
    with connect(**database_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE queue_requests")
            conn.commit()


def test_empty_queue_main(fixture_clean_queue_main):
    with connect(**database_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM queue_main")
            query_result = cursor.fetchone()
            assert query_result[0] == 0


def test_add_to_empty_queue_main(fixture_clean_queue_main, user, user_password):
    creds = f"{user}:{user_password}"
    user_and_pass = b64encode(bytes(creds, encoding="utf8")).decode("ascii")
    headers = {"Authorization": "Basic %s" % user_and_pass}
    client.post("/bb/zxc/", json=TEST_JSON, headers=headers)
    with connect(**database_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM queue_main")
            query_result = cursor.fetchone()
            assert query_result[0] == 1


def test_add_to_non_empty_queue_main(user, user_password):
    creds = f"{user}:{user_password}"
    user_and_pass = b64encode(bytes(creds, encoding="utf8")).decode("ascii")
    headers = {"Authorization": "Basic %s" % user_and_pass}
    client.post("/bb/zxc/", json=TEST_JSON, headers=headers)
    with connect(**database_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM queue_main")
            query_result = cursor.fetchone()
            assert query_result[0] == 2


def test_add_to_empty_queue_requests(fixture_clean_queue_request, user, user_password):
    creds = f"{user}:{user_password}"
    user_and_pass = b64encode(bytes(creds, encoding="utf8")).decode("ascii")
    headers = {"Authorization": "Basic %s" % user_and_pass}
    client.post("/bb/zxc/", json=TEST_JSON, headers=headers)
    with connect(**database_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM queue_requests")
            query_result = cursor.fetchone()
            assert query_result[0] == 1


def test_add_to_non_empty_queue_requests(user, user_password):
    creds = f"{user}:{user_password}"
    user_and_pass = b64encode(bytes(creds, encoding="utf8")).decode("ascii")
    headers = {"Authorization": "Basic %s" % user_and_pass}
    client.post("/bb/zxc/", json=TEST_JSON, headers=headers)
    with connect(**database_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM queue_requests")
            query_result = cursor.fetchone()
            assert query_result[0] == 2

