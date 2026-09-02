from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_create_conversation_invalid_user_id():
    payload = {
        "user_id": "invalid-uuid"
    }

    response = client.post("/api/conversations", json=payload)

    assert response.status_code == 422