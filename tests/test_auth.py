from base64 import b64encode
from fastapi.testclient import TestClient
from requests.auth import HTTPBasicAuth
import os

from main import app
from core.settings import config, settings

client = TestClient(app)


TEST_JSON = {"user": "asd"}


def test_no_auth():
    response = client.post("/bb/create_project", TEST_JSON)
    assert response.status_code == 401


def test_basic_auth():
    creds = f"{settings.fake_users_db[os.environ['old_api_user']]['username']}:{settings.fake_users_db[os.environ['old_api_user']]['password']}"
    user_and_pass = b64encode(bytes(creds, encoding='utf8')).decode("ascii")
    headers = {'Authorization': 'Basic %s' % user_and_pass}
    response = client.post("/bb/create_project", json=TEST_JSON, headers=headers)
    assert response.status_code == 200


def test_basic_incorrect_user():
    creds = f"{settings.fake_users_db[os.environ['old_api_user']]['username']}:{settings.fake_users_db['qwe']['password']}"
    user_and_pass = b64encode(bytes(creds, encoding='utf8')).decode("ascii")
    headers = {'Authorization': 'Basic %s' % user_and_pass}
    response = client.post("/bb/create_project", json=TEST_JSON, headers=headers)
    assert response.status_code == 401


def test_basic_no_creds():
    headers = {'Authorization': 'Basic '}
    response = client.post("/bb/create_project", json=TEST_JSON, headers=headers)
    assert response.status_code == 401
