---
origin: web-authored
sources:
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.promptingguide.ai/guides/context-engineering-guide
  - https://medium.com/ai-in-plain-english/10-context-engineering-techniques-every-ai-engineer-should-know-b54b486a6921
confidence: high
cleaned: 2026-07-29
---
# 3 — Retrieval Strategies: Pre-Computed vs. Just-in-Time

> How content gets into the window. The biggest architectural shift in this pillar.

---

## The shift

The RAG-era assumption was: **retrieve before inference**. Embed the corpus, embed the query, pull top-k chunks, stuff them in the window, generate. All retrieval happens before the model does anything.

The agentic assumption is: **retrieve during inference**. Give the model tools and lightweight identifiers, and let it decide what to load, when, based on what it has learned so far. Anthropic calls this **just-in-time context**.

The difference is who decides relevance. Pre-computed retrieval makes an embedding-similarity guess about relevance *before seeing the model's reasoning*. Just-in-time lets relevance be determined by an agent that has already read the first file and now knows which one it actually needs.

---

## Just-in-time context

Instead of loading data, maintain **lightweight identifiers** and load at runtime:

- File paths
- Stored queries
- Web links
- Record IDs, table names
- Search commands

A file path costs ~10 tokens. The file costs 5,000. If the agent needs three of the fifty files a pre-retrieval step would have loaded, the identifier approach spends ~500 tokens on the index and 15,000 on the three files it actually reads — instead of 250,000 on all fifty.

**Progressive disclosure** is the behavioral pattern: the agent discovers relevant context incrementally through exploration, each read informing the next. It mirrors how a human engineer approaches an unfamiliar codebase — `ls`, then `grep`, then read the three files that matter. Nobody reads the repo front to back first.

Metadata carries signal for free. A path like `tests/integration/test_auth_retry.py` tells the agent about scope, purpose, and relationship before a single byte of content is read. Naming conventions are a retrieval optimization.

### Costs

Just-in-time is not free:

- **Latency.** Sequential tool calls are slower than one upfront retrieval. Each exploration round-trip is a full inference.
- **Wandering.** The agent can explore unproductively, burning context on the search itself rather than the answer.
- **Non-determinism.** Two runs may load different files, complicating evals and reproducibility.

---

## The hybrid strategy

The practical default. Pre-load what is cheap and near-certainly needed; leave the long tail to runtime exploration.

```
Pre-load (fixed cost, high hit rate)      Just-in-time (variable, long tail)
-----------------------------------      ---------------------------------
CLAUDE.md / project conventions          Any specific source file
Directory tree / file index              Full API reference sections
Schema summaries                         Historical records
Recently touched files                   Log output, test output
```

Claude Code is this pattern: `CLAUDE.md` loads every session; everything else is `Read`, `Grep`, `Glob` on demand.

**Design question that decides it:** *Is this needed on ≥80% of turns?* Yes → pre-load. No → identifier plus a tool to fetch it.

---

## Pre-retrieval pipeline

When you do retrieve upfront, the operations below compose in this order. Each stage narrows the candidate set, so cheap filters go first.

```
User Query
      ↓
Metadata Filtering       <- cheapest; drop by permission, date, source, tenant
      ↓
Vector Search            <- semantic top-k over what survived
      ↓
Context Ranking          <- rerank with a cross-encoder; send only top of rerank
      ↓
Deduplication            <- collapse near-identical chunks
      ↓
Compression              <- reduce each doc to what answers *this* query
      ↓
Memory Injection         <- add cross-session facts
      ↓
Structured Formatting    <- tag and delimit; never dump raw text
      ↓
LLM
```

Stage notes:

