# RAG Optimisation Workbench — Methodology

---

## What This Is

A reusable framework for discovering the optimal RAG pipeline configuration for any given knowledge base. It does this by starting from a fixed, uniform baseline and systematically varying configuration choices — measuring the effect of each change against a benchmark that is defined before any technical work begins.

Each knowledge base is its own self-contained project. The same phases are applied every time, producing comparable outputs and a clear picture of what configuration works best and why.

---

## Organisational Context

Most organisations adopting RAG right now are doing it in an ad hoc way. A team picks a library, builds something, it kind of works, they ship it. There is no baseline, no benchmark, no understanding of whether a different configuration would have produced significantly better results. Decisions are made on intuition and the findings are not transferable to the next project.

This framework exists to fix that.

**Where it sits** depends on organisational maturity. In an early or mid-stage company it lives within an AI or data engineering team, owned by a technical lead trying to establish repeatable practice around AI adoption. In a larger organisation it sits within a Centre of Excellence, an AI platform team, or an R&D function — a team whose job is to evaluate and standardise how the organisation adopts AI capabilities. In a consultancy or agency context it becomes a client-facing methodology, giving engagements structure, credibility, and a defensible output.

**What problem it solves** is the absence of rigour without the weight of bureaucracy. It is not a governance process. It is a structured way of working that produces evidence — evidence that a configuration was tested, that an improvement was measured, and that the methodology can be repeated.

**The broader framing** is that this framework is, at its core, an AI evaluation practice. Most organisations do not have one yet but increasingly need one as they move from experimenting with AI to depending on it. The ability to measure, compare, and document AI system performance in a repeatable way is becoming a core organisational capability. This workbench is a practical, project-level expression of that capability. Done well, it is the seed of something larger — a standardised approach to how an organisation evaluates and improves any AI system it builds.

---

## Why Do It This Way

The goal is not just to build a RAG system — it is to demonstrate RAG optimisation. That requires three things: an honest definition of what good looks like before any technical work begins, a uniform baseline to measure against, and a structured way to improve on that baseline and show the difference.

**For technical teams** it provides a shared language and a repeatable process. Instead of every RAG project starting from scratch, the team has a playbook. Over multiple projects the benchmark scores and reports accumulate into institutional knowledge about which configurations work and which don't across different types of knowledge bases.

**For leadership and stakeholders** it provides visibility and justification. Instead of "we built a RAG system and it seems good," you can say "we started from a standard baseline, tested a series of configurations against a fixed benchmark, improved accuracy by X, and here is the report." That is a fundable, defensible, presentable result.

**For the organisation over time** it builds a body of evidence. Which configurations generalise across knowledge bases? Which techniques tend to help most for internal documentation versus customer-facing content? You can only answer those questions if the methodology is consistent across projects. This framework makes that consistency possible.

There is also a deliberate separation between exploration and commitment. The notebook phases are fast and disposable — you are learning, not building. The MVP phases are structured and measurable — you are building on what you have already learned. This stops you from making permanent architectural decisions before you understand the data.

---

## The Baseline

Every project starts with the same thing: a basic LangChain pipeline. Not because LangChain is the best tool, but because it is the same tool across every project. That uniformity is what makes the baseline meaningful and what makes results comparable across projects.

The library and the pipeline are ultimately secondary. What matters is understanding which **configuration** produces the best results for a given knowledge base. Configuration means the full set of choices that shape how the pipeline behaves — chunking strategy, chunk size and overlap, embedding model, retrieval method, reranking approach, query handling, and any other technique introduced along the way.

Custom code enters the picture not because it is inherently better than LangChain but because some configurations — reranking, hybrid search, query expansion, and others — are either unavailable in LangChain or too abstracted to control meaningfully. Custom code is the escape hatch that unlocks configuration space when LangChain's boundaries are reached. It is a tool, not a destination.

The story the framework tells across every project is: here is what a standard pipeline produces on this knowledge base, and here is how far we were able to move that result by finding the right configuration.

---

## The Core Loop

The framework follows a deliberate rhythm: **define the benchmark, explore the data, build, explore further, build again, then report.**

The human sets the standard first. Before any code runs, a benchmark exists that defines what good performance looks like for this specific knowledge base. Everything that follows is measured against it.

Exploration happens in notebooks — fast, visual, disposable. Building happens in Python files — structured, usable, evaluated against the fixed benchmark. The benchmark is a JSONL file of questions and expected answers, created once in Phase 1 and never changed, so every configuration change across all phases is measured against the same standard.

The key distinction between the two build phases is the configuration of the pipeline. Everything else — the Gradio interfaces, the benchmark file, the evaluation logic — stays identical. That is what makes the comparison meaningful.

---

## The Phases

---

### Phase 1 — Define the Benchmark
*No code. Goal: define what good performance looks like before any technical work begins.*

