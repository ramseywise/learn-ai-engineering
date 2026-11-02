# Worked Example: Deterministic Workflow Orchestration (40 min, offline)

> **Constraint note:** pure stdlib, stubbed LLM, no network. The interviewer supplies `classify_llm`, `retrieve_docs`, and `generate_llm` as stubs you call but don't implement.

**Format:** 40 min, browser editor, interviewer watching.
**Prompt:** *"Implement the orchestration for a support-answering system: classify the request, retrieve relevant docs, validate that retrieval was sufficient, then generate an answer. Some steps can fail. Make the failure behavior explicit."*

The MCQ pairing here is **workflow vs ReAct** — and the whole exercise is a test of whether you reach for the right one. Candidates who have read about agents tend to build a loop that lets the model decide the next step. That is the wrong answer to this prompt, and saying why is most of the grade.

---

## 0–5 min — name the architecture, then justify it

[NARRATE: "The step sequence is given and fixed — classify, retrieve, validate, generate. That means this is a deterministic workflow, not an agent. I'm not going to give a model control over the control flow, because there's no branching decision here that requires reasoning at runtime. A workflow is testable, traceable, and its cost is bounded — an agent loop is none of those, and I'd only reach for one if the step order genuinely depended on intermediate results."]

That paragraph, said in the first two minutes, is what separates a candidate who has *used* agents from one who has read about them. Then commit to the shape:

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import logging

log = logging.getLogger(__name__)


class Status(Enum):
    OK = "ok"
    DECLINED = "declined"        # ran correctly, cannot answer — not an error
    FAILED = "failed"            # a step broke


@dataclass
class Context:
    """Accumulating state passed through every step.

    One mutable object rather than threading five positional args through four
    functions — each step reads what it needs and writes what it produces.
    """
    query: str
    category: str | None = None
    docs: list[dict] = field(default_factory=list)
    answer: str | None = None
    status: Status = Status.OK
    reason: str | None = None
    trace: list[str] = field(default_factory=list)
```

[NARRATE: "I'm separating DECLINED from FAILED deliberately. 'We retrieved nothing so we're not going to guess' is the system working correctly — it should not page anyone. 'The classifier threw' is a genuine failure. If you collapse those into one error state you lose the ability to alert on the second without drowning in the first."]

That distinction is a production instinct and interviewers notice it immediately.

---

## 5–20 min — steps as a uniform interface

Each step takes a `Context` and returns a `Context`. Uniformity is what makes the runner trivial.

```python
Step = Callable[[Context], Context]


def classify(ctx: Context) -> Context:
    ctx.category = classify_llm(ctx.query)          # stub: returns a label string
    if ctx.category not in {"billing", "technical", "account"}:
        ctx.status = Status.DECLINED
        ctx.reason = f"unroutable category: {ctx.category!r}"
    ctx.trace.append(f"classify -> {ctx.category}")
    return ctx


def retrieve(ctx: Context) -> Context:
    ctx.docs = retrieve_docs(ctx.query, category=ctx.category)
    ctx.trace.append(f"retrieve -> {len(ctx.docs)} docs")
    return ctx


def validate(ctx: Context) -> Context:
    """The gate. Everything downstream assumes this passed."""
    if not ctx.docs:
        ctx.status = Status.DECLINED
        ctx.reason = "no documents retrieved"
    elif max(d.get("score", 0) for d in ctx.docs) < MIN_SCORE:
        ctx.status = Status.DECLINED
        ctx.reason = "retrieval below confidence threshold"
    ctx.trace.append(f"validate -> {ctx.status.value}")
    return ctx


def generate(ctx: Context) -> Context:
    ctx.answer = generate_llm(ctx.query, ctx.docs)
    ctx.trace.append("generate -> ok")
    return ctx
```

[NARRATE: "The validate step is the reason this architecture is worth anything. It's a gate between retrieval and generation — if retrieval was weak, we stop here rather than handing thin context to the model and getting a confident hallucination back. That's the single highest-value check in a RAG pipeline and it's four lines."]

[NARRATE: "I'm also appending to a trace at every step. When this misbehaves in production, the first question is always 'which step went wrong' — and if you didn't record it, you're guessing."]

---

## 20–30 min — the runner

```python
def run(ctx: Context, steps: list[Step]) -> Context:
    """Execute steps in order, short-circuiting on non-OK status.

    A step that raises is contained: the pipeline stops, records which step
    failed, and returns partial state rather than propagating.
    """
    for step in steps:
        if ctx.status is not Status.OK:
            log.info("short-circuit before %s: %s", step.__name__, ctx.reason)
            break
        try:
            ctx = step(ctx)
        except Exception as e:
            log.exception("step %s failed", step.__name__)
            ctx.status = Status.FAILED
            ctx.reason = f"{step.__name__}: {e.__class__.__name__}: {e}"
            ctx.trace.append(f"{step.__name__} -> raised")
            break
    return ctx


