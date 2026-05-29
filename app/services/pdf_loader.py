from dataclasses import dataclass
from pathlib import Path

from app.utils.logging_utils import get_logger
from app.utils.text_cleaning import clean_text

logger = get_logger(__name__)


@dataclass
class PageRecord:
    file_name: str
    page_number: int
    text: str


def load_pdf_pages(path: Path) -> list[PageRecord]:
    """Extract text from each page of a PDF.

    Prefers PyMuPDF; falls back to pypdf if PyMuPDF cannot open the file.
    """
    path = Path(path)
    pages = _load_with_pymupdf(path)
    if not pages:
        pages = _load_with_pypdf(path)
    if not pages:
        logger.warning("No text extracted from %s", path.name)
    return [p for p in pages if p.text]


def _load_with_pymupdf(path: Path) -> list[PageRecord]:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return []
    try:
        doc = fitz.open(path)
    except Exception as exc:  # corrupt or non-PDF
        logger.warning("PyMuPDF failed on %s: %s", path.name, exc)
        return []
    out: list[PageRecord] = []
    for i, page in enumerate(doc, start=1):
        text = clean_text(page.get_text("text"))
        out.append(PageRecord(file_name=path.name, page_number=i, text=text))
    doc.close()
    return out


def _load_with_pypdf(path: Path) -> list[PageRecord]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return []
    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        logger.error("pypdf failed on %s: %s", path.name, exc)
        return []
    out: list[PageRecord] = []
    for i, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        out.append(PageRecord(file_name=path.name, page_number=i, text=text))
    return out
