from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_missing_user_returns_404():
    response = client.get("/users/999")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "User not found"
