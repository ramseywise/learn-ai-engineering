# Generative AI

LLM/NLP fundamentals and a curated set of agentic-AI course repos.

## Finished / organized

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
