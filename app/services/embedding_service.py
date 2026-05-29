from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    settings = get_settings()
    return SentenceTransformer(settings.embedding_model)


class Embedder:
    """Wraps the configured sentence-transformer model.

    The same instance is used for both ingestion and query embedding.
    Mismatched models silently destroy recall.
    """

    @staticmethod
    def embed_texts(texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = _model().encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return vectors.tolist()

    @staticmethod
    def embed_query(text: str) -> list[float]:
        vector = _model().encode(
            text,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return vector.tolist()
