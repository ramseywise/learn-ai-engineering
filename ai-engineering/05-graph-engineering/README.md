# 05 — Graph Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md)
> Position in the stack: fifth foundation, prompt → context → harness → loop → **graph**. Builds on [04-loop](../04-loop-engineering/README.md).

---

## What it is

Graph engineering is the discipline of designing the **topology** of a multi-agent system: which nodes exist (agents, deterministic functions, routers, human checkpoints), which transitions between them are permitted, and how the runtime work graph forms and mutates. Where loop engineering governs individual agent behavior (one agent, one cycle), graph engineering governs the structure connecting multiple agents — conditional routing, shared state, parallel fan-out and merge, and hierarchical composition of subgraphs.

> **Graphs make agent organisations programmable the way loops make individual agent behaviour programmable.**

Graph is a **peer fifth foundation**, ordered after loop because it presumes loop mastery — but it is a first-class discipline, not an advanced optional tier. The relationship is containment, not replacement: per LangChain, *"a loop is just a directed, cyclic graph."*

The operative rule is the opposite of "build a graph": **start with a loop, and add a node only when a signal forces it** ([note 01](notes/01-graph-vs-loop.md)). The five signals are distinct specialties, parallel fan-out and join, a different model or toolset per step, control flow that must be auditable, and an overloaded verifier. Each names something a single loop structurally can't do.

Production agents are **not DAGs**. They need cycles for retry and revision, conditional edges for routing, and durable state so they can pause. That is why the substrate is a cyclic state machine with a checkpointer, not a pipeline runner.

**Two things called "graph engineering."** Keep the distinction sharp:

| | Agent graph (Track A, notes 01–08) | Knowledge graph (Track B, notes 09–13) |
|---|---|---|
| Nodes are | Units of computation | Entities |
| Edges are | Permitted transitions | Typed relationships |
| The graph is | Execution topology | Data structure for retrieval |
| Runtime concern | Routing, state, cost | Traversal, entity resolution |

They meet in [note 12](notes/12-kg-as-shared-agent-memory.md): in a multi-agent system, a shared knowledge graph is often the memory the execution graph coordinates through.

**Not everything should be a graph.** Work whose steps can't be named ahead of time — generic deep research is the canonical case — belongs in a harness with a good loop ([note 06](notes/06-when-not-to-build-a-graph.md)). Forcing it into deterministic paths is the wrong move, and graph fan-out runs ~3× the tokens per cycle (Anthropic's multi-agent research system: ~15× a chat turn).

**Inherits the weaknesses of:** loop engineering — a graph routing between unreliable loops inherits all loop failures at the organizational scale, and adds coordination failures on top.

---

## Start here

1. Read the notes in order (table below). They are the course: every slide's claim, table, code and figure is in the note it comes from.
2. Use the deck for review or teaching: [slides/graph-engineering.pptx](slides/graph-engineering.pptx), a 5-part talk built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=05-graph-engineering`.
3. Keep the [rules of thumb](#rules-of-thumb) as the one-page summary.

## Lab

A LangGraph support graph: routing, a fan-out with a reducer, a retry cycle, an approval interrupt and a checkpoint. TypeScript uses LangGraph.js. It comes in both languages, side by side, on the same inputs. Both run offline with a stub by default, and each README says how to swap in a real model.

| Language | Folder | Run |
|---|---|---|
| TypeScript | [practice/langgraph-graph-ts/](practice/langgraph-graph-ts/README.md) | `cd practice/langgraph-graph-ts && npm install && npx tsx run.ts` |
| Python | [practice/langgraph-graph/](practice/langgraph-graph/README.md) | `cd practice/langgraph-graph && uv run run.py` |

## Layout

```
README.md      this file: overview, start here, rules of thumb, resource map
references.md  every source the notes cite, mapped to notes
notes/         01–13, the course; figures and code inline
slides/        deck.yaml + graph-engineering.pptx
practice/      the lab, in TypeScript and Python
sources/       book chapter PDFs, paper PDFs, the LangGraph style deck
  images/      every figure the notes and deck use (<author>-<slug>-fig<N>)
  images/unreferenced/   course images not used anywhere yet, kept for review
