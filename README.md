# Personalized Learning Assistant

A Retrieval-Augmented Generation (RAG) study assistant that lets students upload course PDFs, ask questions about their own materials, request summaries, and automatically generate practice multiple-choice questions (MCQs) with answer keys and source references.

This project is designed for **Track 3: Personalized Learning Assistant**. It focuses on building a real study tool that can work with any uploaded course document set instead of being hardcoded to one fixed textbook or lecture.

---

## Quick Start (Windows / PowerShell)

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

- Backend: http://127.0.0.1:8000  ·  Docs: http://127.0.0.1:8000/docs
- Frontend: http://localhost:8501

Run tests:

```powershell
.venv\Scripts\pytest.exe -q
```

Run the full evaluation:

```powershell
.venv\Scripts\python.exe scripts\run_evaluation.py all
# -> docs\evaluation_report.md
```

See `docs/grading_anchors.md` for the Track 3 rubric ↔ code mapping.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Main Features](#main-features)
4. [Track 3 Requirement Mapping](#track-3-requirement-mapping)
5. [System Architecture](#system-architecture)
6. [RAG Pipeline Workflow](#rag-pipeline-workflow)
7. [Technology Stack](#technology-stack)
8. [Project Structure](#project-structure)
9. [Installation](#installation)
10. [Environment Variables](#environment-variables)
11. [How to Run the Project](#how-to-run-the-project)
12. [How to Use the Application](#how-to-use-the-application)
13. [API Documentation](#api-documentation)
14. [Document Ingestion Pipeline](#document-ingestion-pipeline)
15. [Retrieval-Augmented Generation](#retrieval-augmented-generation)
16. [MCQ Generation Mode](#mcq-generation-mode)
17. [Evaluation Plan](#evaluation-plan)
18. [Testing](#testing)
19. [Example Use Cases](#example-use-cases)
20. [Limitations](#limitations)
21. [Future Improvements](#future-improvements)
22. [Academic Integrity Statement](#academic-integrity-statement)
23. [References](#references)

---

## Project Overview

The **Personalized Learning Assistant** is an AI-powered educational assistant that helps students study from their own course materials. A user can upload lecture slides, textbook chapters, notes, or other PDF documents. The system then parses the PDFs, chunks the text, stores the chunks in a vector database, retrieves relevant information based on the user's question, and generates a contextual response using a Transformer-based language model.

The system supports three major study tasks:

1. **Question Answering**
   - The student asks a question.
   - The system retrieves relevant document chunks.
   - The model answers using only the retrieved context.

2. **Summarization**
   - The student asks for a summary of a topic, chapter, or uploaded document.
   - The system retrieves related chunks and produces a concise study summary.

3. **MCQ Generation**
   - The student asks the system to generate practice questions.
   - The system creates multiple-choice questions from the uploaded material.
   - Each question includes answer choices, the correct answer, and optional explanation.

The main goal is to create a practical study assistant that is useful for real students and can be applied to different subjects such as Machine Learning, Biology, History, Computer Science, Mathematics, or Business.

---

## Problem Statement

Students often have many lecture slides, textbook chapters, and notes but limited time to review them effectively. Traditional keyword search can find exact terms, but it cannot explain concepts, summarize material, or generate practice questions. Large language models can answer questions, but without the student's actual course material, they may provide answers that are too general or may hallucinate information.

This project solves that problem by combining:

- PDF document processing
- Text chunking
- Vector similarity search
- Retrieval-Augmented Generation
- Transformer-based language models
- FastAPI backend deployment
- Streamlit frontend interface

The result is a personalized study assistant that answers questions based on the user's uploaded documents and provides page or section references whenever possible.

---

## Main Features

### 1. PDF Upload

Users can upload multiple PDF files through the Streamlit interface.

Supported examples:

- Lecture slides
- Textbook chapters
- Course notes
- Academic handouts
- Study guides
- Research papers

The system is designed to work with any uploaded document set and is not hardcoded to a specific subject.

---

### 2. Automatic Document Parsing

After upload, the backend extracts text from each PDF file.

The parser stores metadata such as:

- File name
- Page number
- Chunk ID
- Upload timestamp
- Optional subject name
- Optional section title

This metadata is later used to show source references in answers.

---

### 3. Text Chunking

Long documents are divided into smaller chunks so the retrieval system can search them effectively.

Example chunk configuration:

```python
chunk_size = 800
chunk_overlap = 150
```

Chunking helps the system retrieve only the most relevant parts of the document instead of passing the entire PDF to the language model.

---

### 4. Vector Database Indexing

Each text chunk is converted into an embedding vector using a sentence embedding model. The vectors are stored in a vector database such as ChromaDB or FAISS.

Recommended default:

```text
Vector Store: ChromaDB
Embedding Model: sentence-transformers/all-MiniLM-L6-v2
```

Alternative options:

```text
Vector Store: FAISS
Embedding Model: BAAI/bge-small-en-v1.5
Embedding Model: sentence-transformers/all-mpnet-base-v2
```

---

### 5. RAG-Based Question Answering

When the user asks a question, the system follows this process:

1. Convert the user query into an embedding.
2. Search the vector database for similar document chunks.
3. Retrieve the top-k most relevant chunks.
4. Build a prompt using the retrieved chunks.
5. Send the prompt to a Transformer-based language model.
6. Generate a final answer with source references.

---

### 6. Source References

The assistant includes references to the original course material.

Example:

```text
Answer:
Gradient descent is an optimization algorithm used to minimize a loss function by repeatedly updating model parameters in the direction of the negative gradient.

Sources:
- Lecture_03_Optimization.pdf, page 12
- Lecture_03_Optimization.pdf, page 14
```

This improves trust and helps students verify the answer.

---

### 7. Summary Generation

Users can ask for summaries such as:

```text
Summarize Chapter 3.
Summarize the uploaded lecture on neural networks.
Give me the key points from the PDF about gradient descent.
Explain this chapter in simple words.
```

The system retrieves relevant chunks and generates a clear summary.

---

### 8. MCQ Quiz Mode

Users can generate practice questions from their uploaded course content.

Example prompt:

```text
Generate 5 MCQs about gradient descent.
```

Example output:

```text
Question 1:
What is the main purpose of gradient descent?

A. To increase the loss function
B. To minimize the loss function
C. To randomly initialize model weights
D. To remove outliers from data

Correct Answer: B

Explanation:
Gradient descent updates model parameters in the direction that reduces the loss function.
```

---

### 9. Chat History

The Streamlit interface keeps chat history so users can review previous questions and answers during the same session.

---

### 10. FastAPI Backend

The backend serves the main AI functions through API endpoints.

Main backend responsibilities:

- Receive uploaded PDF files
- Parse and chunk documents
- Create and update vector database
- Retrieve relevant context
- Generate answers
- Generate summaries
- Generate MCQs
- Return results to the frontend

---

### 11. Streamlit Frontend

The frontend provides a simple interface for real users.

Main frontend components:

- PDF uploader
- Subject name input
- Chat interface
- Summary button
- MCQ quiz mode
- Source reference display
- Chat history panel

---

## Track 3 Requirement Mapping

| Assignment Requirement | How This Project Meets It |
|---|---|
| Choose one academic subject | The demo can use one subject such as Machine Learning, but the system supports any uploaded document set. |
| Use 5–10 lecture slide PDFs or textbook chapters | The knowledge base is built from 5–10 uploaded PDFs for testing and demonstration. |
| System must work on any uploaded document set | The pipeline dynamically parses, chunks, embeds, and indexes uploaded PDFs. |
| Input: PDF files + natural language query | Users upload PDFs and type questions in the Streamlit chat interface. |
| Document ingestion pipeline | PDFs are parsed, chunked, and indexed into ChromaDB or FAISS. |
| RAG pipeline | LangChain or LlamaIndex retrieves relevant chunks and passes them to the language model. |
| Transformer-based language model | The system uses a GPT-based API model, Mistral, T5, or another Transformer model. |
| Contextual Q&A | The assistant answers questions using retrieved document context. |
| Automatic MCQ generation | The assistant generates MCQs, options, answer keys, and explanations. |
| Expected output includes source references | Answers include file names and page numbers when available. |
| Deployment | FastAPI backend and Streamlit frontend. |
| Rigorous evaluation | Retrieval, QA, generation, MCQ quality, and human evaluation metrics are reported. |

---

## System Architecture

```text
+----------------------+
|     Streamlit UI     |
|----------------------|
| PDF Upload           |
| Chat Interface       |
| Summary Mode         |
| MCQ Quiz Mode        |
+----------+-----------+
           |
           | HTTP Requests
           v
+----------------------+
|    FastAPI Backend   |
|----------------------|
| Upload Endpoint      |
| Query Endpoint       |
| Summary Endpoint     |
| MCQ Endpoint         |
+----------+-----------+
           |
           v
+----------------------+
| Document Processing  |
|----------------------|
| PDF Text Extraction  |
| Text Cleaning        |
| Chunking             |
| Metadata Storage     |
+----------+-----------+
           |
           v
+----------------------+
| Embedding Layer      |
|----------------------|
| Sentence Transformer |
| Query Embedding      |
| Document Embedding   |
+----------+-----------+
           |
           v
+----------------------+
| Vector Store         |
|----------------------|
| ChromaDB / FAISS     |
| Similarity Search    |
| Top-k Retrieval      |
+----------+-----------+
           |
           v
+----------------------+
| Language Model       |
|----------------------|
| GPT / Mistral / T5   |
| Answer Generation    |
| Summary Generation   |
| MCQ Generation       |
+----------+-----------+
           |
           v
+----------------------+
| Final Response       |
|----------------------|
| Answer               |
| Source References    |
| MCQs + Answer Keys   |
+----------------------+
```

---

## RAG Pipeline Workflow

```text
Step 1: User uploads PDFs
        |
        v
Step 2: Backend extracts text from each page
        |
        v
Step 3: Text is cleaned and split into overlapping chunks
        |
        v
Step 4: Each chunk is converted into an embedding vector
        |
        v
Step 5: Embeddings are stored in ChromaDB or FAISS
        |
        v
Step 6: User asks a question
        |
        v
Step 7: Query is embedded using the same embedding model
        |
        v
Step 8: Vector store retrieves top-k relevant chunks
        |
        v
Step 9: Retrieved chunks are inserted into the prompt
        |
        v
Step 10: Transformer-based LLM generates the answer
        |
        v
Step 11: System returns answer with source references
```

---

## Technology Stack

### Backend

| Tool | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | Backend API deployment |
| Uvicorn | ASGI server for FastAPI |
| Pydantic | Request and response validation |
| PyMuPDF / pypdf | PDF text extraction |
| LangChain or LlamaIndex | RAG orchestration |
| ChromaDB or FAISS | Vector database |
| Sentence Transformers | Text embeddings |
| OpenAI API / Mistral / T5 | Transformer-based language model |

---

### Frontend

| Tool | Purpose |
|---|---|
| Streamlit | Web interface |
| Streamlit file uploader | PDF upload |
| Streamlit chat components | Chat interface |
| Pandas | Displaying MCQ tables and evaluation results |
| Requests | Calling FastAPI endpoints |

---

### Evaluation

| Tool | Purpose |
|---|---|
| scikit-learn | Retrieval and evaluation metrics |
| rouge-score | ROUGE evaluation for summaries |
| nltk / sacrebleu | BLEU score |
| pandas | Result tables |
| matplotlib | Evaluation plots |

---

## Project Structure

```text
personalized-learning-assistant/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── upload_routes.py
│   │   ├── chat_routes.py
│   │   ├── summary_routes.py
│   │   └── mcq_routes.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py
│   │   ├── text_chunker.py
│   │   ├── embedding_service.py
│   │   ├── vector_store.py
│   │   ├── retrieval_service.py
│   │   ├── llm_service.py
│   │   ├── rag_service.py
│   │   └── mcq_service.py
│   │
│   ├── prompts/
│   │   ├── qa_prompt.txt
│   │   ├── summary_prompt.txt
│   │   └── mcq_prompt.txt
│   │
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py
│       ├── logging_utils.py
│       └── text_cleaning.py
│
├── frontend/
│   ├── streamlit_app.py
│   ├── components/
│   │   ├── upload_panel.py
│   │   ├── chat_panel.py
│   │   └── mcq_panel.py
│   └── utils/
│       └── api_client.py
│
├── data/
│   ├── raw/uploaded_pdfs/
│   ├── processed/chunks/
│   └── evaluation/
│       ├── qa_eval_set.csv
│       ├── retrieval_eval_set.csv
│       ├── summary_eval_set.csv
│       └── mcq_eval_set.csv
│
├── vector_db/chroma/
│
├── notebooks/
│   ├── 01_pdf_parsing_experiment.ipynb
│   ├── 02_chunking_experiment.ipynb
│   ├── 03_retrieval_evaluation.ipynb
│   └── 04_generation_evaluation.ipynb
│
├── tests/
│   ├── test_pdf_loader.py
│   ├── test_text_chunker.py
│   ├── test_vector_store.py
│   ├── test_rag_service.py
│   ├── test_mcq_service.py
│   └── test_api_routes.py
│
├── scripts/
│   ├── ingest_documents.py
│   ├── run_evaluation.py
│   ├── clear_vector_db.py
│   ├── generate_demo_pdfs.py
│   └── setup.ps1
│
└── docs/
    ├── system_design.md
    ├── evaluation_report.md
    ├── grading_anchors.md
    ├── demo_guide.md
    ├── project_demo.md
    └── presentation_script.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Vipproplayerone1/ADC_FP.git
cd ADC_FP
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Install and Start Ollama

```powershell
# https://ollama.com/download
ollama pull llama3.1:8b
ollama serve
```

---

## Environment Variables

Create a `.env` file in the project root (copy from `.env.example`).

---

## How to Run the Project

### 1. Start the FastAPI Backend

```powershell
.venv\Scripts\uvicorn.exe app.main:app --reload
```

Backend URL: `http://127.0.0.1:8000`
API docs: `http://127.0.0.1:8000/docs`

### 2. Start the Streamlit Frontend

```powershell
.venv\Scripts\streamlit.exe run frontend\streamlit_app.py
```

Streamlit URL: `http://localhost:8501`

### 3. Optional: Ingest Documents from Command Line

```powershell
.venv\Scripts\python.exe scripts\generate_demo_pdfs.py
.venv\Scripts\python.exe scripts\ingest_documents.py --input_dir data\raw\uploaded_pdfs
```

### 4. Optional: Clear Vector Database

```powershell
.venv\Scripts\python.exe scripts\clear_vector_db.py
```

---

## How to Use the Application

1. **Upload Course PDFs** — drag-and-drop in the Streamlit upload panel.
2. **Wait for processing** — the backend parses, chunks, embeds, and indexes the PDFs.
3. **Ask Questions** in the Q&A tab.
4. **Review Source References** — each answer cites file name and page number.
5. **Generate Summaries** in the Summary tab.
6. **Generate MCQs** in the MCQ tab.

---

## API Documentation

### Health Check

```http
GET /
```

### Upload PDFs

```http
POST /upload
```

multipart/form-data with one or more PDF files in the `files` field.

### Ask a Question

```http
POST /chat
Content-Type: application/json

{"query": "What is gradient descent?", "top_k": 5}
```

### Generate Summary

```http
POST /summary
Content-Type: application/json

{"query": "Summarize logistic regression", "top_k": 8}
```

### Generate MCQs

```http
POST /mcq
Content-Type: application/json

{"topic": "gradient descent", "num_questions": 5, "difficulty": "medium"}
```

See `http://127.0.0.1:8000/docs` for the live Swagger UI.

---

## Document Ingestion Pipeline

1. **PDF Loading** — PyMuPDF (with pypdf fallback).
2. **Text Extraction** — page-by-page with `(file_name, page_number, text)` metadata.
3. **Text Cleaning** — collapse whitespace, dehyphenate line breaks, drop bare page-number lines.
4. **Chunking** — `RecursiveCharacterTextSplitter`, `chunk_size=800`, `chunk_overlap=150`.
5. **Embedding** — `sentence-transformers/all-MiniLM-L6-v2`, same model for index and query.
6. **Vector Indexing** — ChromaDB persistent client with cosine similarity.

Every chunk carries `file_name`, `page_number`, and `chunk_id` in its metadata for downstream citations.

---

## Retrieval-Augmented Generation

### Prompt Templates

All prompt templates live in `app/prompts/*.txt`. The Q&A prompt enforces a refusal phrase when the retrieved context does not answer the question, blocking hallucinations.

---

## MCQ Generation Mode

`POST /mcq` accepts a topic, number of questions, and difficulty (easy / medium / hard). The MCQ service retrieves topic-relevant chunks, calls the LLM in JSON mode, validates the response against the Pydantic `MCQItem` schema, and retries once with a stricter instruction if the first response cannot be parsed.

Each item includes: `question`, `choices.A/B/C/D`, `correct_answer`, `explanation`, and `source`.

---

## Evaluation Plan

### Dataset Split

| Split | Purpose | Rows in CSV |
|---|---|---|
| Train (Dev) | Prompt tuning, chunk-size tuning | rows where `split == "train"` |
| Validation | Choose top-k, chunk size, overlap, embedding model | rows where `split == "val"` |
| Test | Final unbiased numbers reported in `docs/evaluation_report.md` | rows where `split == "test"` |

Eval CSVs live in `data/evaluation/`.

### Retrieval Metrics

- **Precision@K**
- **Recall@K**
- **MRR (Mean Reciprocal Rank)**
- **Hit Rate @3 and @5** (rubric requirement)

### Q&A Metrics

- **QA Accuracy** — fraction of answers covering ≥50% of key reference tokens.
- **ROUGE-L F1** — lexical overlap with the reference answer.
- **BLEU** — n-gram precision.
- **Grounded rate** — fraction of answers with at least one citation.

### Summary Metrics

- **ROUGE-1 / ROUGE-2 / ROUGE-L F1**
- **Grounded rate**

### MCQ Metrics

- **Relevance** — topic-keyword overlap.
- **Distinct choices** — A/B/C/D uniqueness.
- **Format ok** — `correct_answer` in {A, B, C, D}.
- **Explanation length** — sanity check.

### System Performance

- **avg_retrieval_latency_s** — embed + Chroma query.
- **avg_e2e_latency_s** — full Q&A round-trip.
- **avg_summary_latency_s**, **avg_mcq_latency_s** — generation latencies.

---

## Testing

```powershell
.venv\Scripts\pytest.exe -q
```

Six test files cover the pipeline end-to-end with mocked LLM where appropriate. See `docs/grading_anchors.md` §Test Coverage for the matrix.

---

## Example Use Cases

- "What is overfitting?"
- "Summarize the lecture about logistic regression."
- "Generate 5 easy MCQs about supervised learning."
- "Where does the lecture explain train-test split?"

---

## Limitations

1. Scanned PDFs need OCR.
2. Math notation extraction is imperfect.
3. Hallucination risk is reduced but not eliminated.
4. The context window limits how much retrieved text the LLM sees.
5. Source accuracy depends on the PDF parser's page-level fidelity.
6. MCQs should be reviewed by an instructor before exam use.

---

## Future Improvements

OCR support, table/formula extraction, user accounts, in-app quiz scoring, spaced repetition, multi-course KBs, citation chunk highlighting, multilingual support, learning analytics dashboard.

---

## Academic Integrity Statement

This is a study-support tool. It should help students understand course materials, review concepts, and practice questions. It is not a substitute for original work on assessments.

---

## References

FastAPI, Streamlit, LangChain, ChromaDB, Sentence Transformers, Llama 3.1 via Ollama, PyMuPDF, pypdf, rouge-score, sacreBLEU.
