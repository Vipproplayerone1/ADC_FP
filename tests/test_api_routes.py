import json
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert "running" in r.json()["message"].lower()


def test_health_endpoint() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_upload_indexes_a_real_pdf(tiny_pdf: Path) -> None:
    with tiny_pdf.open("rb") as fh:
        r = client.post(
            "/upload",
            files=[("files", ("tiny.pdf", fh, "application/pdf"))],
        )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "success"
    assert "tiny.pdf" in body["files"]
    assert body["total_chunks"] >= 1


def test_upload_rejects_non_pdf(tmp_path: Path) -> None:
    bad = tmp_path / "bad.txt"
    bad.write_text("not a pdf")
    with bad.open("rb") as fh:
        r = client.post(
            "/upload",
            files=[("files", ("bad.txt", fh, "text/plain"))],
        )
    assert r.status_code == 400


def test_chat_returns_correct_shape(tiny_pdf: Path) -> None:
    with tiny_pdf.open("rb") as fh:
        client.post(
            "/upload",
            files=[("files", ("tiny.pdf", fh, "application/pdf"))],
        )
    with patch(
        "app.services.rag_service.OpenAIClient.complete",
        return_value="Gradient descent reduces the loss.",
    ):
        r = client.post("/chat", json={"query": "What is gradient descent?"})
    assert r.status_code == 200
    body = r.json()
    assert "answer" in body and "sources" in body
    assert isinstance(body["sources"], list)


def test_chat_rejects_empty_query() -> None:
    r = client.post("/chat", json={"query": ""})
    assert r.status_code == 422


def test_summary_returns_correct_shape(tiny_pdf: Path) -> None:
    with tiny_pdf.open("rb") as fh:
        client.post(
            "/upload",
            files=[("files", ("tiny.pdf", fh, "application/pdf"))],
        )
    with patch(
        "app.services.rag_service.OpenAIClient.complete",
        return_value="Summary of the gradient descent lecture.",
    ):
        r = client.post("/summary", json={"query": "gradient descent"})
    assert r.status_code == 200
    body = r.json()
    assert "summary" in body and "sources" in body


def test_mcq_returns_correct_shape(tiny_pdf: Path) -> None:
    with tiny_pdf.open("rb") as fh:
        client.post(
            "/upload",
            files=[("files", ("tiny.pdf", fh, "application/pdf"))],
        )
    payload = json.dumps(
        {
            "questions": [
                {
                    "question": "What does gradient descent minimize?",
                    "choices": {
                        "A": "Accuracy",
                        "B": "A loss function",
                        "C": "RAM",
                        "D": "Vocabulary",
                    },
                    "correct_answer": "B",
                    "explanation": "It steps opposite the gradient.",
                    "source": {"file_name": "tiny.pdf", "page": 1, "chunk_id": None},
                }
            ]
        }
    )
    with patch(
        "app.services.mcq_service.OpenAIClient.complete",
        return_value=payload,
    ):
        r = client.post(
            "/mcq",
            json={"topic": "gradient descent", "num_questions": 1, "difficulty": "easy"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["questions"]
    q = body["questions"][0]
    assert q["correct_answer"] in {"A", "B", "C", "D"}


def test_mcq_rejects_invalid_difficulty() -> None:
    r = client.post(
        "/mcq",
        json={"topic": "x", "num_questions": 3, "difficulty": "impossible"},
    )
    assert r.status_code == 422
