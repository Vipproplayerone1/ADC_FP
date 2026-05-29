"""Evaluation driver.

Subcommands:
    retrieval  - Precision@K, Recall@K, MRR, Hit@K from retrieval_eval_set.csv
    qa         - ROUGE-L, BLEU, latency from qa_eval_set.csv (calls live LLM)
    summary    - ROUGE-1/2/L, latency from summary_eval_set.csv (calls live LLM)
    mcq        - heuristic MCQ rubric from mcq_eval_set.csv (calls live LLM)
    all        - run all four and write docs/evaluation_report.md

Usage:
    python scripts\\run_evaluation.py retrieval
    python scripts\\run_evaluation.py all
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections.abc import Iterable
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.schemas import MCQItem  # noqa: E402
from app.services.mcq_service import generate_mcqs  # noqa: E402
from app.services.rag_service import answer_question, summarize  # noqa: E402
from app.services.retrieval_service import retrieve  # noqa: E402
from app.utils.logging_utils import get_logger  # noqa: E402

logger = get_logger("eval")

EVAL_DIR = Path("data/evaluation")
REPORT_PATH = Path("docs/evaluation_report.md")


# ---------- Retrieval ---------- #

def _hit_matches(hit_file: str, hit_page: int, expected_file: str, expected_page: int) -> bool:
    return (
        hit_file.strip().lower() == expected_file.strip().lower()
        and int(hit_page) == int(expected_page)
    )


def evaluate_retrieval(top_k: int) -> dict:
    csv_path = EVAL_DIR / "retrieval_eval_set.csv"
    if not csv_path.exists():
        logger.warning("Missing %s; skipping retrieval eval.", csv_path)
        return {}
    df = pd.read_csv(csv_path)
    precisions: list[float] = []
    recalls: list[float] = []
    rrs: list[float] = []
    hits_topk: list[int] = []
    hits_top3: list[int] = []
    latencies: list[float] = []
    for _, row in df.iterrows():
        query = str(row["query"])
        expected_file = str(row["relevant_file"])
        expected_page = int(row["relevant_page"])
        t0 = time.perf_counter()
        results = retrieve(query, top_k)
        latencies.append(time.perf_counter() - t0)
        matches = [_hit_matches(r.file_name, r.page_number, expected_file, expected_page) for r in results]
        n_relevant_in_topk = sum(matches)
        precisions.append(n_relevant_in_topk / max(top_k, 1))
        recalls.append(1.0 if n_relevant_in_topk > 0 else 0.0)
        rr = 0.0
        for i, m in enumerate(matches, start=1):
            if m:
                rr = 1.0 / i
                break
        rrs.append(rr)
        hits_topk.append(1 if n_relevant_in_topk > 0 else 0)
        hits_top3.append(1 if any(matches[:3]) else 0)
    return {
        "n": len(df),
        "top_k": top_k,
        "precision_at_k": _mean(precisions),
        "recall_at_k": _mean(recalls),
        "mrr": _mean(rrs),
        "hit_rate_at_3": _mean(hits_top3),
        "hit_rate_at_k": _mean(hits_topk),
        "avg_retrieval_latency_s": _mean(latencies),
    }


# ---------- Q&A ---------- #

def _rouge_l(reference: str, hypothesis: str) -> float:
    from rouge_score import rouge_scorer

    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    return scorer.score(reference, hypothesis)["rougeL"].fmeasure


def _rouge_all(reference: str, hypothesis: str) -> dict[str, float]:
    from rouge_score import rouge_scorer

    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference, hypothesis)
    return {k: scores[k].fmeasure for k in ("rouge1", "rouge2", "rougeL")}


def _bleu(reference: str, hypothesis: str) -> float:
    from sacrebleu import sentence_bleu

    return sentence_bleu(hypothesis, [reference]).score / 100.0


def _qa_accuracy(reference: str, hypothesis: str) -> int:
    """Token-overlap heuristic: 1 if all key terms from reference appear in hypothesis."""
    if not reference or not hypothesis:
        return 0
    ref_tokens = {t.lower().strip(".,?!:;") for t in reference.split() if len(t) > 3}
    hyp_lower = hypothesis.lower()
    if not ref_tokens:
        return 0
    hits = sum(1 for t in ref_tokens if t in hyp_lower)
    return 1 if hits / len(ref_tokens) >= 0.5 else 0


def evaluate_qa(pace_s: float = 0.0) -> dict:
    csv_path = EVAL_DIR / "qa_eval_set.csv"
    if not csv_path.exists():
        logger.warning("Missing %s; skipping qa eval.", csv_path)
        return {}
    df = pd.read_csv(csv_path)
    rouges: list[float] = []
    bleus: list[float] = []
    accuracies: list[int] = []
    latencies: list[float] = []
    grounded: list[int] = []
    for i, row in df.iterrows():
        if i > 0 and pace_s > 0:
            time.sleep(pace_s)
        query = str(row["query"])
        reference = str(row.get("reference_answer", ""))
        t0 = time.perf_counter()
        try:
            answer, sources = answer_question(query)
        except Exception as exc:
            logger.error("Q&A failed for %r: %s", query, exc)
            continue
        latencies.append(time.perf_counter() - t0)
        if reference:
            rouges.append(_rouge_l(reference, answer))
            bleus.append(_bleu(reference, answer))
            accuracies.append(_qa_accuracy(reference, answer))
        grounded.append(1 if sources else 0)
    return {
        "n": len(df),
        "qa_accuracy": _mean(accuracies),
        "rouge_l": _mean(rouges),
        "bleu": _mean(bleus),
        "grounded_rate": _mean(grounded),
        "avg_e2e_latency_s": _mean(latencies),
    }


# ---------- Summary ---------- #

def evaluate_summary(pace_s: float = 0.0) -> dict:
    csv_path = EVAL_DIR / "summary_eval_set.csv"
    if not csv_path.exists():
        logger.warning("Missing %s; skipping summary eval.", csv_path)
        return {}
    df = pd.read_csv(csv_path)
    rouge1: list[float] = []
    rouge2: list[float] = []
    rougeL: list[float] = []
    latencies: list[float] = []
    grounded: list[int] = []
    for i, row in df.iterrows():
        if i > 0 and pace_s > 0:
            time.sleep(pace_s)
        query = str(row["query"])
        reference = str(row.get("reference_summary", ""))
        t0 = time.perf_counter()
        try:
            summary, sources = summarize(query)
        except Exception as exc:
            logger.error("Summary failed for %r: %s", query, exc)
            continue
        latencies.append(time.perf_counter() - t0)
        if reference:
            scores = _rouge_all(reference, summary)
            rouge1.append(scores["rouge1"])
            rouge2.append(scores["rouge2"])
            rougeL.append(scores["rougeL"])
        grounded.append(1 if sources else 0)
    return {
        "n": len(df),
        "rouge_1": _mean(rouge1),
        "rouge_2": _mean(rouge2),
        "rouge_l": _mean(rougeL),
        "grounded_rate": _mean(grounded),
        "avg_summary_latency_s": _mean(latencies),
    }


# ---------- MCQ ---------- #

def _mcq_score(items: list[MCQItem], topic: str) -> dict:
    if not items:
        return {"count": 0, "relevance": 0.0, "distinct_choices": 0.0, "explanation_len": 0.0, "format_ok": 0.0}
    topic_terms = {t.lower() for t in topic.split() if len(t) > 3}
    relevance: list[float] = []
    distinct: list[float] = []
    explain_lens: list[int] = []
    format_ok: list[int] = []
    for q in items:
        words = {w.lower().strip(".,?!") for w in q.question.split()}
        relevance.append(1.0 if topic_terms.intersection(words) else 0.5)
        choices = [q.choices.A, q.choices.B, q.choices.C, q.choices.D]
        distinct.append(len(set(c.strip().lower() for c in choices)) / 4.0)
        explain_lens.append(len(q.explanation.split()))
        format_ok.append(1 if q.correct_answer in {"A", "B", "C", "D"} else 0)
    return {
        "count": len(items),
        "relevance": _mean(relevance),
        "distinct_choices": _mean(distinct),
        "explanation_len": _mean(explain_lens),
        "format_ok": _mean(format_ok),
    }


def evaluate_mcq(pace_s: float = 0.0) -> dict:
    csv_path = EVAL_DIR / "mcq_eval_set.csv"
    if not csv_path.exists():
        logger.warning("Missing %s; skipping mcq eval.", csv_path)
        return {}
    df = pd.read_csv(csv_path)
    per_row: list[dict] = []
    latencies: list[float] = []
    for i, row in df.iterrows():
        if i > 0 and pace_s > 0:
            time.sleep(pace_s)
        topic = str(row["topic"])
        n = int(row.get("num_questions", 5))
        difficulty = str(row.get("difficulty", "medium"))
        t0 = time.perf_counter()
        try:
            items = generate_mcqs(topic, n, difficulty)  # type: ignore[arg-type]
        except Exception as exc:
            logger.error("MCQ failed for %r: %s", topic, exc)
            continue
        latencies.append(time.perf_counter() - t0)
        per_row.append(_mcq_score(items, topic))
    if not per_row:
        return {"n": 0}
    keys = per_row[0].keys()
    aggregated = {k: _mean([r[k] for r in per_row]) for k in keys}
    aggregated["n"] = len(per_row)
    aggregated["avg_mcq_latency_s"] = _mean(latencies)
    return aggregated


# ---------- helpers ---------- #

def _mean(values: Iterable[float]) -> float:
    seq = list(values)
    return float(statistics.fmean(seq)) if seq else 0.0


def _fmt(d: dict) -> str:
    if not d:
        return "_no data_"
    lines = []
    for k, v in d.items():
        if isinstance(v, float):
            lines.append(f"- **{k}**: {v:.4f}")
        else:
            lines.append(f"- **{k}**: {v}")
    return "\n".join(lines)


def write_report(retrieval: dict, qa: dict, summary: dict, mcq: dict) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    s = get_settings()
    body = f"""# Evaluation Report

