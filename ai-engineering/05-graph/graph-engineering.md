---
origin: web-authored
sources:
  - https://langchain-ai.github.io/langgraph/
  - https://docs.langchain.com/langgraph
  - https://www.explainx.ai/post/graph-engineering
confidence: high
cleaned: 2026-07-21
---
# Graph Engineering

## Position in the stack

Graph engineering is the **fifth foundation**, building on loops: *graphs make agent organizations programmable the way loops make individual agent behavior programmable*. The nesting rule: harness implements loops → graphs organize loops into coordinated multi-agent topologies. Where loop engineering ends and graph engineering begins: once you need **more than one agent collaborating with conditional handoffs and shared state across that collaboration**, you're in graph territory. A single agent with a tool loop is loop engineering. Multiple agents with routing logic between them is graph engineering.

---

## What graphs are in agent systems

A graph is a **directed structure of nodes and edges** representing an agent workflow:

- **Node** — a discrete processing unit (typically a function or agent step) that reads state, performs work, and writes state.
- **Edge** — a directed connection defining which node executes next.
- **State** — a shared data structure (e.g., `MessagesState`) that persists across all node executions within a graph run. Nodes transform state; edges route based on it.

The key insight: **graphs contain loops.** A loop is a single-agent cycle (perceive → decide → act → repeat). A graph can contain multiple loops running as coordinated agents, with conditional routing between them. The graph is the topology; loops are its building blocks.

---

## Core concepts

### State management

LangGraph (the canonical graph-engineering framework) maintains application state throughout execution:
- **Short-term**: working memory for ongoing reasoning within a graph run.
- **Long-term**: persistence across sessions — graph runs can resume after interruptions or failures.
- **Reducers**: control how state is updated when multiple branches write to the same key.

State is the shared substrate that replaces the message-passing overhead in naive multi-agent designs.

### Conditional routing

Graphs support conditional edges — routing decisions that determine which node executes next based on the current state. This enables:

- **Adaptive branching**: route to a specialized agent based on intent classification.
- **Error handling paths**: route to a retry node on tool failure.
- **Approval gates**: route to a human-in-the-loop node before committing irreversible actions.
- **Early exit**: route directly to END when a stopping condition is met.

In LangGraph: `add_conditional_edges(source_node, routing_function, {result_value: target_node})`.

### Multi-agent organizations

Graphs compose individual agent loops into organizations:

- **Supervisor pattern**: a coordinator node routes tasks to specialized worker agents based on task type, aggregates results.
- **Parallel fan-out**: multiple agents execute simultaneously (graph branches), results merged into shared state.
- **Hierarchical graphs**: a subgraph is itself a node in a parent graph — enables nested orchestration (team-of-teams).
- **Handoff protocol**: an agent signals completion by updating state with a designated key; the conditional edge reads that key to decide the next agent.

### Human-in-the-loop

A first-class graph primitive: the graph pauses at designated nodes for human inspection and state modification before continuing. This requires stateful persistence across the pause — a capability loops alone cannot provide.

---

## Knowledge-graph facet (KG for RAG)

Graphs appear in a second context: **knowledge graphs as retrieval structure** rather than as agent topology. Here, nodes are entities (people, places, concepts) and edges are typed relationships — the graph encodes structured world knowledge that a RAG pipeline queries instead of (or alongside) a vector index.

Key distinction: KG-for-RAG is about *data structure for retrieval*; agent graph engineering is about *execution topology for orchestration*. Both are "graph engineering" but at different layers. Course reference: [`Knowledge_Graphs_for_RAG-main`](Knowledge_Graphs_for_RAG-main/).

---

## Graphs vs. loops: when to choose

| Situation | Use |
|---|---|
| Single agent, tool-augmented reasoning cycle | Loop engineering (04-loop) |
| Multiple agents with conditional handoffs | Graph engineering |
| Long-running tasks requiring fault tolerance and resume | Graph (LangGraph persistence) |
| Human approval checkpoints mid-execution | Graph (interrupt/resume) |
| Parallel specialist agents merging results | Graph (fan-out/fan-in) |
| Structured world knowledge for retrieval | Knowledge graph (KG-for-RAG facet) |

---

## LangGraph architecture (canonical implementation)

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

The compiled graph is callable like a function; LangGraph handles state persistence, streaming, and interrupts.

---

## Why "graphs make agent organizations programmable"

The progression (from the loop-engineering and harness literature):
- **Harnesses** make agent capabilities deployable — tools, memory, guardrails.
- **Loops** make individual agent behavior programmable — the perceive-decide-act cycle.
- **Graphs** make multi-agent *organizations* programmable — topology, routing, coordination.

Each layer presumes the one below. You cannot graph-engineer effectively without loop engineering fluency.

---

## Resources

- Pillar guide: [`4-agents`](../../interviewing/guides/4-agents/00-overview.md)
- Coursera code — agent graphs: [`AI-Agents-in-LangGraph-main`](../../generative-ai/03-agentic-foundations/AI-Agents-in-LangGraph-main/)
- Coursera code — KG for RAG: [`Knowledge_Graphs_for_RAG-main`](Knowledge_Graphs_for_RAG-main/)
- Readings — knowledge graphs: [`3-rag-knowledge-graphs/`](3-rag-knowledge-graphs/)
- LangGraph docs: https://docs.langchain.com/langgraph
- Loop engineering note: [`loop-engineering.md`](loop-engineering.md)