```

---

## Syllabus

Read the notes in order; each one is earned by the one before. Notes 01–08 are Track A (agent graphs). Notes 09–13 are Track B (knowledge graphs); note 12 joins the two tracks, and note 13 adds learning on graphs.

| # | Note | Covers |
|---|---|---|
| 1 | [Graph vs. loop](notes/01-graph-vs-loop.md) | Definition, containment, production agents aren't DAGs, the five signals, the decision tree, two senses of "graph", the map |
| 2 | [Graph primitives](notes/02-graph-primitives.md) | Node kinds, spending agency per node, edges, the minimal program, generate-then-verify |
| 3 | [State and reducers](notes/03-state-and-reducers.md) | Typed state, input and output schemas, reducers, parallel-write races, Send fan-out, handoffs, the true-dependency test |
| 4 | [Durable execution and interrupts](notes/04-durable-execution-and-interrupts.md) | Checkpointers, threads, `interrupt()`, editing state, time travel, where gates go |
| 5 | [Topology patterns](notes/05-topology-patterns.md) | Generate-then-verify, supervisor, fan-out, subgraphs, handoff; the Claude Code mapping |
| 6 | [When not to build a graph](notes/06-when-not-to-build-a-graph.md) | Unnameable work, fan-out cost, premature graphs, split the verifier, incremental adoption |
| 7 | [Failure modes at scale](notes/07-failure-modes-at-scale.md) | Mechanical and control failures, correlated errors, verifier isolation, anchors, pre-flight check |
| 8 | [Governance and production](notes/08-governance-and-production.md) | IDs and tracing, budgets, approvals, the checklist, n8n case study |
| 9 | [KG fundamentals and Cypher](notes/09-kg-fundamentals-and-cypher.md) | What a KG is, why it pairs with LLMs, LPG vs. RDF, typed edges, Cypher cheat sheet |
| 10 | [Building KGs with LLMs](notes/10-building-kgs-with-llms.md) | Per-hop compounding, the extraction pipeline, model tiers, metagraph, ER and NED, extraction evals, the lifecycle after the load |
| 11 | [KG-RAG and text-to-Cypher](notes/11-kg-rag-and-text-to-cypher.md) | Vector RAG limits, GraphRAG evidence, retrieval modes and granularity, graph-to-prompt formats, schema-first text-to-Cypher, the LangGraph QA agent |
| 12 | [KG as shared agent memory](notes/12-kg-as-shared-agent-memory.md) | State vs. memory, loop → swarm → graph, `GraphUpdate`, reversible ER and provenance, five planes, swarm cost |
| 13 | [Learning on graphs](notes/13-graph-ml-and-gnns.md) | Why nodes aren't i.i.d., the task map, manual vs. learned features, DWPC, embeddings and message passing, GNN + LLM patterns, LLM graph reasoning and its limits, predictions as claims |

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
| Never execute model-written Cypher as a write: extract structured mentions, assemble with deterministic `MERGE` | [10](notes/10-building-kgs-with-llms.md) |
| A live KG needs standing pipelines for update, assessment, deletion and access, not a one-off build | [10](notes/10-building-kgs-with-llms.md) |
| Return the smallest graph unit the question needs: node, triplet, path, then subgraph | [11](notes/11-kg-rag-and-text-to-cypher.md) |
| Paths, degree and ordering are graph queries, not prompts: give the model the tool | [13](notes/13-graph-ml-and-gnns.md) |
| If a run's only durable record is its chat transcript, you have no graph | [12](notes/12-kg-as-shared-agent-memory.md) |
| Beat a domain-informed feature baseline before trusting a learned embedding | [13](notes/13-graph-ml-and-gnns.md) |
| A predicted edge is a claim: flag it, score it, keep it out of default traversals | [13](notes/13-graph-ml-and-gnns.md) |

---

## Resource map

### Related notes elsewhere
- Memory-augmented RAG notes are merged into 02-context [notes/06-memory.md](../02-context-engineering/notes/06-memory.md) (memory designs) and [generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md](../../generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md) (retrieval).

### Book notes — *Knowledge Graphs and LLMs in Action* (Manning)
- [sources/kg-and-llms-in-action/](sources/kg-and-llms-in-action/): the chapter PDFs, `chNN-<topic>.pdf` and `appendix-{a,b,c}-<topic>.pdf`. Their content is folded into notes 09–13, which cite the chapter for each claim (ch1–3 and appendices A–B → 09, ch4–8 and appendix C → 10, ch13–15 → 11, ch9–12 → 13). Topics: KG+LLM hybrid systems, ontology-driven construction, multisource integration, LLM-driven extraction, named entity disambiguation, graph feature engineering, GNNs (representation learning, node classification, link prediction), KG-powered RAG, text-to-Cypher, and a LangGraph QA agent — plus graph-theory, Neo4j and structured-sources appendices.

### Other books folded in
- Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), [sources/building-ai-agents-llms-rag-kgs/](sources/building-ai-agents-llms-rag-kgs/). Ch. 7 → notes 10 (KG lifecycle after the load), 11 (retrieval granularity, retrievers, prompt formats, HybridRAG) and 13 (LLM graph reasoning and its limits). Ch. 9 → notes 05, 06 and 07.
- Albada, *Building Applications with AI Agents* (O'Reilly, 2025), [sources/building-applications-with-ai-agents/](sources/building-applications-with-ai-agents/). Ch. 8 → notes 05 and 07 (actor-critic, supervisor routing, A2A, ADAS, distributed transports).
- Oshin & Campos, *Learning LangChain* (O'Reilly, 2025), PDFs in [generative-ai/01-llm-fundamentals/sources/learning-langchain/](../../generative-ai/01-llm-fundamentals/sources/learning-langchain/). Ch. 5 → notes 02 (the agency ladder, LLM routers) and 03 (input and output schemas).

Chapter-to-note maps and quality flags for all three are in [references.md](references.md).

### Interviewing guide
- [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Notebooks and course code
- DeepLearning.AI × Neo4j, [*Knowledge Graphs for RAG*](https://www.deeplearning.ai/short-courses/knowledge-graphs-rag/) (Kollegger, 2024). The course notebooks are folded into the notes as commented snippets (L1–L2 → note 09, L3–L7 graph building → note 10, L3–L7 retrieval queries → note 11), with deprecated APIs flagged; its figures are in [sources/images/](sources/images/) as `kollegger-knowledge-graphs-for-rag-*`. An `L#` reference in a note is a lesson of this course.
  - **Credentials:** `notebooks/knowledge-graphs-for-rag/code/.env` is the only file left of the local copy of the course. It holds live credentials, is gitignored and has never been committed. Rotate the keys if the repo or that folder is ever shared, and delete the file once you no longer run the notebooks locally.
