"""Ingest all PDFs from an input directory into the Chroma vector store.

Usage:
    python scripts\\ingest_documents.py --input_dir data\\raw\\uploaded_pdfs
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.services.embedding_service import Embedder  # noqa: E402
from app.services.pdf_loader import load_pdf_pages  # noqa: E402
from app.services.text_chunker import chunk_pages  # noqa: E402
from app.services.vector_store import ChromaStore  # noqa: E402
from app.utils.logging_utils import get_logger  # noqa: E402

logger = get_logger("ingest")


def ingest(input_dir: Path) -> int:
    settings = get_settings()
    pdfs = sorted(input_dir.glob("*.pdf"))
    if not pdfs:
        logger.warning("No PDFs found in %s", input_dir)
        return 0

    total = 0
    for pdf in pdfs:
        pages = load_pdf_pages(pdf)
        if not pages:
            logger.warning("Skipping %s — no text extracted.", pdf.name)
            continue
        chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            logger.warning("Skipping %s — no chunks produced.", pdf.name)
            continue
        embeddings = Embedder.embed_texts([c.text for c in chunks])
        n = ChromaStore.add_chunks(chunks, embeddings)
        total += n
        logger.info("Indexed %s: %d chunks", pdf.name, n)

    logger.info("Total chunks now in store: %d", ChromaStore.count())
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input_dir",
        type=Path,
        default=Path("data/raw/uploaded_pdfs"),
        help="Directory containing PDFs to ingest.",
    )
    args = parser.parse_args()
    ingest(args.input_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
