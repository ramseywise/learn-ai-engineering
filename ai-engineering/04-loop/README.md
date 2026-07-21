# 04 — Loop Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](../../interviewing/guides/4-agents/00-overview.md)
> Position in the stack: *loops make agent behavior programmable; the graph foundation ([05-graph](../05-graph/README.md)) builds on loops*.
> Deep note: [loop-engineering.md](../../interviewing/notes/loop-engineering.md)

---

## What it is

Loop engineering is the discipline of designing the **perceive → decide → act → repeat** cycle inside an agent. A loop is the unit of individual agent behavior: the model receives observations, reasons about them, selects an action (often a tool call), receives the result, and loops. Loop design governs: termination conditions, action selection strategy, error recovery within a cycle, and how the loop integrates with the surrounding harness.

*"Loops made agent behavior programmable."* — explainx graph-engineering

The next foundation — [05-graph](../05-graph/README.md) — extends this: graphs make *multi-agent organizations* programmable by composing and routing between loops.

**Inherits the weaknesses of:** harness engineering — a loop operating inside a poorly instrumented harness will produce unreliable behavior that is hard to debug, even if the loop logic itself is sound.

---

## Resource map

### Deep notes
- [loop-engineering.md](../../interviewing/notes/loop-engineering.md) — loop anatomy, termination design, tool integration, the art of the loop. Cites LangChain art-of-loop + Anthropic loops blog.
- [reliable-agents.md](../../interviewing/notes/reliable-agents.md) — reliability patterns: retry logic, graceful degradation, human-in-the-loop escalation.

### Interviewing guide
- [4-agents](../../interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [AI-Agents-in-LangGraph-main](../../generative-ai/coursera-references/AI-Agents-in-LangGraph-main/) — agent loops implemented as LangGraph graphs.
- [internet-search-agent-main](../../generative-ai/coursera-references/internet-search-agent-main/) — concrete loop with web-search tooling.

### Next layer
→ [05-graph/](../05-graph/README.md) — graph engineering composes loops into multi-agent topologies.