Before any code runs, we read the knowledge base as humans and write a representative set of questions and expected answers. These are stored in a JSONL file that becomes the fixed benchmark for the entire project.

This is the most important phase in the framework. By defining success criteria before building anything, we ensure that every technical decision that follows is made in service of a clear, pre-agreed standard — not retrofitted around whatever the system happens to produce.

Writing the benchmark first also prevents a subtle but common failure: unconsciously designing a system around questions you already know it can answer. The benchmark is written without any system in mind, which makes it honest.

Each entry in the benchmark file contains the question, a list of keywords that must appear in retrieved context, a reference answer, and a category that describes the type of reasoning required — for example `direct_fact`, `temporal`, `spanning`, or `holistic`. Questions should span multiple categories to give a complete picture of how the system performs across different retrieval challenges.

The benchmark file is locked at the end of this phase and never changed.

**Output:** `data/tests.jsonl` — a JSONL benchmark file of questions and expected answers representing realistic use of the knowledge base.

---

### Phase 2 — Explore the Data
*Notebook-based. Goal: understand the knowledge base mathematically before building anything.*

With the benchmark defined, we now look at the knowledge base technically. Using a basic LangChain RAG pipeline in a notebook, we chunk and embed the knowledge base then visualise the embedding space using t-SNE. We are looking for cluster structure, separation quality, and any obvious anomalies in how the data sits in vector space.

In this phase we use a free local embedding model (HuggingFace `all-MiniLM-L6-v2`) to iterate quickly without incurring API costs. Once we have a feel for the data, we can switch to a higher-quality model (`text-embedding-3-large`) to see how cluster structure changes. We also check the size of the knowledge base in characters and tokens — this informs chunking decisions and gives a sense of whether the context window becomes a factor.

From there we do lightweight hyperparameter tuning — chunk size, overlap, embedding model choices — until we have a clear picture of how this knowledge base behaves. The starting point for chunk size is 1000 characters with 200-character overlap; how tightly the data clusters in the 2D and 3D t-SNE projections tells us whether that needs to change.

Nothing in this phase is permanent. It is purely about understanding the shape of the data before committing to any architectural decisions.

**Output:** `notebooks/phase2_exploration.ipynb` — a notebook with visualisations and notes on embedding characteristics and what parameters seem to work best.

---

### Phase 3 — Build the LangChain MVP
*Python files + Gradio. Goal: establish a uniform, measurable baseline.*

We migrate the best-performing Phase 2 pipeline into structured Python code. The implementation has three modules:

- **`ingest.py`** — loads all `.md` files from the knowledge base, adds folder-name metadata (`doc_type`), chunks with `RecursiveCharacterTextSplitter` (1000 characters, 200 overlap), embeds with `text-embedding-3-large`, and stores in a local Chroma vector database. Run once to populate the database.
- **`answer.py`** — the retrieval and generation pipeline. Combines conversation history with the current question to improve retrieval, fetches the top 10 documents (`RETRIEVAL_K = 10`), and calls `gpt-4.1-mini` with a system prompt containing the retrieved context.
- **`evaluate.py`** — runs the benchmark. For each test question it calculates retrieval metrics (MRR, nDCG, keyword coverage) and calls an LLM judge that scores the generated answer against the reference answer on accuracy, completeness, and relevance (each 1–5).

These are wrapped in two Gradio interfaces: `app.py` — a chat panel on the left, retrieved context on the right — for interactive use; and `evaluator.py` — an evaluation dashboard that runs all 150 benchmark tests and displays colour-coded aggregate scores and per-category bar charts.

This system will not be perfect. That is expected and fine. Its purpose is to establish an honest, measurable baseline — a score against the benchmark that every subsequent configuration change is trying to beat. Because every project starts from the same LangChain foundation, this score is also comparable across projects.

**Output:** `phase3_baseline/` — a working LangChain-based RAG application and a baseline benchmark score.

---

### Phase 4 — Explore Custom Configurations
*Notebook-based. Goal: use what we learned in Phases 2 and 3 to test configurations beyond what LangChain allows.*

Armed with a baseline score and a clear picture of where the Phase 3 configuration falls short, we return to a notebook. Where LangChain's abstractions limit the configurations we can test, we introduce custom code — not as a wholesale replacement but as the tool that lets us reach techniques like reranking, hybrid search, query expansion, and custom retrieval logic.

The key techniques explored here are:

