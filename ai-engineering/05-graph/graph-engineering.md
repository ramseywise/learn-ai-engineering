---
origin: web-authored
sources:
  - https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph
  - https://www.truefoundry.com/blog/graph-engineering-enterprise-guide
  - https://www.eigent.ai/blog/graph-engineering-ai-agents
  - https://flowtivity.ai/blog/graph-engineering-2026-guide-openclaw-codex/
  - https://www.aibuilderclub.com/blog/graph-engineering-with-claude-code
  - https://medium.com/@GaoDalie_AI/forget-loop-engineering-graph-engineering-is-about-this-713a9cf2e985
  - https://addyosmani.com/blog/loop-engineering/
  - https://langchain-ai.github.io/langgraph/
  - https://docs.langchain.com/langgraph
  - https://www.explainx.ai/post/graph-engineering
confidence: high
cleaned: 2026-07-29
---

# Graph Engineering — deep note

## 1. Definition and where it sits

Graph engineering is designing the **topology** of a multi-agent system: which nodes exist,
which transitions between them are permitted, and how the runtime work graph forms and
mutates. Where loop engineering asks *"what cycle re-prompts this agent and decides when it
quits?"*, graph engineering asks *"who is allowed to hand work to whom, under what
condition, carrying what state?"*

Three framings worth holding together:

- **TrueFoundry (structural framing):** *"Graph engineering designs the topology of a
  multi-agent system — which nodes exist (agents, deterministic functions, routers, human
  checkpoints), which transitions are permitted, and how runtime work graphs form and
  mutate."*
- **LangChain (control framing):** graphs let you *"impose your preconceptions of how the
  system should work into more constrained paths, not relying solely on the judgement of the
  LLM."* Representing agentic systems as graphs is *"a very reasonable way to harness the
  power of LLMs"* because it lets you *"more tightly control behavior when you want the
  agent to follow specific paths."*
- **Eigent (control-theory framing):** *"Graph engineering is the craft of wiring many
  feedback loops — metrics, evals, audits, policies, and workflows — into a network where
  they watch, constrain, and correct one another."*

Position in the progression: prompt → context → harness → loop → **graph**. The harness
([03-harness](../03-harness/README.md)) supplies tools, state, and guardrails; the loop
([04-loop](../04-loop/README.md)) decides how many times to use them and when to stop; the
graph decides *which loop runs next and who is accountable for it.* Each layer presumes the
one below — you cannot graph-engineer effectively without loop-engineering fluency.

> **Inherits the weaknesses of loop engineering.** A graph routing between unreliable loops
> inherits every loop failure at organizational scale, and adds coordination failure on top.

### The relationship is containment, not replacement

LangChain's sharpest line from three years of LangGraph: **"A loop is just a directed,
cyclic graph."** Loop engineering and harness engineering are variations of graph-based
thinking, not rivals to it. The Medium framing ("forget loop engineering") overstates the
break; TrueFoundry's is more accurate — loop and graph engineering are *"complementary
layers, not substitutes."*

What actually changes at the boundary is the failure mode you're engineering against. A
single loop fails by not converging. A graph fails by mis-routing, deadlocking, double-
writing shared state, or losing accountability for a decision. Gao Dalie's diagnosis of why
teams hit the wall: **"It's not that the agents aren't smart enough, but rather that the
organizational structure isn't clear enough."**

### Where loop ends and graph begins

You are in graph territory once you need **more than one agent collaborating with
conditional handoffs and shared state across that collaboration.** A single agent with a
tool loop is loop engineering. Multiple agents with routing logic between them is graph
engineering. The flowtivity decision rule is narrower and more useful in practice: reach for
a graph when you have a **complex task with 3+ independent verification or research steps**.
Below that bar, a sequential loop is cheaper and simpler.

---

## 2. Production agents are not DAGs

The single most load-bearing lesson from LangChain's three years shipping LangGraph:

