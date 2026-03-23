from fastapi.testclient import TestClient

from discord_commit_tracker.server import app


def test_health_returns_200():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
