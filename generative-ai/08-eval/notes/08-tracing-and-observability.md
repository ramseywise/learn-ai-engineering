---
origin: synthesis
sources:
  - https://opentelemetry.io/docs/specs/semconv/gen-ai/
  - https://arize.com/docs/phoenix
  - https://langfuse.com/docs
  - https://www.deeplearning.ai/short-courses/evaluating-ai-agents/
  - "Huyen, AI Engineering (O'Reilly, 2025), ch. 10"
  - "Michael Albada, Building Applications with AI Agents (O'Reilly, 2025), ch. 10"
  - eval-harness.md (retired 2026-10-28)
confidence: high
cleaned: 2026-11-01
---
# 8 — Tracing and Observability

> You can't grade what you didn't record. A trace is the eval's raw material: every model call, tool call and retrieval as a span, with inputs, outputs, tokens and timing. Instrument once, and the same traces feed offline evals, production monitoring and debugging.

A nightly eval says grounding fell, and the team can't say which request, prompt version or retrieval caused it, because they logged only the final reply. Every grader in this course reads from a record of what happened: a trajectory check needs tool calls, and a grounding check needs passage text. This chapter covers what a trace has to hold so that evals, cost attribution and debugging all work from one source.

---

## Why traces come first

Final-output evals tell you *that* something failed. Traces tell you *where*. Without them:

