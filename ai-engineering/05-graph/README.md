# 05 — Graph Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](../../interviewing/guides/4-agents/00-overview.md)
> Position in the stack: fifth foundation — builds on [04-loop](../04-loop/README.md); *graphs make agent organizations programmable*.
> Deep note: [graph-engineering.md](../../interviewing/notes/graph-engineering.md)

---

## What it is

Graph engineering is the discipline of designing **directed graphs of nodes and edges** to orchestrate multi-agent workflows. Where loop engineering governs individual agent behavior (one agent, one cycle), graph engineering governs the *topology* connecting multiple agents: conditional routing between them, shared state across them, parallel fan-out and merge, and hierarchical composition of subgraphs.

*"Graphs make agent organizations programmable the way loops make individual agent behavior programmable."*

Graph is a **peer fifth foundation**, ordered after loop because it presumes loop mastery — but it is a first-class discipline, not an advanced optional tier. Every graph contains loops; graph engineering is about the structure connecting those loops.

**Inherits the weaknesses of:** loop engineering — a graph routing between unreliable loops inherits all loop failures at the organizational scale.

---

## Resource map

### Deep notes
- [graph-engineering.md](../../interviewing/notes/graph-engineering.md) — graph topology: nodes, edges, state, conditional routing, multi-agent patterns (supervisor, fan-out, hierarchical), human-in-the-loop, and the knowledge-graph-for-RAG facet.

### Interviewing guide
- [4-agents](../../interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [AI-Agents-in-LangGraph-main](../../generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main/) — LangGraph agent graphs: nodes, edges, state, conditional routing.
- [Knowledge_Graphs_for_RAG-main](./Knowledge_Graphs_for_RAG-main/) — knowledge-graph facet: entity graphs as retrieval structure.

### Readings
- [readings/3-rag-knowledge-graphs/](../../readings/3-rag-knowledge-graphs/) — KG for RAG reference papers.

### External references
- LangGraph docs: https://docs.langchain.com/langgraph
- LangGraph GitHub: https://github.com/langchain-ai/langgraph

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