PIPELINE = [classify, retrieve, validate, generate]

result = run(Context(query="why was I charged twice?"), PIPELINE)
```

[NARRATE: "Three properties I want to point out. The pipeline is data — a list — so I can test any prefix of it, or reorder it, without touching the runner. Short-circuiting means a DECLINED at validate never reaches generate, so we never pay for a call we've already decided not to trust. And catching at the runner rather than inside each step means the steps stay readable and the error handling lives in exactly one place."]

[NARRATE: "I'm catching bare `Exception` here, which I'd normally avoid — the justification is that this is a top-level boundary whose job is to convert any failure into a status. It logs with `.exception` so the traceback survives, and it records which step raised. That's containment, not swallowing."]

**If asked "what about retries?"** — name where they go and why not everywhere:

[NARRATE: "Retries belong on the individual network-bound steps, not the whole pipeline — re-running classify because generate failed wastes a call and can produce a different category. I'd wrap the LLM-calling steps in a backoff decorator, and I'd only retry on transient errors: timeouts and 5xx, never on a validation error, because retrying a deterministic failure just burns quota. Past a failure threshold, a circuit breaker so we stop calling a dead dependency entirely and fail fast."]

That last sentence connects straight to the circuit-breaker MCQ and shows the concepts are linked in your head rather than memorized separately.

---

## 30–37 min — tests

The uniform step interface pays off here: every step is testable in isolation with a hand-built `Context`.

```python
def test_declines_when_no_docs():
    ctx = validate(Context(query="q", category="billing", docs=[]))
    assert ctx.status is Status.DECLINED
    assert "no documents" in ctx.reason

def test_short_circuits_before_generate():
    calls = []
    def spy(ctx):
        calls.append("generate")
        return ctx
    ctx = Context(query="q", status=Status.DECLINED, reason="test")
    run(ctx, [spy])
    assert calls == []                      # never ran

def test_step_exception_is_contained():
    def boom(ctx):
        raise ConnectionError("upstream down")
    ctx = run(Context(query="q"), [boom])
    assert ctx.status is Status.FAILED
    assert "ConnectionError" in ctx.reason

def test_trace_records_each_step():
    ctx = run(Context(query="q"), [classify, retrieve])
    assert len(ctx.trace) == 2
```

[NARRATE: "The short-circuit test uses a spy rather than asserting on output, because the property I care about is that generate was never *called* — that's a cost and safety guarantee, and you can't observe it from the return value alone."]

---

## 37–40 min — close

[NARRATE: "Next steps in priority order: backoff on the two LLM steps with a circuit breaker behind it; make MIN_SCORE configurable rather than a module constant, since it's a tuning knob that'll change with the corpus; and emit the trace as structured logs with a correlation id so a single request is greppable end to end. What I skipped deliberately: parallelism — the steps are strictly sequential here, and there's nothing to overlap. If retrieval fanned out across multiple sources I'd revisit that."]

**If the interviewer asks "when would you make this an agent?"** — the answer that lands:

[NARRATE: "When the step sequence stops being knowable in advance. If a request might need zero, one, or three retrievals depending on what came back — a comparison question needing two lookups, say — then the control flow genuinely depends on intermediate results and a loop with tool calls earns its cost. I'd still bound it: a max-iteration cap, a step budget, and the same validate gate before any answer goes out. The failure mode of an unbounded agent loop is a runaway spend, so the cap isn't optional."]

---

## What the interviewer is grading

| Signal | Where it appeared |
|---|---|
| Picked the right architecture | Named workflow-over-agent in minute 2, with the runtime-branching justification |
| Failure taxonomy | DECLINED vs FAILED separated — correct-refusal isn't an error |
| The gate | validate between retrieval and generation, and why it's the highest-value check |
| Observability | trace appended per step; "which step failed" answerable without a debugger |
| Containment | Runner catches, logs with traceback, records the failing step — not a swallow |
| Composability | Pipeline is a list; steps share one interface; any prefix is testable |
| Cost awareness | Short-circuit avoids the generate call; retries scoped to network steps only |
| Knows when to escalate | Can state the conditions under which an agent *would* be right, with bounds |

The weakest version builds a `while` loop that asks a model "what should I do next?", has no validate gate, and cannot answer "which step failed?" when asked.
