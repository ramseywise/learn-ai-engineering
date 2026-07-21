# Start Here — the AI Engineering Journey

A step-by-step route through this repo's knowledge: ten pillars, ordered so each builds
on the last. Written for someone starting from (almost) zero — if you already know a
pillar, skim its overview's resource map and move on.

## How each pillar works

Every pillar folder has three layers:
1. **`00-overview.md`** — start here: why the pillar matters, the learning path through
   it, and a resource map pointing at every book/PDF (`readings/`), runnable course
   (repo folders), librarian wiki page, and cleaned note.
2. **Detailed notes** (`01-…`, `02-…`) — deep dives, added pillar-by-pillar over time.
3. **`interview-guide.md`** — the compressed exam-prep view: concepts, trade-offs, and a
   question bank with answer sketches. Read it *last*, as a self-test.

## The journey

| # | Pillar | You can now… | Prereqs |
|---|---|---|---|
| 0 | [Programming](0-programming/00-overview.md) | write clean, efficient code and solve DSA problems | Python |
| 1 | [Foundations](1-foundations/00-overview.md) | train, evaluate, and explain a classical ML model honestly | Python |
| 2 | [LLM Fundamentals](2-llm-fundamentals/00-overview.md) | build a tiny GPT; explain attention, RLHF, and prompting without hand-waving | 1 |
| 3 | [RAG](3-rag/00-overview.md) | build a document-QA system with citations and measure its faithfulness | 2 |
| 4 | [Agents](4-agents/00-overview.md) | build a tool-using, stateful agent and explain its harness | 3 |
| 5 | [Context & Cost](5-context-cost/00-overview.md) | budget tokens/latency and design a cached, compacted context | 4 |
| 6 | [Evals & Observability](6-evals-observability/00-overview.md) | stand up a golden set + judge + traces for anything you built | 3–5 |
| 7 | [Security & Safety](7-security-safety/00-overview.md) | threat-model an agent and layer real defenses | 4 |
| 8 | [Data Eng & MLOps](8-data-eng-mlops/00-overview.md) | ship a monitored pipeline and deploy a model with rollback | 1 |
| 9 | [System Design](9-system-design/00-overview.md) | design a whole LLM system aloud, trade-offs and all | 3–8 |
| 10 | [Product & Delivery](10-product-delivery/00-overview.md) | frame, cost, and deliver a project end to end — and explain it to a funder | any |

Pillars 1 and 8 can run in parallel; 9 and 10 are integrative — revisit them repeatedly.

**Coming pillars** (deferred): *Stats & Experimentation* (A/B testing, causal inference —
seed: `data-analytics/0-cross-stats/`).

## Other entry points

- Interview prep: [../README.md](../README.md) — role × topic matrix + the
  [rounds/](../rounds/) files (one per interview-round type).
- Raw sources: [../notes/](../notes/) (cleaned Notion notes) and the librarian wiki (compiled
  design experience; it scrapes this KB back in turn).
