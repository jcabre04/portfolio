import pytest
from app import app


@pytest.fixture()
def client():
    return app.test_client()


@pytest.fixture()
def runner():
    return app.test_cli_runner()


def test_request_example(client):
    response = client.get("/index")
    assert "200 OK" == response.status
