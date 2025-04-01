from fastapi.testclient import TestClient

from data_hub_metrics_api.main import create_app


def test_read_main():
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
