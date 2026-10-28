---
origin: web-authored
sources:
  - https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph
  - https://www.anthropic.com/engineering/building-effective-agents
  - https://www.truefoundry.com/blog/graph-engineering-enterprise-guide
  - https://www.eigent.ai/blog/graph-engineering-ai-agents
  - https://www.aibuilderclub.com/blog/agent-graph-vs-loop-when-to-use
  - https://medium.com/@GaoDalie_AI/forget-loop-engineering-graph-engineering-is-about-this-713a9cf2e985
confidence: high
cleaned: 2026-10-28
---
# 1 — Graph vs. Loop

> What graph engineering is, how it contains loop engineering rather than replacing it, the rule for when to add a node, and the map of this pillar.

---

## The definition

> **Graph engineering is designing the topology of a multi-agent system: which nodes exist, which transitions between them are permitted, and what state they carry across those transitions.**

Loop engineering asks *"what cycle re-prompts this agent and decides when it quits?"* Graph engineering asks *"who is allowed to hand work to whom, under what condition, carrying what state?"*

Three framings worth holding together:

- **LangChain (control):** graphs let you *"impose your preconceptions of how the system should work into more constrained paths, not relying solely on the judgement of the LLM."* You *"more tightly control behavior when you want the agent to follow specific paths."*
- **TrueFoundry (structure):** the topology is *"which nodes exist (agents, deterministic functions, routers, human checkpoints), which transitions are permitted, and how runtime work graphs form and mutate."*
- **Eigent (control theory):** *"the craft of wiring many feedback loops (metrics, evals, audits, policies, and workflows) into a network where they watch, constrain, and correct one another."*

The first is the one to build on. TrueFoundry and Eigent are vendor blogs; their framings are useful, but LangChain's comes from three years of running LangGraph in production.

Anthropic's *Building Effective Agents* draws the same line from the other side. **Workflows** are systems where models and tools are orchestrated through predefined code paths; **agents** are systems where the model directs its own process. A graph is how you write a workflow down, and it is also how you mix the two: fixed paths where you know the route, an agent node where you don't.

---

## Containment, not replacement

LangChain's sharpest line from three years of LangGraph:

> **"A loop is just a directed, cyclic graph."**

So a loop is a graph with **one node and an edge back to itself**. Graph engineering is not a rival to loop engineering; it is the same system with more nodes. The Medium framing ("forget loop engineering") overstates the break. TrueFoundry's is closer: loop and graph engineering are *"complementary layers, not substitutes."*

What changes at the boundary is the **failure mode** you engineer against:

| Layer | Fails by |
|---|---|
| Loop | Not converging: spinning, quitting early, gaming the scorekeeper |
| Graph | Mis-routing, deadlocking, double-writing shared state, losing accountability for a decision |

> **Inherits the weaknesses of loop engineering.** A graph routing between unreliable loops inherits every loop failure at organisational scale, and adds coordination failures on top. Fix the loop first.

Gao Dalie's diagnosis of why teams hit the wall: *"It's not that the agents aren't smart enough, but rather that the organizational structure isn't clear enough."*

---

## Production agents are not DAGs

The most load-bearing lesson from LangChain:

> **"Production agents need cycles: retrying failed tool calls, asking users for missing information, revising answers after validation, calling tools repeatedly until they have enough context."**

This is why the Airflow-style DAG model imported from data engineering breaks on agents. A DAG is acyclic by definition. A production agent must be able to go A → B, discover B failed, return to A, and only then reach C. **Graph engineering for agents is cyclic-graph engineering.** Anything that forbids cycles is a workflow engine, not an agent framework.

The second lesson: **static edges are not enough.** Real systems mix *"known structure with runtime variability"*. The set of nodes to run is often unknown until runtime: one reviewer per changed file, one worker per retrieved document. That is what LangGraph's Send API is for ([03](03-state-and-reducers.md#dynamic-fan-out-the-send-api)).

---

## Where loop ends and graph begins

You are in graph territory once you need **more than one agent collaborating, with conditional handoffs and shared state across that collaboration.** One agent with a tool loop is loop engineering. Several agents with routing logic between them is graph engineering.

### The default plus an escalation rule

> **Start with a loop. Add a node only when a specific signal forces it.**

Escalation is a cost you justify, not a maturity level you graduate to. Five signals justify a node, and each names something a single loop structurally cannot do:

