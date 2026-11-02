# Start Here — the AI Engineering Journey

A step-by-step route through the curriculum for interview prep: twelve pillars, ordered so each
builds on the last. Written for someone starting from (almost) zero. If you already know a pillar,
skip to its interview guide.

## How each pillar works

Every pillar folder has two files:

1. **`00-overview.md`**: why the pillar matters, and links to the curriculum chapters that teach it,
   in order.
2. **`interview-guide.md`**: the recall sheet: concepts, trade-offs, and a question bank with answer
   sketches. Read it *last*, as a self-test.

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
| 11 | [Stats & Experimentation](11-stats-experimentation/00-overview.md) | design an A/B test, read its result honestly, and say what a p-value doesn't mean | Python |

Pillars 1 and 8 can run in parallel; 9 and 10 are integrative — revisit them repeatedly. Pillar 11
runs alongside pillar 1, and comes first for analyst and data science roles despite its number.
Aiming for a data job rather than AI engineering? Start with
[pillar 1's overview](1-foundations/00-overview.md), which sets out a path for analysts, scientists
and engineers.

## Other entry points

- Interview prep: [../README.md](../README.md) has the role × topic matrix and the
  `rounds/` folders, one per interview-round type.
- The curriculum: [CURRICULUM.md](../../../CURRICULUM.md).
