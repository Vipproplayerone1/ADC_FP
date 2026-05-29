from fastapi import APIRouter, HTTPException, UploadFile

from app.config import get_settings
from app.schemas import UploadResponse
from app.services.embedding_service import Embedder
from app.services.pdf_loader import load_pdf_pages
from app.services.text_chunker import chunk_pages
from app.services.vector_store import ChromaStore
from app.utils.file_utils import save_bytes
from app.utils.logging_utils import get_logger

router = APIRouter(tags=["upload"])
logger = get_logger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload(files: list[UploadFile]) -> UploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    upload_dir = settings.upload_path

    saved_names: list[str] = []
    total_chunks = 0

    for f in files:
        if not f.filename or not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Not a PDF: {f.filename}")
        content = await f.read()
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"{f.filename} exceeds {settings.max_upload_size_mb} MB.",
            )
        path = save_bytes(content, upload_dir, f.filename)
        logger.info("Saved %s (%d bytes)", path.name, len(content))

        pages = load_pdf_pages(path)
        if not pages:
            logger.warning("No text extracted from %s; skipping.", path.name)
            continue

        chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            continue

        embeddings = Embedder.embed_texts([c.text for c in chunks])
        n = ChromaStore.add_chunks(chunks, embeddings)
        total_chunks += n
        saved_names.append(path.name)
        logger.info("Indexed %s: %d chunks", path.name, n)

    if not saved_names:
        return UploadResponse(
            status="error",
            message="No text could be extracted from the uploaded PDFs.",
            files=[],
            total_chunks=0,
        )

    return UploadResponse(
        status="success",
        message=f"{len(saved_names)} files uploaded and indexed successfully",
        files=saved_names,
        total_chunks=total_chunks,
    )
