import html

import streamlit as st

from frontend.utils.api_client import APIClient


def _render_score(correct: int, total: int) -> None:
    pct = (100 * correct / total) if total else 0
    st.markdown(
        f"""
        <div class="plr-score">
            <div class="num">{correct} / {total}</div>
            <div class="pct">{pct:.0f}% correct</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _clear_quiz_state() -> None:
    for k in ("mcq_questions", "mcq_answers", "mcq_scored"):
        st.session_state.pop(k, None)
    for k in [k for k in st.session_state.keys() if k.startswith("mcq_pick_")]:
        del st.session_state[k]


def render(api: APIClient) -> None:
    st.markdown(
        """
        <div class="plr-card">
            <div class="plr-card-title">Generate practice MCQs</div>
            <div class="plr-card-body">
                Pick a topic, count, and difficulty. Questions are generated from your uploaded material
                and include an answer key, explanation, and source page.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        topic = st.text_input(
            "Topic",
            placeholder="e.g. gradient descent",
            key="mcq_topic",
        )
    with col2:
        num = st.number_input(
            "How many", min_value=1, max_value=20, value=5, key="mcq_num"
        )
    with col3:
        difficulty = st.selectbox(
            "Difficulty", ["easy", "medium", "hard"], index=1, key="mcq_diff"
        )

    btn_col1, btn_col2, _ = st.columns([1, 1, 4])
    with btn_col1:
        gen_clicked = st.button("Generate", type="primary", disabled=not topic)
    with btn_col2:
        reset_clicked = st.button("Reset quiz")

    if reset_clicked:
        _clear_quiz_state()
        st.rerun()

    if gen_clicked:
        with st.spinner("Generating MCQs..."):
            try:
                resp = api.generate_mcq(topic, int(num), difficulty)
            except Exception as exc:
                st.error(f"MCQ generation failed: {exc}")
                return
        questions = resp.get("questions", [])
        if not questions:
            st.warning("No questions returned. Try a different topic.")
            return
        _clear_quiz_state()
        st.session_state["mcq_questions"] = questions
        st.session_state["mcq_answers"] = {}
        st.session_state["stats_mcq_batches"] += 1

    if "mcq_questions" not in st.session_state:
        return

    questions = st.session_state["mcq_questions"]
    answers = st.session_state.setdefault("mcq_answers", {})
    scored = st.session_state.get("mcq_scored", False)

    for i, q in enumerate(questions):
        st.markdown(
            f"""
            <div class="plr-mcq-card">
                <div style="margin-bottom:10px;">
                    <span class="qnum">Q{i+1}</span>
                    <span style="font-size:15px;font-weight:600;color:#1f2433;">{html.escape(q["question"])}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        choices = q["choices"]
        opts = [f"{k}. {v}" for k, v in choices.items()]
        picked = st.radio(
            f"Your answer for Q{i+1}",
            options=opts,
            index=None,
            key=f"mcq_pick_{i}",
            label_visibility="collapsed",
        )
        if picked is not None:
            answers[i] = picked.split(".")[0]

        src = q["source"]
        st.markdown(
            f'<div class="plr-pills" style="margin-bottom:6px;">'
            f'<span class="plr-pill">&#128196; {html.escape(str(src["file_name"]))} '
            f'&middot; p.{html.escape(str(src["page"]))}</span></div>',
            unsafe_allow_html=True,
        )

        if scored:
            given = answers.get(i)
            expected = q["correct_answer"]
            explanation = html.escape(q.get("explanation", ""))
            if given == expected:
                st.markdown(
                    f'<div class="plr-banner good">&#10003; Correct ({expected}) &mdash; {explanation}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="plr-banner bad">&#10005; Expected {expected}, '
                    f'you picked {given or "&empty;"} &mdash; {explanation}</div>',
                    unsafe_allow_html=True,
                )

    if not scored:
        score_col1, _ = st.columns([1, 4])
        with score_col1:
            if st.button("Score quiz", type="primary"):
                st.session_state["mcq_scored"] = True
                st.rerun()
    else:
        correct = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["correct_answer"])
        _render_score(correct, len(questions))