- **Metadata filtering first.** Permission checks and freshness filters are near-free compared to embedding search, and dropping candidates early makes every later stage cheaper. Permission filtering here is also a security control, not just an optimization.
- **Ranking ≠ retrieval.** Bi-encoder vector search is fast and approximate; a cross-encoder reranker is slow and accurate. Retrieve wide (k=50), rerank, send narrow (k=5).
- **Deduplication has a trap.** A chunk retrieved by multiple sub-queries is often the *most* relevant one, not redundant noise. Collapse duplicates but treat multi-retrieval as a positive ranking signal rather than a reason to discard.
- **Compression is query-conditional.** Reduce each document to the portion that answers the current question — not a generic summary. A generic summary discards the specific detail the query needed.
- **Structured formatting.** Wrap in tags with source attribution so the model can cite and so injected content stays distinguishable from instructions.

### A worked example

A production pipeline with the same shape — ingestion and indexing on the left, query and retrieval on the right:

![AWS Bedrock knowledge base pipeline: web crawl → semantic chunking → vector database, then query transformation → hybrid search → context injection → generation](../../images/bedrock-kb-pipeline-billydk.png)

Two things worth noting against the abstract pipeline above. **Hybrid search** runs semantic and keyword retrieval together rather than choosing between them — vectors catch paraphrase, keywords catch exact identifiers, and each covers the other's failure mode. And **query transformation** sits before retrieval: the user's original phrasing is rewritten into tool parameters, because the text a human types is rarely the text that retrieves best.

What the diagram omits is as informative as what it shows — there is no reranking stage and no deduplication, which is typical of a first production cut. Those are the stages teams add after retrieval quality plateaus.

### Ingestion determines the ceiling

Retrieval can only return what parsing extracted. Parser capability tiers roughly like this:

![Three parser tiers: text-only extraction; text plus image descriptions, audio transcription and video summarization; and visually rich document handling](../../images/parser-tiers-by-modality.png)

The consequence for context engineering: a tier-one parser over a PDF-heavy corpus silently drops every chart, diagram, and table into either nothing or garbled text. The retrieval layer then looks broken — low recall, irrelevant chunks — when the actual failure happened at ingestion. Check what the parser produced before tuning k, rerankers, or chunk size.

### Dynamic context windows

Scale retrieval depth to task complexity rather than using a fixed k:

| Task shape | Chunks |
|---|---|
| Simple factual lookup | few — more is pure dilution |
| Comparison / synthesis across sources | more — needs breadth |
| Ambiguous or exploratory | retrieve wide, rerank hard, send narrow |

Fixed k is a bug for both directions: it over-fills simple queries (rot) and under-fills complex ones (missing evidence).

---

## Hierarchical retrieval

For large corpora, retrieve in tiers: search summaries or section headers first, then fetch full content only for the sections that matched. This is just-in-time applied inside a pre-retrieval pipeline — the tier-1 index is the lightweight identifier.

---

## Caching

Two distinct caches, often confused:

- **Prompt caching** (inference-level) — caches the prefill computation for a token prefix. Prefix-match only, so ordering governs hit rate. See [02-context-anatomy.md](02-context-anatomy.md#ordering-stable-before-dynamic).
- **Retrieval caching** (application-level) — caches the *results* of expensive retrieval keyed by query similarity. A near-duplicate query reuses the prior result set instead of re-running search, planning, or sub-query generation. Cuts cost and latency on hot queries.

---

## Context validation

Retrieved content is not trustworthy by default. Validate before injecting:

- Remove outdated documents (freshness threshold)
- Enforce permissions — never surface content the requester cannot access
- Detect conflicting information across sources; surface the conflict rather than silently picking one
- Verify citations resolve to real, retrievable sources

Conflict detection matters most. Two retrieved documents contradicting each other, both injected silently, is a reliable path to a confidently wrong answer. This is **context clash** — see [07-context-failure-modes.md](07-context-failure-modes.md).

---

## Working reference

`~/.claude/refs/agent-context.md` — the Select lever. `~/.claude/refs/agent-tools.md` — tool design determines whether just-in-time retrieval is viable; a tool returning 50k tokens of raw output defeats the purpose. See [06-multi-agent-context.md](06-multi-agent-context.md) for token-efficient tool design.

---

→ Next: [04-compression-compaction.md](04-compression-compaction.md) — what to do when the window fills anyway.
