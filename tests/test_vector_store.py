from app.services.embedding_service import Embedder
from app.services.text_chunker import Chunk
from app.services.vector_store import ChromaStore


def test_round_trip_add_and_query() -> None:
    chunks = [
        Chunk(
            chunk_id="L_p1_c0",
            text="Gradient descent updates parameters to minimize the loss.",
            metadata={"file_name": "L.pdf", "page_number": 1, "chunk_id": "L_p1_c0"},
        ),
        Chunk(
            chunk_id="L_p2_c0",
            text="A sigmoid function maps a real number to (0, 1).",
            metadata={"file_name": "L.pdf", "page_number": 2, "chunk_id": "L_p2_c0"},
        ),
    ]
    embeddings = Embedder.embed_texts([c.text for c in chunks])
    n = ChromaStore.add_chunks(chunks, embeddings)
    assert n == 2
    assert ChromaStore.count() == 2

    q = Embedder.embed_query("how does gradient descent work")
    hits = ChromaStore.query(q, top_k=2)
    assert hits
    top = hits[0]
    assert top.file_name == "L.pdf"
    assert top.page_number == 1
    assert "gradient" in top.text.lower()


def test_query_on_empty_store_returns_empty_list() -> None:
    q = Embedder.embed_query("anything")
    assert ChromaStore.query(q, top_k=5) == []
