from main import app

from fastapi.testclient import TestClient

client = TestClient(app)


def test_statistics():
    response = client.get("queue/info?status=new")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "uuid": "354da90c-ea76-49e8-b83e-45673473c757", "endpoint": "/endpoint/", "initiator_login": "qwe",
         "timestamp": "2021-11-18T14:28:23.516859", "status": "new", "priority": 0, "work_count": 0, "domain": "sigma"},
        {"id": 2, "uuid": "52f51202-b744-4353-bcff-28afae1ac619", "endpoint": "/endpoint/", "initiator_login": "qwe",
         "timestamp": "2021-11-18T14:42:36.873475", "status": "new", "priority": 0, "work_count": 0, "domain": "sigma"}]
