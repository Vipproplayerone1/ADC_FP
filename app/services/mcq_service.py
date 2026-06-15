import json
from typing import Literal

from pydantic import ValidationError

from app.schemas import MCQItem, Source
from app.services.llm_service import OpenAIClient
from app.services.prompt_loader import load_prompt
from app.services.retrieval_service import format_context, retrieve
from app.services.vector_store import Hit
from app.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _build_prompt(topic: str, num_questions: int, difficulty: str, hits: list[Hit]) -> str:
    template = load_prompt("mcq_user")
    return template.format(
        num_questions=num_questions,
        topic=topic,
        difficulty=difficulty,
        retrieved_context=format_context(hits),
    )


def _fallback_source(hits: list[Hit]) -> Source | None:
    if not hits:
        return None
    h = hits[0]
    return Source(file_name=h.file_name, page=h.page_number, chunk_id=h.chunk_id)


def _parse_items(raw: str, hits: list[Hit]) -> list[MCQItem]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.warning("MCQ JSON parse failed: %s", exc)
        return []
    items = data.get("questions") if isinstance(data, dict) else None
    if not isinstance(items, list):
        return []
    fallback = _fallback_source(hits)
    parsed: list[MCQItem] = []
    for item in items:
        if isinstance(item, dict) and "source" not in item and fallback is not None:
            item["source"] = fallback.model_dump()
        try:
            parsed.append(MCQItem.model_validate(item))
        except ValidationError as exc:
            logger.warning("Skipping invalid MCQ item: %s", exc)
    return parsed


def generate_mcqs(
    topic: str,
    num_questions: int,
    difficulty: Literal["easy", "medium", "hard"],
    top_k: int | None = None,
) -> list[MCQItem]:
    hits = retrieve(topic, top_k)
    prompt = _build_prompt(topic, num_questions, difficulty, hits)
    system = load_prompt("mcq_system")
    raw = OpenAIClient.complete(prompt, json_mode=True, temperature=0.4, system=system)
    items = _parse_items(raw, hits)
    if items:
        return items[:num_questions]

    # One retry with a stricter suffix if the first response was unparseable.
    logger.info("Retrying MCQ generation with stricter JSON instruction.")
    stricter = prompt + "\n\nReturn ONLY valid JSON. Do not include any prose."
    raw = OpenAIClient.complete(stricter, json_mode=True, temperature=0.2, system=system)
    items = _parse_items(raw, hits)
    return items[:num_questions]
