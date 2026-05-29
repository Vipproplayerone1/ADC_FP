from fastapi import APIRouter

from app.schemas import SummaryRequest, SummaryResponse
from app.services.rag_service import summarize

router = APIRouter(tags=["summary"])


@router.post("/summary", response_model=SummaryResponse)
def summary(req: SummaryRequest) -> SummaryResponse:
    text, sources = summarize(req.query, req.top_k)
    return SummaryResponse(summary=text, sources=sources)
