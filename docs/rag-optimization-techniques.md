# RAG Optimization Techniques

Last Updated: June 2026

## Chunking

**Fixed-size chunking** : Split documents into equal token/character chunks. Simple baseline; ignores semantic boundaries.

**Recursive chunking** : Split on progressively smaller separators (paragraphs → sentences → words) until chunks hit a target size. Good all-rounder.

**Semantic chunking** : Split at semantically meaningful boundaries by comparing embedding similarity between consecutive sentences. Preserves topic coherence.

**Sliding window chunking** : Create overlapping chunks so context at chunk boundaries isn't lost. Controlled by chunk size + overlap parameters.

**Parent-child chunking** : Index small chunks for precision retrieval, but return their larger parent chunk for richer generation context.

**Sentence window retrieval** : Embed individual sentences, retrieve on sentence precision, but expand to surrounding ±N sentences at generation time.

**Document-structure chunking** : Respect document structure (headings, sections, tables, markdown) as natural split points rather than token limits.

**Late chunking** : Embed the full document first with a long-context model, then split into chunk embeddings that retain global document context.

**LLM-driven chunking** : Use an LLM to identify semantically optimal chunk boundaries, trading cost for maximum coherence.

**Adaptive chunking** : Dynamically select chunking strategy per-document based on intrinsic document metrics rather than one fixed method.

**RAPTOR** : Recursively cluster and summarize chunks into a tree of abstractions. At query time retrieve from multiple tree levels simultaneously for multi-hop reasoning.

---

## Indexing

**Contextual retrieval** : Prepend an LLM-generated 1–2 sentence summary (explaining where a chunk sits in its document) to each chunk before embedding. Cuts retrieval failure rate significantly.

**Metadata enrichment** : Attach structured metadata (source, date, entity tags, section title) to chunks to enable downstream filtering and ranking signals.

**Hypothetical question indexing** : Generate representative questions for each chunk and index those alongside the chunk. Bridges the query-document vocabulary gap.

**Summary indexing** : Generate and index document-level or section-level summaries alongside raw chunks for coarse-to-fine retrieval.

**Knowledge graph indexing (GraphRAG)** : Extract entity-relation triples from documents into a graph DB. At query time traverse the graph to gather multi-hop relational information.

**Embedding caching** : Cache computed embeddings for frequently-seen content to avoid redundant model calls and reduce latency.

**Vector quantization** : Compress vector embeddings (e.g., via product quantization) to reduce memory and speed up ANN search at minor accuracy cost.

**Retriever fine-tuning** : Fine-tune the embedding model on domain data or (query, relevant-doc) pairs to better match the retrieval distribution of your knowledge base.

---

## Query Transformation

**Query rewriting** : Rephrase the user query before retrieval to better match document phrasing or correct ambiguity, using an LLM.

**Query expansion** : Broaden the query by adding synonyms, related terms, or sub-questions to improve recall.

**Query decomposition** : Break a complex multi-part question into simpler sub-queries, retrieve for each, then synthesize. Handles multi-hop reasoning.

**HyDE (Hypothetical Document Embeddings)** : Generate a hypothetical answer to the query with an LLM, then embed that answer as the retrieval query. Bridges the query-document asymmetry.

**Step-back prompting** : Rewrite the query as a higher-level, more general question to retrieve background knowledge that enables better downstream reasoning.

**Multi-query generation** : Generate multiple paraphrases of the query, retrieve for each, and fuse results. Broader coverage than a single query.

**RAG Fusion** : Combine multi-query generation with RRF; produces a richer, more comprehensive retrieval set by exploiting query variation.

**Query routing** : Classify the query type and dispatch to the right retrieval system (vector DB, SQL, web search, graph) based on what kind of answer is needed.

**IRCoT (Interleaved Retrieval + Chain-of-Thought)** : Alternate between retrieval steps and chain-of-thought reasoning, so each reasoning step can trigger a targeted retrieval.

---

## Retrieval

**Dense vector retrieval** : Embed query and documents into a high-dimensional vector space using a transformer encoder; retrieve by cosine/dot-product similarity.

**BM25 (sparse retrieval)** : Classic keyword-based TF-IDF variant. Strong on exact and rare term matching; zero training cost. Often outperforms dense on precise numeric queries.

**SPLADE** : Sparse learned representation that combines BM25-style sparsity with neural expansion. Bridges keyword and semantic retrieval.

**Hybrid search** : Combine dense and sparse (BM25/SPLADE) scores at retrieval time to capture both semantic intent and exact keyword match.

**Reciprocal Rank Fusion (RRF)** : Score-agnostic method to merge ranked lists from multiple retrievers. Robust to score scale differences; the standard hybrid fusion technique.

**ColBERT (late interaction)** : Retain per-token embeddings for both query and document; score via MaxSim at query time. More precise than single-vector retrieval at the cost of index size.

**Multi-vector retrieval** : Represent a document as multiple vectors (e.g., per sentence or per topic) and match against any of them, improving recall for long documents.

