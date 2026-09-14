import sys
from pathlib import Path

from fastapi.testclient import TestClient


# Add the repository root to Python's import path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from main import app


client = TestClient(app)


def test_missing_user_returns_404():
    response = client.get("/users/999")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "User not found"
