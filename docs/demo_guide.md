# Demo Guide

A scripted walkthrough for showing the Personalized Learning Assistant in a 5-minute live demo.

## Pre-demo checklist (do this 10 minutes before)

1. `ollama serve` is running and `llama3.1:8b` is pulled (`ollama pull llama3.1:8b`).
2. Demo PDFs exist: `data/raw/uploaded_pdfs/Lecture_0[2-6]_*.pdf`. If not, run `.venv\Scripts\python.exe scripts\generate_demo_pdfs.py`.
3. Chroma is seeded: `.venv\Scripts\python.exe scripts\ingest_documents.py`. Verify with `.venv\Scripts\python.exe -c "from app.services.vector_store import ChromaStore; print(ChromaStore.count())"` — expect ~41.
4. Backend started: `.venv\Scripts\uvicorn.exe app.main:app --reload`. Hit `http://127.0.0.1:8000/health` to confirm 200.
5. Frontend started: `.venv\Scripts\streamlit.exe run frontend\streamlit_app.py`. Open `http://localhost:8501`.

## Demo flow (5 minutes)

### Minute 1 — set the stage

"Students have lots of lecture PDFs but no time to re-read them. Generic LLMs hallucinate. We built a personalized assistant that grounds answers in the student's own materials."

Show the Streamlit homepage. Point at the three tabs (Q&A, Summary, MCQ). Mention the sidebar settings.

### Minute 2 — ingest a PDF live

Drag-drop **Lecture_03_Gradient_Descent.pdf** into the upload panel. Click *Upload & index*. The response shows `total_chunks` and the file name. Say: "PyMuPDF extracts page-by-page text, the chunker preserves `(file, page, chunk_id)` metadata, MiniLM embeds, Chroma indexes."

### Minute 3 — grounded Q&A

In the Q&A tab, ask: **"What is gradient descent and how does the learning rate affect it?"**

Read the answer aloud. Then expand the **Sources** dropdown. Point out: file name + page numbers. Say: "Citations come from real chunks. The page number is verifiable — let me show you." Switch to the PDF, jump to page 4 or 5, show the text matches.

### Minute 4 — summary + MCQ

Switch to **Summary** tab. Type **"neural networks"**, top-k 8, hit *Generate*. The output is a structured study summary with citations.

Switch to **MCQ** tab. Topic **"gradient descent"**, 3 questions, difficulty *medium*, hit *Generate*. Show: four-choice question, correct answer key, explanation, source. Pick wrong answers on Q1 and Q2, the right one on Q3. Hit *Score quiz*. Show the per-question feedback and the final score.

### Minute 5 — wrap-up

"Backend is FastAPI. Frontend is Streamlit. The LLM is Llama 3.1 8B — a Transformer — running locally via Ollama, no API keys. Retrieval uses ChromaDB with cosine similarity on MiniLM embeddings. Evaluation is in `docs/evaluation_report.md`: 100% Hit@5, 100% MRR on the eval set, ROUGE-L 0.37 against reference answers, full citation coverage on every response."

Optional flourish: open `http://127.0.0.1:8000/docs` to show the Swagger UI auto-generated from Pydantic schemas. "Every endpoint is documented, every request and response is validated."

## Q&A defense one-liners

- "Why ChromaDB?" — persistence and metadata filtering out of the box.
- "Why MiniLM?" — 384-dim, fast on CPU, sufficient recall for lecture-style text.
- "Why Llama via Ollama?" — no API keys, no rate limits, reproducible for graders.
- "How do you prevent hallucination?" — refusal phrase enforced in the prompt; sources always returned.
- "How do you handle bad LLM JSON?" — `mcq_service` retries once with a stricter prompt; invalid items are dropped.
- "What about scanned PDFs?" — current scope is text PDFs; OCR is in Future Improvements.

## If something breaks during the demo

- Backend not reachable: show the Streamlit banner that already explains it, then start it in a new terminal.
- Chroma empty: run `scripts\ingest_documents.py` while explaining the ingestion pipeline.
- Ollama 500: `ollama serve` in another terminal; `ollama list` shows pulled models.
