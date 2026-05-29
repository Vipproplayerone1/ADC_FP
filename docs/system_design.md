# System Design

## Goal

A Retrieval-Augmented Generation study assistant that lets a student upload course PDFs and ask grounded questions, get summaries, or generate practice MCQs. Designed for Track 3 of the ADC final project.

## High-level architecture

```
[Streamlit UI] ──HTTP──▶ [FastAPI backend]
                              │
                              ├── /upload  ─▶ pdf_loader ─▶ text_chunker ─▶ Embedder ─▶ Chroma
                              ├── /chat    ─▶ retrieval_service ─▶ rag_service ─▶ Ollama (llama3.1:8b)
                              ├── /summary ─▶ retrieval_service ─▶ rag_service ─▶ Ollama
                              └── /mcq     ─▶ retrieval_service ─▶ mcq_service ─▶ Ollama (JSON mode)
```

## Module breakdown

### Backend (FastAPI)

- **`app/main.py`** — application factory. Mounts CORS and four routers. Exposes `/` and `/health`.
- **`app/config.py`** — `pydantic-settings` `Settings` class loaded from `.env`. Single source of truth for chunk size, top-k, paths, model names. Cached with `lru_cache`.
- **`app/schemas.py`** — all request/response Pydantic models. No raw dicts cross the API boundary.
- **`app/api/*`** — thin route handlers (each ≤ 25 LOC). They validate input, delegate to a service, return a response model.

### Services (pure, no FastAPI imports)

- **`pdf_loader.py`** — PyMuPDF primary, pypdf fallback. Returns `PageRecord(file_name, page_number, text)`.
- **`text_chunker.py`** — `RecursiveCharacterTextSplitter`. Carries `file_name`, `page_number`, `chunk_id` in every chunk's metadata. Chunk IDs are stable: `{stem}_p{page}_c{idx}`.
- **`embedding_service.py`** — `sentence-transformers/all-MiniLM-L6-v2`. **Same instance** used for ingestion and queries (a mismatch silently destroys recall). Normalized embeddings, cached singleton.
- **`vector_store.py`** — Chroma `PersistentClient`. Cosine distance. `add_chunks` upserts; `query` returns `Hit(chunk_id, text, file_name, page_number, score)`.
- **`retrieval_service.py`** — `retrieve(query, k)` → list of Hits. `format_context(hits)` builds the LLM context block.
- **`llm_service.py`** — OpenAI Python SDK pointed at the local Ollama OpenAI-compatible endpoint. JSON mode supported.
- **`rag_service.py`** — `answer_question` and `summarize`. Loads the prompt template, formats context + question, calls the LLM, deduplicates sources by `(file, page)`.
- **`mcq_service.py`** — `generate_mcqs`. Calls LLM in JSON mode, validates with Pydantic `MCQItem`, retries once with a stricter instruction if the first response is unparseable. Auto-fills `source` from the top retrieved hit when the LLM omits it.

### Prompts

Three templates in `app/prompts/*.txt`. The Q&A and Summary templates enforce the refusal phrase *"I could not find enough information in the uploaded documents."* when the retrieved context is insufficient. The MCQ template demands JSON output with a strict schema.

### Frontend (Streamlit)

- **`streamlit_app.py`** — page config, sidebar (backend URL, clear chat history), health check, three tabs.
- **`components/upload_panel.py`** — multi-file uploader → `/upload`.
- **`components/chat_panel.py`** — chat-style Q&A with persistent `st.session_state` history, plus a Summary view.
- **`components/mcq_panel.py`** — MCQ generation form with interactive scoring (student picks A–D, gets a score).
- **`utils/api_client.py`** — typed wrapper around `requests`.

## Data flow

### Ingestion

1. Client uploads PDFs to `POST /upload`.
2. Each file is saved under `data/raw/uploaded_pdfs/` with a sanitized filename.
3. PyMuPDF extracts per-page text; `text_cleaning.clean_text` normalizes whitespace and dehyphenates.
4. Text is chunked at 800 chars with 150 overlap.
5. Chunks are embedded and upserted into Chroma with `(file_name, page_number, chunk_id)` metadata.
6. Response reports `status`, `files`, `total_chunks`.

### Q&A

1. Client posts `{"query": ...}` to `POST /chat`.
2. Query is embedded with the same model.
3. Chroma returns top-k Hits.
4. `format_context` builds a `[i] file (page N) chunk_id=...\n<text>` block.
5. Prompt template is filled and sent to Llama 3.1 via Ollama.
6. Response: `{answer, sources}` where sources are deduplicated by `(file, page)`.

### MCQ

1. `POST /mcq` with `{topic, num_questions, difficulty}`.
2. Topic is used as the retrieval query.
3. LLM is called in JSON mode with the strict schema in the prompt.
4. Output is parsed; invalid items are skipped (logged).
5. If 0 items survive validation, retry once with a stricter instruction.
6. Items without an LLM-supplied source are auto-filled from the top retrieved hit.

## Configuration

All tunables read from `.env`:

| Variable | Default | Purpose |
|---|---|---|
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Same model for index + query |
| `OLLAMA_MODEL` | `llama3.1:8b` | Transformer LLM |
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | OpenAI-compatible endpoint |
| `CHUNK_SIZE` | 800 | Character budget per chunk |
| `CHUNK_OVERLAP` | 150 | Sliding overlap |
| `TOP_K` | 5 | Default retrieval depth |
| `MAX_UPLOAD_SIZE_MB` | 50 | Per-file upload cap |

## Testing strategy

22 tests across 6 files cover: PDF parsing, chunk metadata, vector round-trip, RAG happy-path + refusal, MCQ JSON parsing + retry + source fallback, and full HTTP route shapes (with mocked LLM). Each test uses an isolated Chroma directory via the `_isolated_chroma` autouse fixture so tests don't bleed into each other.

## Trade-offs and decisions

- **Chroma over FAISS** — Chroma ships a built-in persistence layer and metadata filtering, simpler than maintaining a FAISS index + sidecar metadata.
- **MiniLM over a larger embedding model** — 384-dim vectors, fast CPU inference, sufficient recall on lecture-style content.
- **Local Llama 3.1 over a cloud API** — no API keys, no rate limits, no per-token cost, and the project remains reproducible for graders.
- **JSON mode for MCQs** — eliminates regex parsing of free-form text.
- **Prompts in `.txt` files** — easy to tune without code changes; loaded once and cached.

## Failure modes and mitigations

| Failure | Mitigation |
|---|---|
| Scanned PDF (no extractable text) | Logged warning, file is skipped, response reflects `partial`/`error` |
| LLM hallucinates | Prompt instructs refusal when context is insufficient; sources are always returned |
| LLM produces bad JSON for MCQ | One automatic retry with a stricter instruction; invalid items dropped |
| Embedding/index model mismatch | Single `Embedder` singleton reads from `settings.embedding_model` |
| Filename injection | `safe_filename()` strips path separators and dangerous characters |