Auto-generated by `scripts/run_evaluation.py all` against the CSVs in `data/evaluation/`.

- **LLM backend**: `{s.active_llm_model}` via `{s.active_llm_base_url}` (Ollama)
- **Embedding model**: `{s.embedding_model}`
- **Chunking**: size={s.chunk_size}, overlap={s.chunk_overlap}
- **Retrieval**: top_k={s.top_k}

## Retrieval

Run against `retrieval_eval_set.csv`. Each query has one ground-truth `(file, page)`.

{_fmt(retrieval)}

| Metric | Meaning |
|---|---|
| precision_at_k | Fraction of top-k chunks that are the ground-truth chunk. With one truth per query the ceiling is 1/k. |
| recall_at_k    | Fraction of queries where the ground-truth chunk appears in top-k. |
| mrr            | Mean Reciprocal Rank — 1.0 means the relevant chunk was always retrieved first. |
| hit_rate_at_3  | Fraction of queries with at least one relevant chunk in top-3 (rubric requirement). |
| hit_rate_at_k  | Fraction of queries with at least one relevant chunk in top-k. |
| avg_retrieval_latency_s | Mean wall time for embed + Chroma query. |

## Q&A (generation)

Run against `qa_eval_set.csv` — each row is a `(query, reference_answer)` pair.

