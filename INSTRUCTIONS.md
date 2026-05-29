# How to Run This Project

A step-by-step guide for getting the **Personalized Learning Assistant** running on a fresh machine. If you only want the one-liner version, see the Quick Start in `README.md`. Use this file when you need every step spelled out, including what to do when something doesn't work.

---

## 1. Prerequisites

Install these once before you start:

| Tool | Version | Where to get it |
|---|---|---|
| **Python** | 3.12 or 3.13 | https://www.python.org/downloads/ — tick "Add Python to PATH" during install |
| **Ollama** | latest | https://ollama.com/download — Windows installer |
| **Git** | any recent | https://git-scm.com/download/win |

Verify each is on your `PATH`:

```powershell
python --version          # should print Python 3.12.x or 3.13.x
ollama --version          # should print an Ollama version
git --version             # should print a git version
```

If any command says "not recognized", reopen PowerShell after installing and try again.

---

## 2. Clone the Repository

```powershell
git clone https://github.com/Vipproplayerone1/ADC_FP.git
cd ADC_FP
```

All commands below assume you are inside the `ADC_FP` folder.

---

## 3. One-Shot Setup

```powershell
.\scripts\setup.ps1
```

This script:

1. Creates a virtual environment at `.venv\` (only if one doesn't already exist).
2. Upgrades `pip` and installs everything in `requirements.txt`.
3. Copies `.env.example` to `.env` if you don't already have one.

It takes a few minutes the first time. When it finishes you should see `Setup complete.` followed by the next-step hints.

> **If `setup.ps1` is blocked by execution policy**, run it once with:
> ```powershell
> powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
> ```

---

## 4. Pull the Language Model

The system uses **Llama 3.1 8B** via Ollama running locally — no API keys are required.

```powershell
ollama pull llama3.1:8b
```

The download is ~4.7 GB. After it finishes, start the Ollama daemon (it usually starts automatically after install; this is just to be sure):

```powershell
ollama serve
```

Leave this window open — Ollama needs to keep running while you use the app. You can confirm it's up with:

```powershell
Invoke-WebRequest http://localhost:11434/api/tags -UseBasicParsing | Select-Object StatusCode
```

A status code of `200` means Ollama is ready.

---

## 5. Generate Demo PDFs and Index Them

The repository ships **without** any sample PDFs (they are excluded by `.gitignore` as runtime data). Generate the demo set and index it into ChromaDB:

```powershell
.venv\Scripts\python.exe scripts\generate_demo_pdfs.py
.venv\Scripts\python.exe scripts\ingest_documents.py
```

You should now have:

- 5–6 PDFs in `data\raw\uploaded_pdfs\`
- A populated ChromaDB store at `vector_db\chroma\`

You can skip this step if you plan to upload your own PDFs through the UI.

---

## 6. Start the Backend

In one PowerShell window:

```powershell
.venv\Scripts\uvicorn.exe app.main:app --reload
```

The backend should start on `http://127.0.0.1:8000`. Open these to confirm it's healthy:

- http://127.0.0.1:8000/health → `{"status":"ok"}`
- http://127.0.0.1:8000/docs → interactive Swagger UI for all four endpoints (`/upload`, `/chat`, `/summary`, `/mcq`)

Leave this window running.

---

## 7. Start the Frontend

In a **second** PowerShell window (don't close the backend one):

```powershell
.venv\Scripts\streamlit.exe run frontend\streamlit_app.py
```

Your browser should open `http://localhost:8501` automatically. If not, navigate there manually.

You'll see the Personalized Learning Assistant UI with three modes: **Q&A**, **Summary**, and **MCQ**.

---

## 8. Try It Out

In the Streamlit UI:

1. **Upload a PDF** in the upload panel (or use the demo PDFs already ingested in Step 5).
2. **Q&A tab** — ask a grounded question, e.g. `What is model evaluation about?` Every answer cites the file and page it came from.
3. **Summary tab** — ask `Summarize gradient descent`. The summary is built only from your uploaded content.
4. **MCQ tab** — request something like `3 medium MCQs about logistic regression`. Each question includes A–D options, the correct answer, an explanation, and a source citation.

---

## 9. Run the Tests (Optional)

```powershell
.venv\Scripts\pytest.exe -q
```

You should see 22 tests passing.

---

## 10. Run the Evaluation (Optional)

The evaluation notebook computes Hit@3, Hit@5, MRR, QA Accuracy, ROUGE-L, BLEU, and MCQ format-correctness against the eval CSVs in `data\evaluation\`:

```powershell
.venv\Scripts\jupyter.exe nbconvert --to notebook --execute notebooks\04_generation_evaluation.ipynb --output 04_generation_evaluation.executed.ipynb
```

This runs the full eval end-to-end (≈11 minutes on a modern laptop). You can also use the CLI runner:

```powershell
.venv\Scripts\python.exe scripts\run_evaluation.py all
# -> writes results to docs\evaluation_report.md
```

---

## 11. Stopping Everything

- **Backend / Frontend**: press `Ctrl + C` in each PowerShell window.
- **Ollama**: close its PowerShell window, or right-click its tray icon → Quit.

Optionally clear the vector database before your next demo:

```powershell
.venv\Scripts\python.exe scripts\clear_vector_db.py
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `python` is not recognized | Reinstall Python and tick **Add Python to PATH**, then reopen PowerShell. |
| `ModuleNotFoundError: No module named 'pydantic_settings'` (or any project module) | The command ran outside the venv. Always use `.venv\Scripts\python.exe ...`, `.venv\Scripts\uvicorn.exe ...`, etc., **not** plain `python` / `uvicorn`. |
| `setup.ps1 cannot be loaded because running scripts is disabled` | Run with `powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1`. |
| `/chat` or `/summary` hangs or returns 500 | Ollama is probably not running. In another window: `ollama serve` and confirm `http://localhost:11434/api/tags` responds. |
| `model 'llama3.1:8b' not found` | Pull the model: `ollama pull llama3.1:8b`. |
| Streamlit shows "Connection error" on the upload panel | The backend is not running on port 8000. Start it: `.venv\Scripts\uvicorn.exe app.main:app --reload`. |
| `ChromaError` or stale results | Reset the store: `.venv\Scripts\python.exe scripts\clear_vector_db.py`, then re-run `ingest_documents.py`. |

---

## Summary of Ports

| Service | URL | Purpose |
|---|---|---|
| FastAPI backend | http://127.0.0.1:8000 | API |
| Swagger docs | http://127.0.0.1:8000/docs | interactive API explorer |
| Streamlit frontend | http://localhost:8501 | user interface |
| Ollama daemon | http://localhost:11434 | local LLM server |

That's it. If you followed steps 1–7 in order, the app is running end-to-end.
