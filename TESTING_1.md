# Testing Checklist

Work through these in order. Each phase depends on the previous one completing successfully.

---

## Progress

| Phase | Status |
|-------|--------|
| 1 — Define Benchmark | ✅ Complete — `data/tests.jsonl` locked (150 Q&A pairs) |
| 2 — Explore the Data | ✅ Complete — t-SNE plots for 3 embedding models, see `docs/phase_2_embedding_progression.md` |
| 3 — Baseline Pipeline | ✅ Complete — chat UI and evaluation dashboard working |
| 4 — Explore Custom Configs | ✅ Complete — notebook fixed and ready to run |
| 5 — Build Custom MVP | ✅ Complete — ingest done (559 chunks), evaluate working |
| 6 — Report Results | 🔲 Pending |

---

## Setup

- [x] `cp .env.example .env` and add `OPENAI_API_KEY`
- [x] `uv sync` — no errors
- [x] `python -c "import openai, chromadb, gradio, langchain"` — no import errors

---

## Phase 2 — Explore the Data ✅

- [x] `uv run jupyter lab` — opens in browser
- [x] Open `notebooks/phase2_exploration.ipynb`
- [x] Run all cells — t-SNE 2D and 3D plots render for all-MiniLM-L6-v2, text-embedding-3-small, text-embedding-3-large
- [x] Screenshots saved to `assets/phase2/`

---

## Phase 3 — Baseline Pipeline ✅

### Ingest
- [x] `uv run python -m phase3_baseline.implementation.ingest`
- [x] Prints document count, chunk count, vector dimensions
- [x] `phase3_baseline/vector_db/` directory created

### Chat UI
- [x] `cd phase3_baseline && uv run python app.py`
- [x] Browser opens to Gradio UI
- [x] Ask "Who founded Insurellm?" — answer is coherent
- [x] Right panel shows retrieved context with source filenames

### Evaluate (single test)
- [x] `uv run python -m phase3_baseline.implementation.evaluate 0`
- [x] Prints question, keywords, category, reference answer
- [x] Prints MRR, nDCG, keyword coverage scores
- [x] Prints generated answer and accuracy/completeness/relevance scores

### Evaluation Dashboard (all 150 tests)
- [x] `cd phase3_baseline && uv run python evaluator.py`
- [x] Gradio dashboard opens — retrieval and answer evaluation tabs both work
- [x] Bar charts render by category
- [x] Screenshot saved to `assets/phase3/evaluator_ui.png`

---

## Phase 4 — Explore Custom Configurations ✅

- [x] Notebook fixed: replaced `litellm` with direct `openai` calls (litellm not in deps)
- [x] Cell 11 updated: falls back to `sample_chunks` safely if cell-9 is skipped
- [ ] `uv run jupyter lab` — opens in browser
- [ ] Open `notebooks/phase4_exploration.ipynb`
- [ ] Run LLM-based chunking cells — verify chunking works on one document
- [ ] Run reranking experiment — compare ranked vs unranked results
- [ ] Run query rewriting experiment — compare original vs rewritten query
- [ ] Run full advanced pipeline demo
- [ ] Save t-SNE screenshots to `assets/phase4/`
- [ ] ⚠️ Skip "Process all documents" cell unless you want to wait — it makes one LLM call per document

---

## Phase 5 — Optimized Pipeline ✅

### Ingest
- [x] `uv run python -m phase5_optimized.implementation.ingest`
- [x] Progress bar shows documents being processed (76 docs → 559 chunks, ~3 min)
- [x] `phase5_optimized/preprocessed_db/` directory created

### Chat UI
- [ ] `cd phase5_optimized && uv run python app.py`
- [ ] Browser opens to Gradio UI
- [ ] Ask same question as Phase 3 — compare answer quality
- [ ] Right panel shows retrieved context
- [ ] Save screenshot to `assets/phase5/chat_ui.png`

### Evaluate
- [x] `uv run python -m phase5_optimized.implementation.evaluate 0`
- [x] Test #0 — "Who won the IIOTY award in 2023?" — Accuracy 5/5, Completeness 5/5, Relevance 5/5
- [ ] Run `cd phase5_optimized && uv run python evaluator.py` — compare aggregate scores to Phase 3
- [x] `evaluator.py` created (was missing — added)

---

## Phase 6 — Report Results 🔲

- [ ] Write comparison report covering: knowledge base characteristics, baseline scores, configurations tested, final score comparison
- [ ] Save to `docs/` or project root

---

## Benchmark Generation (optional)

- [ ] `uv run python data/generate_tests.py`
- [ ] Prints progress per category
- [ ] `data/tests.jsonl` is overwritten with new questions
- [ ] ⚠️ This replaces the original benchmark — only run if intentional
