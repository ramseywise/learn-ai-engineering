---
origin: own coursework
sources:
  - https://langfuse.com/docs/observability/sdk/overview
  - https://langfuse.com/docs/observability/sdk/python/instrumentation
  - https://langfuse.com/docs/observability/sdk/upgrade-path/python-v4-to-v5
  - https://python.reference.langfuse.com
  - https://arxiv.org/abs/2411.05285
  - ../practice/support_agent/
confidence: high
cleaned: 2026-11-01
---
# 1 — Tracing with Langfuse

> One trace per agent turn, one child observation per model or tool call: the Langfuse data model, instrumenting with the current v5 SDK, carrying a trace into tools with a `ContextVar`, and the score keys a support agent records.

On a Monday in October a customer of Acme Books writes in to say the support assistant told them something that turned out to be false, and the invoice page took half a minute to load an answer on Friday. An ordinary service log can tell you the request returned 200 in 22 seconds. It can't tell you which documents the model read, whether it retried, how many tokens it spent, or whether the sentence the customer complained about appears in any of those documents. Tracing exists to answer those questions after the fact, when the turn cannot be reproduced because the model will not say the same thing twice.

This pillar works one incident from the first trace to the dashboard that should have caught it. This chapter reads one bad turn, then instruments the agent so that every future turn can be read the same way.

---

## The case study: a fortnight at Acme Books

Acme Books is a fictional invoicing product with Danish and English customers. Its support agent routes each message with a small model, searches a help centre, calls account tools, answers with a larger model, and checks the answer before sending it. Nothing here calls a model. The package in [practice/support_agent/](../practice/support_agent/) is a stub that produces the telemetry such an agent would, with failures planted at known rates and the truth recorded in `seeded_failure`, so that each later chapter can measure how much of the planted damage its checks find.

Every code block in these chapters reads the same fortnight of 1,400 turns, from 5 to 18 October 2026.

| Date | What changed | Who would notice |
|---|---|---|
| 5 Oct | Release `v1`, running normally | |
| 11 Oct | A vendor behind the `get_invoice` tool starts stalling on some calls | Billing customers, then latency percentiles |
| 14 Oct | Release `v2.0`: a timestamp lands in the system prompt, which breaks the prompt cache, and a retriever change raises wrong answers on billing and refunds | The bill, and nobody at first for the answers |
| 17 Oct | Release `v2.1` removes the timestamp. The answers stay wrong | The bill recovers, which looks like the end of the incident |

The numbers are synthetic and only the mechanisms carry over. The per-turn token counts are plausible, and 100 turns a day is deliberately small, so a percentile computed on one day is noisy in the way a small route's percentile is noisy in production.

---

## Reading one bad trace

A trace is the record of one request from end to end. Inside it sit observations: the spans, model calls and tool calls that made up the work. The first thing to learn is how to read one, because no aggregate tells you what a failure looks like.

```python
from support_agent import generate_traces, print_tree

traces = generate_traces()
looping = next(t for t in traces if t.seeded_failure == "retry_loop")
print_tree(looping)
print("Q:", looping.question)
print("A:", looping.answer)
```

```text
t00004  account/en  v1  outcome=abandoned  16.5s  $0.0259
  input_guardrail guardrail          8 ms
  route           generation       345 ms  in=82 read=420 write=0 out=7
  kb_search       retriever        864 ms  ERROR
  answer          generation      1996 ms  in=595 read=4200 write=0 out=83
  kb_search       retriever        670 ms  ERROR
  answer          generation      1611 ms  in=677 read=4200 write=0 out=82
  kb_search       retriever        642 ms  ERROR
  answer          generation      1681 ms  in=912 read=4200 write=0 out=43
  kb_search       retriever        212 ms
  get_account     tool             122 ms
  answer          generation      8306 ms  in=839 read=4200 write=0 out=315
  grounding_check guardrail         10 ms
Q: How many users are on the Standard plan?
A: The Standard plan includes 5 users. Add users under Settings, then Team.
```

