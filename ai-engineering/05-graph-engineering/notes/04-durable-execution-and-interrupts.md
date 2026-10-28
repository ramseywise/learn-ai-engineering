---
origin: web-authored
sources:
  - https://docs.langchain.com/langgraph
  - https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph
  - https://www.truefoundry.com/blog/graph-engineering-enterprise-guide
confidence: medium
cleaned: 2026-10-28
---
# 4 — Durable Execution and Interrupts

> A checkpointer saves state after every step. That one mechanism gives you human-in-the-loop pauses, resume after a crash, and time-travel debugging.

---

## Why a loop can't pause

A plain agent loop keeps its progress on the call stack and in a message list in memory. If it stops to wait for a human, or the process dies, that stack is gone. A loop that pauses *has nowhere to put its stack.*

The harness answer is to externalise state to files ([03-harness note 06](../../03-harness-engineering/notes/06-long-horizon-execution.md); [04-loop note 05](../../04-loop-engineering/notes/05-long-running-loops.md)). The graph answer is the same idea built into the runtime: because state is explicit and steps are discrete, the framework can save a complete snapshot after every step.

---

## Checkpointers

```python
from langgraph.checkpoint.memory import InMemorySaver
# production: SqliteSaver / PostgresSaver (langgraph-checkpoint-sqlite / -postgres)

graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "review-42"}}
graph.invoke({"task": "..."}, config)
```

| Term | Meaning |
|---|---|
| **Checkpoint** | A snapshot of the full state, saved at the end of every super-step |
| **Thread** | The sequence of checkpoints for one run, keyed by `thread_id` |
| **Resume** | Invoke again with the same `thread_id`; execution continues from the latest checkpoint |

The `thread_id` is the run's identity. Pick it deliberately (a ticket ID, a session key, `workflow-{id}-user-{id}`), because resuming means knowing it.

> **Rule: if a run can outlive the process that started it, compile with a persistent checkpointer.** `InMemorySaver` is for tests; it dies with the process.

---

## Three features, one mechanism

| Feature | What it does with checkpoints |
|---|---|
| **Human-in-the-loop** | Stop at a node, save, wait any length of time, resume with the human's input |
| **Resume after crash** | Restart with the same `thread_id`; continue from the last saved step |
| **Time travel** | List past checkpoints, inspect any of them, or fork a new run from one |

### Human-in-the-loop with `interrupt`

```python
from langgraph.types import interrupt, Command

def publish(state):
    decision = interrupt({"question": "Publish this?", "draft": state["draft"]})
    if decision != "approve":
        return {"status": "rejected"}
    send_to_cms(state["draft"])
    return {"status": "published"}

graph.invoke({"task": "..."}, config)              # runs until the interrupt, then returns
graph.invoke(Command(resume="approve"), config)    # later, maybe days later
```

While paused you can read the state with `graph.get_state(config)`, and **edit** it with `graph.update_state(config, {"draft": fixed})` before resuming. The human isn't limited to yes or no; they can correct the work.

There is also a static form, `compile(interrupt_before=["publish"])`, which pauses before a node runs. It's useful for debugging. Prefer `interrupt()` in production, because the node can pass the human exactly what they need to decide.

> **Gotcha: on resume, the interrupted node runs again from its first line.** Anything before `interrupt()` executes twice. Keep side effects after the interrupt, or make them idempotent.

### Time travel

`graph.get_state_history(config)` lists every checkpoint in the thread, newest first. Each has its own `checkpoint_id`. Invoking with that ID in the config replays from that point; calling `update_state` on an old checkpoint and then invoking creates a fork. This is the debugger: find the step where the run went wrong, change the state there, and rerun from that point instead of from the start.

---

## Where approval gates go

TrueFoundry's observation is the one to keep: *"human approval checkpoints before configured sensitive tool calls at exactly the edges where consequence concentrates."*

Consequence is not spread evenly across a graph. It concentrates at a few edges: sending, publishing, paying, deleting, deploying. Put the gate **there**, not on every node. A gate everywhere trains the human to click approve without reading, which is worse than no gate.

| Gate before | Why |
|---|---|
| Irreversible actions (send, pay, delete, deploy) | Can't be undone, so check first |
| Actions crossing a trust boundary (external API, another tenant) | Someone else bears the cost |
| Low-confidence router decisions | Cheap for a human, expensive to mis-route |

n8n's workflow builder puts its one gate after the **Planner**, before any build work starts ([08](08-governance-and-production.md#case-study-n8ns-ai-workflow-builder)). The plan is the cheapest thing to correct.

---

## Checkpoint contents

Graph state checkpoints are only as useful as the state schema. To resume cleanly, state must hold everything the next step needs: the plan, which steps are complete, intermediate outputs, and run metadata (attempt counts, budget used). If a node depends on something held only in a Python variable or an open connection, a resume will lose it.

This matches the checkpoint rule in `~/.claude/refs/agent-reliability.md`: checkpoint after each plan step, and include plan state, completed steps, intermediate outputs and run metadata.

---

## Working reference

`~/.claude/refs/agent-reliability.md` — checkpointing, resumability. `~/.claude/refs/agent-memory.md` — state lifetimes.

---

→ Next: [05-topology-patterns.md](05-topology-patterns.md) — supervisor, fan-out, subgraphs, and how they look in Claude Code.
