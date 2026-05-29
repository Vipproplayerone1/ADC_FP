from dataclasses import dataclass, field
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.pdf_loader import PageRecord


@dataclass
class Chunk:
    chunk_id: str
    text: str
    metadata: dict = field(default_factory=dict)


def chunk_pages(
    pages: list[PageRecord],
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    out: list[Chunk] = []
    for page in pages:
        if not page.text.strip():
            continue
        stem = Path(page.file_name).stem
        parts = splitter.split_text(page.text)
        for idx, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            chunk_id = f"{stem}_p{page.page_number}_c{idx}"
            out.append(
                Chunk(
                    chunk_id=chunk_id,
                    text=part,
                    metadata={
                        "file_name": page.file_name,
                        "page_number": page.page_number,
                        "chunk_id": chunk_id,
                    },
                )
            )
    return out