Read it top to bottom as a story. The router was fast and cheap. The first search failed, and the agent's response was to ask the expensive model what to do, three times, with a growing context each time. The fourth search worked and the answer is correct, so a log line that recorded only the final reply would show nothing wrong. The tree shows what the customer lived through: 16.5 seconds of waiting and the outcome `abandoned`, because they left before it finished. The failing spans are marked `ERROR`, which makes them something you can count across a fortnight rather than something you notice once.

Now compare a healthy turn, and look at the `read=` column. The system prompt comes from the prompt cache, which is why the answer call is cheap despite carrying thousands of tokens.

```python
from support_agent import generate_traces, print_tree

traces = generate_traces()
print_tree(next(t for t in traces if t.seeded_failure is None and t.route == "account"))
print()
print_tree(next(t for t in traces if t.release == "v2.0" and t.seeded_failure is None and t.route == "account"))
```

```text
t00081  account/en  v1  outcome=resolved  7.0s  $0.0107
  input_guardrail guardrail          6 ms
  route           generation       231 ms  in=68 read=420 write=0 out=7
  kb_search       retriever        112 ms
  get_account     tool              41 ms
  answer          generation      6646 ms  in=866 read=4200 write=0 out=321
  grounding_check guardrail         12 ms

t00994  account/da  v2.0  outcome=resolved  7.4s  $0.0293
  input_guardrail guardrail         10 ms
  route           generation       338 ms  in=71 read=420 write=0 out=8
  kb_search       retriever        152 ms
  get_account     tool              86 ms
  answer          generation      6770 ms  in=603 read=0 write=4200 out=293
  grounding_check guardrail         13 ms
```

The second tree is the same kind of question nine days later, and it costs nearly three times as much. `read=0 write=4200` on the answer call is the cache regression in a single line: every turn now pays the write premium on the whole prefix instead of the read discount. No error fired, because nothing failed. [Chapter 6](06-cost-and-latency-dashboards.md) turns this into a chart and an alert.

---

## The data model

```text
Session  sess-0502                    groups the turns of one conversation
  Trace  support_turn                 one request; carries user, session, tags, release
    input    {message}
    output   {message, escalated}
    metadata {route, language, prompt_version, git_commit, outcome}

    agent       agent_turn            the root observation
      guardrail   input_guardrail
      generation  route               model, usage_details, cost_details
      retriever   kb_search           input {query}, output {passage_count, top_score, urls}
      tool        get_invoice         level WARNING when it stalls
      generation  answer              model, usage_details, cost_details
      guardrail   grounding_check

    Score citation_hallucination      attached to the trace, numeric, boolean or categorical
    Score language_consistency        online heuristic, free
    Score user_feedback               explicit, sparse
```

Each of those words matters for a reason. A **generation** carries a model name and token usage, which is what cost tracking reads. A **tool** or **retriever** observation records arguments and results, which is what lets you ask whether the model searched for the right thing. A **score** is attached after the fact and can come from code, from a judge, or from a person. Langfuse takes the trace's input and output from the root observation, so set them there.

