---
origin: curated
sources:
  - ../resources.md (section "06 — Observability and evals", copied 2026-10-31)
  - https://github.com/pedroalexleite/Learning-LangFuse
  - https://github.com/gustavobrieva1/langfuse-evaluation
  - https://github.com/Log-LogN/langfuse-mcp-python
confidence: high
cleaned: 2026-11-01
---
# References — Observability

> Every source the notes cite, mapped to notes. **★** = read first. Eval-methodology sources live in [generative-ai/08-eval/references.md](../08-eval/references.md) and are not repeated here.

---

## Books

No book has a chapter on LLM observability that this pillar relies on. These two free chapters supply the general discipline note 06 applies.

| | Book, chapter | Cost | Notes | Use it for |
|---|---|---|---|---|
| ★ | Beyer, Jones, Petoff, Murphy (eds), *Site Reliability Engineering*, [ch 6 Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) | Free online | 06 | The four golden signals (latency, traffic, errors, saturation), and why tails matter more than means |
| | Beyer, Murphy, Rensin, Kawahara, Thorne (eds), *The Site Reliability Workbook*, [ch 5 Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) | Free online | 06 | Turning a target into an alert, the next step after note 06's threshold replay |

## Core papers

| | Paper | Notes | Why |
|---|---|---|---|
| ★ | Dong, Lu, Zhu, [*A Taxonomy of AgentOps for Enabling Observability of Foundation Model based Agents*](https://arxiv.org/abs/2411.05285), 2024. PDF in [sources/](sources/dong-2024-agentops.pdf) | [01](notes/01-tracing-with-langfuse.md), [05](notes/05-support-agent-observability.md), [06](notes/06-cost-and-latency-dashboards.md) | Reviews 17 tools and proposes the artefacts a trace should hold. A preprint, and the taxonomy is not validated |

## AI Papers of the Week

| Paper | Notes | Status |
|---|---|---|
| Dong, Lu, Zhu, *A Taxonomy of AgentOps*, above | 01, 05, 06 | Read in full and cited in those notes. The DAIR list is where it entered the ledger |

## Courses and videos

Free unless marked. None is required: `practice/` needs no account or key.

| Course | Platform, cost | Where | Notes | Use it for |
|---|---|---|---|---|
| ★ Langfuse Academy | Langfuse, free docs | [academy](https://langfuse.com/academy), start at [tracing](https://langfuse.com/academy/tracing) and [monitoring](https://langfuse.com/academy/monitoring) | 01, 02, 06 | The vendor's account of the loop, with the hosted UI this pillar replaces with fakes |
| *Introduction to LangSmith* | LangChain Academy, free | [course](https://academy.langchain.com/courses/intro-to-langsmith) | 01, 02 | The same ideas on the alternative platform; pairs with [04-agentic-frameworks 05](../04-agentic-frameworks/notes/05-langsmith.md) |
| *Evaluating AI Agents* | DeepLearning.AI with Arize AI, free during the platform beta | [course](https://www.deeplearning.ai/short-courses/evaluating-ai-agents/) | 01, 02, 03 | Tracing, then evaluating, one agent end to end on a different tool |
| *Automated Testing for LLMOps* | DeepLearning.AI, free during the platform beta | [course](https://www.deeplearning.ai/short-courses/automated-testing-llmops/) | 02 | Putting a release gate in CI |
| *Quality and Safety for LLM Applications* | DeepLearning.AI, free during the platform beta | [course](https://www.deeplearning.ai/short-courses/quality-safety-llm-applications/) | 01, 05 | Online heuristics for injection, leakage and refusals |

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
| | Langfuse [token and cost tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking), [Metrics API](https://langfuse.com/docs/metrics/features/metrics-api) | 06 |
| | Langfuse [native MCP server](https://langfuse.com/docs/api-and-data-platform/features/mcp-server) | 04 |
| | Anthropic [pricing](https://platform.claude.com/docs/en/about-claude/pricing), [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | 01, 06 |
| | [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | 01 |

## From the subject reading list

Copied from `generative-ai/resources.md` (retired 2026-10-31), section *06 — Observability and evals*, on 2026-10-31.

| | Source | Notes |
|---|---|---|
| ★ | [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (Anthropic) | 02, 03, 05, 06 |
| | [Langfuse docs](https://langfuse.com/docs): the tool this pillar's three course repos use | 01–06 |
| | [Promptfoo](https://www.promptfoo.dev/docs/) · [Ragas](https://docs.ragas.io/) · [OpenAI Evals](https://github.com/openai/evals) | 02, 03 |
| | Serving: [vLLM](https://docs.vllm.ai/) · [LiteLLM](https://docs.litellm.ai/) | Further reading, not cited in a note |
| | Security: [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) | 04 |

## Source quality

| Source | Flag |
|---|---|
| Learning-LangFuse results | n=20, one judge sample per item, judge is the 8B baseline model. Read as a method demo, not a model comparison |
| langfuse-evaluation cost figure (~$3.70 per 1k conversations) | Author's estimate for Gemini Flash/Pro pricing at the time; recompute for current prices |
| Note 05 | Adapted from own reference specs for a support-agent eval platform; file paths in them are that project's and illustrative here |
| All numbers from the fortnight (notes 01–06) | Synthetic traces and rule-based judge stubs from `practice/`. They show how methods behave, not how a real agent performs |
