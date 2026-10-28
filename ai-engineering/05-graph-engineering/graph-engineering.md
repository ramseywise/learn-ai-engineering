---
origin: synthesis
sources:
  - https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph
  - https://docs.langchain.com/langgraph
  - https://www.anthropic.com/engineering/building-effective-agents
  - https://www.anthropic.com/engineering/multi-agent-research-system
  - https://arxiv.org/abs/2404.16130
  - https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide
confidence: high
cleaned: 2026-10-28
---
# Graph Engineering

> Overview note. Topic depth lives in [notes/](notes/). The original single deep note is archived at [sources/graph-engineering-deep-note.md](sources/graph-engineering-deep-note.md).

---

## Position in the stack

Graph engineering is the **fifth layer**: prompt → context → harness → loop → **graph**. Loop engineering governs one agent's cycle. Graph engineering governs the **topology** connecting several units of work: which nodes exist, which transitions are allowed, what state they share, and where a person or a deterministic check sits in the path.

The relationship is containment, not replacement:

> **"A loop is just a directed, cyclic graph."** — LangChain

**Inherits the weaknesses of:** loop engineering. A graph that routes between unreliable loops inherits every loop failure and adds coordination failures on top.

---

## The thesis

> **Graphs make agent organisations programmable the way loops make individual agent behaviour programmable.**

The operative rule is the opposite of "build a graph": **start with a loop, and add a node only when a signal forces it** ([note 01](notes/01-graph-vs-loop.md)). The five signals are distinct specialties, parallel fan-out and join, a different model or toolset per step, control flow that must be auditable, and an overloaded verifier. Each names something a single loop structurally can't do. Anything you can't name in advance stays inside a loop with agency ([note 06](notes/06-when-not-to-build-a-graph.md)).

Production agents are **not DAGs**. They need cycles for retry and revision, conditional edges for routing, and durable state so they can pause. That is why the substrate is a cyclic state machine with a checkpointer, not a pipeline runner.

---

## Two things called "graph"

| | Agent graph (Track A) | Knowledge graph (Track B) |
|---|---|---|
| Nodes are | Units of computation | Entities |
| Edges are | Permitted transitions | Typed relationships |
| The graph is | Execution topology | Data structure for retrieval |
| Runtime concern | Routing, state, cost | Traversal, entity resolution |

They meet in [note 12](notes/12-kg-as-shared-agent-memory.md): in a multi-agent system, a shared knowledge graph is often the memory the execution graph coordinates through.

---

## Topic notes

**Track A: agent graphs**

1. [Graph vs. loop](notes/01-graph-vs-loop.md): containment, production agents aren't DAGs, the five signals, the decision tree.
2. [Graph primitives](notes/02-graph-primitives.md): node kinds, spending agency per node, edges, the minimal program.
3. [State and reducers](notes/03-state-and-reducers.md): typed state, reducers as the concurrency primitive, `Send` fan-out, the true-dependency test.
4. [Durable execution and interrupts](notes/04-durable-execution-and-interrupts.md): checkpointers, threads, `interrupt()`, time travel, where gates go.
5. [Topology patterns](notes/05-topology-patterns.md): generate-then-verify, supervisor, fan-out, subgraphs, handoff; the Claude Code mapping.
6. [When not to build a graph](notes/06-when-not-to-build-a-graph.md): unnameable work, fan-out cost, premature graphs, incremental adoption.
7. [Failure modes at scale](notes/07-failure-modes-at-scale.md): mechanical and control failures, correlated errors, verifier isolation, anchors.
8. [Governance and production](notes/08-governance-and-production.md): IDs and tracing, budgets, approvals, the n8n case study.

**Track B: knowledge graphs**

