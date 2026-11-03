# 06 — Observability

> Interview recall: the checklists in these notes. Role map: [interviewing](../../practice/interviewing/README.md).
> Position: sixth generative-ai pillar, the tooling layer. It sits after the agent and model pillars ([04](../04-agentic-frameworks/README.md), [05](../05-RL/README.md)) and before shipping them ([07](../07-agentic-applications/README.md)). Read it alongside the Eval pillar, [generative-ai/08-eval](../08-eval/README.md): this one is how you collect and read the evidence, that one is how you judge it.

---

## What it is

Observability for LLM applications means you can see what happened inside a run: which tools were called, what the model received and returned, how long each step took and what it cost, and whether the output was any good. This pillar is the hands-on tooling for that, with Langfuse as the main platform and LangSmith as the alternative.

> **Observability is the infrastructure; eval is the discipline.** The questions you can answer about an agent next month are fixed by what you log today.

One failed fortnight runs through all six chapters. Acme Books, a fictional invoicing product, runs a support agent in Dutch and English, and we follow 1,400 synthetic turns from 5 to 18 October 2026. On 11 October a vendor behind `get_invoice` starts to stall. On 14 October release v2.0 puts a timestamp in the system prompt, which breaks the prompt cache, and changes the retriever, which raises wrong answers on billing and refunds. On 17 October v2.1 removes the timestamp, the spend recovers, and the answers stay wrong. Each chapter asks what one tool could see of that fortnight and what it could not.

The pillar follows one data model, trace → span → score and dataset → run, through six uses:

- tracing an agent turn
- scoring traces and comparing system versions on a golden dataset
- running a pipeline of specialised judges over exported production traces
- letting an agent query its traces through MCP
- writing the contract a real system logs to, and promoting checks from log-only to blocking
- reading spend and latency on dashboards, and setting the alerts that fire on them

What a good grader is, how to calibrate a judge, and how to read a result with n=20 are covered in [generative-ai/08-eval](../08-eval/README.md). The notes here link to that pillar and don't repeat it.

---

## Start here

1. Read notes 01–04 in order: trace, score, judge at scale, query.
2. Read 05 for the contract that makes 01–04 possible on one system, then 06 for what the same traces cost and how long they took.
3. For the theory behind any score here, follow the links into [generative-ai/08-eval](../08-eval/README.md).
4. Keep the [rules of thumb](#rules-of-thumb) as the one-page summary, and use the [deck](#deck) to revise.

## Layout

```
README.md      this file: overview, start here, syllabus, rules of thumb, resource map
references.md  every source the notes cite, mapped to notes, with licences
notes/         01–06, the course; code inline
practice/      the stubbed agent and synthetic traces, and the check that runs every block
slides/        the lecture deck
sources/       the AgentOps paper and the dashboard figure
```

---

## Syllabus

| # | Note | Covers |
|---|---|---|
| 1 | [Tracing with Langfuse](notes/01-tracing-with-langfuse.md) | Reading one turn as a tree; session, trace, observation and score; SDK v5 wiring, `@observe`, `CallbackHandler`; the `ContextVar` pattern for tools; OpenTelemetry; online scores and what they miss; masking and sampling |
| 2 | [Scoring, datasets and experiments](notes/02-scoring-datasets-experiments.md) | Golden dataset; `run_experiment`; judge in code vs managed evaluators; embedding similarity; reading two versions by category; the bootstrap interval; a release gate with floors |
| 3 | [Judge pipelines over trace exports](notes/03-judge-pipelines-over-trace-exports.md) | ETL from exported traces; one judge per failure mode; evidence-first grounding schema; gated verification; lenient vs strict A/B; cost; what recall a second stage can lose |
| 4 | [A Langfuse MCP server](notes/04-langfuse-mcp-server.md) | Native vs community servers; writing a small read-only server; tool output as context; allowlists and least privilege; prompt injection through traces |
| 5 | [Support agent observability](notes/05-support-agent-observability.md) | The base trace metadata contract and its validator; where human review goes; sampling for concentration; config diffs; promoting a check from log-only to blocking per segment |
| 6 | [Cost and latency dashboards](notes/06-cost-and-latency-dashboards.md) | Cache-aware cost; the bucket table; percentiles that don't add; cost per resolved turn; replaying alerts on the fortnight; what a dashboard can't see; cost levers in order |

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DA 05/05 Dashboards and storytelling](../../data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling.md) | Optional background: what a dashboard is for and what it can hide |

**Feeds into**

