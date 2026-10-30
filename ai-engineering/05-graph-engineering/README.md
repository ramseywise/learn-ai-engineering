# 05 — Graph Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md)
> Position in the stack: fifth foundation — builds on [04-loop](../04-loop-engineering/README.md); *graphs make agent organizations programmable*.
> Overview: [graph-engineering.md](graph-engineering.md)

---

## What it is

Graph engineering is the discipline of designing the **topology** of a multi-agent system: which nodes exist (agents, deterministic functions, routers, human checkpoints), which transitions between them are permitted, and how the runtime work graph forms and mutates. Where loop engineering governs individual agent behavior (one agent, one cycle), graph engineering governs the structure connecting multiple agents — conditional routing, shared state, parallel fan-out and merge, and hierarchical composition of subgraphs.

*"Graphs make agent organizations programmable the way loops make individual agent behavior programmable."*

Graph is a **peer fifth foundation**, ordered after loop because it presumes loop mastery — but it is a first-class discipline, not an advanced optional tier. The relationship is containment, not replacement: per LangChain, *"a loop is just a directed, cyclic graph."*

**Two things called "graph engineering."** Agent graphs are *execution topology* (nodes = computation, edges = permitted transitions). Knowledge graphs are *retrieval structure* (nodes = entities, edges = typed relationships). Both live in this pillar; keep the distinction sharp.

**Not everything should be a graph.** Work whose steps can't be named ahead of time — generic deep research is the canonical case — belongs in a harness with a good loop. Forcing it into deterministic paths is the wrong move, and graph fan-out runs ~3× the tokens per cycle (Anthropic's multi-agent research system: ~15× a chat turn).

**Inherits the weaknesses of:** loop engineering — a graph routing between unreliable loops inherits all loop failures at the organizational scale, and adds coordination failures on top.

---

## Syllabus

Read the notes in order; each one is earned by the one before. Notes 01–08 are Track A (agent graphs). Notes 09–13 are Track B (knowledge graphs); note 12 joins the two tracks, and note 13 adds learning on graphs.