9. [KG fundamentals and Cypher](notes/09-kg-fundamentals-and-cypher.md): what a KG is and why it pairs with LLMs, LPG vs. RDF, typed edges, Cypher.
10. [Building KGs with LLMs](notes/10-building-kgs-with-llms.md): per-hop compounding, the extraction pipeline, ER and NED, extraction evals.
11. [KG-RAG and text-to-Cypher](notes/11-kg-rag-and-text-to-cypher.md): vector RAG limits, GraphRAG evidence, retrieval modes, schema-first text-to-Cypher.
12. [KG as shared agent memory](notes/12-kg-as-shared-agent-memory.md): state vs. memory, loop → swarm → graph, `GraphUpdate`, the five planes.
13. [Learning on graphs](notes/13-graph-ml-and-gnns.md): why nodes aren't i.i.d., features vs. embeddings, DWPC, message passing, GNN + LLM patterns, predictions as claims.

---

## Rules of thumb

| Rule | Note |
|---|---|
| Generate-then-verify is the highest-yield first graph | [02](notes/02-graph-primitives.md), [05](notes/05-topology-patterns.md) |
| Spend agency per node: code where you can, one LLM call where you must, an agent only where the path is unknown | [02](notes/02-graph-primitives.md) |
| Every shared key has one writer or a reducer | [03](notes/03-state-and-reducers.md) |
| Does the next step read the previous step's output? If not, fan out | [03](notes/03-state-and-reducers.md) |
| Gate the edges where consequences concentrate, not every node | [04](notes/04-durable-execution-and-interrupts.md) |
| "We need a graph" is often an overloaded verifier: strengthen it and ship the loop | [06](notes/06-when-not-to-build-a-graph.md) |
| Fan-out is expensive (Anthropic's multi-agent research system: ~15× a chat turn's tokens), so measure break-even | [06](notes/06-when-not-to-build-a-graph.md) |
| Verifiers see the task and the output, never the generator's reasoning | [07](notes/07-failure-modes-at-scale.md) |
| Keep at least one anchor the graph can't edit | [07](notes/07-failure-modes-at-scale.md) |
| Errors compound per hop: at 85% per hop, a 5-hop answer is ~44% right | [10](notes/10-building-kgs-with-llms.md) |
| Never merge entities destructively; keep provenance on every edge | [10](notes/10-building-kgs-with-llms.md), [12](notes/12-kg-as-shared-agent-memory.md) |
| Vector search first, canned traversals for named question shapes, text-to-Cypher only with a validator | [11](notes/11-kg-rag-and-text-to-cypher.md) |
| If a run's only durable record is its chat transcript, you have no graph | [12](notes/12-kg-as-shared-agent-memory.md) |
| Beat a domain-informed feature baseline before trusting a learned embedding | [13](notes/13-graph-ml-and-gnns.md) |
| A predicted edge is a claim: flag it, score it, keep it out of default traversals | [13](notes/13-graph-ml-and-gnns.md) |

---

## Practice

- [P1: agent graph labs](practice/01-agent-graph-labs.md) grow one generate-then-verify graph through notes 01–08.
- [P2: knowledge graph labs](practice/02-knowledge-graph-labs.md) run the Neo4j course, then measured extraction, text-to-Cypher, a shared-memory swarm and link prediction.
- [templates/](templates/): `generate-then-verify.py`, `fan-out-merge.py`, `graph-update.schema.json`.

---

## Resources

- Pillar guide: [4-agents](../../interviewing/guides/4-agents/00-overview.md)
- LangChain, 3 years of graph engineering with LangGraph: https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph
- LangGraph docs: https://docs.langchain.com/langgraph
- Anthropic, Building effective agents: https://www.anthropic.com/engineering/building-effective-agents
- Anthropic, multi-agent research system: https://www.anthropic.com/engineering/multi-agent-research-system
- Edge et al., GraphRAG: https://arxiv.org/abs/2404.16130
- Anthropic KG construction cookbook: https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide
- Book notes: [sources/kg-and-llms-in-action/](sources/kg-and-llms-in-action/), *Knowledge Graphs and LLMs in Action* (Manning)
- Neo4j course: [notebooks/knowledge-graphs-for-rag/](notebooks/knowledge-graphs-for-rag/)
- Secondary sources (vendor and aggregator posts) are listed with a quality assessment in [OUTLINE.md](OUTLINE.md#source-quality-replace-before-splitting).
