from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_empty_query_returns_validation_error():
    response = client.post(
        "/api/query",
        json={"query": ""}
    )

    assert response.status_code == 422