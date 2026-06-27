# RAG Pipeline Findings — [Project Name]

> **How to use:** Fill in the bracketed placeholders as you complete each phase. Score tables are filled in after running `evaluator.py` for both Phase 3 and Phase 5.

---

## 1. Knowledge Base

| Property | Value |
|----------|-------|
| Domain | |
| Document count | |
| Categories | |
| Notable characteristics | [e.g. mix of narrative prose and structured tables; some docs very short] |

**Benchmark:** [N] question–answer pairs across [N] categories, locked before any technical work began. All phases are scored against the same standard.

---

## 2. Embedding Model Selection (Phase 2)

| Model | Dims | Observation |
|-------|-----:|-------------|
| `all-MiniLM-L6-v2` | 384 | |
| `text-embedding-3-small` | 1,536 | |
| `text-embedding-3-large` | 3,072 | |

**Selected:** [model] — [reason]

---

## 3. Baseline Pipeline (Phase 3)

**Configuration:**

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Chunking | `RecursiveCharacterTextSplitter` — 1,000 chars, 200 overlap | |
| Embedding | | |
| Vector store | ChromaDB | |
| LLM | | |
| Retrieval | Top-10 by cosine similarity | |

### Baseline Scores

| Metric | Score |
|--------|-------|
| MRR | |
| nDCG | |
| Keyword Coverage | |
| Accuracy (1–5) | |
| Completeness (1–5) | |
| Relevance (1–5) | |

**Where it fell short:** [Which question categories scored lowest? What retrieval failures were observed?]

---

## 4. Techniques Explored (Phase 4)

### LLM-based chunking

[Describe the chunking approach and what the chunks looked like. Note chunk count vs baseline.]

**Observed improvement:** [What got better? What didn't?]

### Query rewriting

[Describe the rewriting approach. Include 2–3 before/after examples from your domain.]

### Reranking

[Describe the reranking approach. Note the retrieval K before and after reranking.]

### Multi-pass retrieval

[Describe the multi-pass approach. Note recall improvement vs cost.]

---

## 5. Optimised Pipeline (Phase 5)

**Configuration:**

| Component | Choice |
|-----------|--------|
| Chunking | |
| Embedding | |
| Vector store | ChromaDB |
| LLM | |
| Retrieval | |

### Optimised Scores

| Metric | Score |
|--------|-------|
| MRR | |
| nDCG | |
| Keyword Coverage | |
| Accuracy (1–5) | |
| Completeness (1–5) | |
| Relevance (1–5) | |

---

## 6. Comparison

| Metric | Phase 3 Baseline | Phase 5 Optimised | Change |
|--------|-----------------|-------------------|--------|
| MRR | | | |
| nDCG | | | |
| Keyword Coverage | | | |
| Accuracy | | | |
| Completeness | | | |
| Relevance | | | |

---

## 7. Key Findings

**What worked:**
-
-

**What didn't move the needle:**
-

**Trade-offs:** [Latency, ingest cost, complexity vs score improvement]

**If starting again:** [What would you change?]

---

## 8. Current Status and Recommendation

[Is the optimised pipeline ready to replace the baseline? If not, what's the next experiment?]

**Recommendation:** [Continue with baseline / deploy optimised / run further experiments]
