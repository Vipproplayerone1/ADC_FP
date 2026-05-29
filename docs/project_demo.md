# Project Demo Notes

Reference notes for the project demonstration: what to show, what to say, what to have open on screen.

## Setup checklist

- [ ] Ollama running with `llama3.1:8b` pulled
- [ ] FastAPI backend running on :8000
- [ ] Streamlit frontend running on :8501
- [ ] Browser tabs open:
  - http://localhost:8501  (Streamlit UI)
  - http://127.0.0.1:8000/docs  (Swagger)
  - One of the demo PDFs open in a viewer for citation cross-check

## Demo storyline (mirrors `demo_guide.md`)

1. Frame the problem (30s)
2. Upload a fresh PDF live (45s)
3. Ask a Q&A question, verify citation against the PDF (90s)
4. Generate a summary (45s)
5. Generate 3 MCQs and take the quiz interactively (75s)
6. Show evaluation report numbers and the Swagger UI (60s)
7. Q&A defense (remaining time)

## Talking points by feature

### PDF upload
- Accepts multiple files at once.
- Per-file size cap from `.env` (`MAX_UPLOAD_SIZE_MB`).
- Rejects non-PDFs at the API layer.
- Returns `total_chunks` so you can show that ingestion happened.

### Retrieval
- Same embedding model for index + query — the codebase has exactly one `Embedder._model()` singleton.
- Chroma cosine similarity, persisted across restarts.
- Top-k is configurable per-request or via `.env`.

### Q&A
- Prompt template lives in `app/prompts/qa_prompt.txt`.
- Refusal phrase is hard-coded in the prompt; if retrieval is empty, the LLM is instructed to say *"I could not find enough information in the uploaded documents."*
- Sources are deduplicated by `(file, page)` so a chunk hit twice on the same page only cites once.

### Summary
- Re-uses the same retrieve → format_context → LLM flow.
- Lower temperature than chat to keep summaries faithful.

### MCQ
- LLM is called in JSON mode with a strict schema.
- Pydantic validates each item; invalid items are dropped.
- One retry with a stricter instruction if the first response is unparseable.
- If the LLM omits `source`, it's auto-filled from the top retrieved hit.
- Streamlit panel lets the student take the quiz and see a score with per-question feedback.

## Numbers to memorize

- 41 chunks across 5 demo PDFs (~8 per file)
- Hit@3 = Hit@5 = MRR = 1.0 on the eval set
- 22 pytest tests, all green
- 4 API endpoints + 1 health endpoint
- 3 Streamlit tabs

## Common questions

- **Why not OpenAI GPT-4?** Cost, rate limits, reproducibility for graders. Llama 3.1 8B is a Transformer LLM and meets the rubric.
- **Why not FAISS?** Chroma ships persistence + metadata filtering with less ceremony.
- **What about scanned PDFs?** Out of scope. Future work: Tesseract OCR.
- **How is hallucination prevented?** Refusal prompt + always-on citations. Not bulletproof, but auditable.
- **What if the LLM returns malformed JSON for MCQs?** One automatic retry with a stricter instruction; if still bad, invalid items are silently dropped.
- **Why so many tests?** They catch regressions in chunk metadata, source citations, JSON parsing, and the refusal path — the four things the rubric scores.
