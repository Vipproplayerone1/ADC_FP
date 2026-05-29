from fastapi import APIRouter

from app.schemas import ChatRequest, ChatResponse
from app.services.rag_service import answer_question

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    answer, sources = answer_question(req.query, req.top_k)
    return ChatResponse(answer=answer, sources=sources)
