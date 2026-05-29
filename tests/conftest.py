"""Shared pytest fixtures.

Every test that touches the vector store must run against an isolated Chroma
directory so tests do not bleed into each other (or into the developer's
real index). We achieve that by pointing the singleton settings at a
tmp_path before any service imports the store.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _isolated_chroma(tmp_path, monkeypatch):
    """Point Chroma and uploads at a per-test temp directory."""
    from app import config as config_module

    config_module.get_settings.cache_clear()
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("CHROMA_COLLECTION", "pla_test")

    from app.services import vector_store as vs_module

    vs_module._client.cache_clear()

    yield

    config_module.get_settings.cache_clear()
    vs_module._client.cache_clear()


@pytest.fixture
def tiny_pdf(tmp_path) -> Path:
    """Write a 2-page synthetic PDF and return its path."""
    import fitz  # PyMuPDF

    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_textbox(
        fitz.Rect(72, 72, 540, 720),
        "Page one talks about gradient descent and the learning rate parameter.",
        fontsize=12,
        fontname="helv",
    )
    page2 = doc.new_page()
    page2.insert_textbox(
        fitz.Rect(72, 72, 540, 720),
        "Page two introduces logistic regression and the sigmoid function for binary classification.",
        fontsize=12,
        fontname="helv",
    )
    path = tmp_path / "tiny.pdf"
    doc.save(str(path))
    doc.close()
    return path
