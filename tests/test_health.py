from fastapi.testclient import TestClient

from app.main import app


# client = TestClient(app)

def test_health(client):
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_register_invalid_username(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "a",
            "password": "123456",
            "age": 20,
        },
    )

    assert response.status_code == 422