| Chapter | Why |
|---|---|
| [AIE 02/09 Protocols](../../ai-engineering/02-context-engineering/notes/09-protocols.md) | MCP, whose observability use is taught here |

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
| Validate the metadata contract in CI; a field nobody checks stops being there | [05](notes/05-support-agent-observability.md) |
| Run a new check log-only, and promote it per segment on measured precision | [05](notes/05-support-agent-observability.md) |
| Keep a random slice beside targeted sampling, or you can't estimate the base rate | [05](notes/05-support-agent-observability.md) |
| Compute cost from cache read, cache write and uncached input as three separate counts | [06](notes/06-cost-and-latency-dashboards.md) |
| Alert on cost per resolved turn and cache hit rate, not only on total spend | [06](notes/06-cost-and-latency-dashboards.md) |
| Report p95 per route; percentiles don't add across spans and an all-route p95 hides one bad route | [06](notes/06-cost-and-latency-dashboards.md) |
| Protect the cache first, cap loops, batch judges, then test cheaper models through the gate | [06](notes/06-cost-and-latency-dashboards.md) |
| A healthy dashboard says nothing about correctness; read it beside the judges | [06](notes/06-cost-and-latency-dashboards.md) |

---

## Primary texts

- Beyer et al., *Site Reliability Engineering*, ch. 6
- Dong et al., *A Taxonomy of AgentOps*
- Langfuse documentation

Everything else: [references.md](references.md).

## Resource map

### Related notes elsewhere
- Eval theory: [generative-ai/08-eval](../08-eval/README.md), especially [05 LLM as judge](../08-eval/notes/05-llm-as-judge.md), [15 calibrating a judge](../08-eval/notes/15-calibration-against-human-labels.md), [07 evaluating RAG and grounding](../08-eval/notes/07-evaluating-rag-and-grounding.md), [08 tracing and observability](../08-eval/notes/08-tracing-and-observability.md) and [13 case study: support agent](../08-eval/notes/13-case-study-support-agent.md).
- LangSmith, the alternative platform: [04-agentic-frameworks 05](../04-agentic-frameworks/notes/05-langsmith.md).
- MCP as a protocol: [ai-engineering/02-context-engineering 09](../../ai-engineering/02-context-engineering/notes/09-protocols.md).

### Books and courses
- *Learning-LangFuse* (healthcare chatbot evaluation project) → note 02.
- *langfuse-evaluation* (judge pipeline over production traces) → note 03, generic design only.
- *langfuse-mcp-python* (MCP server) → note 04.
- Courses, the SRE book chapters, the AgentOps paper, upstream repos and licences: [references.md](references.md).

### Coursework and practice
Every block in the notes runs from [practice/](practice/README.md) with no key and no network, against a stubbed agent and 1,400 synthetic turns. From `practice/`:

```bash
uv run --no-project --with 'langfuse>=5' --with pandas --with numpy --with langgraph --with langchain --with anthropic --with 'mcp>=2' --with matplotlib python check_blocks.py
```

That runs each block as written and compares it to the output printed in the chapter. `trace_server.py` is chapter 4's MCP server and `make_dashboard_chart.py` draws chapter 6's figure.

To do the same against real services, each chapter's Labs section links the upstream project:

| Lab | Note | Runs |
|---|---|---|
| Judge, dataset runs, embedding similarity | [02](notes/02-scoring-datasets-experiments.md#labs) | Needs Docker (self-hosted Langfuse) and `GROQ_API_KEY_1`; embeddings and agents need `GEMINI_API_KEY` |
| Judge pipeline over trace exports | [03](notes/03-judge-pipelines-over-trace-exports.md) | Upstream is internal-use; rebuild from the note's code against your own exports. Needs a Gemini/Vertex key |
| Langfuse MCP server | [04](notes/04-langfuse-mcp-server.md#labs) | Needs a Langfuse project and keys; Python ≥ 3.11 |

### Deck
The lecture deck is [slides/observability.pptx](slides/observability.pptx) ([PDF](slides/observability.pdf), source [slides/deck.yaml](slides/deck.yaml)). Rebuild it from the repo root with `make slides PILLAR=generative-ai/06-observability STRICT=1 PREVIEW=1`.

### Readings
- Langfuse docs, Anthropic's evals post, the AgentOps paper, courses, serving and security links: [references.md](references.md).

### Interviewing guide
- [Interviewing](../../practice/interviewing/README.md): role map to these checklists, and the rounds.

### Previous and next layer
← [05-RL](../05-RL/README.md)
→ [07-agentic-applications](../07-agentic-applications/README.md): projects that ship the agents traced and scored here.
