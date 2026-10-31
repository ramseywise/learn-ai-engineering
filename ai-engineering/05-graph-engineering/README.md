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
2. Use the deck for review or teaching: [slides/graph-engineering.pptx](slides/graph-engineering.pptx), a 4-part talk built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=05-graph-engineering`.
3. Keep the [rules of thumb](#rules-of-thumb) as the one-page summary.

## Layout

```
README.md      this file: overview, start here, rules of thumb, sources
notes/         01–13, the course; figures and code inline
slides/        deck.yaml + graph-engineering.pptx
sources/       book chapters and PDFs, the archived deep note, the LangGraph style deck
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
| 3 | [State and reducers](notes/03-state-and-reducers.md) | Typed state, reducers, parallel-write races, Send fan-out, handoffs, the true-dependency test |
| 4 | [Durable execution and interrupts](notes/04-durable-execution-and-interrupts.md) | Checkpointers, threads, `interrupt()`, editing state, time travel, where gates go |
| 5 | [Topology patterns](notes/05-topology-patterns.md) | Generate-then-verify, supervisor, fan-out, subgraphs, handoff; the Claude Code mapping |
| 6 | [When not to build a graph](notes/06-when-not-to-build-a-graph.md) | Unnameable work, fan-out cost, premature graphs, split the verifier, incremental adoption |
| 7 | [Failure modes at scale](notes/07-failure-modes-at-scale.md) | Mechanical and control failures, correlated errors, verifier isolation, anchors, pre-flight check |
| 8 | [Governance and production](notes/08-governance-and-production.md) | IDs and tracing, budgets, approvals, the checklist, n8n case study |
| 9 | [KG fundamentals and Cypher](notes/09-kg-fundamentals-and-cypher.md) | What a KG is, why it pairs with LLMs, LPG vs. RDF, typed edges, Cypher cheat sheet |
| 10 | [Building KGs with LLMs](notes/10-building-kgs-with-llms.md) | Per-hop compounding, the extraction pipeline, model tiers, metagraph, ER and NED, extraction evals |
| 11 | [KG-RAG and text-to-Cypher](notes/11-kg-rag-and-text-to-cypher.md) | Vector RAG limits, GraphRAG evidence, retrieval modes, schema-first text-to-Cypher, the LangGraph QA agent |
| 12 | [KG as shared agent memory](notes/12-kg-as-shared-agent-memory.md) | State vs. memory, loop → swarm → graph, `GraphUpdate`, reversible ER and provenance, five planes, swarm cost |
| 13 | [Learning on graphs](notes/13-graph-ml-and-gnns.md) | Why nodes aren't i.i.d., the task map, manual vs. learned features, DWPC, embeddings and message passing, GNN + LLM patterns, predictions as claims |

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

## Resource map

### Deep notes
- [sources/graph-engineering-deep-note.md](sources/graph-engineering-deep-note.md): the original single deep note, archived. A `§N` reference in a note means a section of this file.
- Memory-augmented RAG notes are merged into 02-context [notes/06-memory.md](../02-context-engineering/notes/06-memory.md) (memory designs) and [generative-ai/02-rag-retrieval/rag.md](../../generative-ai/02-rag-retrieval/rag.md) (retrieval).

### Book notes — *Knowledge Graphs and LLMs in Action* (Manning)
- [sources/kg-and-llms-in-action/](sources/kg-and-llms-in-action/) — the depth layer under notes 09–13 (ch1–3 → 09, ch4–8 → 10, ch13–15 → 11, ch9–12 → 13; chapter PDFs in `pdf/`). Chapter-by-chapter notes: KG+LLM hybrid systems, ontology-driven construction, multisource integration, LLM-driven extraction, named entity disambiguation, graph feature engineering, GNNs (representation learning, node classification, link prediction), KG-powered RAG, text-to-Cypher, and a LangGraph QA agent — plus graph-theory and Neo4j/Cypher appendices.