- **LLM-based chunking** — instead of splitting by character count, the LLM reads each document and produces structured chunks: a brief headline, a summary of the chunk's content, and the original text verbatim. The headline and summary make each chunk more semantically rich and more likely to surface in relevant queries. The original text is preserved unchanged.
- **Query rewriting** — the user's conversational question is reformulated into a short, precise knowledge base query before retrieval. This bridges the vocabulary gap between how users phrase questions and how information is stored.
- **Reranking** — after vector retrieval, a second LLM call re-orders the results by relevance to the original question. Vector similarity is a good but imperfect proxy for relevance; an LLM can surface chunks that were ranked too low by cosine distance.
- **Multi-pass retrieval** — retrieving on both the original question and the rewritten query, then merging and deduplicating the results before reranking, increases recall without proportionally increasing context length.

We visualise the new embedding space alongside the Phase 2 results to see whether LLM-enhanced chunks cluster more cleanly.

**Output:** `notebooks/phase4_exploration.ipynb` — configuration experiments, visualisations, and a clear rationale for what to carry into Phase 5.

---

### Phase 5 — Build the Custom MVP
*Python files + Gradio. Goal: build the best configuration found in Phase 4 and compare it against the baseline.*

We build the refined pipeline into exactly the same structure as Phase 3 — the same Gradio interface, the same JSONL benchmark file, the same evaluation logic. The only thing that changes is the pipeline configuration.

The Phase 5 pipeline is meaningfully more involved than Phase 3:

- **`ingest.py`** — uses the LLM to chunk every document (headline + summary + original text), processes documents in parallel using a worker pool to manage throughput against the LLM's rate limits, and stores the enriched chunks in a separate Chroma database (`preprocessed_db`).
- **`answer.py`** — implements the full multi-pass pipeline: rewrite the query, retrieve the top 20 candidates on both the original and rewritten queries, merge and deduplicate, rerank the merged set by LLM relevance assessment, and return the top 10. All LLM calls that touch the API are wrapped in retry logic with exponential backoff to handle rate limiting gracefully.
- **`evaluate.py`** — identical evaluation logic to Phase 3, measuring the same metrics against the same benchmark so results are directly comparable.

Running the evaluation now gives us a direct comparison: did the new configuration outperform the baseline, and by how much? Was the added complexity justified by the result?

**Output:** `phase5_optimized/` — a working custom RAG application and a benchmark score that can be directly compared to Phase 3.

---

### Phase 6 — Report the Results
*Written report. Goal: tell the story of what was tried, what changed, and what was learned.*

With two complete systems and two benchmark scores, we write up the findings. The report is not just a summary of results — it is a transferable record of configuration decisions made and lessons learned that can inform future projects.

The report covers:

- What the knowledge base looked like and how that shaped early decisions
- What the baseline configuration produced and where it fell short
- Which configurations were tested in Phases 4 and 5 and why
- A direct comparison of benchmark scores between the baseline and the optimised pipeline
- Conclusions and recommendations for what the next configuration step would be

**Output:** A structured report that stands on its own as a reference for future projects.

---

## Evaluation Metrics

The benchmark drives two types of evaluation, both running against the same fixed test set:

**Retrieval metrics** measure whether the right documents are being surfaced:

- **Keyword coverage** — the percentage of expected keywords found anywhere in the top-10 retrieved documents. A low score here means the retriever is missing relevant content entirely.
- **MRR (Mean Reciprocal Rank)** — the average of 1/rank across all keywords. It rewards retrieving relevant content early, not just retrieving it at all.
- **nDCG (Normalised Discounted Cumulative Gain)** — accounts for position and ideal ranking. Penalises finding a keyword at rank 8 more than finding it at rank 2.

**Answer metrics** measure whether the generated answer is actually correct:

- **Accuracy (1–5)** — factual correctness compared to the reference answer. A wrong answer must score 1.
- **Completeness (1–5)** — whether all aspects of the reference answer are addressed.
- **Relevance (1–5)** — whether the answer is focused on the specific question without unnecessary additions.

Accuracy, completeness, and relevance are scored by an LLM judge that sees the generated answer and the reference answer side by side.

---

## Project Structure

```
/project-name/
  /knowledge-base/          ← input .md files, organised by category
  /data/
    tests.jsonl             ← benchmark (locked after Phase 1)
  /notebooks/
    phase2_exploration.ipynb
    phase4_exploration.ipynb
  /phase3_baseline/         ← LangChain MVP
    app.py
    evaluator.py
    /implementation/
      ingest.py
      answer.py
      evaluate.py
  /phase5_optimized/        ← Custom pipeline
    app.py
    /implementation/
      ingest.py
      answer.py
      evaluate.py
  /docs/
    methodology.md          ← this document
```

---

## What Success Looks Like

At the end of any project run through this framework you have:

- A fixed, honest benchmark defined by humans before any technical work began
- A clear picture of the knowledge base's embedding characteristics
- A uniform baseline score that is comparable across every project run through this framework
- A refined pipeline that demonstrably outperforms that baseline
- A quantified, direct comparison between the two
- A written record of every configuration decision made and what was learned
- A reusable methodology that gets more valuable with every project it is applied to
