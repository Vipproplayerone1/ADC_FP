from app.schemas import Source
from app.services.llm_service import OpenAIClient
from app.services.prompt_loader import load_prompt
from app.services.retrieval_service import format_context, retrieve
from app.services.vector_store import Hit


def _sources_from_hits(hits: list[Hit]) -> list[Source]:
    seen: set[tuple[str, int]] = set()
    out: list[Source] = []
    for h in hits:
        key = (h.file_name, h.page_number)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            Source(file_name=h.file_name, page=h.page_number, chunk_id=h.chunk_id)
        )
    return out


def answer_question(query: str, top_k: int | None = None) -> tuple[str, list[Source]]:
    hits = retrieve(query, top_k)
    template = load_prompt("qa_prompt")
    prompt = template.format(
        retrieved_context=format_context(hits),
        user_question=query,
    )
    answer = OpenAIClient.complete(prompt).strip()
    return answer, _sources_from_hits(hits)


def summarize(query: str, top_k: int | None = None) -> tuple[str, list[Source]]:
    hits = retrieve(query, top_k)
    template = load_prompt("summary_prompt")
    prompt = template.format(
        retrieved_context=format_context(hits),
        user_question=query,
    )
    summary = OpenAIClient.complete(prompt, temperature=0.3).strip()
    return summary, _sources_from_hits(hits)
