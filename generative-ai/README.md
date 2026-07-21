# Generative AI

> **Depth domain.** This folder goes deep on the seven pillars of generative AI.
> The [interviewing guides](../interviewing/guides/00-start-here.md) are the compressed
> summary layer — read those for exam prep. Read here for synthesis and depth.

---

## The seven pillars

```
LLM fundamentals → RAG & retrieval → Agentic foundations → Agentic frameworks
                                    → RL & alignment
                                    → Observability
                                    → Agentic applications
```

The order encodes dependency and temporal emergence:

- **LLM fundamentals** — what these models are, how they're trained, how to prompt them.
  Everything else builds on this.
- **RAG & retrieval** — the first killer app pattern: augment a model with external
  knowledge at inference time. Presumes prompt fundamentals.
- **Agentic foundations** — framework learning: LangGraph, ADK, AutoGen courses.
  Models that plan, use tools, and operate in loops.
- **Agentic frameworks** — framework reference material: comparison docs, selection
  guides. Use after foundations to choose and configure the right tool.
- **RL & alignment** — reinforcement learning and RLHF: how models are aligned
  post-pretraining. Large and growing field; currently reference-heavy.
- **Observability** — LangFuse and related tooling: tracing, scoring, and evaluation
  pipelines for LLM applications.
- **Agentic applications** — specific projects built with the frameworks: an
  internet-search agent and a deep-research bot.

---

## Pillar → interviewing-guide crosswalk

| Pillar | Depth (here) | Summary (guide) |
|---|---|---|
| LLM fundamentals | [01-llm-fundamentals/](01-llm-fundamentals/README.md) | [2-llm-fundamentals](../interviewing/guides/2-llm-fundamentals/00-overview.md) |
| RAG & retrieval | [02-rag-retrieval/](02-rag-retrieval/README.md) | [3-rag](../interviewing/guides/3-rag/00-overview.md) |
| Agentic foundations | [03-agentic-foundations/](03-agentic-foundations/README.md) | [4-agents](../interviewing/guides/4-agents/00-overview.md) |
| Agentic frameworks | [04-agentic-frameworks/](04-agentic-frameworks/README.md) | [4-agents](../interviewing/guides/4-agents/00-overview.md) |
| RL & alignment | [05-RL/](05-RL/README.md) | [2-llm-fundamentals](../interviewing/guides/2-llm-fundamentals/00-overview.md) |
| Observability | [06-observability/](06-observability/README.md) | [4-agents](../interviewing/guides/4-agents/00-overview.md) |
| Agentic applications | [07-agentic-applications/](07-agentic-applications/README.md) | [4-agents](../interviewing/guides/4-agents/00-overview.md) |

---

## Relationship to ai-engineering

These two folders are complementary, not redundant:

- **generative-ai/** is the **application wave** — building things with LLMs. It maps
  the course material, foundational papers, and practical patterns for using LLMs.
- **[ai-engineering/](../ai-engineering/README.md)** is the **discipline wave** — the
  engineering practices that make LLM applications reliable, observable, and maintainable.
  It emerged after the application wave and presumes it.

Temporal order: learn the gen-AI pillars first; the ai-engineering foundations
(prompt → context → harness → loop → graph → eval) layer engineering discipline on top.

Cross-links from gen-AI pillars into ai-engineering:

| gen-AI pillar | ai-engineering depth |
|---|---|
| 01 LLM fundamentals | [01-prompt/](../ai-engineering/01-prompt/README.md) — prompt engineering |
| 02 RAG & retrieval | [02-context/](../ai-engineering/02-context/README.md) + [05-graph/](../ai-engineering/05-graph/README.md) |
| 03-04 Agentic foundations + frameworks | [03-harness/](../ai-engineering/03-harness/README.md) + [04-loop/](../ai-engineering/04-loop/README.md) |
| 06 Observability | [06-eval/](../ai-engineering/06-eval/README.md) — evaluation and measurement |

---

## Removed

Earlier versions of this README described `mcp-server-template/`, `mcp/`, `chatbot/berlin/`,
and `chatbot/BERT/`. None of these were ever committed to this repo, and none remain on disk —
they are not recoverable from git history. Recorded here because this README is the only
surviving description of them:

- `mcp-server-template/` — a generic FastMCP server template (env-var token auth → MCP tools),
  extracted from a personal integration against a SaaS API.
- `mcp/` — the original vendor-tied accounting-API integration that the template came from.
- `chatbot/BERT/` — appeared to be real production work (AWS Lambda deployment code) rather
  than course material.
- `chatbot/berlin/` — a reference chatbot clone.

`chatbot/deep_research_bench/` is still present and untouched.
