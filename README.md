# Personalized Learning Assistant

Quick-start. The full product spec is in [`README_track3.md`](./README_track3.md).

## What it does

Upload course PDFs → ask grounded questions, get summaries, or generate practice MCQs. RAG with ChromaDB + Llama 3.1 (Ollama). FastAPI backend, Streamlit frontend.

## Quick start (Windows / PowerShell)

```powershell
# 1. Setup (creates .venv, installs requirements, copies .env)
.\scripts\setup.ps1

# 2. Pull the LLM
ollama pull llama3.1:8b

# 3. Generate demo PDFs and index them
.venv\Scripts\python.exe scripts\generate_demo_pdfs.py
.venv\Scripts\python.exe scripts\ingest_documents.py

# 4. Run backend
.venv\Scripts\uvicorn.exe app.main:app --reload

# 5. Run frontend (separate terminal)
.venv\Scripts\streamlit.exe run frontend\streamlit_app.py
```

- Backend: http://127.0.0.1:8000  · Docs: http://127.0.0.1:8000/docs
- Frontend: http://localhost:8501

## Tests

```powershell
.venv\Scripts\pytest.exe -q
```

## Evaluation

```powershell
.venv\Scripts\python.exe scripts\run_evaluation.py all
# -> docs\evaluation_report.md
```

## Project layout

- `app/` — FastAPI backend (routes, services, schemas, prompts)
- `frontend/` — Streamlit UI
- `scripts/` — ingestion, demo PDFs, evaluation, DB reset, setup
- `tests/` — pytest suite
- `data/evaluation/` — retrieval / QA / summary / MCQ CSVs
- `docs/` — system design, evaluation report, grading anchors, demo guide, presentation
- `notebooks/` — experiment notebooks

See `docs/grading_anchors.md` for the Track 3 rubric ↔ code mapping.