**Metadata filtering** : Pre-filter the vector index by structured metadata (date, author, category) before semantic search, reducing noise and cost.

**MMR (Maximal Marginal Relevance)** : Select retrieved docs to balance relevance to the query against diversity within the result set, reducing redundancy.

**ANN indexing (HNSW, IVF)** : Approximate nearest-neighbor algorithms that trade a small recall loss for dramatically faster vector search at scale.

---

## Reranking & Post-processing

**Cross-encoder reranking** : After initial retrieval, run a cross-encoder that sees query and document together to produce a fine-grained relevance score. More accurate than bi-encoder similarity.

**Cohere Rerank / API rerankers** : Managed reranking API that returns relevance scores without managing local cross-encoder infrastructure.

**LLM-as-reranker** : Prompt an LLM to score or order retrieved documents by relevance. Flexible and zero-shot but slower and costlier than a dedicated reranker.

**Pointwise / pairwise / listwise reranking** : Three reranking paradigms: score each doc independently, compare docs in pairs, or rank the entire list at once.

**Adaptive reranking** : Dynamically adjust how many documents are reranked based on query complexity to avoid unnecessary compute on simple queries.

**Context compression** : After retrieval, use an LLM to distill only the relevant passages from retrieved chunks before feeding to the generator, shrinking prompt size.

---

## Architecture Patterns

**Self-RAG** : The LLM decides when to retrieve (on-demand), then critiques its own retrieved documents and output using reflection tokens. Reduces unnecessary retrieval.

**CRAG (Corrective RAG)** : Evaluate retrieved document quality; if below a confidence threshold, fall back to a web search for fresher or better-matched content.

**Adaptive RAG** : Route queries to different-sized retrieval pipelines based on query complexity — simple queries skip retrieval entirely; complex ones use full pipelines.

**Agentic RAG** : LLM agent with tool access decides what to retrieve, when, and from where. Can loop, use APIs, write SQL, or browse the web dynamically.

**Multi-agent RAG** : Multiple specialized agents (planner, searcher, summarizer, validator) collaborate on retrieval and synthesis for complex tasks.

**Modular RAG** : Design the pipeline as swappable, composable modules so individual stages (chunker, retriever, reranker, generator) can be replaced independently.

**FLARE (Forward-Looking Active Retrieval)** : Trigger retrieval mid-generation when the model is uncertain about upcoming tokens, rather than only at the start.

**LightRAG** : Graph-based RAG variant that combines entity graphs with vector retrieval, emphasizing efficiency and lower token usage than GraphRAG.

**Semantic caching** : Cache retrieval results for semantically similar queries to avoid redundant searches and reduce latency at inference time.

**Retrieval-based memory** : For multi-turn chat, selectively retrieve relevant past turns rather than injecting full conversation history, managing context window efficiently.

---

## Generation Optimization

**Prompt compression** : Compress retrieved context before passing to the LLM to fit more relevant information into the context window.

**Forced citations** : Instruct the LLM to cite its source chunks inline, enabling provenance tracking and reducing hallucination by grounding each claim.

**Lost-in-the-middle mitigation** : Reorder retrieved docs to place most relevant content at the start and end of the context window, exploiting LLM attention patterns.

**Prompt tuning for RAG** : Optimize the prompt template that wraps retrieved context (system prompt, framing, instruction phrasing) to improve generation quality.

**Generator fine-tuning** : Fine-tune the LLM on domain-specific retrieval-augmented examples so it better leverages retrieved context and reduces hallucination.

---

## Evaluation

**Faithfulness** : Measures whether every claim in the generated answer is supported by the retrieved context. Primary hallucination metric.

**Answer relevancy** : Measures how well the generated answer addresses the user's actual query.

**Context precision** : Proportion of retrieved chunks that are actually relevant to the query. Low precision = noisy retrieval.

**Context recall** : Proportion of necessary information that was successfully retrieved. Low recall = missing key facts.

**RAGAS** : Open-source framework combining faithfulness, answer relevancy, context precision, and context recall into a unified RAG evaluation suite.

**Precision@k / Recall@k** : Classic IR metrics measured at top-k retrieved documents. Useful for benchmarking retriever changes independently of the generator.

**MRR (Mean Reciprocal Rank)** : Measures how high the first relevant document appears in the ranked result list. Useful for evaluating reranker quality.

**nDCG (Normalized Discounted Cumulative Gain)** : Graded relevance metric that rewards highly relevant docs ranked higher. Standard benchmark metric for retrieval systems.

**Groundedness / hallucination rate** : End-to-end measure of how often responses contain claims not supported by retrieved or ground-truth sources.

**LLM-as-judge** : Use an LLM to score retrieval or generation quality on custom rubrics when ground-truth labels are unavailable.

**Synthetic QA generation** : Auto-generate question-answer pairs from the knowledge base to build a cheap evaluation set without manual labelling.