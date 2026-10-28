---
origin: web-authored
sources:
  - https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph
  - https://docs.langchain.com/langgraph
  - https://flowtivity.ai/blog/graph-engineering-2026-guide-openclaw-codex/
  - https://www.aibuilderclub.com/blog/graph-engineering-with-claude-code
  - https://code.claude.com/docs/en/sub-agents
confidence: medium
cleaned: 2026-10-28
---
# 5 — Topology Patterns

> The handful of shapes that recur, what each costs, how each fails, and how the same shapes look in Claude Code.

---

## The catalogue

| Pattern | Shape | Use when | Costs | Fails by |
|---|---|---|---|---|
| **Generate-then-verify** | produce → check → back-edge | The job splits into a produce step and an independent check | One extra node per cycle | Checker sees the producer's reasoning and agrees with it |
| **Supervisor** | router → specialists → router | Work arrives in several kinds that need different handling | A routing call per turn | Mis-routing; the supervisor becomes a bottleneck |
| **Fan-out / fan-in** | split → N parallel workers → merge | Many independent items, then one combined result | Tokens scale with N | Missing reducer; redundant findings; correlated errors |
| **Hierarchical** | a subgraph as one node of a parent | A sub-topology is reused or owned by another team | State mapping at the boundary | Hidden cost; failures inside the subgraph are hard to see from outside |
| **Handoff** | agent writes status → edge reads it | Agents should pass control without knowing each other | A status key in the schema | Status values drift; nobody handles an unexpected one |

### Generate-then-verify

The highest-yield first graph ([02](02-graph-primitives.md#the-first-graph-generate-then-verify)). Draft-then-review, research-then-write, build-then-test. **The separation creates the value; parallelism is a bonus.** Put deterministic checks before the LLM checker, and bound the back-edge.

### Supervisor

A coordinator node classifies each incoming task and dispatches it to a specialist, then decides whether the work is done or needs another specialist. It is the settled baseline for most multi-agent work: the orchestrator holds the plan, and the workers run in isolated contexts. n8n's AI Workflow Builder is a production example: a supervisor routing to five specialist subgraphs ([08](08-governance-and-production.md#case-study-n8ns-ai-workflow-builder)).

Specialise by prompt first. n8n runs every specialist on the same model at temperature 0, and the roles differ only by system prompt. A separate model per node is an optimisation you justify with measurements, not the starting point.

### Fan-out / fan-in

Several workers run at once on independent branches, and a synthesiser merges their results into shared state. It wins on wall-clock time and costs tokens. Use `Send` when N is only known at runtime, and give the merge key a reducer ([03](03-state-and-reducers.md#dynamic-fan-out-the-send-api)).

**The parallel review graph** is the canonical fan-out: a planner sets objectives, a worker produces, then security, logic and style reviewers run **in parallel**, a synthesiser collects their findings, and a pass/fail gate routes feedback back to the worker. flowtivity reports it as ~3× faster than the sequential version on code review. Measure it yourself before quoting the number ([Lab 4](../practice/01-agent-graph-labs.md#lab-4--subgraphs-and-the-parallel-review-graph)).

### Hierarchical: subgraphs

A compiled graph can be added as a node in another graph. That gives you nested orchestration and reusable sub-topologies: build the review graph once, then drop it into any pipeline that needs review.

```python
review = review_builder.compile()          # a whole graph
parent.add_node("review", review)          # used as one node
```

How state crosses the boundary:

| Parent and child schemas | What to do |
|---|---|
| **Share keys** | Add the compiled subgraph directly; shared keys flow in and out |
| **Differ** | Call the subgraph inside a wrapper node that maps parent state → child input and child output → parent update |

The wrapper is more code, and usually worth it: it makes the subgraph's contract explicit, and it stops a child from writing parent keys it shouldn't touch.

### Handoff

An agent signals completion by writing a designated state key; a conditional edge reads that key and picks the next agent ([03](03-state-and-reducers.md#handoffs-live-in-state)). Coupling lives in state, not in code. Always route unknown status values to an explicit error node rather than letting the router throw.

---

## The same patterns in Claude Code

The concepts already exist in Claude Code under different names:

| Graph concept | Claude Code |
|---|---|
| **Node** | A subagent: *"a separate agent instance with its own context window, its own system prompt, and scoped tool access"* |
| **Edge** | The main session's decision about which subagent to spawn, when, and with what brief |
| **State** | Return values: *"a subagent's final output flows back to the orchestrator, which passes the relevant piece to the next node"* |
| **Deterministic edge** | A hook: when probabilistic routing isn't good enough, a hook *guarantees* the transition |
| **Programmatic topology** | The Claude Agent SDK: define the graph in code, so it can run unattended and be tested |

Three implementation levels, in increasing order of determinism:

1. **Markdown subagents** in `.claude/agents/`: the fastest way to stand up a multi-node graph.
2. **Hooks as deterministic edges**: a pass/fail gate that runs code, not a model.
3. **Agent SDK**: a programmatic graph for unattended operation.

What you lose compared with LangGraph: there is no typed shared state, no reducers, and no checkpoints. State is whatever the orchestrator chooses to pass along, which is a context firewall when you want one ([03-harness note 07](../../03-harness-engineering/notes/07-orchestration.md)) and a liability when you need resume.

This workspace already runs the fan-out pattern: `/akira` (parallel haiku scanners), `/workflow-research fan-out` (parallel scouts) and `/workflow-review` (a multi-reporter pipeline). Each is a parallel review graph with a synthesiser node.

---

## Choosing a pattern

1. Is there a produce step and an independent check? → **generate-then-verify**. Start here.
2. Do tasks arrive in different kinds? → **supervisor** over specialists.
3. Are there many independent items? → **fan-out / fan-in** with a reducer.
4. Is a sub-topology reused, or owned by someone else? → **subgraph** with a wrapper node.

Patterns compose. A supervisor can dispatch to a fan-out subgraph whose workers each run generate-then-verify. Add each layer only when one of the five signals in [01](01-graph-vs-loop.md#the-default-plus-an-escalation-rule) forces it.

---

## Working reference

`~/.claude/refs/agent-architecture.md` — subagent criteria, orchestrator-holds-plan baseline, dynamic fan-out.

---

→ Next: [06-when-not-to-build-a-graph.md](06-when-not-to-build-a-graph.md) — the negative case, and what fan-out really costs.
