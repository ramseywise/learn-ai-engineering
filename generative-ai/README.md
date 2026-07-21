# Generative AI

> **Depth domain.** This folder goes deep on the three pillars of generative AI.
> The [interviewing guides](../interviewing/guides/00-start-here.md) are the compressed
> summary layer — read those for exam prep. Read here for synthesis and depth.

---

## The three pillars

```
LLM fundamentals → RAG & retrieval → Agentic applications
```

The order encodes temporal emergence and dependency:

- **LLM fundamentals** — what these models are, how they're trained, how to prompt them.
  Everything else builds on this.
- **RAG & retrieval** — the first killer app pattern: augment a model with external
  knowledge at inference time. Presumes prompt fundamentals.
- **Agentic applications** — the current frontier: models that plan, use tools, and
  operate over multiple turns. Presumes both prior pillars.

---

## Pillar → interviewing-guide crosswalk

| Pillar | Depth (here) | Summary (guide) | Coursera repos | Seed notes |
|---|---|---|---|---|
| LLM fundamentals | [01-llm-fundamentals/](01-llm-fundamentals/README.md) | [2-llm-fundamentals](../interviewing/guides/2-llm-fundamentals/00-overview.md) | `nn-zero-to-hero`, `intro-to-nlp` | [prompt-engineering.md](../interviewing/notes/prompt-engineering.md), [rl.md](../interviewing/notes/rl.md) |
| RAG & retrieval | [02-rag-retrieval/](02-rag-retrieval/README.md) | [3-rag](../interviewing/guides/3-rag/00-overview.md) | `Deeplearning.ai-RAG-main`, `Knowledge_Graphs_for_RAG-main` | [rag.md](../interviewing/notes/rag.md), [graph-engineering.md](../interviewing/notes/graph-engineering.md) |
| Agentic applications | [03-agentic-applications/](03-agentic-applications/README.md) | [4-agents](../interviewing/guides/4-agents/00-overview.md) | AutoGen, LangGraph, AgenticAIFrameworks, Context-Engineering, agent-memory (2), internet-search-agent, LangFuse (3), Evaluating-AI-Agents | [agent-harness.md](../interviewing/notes/agent-harness.md), [deep-agents.md](../interviewing/notes/deep-agents.md), [loop-engineering.md](../interviewing/notes/loop-engineering.md), [reliable-agents.md](../interviewing/notes/reliable-agents.md) |

---

## Relationship to ai-engineering

These two folders are complementary, not redundant:

- **generative-ai/** is the **application wave** — building things with LLMs. It maps
  the course material, foundational papers, and practical patterns for using LLMs.
- **[ai-engineering/](../ai-engineering/README.md)** is the **discipline wave** — the
  engineering practices that make LLM applications reliable, observable, and maintainable.
  It emerged after the application wave and presumes it.

Temporal order: learn the three gen-AI pillars first; the ai-engineering foundations
(prompt → context → harness → loop → graph → eval) layer engineering discipline on top.

Cross-links from gen-AI pillars into ai-engineering:
- RAG patterns → ai-eng [02-context/](../ai-engineering/02-context/README.md) (context assembly) and [05-graph/](../ai-engineering/05-graph/README.md) (KG-for-RAG)
- Agentic patterns → ai-eng [03-harness/](../ai-engineering/03-harness/README.md), [04-loop/](../ai-engineering/04-loop/README.md), [06-eval/](../ai-engineering/06-eval/README.md)

---

## Content in this folder

- **`intro-to-nlp/`** — NLTK, TensorFlow, transformers, word-cloud, word2vec. See its own
  [README](intro-to-nlp/README.md).
- **`nn-zero-to-hero/`** — Karpathy's course: micrograd, makemore, nanogpt. See its own
  [README](nn-zero-to-hero/README.md).
- **`coursera-references/`** — 13 course-companion repos on agentic AI, extracted from what used to
  be a top-level `coursera/` folder of unopened zips: AutoGen design patterns, LangGraph agent
  courses, RAG (2), knowledge graphs for RAG, LangFuse eval/observability (3), agent memory (2),
  context engineering, evaluating AI agents, and an internet-search agent. 5 zips that were
  redundant mega-aggregations of the same material (one shipped a committed 438MB `venv/`) were
  deleted rather than extracted.
- **`chatbot/deep-research-bot/`** — the one genuinely active thing in the old chatbot grab-bag: a
  2025 agent-building workshop clone with its own `CLAUDE.md`/`AGENTS.md`, and real post-clone
  activity (eval scripts and a notebook edited well after the initial clone date). Several older,
  never-revisited demo clones (`HubermanGPT`, `buddha-gpt`, ~6 more reference chatbot examples) were
  deleted.

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
