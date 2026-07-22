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
  post-pretraining. Covers six topic areas: RL foundations, RLHF pipeline, preference
  optimization algorithms (PPO/DPO/GRPO), reward modeling, constitutional AI/RLAIF,
  and RL for agentic systems. Includes a curriculum with resource map and gap analysis.
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

## TypeScript Examples

**What exists:** `01-llm-fundamentals/typescript/` — 4 self-contained Anthropic SDK examples
covering the core API patterns: basic message creation + streaming (`01-api-call.ts`), structured
JSON output via forced tool use (`02-structured-output.ts`), multi-tool agentic loop with dispatch
(`03-function-calling.ts`), and conversation history / multi-turn REPL (`04-multi-turn.ts`).
See [`01-llm-fundamentals/typescript/README.md`](01-llm-fundamentals/typescript/README.md) for
setup and running instructions.

**Gaps — no TypeScript examples in pillars 02–07:**

| Pillar | Python coverage | TypeScript gap |
|---|---|---|
| 02 — RAG & retrieval | DeepLearning.AI RAG notebooks | No TS RAG example (Vercel AI SDK + vector store pattern missing) |
| 03 — Agentic foundations | AutoGen, LangGraph, ADK course repos | No TS agent example (LangGraph.js or Vercel AI SDK agent loop missing) |
| 04 — Agentic frameworks | LangGraph notebooks, ADK notes | No TS framework example |
| 05 — RL & alignment | RLHF readings | Not applicable (no runnable code for either language) |
| 06 — Observability | LangFuse Python SDK repos | No TS observability example (LangFuse JS SDK missing) |
| 07 — Agentic applications | Python internet-search agent, deep-research bot | No TS application |

**Priority additions (if filling the gap):**
1. Pillar 02: a minimal RAG example using Vercel AI SDK + Anthropic + an in-memory vector store — the JS/TS equivalent of the Python RAG pattern is the highest-value addition given Vercel AI SDK is in active use.
2. Pillar 03/04: a tool-using agent loop in LangGraph.js or Vercel AI SDK — directly parallels the Python LangGraph course material.
3. Pillar 06: LangFuse JS SDK tracing example — low effort, high value for observability coverage.

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
