from typing import Literal

from pydantic import BaseModel, Field


class Source(BaseModel):
    file_name: str
    page: int
    chunk_id: str | None = None


class UploadResponse(BaseModel):
    status: Literal["success", "partial", "error"]
    message: str
    files: list[str]
    total_chunks: int


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=50)
    history: list[ChatTurn] = []


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    rewritten_query: str | None = None


class SummaryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=50)


class SummaryResponse(BaseModel):
    summary: str
    sources: list[Source]


class MCQChoices(BaseModel):
    A: str
    B: str
    C: str
    D: str


class MCQItem(BaseModel):
    question: str
    choices: MCQChoices
    correct_answer: Literal["A", "B", "C", "D"]
    explanation: str
    source: Source


class MCQRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=200)
    num_questions: int = Field(default=5, ge=1, le=20)
    difficulty: Literal["easy", "medium", "hard"] = "medium"


class MCQResponse(BaseModel):
    questions: list[MCQItem]
