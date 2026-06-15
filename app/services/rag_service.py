from app.schemas import ChatTurn, Source
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


_HISTORY_TURNS_CAP = 6


def _format_history(history: list[ChatTurn]) -> str:
    labels = {"user": "User", "assistant": "Assistant"}
    return "\n".join(f"{labels[t.role]}: {t.content}" for t in history)


def _rewrite_query(query: str, history: list[ChatTurn]) -> str:
    prompt = load_prompt("rewrite_user").format(
        conversation_history=_format_history(history[-_HISTORY_TURNS_CAP:]),
        latest_question=query,
    )
    rewritten = OpenAIClient.complete(
        prompt, temperature=0.0, system=load_prompt("rewrite_system")
    ).strip()
    # Models often wrap the rewritten query in quotes; they add nothing for retrieval.
    rewritten = rewritten.strip('"\'').strip()
    return rewritten or query


def answer_question(
    query: str,
    top_k: int | None = None,
    history: list[ChatTurn] | None = None,
) -> tuple[str, list[Source], str | None]:
    rewritten = _rewrite_query(query, history) if history else None
    hits = retrieve(rewritten or query, top_k)
    prompt = load_prompt("qa_user").format(
        retrieved_context=format_context(hits),
        user_question=query,
    )
    answer = OpenAIClient.complete(prompt, system=load_prompt("qa_system")).strip()
    return answer, _sources_from_hits(hits), rewritten


def summarize(query: str, top_k: int | None = None) -> tuple[str, list[Source]]:
    hits = retrieve(query, top_k)
    prompt = load_prompt("summary_user").format(
        retrieved_context=format_context(hits),
        user_question=query,
    )
    summary = OpenAIClient.complete(
        prompt, temperature=0.3, system=load_prompt("summary_system")
    ).strip()
    return summary, _sources_from_hits(hits)