> **"Production agents need cycles: retrying failed tool calls, asking users for missing
> information, revising answers after validation, calling tools repeatedly until they have
> enough context."**

This is why the airflow/DAG mental model imported from data engineering breaks on agents. A
DAG is acyclic by definition; a production agent must be able to go A → B, discover B failed,
return to A, and only then reach C. **Graph engineering for agents is cyclic-graph
engineering.** Anything that forbids cycles is a workflow engine, not an agent framework.

The second lesson is that **static edges are insufficient.** Real systems need *"mixing
known structure with runtime variability"* — the set of nodes to run is often not known
until runtime (fan out over N retrieved documents, spawn one reviewer per changed file).
Hence LangGraph's **Send API**: a node can *"route work to one or more downstream nodes
dynamically, without statically defining every transition."*

---

## 3. Core primitives

### Nodes

> **"Nodes do work. A node can be deterministic code, a single LLM call, a tool call, or a
> full agent with its own internal loop."**

This heterogeneity is the point, not an implementation detail. LangChain's docs-agent
example deliberately mixes node types — a fixed API call, a single LLM call with no tools,
and a full agent node for the open-ended part — producing a system that is *"predictable,
powerful, and efficient."* The design skill is deciding, per node, **how much agency to
spend.** Every node that could be deterministic code and isn't is a node you pay tokens and
variance for.

TrueFoundry's node taxonomy for production systems:

| Node kind | Purpose | Determinism |
|---|---|---|
| Agent | Open-ended reasoning with its own tool loop | Low |
| Deterministic function | Parsing, validation, formatting, API calls | Total |
| Router | Classify and dispatch | Medium (single LLM call or rules) |
| Human checkpoint | Approval before a consequential action | External |

### Edges

Edges define which node executes next. Some are deterministic (always A → B); others are
**conditional**, reading node results or accumulated state to choose. In LangGraph:
`add_conditional_edges(source_node, routing_function, {result_value: target_node})`.

Conditional edges are what buy you:

- **Adaptive branching** — route to a specialist based on intent classification.
- **Error paths** — route to a retry or repair node on tool failure.
- **Approval gates** — route to a human-in-the-loop node before an irreversible action.
- **Early exit** — route straight to `END` when a stopping condition is met.

### State

State is a shared data structure (e.g. `MessagesState`) that persists across node executions
within a run. Nodes transform state; edges route on it. The framework is *"a state machine
where the graph defines the workflow, the state that moves through it, and the transitions
between steps."*

- **Short-term** — working memory for reasoning within a run.
- **Long-term** — persistence across sessions; runs resume after interruption or failure.
- **Reducers** — control how state is merged when multiple branches write the same key. This
  is the concurrency primitive: without a reducer, parallel fan-out into one key is a race.

State is the substrate that replaces message-passing overhead in naive multi-agent designs.
It is also where the [`agent-memory.md`](~/.claude/refs/agent-memory.md) single-writer rule
bites hardest — designate one writer per key, or use a reducer that makes multi-writer
merging explicit.

### Durable execution and interrupts

Human-in-the-loop is a first-class graph primitive, not a UI feature: the graph pauses at a
designated node, a human inspects and may modify state, and execution resumes. This requires
**stateful persistence across the pause** — a capability loops alone cannot provide, because
a loop that pauses has nowhere to put its stack. Checkpointers are what make interrupts,
resume-after-crash, and time-travel debugging all the same mechanism.

### Typed edges (knowledge-graph side)

Flowtivity's contribution is on the KG side of the discipline: **"the edge type IS the
knowledge."** Untyped edges carry minimal reasoning value. Six edge types they claim every
production graph needs:

| Edge type | Meaning |
|---|---|
| `SUPERSEDES` | this replaces that |
| `DEPENDS_ON` | this needs that |
| `DECIDED_BY` | this was chosen because |
| `CAUSED` | this created that |
| `IMPLEMENTS` | this realises that |
| `REFERENCES` | this mentions that |