- [AI-Agents-in-LangGraph-main](../../generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph.md) — LangGraph agent graphs (nodes, edges, state, conditional routing): runnable companion code for notes 01–05 (L1 ReAct from scratch, L2 LangGraph components, L3 agentic search, L4 persistence and streaming).
- [sources/langgraph_extended.pptx](sources/langgraph_extended.pptx) — *LangGraph: A Visual Guide* (26 slides): nodes, edges, state and reducers, memory, checkpointers and durable execution, interrupts and time travel, streaming, subgraphs, observability, and LangGraph vs Google ADK. Also the style reference for the course's `make slides` decks.

### Readings
- [sources/](sources/) — the book PDFs (above), figures in `images/`, and the community-compiled *Graph Engineering: The Karpathy Loop, Improved 1000x by Itself* (2026) PDF.
- Li, *AI Agents in Depth*, [ch. 10 Multi-Agent Collaboration](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter10.md): when multi-agent actually beats single-agent, shared vs isolated context, failure modes. Synthesised into [05](notes/05-topology-patterns.md) (two design dimensions, the new-information test, the runtime as an OS, handoff packages, A2A; [labs table](notes/05-topology-patterns.md#labs)) and [07](notes/07-failure-modes-at-scale.md) (Byzantine faults, semantic conflicts, cascading amplification, MAST). Ch. 3's RAPTOR vs GraphRAG comparison is in [11](notes/11-kg-rag-and-text-to-cypher.md).

### External references and source quality
Every web source, paper and book the notes cite, mapped to notes, with the quality flags for vendor and secondary posts: [references.md](references.md).

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
