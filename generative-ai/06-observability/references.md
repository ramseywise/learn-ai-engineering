---
origin: curated
sources:
  - ../resources.md (section "06 — Observability and evals", copied 2026-10-31)
  - https://github.com/pedroalexleite/Learning-LangFuse
  - https://github.com/gustavobrieva1/langfuse-evaluation
  - https://github.com/Log-LogN/langfuse-mcp-python
confidence: high
cleaned: 2026-10-31
---
# References — Observability

> Every source the notes cite, mapped to notes. **★** = read first. Eval-methodology sources live in [ai-engineering/06-eval/references.md](../../ai-engineering/06-eval/references.md) and are not repeated here.

---

## Projects (condensed into the notes)

| | Source | Licence | Notes |
|---|---|---|---|
| ★ | Pedro Leite, [*Learning-LangFuse*](https://github.com/pedroalexleite/Learning-LangFuse): healthcare chatbot, golden dataset (20 Q&A, 8 categories), LLM-as-judge, dataset runs, embedding similarity, traced single and multi-agent | MIT (README badge) | [02](notes/02-scoring-datasets-experiments.md) |
| | gustavobrieva1, [*langfuse-evaluation*](https://github.com/gustavobrieva1/langfuse-evaluation): multi-agent judge pipeline over exported Langfuse traces for a banking assistant | README: "Internal use only". Only the generic architecture and schemas are condensed; no prompts, data or results reproduced | [03](notes/03-judge-pipelines-over-trace-exports.md) |
| | Log-LogN, [*langfuse-mcp-python*](https://github.com/Log-LogN/langfuse-mcp-python) v1.0.0: 34-tool MCP server over the Langfuse API | MIT, © 2026 LogLogN | [04](notes/04-langfuse-mcp-server.md) |

## Platform docs

| | Source | Notes |
|---|---|---|
| ★ | [Langfuse docs](https://langfuse.com/docs): [Python decorators](https://langfuse.com/docs/sdk/python/decorators), [LangChain/LangGraph tracing](https://langfuse.com/docs/integrations/langchain/tracing), [datasets](https://langfuse.com/docs/evaluation/dataset-runs/datasets), [LLM-as-judge](https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge), [export](https://langfuse.com/docs/api-and-data-platform/features/export-from-ui), [public API](https://langfuse.com/docs/api-and-data-platform/features/public-api), [self-hosting](https://langfuse.com/docs/self-hosting/docker-compose) | 01–05 |
| | [Model Context Protocol](https://modelcontextprotocol.io/) | 04 |

## From the subject reading list

Copied from `generative-ai/resources.md` (retired 2026-10-31), section *06 — Observability and evals*, on 2026-10-31.

| | Source | Notes |
|---|---|---|
| ★ | [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (Anthropic) | 02, 03 |
| | [Langfuse docs](https://langfuse.com/docs): the tool this pillar's three course repos use | 01–05 |
| | [Promptfoo](https://www.promptfoo.dev/docs/) · [Ragas](https://docs.ragas.io/) · [OpenAI Evals](https://github.com/openai/evals) | 02, 03 |
| | Serving: [vLLM](https://docs.vllm.ai/) · [LiteLLM](https://docs.litellm.ai/) | — |
| | Security: [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) | 04 |

## Source quality

| Source | Flag |
|---|---|
| Learning-LangFuse results | n=20, one judge sample per item, judge is the 8B baseline model. Read as a method demo, not a model comparison |
| langfuse-evaluation cost figure (~$3.70 per 1k conversations) | Author's estimate for Gemini Flash/Pro pricing at the time; recompute for current prices |
| Notes 01 and 05 | Own reference specs for a support-agent eval platform; file paths in them are that project's and illustrative here |
