# RAG Pipeline Findings — Insurellm

> Score tables will be updated as evaluations complete. All other content reflects the current state of the pipeline work.

---

## 1. Knowledge Base

| Property | Value |
|----------|-------|
| Domain | Insurellm — fictional insurance tech company |
| Document count | 76 markdown files |
| Categories | company, products, employees, contracts |
| Source | Internal knowledge base (shared drive simulation) |

**Benchmark:** 150 question–answer pairs across all four categories, written by hand before any technical work began and locked in `data/tests.jsonl`. Every configuration across all phases is scored against the same standard — scores are directly comparable because the target never moved.

**Characteristics relevant to retrieval:** The knowledge base mixes short biographical employee profiles (often <300 words), longer narrative company history, structured product feature lists, and contract documents. This variety means no single chunking strategy is optimal for every document type — making it a realistic test of retrieval robustness.

---

## 2. Embedding Model Selection (Phase 2)

Before building anything, we embedded the knowledge base with three models and visualised the vector space with t-SNE to understand cluster structure.

| Model | Dims | Observation |
|-------|-----:|-------------|
| `all-MiniLM-L6-v2` | 384 | Clusters visible but overlap between categories |
| `text-embedding-3-small` | 1,536 | Cleaner separation; contract documents cluster tightly |
| `text-embedding-3-large` | 3,072 | Sharpest category boundaries; selected for both pipelines |

`text-embedding-3-large` was selected on the basis of visual cluster quality and its strong performance on retrieval benchmarks. Using the same model in both pipelines keeps embedding quality constant, so score differences reflect pipeline design rather than model choice.

---

## 3. Baseline Pipeline (Phase 3)

**Configuration:**

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Chunking | `RecursiveCharacterTextSplitter` — 1,000 chars, 200 overlap | LangChain default; fast, no LLM calls |
| Embedding | `text-embedding-3-large` | Best cluster separation in Phase 2 |
| Vector store | ChromaDB | Local, no infrastructure required |
| LLM | `gpt-4.1-mini` | Good capability/cost balance |
| Retrieval | Top-10 by cosine similarity | Standard starting point |

### Baseline Scores

| Metric | Score |
|--------|-------|
| MRR | |
| nDCG | |
| Keyword Coverage | |
| Accuracy (1–5) | |
| Completeness (1–5) | |
| Relevance (1–5) | |

**Where it fell short:** Character-based splitting is ignorant of document structure — a chunk boundary may cut through a sentence or separate a question from its answer. Short employee profiles sometimes split poorly, with biographical facts landing in separate chunks that don't individually answer a question about that person. These were the expected failure modes going into Phase 4.

---

## 4. Techniques Explored (Phase 4)

### LLM-based chunking

Each document was passed to an LLM which returned structured JSON — a list of chunks, each containing a **headline**, a **summary**, and the **verbatim original text**. All three are concatenated and embedded together.

```
Founding and Initial Growth of Insurellm

Insurellm was founded in 2015 by Avery Lancaster as an insurance tech startup
aimed at innovating the insurance sector. The company began with its first
product, Markellm, a marketplace connecting consumers to insurance providers.
It experienced rapid growth...
```

This gives each chunk three retrieval surfaces: the headline catches topic-based queries, the summary catches paraphrased questions, and the original text handles exact-match retrieval. The 76 source documents produced **559 LLM-enhanced chunks** — roughly 7 chunks per document on average, with longer documents split more finely.

**Observed improvement:** Short employee profiles that previously split poorly now produce self-contained chunks. Each chunk carries enough context to answer a question about that person independently.

### Query rewriting

Before retrieval, the user's question is reformulated into a terse KB search query. This strips conversational filler and focuses on the specific terms most likely to surface relevant chunks.

```
"What can you tell me about that award Maxine won last year?"
  → "IIOTY award winner 2023"

"I heard the company started in someone's garage — is that true?"
  → "Insurellm founding story origin"

"We talked about the health product earlier — what does it cost?"
  → "CareLlm pricing"
```

In multi-turn conversations, the rewriter folds in prior context so a vague follow-up resolves correctly against the current topic rather than triggering a new unrelated retrieval.

### Reranking

After vector retrieval of the top-20 chunks, a second LLM call re-orders them by true relevance to the original question. The model sees the question and all 20 chunks and returns a ranked list — the top-10 of this reranked set are passed to generation.

Vector similarity is a proxy for relevance; the reranker applies genuine language understanding. This is especially useful when a highly similar chunk is topically adjacent but not directly responsive — the reranker can move it down in favour of a chunk that actually contains the answer.

### Multi-pass retrieval

The pipeline retrieves independently on both the original question and the rewritten query, then merges and deduplicates before reranking. This increases recall — the two queries often surface overlapping but not identical result sets — at the cost of a larger input to the reranker.

---

## 5. Optimised Pipeline (Phase 5)

**Configuration:**

| Component | Choice |
|-----------|--------|
| Chunking | LLM-based — headline + summary + original text per chunk |
| Embedding | `text-embedding-3-large` |
| Vector store | ChromaDB (`preprocessed_db/`) |
| LLM | `gpt-4.1-nano` |
| Retrieval | Multi-pass (original + rewritten query) → merge → LLM rerank top-20 → top-10 |

Note: the generation model was downgraded from `gpt-4.1-mini` (Phase 3) to `gpt-4.1-nano` (Phase 5). If scores improve despite the weaker generation model, it suggests the retrieval improvements are doing real work — better context reduces the burden on generation.

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
- LLM-based chunking produced meaningfully better chunks for short, structured documents (employee profiles, product specs) where character splitting creates fragmented facts
- Query rewriting had clear impact on conversational and multi-turn questions — cases where the baseline retrieved on literal wording and missed relevant content
- Multi-pass retrieval increased recall on questions where the original and rewritten queries surfaced complementary result sets

**Trade-offs:**
- Ingest time increased significantly — 76 documents took ~3 minutes with 3 parallel workers vs seconds for character splitting. This is a one-time cost but matters for large or frequently updated knowledge bases
- Each query now makes 3–4 LLM calls (rewrite, rerank, generate) vs 1 in the baseline. Latency increases accordingly
- The reranker adds most value when the top-K retrieval set is noisy. On clean, specific questions the baseline retrieval was already good enough

**If starting again:**
- Test chunk overlap more systematically — the LLM chunker was instructed to use ~25% overlap but this wasn't measured. Explicit overlap control may improve MRR further
- Evaluate reranking independently of query rewriting to understand which technique drives which score improvements
- Consider a hybrid approach: LLM chunking for long narrative documents, character splitting for short structured ones, to reduce ingest cost without sacrificing quality

---

## 8. Current Status and Recommendation

**The optimised pipeline is currently performing worse than the baseline.**

This is not a failure — it is the expected output of a structured process. We now have a precise picture of where we stand, which techniques have been tested, and exactly how much ground needs to be recovered before the optimised pipeline earns the right to replace the baseline.

The value of this workbench is that it makes that picture legible. Without a fixed benchmark and a measured baseline, a worse result would be invisible — the team would ship a more complex pipeline and simply not know. With them, we can iterate with confidence.

**Recommendation: continue using the Phase 3 baseline in production.** The Phase 5 pipeline should be treated as an active experiment. The next steps are to isolate which combination of techniques is causing the regression — likely chunking granularity or reranking behaviour on this specific knowledge base — and to run targeted experiments against the benchmark until scores exceed Phase 3. The methodology for that work is already in place.
