from base64 import b64encode
from fastapi.testclient import TestClient
import pytest
import os

from main import app
from core.settings import settings

client = TestClient(app)

TEST_JSON = {"user": "asd"}


@pytest.fixture
def user():
    return settings.fake_users_db[os.environ['old_api_user']]['username']


@pytest.fixture
def user_password():
    return settings.fake_users_db[os.environ['old_api_user']]['password']


@pytest.fixture
def get_token(user, user_password):
    creds = f"{user}:{user_password}"
    user_and_pass = b64encode(bytes(creds, encoding='utf8')).decode("ascii")
    headers = {'Authorization': 'Basic %s' % user_and_pass}
    response = client.post("/token_new/", json=TEST_JSON, headers=headers)
    return response.json()


def test_no_auth():
    response = client.post("/bb/create_project", TEST_JSON)
    assert response.status_code == 401


def test_basic_auth(user, user_password):
    creds = f"{user}:{user_password}"
    user_and_pass = b64encode(bytes(creds, encoding='utf8')).decode("ascii")
    headers = {'Authorization': 'Basic %s' % user_and_pass}
    response = client.post("/bb/create_project", json=TEST_JSON, headers=headers)
    assert response.status_code == 200


def test_basic_incorrect_user():
    creds = f"random_user:random_password"
    user_and_pass = b64encode(bytes(creds, encoding='utf8')).decode("ascii")
    headers = {'Authorization': 'Basic %s' % user_and_pass}
    response = client.post("/bb/create_project", json=TEST_JSON, headers=headers)
    assert response.status_code == 401


def test_basic_no_creds():
    headers = {'Authorization': 'Basic '}
    response = client.post("/bb/create_project", json=TEST_JSON, headers=headers)
    assert response.status_code == 401


def test_get_token(get_token):
    assert get_token.get('access_token') is not None


def test_get_token_incorrect_user():
    creds = f"random_user:random_password"
    user_and_pass = b64encode(bytes(creds, encoding='utf8')).decode("ascii")
    headers = {'Authorization': 'Basic %s' % user_and_pass}
    response = client.post("/token_new/", json=TEST_JSON, headers=headers)
    assert response.status_code == 400


def test_get_token_no_header():
    response = client.post("/token_new/", json=TEST_JSON)
    assert response.status_code == 401


def test_wrong_token_access():
    random_token = 'Bearer: random_token'
    headers = {'Authorization': random_token}
    response = client.post("/api/v3/nexus/info", json=TEST_JSON, headers=headers)
    assert response.status_code == 401
