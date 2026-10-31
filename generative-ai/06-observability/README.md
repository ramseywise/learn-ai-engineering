# 06 — Observability

> Depth layer. Summary: [interviewing/guides/6-evals-observability](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/6-evals-observability/00-overview.md)
> Position: sixth generative-ai pillar, the tooling layer. It sits after the agent and model pillars ([04](../04-agentic-frameworks/README.md), [05](../05-RL/README.md)) and before shipping them ([07](../07-agentic-applications/README.md)). Eval theory is in [ai-engineering/06-eval](../../ai-engineering/06-eval/README.md).

---

## What it is

Observability for LLM applications means you can see what happened inside a run: which tools were called, what the model received and returned, how long each step took and what it cost, and whether the output was any good. This pillar is the hands-on tooling for that, with Langfuse as the main platform and LangSmith as the alternative.

> **Observability is the infrastructure; eval is the discipline.** The questions you can answer about an agent next month are fixed by what you log today.

The pillar follows one data model, trace → span → score and dataset → run, through four uses:

- tracing an agent turn
- scoring traces and comparing model versions on a golden dataset
- running a pipeline of specialised judges over exported production traces
- letting an agent query its own traces through MCP

A worked support-agent example closes it: the schema contract a real two-framework system logs.

What a good grader is, how to calibrate a judge, and how to read a result with n=20 are covered in [ai-engineering/06-eval](../../ai-engineering/06-eval/README.md). The notes here link to that pillar and don't repeat it.

---

## Start here

1. Read notes 01–04 in order: trace, score, judge at scale, query.
2. Read 05 as the worked example of 01–04 applied to one system.
3. For the theory behind any score here, follow the links into [ai-engineering/06-eval](../../ai-engineering/06-eval/README.md).
4. Keep the [rules of thumb](#rules-of-thumb) as the one-page summary.

## Layout

```
README.md      this file: overview, start here, syllabus, rules of thumb, resource map
references.md  every source the notes cite, mapped to notes, with licences
notes/         01–05, the course; code inline
```

---

## Syllabus

| # | Note | Covers |
|---|---|---|
| 1 | [Tracing with Langfuse](notes/01-tracing-with-langfuse.md) | Trace with child spans, the `ContextVar` pattern for tools, per-framework wiring, `@observe` and `CallbackHandler`, OTEL, post-hoc scores and score keys, datasets and runs, annotation queues, remote prompts |
| 2 | [Scoring, datasets and experiments](notes/02-scoring-datasets-experiments.md) | Langfuse eval data model; golden dataset; judge in a loop vs dataset runs vs managed evaluators; embedding similarity; reading a two-model comparison by category; tracing single and multi-agent trajectories |
| 3 | [Judge pipelines over trace exports](notes/03-judge-pipelines-over-trace-exports.md) | ETL from exported traces; four parallel judges (relevance, hallucination, completeness, escalation); gated verification; evidence-first hallucination schema; lenient vs strict judge A/B; cost |
| 4 | [A Langfuse MCP server](notes/04-langfuse-mcp-server.md) | Transports and client config; server architecture (cache, retries, rate limit, pagination); the 34 tools and which ones write; least-privilege rules; workflows |
| 5 | [Support agent observability (worked example)](notes/05-support-agent-observability.md) | What to record in a trace, base trace metadata, `ExperimentRun` / `RagConfig` / `BedrockConfig` / `ChunkRecord`, coverage table, grounding-tier promotion policy, implementation state |

## Rules of thumb

| Rule | Note |
|---|---|
| One trace per agent turn, one child span per tool call | [01](notes/01-tracing-with-langfuse.md) |
| Carry the active trace into tools with a `ContextVar`, reset in `finally` | [01](notes/01-tracing-with-langfuse.md) |
| Put agent name, framework and version in trace metadata from day one | [01](notes/01-tracing-with-langfuse.md), [04](notes/04-langfuse-mcp-server.md), [05](notes/05-support-agent-observability.md) |
| Name every dataset run after the system version it tests | [02](notes/02-scoring-datasets-experiments.md) |
| Slice by category before trusting an average; a small average gain can hide a safety regression | [02](notes/02-scoring-datasets-experiments.md) |
| Embedding similarity can't see a refusal regression; don't use it alone | [02](notes/02-scoring-datasets-experiments.md) |
| One judge per failure mode, so each score maps to one fix | [03](notes/03-judge-pipelines-over-trace-exports.md) |
| Evidence before verdict; recompute the verdict from the evidence | [03](notes/03-judge-pipelines-over-trace-exports.md) |
| Spend the strong judge only on positives | [03](notes/03-judge-pipelines-over-trace-exports.md) |
| Give agents read-only, project-scoped keys to observability tools | [04](notes/04-langfuse-mcp-server.md) |
| Scrub PII before anything reaches an external grader or a trace | [04](notes/04-langfuse-mcp-server.md), [05](notes/05-support-agent-observability.md) |

---

## Resource map

### Related notes elsewhere
- Eval theory: [ai-engineering/06-eval](../../ai-engineering/06-eval/README.md), especially [05 LLM-as-judge](../../ai-engineering/06-eval/notes/05-llm-as-judge.md), [07 evaluating RAG and grounding](../../ai-engineering/06-eval/notes/07-evaluating-rag-and-grounding.md), [08 tracing and observability](../../ai-engineering/06-eval/notes/08-tracing-and-observability.md) and [13 case study: support agent](../../ai-engineering/06-eval/notes/13-case-study-support-agent.md).
- LangSmith, the alternative platform: [04-agentic-frameworks 05](../04-agentic-frameworks/notes/05-langsmith.md).
- MCP as a protocol: [ai-engineering/02-context-engineering 09](../../ai-engineering/02-context-engineering/notes/09-protocols.md).

### Books and courses
- *Learning-LangFuse* (healthcare chatbot evaluation project) → note 02.
- *langfuse-evaluation* (judge pipeline over production traces) → note 03, generic design only.
- *langfuse-mcp-python* (MCP server) → note 04.
- Full citations, upstream repos and licences: [references.md](references.md).

### Coursework and practice
The three repos were condensed into the notes and removed. Each note ends with a **Labs** table linking upstream:

| Lab | Note | Runs |
|---|---|---|
| Judge, dataset runs, embedding similarity | [02](notes/02-scoring-datasets-experiments.md#labs) | Needs Docker (self-hosted Langfuse) and `GROQ_API_KEY_1`; embeddings and agents need `GEMINI_API_KEY` |
| Judge pipeline over trace exports | [03](notes/03-judge-pipelines-over-trace-exports.md) | Upstream is internal-use; rebuild from the note's code against your own exports. Needs a Gemini/Vertex key |
| Langfuse MCP server | [04](notes/04-langfuse-mcp-server.md#labs) | Needs a Langfuse project and keys; Python ≥ 3.11 |

### Readings
- Langfuse docs, Anthropic's evals post, Promptfoo, Ragas, OpenAI Evals, serving and security links: [references.md](references.md).

### Interviewing guide
- [6-evals-observability](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/6-evals-observability/00-overview.md): compressed summary for interview prep.

### Previous and next layer
← [05-RL](../05-RL/README.md)
→ [07-agentic-applications](../07-agentic-applications/README.md): projects that ship the agents traced and scored here.
