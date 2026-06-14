# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_health_returns_document_count() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["document_count"] >= 8


def test_ask_returns_grounded_answer_with_sources() -> None:
    response = client.post("/ask", json={"question": "How do I read a CSV file in Python?"})

    assert response.status_code == 200
    body = response.json()
    assert body["confidence"] in {"high", "medium"}
    assert "csv" in body["answer"].lower() or "pandas" in body["answer"].lower()
    assert len(body["sources"]) >= 1


def test_ask_handles_low_confidence_questions() -> None:
    response = client.post("/ask", json={"question": "How do I tune a guitar?"})

    assert response.status_code == 200
    body = response.json()
    assert body["confidence"] == "low"
    assert body["sources"] == []
    assert body["limitations"]


def test_ask_validates_short_question() -> None:
    response = client.post("/ask", json={"question": "py"})

    assert response.status_code == 422