### Interviewing guide
- [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Notebooks and course code
- DeepLearning.AI × Neo4j, [*Knowledge Graphs for RAG*](https://www.deeplearning.ai/short-courses/knowledge-graphs-rag/) (Kollegger, 2024). The course notebooks are folded into the notes as commented snippets (L1–L2 → note 09, L3–L7 graph building → note 10, L3–L7 retrieval queries → note 11), with deprecated APIs flagged; its figures are in [sources/images/](sources/images/) as `kollegger-knowledge-graphs-for-rag-*`. An `L#` reference in a note is a lesson of this course.
  - **Credentials:** `notebooks/knowledge-graphs-for-rag/code/.env` is the only file left of the local copy of the course. It holds live credentials, is gitignored and has never been committed. Rotate the keys if the repo or that folder is ever shared, and delete the file once you no longer run the notebooks locally.
- [AI-Agents-in-LangGraph-main](../../generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main/) — LangGraph agent graphs (nodes, edges, state, conditional routing); used in the Track A labs. An `LG L#` reference means `Lesson_#_Student.ipynb` there (L1 ReAct from scratch, L2 LangGraph components, L3 agentic search, L4 persistence and streaming).
- [sources/langgraph_extended.pptx](sources/langgraph_extended.pptx) — *LangGraph: A Visual Guide* (26 slides): nodes, edges, state and reducers, memory, checkpointers and durable execution, interrupts and time travel, streaming, subgraphs, observability, and LangGraph vs Google ADK. Also the style reference for the course's `make slides` decks.

### Readings
- [sources/](sources/) — the book (notes and PDFs, above), the archived deep note, and the community-compiled *Graph Engineering: The Karpathy Loop, Improved 1000x by Itself* (2026) PDF.
- Li, *AI Agents in Depth*, [ch. 10 Multi-Agent Collaboration](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter10.md): when multi-agent actually beats single-agent, shared vs isolated context, failure modes. Synthesised into [05](notes/05-topology-patterns.md) (two design dimensions, the new-information test, the runtime as an OS, handoff packages, A2A; [labs table](notes/05-topology-patterns.md#labs)) and [07](notes/07-failure-modes-at-scale.md) (Byzantine faults, semantic conflicts, cascading amplification, MAST). Ch. 3's RAPTOR vs GraphRAG comparison is in [11](notes/11-kg-rag-and-text-to-cypher.md).

### External references
- LangGraph docs: https://docs.langchain.com/langgraph
- Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) and [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (source of the ~15× token figure).
- Edge et al., [From Local to Global: a Graph RAG approach](https://arxiv.org/abs/2404.16130) (GraphRAG, 2024).
- Anthropic, [knowledge graph construction cookbook](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide).
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

### Source quality

Several external references above are secondary or vendor posts. Per [SOURCES.md](../SOURCES.md), Tier 2 sources are gap-detectors, not citations of record. The notes flag numbers that rest on them; corroborate before you quote them:

| Source | Problem | Corroborate via |
|---|---|---|
| flowtivity.ai, "graph engineering 2026 guide" | Vendor marketing; supplies most of the hard numbers (~3× tokens, ~50% break-even, ~18% typed-edge gain, 53.4 vs 42.9% multi-hop, "~3× faster") and the OpenClaw / Codex tooling claims | Your own measurements (lab A5); the GraphRAG paper; LangGraph docs |
| youmind.com viral-article landing page | Source of the Bun $165k figure and Dynamic Workflows limits | Anthropic docs for Dynamic Workflows; Bun's own post; otherwise drop |
| pkhamdee.blog | Personal blog synthesising primary sources | Karpathy's autoresearch repo; Anthropic's KG cookbook; Anthropic engineering posts |
| [sources/graph-engineering-karpathy-loop-anthropic-playbook-2026.pdf](sources/graph-engineering-karpathy-loop-anthropic-playbook-2026.pdf) | Community-compiled; carries an Anthropic logo but says "not affiliated … not endorsed" | Cite as secondary only |
| explainx.ai/post/graph-engineering | SEO aggregator | Drop; LangChain's "3 years of graph engineering" has the same line first-hand |
| Medium, GaoDalie "Forget loop engineering" | Opinion piece; overstates | A quote at most, not evidence |
| Medium, Rathod n8n deep dive | Third-party teardown | n8n's own source and `docs.n8n.io` |
| aibuilderclub.com | Tier 2 aggregator | Claude Code docs (subagents, hooks), Claude Agent SDK docs, *Building effective agents* |
| truefoundry.com enterprise guide | Vendor (sells an AI gateway); gateway-centric framing | OpenTelemetry GenAI semantic conventions; LangSmith / LangGraph tracing docs |
| eigent.ai blog | Vendor blog; sound framing but uncited | Keep as framing; anchor Goodhart in the original literature |

First-party and fine to cite: LangChain's "3 years of graph engineering with LangGraph", the LangGraph docs and GitHub, `docs.n8n.io`, Anthropic's engineering posts, Addy Osmani.

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
