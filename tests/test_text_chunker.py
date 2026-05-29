from app.services.pdf_loader import PageRecord
from app.services.text_chunker import chunk_pages


def _page(text: str, page_number: int = 1, file_name: str = "L01.pdf") -> PageRecord:
    return PageRecord(file_name=file_name, page_number=page_number, text=text)


def test_chunks_carry_required_metadata() -> None:
    pages = [_page("Some content about a topic. " * 100, page_number=3)]
    chunks = chunk_pages(pages, chunk_size=200, chunk_overlap=20)
    assert chunks
    for c in chunks:
        assert c.metadata["file_name"] == "L01.pdf"
        assert c.metadata["page_number"] == 3
        assert c.metadata["chunk_id"] == c.chunk_id
        assert c.chunk_id.startswith("L01_p3_c")


def test_chunk_size_is_respected_within_tolerance() -> None:
    pages = [_page("word " * 1000)]
    chunks = chunk_pages(pages, chunk_size=200, chunk_overlap=20)
    assert chunks
    for c in chunks:
        # RecursiveCharacterTextSplitter can produce slightly under the target
        # but should never exceed it by more than a small overshoot.
        assert len(c.text) <= 220


def test_empty_pages_produce_no_chunks() -> None:
    pages = [_page("   "), _page("")]
    chunks = chunk_pages(pages, chunk_size=200, chunk_overlap=20)
    assert chunks == []