They report adding relationship semantics improves reasoning accuracy by ~18%. Treat the
specific number as vendor-adjacent, the principle as sound.

---

## 4. Topology patterns

- **Supervisor** — a coordinator node routes tasks to specialist workers by task type and
  aggregates results. The settled baseline for most multi-agent work.
- **Parallel fan-out / fan-in** — multiple agents run simultaneously on independent branches;
  a synthesizer merges into shared state. Wins wall-clock, costs tokens.
- **Hierarchical (team-of-teams)** — a subgraph is itself a node in a parent graph, enabling
  nested orchestration and reusable sub-topologies.
- **Handoff protocol** — an agent signals completion by writing a designated state key; the
  conditional edge reads that key to pick the next agent. Keeps coupling in state, not code.
- **Parallel review graph** (flowtivity's worked example) — planner defines objectives →
  worker executes → three reviewer nodes (security, logic, style) run **in parallel** →
  synthesizer collects → pass/fail gate routes feedback. Reported ~3× faster wall-clock than
  the sequential equivalent on code review.

### Generate-then-verify is the highest-yield first graph

Both the Claude Code and flowtivity write-ups converge on the same advice for a first graph:
pick a job that **splits naturally into a produce step and an independent check step** —
draft-then-review, research-then-write, build-then-test. The separation is what creates the
value; the parallelism is a bonus.

---

## 5. When NOT to build a graph

LangChain is explicit that some work is too fluid to pin down:

> Generic deep research **"requires planning and delegation in ways that are hard to pin down
> ahead of time"** — forcing agentic tasks **"into deterministic paths is the wrong move."**
> Use an agent harness instead.

The heuristic: **structure what you know, leave agency where you don't.** If you cannot name
the nodes before the run starts and the Send API can't derive them from a known step, you
want a harness with a good loop, not a graph.

Cost is the other gate. Flowtivity's tradeoff table:

| Metric | Loop | Graph |
|---|---|---|
| Wall-clock time | High | Low |
| Token cost per cycle | Lower | ~3× higher |
| Break-even pass rate | — | ~50% |

Graphs win on cost when per-cycle success rates are 50%+; they lose on simple, low-pass-rate
tasks where you're paying fan-out cost for work that will be redone anyway. Anthropic's own
multi-agent research system runs at *"roughly 15× the tokens of a chat turn"* — graph
engineering **requires genuine job separation to justify the overhead.**

---

## 6. Failure modes at scale (Eigent)

Eigent's contribution is a control-theory reading of why independent loops degrade once
there are many of them. Four structural failures:

1. **Goodhart's Law** — metrics detach from their original meaning under aggressive
   optimization.
2. **Upward blindness** — a loop cannot question its own targets or reference values.
3. **Inter-loop conflict** — independent loops fight over shared resources with no awareness
   of each other.
4. **Measurement decay** — sensors drift and definitions shift while loops keep running on
   stale data.

Their four design principles, which read as the governance layer of graph engineering:

| Principle | Description |
|---|---|
| **Paired metrics** | Every optimization metric gets a counter-metric and an anchor metric |
| **Owned references** | Targets are owned by slower loops, so objectives can't change silently |
| **Separated cadences** | Fast loops *escalate* to slower loops rather than overriding them |
| **Frozen nodes** | Some measurements are intentionally non-tunable |

### Anchors

**Anchors are "external fixed nodes the internal machinery is forbidden to rewrite."**
Held-out test sets, physical inventory counts, banked revenue, safety specifications.
Without anchors a graph becomes *"perfectly self-consistent while drifting arbitrarily far
from reality."*

This maps directly onto the 不易 (immutable) layer in [`/sanyi`](~/.claude/skills/sanyi/) —
the invariants that must never become configurable. An anchor made tunable is an anchor that
will eventually be tuned.

---

## 7. Production and governance (TrueFoundry)

The enterprise angle is mostly about **attribution**: once work fans out across nodes,
"the graph did it" is not an acceptable audit answer.

### Identity and tracing
Every independently governed caller needs a resolved identity. Gateway-mediated model and
MCP calls must carry stable `graph_id`, `run_id`, and `node_id` identifiers so orchestration
traces correlate with gateway records for cost, policy, latency, and tool use. That
propagation is what makes node-level cost attribution possible at all.

### Cost control
Work graphs amplify spend through fan-out, retries, and dynamically spawned subtasks. Budget
rules need to operate at tenant/team scope with separate limits per virtual account or
metadata value — a per-run cap is not enough when one run can spawn fifty nodes.

### Structural checkpoints
Approval gates at sensitive tool transitions are, in TrueFoundry's read, a genuinely new
security pattern: *"human approval checkpoints before configured sensitive tool calls at
exactly the edges where consequence concentrates."* The insight is that **consequence
concentrates at specific edges**, so that's where the gate belongs — not uniformly across
every node.

### Production checklist

1. Does every independently governed caller have a resolved identity?
2. Do gateway-mediated model and MCP calls carry stable graph, run, and node identifiers?
3. Does the orchestrator record the **actual runtime work graph** (not just the declared one)?
4. Can orchestration traces be correlated with gateway cost, policy, latency, and tool records?
5. Are graph- or node-associated budget rules mapped through virtual accounts or metadata?
6. Are sensitive tool actions protected by explicit approval checkpoints?
7. Are model changes isolated behind virtual-model routing?

Production readiness requires *"explicit ownership across orchestration, identity, policy,
budgets, approvals, and evidence."*

---

## 8. Graph engineering in Claude Code

The Claude Code mapping is direct — the concepts already exist in the harness under
different names:

- **Subagents are nodes.** *"Each subagent is a separate agent instance with its own context
  window, its own system prompt, and scoped tool access."*
- **Orchestration decisions are edges.** *"Your main Claude session is itself a node, and its
  decisions about which subagent to spawn, when, and with what brief are the edges."*
- **State flows by return value.** *"A subagent's final output flows back to the orchestrator,
  which passes the relevant piece to the next node."*

Three implementation levels, in increasing order of determinism:

1. **Markdown subagents** in `.claude/agents/` with YAML frontmatter — fastest way to stand
   up a multi-node graph.
2. **Hooks as deterministic edges** — when probabilistic routing isn't good enough, a hook
   *guarantees* the transition.
3. **Claude Agent SDK** — programmatic graph definition, for unattended operation and for
   making the topology testable.

The practical caution is the same 15×-token warning: fan out only where the work genuinely
separates. In this workspace the pattern already appears as `/akira` (parallel haiku
scanners), `/workflow-research fan-out` (parallel scouts), and `/workflow-review`
(multi-reporter pipeline) — each is a parallel review graph with a synthesizer node.

---

## 9. The knowledge-graph facet

Graphs appear in a second, distinct sense: **knowledge graphs as retrieval structure** rather
than as execution topology. Nodes are entities (people, places, concepts), edges are typed
relationships, and the graph encodes structured world knowledge that a RAG pipeline queries
instead of — or alongside — a vector index.

The distinction is worth keeping sharp:

| | Agent graph | Knowledge graph |
|---|---|---|
| Nodes are | Units of computation | Entities |
| Edges are | Permitted transitions | Typed relationships |
| The graph is | Execution topology | Data structure for retrieval |
| Runtime concern | Routing, state, cost | Traversal, entity resolution |

Flowtivity's rule of thumb: **"Vector search finds things that sound like your question.
Graphs find things that are connected to your answer."** On multi-hop reasoning they report
53.4% accuracy for graph retrieval vs 42.9% for vector-only — but with the crucial caveat
that at 85% per-hop accuracy, **"a 5-hop traversal is only 44% trustworthy"** without solid
entity resolution. Traversal depth compounds error; entity resolution is the load-bearing
sub-problem, not an implementation detail.

Detailed chapter notes: [`kg-and-llms-in-action/`](kg-and-llms-in-action/) — 15 chapters plus
appendices from *Knowledge Graphs and LLMs in Action* (Manning), covering ontology design,
LLM-driven KG construction, named entity disambiguation, graph feature engineering, GNNs,
KG-powered RAG, text-to-Cypher, and a LangGraph QA agent.

---

## 10. Adoption methodology

Flowtivity's five stages, which match how the other sources describe incremental adoption:

1. **AUDIT** — document current workflows and where they bottleneck.
2. **IDENTIFY** — find the steps that are genuinely independent (i.e. parallelizable).
3. **DESIGN** — sketch the topology; start at 3–5 nodes.
4. **IMPLEMENT** — build it and measure a baseline before optimizing.
5. **TYPE** — add relationship semantics to edges.

Start small. A 3–5 node graph with one honest verification step beats a twelve-node topology
whose failure modes you can't reason about.

---

## 11. Graphs vs. loops: choosing

| Situation | Use |
|---|---|
| Single agent, tool-augmented reasoning cycle | Loop engineering ([04-loop](../04-loop/README.md)) |
| Open-ended research with unknowable steps | Harness + loop, **not** a graph |
| Multiple agents with conditional handoffs | Graph engineering |
| 3+ independent verification steps | Graph (parallel review) |
| Long-running work needing fault tolerance and resume | Graph (checkpointed persistence) |
| Human approval mid-execution | Graph (interrupt/resume) |
| Parallel specialists merging results | Graph (fan-out/fan-in with reducers) |
| Simple task, low per-cycle pass rate | Loop (graph fan-out cost isn't recovered) |
| Structured world knowledge for retrieval | Knowledge graph (§9) |

---

## 12. LangGraph reference implementation

```python
from langgraph.graph import StateGraph, MessagesState, START, END

def node_a(state: MessagesState) -> MessagesState:
    # read state, do work, return updates
    return {"messages": [...]}

def router(state: MessagesState) -> str:
    # conditional logic → returns node name
    return "node_b" if condition else END

builder = StateGraph(MessagesState)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_edge(START, "node_a")
builder.add_conditional_edges("node_a", router)
graph = builder.compile()
```

The compiled graph is callable like a function; LangGraph handles state persistence,
streaming, and interrupts. Add a checkpointer at `compile(checkpointer=...)` to get durable
execution, resume, and human-in-the-loop interrupts from the same mechanism.

---

## 13. Tooling landscape (2026)

- **LangGraph** — the canonical implementation; three years of production feedback behind
  its primitives.
- **OpenClaw Code Mode** — lets the model *"write a small JavaScript or TypeScript program
  instead of choosing directly from a long list of tools,"* which makes the topology
  expressible as code rather than as tool-choice sequences.
- **OpenAI Codex "graph-max"** — sketch a workflow diagram, send it to Codex, execute as
  multi-agent code.
- **Claude Code** — subagents, hooks, and the Agent SDK (§8).
- **Google ADK** — workflow agents (sequential, parallel, loop) as composable topology
  primitives.

Community consensus flowtivity reports for the KG side, via Eugeniu Ghelbur: *"small typed
core, cheap indexing, hybrid retrieval, temporal supersession. All four of those are
implementable on markdown files you own."*

---

## Resources

- Pillar guide: [`4-agents`](../../interviewing/guides/4-agents/00-overview.md)
- Book notes: [`kg-and-llms-in-action/`](kg-and-llms-in-action/)
- Coursera code — agent graphs: [`AI-Agents-in-LangGraph-main`](../../generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main/)
- Coursera code — KG for RAG: [`Knowledge_Graphs_for_RAG-main`](Knowledge_Graphs_for_RAG-main/)
- Readings — knowledge graph papers: [`3-rag-knowledge-graphs/`](3-rag-knowledge-graphs/)
- LangGraph docs: https://docs.langchain.com/langgraph
- Loop engineering note: [`loop-engineering.md`](../04-loop/loop-engineering.md)
