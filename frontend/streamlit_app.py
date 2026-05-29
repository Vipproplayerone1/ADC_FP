import os
import sys
from pathlib import Path

import streamlit as st

# Allow `python -m streamlit run frontend\streamlit_app.py` from project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from frontend.components import chat_panel, mcq_panel, upload_panel  # noqa: E402
from frontend.utils.api_client import APIClient  # noqa: E402


st.set_page_config(
    page_title="Personalized Learning Assistant",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


GLOBAL_CSS = """
<style>
:root {
    --plr-primary: #6366f1;
    --plr-primary-dark: #4f46e5;
    --plr-violet: #8b5cf6;
    --plr-surface: #ffffff;
    --plr-muted: #f5f6fb;
    --plr-border: #e5e7f0;
    --plr-text: #1f2433;
    --plr-subtle: #6b7280;
    --plr-success: #10b981;
    --plr-danger: #ef4444;
    --plr-shadow: 0 6px 24px rgba(99, 102, 241, 0.08), 0 2px 6px rgba(31, 36, 51, 0.04);
}

/* hide default Streamlit chrome */
#MainMenu {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* tighten the top padding so the hero hugs the top */
.block-container {padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1200px;}

/* hero banner */
.plr-hero {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 55%, #ec4899 110%);
    color: white;
    padding: 28px 32px;
    border-radius: 16px;
    margin-bottom: 18px;
    box-shadow: var(--plr-shadow);
}
.plr-hero h1 {
    color: white;
    margin: 0 0 6px 0;
    font-size: 30px;
    font-weight: 700;
    letter-spacing: -0.01em;
}
.plr-hero p {
    color: rgba(255,255,255,0.92);
    margin: 0;
    font-size: 15px;
}
.plr-hero .plr-hero-badges {
    margin-top: 14px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.plr-hero .plr-hero-badge {
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.28);
    color: white;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    backdrop-filter: blur(6px);
}

/* card */
.plr-card {
    background: var(--plr-surface);
    border: 1px solid var(--plr-border);
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: var(--plr-shadow);
    margin-bottom: 14px;
}
.plr-card-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--plr-subtle);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}
.plr-card-body {
    color: var(--plr-text);
    font-size: 15px;
    line-height: 1.6;
}

/* source pills */
.plr-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
}
.plr-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #eef0ff;
    border: 1px solid #d6d9f7;
    color: var(--plr-primary-dark);
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 500;
}

/* RAG flow visualization */
.plr-flow {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr;
    align-items: center;
    gap: 10px;
    margin-top: 8px;
}
.plr-flow-step {
    background: var(--plr-muted);
    border: 1px solid var(--plr-border);
    border-radius: 12px;
    padding: 12px 14px;
    text-align: center;
}
.plr-flow-step .label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--plr-subtle);
    margin-bottom: 4px;
}
.plr-flow-step .value {
    font-size: 14px;
    color: var(--plr-text);
    font-weight: 600;
}
.plr-flow-arrow {
    color: var(--plr-primary);
    font-weight: 700;
    font-size: 18px;
}

/* status dot in sidebar */
.plr-status {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 10px;
    background: var(--plr-muted);
    border: 1px solid var(--plr-border);
    font-size: 14px;
    font-weight: 500;
}
.plr-status .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--plr-success);
    box-shadow: 0 0 0 3px rgba(16,185,129,0.18);
}
.plr-status.bad .dot {
    background: var(--plr-danger);
    box-shadow: 0 0 0 3px rgba(239,68,68,0.18);
}

/* tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    border-bottom: 1px solid var(--plr-border);
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 18px;
    border-radius: 10px 10px 0 0;
    font-weight: 600;
    color: var(--plr-subtle);
}
.stTabs [aria-selected="true"] {
    color: var(--plr-primary-dark) !important;
    background: var(--plr-muted);
}

/* primary button polish */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--plr-primary) 0%, var(--plr-violet) 100%);
    border: none;
    font-weight: 600;
    box-shadow: 0 4px 14px rgba(99,102,241,0.28);
}
.stButton > button[kind="primary"]:hover {
    filter: brightness(1.05);
}

/* result/answer card */
.plr-answer {
    background: linear-gradient(180deg, #ffffff 0%, #fafbff 100%);
    border: 1px solid var(--plr-border);
    border-left: 4px solid var(--plr-primary);
    border-radius: 12px;
    padding: 16px 18px;
    margin: 8px 0 4px 0;
}

/* mcq question card */
.plr-mcq-card {
    background: var(--plr-surface);
    border: 1px solid var(--plr-border);
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: var(--plr-shadow);
}
.plr-mcq-card .qnum {
    display: inline-block;
    background: var(--plr-primary);
    color: white;
    font-weight: 700;
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 12px;
    margin-right: 8px;
}
.plr-banner {
    padding: 10px 14px;
    border-radius: 10px;
    margin: 8px 0;
    font-size: 14px;
}
.plr-banner.good {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    color: #047857;
}
.plr-banner.bad {
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #b91c1c;
}

/* score card */
.plr-score {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    border-radius: 14px;
    padding: 22px 24px;
    text-align: center;
    margin: 12px 0;
    box-shadow: var(--plr-shadow);
}
.plr-score .num {font-size: 40px; font-weight: 800; line-height: 1;}
.plr-score .pct {font-size: 14px; opacity: 0.9; margin-top: 6px;}

/* metric cards (override Streamlit's metric) */
[data-testid="stMetricValue"] {
    color: var(--plr-primary-dark);
    font-weight: 700;
}
[data-testid="stMetric"] {
    background: var(--plr-surface);
    border: 1px solid var(--plr-border);
    border-radius: 12px;
    padding: 12px 16px;
    box-shadow: 0 2px 8px rgba(31,36,51,0.04);
}

/* chip-style buttons (used for sample questions) */
div[data-testid="column"] .stButton > button:not([kind="primary"]) {
    background: white;
    border: 1px solid var(--plr-border);
    color: var(--plr-text);
    border-radius: 999px;
    padding: 4px 14px;
    font-size: 13px;
    font-weight: 500;
}
div[data-testid="column"] .stButton > button:not([kind="primary"]):hover {
    border-color: var(--plr-primary);
    color: var(--plr-primary-dark);
    background: #f7f8ff;
}
</style>
"""


def _init_stats() -> None:
    st.session_state.setdefault("stats_files", [])
    st.session_state.setdefault("stats_chunks", 0)
    st.session_state.setdefault("stats_questions", 0)
    st.session_state.setdefault("stats_summaries", 0)
    st.session_state.setdefault("stats_mcq_batches", 0)
    st.session_state.setdefault("chat_history", [])


def _render_hero() -> None:
    st.markdown(
        """
        <div class="plr-hero">
            <h1>Personalized Learning Assistant</h1>
            <p>Upload course PDFs &middot; ask grounded questions &middot; get summaries &middot; generate practice MCQs.</p>
            <div class="plr-hero-badges">
                <span class="plr-hero-badge">RAG</span>
                <span class="plr-hero-badge">FastAPI + Streamlit</span>
                <span class="plr-hero-badge">ChromaDB</span>
                <span class="plr-hero-badge">Sentence-Transformers</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_stats_dashboard() -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Files indexed", len(st.session_state["stats_files"]))
    c2.metric("Chunks indexed", st.session_state["stats_chunks"])
    c3.metric("Questions asked", st.session_state["stats_questions"])
    c4.metric("MCQ batches", st.session_state["stats_mcq_batches"])


def _render_sidebar(default_backend: str) -> tuple[str, bool]:
    with st.sidebar:
        st.markdown("### Settings")
        backend = st.text_input(
            "Backend URL",
            value=os.getenv("BACKEND_URL", default_backend),
            label_visibility="visible",
        )

        api = APIClient(backend)
        try:
            api.health()
            ok = True
            st.markdown(
                '<div class="plr-status"><span class="dot"></span>Backend connected</div>',
                unsafe_allow_html=True,
            )
        except Exception as exc:
            ok = False
            st.markdown(
                '<div class="plr-status bad"><span class="dot"></span>Backend offline</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"`{exc}`")

        st.divider()
        st.markdown("### Session")
        if st.button("Clear chat history", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()
        if st.button("Reset all stats", use_container_width=True):
            for k in ("stats_files", "stats_chunks", "stats_questions",
                      "stats_summaries", "stats_mcq_batches", "chat_history",
                      "mcq_questions", "mcq_answers"):
                st.session_state.pop(k, None)
            st.rerun()

        st.divider()
        st.markdown("### Quick start")
        st.caption("Backend (terminal 1)")
        st.code("uvicorn app.main:app --reload", language="bash")
        st.caption("Frontend (terminal 2)")
        st.code("streamlit run frontend\\streamlit_app.py", language="bash")

    return backend, ok


def main() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    _init_stats()
    _render_hero()

    backend, backend_ok = _render_sidebar("http://127.0.0.1:8000")

    _render_stats_dashboard()

    if not backend_ok:
        st.error(
            f"Cannot reach backend at {backend}. Start it with "
            "`uvicorn app.main:app --reload` in another terminal."
        )
        return

    api = APIClient(backend)

    tab_upload, tab_chat, tab_summary, tab_mcq = st.tabs(
        ["Upload", "Q&A", "Summary", "MCQ"]
    )
    with tab_upload:
        upload_panel.render(api)
    with tab_chat:
        chat_panel.render_chat(api)
    with tab_summary:
        chat_panel.render_summary(api)
    with tab_mcq:
        mcq_panel.render(api)


if __name__ == "__main__":
    main()
