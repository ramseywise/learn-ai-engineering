# Generative AI

LLM/NLP fundamentals, a reusable MCP server pattern, reference papers, and a curated set of
agentic-AI course repos.

## Finished / organized

- **`intro-to-nlp/`** — NLTK, TensorFlow, transformers, word-cloud, word2vec. See its own
  [README](intro-to-nlp/README.md).
- **`nn-zero-to-hero/`** — Karpathy's course: micrograd, makemore, nanogpt. See its own
  [README](nn-zero-to-hero/README.md).
- **`mcp-server-template/`** — a generic FastMCP server template (env-var token auth → MCP tools),
  extracted from a real personal integration against a SaaS API. Swap in your own base URL/token/
  endpoints to reuse the pattern. See its own [README](mcp-server-template/README.md).
- **`readings/`** — reference papers: *Attention Is All You Need*, WaveNet, batch normalization, and
  others. No notes, pure reference.
- **`coursera-references/`** — 13 course-companion repos on agentic AI, extracted from what used to
  be a top-level `coursera/` folder of unopened zips: AutoGen design patterns, LangGraph agent
  courses, RAG (2), knowledge graphs for RAG, LangFuse eval/observability (3), agent memory (2),
  context engineering, evaluating AI agents, and an internet-search agent. 5 zips that were
  redundant mega-aggregations of the same material (one shipped a committed 438MB `venv/`) were
  archived rather than extracted.
- **`chatbot/deep-research-bot/`** — the one genuinely active thing in the old chatbot grab-bag: a
  2025 agent-building workshop clone with its own `CLAUDE.md`/`AGENTS.md`, and real post-clone
  activity (eval scripts and a notebook edited well after the initial clone date). Several older,
  never-revisited demo clones (`HubermanGPT`, `buddha-gpt`, ~6 more reference chatbot examples) were
  archived.

## Not part of this showcase

- `mcp/` — the original vendor-tied accounting-API integration, superseded by
  `mcp-server-template/`. Left as-is, out of scope.
- `chatbot/berlin/`, `chatbot/BERT/`, `chatbot/deep_research_bench/` — left untouched, permissions
  unchanged. `BERT/` in particular looks like real production work (AWS Lambda deployment code), not
  course material — flagged for your own review, not characterized further or moved.
