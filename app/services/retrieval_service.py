from app.config import get_settings
from app.services.embedding_service import Embedder
from app.services.vector_store import ChromaStore, Hit


def retrieve(query: str, top_k: int | None = None) -> list[Hit]:
    settings = get_settings()
    k = top_k or settings.top_k
    vector = Embedder.embed_query(query)
    return ChromaStore.query(vector, k)


def format_context(hits: list[Hit]) -> str:
    if not hits:
        return "(no relevant context found in the uploaded documents)"
    blocks: list[str] = []
    for i, h in enumerate(hits, start=1):
        blocks.append(
            f"[{i}] {h.file_name} (page {h.page_number}) chunk_id={h.chunk_id}\n{h.text}"
        )
    return "\n\n".join(blocks)
