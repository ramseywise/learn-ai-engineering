# Interviewing KB

Interview-prep knowledge base for ML / AI-engineering / DS / FDE roles. Three layers:

1. **[Study guides](#study-guides)** (`guides/`) — compiled topic summaries: core concepts,
   trade-offs, common questions with answer sketches. Each ends with a `Sources:` section
   pointing at the material it was compiled from.
2. **[Interview rounds](#interview-rounds)** (`rounds/`) — one file per round type: what's
   tested, format and current trends, prep checklist, question bank, per-role weighting.
3. **Sources** — [`notes/`](notes/) (cleaned Notion notes with provenance frontmatter),
   [`images/`](images/), the [readings library](../generative-ai/readings/README.md)
   (local-only PDFs), this repo's course folders, and the librarian wiki (public domains),
   which also scrapes this KB back into its own knowledge graph.

**How to use:** pick your target role in the matrix below → work the ● topics via their
study guides → then prep each round you're facing from `rounds/`.

## Role × topic matrix

Roles: **AIE** (AI/agent engineer), **MLE** (ML engineer), **DS** (data scientist),
**FDE** (forward-deployed / applied AI engineer). ● core ◐ secondary ○ awareness.

| Topic → guide | AIE | MLE | DS | FDE |
|---|---|---|---|---|
| [LLM fundamentals](guides/llm-fundamentals.md) | ● | ● | ◐ | ● |
| [RAG](guides/rag.md) | ● | ◐ | ○ | ● |
| [Agents](guides/agents.md) | ● | ◐ | ○ | ● |
| [Evals & observability](guides/evals-observability.md) | ● | ● | ◐ | ● |
| [Security & safety](guides/security-safety.md) | ● | ◐ | ○ | ● |
| [Context engineering & cost](guides/context-engineering-cost.md) | ● | ◐ | ○ | ◐ |
| [ML foundations](guides/ml-foundations.md) (incl. SQL/analytics) | ◐ | ● | ● | ○ |
| [Data engineering & MLOps](guides/data-engineering-mlops.md) | ◐ | ● | ◐ | ◐ |
| [System design](guides/system-design.md) | ● | ● | ◐ | ● |
| [Product & business sense](guides/product-business.md) | ◐ | ○ | ● | ● |
| Stats & experimentation — *deferred (see below)* | ○ | ◐ | ● | ○ |
| Coding patterns / DS&A — *deferred (see below)* | ◐ | ◐ | ◐ | ◐ |

**Deferred topics** (separate milestone): stats/experimentation (seed material:
`readings/stats_recs/`) and coding patterns (seed: `programming/Leet-Code/`).

## Study guides

| Guide | One-liner |
|---|---|
| [llm-fundamentals](guides/llm-fundamentals.md) | Transformers, tokenization, fine-tuning, RLHF — the theory round |
| [rag](guides/rag.md) | Architectures, chunking, reranking, eval — the default enterprise pattern |
| [agents](guides/agents.md) | Orchestration, memory, tools/MCP, harness engineering, multi-agent |
| [evals-observability](guides/evals-observability.md) | Graders, capability vs regression, tracing, online sampling |
| [security-safety](guides/security-safety.md) | Prompt injection, guardrails, PII, compliance |
| [context-engineering-cost](guides/context-engineering-cost.md) | Caching, compaction, context rot, cost/latency budgets |
| [ml-foundations](guides/ml-foundations.md) | Classical ML, DL basics, metrics, SQL/analytics screens |
| [data-engineering-mlops](guides/data-engineering-mlops.md) | Pipelines, orchestration, deployment, monitoring |
| [system-design](guides/system-design.md) | The design-round method: clarify → trade-offs → iterate |
| [product-business](guides/product-business.md) | ROI framing, product sense, nonprofit/enterprise constraints |

## Interview rounds

| Round | Covers |
|---|---|
| [recruiter-screen](rounds/recruiter-screen.md) | Narrative, logistics, comp framing |
| [coding-challenge](rounds/coding-challenge.md) | Live coding, debugging rounds, pair programming (AI-assisted) |
| [technical-questions](rounds/technical-questions.md) | ML/LLM breadth & theory rapid-fire |
| [system-design-round](rounds/system-design-round.md) | ML/LLM/agent system design interviews |
| [code-review-round](rounds/code-review-round.md) | Reviewing unfamiliar code under observation |
| [case-study](rounds/case-study.md) | Live + take-home cases, presentation/defense |
| [project-deep-dive](rounds/project-deep-dive.md) | Walking through your own systems |
| [behavioral](rounds/behavioral.md) | STAR stories, failure questions, collaboration |
| [customer-simulation](rounds/customer-simulation.md) | FDE stakeholder role-play, ambiguous-client scenarios |
| [leadership-rounds](rounds/leadership-rounds.md) | CTO / head-of-product conversations + reverse interview |

## Maintenance

- New raw material → `notes/` with provenance frontmatter (`origin`, `confidence`, `sources`, `cleaned`).
- Guides cite sources by repo path + librarian wiki page title (compile-and-cite; no `wiki/private/` content).
- Librarian scrapes `interviewing/**/*.md` into its `raw/repos/` tier — keep guides self-contained.