Why spans of different types rather than one generic span? The review by Dong, Lu and Zhu of 17 agent observability tools ([arXiv:2411.05285](https://arxiv.org/abs/2411.05285), Dong, Lu and Zhu, 2024-11, preprint) found every tool offered tracing but most centred on LLM metrics, with limited support for the goals, plans and tools that make an agent different from a chain. The taxonomy they propose gives reasoning, planning, task, tool, evaluation and guardrail steps their own span types, each with its own metadata. Langfuse's `as_type` values cover part of that list, and [chapter 5](05-support-agent-observability.md) maps our schema onto the rest. The paper notes that the taxonomy has not yet been validated in real case studies, so treat it as a checklist of what to consider logging, not a standard.

---

## Instrumenting with the v5 SDK

Install the SDK and set three variables. Version 5 needs Python 3.11 or newer and, if you self-host, a server at v4.59.0 or later.

```bash
uv add langfuse
```

```bash
# .env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL
```

The SDK is built on OpenTelemetry, and the unit of work is a context manager that opens an observation and makes it current. Older tutorials use `lf.trace()`, `trace.span()`, `lf.score()` and `langfuse.decorators`. Those belong to the v2 API and no longer exist. In the block below, `offline_langfuse()` returns the real client from the real package, but with an in-memory span exporter and a mocked HTTP transport, so you can see exactly what would be sent. In production you replace that line with `from langfuse import get_client; lf = get_client()`.

```python
from langfuse import propagate_attributes
from support_agent.fakes import offline_langfuse

lf, capture = offline_langfuse()

def search_kb(query):
    with lf.start_as_current_observation(name="kb_search", as_type="retriever", input={"query": query}) as span:
        result = {"passage_count": 2, "top_score": 0.82}
        span.update(output=result)
        return result

def answer(question, passages):
    with lf.start_as_current_observation(name="answer", as_type="generation", model="claude-opus-5-5", input=question) as gen:
        text = "The default payment term is 14 days."
        # Usage keys are exclusive buckets: each token is counted in exactly one.
        gen.update(output=text, usage_details={"input": 640, "cache_read_input_tokens": 4200, "output": 180})
        return text

with propagate_attributes(session_id="sess-0502", version="v1", trace_name="support_turn",
                          tags=["billing", "en"], metadata={"route": "billing", "prompt_version": "answer-v7"}):
    with lf.start_as_current_observation(name="agent_turn", as_type="agent", input={"message": "What is the default payment term?"}) as root:
        hits = search_kb("default payment term")
        reply = answer("What is the default payment term?", hits)
        root.update(output={"message": reply, "escalated": False})

lf.flush()
for span in capture.spans():
    a = span.attributes
    print(f"{span.name:<11} type={a['langfuse.observation.type']:<11} session={a['session.id']} route={a['langfuse.trace.metadata.route']}")
print(capture.spans()[1].attributes["langfuse.observation.usage_details"])
```

```text
kb_search   type=retriever   session=sess-0502 route="billing"
answer      type=generation  session=sess-0502 route="billing"
agent_turn  type=agent       session=sess-0502 route="billing"
{"input": 640, "cache_read_input_tokens": 4200, "output": 180}
```

Four things in that block are decisions.

1. **`propagate_attributes` sets trace-level fields once**, and every observation opened inside inherits them. That is how a dashboard can later filter by release without each tool knowing about releases.
2. **Usage keys don't overlap.** Langfuse derives the total as a sum, so the three buckets must partition the tokens. Anthropic's API reports them the same way: `input_tokens` is only what came after the last cache breakpoint, so total input is `cache_read_input_tokens + cache_creation_input_tokens + input_tokens`.
3. **A trace id can come from you.** `Langfuse.create_trace_id(seed=ticket_id)` gives a stable id, so a score posted hours later by a batch job can find its trace without a lookup. [`replay.py`](../practice/support_agent/replay.py) uses this to send a whole synthetic trace through the SDK.
4. **Spans are buffered and exported in the background.** Short scripts must call `lf.flush()` before they exit, or the last batch is lost silently.

If the agent has a normal call stack, the `@observe` decorator is shorter and captures function arguments and return values for you. Set `capture_input=False` on anything holding data you must not log.

```python
from langfuse import observe
from support_agent.fakes import offline_langfuse

lf, capture = offline_langfuse()

@observe(name="kb_search", as_type="retriever")
def search_kb(query):
    return {"passage_count": 2, "top_score": 0.82}

@observe(name="agent_turn", as_type="agent")
def run_turn(message):
    hits = search_kb(message)
    print("trace id length:", len(lf.get_current_trace_id()))
    return {"message": "stub", "hits": hits["passage_count"]}

print(run_turn("How long is my reset link valid?"))
lf.flush()
print([s.name for s in capture.spans()])
```

```text
trace id length: 32
{'message': 'stub', 'hits': 2}
['kb_search', 'agent_turn']
```

---

## Carrying a trace into tools

Context managers and decorators rely on the current OpenTelemetry context flowing down the call stack. That holds in ordinary Python and in `asyncio` tasks that copy their context. It stops holding when a framework runs tools from its own event loop or hands them to a worker, as runner-style agents like Google ADK can do: the tool may run with no current span, and its observation becomes a new orphan trace.

The fix is to stop relying on implicit context. Keep an explicit reference to the root in a `ContextVar` you own, set it before handing control to the runner, and open children from the object rather than from the ambient context. `start_observation` creates an observation without making it current, and calling it on the root makes it a child however the call was scheduled.

```python
import asyncio
from contextvars import ContextVar
from support_agent.fakes import offline_langfuse

lf, capture = offline_langfuse()
turn_root = ContextVar("turn_root", default=None)

async def kb_tool(query):
    """A tool the framework calls. It has no argument for the trace, and doesn't need one."""
    root = turn_root.get()
    span = root.start_observation(name="kb_search", as_type="retriever", input={"query": query}) if root else None
    await asyncio.sleep(0)
    result = {"passage_count": 2, "top_score": 0.82}
    if span:
        span.update(output=result)
        span.end()
    return result

async def framework_runner(message):
    """Stands in for a runner that schedules tools itself."""
    yield await asyncio.create_task(kb_tool(message))

async def handle(message):
    with lf.start_as_current_observation(name="agent_turn", as_type="agent", input={"message": message}) as root:
        token = turn_root.set(root)
        try:
            async for event in framework_runner(message):
                root.update(output=event)
        finally:
            turn_root.reset(token)  # always reset, or the next turn inherits this trace

asyncio.run(handle("What is the API rate limit?"))
lf.flush()
spans = {s.name: s for s in capture.spans()}
child, parent = spans["kb_search"], spans["agent_turn"]
print("same trace:", child.context.trace_id == parent.context.trace_id)
print("parent is the root:", child.parent.span_id == parent.context.span_id)
```

```text
same trace: True
parent is the root: True
```

Two checks at the end are what you want from any instrumentation test: the child landed in the same trace, under the right parent. A framework's own OpenTelemetry auto-instrumentation (ADK's `invoke_agent` and `call_llm` spans, for example) fires alongside these and shows up as a sibling branch in the same tree, which is useful rather than noisy.

To join a tree that started in another process, pass `trace_context={"trace_id": ..., "parent_span_id": ...}` when opening the observation, and forward those two ids in your own request headers or job payload.

---

## Per-framework tracing: no unified span layer

Each agent should use its framework's native instrumentation: `@observe` for a regular call-stack agent, `CallbackHandler` for LangGraph, LangSmith auto-tracing for frameworks with native LangSmith integration. Don't put an adapter layer in front of them that normalises spans across frameworks.

The reason is that a unified tracing abstraction adds code with no framework-neutral benefit, and native instrumentation gives depth a generic wrapper loses: tool call sequences, graph node transitions. The cost is real. A latency breakdown across two frameworks on two platforms requires joining two exports. That trade is right when data ownership favours a self-hosted platform for some agents and a managed one for others. So don't build a single `trace()` wrapper that every agent calls. Wire each agent to its platform directly, and agree on the metadata keys ([chapter 5](05-support-agent-observability.md)) rather than the instrumentation.

For LangGraph, the callback handler captures every node and edge with no changes to the graph. It reads the client from the singleton, so it takes no secrets. Trace-level fields go through `propagate_attributes`.

```python
from typing import TypedDict
from langfuse import propagate_attributes
from langfuse.langchain import CallbackHandler
from langgraph.graph import END, START, StateGraph
from support_agent.fakes import offline_langfuse

lf, capture = offline_langfuse()

class State(TypedDict):
    question: str
    route: str

def route(state):
    return {"route": "billing" if "invoice" in state["question"] else "account"}

graph = StateGraph(State)
graph.add_node("route", route)
graph.add_edge(START, "route")
graph.add_edge("route", END)
app = graph.compile()

handler = CallbackHandler()
with propagate_attributes(session_id="sess-0502", metadata={"agent": "support_agent", "prompt_version": "answer-v7"}):
    print(app.invoke({"question": "Where is my invoice?"}, config={"callbacks": [handler]}))
lf.flush()
print(sorted({s.name for s in capture.spans()}))
```

```text
{'question': 'Where is my invoice?', 'route': 'billing'}
['LangGraph', 'route']
```

If one agent needs both Langfuse and LangSmith coverage, send OpenTelemetry through a collector and fan out from there rather than instrumenting twice. Two sets of instrumentation drift, and the numbers disagree in ways nobody can explain.

### Why Langfuse

Langfuse is open source and self-hostable, so traces stay in your infrastructure, and with customer messages in those traces that often settles the question. It is built on OpenTelemetry, so instrumentation is not locked to it, and it has a scoring API, datasets, experiments, prompt management and annotation queues in one place. LangSmith has a richer experiment UI and native LangGraph integration, but it is closed source and analysis outside its UI means exporting data ([04-agentic-frameworks](../../04-agentic-frameworks/README.md) covers it). Dong et al.'s feature table records Langfuse as having prompt management, evaluation, feedback, monitoring and tracing, but no guardrails, and their mapping is from 2024, so check the current docs before relying on a gap.

---

## Attaching scores

A trace tells you what happened, and a score tells you whether it was any good. Scores attach to a trace or an observation at any time, from any process, which is what makes it possible to run a judge hours later ([chapter 3](03-judge-pipelines-over-trace-exports.md)).

The cheap scores are computed on every turn with no model at all. [`scorers.py`](../practice/support_agent/scorers.py) implements four. A check is only worth keeping if you know how often it is right, and because this fortnight has planted failures, we can measure that here. In production you would get the labels by reading a sample of traces.

```python
from support_agent import generate_traces
from support_agent.judges import precision_recall

traces = generate_traces()
checks = {
    "citation_hallucination": (lambda t: t.scores["citation_hallucination"] == 1, {"hallucinated_citation"}),
    "language_consistency": (lambda t: t.scores["language_consistency"] == 0, {"language_mismatch"}),
    "retrieval_quality < 0.5": (lambda t: t.scores["retrieval_quality"] < 0.5, {"retrieval_miss", "wrong_route"}),
}
for name, (fires, planted) in checks.items():
    r = precision_recall([fires(t) for t in traces], [t.seeded_failure in planted for t in traces])
    print(f"{name:<25} precision {r['precision']:.2f}  recall {r['recall']:.2f}  (tp {r['tp']}, fp {r['fp']}, fn {r['fn']})")

da = [t for t in traces if t.language == "da" and t.seeded_failure != "language_mismatch"]
print("false language alarms on healthy Danish turns:", sum(t.scores["language_consistency"] == 0 for t in da), "of", len(da))
```

```text
citation_hallucination    precision 0.86  recall 1.00  (tp 18, fp 3, fn 0)
language_consistency      precision 0.23  recall 0.86  (tp 18, fp 61, fn 3)
retrieval_quality < 0.5   precision 1.00  recall 1.00  (tp 81, fp 0, fn 0)
false language alarms on healthy Danish turns: 61 of 402
```

Look at the language check. A stopword guess is fine in English and raises many false alarms on Danish, because short Danish sentences share few markers. It would be a mistake to page anyone on this score. It is still useful as a trend, and [chapter 5](05-support-agent-observability.md) turns that into a written policy for which checks may block a release. The citation check has the opposite profile. It rarely lies, but it only catches an invented URL, and a real URL paired with a changed number passes straight through. That gap is why chapter 3 exists. Don't read much into the perfect retrieval line: the stub gives a bad retrieval a low score by construction, and a real retriever's scores overlap far more.

Writing a score back is one call. The SDK batches it to the scores endpoint.

```python
from langfuse import Langfuse
from support_agent import generate_traces
from support_agent.fakes import offline_langfuse

lf, capture = offline_langfuse()
turn = generate_traces()[0]
trace_id = Langfuse.create_trace_id(seed=turn.trace_id)

lf.create_score(trace_id=trace_id, name="grounding", value=0.4, data_type="NUMERIC",
                comment="The cited document says 14 days, the answer says 30.")
lf.create_score(trace_id=trace_id, name="escalation_correct", value=1, data_type="BOOLEAN")
lf.flush()
for score in capture.api.scores:
    print(score["name"], score["value"], score["dataType"])
```

```text
grounding 0.4 NUMERIC
escalation_correct 1.0 BOOLEAN
```

Inside a live turn, `lf.score_current_trace(...)` and `span.score(...)` do the same without passing an id. Agree on the names first, because a score you can't compare across months is not much use.

**Heuristic grounding tiers (free, no model)**

| Key | Range | Tier |
|---|---|---|
| `citation_hallucination` | 0 / 1 | Tier 1: a response URL is not in the retrieved set |
| `missing_citation` | 0 / 1 | Tier 2: a substantive response with no citations |
| `citation_recall` | 0–1 | Golden URL recall on a dataset (alias: `source_match`) |
| `language_consistency` | 0 / 1 | Tier 4: query language differs from response language |

**Model-graded (calibrated tier)**

| Key | Range |
|---|---|
| `grounding` | 0–1 |
| `answer_relevancy` | 0–1 |
| `completeness` | 0–1 |
| `escalation_correct` | 0 / 1 |
| `routing_accuracy` | 0 / 1, intent label match |

---

## From trace to fixture to person

A failing trace in production is the best test case you will ever get, because you did not have to imagine it. Langfuse has three features that move a trace onward.

**Datasets** collect input and expected-output pairs. In the UI, open a trace and choose "Add to dataset". In code, pass `source_trace_id`, which keeps the link to where the example came from. [Chapter 2](02-scoring-datasets-experiments.md) runs experiments over these.

**Annotation queues** route uncertain cases to a person, which is cheaper than building a review tool and leaves the label attached to the trace. Reviewers label in the UI, and completed labels can be exported as regression fixtures.

```python
from langfuse import Langfuse
from support_agent import generate_traces
from support_agent.fakes import offline_langfuse

lf, capture = offline_langfuse()
traces = generate_traces()

lf.create_dataset(name="support-regressions", description="Turns that went wrong in production")
queue = lf.api.annotation_queues.create_queue(name="uncertain-grounding", score_config_ids=[])

added = queued = 0
for t in traces:
    trace_id = Langfuse.create_trace_id(seed=t.trace_id)
    if t.scores["citation_hallucination"] == 1:
        lf.create_dataset_item(dataset_name="support-regressions", input={"message": t.question},
                               metadata={"route": t.route, "release": t.release}, source_trace_id=trace_id)
        added += 1
    elif t.scores["retrieval_quality"] < 0.5 and t.outcome == "abandoned":
        lf.api.annotation_queues.create_queue_item(queue.id, object_id=trace_id, object_type="TRACE")
        queued += 1
print("added to dataset:", added)
print("sent to a person:", queued)
```

```text
added to dataset: 21
sent to a person: 33
```

**Prompt management** lets you change a prompt without a deploy, and it records the prompt version on each generation so a score can be traced to a wording. Always pass a fallback, so a Langfuse outage degrades to the local copy instead of breaking the agent. Fetch inside a lazy factory so the client exists before the agent is constructed, and cache for the process lifetime rather than fetching per request. The SDK also keeps its own short cache.

```python
from support_agent.fakes import offline_langfuse

lf, capture = offline_langfuse()
AGENT_INSTRUCTION = "You are the Acme Books support agent. Answer from the help centre, and cite it."

prompt = lf.get_prompt("agent_instruction", fallback=AGENT_INSTRUCTION, type="text")
print("served from the fallback:", prompt.is_fallback)
print(prompt.compile())
```

```text
served from the fallback: True
You are the Acme Books support agent. Answer from the help centre, and cite it.
```

The fake server has no such prompt, so this shows the failure path, which is the one you need to know works.

---

## Keeping traces safe and affordable

Traces hold customer messages, invoice data and tool arguments. The client takes a `mask` function, applied to inputs, outputs and metadata before anything is exported. Run it in the client rather than on the server, since then the data never leaves. `sample_rate` keeps a fraction of traces, and `should_export_span` filters individual spans.

```python
import re
from langfuse import Langfuse
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")

def mask(*, data, **kwargs):
    return EMAIL.sub("<email>", data) if isinstance(data, str) else data

exporter = InMemorySpanExporter()
lf = Langfuse(public_key="pk-lf-local", secret_key="sk-lf-local", base_url="http://langfuse.invalid",
              span_exporter=exporter, mask=mask)
with lf.start_as_current_observation(name="agent_turn", as_type="agent", input="Reset the login for a.jensen@example.dk"):
    pass
lf.flush()
print(exporter.get_finished_spans()[0].attributes["langfuse.observation.input"])
lf.shutdown()
```

```text
Reset the login for <email>
```

Be careful with sampling. It is fine for volume, but it discards the rare failures you most want, and it makes per-trace cost totals wrong unless you scale them back up. Keep every trace that errored, and sample the healthy ones. If you can't decide that at the point of export, sample nothing, and shorten retention instead.

---

## Pitfalls

| Pitfall | What happens | Instead |
|---|---|---|
| Following a v2 tutorial | `lf.trace()`, `lf.score()` and `langfuse.decorators` raise errors on v5 | Use `start_as_current_observation`, `create_score` and `from langfuse import observe` |
| No `flush()` in a script or job | The last batch is lost, and you see missing traces with no error | Flush on exit; `shutdown()` in long-lived services |
| Summing usage buckets twice | Reporting `input` as the total prompt size counts cached tokens twice, because the total is derived | Keep buckets exclusive, and map the API's fields one to one |
| A `ContextVar` that is never reset | The next turn on the same worker writes into the previous trace | Reset in `finally` |
| Trusting a score nobody has measured | A heuristic with poor precision on one language becomes a false regression | Measure precision and recall on labelled traces, per segment |
| Logging raw customer data by default | Traces become the least protected copy of your most sensitive data | `mask` in the client, `capture_input=False` where it's sensitive |
| Rendering only the final answer | Retry loops and stalled tools stay invisible when the answer is right | Read trees, and count `ERROR` and `WARNING` spans |

---

## Try it

Run these from [practice/](../practice/) with the command in its [README](../practice/README.md).

1. Find the most expensive turn of the fortnight that was not a retry loop, and print its tree. What explains its cost?

   <details><summary>Answer</summary>

   Use `max((t for t in generate_traces() if t.seeded_failure != "retry_loop"), key=lambda t: t.cost_usd)`. It falls in `v2.0`, with `read=0 write=4200` on the answer generation and a long answer. The cost comes from cache writes plus output tokens, and no failure was needed.

   </details>

2. Send a healthy turn and a retry-loop turn through `replay()` with an offline client. How many spans does each produce, and which attribute would you filter on to count the failures?

   <details><summary>Answer</summary>

   One span per tree row plus the root: 7 for the first healthy turn and 13 for the retry loop. Filter on `langfuse.observation.level` equal to `ERROR`, or in the UI, on observation level.

   </details>

3. Remove the `turn_root.reset(token)` line from the `ContextVar` block and call `handle` twice inside a single task, printing `turn_root.get()` between calls. What goes wrong?

   <details><summary>Answer</summary>

   After the first call, `turn_root` still holds the closed root. Any tool that runs outside a turn on that context would create an observation under a finished trace. That is why the reset is in `finally`, so it also runs when the runner raises.

   </details>

---

## Interview checklist

| Question | A good answer |
|---|---|
| What is the difference between a trace and an observation? | A trace is one request end to end, and observations are the spans, generations and tool calls nested in it. The root observation supplies the trace's input and output |
| Why not rely on logs? | Logs record events, while a trace records causation and nesting: which search fed which answer, at what token cost. Agents are non-deterministic, so you can't reproduce a turn to debug it later |
| How do you trace tools in a framework that runs its own event loop? | Hold the root in a `ContextVar`, open children from that object with `start_observation`, and reset in `finally`. Then test that children share the trace id and parent |
| How are cached tokens reported to Langfuse? | As separate exclusive usage keys. The API's `input_tokens` excludes cache reads and writes, so the total is the sum of all three |
| Would you put one tracing wrapper over all frameworks? | No. Native instrumentation has more depth. Standardise the metadata keys, and accept the cost of joining at analysis time |
| What should you check about a heuristic score before alerting on it? | Precision and recall on labelled traces, per segment, because a check that is fine in one language can be mostly false alarms in another |
| How do you stop personal data reaching the trace store? | A client-side `mask` function, plus `capture_input=False` on sensitive functions, so the data never leaves the process |

---

## Next

→ [02-scoring-datasets-experiments.md](02-scoring-datasets-experiments.md): turning traces into scores, a golden dataset into experiment runs, and two versions of the agent into a comparison that finds what the average hides.
