---
origin: planning
sources:
  - https://docs.langchain.com/langgraph
  - generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main/
confidence: medium
cleaned: 2026-10-28
---
# P1 — Agent Graph Labs

> One graph, grown a chapter at a time. Generate-then-verify gains state, checkpoints, a subgraph, fault guards and tracing.

These labs continue the [loop labs](../../04-loop-engineering/practice/01-exercises.md). Warm up with the LangGraph course notebooks in [AI-Agents-in-LangGraph-main](../../../generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main/) (Lesson 1 ReAct from scratch, Lesson 2 LangGraph components, Lesson 4 persistence and streaming) if LangGraph is new to you.

---

## Ground rules

- **One task, one model** for all labs, so the topology is the only thing that changes. Pick a task with a checkable output: code with tests, JSON against a schema, a summary graded against a rubric.
- **Branch per lab**: `graph-gtv`, `graph-fanout`, `graph-checkpoint`, `graph-subgraph`, `graph-breakeven`, `graph-faults`, `graph-trace`.
- **Measure every run.** The point of each lab is a number, not a working demo.
- Run the templates with `uv run --with langgraph --with langchain-anthropic python <file>`.

A run log, one row per run:

```markdown
| Lab | Topology | Runs | Pass rate | Tokens / run | Wall-clock / run | Stop reason | Notes |
|---|---|---|---|---|---|---|---|
```

---

## Lab 1 — Generate-then-verify

*Notes [01](../notes/01-graph-vs-loop.md), [02](../notes/02-graph-primitives.md).*

1. Re-express your 04-loop agent loop as a `StateGraph` with **one node and a conditional self-edge**. Confirm it behaves the same. A loop is a one-node graph.
2. Copy [templates/generate-then-verify.py](../templates/generate-then-verify.py). Put real deterministic checks in `validate`.
3. **Agency audit.** Find one LLM call that could be code, or one agent that could be a single call. Change it. Record the change in tokens and in run-to-run variance over 10 runs.

**Done when:** you can say which node is the most expensive and whether it needs to be.

## Lab 2 — Fan-out and merge

*Note [03](../notes/03-state-and-reducers.md).*

1. Run [templates/fan-out-merge.py](../templates/fan-out-merge.py). Remove the reducer on `findings` and run again; read the `InvalidUpdateError`.
2. Replace `operator.add` with a custom dedupe reducer, and give two items the same finding to prove it works.
3. **True-dependency test.** Take a sequential pipeline you own. Mark each edge "reads previous output" or "incidental". Rewrite the incidental ones as a fan-out and measure wall-clock time.

**Done when:** every key in your state has one writer or a reducer, and you can say which.

## Lab 3 — Checkpoint and interrupt

*Note [04](../notes/04-durable-execution-and-interrupts.md).*

1. Swap `InMemorySaver` for a SQLite checkpointer (`langgraph-checkpoint-sqlite`).
2. Add a "publish" node that calls `interrupt()` before its side effect. Run to the interrupt, inspect with `get_state`, **edit** the draft with `update_state`, then resume with `Command(resume=...)`.
3. **Crash and resume.** Kill the process mid-run. Restart with the same `thread_id` and confirm it continues from the last checkpoint.
4. **Time travel.** Use `get_state_history` to find the checkpoint before a bad step. Fork from it with a corrected state.
5. Put a print statement before the `interrupt()` call and watch it run twice. Move the side effect so that doesn't matter.

**Done when:** a run survives a kill, and a human can correct it mid-run.

## Lab 4 — Subgraphs and the parallel review graph

*Note [05](../notes/05-topology-patterns.md).*

1. Build the parallel review graph: security, logic and style reviewers in parallel → synthesiser → pass/fail gate.
2. Compile it and embed it as **one node** in a parent planner → worker → review graph. Use a wrapper node that maps parent state to the subgraph's input.
3. Compare with a sequential version (the three reviewers in a row) over 10 runs: wall-clock time and tokens. Is it ~3× faster, as flowtivity claims?
4. **Same topology in Claude Code.** Re-implement the reviewers as `.claude/agents/` subagents, with a hook as the pass/fail gate. Write down what you lost (typed state, checkpoints) and what you gained.

## Lab 5 — Break-even measurement

*Note [06](../notes/06-when-not-to-build-a-graph.md).*

1. Run the same task as a single loop and as the Lab 4 graph, 20 trials each. Record tokens, wall-clock time and pass rate.
2. Make the task harder (or the model weaker) until the loop's pass rate drops. Find where the graph stops paying for itself.
3. **Split the verifier first.** Take a loop whose verifier judges several criteria. Split it into per-criterion checks *inside the loop* and measure. Only then compare with the graph.

**Done when:** you have your own break-even number, and you no longer need flowtivity's.

## Lab 6 — Fault injection

*Note [07](../notes/07-failure-modes-at-scale.md).*

Break the Lab 4 graph on purpose, one fault at a time:

| Fault | How | Expect | Guard |
|---|---|---|---|
| Oscillation | Two nodes that always route to each other | `GraphRecursionError` | Attempt counter + `recursion_limit` |
| Race | Two parallel branches write one key with no reducer | `InvalidUpdateError` | Reducer or single writer |
| Self-agreement | Give the reviewer the generator's reasoning | Pass rate up, quality down | Isolated reviewer context |
| Unbounded fan-out | `Send` over a 500-item list | Cost spike | Cap N |

For each, write how you detected it and the guard that fixed it.

**Anchor drill.** Add a frozen held-out set the graph can't edit. Let a reviewer prompt be tuned against the training set. Show the training score climbing while the held-out score falls.

## Lab 7 — Trace and attribute

*Note [08](../notes/08-governance-and-production.md).*

1. Instrument the Lab 4 graph so every model call carries `graph_id`, `run_id` and `node_id` (LangSmith, or OpenTelemetry spans).
2. Run it 10 times and produce a per-node cost table. Find the node that dominates spend.
3. Score the graph against the seven-question checklist in note 08. Fix the two weakest answers.

---

→ Track B labs (`02-knowledge-graph-labs.md`) are planned in [OUTLINE.md](../OUTLINE.md#practice-track).
