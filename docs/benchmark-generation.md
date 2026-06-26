# Benchmark Generation — Methodology

---

## Why the Benchmark Comes First

The benchmark is the most important artefact in the workbench. It defines what "good performance" means for this specific knowledge base — and it must be defined **before any pipeline work begins**.

If the benchmark were written after the system was built, there would be an unconscious temptation to write questions the system can already answer. The result would be an inflated score that does not reflect real-world performance.

By locking the benchmark in Phase 1, every configuration decision in Phases 3 through 5 is made in service of the same pre-agreed standard. The final comparison between the baseline and the optimised pipeline is only meaningful because both are measured against the same questions.

**The benchmark file (`data/tests.jsonl`) is written once and never modified during a project.** Regenerating it mid-project resets comparability — you can no longer compare Phase 3 and Phase 5 scores because they were measured against different questions.

---

## The Generation Script

`data/generate_tests.py` is the script that produced `data/tests.jsonl`. It works as follows:

1. **Loads the full knowledge base** — reads every `.md` file from `knowledge-base/`, organised by subfolder, and concatenates them into a single string with section headers. The LLM receives the complete company knowledge base as context.

2. **Makes one LLM call per question category** — for each of the 7 categories, it sends the full KB text along with a precise category definition and asks the model to generate N questions of that type.

3. **Uses structured output** — the response is parsed into `TestQuestion` Pydantic objects, ensuring every entry has the correct fields and format.

4. **Writes to JSONL** — results are appended to `data/tests.jsonl`, one JSON object per line, in category order.

---

## The 7 Question Categories

Questions are divided into 7 categories that test different aspects of retrieval and reasoning:

| Category | What it tests | Example |
|---|---|---|
| `direct_fact` | Single fact from one document | "Who founded Insurellm?" |
| `temporal` | Date, year, quarter, or time period | "When was Carllm's telematics feature scheduled to launch?" |
| `comparative` | Percentage, change, or improvement | "By what percentage did Priya Sharma's recommendation engine increase conversion?" |
| `numerical` | Count or quantity | "How many active contracts does Homellm have?" |
| `relationship` | Entity-to-entity link | "Which product does Marcus Johnson work on?" |
| `spanning` | Combines facts from ≥2 documents | "What product does the IIOTY award winner work on?" |
| `holistic` | Aggregation across many records | "What is the total contract value of all Healthllm contracts?" |

**Why these categories?** They form a ladder of retrieval difficulty:
- `direct_fact` and `temporal` test basic retrieval — can the system find the right document?
- `comparative`, `numerical`, and `relationship` test precision — can it extract specific facts?
- `spanning` tests cross-document reasoning — can it link information across multiple sources?
- `holistic` tests synthesis — can it aggregate across many records?

A system that performs well on `direct_fact` but poorly on `holistic` needs better multi-document retrieval. A system that fails `spanning` likely needs improved context assembly.

---

## Keyword Rules

Each question has a `keywords` field — a list of 2–4 atomic facts extracted from the reference answer. Keywords are used to score **retrieval** quality (not answer quality):

- Are these key facts present anywhere in the top-10 retrieved documents?
- At what rank do they appear?

**Good keywords:** proper names, numbers, product names, dates, award names, job titles — short, specific, verifiable.

**Bad keywords:** prose phrases, sentences, or anything that needs interpretation.

```json
// Good
"keywords": ["Maxine", "Thompson", "IIOTY", "2023"]

// Bad — too vague, not verifiable
"keywords": ["won an award", "data engineering achievement"]
```

The keyword rules in the generation prompt enforce this explicitly. When reviewing generated output, check that keywords are atomic and would appear verbatim in a relevant document.

---

## Reference Answer Rules

Reference answers are used to score **answer quality** (via LLM-as-judge in `evaluate.py`). They must be:

- **1–3 complete sentences** — enough to fully answer the question, no more
- **Directly answering** — no preamble ("Great question!"), no caveats, just the answer
- **Factually grounded** — derived from the knowledge base, not inferred or hallucinated
- **Consistent in voice** — as if written by the same careful author

```json
// Good
"reference_answer": "Maxine Thompson won the prestigious Insurellm Innovator of the Year (IIOTY) award in 2023."

// Bad — too vague
"reference_answer": "Someone from the data engineering team received an award."
```

---

## Running the Script

```bash
# From the project root
uv run python data/generate_tests.py
```

The script makes 7 LLM calls (one per category). Expect 2–5 minutes depending on the model and rate limits. Progress is printed to stdout.

**Output:**

```
Loading knowledge base...
Knowledge base loaded: 123,456 characters
Generating 70 'direct_fact' questions... done (70 generated)
Generating 20 'temporal' questions... done (20 generated)
...
Writing 150 questions to data/tests.jsonl...
Done. data/tests.jsonl contains 150 entries.

Category breakdown:
  direct_fact: 70
  temporal: 20
  spanning: 20
  ...
```

---

## Customising for a Different Knowledge Base

The script is designed to work with **any** knowledge base of `.md` files, not just Insurellm. To adapt it:

1. **Replace the knowledge base** — drop new `.md` files into `knowledge-base/` subfolders. The script reads whatever is there.
2. **Adjust category counts** — edit `CATEGORY_COUNTS` in `generate_tests.py`. For a smaller KB, reduce counts. For a broader KB, increase them.
3. **Add or remove categories** — add a new entry to both `CATEGORY_COUNTS` and `CATEGORY_DEFINITIONS`. The definition tells the LLM exactly what kind of question to produce.
4. **Change the model** — update `MODEL` at the top of the script. Higher-capability models produce better questions for complex categories (`spanning`, `holistic`).

**When to regenerate:**
- When the knowledge base changes substantially (new documents added, old ones removed)
- When starting a fresh project — always regenerate rather than reusing a previous benchmark
- When you want to experiment with a different category balance

**When NOT to regenerate:**
- During an active project where Phase 3 and Phase 5 benchmarks must be comparable
- After Phase 3 ingestion has run — the baseline score is now pinned to the current benchmark

---

## What the LLM Needs to Produce Good Questions

The quality of generated questions depends on:

1. **Enough KB context** — the full KB text is passed in every call. Do not truncate it to save tokens; the model needs to see all documents to write grounded questions.
2. **Precise category definitions** — vague definitions produce off-category questions. If `spanning` questions look like `direct_fact`, tighten the definition.
3. **Explicit keyword rules** — without these, the model may produce keyword phrases instead of atomic terms.
4. **Retry logic** — the script wraps each generation call in exponential backoff retry. If a call fails (rate limit, timeout), it retries automatically.

Review a sample of generated questions before locking the benchmark. Spot-check that:
- `spanning` questions genuinely require reading two separate documents
- `holistic` questions require summing or counting across many records
- Keywords are short and would appear verbatim in retrieved text
- Reference answers are specific (named entities, numbers) not generic
