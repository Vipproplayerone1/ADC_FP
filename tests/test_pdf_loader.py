from pathlib import Path

from app.services.pdf_loader import load_pdf_pages


def test_extracts_text_and_page_metadata(tiny_pdf: Path) -> None:
    pages = load_pdf_pages(tiny_pdf)
    assert len(pages) == 2
    assert pages[0].page_number == 1
    assert pages[1].page_number == 2
    assert "gradient descent" in pages[0].text.lower()
    assert "logistic regression" in pages[1].text.lower()
    for p in pages:
        assert p.file_name == "tiny.pdf"


def test_returns_empty_list_for_missing_file(tmp_path: Path) -> None:
    pages = load_pdf_pages(tmp_path / "does_not_exist.pdf")
    assert pages == []