| # | Note | Covers | Lab |
|---|---|---|---|
| 1 | [Graph vs. loop](notes/01-graph-vs-loop.md) | Definition, containment, production agents aren't DAGs, the five signals, the decision tree, two senses of "graph", the map | [Lab 1](practice/01-agent-graph-labs.md#lab-1--generate-then-verify) |
| 2 | [Graph primitives](notes/02-graph-primitives.md) | Node kinds, spending agency per node, edges, the minimal program, generate-then-verify | [Lab 1](practice/01-agent-graph-labs.md#lab-1--generate-then-verify) |
| 3 | [State and reducers](notes/03-state-and-reducers.md) | Typed state, reducers, parallel-write races, Send fan-out, handoffs, the true-dependency test | [Lab 2](practice/01-agent-graph-labs.md#lab-2--fan-out-and-merge) |
| 4 | [Durable execution and interrupts](notes/04-durable-execution-and-interrupts.md) | Checkpointers, threads, `interrupt()`, editing state, time travel, where gates go | [Lab 3](practice/01-agent-graph-labs.md#lab-3--checkpoint-and-interrupt) |
| 5 | [Topology patterns](notes/05-topology-patterns.md) | Generate-then-verify, supervisor, fan-out, subgraphs, handoff; the Claude Code mapping | [Lab 4](practice/01-agent-graph-labs.md#lab-4--subgraphs-and-the-parallel-review-graph) |
| 6 | [When not to build a graph](notes/06-when-not-to-build-a-graph.md) | Unnameable work, fan-out cost, premature graphs, split the verifier, incremental adoption | [Lab 5](practice/01-agent-graph-labs.md#lab-5--break-even-measurement) |
| 7 | [Failure modes at scale](notes/07-failure-modes-at-scale.md) | Mechanical and control failures, correlated errors, verifier isolation, anchors, pre-flight check | [Lab 6](practice/01-agent-graph-labs.md#lab-6--fault-injection) |
| 8 | [Governance and production](notes/08-governance-and-production.md) | IDs and tracing, budgets, approvals, the checklist, n8n case study | [Lab 7](practice/01-agent-graph-labs.md#lab-7--trace-and-attribute) |
| 9 | [KG fundamentals and Cypher](notes/09-kg-fundamentals-and-cypher.md) | What a KG is, why it pairs with LLMs, LPG vs. RDF, typed edges, Cypher cheat sheet | [KG Labs 1–2](practice/02-knowledge-graph-labs.md#lab-1--cypher-on-the-movies-graph) |
| 10 | [Building KGs with LLMs](notes/10-building-kgs-with-llms.md) | Per-hop compounding, the extraction pipeline, model tiers, metagraph, ER and NED, extraction evals | [KG Labs 3–4](practice/02-knowledge-graph-labs.md#lab-3--build-the-10-k-graph) |
| 11 | [KG-RAG and text-to-Cypher](notes/11-kg-rag-and-text-to-cypher.md) | Vector RAG limits, GraphRAG evidence, retrieval modes, schema-first text-to-Cypher, the LangGraph QA agent | [KG Labs 5–6](practice/02-knowledge-graph-labs.md#lab-5--chat-with-the-10-k-graph) |
| 12 | [KG as shared agent memory](notes/12-kg-as-shared-agent-memory.md) | State vs. memory, loop → swarm → graph, `GraphUpdate`, reversible ER and provenance, five planes, swarm cost | [KG Labs 7–8](practice/02-knowledge-graph-labs.md#lab-7--swarm-with-and-without-shared-memory) |
| 13 | [Learning on graphs](notes/13-graph-ml-and-gnns.md) | Why nodes aren't i.i.d., the task map, manual vs. learned features, DWPC, embeddings and message passing, GNN + LLM patterns, predictions as claims | [KG Lab 9](practice/02-knowledge-graph-labs.md#lab-9--predict-missing-links) |

### Practice and templates

- [P1 — Agent graph labs](practice/01-agent-graph-labs.md): seven labs that grow one graph through notes 01–08.
- [P2 — Knowledge graph labs](practice/02-knowledge-graph-labs.md): nine labs: the Neo4j course, your own domain, measured extraction, text-to-Cypher, a shared-memory swarm, and link prediction.
- [templates/generate-then-verify.py](templates/generate-then-verify.py) and [templates/fan-out-merge.py](templates/fan-out-merge.py): runnable LangGraph skeletons. [templates/graph-update.schema.json](templates/graph-update.schema.json): the `GraphUpdate` write contract from note 12.

---

## Resource map

### Deep notes
- [graph-engineering.md](graph-engineering.md): pillar overview with the thesis, the two senses of "graph", the topic notes and rules of thumb.
- [sources/graph-engineering-deep-note.md](sources/graph-engineering-deep-note.md): the original single deep note, archived. The `§N` references in OUTLINE.md point here.
- Memory-augmented RAG notes moved to [02-context-engineering/sources/memory-augmented-rag-notion-export.md](../02-context-engineering/sources/memory-augmented-rag-notion-export.md); what was new is merged into 02-context [notes/06-memory.md](../02-context-engineering/notes/06-memory.md).

### Book notes — *Knowledge Graphs and LLMs in Action* (Manning)
- [sources/kg-and-llms-in-action/](sources/kg-and-llms-in-action/) — the depth layer under notes 09–13 (ch1–3 → 09, ch4–8 → 10, ch13–15 → 11, ch9–12 → 13; chapter PDFs in `pdf/`). Chapter-by-chapter notes: KG+LLM hybrid systems, ontology-driven construction, multisource integration, LLM-driven extraction, named entity disambiguation, graph feature engineering, GNNs (representation learning, node classification, link prediction), KG-powered RAG, text-to-Cypher, and a LangGraph QA agent — plus graph-theory and Neo4j/Cypher appendices.

### Interviewing guide
- [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Notebooks and course code
- [notebooks/knowledge-graphs-for-rag/](notebooks/knowledge-graphs-for-rag/) — DeepLearning.AI *Knowledge Graphs for RAG* (Neo4j): notebooks L2–L7, data dumps and lesson notes. Run as KG Labs 1, 3 and 5; L0–L2 feed note 09, L3–L6 note 10, L7 note 11.
- [AI-Agents-in-LangGraph-main](../../generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main/) — LangGraph agent graphs (nodes, edges, state, conditional routing); used in the Track A labs.
- [sources/langgraph_extended.pptx](sources/langgraph_extended.pptx) — *LangGraph: A Visual Guide* (26 slides): nodes, edges, state and reducers, memory, checkpointers and durable execution, interrupts and time travel, streaming, subgraphs, observability, and LangGraph vs Google ADK. Also the style reference for the course's `make slides` decks.

### Readings
- [sources/](sources/) — the book (notes and PDFs, above), the archived deep note, and the community-compiled *Graph Engineering: The Karpathy Loop, Improved 1000x by Itself* (2026) PDF.
- Li, *AI Agents in Depth*, [ch. 10 Multi-Agent Collaboration](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter10.md): when multi-agent actually beats single-agent, shared vs isolated context, failure modes. Synthesised into [05](notes/05-topology-patterns.md) (two design dimensions, the new-information test, the runtime as an OS, handoff packages, A2A; [labs table](notes/05-topology-patterns.md#labs)) and [07](notes/07-failure-modes-at-scale.md) (Byzantine faults, semantic conflicts, cascading amplification, MAST). Ch. 3's RAPTOR vs GraphRAG comparison is in [11](notes/11-kg-rag-and-text-to-cypher.md).

### External references
- LangGraph docs: https://docs.langchain.com/langgraph
- LangGraph GitHub: https://github.com/langchain-ai/langgraph
- [3 years of graph engineering with LangGraph](https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph) — production agents need cycles; loops are simplified graphs.
- [Graph engineering: enterprise guide](https://www.truefoundry.com/blog/graph-engineering-enterprise-guide) — identity, cost attribution, approval checkpoints, 7-question production checklist.
- [Graph engineering for AI agents](https://www.eigent.ai/blog/graph-engineering-ai-agents) — control-theory framing: loop failure modes at scale, paired metrics, anchors.
- [Graph engineering 2026 guide](https://flowtivity.ai/blog/graph-engineering-2026-guide-openclaw-codex/) — parallel review graph, typed edges, loop-vs-graph cost tradeoffs, 5-stage adoption.
- [Graph engineering with Claude Code](https://www.aibuilderclub.com/blog/graph-engineering-with-claude-code) — subagents as nodes, hooks as deterministic edges, Agent SDK.
- [Forget loop engineering](https://medium.com/@GaoDalie_AI/forget-loop-engineering-graph-engineering-is-about-this-713a9cf2e985) — the organizational-structure argument.
- [From Karpathy's loops to shared knowledge graphs](https://pkhamdee.blog/2026/07/21/graph-engineering-from-karpathys-loops-to-shared-knowledge-graphs/) — loop → swarm → graph as capacity unlocks; the KG as shared memory ("the agent forgets, the graph does not"); tiered extraction pipeline; five-plane architecture.
- [Graph engineering vs agent loops](https://youmind.com/landing/x-viral-articles/graph-engineering-ai-agent-loops) — the true-dependency test for what parallelizes; verifier context isolation; swarm cost anchors.
- [Inside n8n's AI Workflow Builder](https://medium.com/@rajveer.rathod1301/inside-n8ns-ai-workflow-builder-a-complete-architecture-deep-dive-f2eeb2d57ec8) — production supervisor-pattern LangGraph case study: six agents, per-node iteration bounds, optimistic locking, published context budgets.
- [Hosting n8n](https://docs.n8n.io/deploy/host-n8n) — deployment surface for a self-hosted graph runtime.

### Previous and next layer
← Builds on [04-loop-engineering/](../04-loop-engineering/README.md)
→ [06-eval/](../06-eval/README.md) — eval measures graph correctness and multi-agent coordination quality.

---

## Working References

Claude Code convention references that map to this pillar. These files live at `~/.claude/refs/` and can be consulted in any Claude Code session.

### `agent-architecture.md`
Conventions for multi-agent orchestration — the architecture decisions that determine graph topology.

Key topics for this pillar:
- Multi-agent orchestration: when to use a subagent (different tool set, context isolation, parallelizable, independently retryable)
- Orchestrator responsibilities: maintain plan and state, dispatch subtasks with scoped context, handle subagent failure, assemble and validate outputs
- Trust boundaries: cross-trust-boundary calls require sanitization; distinguish orchestrator from A2A caller
- Dynamic fan-out: frontier pattern — do not default to it; orchestrator-holds-plan + isolated-window subagents is the settled baseline

### `agent-memory.md`
Conventions for the shared state that a graph must coordinate across nodes and agents.

Key topics for this pillar:
- Memory taxonomy: episodic (events/turns/decisions), semantic (facts/entities/preferences), procedural (skills/instructions) — three tiers, settled vocabulary
- State persistence by lifetime: in-turn (context window), session (in-memory), cross-session (persistent store), cross-agent (shared persistent store)
- Checkpointing: checkpoint after each plan step; checkpoint must include plan state, completed steps, intermediate outputs, run metadata
- Single-writer rule: for each memory tier, designate one writer; multi-writer state without locking produces corruption
- Memory vs. context: memory is the store; context is the current window loaded from it — never conflate the two
