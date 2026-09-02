from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_get_nonexistent_insight_returns_404():
    response = client.get(
        "/api/insights/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404