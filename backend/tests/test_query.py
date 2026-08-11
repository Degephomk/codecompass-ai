from fastapi.testclient import TestClient

from app.main import app
from app.api import query


client = TestClient(app)


def test_query_repository(monkeypatch):
    def mock_answer_question(
        question: str,
        project_id: str,
        conversation: list[dict[str, str]] | None = None,
    ):
        return {
            "answer": "Authentication is implemented in src/auth.py.",
            "sources": [
                {
                    "file_path": "src/auth.py",
                    "language": "python",
                    "distance": 0.42,
                }
            ],
        }

    monkeypatch.setattr(
        query,
        "answer_question",
        mock_answer_question,
    )

    response = client.post(
        "/query/",
        json={
            "project_id": "test-project",
            "question": "Where is authentication implemented?",
            "conversation": [],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "Authentication is implemented in src/auth.py."
    )

    assert len(data["sources"]) == 1
    assert data["sources"][0]["file_path"] == "src/auth.py"
    assert data["sources"][0]["language"] == "python"
    assert data["sources"][0]["distance"] == 0.42


def test_query_rejects_empty_question():
    response = client.post(
        "/query/",
        json={
            "project_id": "test-project",
            "question": "",
            "conversation": [],
        },
    )

    assert response.status_code == 422


def test_query_rejects_empty_project_id():
    response = client.post(
        "/query/",
        json={
            "project_id": "",
            "question": "Where is authentication implemented?",
            "conversation": [],
        },
    )

    assert response.status_code == 422
