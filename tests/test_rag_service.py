from unittest.mock import patch

from app.services.embedding_service import Embedder
from app.services.rag_service import answer_question, summarize
from app.services.text_chunker import Chunk
from app.services.vector_store import ChromaStore


def _seed_store() -> None:
    chunks = [
        Chunk(
            chunk_id="L_p1_c0",
            text="Gradient descent minimizes a loss function by stepping opposite the gradient.",
            metadata={"file_name": "L.pdf", "page_number": 1, "chunk_id": "L_p1_c0"},
        ),
        Chunk(
            chunk_id="L_p2_c0",
            text="The sigmoid function maps inputs to a probability between 0 and 1.",
            metadata={"file_name": "L.pdf", "page_number": 2, "chunk_id": "L_p2_c0"},
        ),
    ]
    embeddings = Embedder.embed_texts([c.text for c in chunks])
    ChromaStore.add_chunks(chunks, embeddings)


def test_answer_question_returns_sources_with_file_and_page() -> None:
    _seed_store()
    with patch(
        "app.services.rag_service.OpenAIClient.complete",
        return_value="Gradient descent reduces the loss by following the negative gradient.",
    ):
        answer, sources = answer_question("What is gradient descent?")
    assert "gradient" in answer.lower()
    assert sources
    assert sources[0].file_name == "L.pdf"
    assert isinstance(sources[0].page, int)


def test_summary_returns_sources() -> None:
    _seed_store()
    with patch(
        "app.services.rag_service.OpenAIClient.complete",
        return_value="The lecture covers gradient descent and the sigmoid function.",
    ):
        summary, sources = summarize("optimization and classification")
    assert summary
    assert sources


def test_empty_store_yields_refusal_pathway() -> None:
    captured: dict = {}

    def fake_complete(prompt: str, **kwargs):
        captured["prompt"] = prompt
        return "I could not find enough information in the uploaded documents."

    with patch(
        "app.services.rag_service.OpenAIClient.complete",
        side_effect=fake_complete,
    ):
        answer, sources = answer_question("Anything?")
    assert sources == []
    assert "no relevant context" in captured["prompt"].lower()
    assert "could not find enough information" in answer.lower()
