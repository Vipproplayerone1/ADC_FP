Prepare the ENTIRE demo for this project. Read CLAUDE.md and INSTRUCTIONS.md first to understand the context.

GOAL: When you're done, I should only need to open the browser and demo — no more typing commands.

MANDATORY RULES:
- Always use `.venv\Scripts\python.exe`, `.venv\Scripts\uvicorn.exe`, `.venv\Scripts\streamlit.exe`, `.venv\Scripts\pytest.exe`. NEVER use bare `python`/`pip`/`uvicorn`/`streamlit`/`pytest`.
- Working dir: D:\Major\ADC FP (Windows 11, PowerShell).
- Long-running services (ollama, uvicorn, streamlit) MUST run in background via `Start-Process` so they don't block you.
- After every step: verify with a real HTTP call (curl/Invoke-WebRequest). NEVER assume success.
- Auto-fix errors when possible. Only ask me when truly blocked.
- Use TodoWrite to track the 10 steps below.

STEPS:

[1] PRE-FLIGHT CHECK
- Verify .venv\, .env, requirements.txt exist
- `.venv\Scripts\python.exe --version` must be 3.12+
- `ollama --version` must succeed
- If .env is missing, copy from .env.example
- Confirm pydantic-settings, fastapi, streamlit, chromadb, langchain are installed via `.venv\Scripts\pip.exe list`

[2] OLLAMA + MODEL
- Test `http://localhost:11434/api/tags`. If it fails, start ollama in the background:
  `Start-Process -WindowStyle Hidden ollama -ArgumentList "serve"`
- Sleep 3s, retry. If still failing, tell me to open a terminal and run `ollama serve`.
- Check that `llama3.1:8b` appears in the tags list. If missing: `ollama pull llama3.1:8b` (~4.7GB, may take minutes).

[3] RESET + INDEX DATA
- `.venv\Scripts\python.exe scripts\clear_vector_db.py`
- `.venv\Scripts\python.exe scripts\generate_demo_pdfs.py`
- `.venv\Scripts\python.exe scripts\ingest_documents.py`
- Verify: `data\raw\uploaded_pdfs\` contains ≥5 PDFs; `vector_db\chroma\` is non-empty. Report chunk count and file count.

[4] TEST SUITE
- `.venv\Scripts\pytest.exe -q`
- Must pass 22/22. If any fail, print the stack trace and debug.

[5] START BACKEND (BACKGROUND)
- `Start-Process -WindowStyle Hidden .venv\Scripts\uvicorn.exe -ArgumentList "app.main:app","--host","127.0.0.1","--port","8000"`
- Sleep 5s
- `Invoke-WebRequest http://127.0.0.1:8000/health` → must return status 200 with `{"status":"ok"}`
- `Invoke-WebRequest http://127.0.0.1:8000/openapi.json` → verify the 4 endpoints exist: /upload, /chat, /summary, /mcq
- Capture and report the backend PID.

[6] START FRONTEND (BACKGROUND)
- `Start-Process -WindowStyle Hidden .venv\Scripts\streamlit.exe -ArgumentList "run","frontend\streamlit_app.py","--server.headless=true","--server.port=8501"`
- Sleep 5s
- `Invoke-WebRequest http://localhost:8501` → must return status 200
- Capture and report the frontend PID.

[7] SMOKE TEST ALL 4 ENDPOINTS (via Invoke-RestMethod)
- POST /chat with body `{"question":"What is gradient descent?"}` → verify the response includes a `sources` array with `file_name` and `page_number` fields.
- POST /summary with body `{"topic":"model evaluation"}` → verify citations are present.
- POST /mcq with body `{"topic":"logistic regression","num_questions":2,"difficulty":"medium"}` → verify each item has A-D options, correct_answer, explanation, and source.
- POST /chat with body `{"question":"What is the capital of France?"}` → must return the refusal message ("could not find enough information in the uploaded documents").
- If any test fails: inspect uvicorn logs, fix the issue, retry.

[8] PREPARE LIVE-UPLOAD DEMO FILE
- Create `data\demo_live_upload\` if it doesn't exist.
- List PDFs in that folder. If empty, print a clear warning:
  "⚠️ Drop a NEW PDF (not yet indexed) into D:\Major\ADC FP\data\demo_live_upload\ before demo to showcase live upload."

[9] PRINT STATUS REPORT
Format as a markdown table:
| # | Item | Status | Notes |
|---|---|---|---|
| 1 | Ollama + llama3.1:8b | ✅/❌ | |
| 2 | Backend /health (200) | ✅/❌ | PID: xxxx |
| 3 | Frontend :8501 | ✅/❌ | PID: xxxx |
| 4 | Vector DB | ✅ | N chunks / M files |
| 5 | Pytest | ✅ | 22/22 |
| 6 | Smoke test /chat | ✅/❌ | |
| 7 | Smoke test /summary | ✅/❌ | |
| 8 | Smoke test /mcq | ✅/❌ | |
| 9 | Out-of-scope refusal | ✅/❌ | |
| 10 | Live upload PDF ready | ✅/⚠️ | |

Include the PIDs of uvicorn and streamlit so I can `Stop-Process -Id <pid>` after the demo.

[10] 15-MINUTE DEMO SCRIPT
Print a markdown demo script with these sections:
- **Opening (30s)**: one-sentence pitch + tech stack (FastAPI + Streamlit + ChromaDB + Llama 3.1 8B via Ollama, fully local).
- **Part 1 — Architecture (2 min)**: open /docs, walk through the 4 endpoints, emphasize "pure services + Pydantic schemas + prompts in template files".
- **Part 2 — Live Upload (2 min)**: upload a file from `data\demo_live_upload\`, show the backend logs revealing the parse → chunk → embed → index pipeline.
- **Part 3 — Q&A (4 min)**: 3 concrete questions grounded in the indexed PDFs:
    * In-document question (with expected file/page citation)
    * Multi-chunk synthesis question
    * Out-of-scope question → refusal demonstration
- **Part 4 — Summary (2 min)**: one concrete summary prompt with expected behavior.
- **Part 5 — MCQ (3 min)**: one concrete MCQ prompt, emphasize "answer key + explanation + source" per Track 3 rubric.
- **Part 6 — Evaluation (2 min)**: open `docs\evaluation_report.md`, walk through Hit@K, MRR, ROUGE-L, BLEU, MCQ format-correctness, latency.
- **Closing (30s)**: pytest 22/22 + GitHub repo link.

Use the ACTUAL content of the indexed PDFs when suggesting questions — don't make up topics. Inspect the demo PDFs first to ground the script.

FINAL OUTPUT — print this exact line in bold:
**✅ DEMO READY — open the browser and start. Backend PID: X, Frontend PID: Y. Streamlit: http://localhost:8501 · Swagger: http://127.0.0.1:8000/docs**

START NOW.