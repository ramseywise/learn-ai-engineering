# Example: Architecture Walkthrough — RAG Pipeline

**Question**: "Walk me through the architecture of one of the AI systems you've built."

---

## Altitude 1: Executive pitch (60 seconds)

> "Our nonprofit client support teams were spending 40% of their time answering questions that were already answered in program documentation — grant guidelines, eligibility rules, policy updates. I built a retrieval-augmented system that lets staff query across all program docs in natural language and get cited answers. It reduced average lookup time from 8 minutes to under 90 seconds, and staff reported significantly higher confidence in their answers."

**[Why this works]**: Opens with the cost, not the technology. States the mechanism in one sentence. Closes with a concrete number. No acronyms that require explanation.

---

## Altitude 2: Architecture walk (5 minutes)

> "Let me draw it. [Draws while talking.]
>
> There are three main parts: an ingestion pipeline, a retrieval index, and a query service.
>
> The ingestion pipeline — on the left — runs offline on a cron schedule. It pulls documents from a Google Drive folder using the Drive API, detects format (PDF, Docs, DOCX), converts to clean text, and chunks them. Chunking was a significant design decision I'll come back to. Each chunk goes through an embedding model — we used OpenAI's text-embedding-3-small — and the vectors plus metadata land in a Pinecone index.
>
> In the middle is the index — the boundary between ingestion and serving. Everything to the left produces it; everything to the right consumes it.
>
> The query service — on the right — is a FastAPI app. A user sends a natural-language question. We embed it with the same model used for ingestion, run a top-k similarity search against Pinecone, pull the matching chunks, and pass them as context to GPT-4 with a prompt that requires citations. The response returns to the user with source references: document name, page, and a snippet.
>
> Scale: ingestion runs nightly on roughly 800 documents ranging from 2 to 50 pages. Query volume is low — 50 to 200 queries per day. p95 latency is around 3 seconds end-to-end.
>
> The key design choices: offline ingestion (not on-demand), fixed chunking with overlap, same embedding model for both sides of the index, citation-required prompting."

**[Why this works]**: Narrates data flow left-to-right. Names the specific technology choices and signals awareness that they were choices. Gives concrete scale numbers unprompted. Flags that chunking was a decision worth drilling — an invitation to go to altitude 3.

---

## Altitude 3: Deep dive — chunking strategy

*[Interviewer picks up the signal and drills.]*

**Probe**: "You mentioned chunking was a significant decision. Walk me through it."

> "Our documents ranged from 2-page policy memos to 50-page grant guidelines. The core tension in chunking is retrieval precision vs. context completeness: smaller chunks surface more precisely matching passages but can split mid-idea; larger chunks give the model more context but bury the relevant passage in noise that degrades ranking.
>
> I evaluated three approaches. First: fixed-size chunks at 512 tokens with 50-token overlap. Fast, predictable, model-agnostic. The overlap handles the boundary case where a sentence splits across chunks. Second: semantic chunking — paragraph boundaries from the document structure. More natural, but our PDFs had inconsistent heading and paragraph structure. Third: hierarchical chunking with a parent-child index — child chunks for retrieval precision, parent chunks injected as context at generation time. This was the most promising but added index complexity and the latency from fetching parent chunks was problematic for our 3-second target.
>
> We went with fixed 512-token chunks with 50-token overlap. The main thing it gave up was semantic coherence — a 512-token chunk sometimes starts mid-paragraph. The mitigation was generous overlap and returning top-5 rather than top-3 chunks to give the model more context to work with.
>
> If I were rebuilding today, I'd use document-structure-aware chunking with a fallback to fixed-size. The library support is much better now than it was when we built this."

**[Why this works]**: Names the tension at the top (precision vs. completeness) — this is what the interviewer was testing. Shows three options, explains the evaluation criteria, lands on a justified choice. Acknowledges the cost of the choice (semantic coherence). Prepares the "differently today" answer without being asked.

---

## Altitude 3: Deep dive — decision defense

**Probe**: "Why Pinecone over something like pgvector or Weaviate?"

> "At the time — late 2023 — pgvector was maturing but required Postgres configuration I wasn't confident we could maintain operationally. Our team didn't have a DBA and the client environment was a managed Google Cloud SQL instance. pgvector on Cloud SQL was available but the index performance at our scale wasn't well documented.
>
> Weaviate was the other serious contender. More feature-rich, especially the hybrid search with BM25 + vector. We ran a quick proof of concept and the results were good, but the self-hosted operational burden was a concern — we needed something that could run managed without dedicated infra attention.
>
> Pinecone was expensive relative to the other two but the operational profile was exactly right: managed, well-documented, no index tuning required at our scale. For 800 documents we weren't going to hit the query limits.
>
> Today I'd give pgvector a more serious look. The Cloud SQL integration has improved, the performance benchmarks are well-documented, and keeping vector data colocated with structured metadata simplifies a lot of the filtering logic we ended up building separately."

**[Why this works]**: Grounds the decision in the actual constraints (no DBA, managed environment, known scale). Shows the evaluation was real (ran a Weaviate POC). Acknowledges the cost (price). Updates correctly for today — the constraint landscape changed.

---

## Common follow-ups and brief answers

**"What happens if the embedding API goes down during ingestion?"**
> "Ingestion fails gracefully — we log the failure, skip to the next batch, and the cron job retries the failed documents the next night. We don't have real-time SLA requirements on ingestion. If the query service embedding call fails, we return a degraded response telling the user to try again rather than an empty error."

**"How do you handle documents that are updated?"**
> "We use document metadata — last-modified timestamp from Drive — to detect changes. If the timestamp changed, we delete the old vectors for that document by document ID and re-ingest. It's a full re-chunk-and-embed on change, not a delta. At 800 documents with low change rate this was fast enough."

**"What would you add if you had another two weeks?"**
> "Evaluation harness. We had no systematic way to measure retrieval quality — whether the right chunks were surfacing for a given query. I added some manual spot-checking but a proper golden eval set with recall@k metrics would have caught a regression we saw in month three much faster."
