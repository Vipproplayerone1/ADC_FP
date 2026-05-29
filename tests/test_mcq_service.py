import json
from unittest.mock import patch

from app.services.embedding_service import Embedder
from app.services.mcq_service import generate_mcqs
from app.services.text_chunker import Chunk
from app.services.vector_store import ChromaStore


def _seed_store() -> None:
    chunks = [
        Chunk(
            chunk_id="L_p1_c0",
            text="Gradient descent minimizes a loss function by stepping opposite the gradient.",
            metadata={"file_name": "L.pdf", "page_number": 1, "chunk_id": "L_p1_c0"},
        ),
    ]
    embeddings = Embedder.embed_texts([c.text for c in chunks])
    ChromaStore.add_chunks(chunks, embeddings)


_GOOD_PAYLOAD = json.dumps(
    {
        "questions": [
            {
                "question": "What does gradient descent minimize?",
                "choices": {
                    "A": "Accuracy",
                    "B": "A loss function",
                    "C": "Memory usage",
                    "D": "Vocabulary size",
                },
                "correct_answer": "B",
                "explanation": "It steps opposite the gradient to reduce loss.",
                "source": {"file_name": "L.pdf", "page": 1, "chunk_id": "L_p1_c0"},
            }
        ]
    }
)


def test_parses_valid_json_payload() -> None:
    _seed_store()
    with patch(
        "app.services.mcq_service.OpenAIClient.complete",
        return_value=_GOOD_PAYLOAD,
    ):
        items = generate_mcqs("gradient descent", num_questions=1, difficulty="easy")
    assert len(items) == 1
    assert items[0].correct_answer == "B"
    assert items[0].source.file_name == "L.pdf"


def test_retries_on_bad_json_then_succeeds() -> None:
    _seed_store()
    bad = "not even close to JSON"
    with patch(
        "app.services.mcq_service.OpenAIClient.complete",
        side_effect=[bad, _GOOD_PAYLOAD],
    ) as mocked:
        items = generate_mcqs("gradient descent", num_questions=1, difficulty="easy")
    assert mocked.call_count == 2
    assert len(items) == 1


def test_injects_source_fallback_when_llm_omits_it() -> None:
    _seed_store()
    payload_no_source = json.dumps(
        {
            "questions": [
                {
                    "question": "What does gradient descent minimize?",
                    "choices": {
                        "A": "Accuracy",
                        "B": "A loss function",
                        "C": "Memory usage",
                        "D": "Vocabulary size",
                    },
                    "correct_answer": "B",
                    "explanation": "It steps opposite the gradient.",
                }
            ]
        }
    )
    with patch(
        "app.services.mcq_service.OpenAIClient.complete",
        return_value=payload_no_source,
    ):
        items = generate_mcqs("gradient descent", num_questions=1, difficulty="easy")
    assert items
    assert items[0].source.file_name == "L.pdf"
    assert items[0].source.page == 1
