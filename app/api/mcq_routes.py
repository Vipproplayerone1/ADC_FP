from fastapi import APIRouter

from app.schemas import MCQRequest, MCQResponse
from app.services.mcq_service import generate_mcqs

router = APIRouter(tags=["mcq"])


@router.post("/mcq", response_model=MCQResponse)
def mcq(req: MCQRequest) -> MCQResponse:
    items = generate_mcqs(req.topic, req.num_questions, req.difficulty)
    return MCQResponse(questions=items)
