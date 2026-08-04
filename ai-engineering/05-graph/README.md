# 05 — Graph Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](../../interviewing/guides/4-agents/00-overview.md)
> Position in the stack: fifth foundation — builds on [04-loop](../04-loop/README.md); *graphs make agent organizations programmable*.
> Deep note: [graph-engineering.md](graph-engineering.md)

---

## What it is

Graph engineering is the discipline of designing the **topology** of a multi-agent system: which nodes exist (agents, deterministic functions, routers, human checkpoints), which transitions between them are permitted, and how the runtime work graph forms and mutates. Where loop engineering governs individual agent behavior (one agent, one cycle), graph engineering governs the structure connecting multiple agents — conditional routing, shared state, parallel fan-out and merge, and hierarchical composition of subgraphs.

*"Graphs make agent organizations programmable the way loops make individual agent behavior programmable."*

Graph is a **peer fifth foundation**, ordered after loop because it presumes loop mastery — but it is a first-class discipline, not an advanced optional tier. The relationship is containment, not replacement: per LangChain, *"a loop is just a directed, cyclic graph."*

**Two things called "graph engineering."** Agent graphs are *execution topology* (nodes = computation, edges = permitted transitions). Knowledge graphs are *retrieval structure* (nodes = entities, edges = typed relationships). Both live in this pillar; keep the distinction sharp.

**Not everything should be a graph.** Work whose steps can't be named ahead of time — generic deep research is the canonical case — belongs in a harness with a good loop. Forcing it into deterministic paths is the wrong move, and graph fan-out runs ~3× the tokens per cycle (Anthropic's multi-agent research system: ~15× a chat turn).

**Inherits the weaknesses of:** loop engineering — a graph routing between unreliable loops inherits all loop failures at the organizational scale, and adds coordination failures on top.

---

## Resource map

### Deep notes
- [graph-engineering.md](graph-engineering.md) — the full discipline: primitives (nodes, edges, state, reducers, checkpointers, interrupts, Send API), why production agents aren't DAGs, topology patterns, when *not* to build a graph, scale failure modes and anchors, enterprise governance checklist, Claude Code mapping, the KG facet (including the KG as
  shared memory for swarms, and swarm cost anchors), adoption methodology, and the n8n
  supervisor-graph case study.
- [memory.md](memory.md) — memory and state across graph nodes.

### Book notes — *Knowledge Graphs and LLMs in Action* (Manning)
- [kg-and-llms-in-action/](kg-and-llms-in-action/) — chapter-by-chapter notes: KG+LLM hybrid systems, ontology-driven construction, multisource integration, LLM-driven extraction, named entity disambiguation, graph feature engineering, GNNs (representation learning, node classification, link prediction), KG-powered RAG, text-to-Cypher, and a LangGraph QA agent — plus graph-theory and Neo4j/Cypher appendices.

### Interviewing guide
- [4-agents](../../interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [AI-Agents-in-LangGraph-main](../../generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main/) — LangGraph agent graphs: nodes, edges, state, conditional routing.
- [Knowledge_Graphs_for_RAG-main](./Knowledge_Graphs_for_RAG-main/) — knowledge-graph facet: entity graphs as retrieval structure.

### Readings
- [3-rag-knowledge-graphs/](3-rag-knowledge-graphs/) — KG-for-RAG source PDFs (book chapters + reference papers).

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
← Builds on [04-loop/](../04-loop/README.md)
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