- A trajectory grader ([06](06-evaluating-agents.md#scoring-tool-calls)) has nothing to read.
- A grounding grader can't see the retrieved text ([07](07-evaluating-rag-and-grounding.md#pass-the-text-not-the-pointer)).
- An efficiency regression (more steps, more tokens) is invisible.
- You can't tell an agent bug from an eval bug ([12](12-failure-modes.md#eval-bugs-look-like-agent-bugs)).

The DeepLearning.AI course makes tracing Lab 2, before any evaluator, for this reason.

---

## Anatomy of a trace

A **trace** is one end-to-end request. It's a tree of **spans**, each one unit of work:

```
invoke_agent  support-agent                       2.8s   $0.012
├── chat      claude-sonnet  (plan)               0.9s   1,840 in / 120 out
├── execute_tool  search_help_center              0.4s
│     └── retrieval: 5 chunks, top score 0.82
├── execute_tool  lookup_order (order_id=8812)    0.2s
└── chat      claude-sonnet  (answer)             1.3s   3,210 in / 260 out
```

Here is the course agent's trace in Phoenix. The agent span wraps two router turns. The first calls a tool, which makes its own LLM call and runs SQL. The second writes the answer:

![Span tree for one agent run: AgentRun (agent) contains router_call (chain) with an LLM chat completion, handle_tool_calls (chain) with the lookup_sales_data tool, its LLM call and execute_sql_query, then a second router_call and LLM call](../sources/images/deeplearning-ai-evaluating-ai-agents-lab2-spans.png)
*Image Source: DeepLearning.AI & Arize, Evaluating AI Agents (2025), Lab 2*

Auto-instrumentation gives you the LLM spans. Your own code adds the agent, chain and tool spans around them:

```python
tracer_provider = register(project_name=PROJECT)      # phoenix.otel: OTel exporter
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)  # every LLM call
tracer = tracer_provider.get_tracer(__name__)

@tracer.tool()                                         # tool span, args + result
def lookup_sales_data(prompt: str) -> str: ...

def run_agent(messages):
    with tracer.start_as_current_span("AgentRun", openinference_span_kind="agent") as span:
        span.set_input(value=messages)
        with tracer.start_as_current_span("router_call", openinference_span_kind="chain"):
            ...                                        # LLM spans nest in here
        span.set_output(value=answer)
        span.set_status(StatusCode.OK)
```

Name the spans after your agent's own steps (router, tool, skill), so a grader can select them by kind and name later ([06](06-evaluating-agents.md#evaluate-the-components-then-the-whole)).

### What each span should carry

| Span type | Record |
|---|---|
| **Agent / request** | User / session ID, prompt + config version, final output, outcome label, total cost |
| **Model call** | Model ID, full input messages, output, tokens in / out / cached, latency, finish reason |
| **Tool call** | Tool name, arguments, result (or error), latency |
| **Retrieval** | Query (after rewrite), returned IDs **and text**, scores, rank |
| **Guardrail / judge** | Verdict, reasoning, grader version |

Record **versions** on the root span: prompt, model, tool set, index, config. "Which change caused this?" is unanswerable without them.

### The questions a trace must answer

1. What did the user ask, and what did they get?
2. Which steps ran, in what order?
3. What did the model see at each step (the full context)?
4. Which tools were called with what, and what came back?
5. Where did the time and money go?
6. Which versions of everything were running?

If your traces can't answer one of these, that's the instrumentation gap to fix first.

---

## Use the standard: OpenTelemetry GenAI

OpenTelemetry's **GenAI semantic conventions** standardize span and attribute names, so traces work across tools:

| Convention | Example |
|---|---|
| Span operation names | `invoke_agent`, `chat`, `execute_tool`, `embeddings` |
| Model attributes | `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.response.finish_reasons` |
| Usage | `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` |
| Tools | `gen_ai.tool.name`, `gen_ai.tool.call.id` |

Instrument with OTel (or OpenInference, which Phoenix uses and maps to it), and you can switch backends without re-instrumenting. Most agent frameworks (LangGraph, ADK, OpenAI Agents SDK, Claude Agent SDK) emit these spans with a one-line setup.

---

## Tools

| Tool | Strength |
|---|---|
| **Arize Phoenix** | Open source, local-first. Traces + evals + experiments in one. The DLAI course uses it |
| **Langfuse** | Open source, self-hostable. Prompt management, datasets, scores on traces |
| **LangSmith** | Tight LangChain / LangGraph integration. Datasets, experiments, annotation queues |
| **Braintrust, W&B Weave** | Experiment-centric. Strong comparison views |
| **Your APM** (Datadog, Honeycomb, Grafana) | Already where ops looks. Accepts OTel GenAI spans |
| **Open-source ops stacks** (Grafana + Loki + Tempo, ELK, SigNoz) | Logs, traces and alerts beside service health, so SREs and AI engineers share one dashboard. No built-in evals: you push grader scores in as span attributes or metrics (*Building Applications with AI Agents*, ch. 10) |

Pick on: can it run evals over stored traces, attach scores back to spans, build datasets from traces, and compare two experiments side by side? Those four turn a trace viewer into an eval platform.

---

## Traces → evals → datasets

The loop that makes traces pay off:

![Traces flow from the agent into an observability platform. The evaluation layer queries traces and writes annotations back to them](../sources/images/deeplearning-ai-evaluating-ai-agents-lab3-traces.png)
*Image Source: DeepLearning.AI & Arize, Evaluating AI Agents (2025), Lab 3*

```
production traces ──sample──▶ graders (online) ──scores on spans──▶ dashboards / alerts
        │                                                                │
        └──── failures, 👎, escalations ──▶ triage ──▶ new eval rows ◀────┘
                                                          │
                                         offline experiments re-run on them
```

- **Scores live on spans.** Attach grader results to the trace they graded, so a bad score is one click from the full context.
- **Datasets come from traces.** Export a failing trace's input (and state) as a new row ([03](03-eval-datasets.md#harvest-from-failures)).
- **Offline and online share graders.** The same grader code runs in CI and on sampled production traffic. Two implementations drift apart.

---

## Cost and latency attribution

Traces are where cost lives. Roll up per span → per request → per user / feature / slice:

- **Cost per success**, not per call ([06](06-evaluating-agents.md#efficiency-metrics)).
- **Where tokens go.** System prompt, retrieved context, conversation history, tool results. Context bloat shows up as a rising input-token share of one category.
- **Cache hit rate** for prompt caching. A prompt change that breaks the cacheable prefix can double cost overnight.
- **Tail latency by step.** p95 is usually one slow tool or one long generation, not the whole pipeline.

Rolling a trace up takes little code, and so does scrubbing it on the way out. This uses the trace in the diagram above, with assumed prices of $3 and $15 per million tokens, so its cost differs from the diagram's $0.012:

```python
import re

# One trace, flattened. Tokens are recorded on model spans; retrieval carries text, not just ids.
TRACE = {"trace_id": "t-8812", "outcome": "resolved", "spans": [
    {"name": "chat plan", "in": 1840, "out": 120, "ms": 900},
    {"name": "execute_tool search_help_center", "ms": 400,
     "chunks": [{"id": "p1", "text": "Refunds go back to the card within 5 days."}]},
    {"name": "execute_tool lookup_order", "ms": 200, "args": "order 8812 for jo@example.com"},
    {"name": "chat answer", "in": 3210, "out": 260, "ms": 1300},
]}
IN_PRICE, OUT_PRICE = 3 / 1e6, 15 / 1e6      # assumed $ per token, for the example only

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")

def export(trace):                           # scrub as the span leaves the process
    clean = dict(trace, spans=[])
    for span in trace["spans"]:
        clean["spans"].append({k: EMAIL.sub("<email>", v) if isinstance(v, str) else v
                               for k, v in span.items()})
    return clean

def rollup(trace):
    spans = trace["spans"]
    cost = sum(s.get("in", 0) * IN_PRICE + s.get("out", 0) * OUT_PRICE for s in spans)
    slowest = max(spans, key=lambda s: s["ms"])
    return {"cost": round(cost, 4), "total_ms": sum(s["ms"] for s in spans),
            "slowest": slowest["name"], "slowest_share": round(slowest["ms"] / sum(s["ms"] for s in spans), 2)}

print(rollup(TRACE))
print(export(TRACE)["spans"][2]["args"])

def cost_per_success(traces):                # failed runs are paid for too
    return sum(rollup(t)["cost"] for t in traces) / sum(t["outcome"] == "resolved" for t in traces)

failed = dict(TRACE, outcome="abandoned")
print("per run", rollup(TRACE)["cost"], "per success at 50%", round(cost_per_success([TRACE, failed]), 4))
```

Output:

```text
{'cost': 0.0209, 'total_ms': 2800, 'slowest': 'chat answer', 'slowest_share': 0.46}
order 8812 for <email>
per run 0.0209 per success at 50% 0.0418
```

The slowest span takes 46% of the time, and a 50% success rate doubles the cost of each success. The email is gone before the span reaches a backend.

---

## What to watch, and when to page someone

Huyen borrows three DevOps numbers to grade the monitoring itself (*AI Engineering*, ch. 10):

- **MTTD**, mean time to detection: how long until you notice something broke.
- **MTTR**, mean time to response: how long from detection to resolution.
- **CFR**, change failure rate: the share of deploys that need a fix or rollback. If you don't know it, the platform isn't observable enough. A high CFR is a signal for the offline eval pipeline ([10](10-evals-in-ci.md)), which should be catching bad changes before they ship.

Metrics detect, logs explain. Her example: metrics say something broke five minutes ago, and you go to the logs to see what. If the logs arrive 15 minutes late, MTTR can't beat 15 minutes. Since you can't know which log you'll need, **log everything**: model endpoint and name, sampling settings, prompt template, the final prompt, every intermediate output, every tool call and its output. Make every metric sliceable by user, release, prompt or chain version, and time. Start with the failures that are easiest to count and to fix, such as invalid JSON and other format errors.

Albada's alert examples for an agent (*Building Applications with AI Agents*, ch. 10):

| Alert | Example threshold |
|---|---|
| Hallucination rate | > 5% over the last 30 minutes |
| Retry loops | > 3 in one session |
| Critical-tool latency | average up > 50% |
| Task abandonment | > 15% |
| Retries across sessions | > 20% of sessions |
| Accuracy | drops > 5–10% over a rolling 24 hours |

These are illustrations, not measured thresholds. Set yours from your own baseline variance, or the pager will fire on noise. Distribution-drift statistics for inputs (KS, PSI, embedding distance) are covered in [11](11-production-and-the-maturity-ladder.md#drift).

**Failure or variation?** Albada's triage for a bad output: rerun it 3–5 times. If it fails more than 80% of the reruns, treat it as a systematic bug and send it to engineering. If it doesn't reproduce, compare it to the baseline distribution before acting. Expected variation gets logged for drift watch, not fixed. This is the per-task pass-rate distribution from [06](06-evaluating-agents.md#non-determinism-run-every-task-k-times) applied to one production trace.

---

## Privacy and retention

Traces contain user input, which means PII. Decide up front:

- What's redacted before storage (emails, card numbers, IDs).
- Who can see raw traces.
- How long they're kept, and whether eval rows derived from them inherit the same limit.
- Whether users consented to their conversations being used for evaluation.

Redact **at span export**, not in the dashboard. OTel exporters provide hooks for scrubbing data as spans leave the process, so raw PII never reaches the backend. Put raw traces behind role-based access control (*Building Applications with AI Agents*, ch. 10).

---

## Checklist

- [ ] Every model call, tool call and retrieval is a span with inputs, outputs, tokens, latency
- [ ] Retrieval spans carry passage text, not just IDs
- [ ] Root span records prompt / model / config / index versions
- [ ] OTel GenAI conventions (or OpenInference) used
- [ ] Grader scores attached back to spans
- [ ] One-click path from a failing trace to a new eval row
- [ ] Cost rolled up per request and per success
- [ ] PII redaction and retention policy in place

## Working reference

`~/.claude/refs/agent-observability.md` — span types, minimum attributes, cost attribution, the six questions.

---

## Pitfalls

- **Logging only the final answer.** Symptom: a failed eval with nothing to read, and "which change caused this?" has no answer. Fix: a span for every model call, tool call and retrieval, with versions on the root span.
- **Retrieval spans with IDs and no text.** Symptom: grounding graders can't run or return `context_missing`. Fix: record passage text, scores and rank on the retrieval span, and the query after rewriting.
- **Two copies of each grader.** Symptom: offline and online scores disagree with no system change. Fix: run the same grader code in CI and on sampled traffic, and attach scores to the spans they graded.
- **Scrubbing PII in the dashboard.** Symptom: raw emails and card numbers sit in the backend behind a display filter, and eval rows inherit them. Fix: redact at span export, restrict raw traces with role-based access, and apply the retention limit to derived rows.
- **Paging on copied thresholds.** Symptom: alert fatigue from Albada's example numbers, which are illustrations and not measurements. Fix: set thresholds from your own baseline variance.
- **Tracking cost per call.** Symptom: a cheaper model looks like a win while retries raise the true bill. Fix: report cost per success, split input tokens by source, and watch the cache hit rate, since a prompt change that breaks the cacheable prefix can double cost overnight.
- **Late logs.** Symptom: metrics show a break five minutes ago, the logs arrive 15 minutes late, and MTTR can't be better than that delay. Fix: treat log lag as part of the monitoring's own grade, beside MTTD, MTTR and CFR.

## Try it

1. Check your own agent's traces, or the trace in this chapter's diagram, against the six questions. Which can't the diagram answer?

   <details><summary>Answer</summary>

   The diagram answers question 2 (which steps ran, in what order) and most of question 5 (where the time went, plus total cost). It partly answers question 4, since it names the tools but not what came back. It doesn't show what the user asked or received (1), the full context the model saw (3) or the versions running (6), so those are the instrumentation gaps. The span table shows the fields that close them.

   </details>

2. In the script, set the answer span's input tokens to 8,210, as if a 5,000-token tool output had been added to the context. What are the cost per run and the cost per success at 50%?

   <details><summary>Answer</summary>

   Running it gives $0.0358 per run and $0.0716 per success, up from $0.0209 and $0.0418. No extra steps were taken, which is why the cost shows up only if tokens are recorded per span.

   </details>

3. A bad output fails 4 of 5 reruns. Under Albada's triage, is that a systematic bug? What about 5 of 5, and 1 of 5?

   <details><summary>Answer</summary>

   His rule is "more than 80%", so 4 of 5 sits exactly on the line and 5 of 5 is the only clear result at five reruns: that is a systematic bug for engineering. Treat 4 of 5 as probably systematic and run more. For 1 of 5, compare with the baseline distribution before acting, and log it for drift watch if it is expected variation.

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| What must a retrieval span record? | The query after rewriting, the returned IDs and text, scores and rank. Without text, a grounding grader has nothing to verify. |
| What goes on the root span? | User or session ID, final output, outcome label, total cost, and the versions of prompt, model, tool set, index and config. |
| Why use the OpenTelemetry GenAI conventions? | Standard span and attribute names such as `invoke_agent` and `gen_ai.usage.input_tokens` let you switch backends without re-instrumenting. |
| Where do you redact PII? | At span export, so raw PII never reaches the backend, with role-based access on raw traces. Eval rows derived from traces should inherit the same retention limit. |
| What do MTTD, MTTR and CFR tell you? | Time to detect, time to resolve, and the share of deploys that need a fix or rollback. A high CFR says the offline eval pipeline is missing bad changes. |
| Your bill doubled overnight and traffic is flat. Where do you look? | Cache hit rate first, since a prompt change that breaks the cacheable prefix can double cost, then input-token share by source for context bloat, then cost per success by version. |
| What features would you require of a tracing tool? | Evals over stored traces, scores attached to spans, datasets built from traces, and side-by-side experiment comparison. Those four turn a trace viewer into part of the eval loop. |

## Next

[09-reading-results.md](09-reading-results.md): when a number changed, did anything change?
