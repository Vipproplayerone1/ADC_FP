import shutil
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.services.text_chunker import Chunk


@dataclass
class Hit:
    chunk_id: str
    text: str
    file_name: str
    page_number: int
    score: float


@lru_cache(maxsize=1)
def _client() -> chromadb.api.ClientAPI:
    s = get_settings()
    persist_dir = s.chroma_path
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(persist_dir),
        settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
    )


def _collection():
    s = get_settings()
    return _client().get_or_create_collection(
        name=s.chroma_collection,
        metadata={"hnsw:space": "cosine"},
    )


class ChromaStore:
    @staticmethod
    def add_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> int:
        if not chunks:
            return 0
        coll = _collection()
        ids = [c.chunk_id for c in chunks]
        docs = [c.text for c in chunks]
        metas = [c.metadata for c in chunks]
        coll.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metas)
        return len(chunks)

    @staticmethod
    def query(query_embedding: list[float], top_k: int) -> list[Hit]:
        coll = _collection()
        if coll.count() == 0:
            return []
        result = coll.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        dists = result.get("distances", [[]])[0]
        hits: list[Hit] = []
        for chunk_id, doc, meta, dist in zip(ids, docs, metas, dists):
            meta = meta or {}
            hits.append(
                Hit(
                    chunk_id=chunk_id,
                    text=doc or "",
                    file_name=str(meta.get("file_name", "")),
                    page_number=int(meta.get("page_number", 0)),
                    score=float(1.0 - dist),
                )
            )
        return hits

    @staticmethod
    def count() -> int:
        return _collection().count()

    @staticmethod
    def reset() -> None:
        s = get_settings()
        try:
            _client().delete_collection(s.chroma_collection)
        except Exception:
            pass
        _client.cache_clear()
        path: Path = s.chroma_path
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
        path.mkdir(parents=True, exist_ok=True)
