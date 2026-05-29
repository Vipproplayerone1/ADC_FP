import html

import streamlit as st

from frontend.utils.api_client import APIClient


CHAT_CHIPS = [
    "Summarize the key concepts",
    "What are the main definitions?",
    "Give me an example from the material",
    "Explain this like I'm new to the topic",
]

SUMMARY_CHIPS = [
    "key concepts",
    "core formulas and rules",
    "important definitions",
    "common pitfalls",
]


def _pills_html(sources: list[dict]) -> str:
    if not sources:
        return '<span style="color:#6b7280;font-size:13px;">No sources cited.</span>'
    pills = []
    for s in sources:
        fname = html.escape(str(s.get("file_name", "?")))
        page = html.escape(str(s.get("page", "?")))
        pills.append(f'<span class="plr-pill">&#128196; {fname} &middot; p.{page}</span>')
    return f'<div class="plr-pills">{"".join(pills)}</div>'


def _render_sources(sources: list[dict]) -> None:
    st.markdown(_pills_html(sources), unsafe_allow_html=True)
    if sources and any(s.get("chunk_id") for s in sources):
        with st.expander(f"Source detail ({len(sources)} chunks)", expanded=False):
            for s in sources:
                st.markdown(
                    f"- **{s.get('file_name','?')}** — page {s.get('page','?')}"
                    + (f" (`{s.get('chunk_id')}`)" if s.get("chunk_id") else "")
                )


def _render_flow(query: str, num_sources: int) -> None:
    q_preview = (query[:48] + "…") if len(query) > 50 else query
    st.markdown(
        f"""
        <div class="plr-flow">
            <div class="plr-flow-step">
                <div class="label">1. Query</div>
                <div class="value">{html.escape(q_preview)}</div>
            </div>
            <div class="plr-flow-arrow">&rarr;</div>
            <div class="plr-flow-step">
                <div class="label">2. Retrieve</div>
                <div class="value">{num_sources} chunks from ChromaDB</div>
            </div>
            <div class="plr-flow-arrow">&rarr;</div>
            <div class="plr-flow-step">
                <div class="label">3. Generate</div>
                <div class="value">LLM answer with citations</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_chips(chips: list[str], key_prefix: str) -> str | None:
    cols = st.columns(len(chips))
    for i, chip in enumerate(chips):
        with cols[i]:
            if st.button(chip, key=f"{key_prefix}_{i}", use_container_width=True):
                return chip
    return None


def _set_state(key: str, value: str) -> None:
    st.session_state[key] = value


def _render_chip_row_into(chips: list[str], target_key: str, key_prefix: str) -> None:
    cols = st.columns(len(chips))
    for i, chip in enumerate(chips):
        with cols[i]:
            st.button(
                chip,
                key=f"{key_prefix}_{i}",
                on_click=_set_state,
                args=(target_key, chip),
                use_container_width=True,
            )


def _handle_chat(api: APIClient, prompt: str) -> None:
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = api.chat(prompt)
            except Exception as exc:
                st.error(f"Chat failed: {exc}")
                return
        answer = resp.get("answer", "")
        sources = resp.get("sources", [])
        st.markdown(
            f'<div class="plr-answer">{html.escape(answer).replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )
        _render_sources(sources)
        with st.expander("How this answer was built", expanded=False):
            _render_flow(prompt, len(sources))
        st.session_state["chat_history"].append(
            {"query": prompt, "answer": answer, "sources": sources}
        )
        st.session_state["stats_questions"] += 1


def render_chat(api: APIClient) -> None:
    st.markdown(
        '<div class="plr-card-title" style="margin-top:6px;">Ask a question</div>',
        unsafe_allow_html=True,
    )
    st.caption("Try a sample prompt or type your own.")
    picked = _render_chips(CHAT_CHIPS, "chat_chip")

    for turn in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.markdown(turn["query"])
        with st.chat_message("assistant"):
            st.markdown(
                f'<div class="plr-answer">{html.escape(turn["answer"]).replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )
            _render_sources(turn["sources"])

    typed = st.chat_input("Ask something about your uploaded PDFs")
    prompt = typed or picked
    if not prompt:
        return
    _handle_chat(api, prompt)


def render_summary(api: APIClient) -> None:
    st.markdown(
        '<div class="plr-card-title" style="margin-top:6px;">Summarize a topic</div>',
        unsafe_allow_html=True,
    )
    st.caption("Pick a sample topic or write your own.")
    _render_chip_row_into(SUMMARY_CHIPS, "summary_query_input", "summary_chip")

    query = st.text_input(
        "What should I summarize?",
        placeholder="e.g. neural networks, overfitting, gradient descent",
        key="summary_query_input",
    )
    top_k = st.slider("Chunks to retrieve", 3, 15, 8, key="summary_top_k")

    if st.button("Generate summary", type="primary", disabled=not query):
        with st.spinner("Summarizing..."):
            try:
                resp = api.summary(query, top_k=top_k)
            except Exception as exc:
                st.error(f"Summary failed: {exc}")
                return
        summary_text = resp.get("summary", "")
        sources = resp.get("sources", [])
        st.markdown(
            f'<div class="plr-answer">{html.escape(summary_text).replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )
        _render_sources(sources)
        st.session_state["stats_summaries"] += 1