| Signal | Why the loop fails |
|---|---|
| **Distinct specialties**: roles needing different instructions, context, tools | One agent context-switches between jobs, carrying each role's baggage into the next |
| **Parallel fan-out + join**: process many items, then merge | A loop is sequential; the wall-clock cost is unnecessary |
| **Per-step model or tool variation**: a different model or a restricted toolset per stage | One agent enforces one model and one tool policy |
| **Auditable control flow**: regulated work needing explicit path tracing | Emergent loop paths are hard to reconstruct afterwards |
| **Overloaded verifier**: one check judging several criteria | A dedicated reviewer node removes the criteria confusion |

### The 30-second decision tree

Start with a loop, then ask in order:

1. Does the work split into **distinct specialties** with different needs?
2. Do you need **true parallelism** (fan-out, then join)?
3. Do different steps need **different models or tools**, or **auditable** branching?
4. Is **one verifier failing** because it judges too many criteria at once?

Yes to any → add a node. No to all → **strengthen the verifier and ship the loop.**

That last clause is the one people skip. The most common "we need a graph" is really an overloaded verifier ([04-loop note 03](../../04-loop-engineering/notes/03-the-scorekeeper.md)), and splitting the verifier is far cheaper than splitting the system. [06](06-when-not-to-build-a-graph.md) develops the negative case.

---

## Two things called "graph"

This pillar uses the word in two senses. Keep them apart:

| | Agent graph (Track A) | Knowledge graph (Track B) |
|---|---|---|
| Nodes are | Units of computation | Entities |
| Edges are | Permitted transitions | Typed relationships |
| The graph is | Execution topology | Data structure for retrieval |
| Runtime concern | Routing, state, cost | Traversal, entity resolution |

They meet in [note 12](12-kg-as-shared-agent-memory.md): in a multi-agent system the knowledge graph is often the shared state layer the execution graph coordinates through.

---

## The map of this pillar

| # | Note | Track | Question it answers |
|---|---|---|---|
| 01 | Graph vs. loop (this note) | A | When does a loop become a graph? |
| 02 | [Graph primitives](02-graph-primitives.md) | A | What are nodes and edges, and how much agency goes in each node? |
| 03 | [State and reducers](03-state-and-reducers.md) | A | What do nodes share, and what happens when two write at once? |
| 04 | [Durable execution and interrupts](04-durable-execution-and-interrupts.md) | A | How does a graph pause, resume, and survive a crash? |
| 05 | [Topology patterns](05-topology-patterns.md) | A | Which shapes recur, and how do they map onto Claude Code? |
| 06 | [When not to build a graph](06-when-not-to-build-a-graph.md) | A | When is the graph overhead not worth it? |
| 07 | [Failure modes at scale](07-failure-modes-at-scale.md) | A | How do graphs fail where single loops don't? |
| 08 | [Governance and production](08-governance-and-production.md) | A | How do you operate a graph, not just demo one? |
| 09 | [KG fundamentals and Cypher](09-kg-fundamentals-and-cypher.md) | B | What is a knowledge graph and how do you query it? |
| 10 | [Building KGs with LLMs](10-building-kgs-with-llms.md) | B | How do you turn text into a graph you can trust? |
| 11 | [KG-RAG and text-to-Cypher](11-kg-rag-and-text-to-cypher.md) | B | How do you retrieve from a graph in natural language? |
| 12 | [KG as shared agent memory](12-kg-as-shared-agent-memory.md) | A + B | How does a KG become a swarm's memory? |

Labs: [P1 agent graph labs](../practice/01-agent-graph-labs.md) (Track A), [P2 knowledge graph labs](../practice/02-knowledge-graph-labs.md) (Track B).

---

## Where it sits

prompt → context → harness → loop → **graph**. The harness ([03-harness](../../03-harness-engineering/README.md)) supplies tools, state and guardrails. The loop ([04-loop](../../04-loop-engineering/README.md)) decides how many times to use them and when to stop. The graph decides *which loop runs next and who is accountable for it*. Each layer presumes the one below: you cannot graph-engineer well without loop-engineering fluency. [06-eval](../../06-eval/README.md) measures whether the whole thing is correct.

---

## Working reference

`~/.claude/refs/agent-architecture.md` — when to use a subagent, orchestrator responsibilities, dynamic fan-out.

---

→ Next: [02-graph-primitives.md](02-graph-primitives.md) — nodes, edges, and how much agency to spend per node.
