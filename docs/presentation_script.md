# Presentation Script (~10 minutes)

A speaker-by-speaker outline matching the slide deck `Personalized_Learning_Assistant_Deck.pptx`.

---

## Slide 1 — Title

"Personalized Learning Assistant — a RAG study tool for any course material. Track 3 of the ADC final project."

## Slide 2 — Problem

Students have ten different lecture PDFs but two days to review. Keyword search can't explain. General LLMs hallucinate because they never read the course. We want grounded, citable answers from the student's own materials — and a way to generate practice questions.

## Slide 3 — Solution overview

Upload PDFs → parse + chunk + embed + index → retrieve top-k for each query → call a Transformer LLM with that context → return an answer plus the exact file and page it came from. Three modes: Q&A, Summary, MCQ.

## Slide 4 — Architecture diagram

Walk through left-to-right: Streamlit UI → FastAPI backend → 4 services (ingestion, retrieval, RAG, MCQ) → ChromaDB persistent store + sentence-transformers embedder + Llama 3.1 8B via Ollama.

## Slide 5 — Document ingestion

PyMuPDF (pypdf fallback) extracts per-page text. Text cleaning collapses whitespace, dehyphenates broken line breaks. RecursiveCharacterTextSplitter at 800 chars with 150 overlap. Every chunk carries `file_name`, `page_number`, `chunk_id`. ~8 chunks per lecture on the demo set.

## Slide 6 — Retrieval

Query is embedded with the **same** MiniLM model (mismatch silently destroys recall). Chroma cosine similarity. Top-5 by default. Default settings are tunable from `.env` without touching code.

## Slide 7 — Generation

Llama 3.1 8B — a Transformer model — via local Ollama exposing OpenAI-compatible chat completions. Same SDK can swap to any cloud provider. JSON mode used for MCQs. Three prompt templates live in `app/prompts/*.txt`, each enforcing the refusal phrase when retrieval is empty.

## Slide 8 — Demo (Q&A)

Live: ask *"What is gradient descent and how does the learning rate affect it?"* Show the answer. Expand sources. Jump to the cited PDF page to prove the citation is real.

## Slide 9 — Demo (Summary + MCQ)

Live: summarize *"neural networks"*. Then generate 3 MCQs on *"gradient descent"*. Show the four choices, explanation, source. Take the quiz interactively, show the score.

## Slide 10 — Evaluation

Report from `docs/evaluation_report.md`:

| Metric | Value |
|---|---|
| Hit@3 | 1.0 |
| Hit@5 | 1.0 |
| MRR | 1.0 |
| QA accuracy | 1.0 |
| ROUGE-L (QA) | 0.37 |
| BLEU (QA) | 0.14 |
| ROUGE-L (summary) | 0.20 |
| Grounded rate | 1.0 across all generation modes |

Explain: high retrieval scores show the index is sharp; ROUGE/BLEU are moderate because the LLM phrases differently from references — semantic correctness is what matters, captured by QA accuracy.

## Slide 11 — Engineering quality

22 pytest tests, isolated Chroma per test, mocked LLM at the API layer. Pydantic at every boundary. Pure services, thin routes. Prompts as files. Single embedding model, cached. Settings via `pydantic-settings` from `.env`.

## Slide 12 — Limitations and future work

Scanned PDFs need OCR. Math notation extraction is imperfect. Hallucination is reduced but not zero — that's why we always return sources. Future: per-user knowledge bases, citation chunk highlighting, multilingual support, learning analytics dashboard.

## Slide 13 — Q&A

Open the floor. Defense one-liners are in `docs/demo_guide.md` §"Q&A defense one-liners".

---

## Timing cheat sheet

- 0:00 – 1:30  Problem + solution overview (slides 1–3)
- 1:30 – 3:30  Architecture, ingestion, retrieval, generation (slides 4–7)
- 3:30 – 6:30  Live demo (slides 8–9)
- 6:30 – 8:30  Evaluation + engineering (slides 10–11)
- 8:30 – 10:00 Limitations + Q&A (slides 12–13)
