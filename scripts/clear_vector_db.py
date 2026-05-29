"""Reset the Chroma vector store (drops the collection and removes the persistence dir)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.vector_store import ChromaStore  # noqa: E402
from app.utils.logging_utils import get_logger  # noqa: E402

logger = get_logger("clear")


def main() -> int:
    before = ChromaStore.count()
    ChromaStore.reset()
    logger.info("Cleared Chroma store (had %d chunks).", before)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
