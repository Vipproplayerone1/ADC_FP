import html

import streamlit as st

from frontend.utils.api_client import APIClient


def _render_result_card(filenames: list[str], total_chunks: int, message: str) -> None:
    files_html = "".join(
        f'<span class="plr-pill">{html.escape(f)}</span>' for f in filenames
    )
    st.markdown(
        f"""
        <div class="plr-card">
            <div class="plr-card-title">Indexed</div>
            <div class="plr-card-body">
                <div style="display:flex; gap:32px; flex-wrap:wrap; margin-bottom:10px;">
                    <div>
                        <div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;">Files</div>
                        <div style="font-size:22px;font-weight:700;color:#4f46e5;">{len(filenames)}</div>
                    </div>
                    <div>
                        <div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;">Chunks</div>
                        <div style="font-size:22px;font-weight:700;color:#4f46e5;">{total_chunks}</div>
                    </div>
                    <div>
                        <div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;">Status</div>
                        <div style="font-size:14px;font-weight:600;color:#10b981;margin-top:4px;">&#10003; {html.escape(message)}</div>
                    </div>
                </div>
                <div class="plr-pills">{files_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render(api: APIClient) -> None:
    st.markdown(
        """
        <div class="plr-card">
            <div class="plr-card-title">Step 1 &middot; Upload course PDFs</div>
            <div class="plr-card-body">
                Files are parsed, chunked, embedded with sentence-transformers, and stored in ChromaDB.
                Page-level metadata is preserved so answers can cite file name + page.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    files = st.file_uploader(
        "Drop one or more PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        key="upload_files",
    )
    col1, _ = st.columns([1, 3])
    with col1:
        clicked = st.button("Upload & index", type="primary", disabled=not files)

    if clicked and files:
        payload = [(f.name, f.read()) for f in files]
        with st.spinner(f"Indexing {len(payload)} file(s)..."):
            try:
                resp = api.upload_pdfs(payload)
            except Exception as exc:
                st.error(f"Upload failed: {exc}")
                return

        names = resp.get("files", [f.name for f in files])
        chunks = int(resp.get("total_chunks", 0))
        message = resp.get("message", "Indexed.")
        for n in names:
            if n not in st.session_state["stats_files"]:
                st.session_state["stats_files"].append(n)
        st.session_state["stats_chunks"] += chunks
        st.session_state["last_upload"] = {
            "files": names,
            "chunks": chunks,
            "message": message,
        }

    last = st.session_state.get("last_upload")
    if last:
        _render_result_card(last["files"], last["chunks"], last["message"])