{_fmt(qa)}

| Metric | Meaning |
|---|---|
| qa_accuracy        | Fraction of answers covering >=50% of key reference tokens (rubric: correct/relevant answers). |
| rouge_l            | ROUGE-L F1 between generated and reference answers (lexical overlap). |
| bleu               | sacreBLEU score in [0, 1] (n-gram precision against the reference). |
| grounded_rate      | Fraction of answers that returned at least one source citation. |
| avg_e2e_latency_s  | Mean time per `/chat` call (embed + retrieve + LLM). |

## Summary

Run against `summary_eval_set.csv` — each row is a `(query, reference_summary)` pair.

{_fmt(summary)}

| Metric | Meaning |
|---|---|
| rouge_1               | ROUGE-1 F1 (unigram overlap with the reference). |
| rouge_2               | ROUGE-2 F1 (bigram overlap). |
| rouge_l               | ROUGE-L F1 (longest common subsequence). |
| grounded_rate         | Fraction of summaries that returned at least one source citation. |
| avg_summary_latency_s | Mean time per `/summary` call. |

## MCQ Generation

Run against `mcq_eval_set.csv`. The rubric is heuristic — `relevance` checks if the question
contains any topic keyword; `distinct_choices` is 1.0 when all four options are distinct;
`format_ok` is 1.0 when `correct_answer` is one of A–D.

{_fmt(mcq)}

| Metric | Meaning |
|---|---|
| count              | Mean number of questions returned per topic. |
| relevance          | Mean topic-keyword overlap score (1.0 perfect). |
| distinct_choices   | Mean fraction of distinct choice strings per question. |
| explanation_len    | Mean explanation length in words. |
| format_ok          | Fraction of items with a valid A–D `correct_answer`. |
| avg_mcq_latency_s  | Mean time per `/mcq` call. |

> If `n` is less than the row count in the CSV, some rows were dropped — check the run log.

---

**Raw JSON**:

```json
{json.dumps({"retrieval": retrieval, "qa": qa, "summary": summary, "mcq": mcq}, indent=2)}
```
"""
    REPORT_PATH.write_text(body, encoding="utf-8")
    logger.info("Wrote %s", REPORT_PATH)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=["retrieval", "qa", "summary", "mcq", "all"],
        help="Which evaluation to run.",
    )
    parser.add_argument("--top_k", type=int, default=None)
    parser.add_argument(
        "--pace_s",
        type=float,
        default=0.0,
        help="Sleep seconds between LLM calls. Default 0 since Ollama is local and unrated; "
        "set positive (e.g. 13.0) when pointing at a rate-limited cloud LLM.",
    )
    args = parser.parse_args()

    settings = get_settings()
    top_k = args.top_k or settings.top_k

    retrieval: dict = {}
    qa: dict = {}
    summary: dict = {}
    mcq: dict = {}

    if args.command in {"retrieval", "all"}:
        retrieval = evaluate_retrieval(top_k)
        logger.info("Retrieval: %s", retrieval)
    if args.command in {"qa", "all"}:
        qa = evaluate_qa(pace_s=args.pace_s)
        logger.info("Q&A: %s", qa)
    if args.command in {"summary", "all"}:
        summary = evaluate_summary(pace_s=args.pace_s)
        logger.info("Summary: %s", summary)
    if args.command in {"mcq", "all"}:
        if args.command == "all" and args.pace_s > 0:
            logger.info("Pausing %ds before MCQ eval to clear the rate window.", int(args.pace_s * 5))
            time.sleep(args.pace_s * 5)
        mcq = evaluate_mcq(pace_s=args.pace_s)
        logger.info("MCQ: %s", mcq)

    if args.command == "all":
        write_report(retrieval, qa, summary, mcq)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
