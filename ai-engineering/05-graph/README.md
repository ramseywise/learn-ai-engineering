# 05 — Graph Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](../../interviewing/guides/4-agents/00-overview.md)
> Position in the stack: fifth foundation — builds on [04-loop](../04-loop/README.md); *graphs make agent organizations programmable*.
> Deep note: [graph-engineering.md](graph-engineering.md)

---

## What it is

Graph engineering is the discipline of designing **directed graphs of nodes and edges** to orchestrate multi-agent workflows. Where loop engineering governs individual agent behavior (one agent, one cycle), graph engineering governs the *topology* connecting multiple agents: conditional routing between them, shared state across them, parallel fan-out and merge, and hierarchical composition of subgraphs.

*"Graphs make agent organizations programmable the way loops make individual agent behavior programmable."*

Graph is a **peer fifth foundation**, ordered after loop because it presumes loop mastery — but it is a first-class discipline, not an advanced optional tier. Every graph contains loops; graph engineering is about the structure connecting those loops.

**Inherits the weaknesses of:** loop engineering — a graph routing between unreliable loops inherits all loop failures at the organizational scale.

---

## Resource map

### Deep notes
- [graph-engineering.md](graph-engineering.md) — graph topology: nodes, edges, state, conditional routing, multi-agent patterns (supervisor, fan-out, hierarchical), human-in-the-loop, and the knowledge-graph-for-RAG facet.
- [memory.md](memory.md) — memory architectures: in-context, external, episodic, semantic; memory as a graph state primitive.

### Interviewing guide
- [4-agents](../../interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [AI-Agents-in-LangGraph-main](../../generative-ai/03-agentic-foundations/AI-Agents-in-LangGraph-main/) — LangGraph agent graphs: nodes, edges, state, conditional routing.
- [Knowledge_Graphs_for_RAG-main](Knowledge_Graphs_for_RAG-main/) — knowledge-graph facet: entity graphs as retrieval structure.

### Readings
- [3-rag-knowledge-graphs/](3-rag-knowledge-graphs/) — KG for RAG reference papers.

### External references
- LangGraph docs: https://docs.langchain.com/langgraph
- LangGraph GitHub: https://github.com/langchain-ai/langgraph

### Previous and next layer
← Builds on [04-loop/](../04-loop/README.md)
→ [06-eval/](../06-eval/README.md) — eval measures graph correctness and multi-agent coordination quality.
