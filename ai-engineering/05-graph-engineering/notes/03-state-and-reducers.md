---
origin: web-authored
sources:
  - https://docs.langchain.com/langgraph
  - https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph
  - https://youmind.com/landing/x-viral-articles/graph-engineering-ai-agent-loops
confidence: medium
cleaned: 2026-10-28
---
# 3 — State and Reducers

> State is the substrate nodes coordinate through. Reducers are the concurrency primitive: they decide what happens when two branches write the same key.

---

## State is the substrate

> LangGraph is *"a state machine where the graph defines the workflow, the state that moves through it, and the transitions between steps."*

State is a typed, shared structure that persists across node executions within a run. Nodes read it and return updates; edges route on it. It replaces the message-passing overhead of naive multi-agent designs, where every agent forwards its full transcript to the next.

```python
from typing import Annotated, TypedDict
import operator

class ReviewState(TypedDict):
    task: str                                      # set once, read by everyone
    draft: str                                     # one writer: the generator
    findings: Annotated[list[str], operator.add]   # many writers: merged by a reducer
    attempts: int                                  # the bound on the cycle
```

Design the schema the way you'd design a database table: name each key, give it a type, and decide **who writes it** before writing any node.

| Lifetime | Holds | Where it lives |
|---|---|---|
| **Short-term** (in-run) | Working memory for this run: draft, findings, attempt count | Graph state, checkpointed per step ([04](04-durable-execution-and-interrupts.md)) |
| **Long-term** (cross-run) | Facts and preferences that outlive a run | A store outside the graph (note 12, planned; [02-context note 06](../../02-context-engineering/notes/06-memory.md)) |

**State is not context.** State is what the graph stores. Context is what you choose to load from it into a given node's prompt. A reviewer node should see the draft and the task, not every key in state ([07](07-failure-modes-at-scale.md#verifiers-need-isolated-context)). Deciding what each node sees is [context engineering](../../02-context-engineering/README.md) applied per node.

---

## Reducers decide merges

When a node returns `{"key": value}`, the framework has to combine that value with what's already there. The rule for each key is its **reducer**:

| Key declared as | Merge rule | Use for |
|---|---|---|
| `draft: str` (no reducer) | **Overwrite**: the new value replaces the old | Keys with exactly one writer |
| `Annotated[list, operator.add]` | **Append**: lists are concatenated | Findings, logs, results from parallel workers |
| `MessagesState` / `add_messages` | Append, but replace a message with a matching ID | Conversation history |
| `Annotated[T, my_fn]` | Whatever `my_fn(old, new)` returns | Dedupe, max-score-wins, merge-by-key |

A custom reducer is a plain function of two arguments:

```python
def dedupe(old: list[str], new: list[str]) -> list[str]:
    seen = set(old)
    return old + [x for x in new if x not in seen and not seen.add(x)]

findings: Annotated[list[str], dedupe]
```

---

## Parallel writes without a reducer race

LangGraph runs a graph in **super-steps**. Every node scheduled for the same super-step runs in parallel, and their updates are applied together when the step ends. If two of them write a key that has **no reducer**, there is no rule for which one wins, and LangGraph refuses: it raises `InvalidUpdateError` rather than silently dropping one write.

That error is the framework doing you a favour. The same bug in a hand-rolled multi-agent system (two agents writing one file, one dict, one row) doesn't raise; it just loses work.

> **Rule: every key has either exactly one writer or an explicit reducer.**

This is the single-writer rule from `~/.claude/refs/agent-memory.md`, enforced at the schema. In production the same rule shows up as optimistic locking: n8n's workflow builder rejects a write unless it carries the `versionId` and `expectedChecksum` it read ([08](08-governance-and-production.md#case-study-n8ns-ai-workflow-builder)), which is single-writer enforced by compare-and-swap instead of by convention.

---

## Dynamic fan-out: the Send API

Static edges fix the topology at build time. Often you only learn how many workers you need at runtime: one reviewer per changed file, one summariser per retrieved document. LangChain's phrase is *"mixing known structure with runtime variability."*

`Send` lets a conditional edge return a **list of tasks**, each with its own input:

```python
from langgraph.types import Send

def fan_out(state: ReviewState) -> list[Send]:
    return [Send("review_file", {"path": p, "task": state["task"]})
            for p in state["changed_files"]]

builder.add_conditional_edges("plan", fan_out, ["review_file"])
builder.add_edge("review_file", "synthesize")
```

Each `review_file` instance runs in parallel with its own private input, and each returns `{"findings": [...]}`. Because `findings` has an `operator.add` reducer, all their results land in one list before `synthesize` runs. Without the reducer, this exact graph raises on the first run with two files.

Fan-out and reducers are one feature: **Send creates the parallel writers, the reducer makes their writes safe.**

---

## Handoffs live in state

The handoff protocol is how agents pass control without knowing about each other: an agent signals it is done by writing a designated key, and a conditional edge reads that key to choose the next agent.

```python
def route(state) -> str:
    return {"needs_research": "researcher",
            "needs_review":   "reviewer",
            "done":           END}[state["status"]]
```

The coupling lives in the **state schema**, not in agent code. You can swap the reviewer for a different one, or add a new status, without touching the agents on either side.

---

## Which edges are real

Not every sequential step is a dependency. The test for each edge:

> **Does the next step actually read the previous step's output?**

If yes, it is a **true dependency** and the edge is real. If no, the ordering is incidental: the steps were written in sequence because that's how a person would do them, and they belong in a fan-out. Most pipelines that "need" to be sequential have one or two real edges and several incidental ones.

---

## Working reference

`~/.claude/refs/agent-memory.md` — state lifetimes, single-writer rule, memory vs. context.

---

→ Next: [04-durable-execution-and-interrupts.md](04-durable-execution-and-interrupts.md) — checkpointers, and why pause, resume and replay are one mechanism.
