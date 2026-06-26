# RAG Workbench

Most teams adopting RAG do it ad hoc — pick a library, build something, ship it. No baseline, no benchmark, no understanding of whether a different configuration would have produced significantly better results. Decisions are made on intuition and the findings don't transfer to the next project.

This workbench exists to fix that. It is a six-phase framework for systematically discovering and optimizing the best RAG pipeline configuration for a given knowledge base. The key idea is simple: **define what good performance looks like before any technical work begins**, establish a measurable baseline, then improve on it in a structured way and show the difference.

The methodology separates exploration (notebooks, fast and disposable) from commitment (structured Python, measurable against a fixed benchmark), and ends with a direct, quantified comparison between the baseline and the optimized pipeline — something you can show to a technical team or a stakeholder.

Built around **Insurellm** — a fictional insurance company with 71 markdown documents covering company info, products, employees, and contracts.

**This repo is a template, not a finished product.** The structure and code are here for you to replicate in your own projects — swap in your own knowledge base, run the phases, and see what configuration works best for your data.

---

## What this demonstrates

| Concept | Where to find it |
|---|---|
| Full RAG pipeline (chunk → embed → retrieve → generate) | `phase3_baseline/implementation/` |
| Multi-provider LLM switching (OpenAI / Anthropic / Gemini) | `phase5_optimized/implementation/answer.py` — `MODEL` + `BASE_URL` |
| Retrieval optimisation: query rewriting + multi-pass + LLM reranking | `phase5_optimized/implementation/answer.py` — `fetch_context()` |
| LLM-based chunking with structured output (Pydantic) | `phase5_optimized/implementation/ingest.py` |
| LLM-as-judge evaluation + retrieval metrics (MRR, nDCG) | `phase3_baseline/implementation/evaluate.py` |
| Prompt engineering: grounding, query rewriting, reranking | `phase5_optimized/implementation/answer.py` |

---

## The Six Phases

| Phase | Type | Output |
|-------|------|--------|
| 1 — Define Benchmark | Human work | `data/tests.jsonl` (150 Q&A pairs, locked) |
| 2 — Explore the Data | Notebook | t-SNE visualizations, chunking insights |
| 3 — Build LangChain MVP | Python + Gradio | Baseline app + benchmark score |
| 4 — Explore Custom Configs | Notebook | Reranking, query rewriting experiments |
| 5 — Build Custom MVP | Python + Gradio | Optimized app + improved benchmark score |
| 6 — Report Results | Written | Comparison document |

---

## Project Structure

```
rag-workbench/
├── knowledge-base/          # 71 markdown documents (source of truth)
│   ├── company/
│   ├── contracts/
│   ├── employees/
│   └── products/
├── data/
│   ├── tests.jsonl          # 150 benchmark Q&A pairs (never modify)
│   └── generate_tests.py   # script to regenerate the benchmark
├── notebooks/
│   ├── phase2_exploration.ipynb
│   └── phase4_exploration.ipynb
├── phase3_baseline/         # LangChain baseline pipeline
│   ├── app.py
│   └── implementation/
│       ├── ingest.py
│       ├── answer.py
│       └── evaluate.py
├── phase5_optimized/        # Custom advanced pipeline
│   ├── app.py
│   └── implementation/
│       ├── ingest.py
│       ├── answer.py
│       └── evaluate.py
├── docs/
│   ├── methodology.md       # six-phase framework guide
│   └── benchmark-generation.md
├── pyproject.toml
└── .env.example
```

---

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — `pip install uv` or see uv docs
- OpenAI API key

---

## Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

---

## Phase 3 — Baseline Pipeline

Uses LangChain with `RecursiveCharacterTextSplitter` (500 chars) and `text-embedding-3-large`.

```bash
# 1. Ingest knowledge base → creates phase3_baseline/vector_db/
uv run python -m phase3_baseline.implementation.ingest

# 2. Launch the chat UI
cd phase3_baseline && uv run python app.py

# 3. Evaluate a single test (0-indexed)
uv run python -m phase3_baseline.implementation.evaluate 0
```

The evaluation framework is what makes the pipeline comparison meaningful — both phases are scored against the same fixed benchmark.

| Metric | What it measures |
|--------|-----------------|
| **MRR** (Mean Reciprocal Rank) | Average rank of first keyword occurrence across retrieved docs |
| **nDCG** (Normalized Discounted Cumulative Gain) | Ranking quality using binary keyword relevance |
| **Keyword Coverage** | % of expected keywords found in top-10 retrieved docs |
| **Accuracy** (1–5) | LLM-as-judge: factual correctness vs reference answer |
| **Completeness** (1–5) | LLM-as-judge: coverage of all aspects of the reference answer |
| **Relevance** (1–5) | LLM-as-judge: how directly the question is answered |

---

## Phase 5 — Optimized Pipeline

Uses LLM-based chunking with headlines + summaries, multi-pass retrieval, and LLM reranking.

```bash
# 1. Ingest knowledge base → creates phase5_optimized/preprocessed_db/
#    (slow — processes each document with an LLM)
uv run python -m phase5_optimized.implementation.ingest

# 2. Launch the chat UI
cd phase5_optimized && uv run python app.py

# 3. Evaluate a single test
uv run python -m phase5_optimized.implementation.evaluate 0
```

---

## Notebooks (Phases 2 & 4)

Run from the **project root**:

```bash
uv run jupyter lab
```

- `notebooks/phase2_exploration.ipynb` — character/token counts, HuggingFace embeddings, t-SNE 2D/3D
- `notebooks/phase4_exploration.ipynb` — LLM chunking, reranking, query rewriting experiments

---

## Further Reading

- [`docs/methodology.md`](docs/methodology.md) — the full six-phase framework: rationale, organisational context, and what success looks like
- [`docs/benchmark-generation.md`](docs/benchmark-generation.md) — how the benchmark was generated and how to adapt it for a new knowledge base
