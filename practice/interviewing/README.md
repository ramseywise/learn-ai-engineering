# Interviewing KB

Interview-prep knowledge base for ML / AI-engineering / DS / FDE roles. The teaching lives in the
curriculum; this folder is the recall and round prep. [`../CROSSWALK.md`](../CROSSWALK.md) maps each
curriculum unit to the guides and drills that test it. Three layers:

1. **[Curriculum pillars](guides/00-start-here.md)** (`guides/`) — twelve numbered pillar
   folders, each with a `00-overview.md` (links to the curriculum chapters that teach the pillar)
   and an `interview-guide.md` (the recall sheet: concepts, trade-offs, question bank with answer
   sketches, `Sources:` footer).
2. **[Interview rounds](#interview-rounds)** (`rounds/`) — one file per round type: what's
   tested, format and current trends, prep checklist, question bank, per-role weighting.
3. **Sources**: the [curriculum](../../README.md) and the librarian wiki (public domains), which
   also scrapes this KB back into its own knowledge graph.

**How to use:** learning from scratch → [guides/00-start-here.md](guides/00-start-here.md).
Interview prep → pick your target role in the matrix below → work the ● topics via their
interview guides → then prep each round you're facing from `rounds/`.

## Role × topic matrix

Roles: **AIE** (AI/agent engineer), **MLE** (ML engineer), **DS** (data scientist),
**FDE** (forward-deployed / applied AI engineer). ● core ◐ secondary ○ awareness.

| Topic → guide | AIE | MLE | DS | FDE |
|---|---|---|---|---|
| [LLM fundamentals](guides/2-llm-fundamentals/interview-guide.md) | ● | ● | ◐ | ● |
| [RAG](guides/3-rag/interview-guide.md) | ● | ◐ | ○ | ● |
| [Agents](guides/4-agents/interview-guide.md) | ● | ◐ | ○ | ● |
| [Evals & observability](guides/6-evals-observability/interview-guide.md) | ● | ● | ◐ | ● |
| [Security & safety](guides/7-security-safety/interview-guide.md) | ● | ◐ | ○ | ● |
| [Context engineering & cost](guides/5-context-cost/interview-guide.md) | ● | ◐ | ○ | ◐ |
| [ML foundations](guides/1-foundations/interview-guide.md) (incl. SQL/analytics) | ◐ | ● | ● | ○ |
| [Data engineering & MLOps](guides/8-data-eng-mlops/interview-guide.md) | ◐ | ● | ◐ | ◐ |
| [System design](guides/9-system-design/interview-guide.md) | ● | ● | ◐ | ● |
| [Product & business sense](guides/10-product-delivery/interview-guide.md) | ◐ | ○ | ● | ● |
| [Stats & experimentation](guides/11-stats-experimentation/interview-guide.md) | ○ | ◐ | ● | ○ |
| Coding patterns / DS&A — [drills](../drills/README.md) | ◐ | ◐ | ◐ | ◐ |

**Analyst or data engineer?** The matrix has no column for them. Analysts: treat stats, the metrics
and SQL parts of ML foundations, and product sense as ●. Data engineers: treat data engineering and
SQL as ●. The [foundations guide](guides/1-foundations/interview-guide.md#0-three-jobs-and-what-each-is-interviewed-on)
compares the jobs.

## Study guides

| Guide | One-liner |
|---|---|
| [llm-fundamentals](guides/2-llm-fundamentals/interview-guide.md) | Transformers, tokenization, fine-tuning, RLHF — the theory round |
| [rag](guides/3-rag/interview-guide.md) | Architectures, chunking, reranking, eval — the default enterprise pattern |
| [agents](guides/4-agents/interview-guide.md) | Orchestration, memory, tools/MCP, harness engineering, multi-agent |
| [evals-observability](guides/6-evals-observability/interview-guide.md) | Graders, capability vs regression, tracing, online sampling |
| [security-safety](guides/7-security-safety/interview-guide.md) | Prompt injection, guardrails, PII, compliance |
| [context-engineering-cost](guides/5-context-cost/interview-guide.md) | Caching, compaction, context rot, cost/latency budgets |
| [ml-foundations](guides/1-foundations/interview-guide.md) | The three data jobs, classical ML, metrics, drift, SQL/analytics screens, and answers to the 18 ML Fundamentals questions |
| [stats-experimentation](guides/11-stats-experimentation/interview-guide.md) | Distributions, intervals, tests, power, regression, A/B design, CUPED, peeking, Bayesian A/B |
| [data-engineering-mlops](guides/8-data-eng-mlops/interview-guide.md) | Pipelines, orchestration, deployment, monitoring |
| [system-design](guides/9-system-design/interview-guide.md) | The design-round method: clarify → trade-offs → iterate |
| [product-business](guides/10-product-delivery/interview-guide.md) | ROI framing, product sense, nonprofit/enterprise constraints |

## Interview rounds

| Round | Covers |
|---|---|
| [recruiter-screen](rounds/recruiter-screen/README.md) | Narrative, logistics, comp framing |
| [coding-challenge](rounds/coding-challenge/README.md) | Live coding, debugging rounds, pair programming (AI-assisted) |
| [technical-questions](rounds/technical-questions/README.md) | ML/LLM breadth & theory rapid-fire |
| [system-design-round](rounds/system-design-round/README.md) | ML/LLM/agent system design interviews |
| [code-review-round](rounds/code-review-round/README.md) | Reviewing unfamiliar code under observation |
| [case-study](rounds/case-study/README.md) | Live + take-home cases, presentation/defense |
| [project-deep-dive](rounds/project-deep-dive/README.md) | Walking through your own systems |
| [behavioral](rounds/behavioral/README.md) | STAR stories, failure questions, collaboration |
| [customer-simulation](rounds/customer-simulation/README.md) | FDE stakeholder role-play, ambiguous-client scenarios |
| [leadership-rounds](rounds/leadership-rounds/README.md) | CTO / head-of-product conversations + reverse interview |

## Maintenance

**The split rule** — *"Is this true regardless of whether I'm being interviewed?"*
Yes → `guides/`. No → `rounds/`. "Separate read and write tools" is true at work → guide.
"Draw the architecture in under 3 minutes" is only true in an interview → round. Nothing
lands in a round folder just because it was useful for that round.

**Strip the preamble on ingest** — content starts at the `#`. Anything the model said
*about* the notes ("here are condensed notes in the same style…") goes in `sources:`, not
above the first heading. Same for scraped page chrome.

- Guide and round files carry provenance frontmatter (`origin`, `confidence`, `sources`, `cleaned`) and
  `units:` where the mapping to the curriculum is clear.
- New files stay local until added to the allowlist in `practice/.gitignore`.
- Guides cite sources by repo path + librarian wiki page title (compile-and-cite; no `wiki/private/` content).
- Librarian scrapes `practice/interviewing/**/*.md` into its `raw/repos/` tier — keep guides self-contained.
