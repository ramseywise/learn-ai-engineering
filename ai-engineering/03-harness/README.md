# 03 — Harness Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](../../interviewing/guides/4-agents/00-overview.md)
> Position in the stack: *harness implements loops*.
> Deep note: [agent-harness.md](agent-harness.md)

---

## What it is

Harness engineering is the scaffolding discipline: building the infrastructure that makes agent loops deployable, reliable, observable, and safe. A harness wraps one or more agent loops and provides: tool execution, memory integration, guardrails, permissions, observability hooks, error handling, and verification. The harness is the layer at which eval/memory/observability become **first-class primitives** (not afterthoughts).

Per `awesome-harness-engineering`: verification & CI/evals, memory & state, observability, permissions, and tool design are essential harness primitives — they determine agent reliability.

**Inherits the weaknesses of:** context engineering — a harness that supplies poorly composed context to its loops will fail at scale regardless of how well the scaffolding itself is engineered.

---

## Resource map

### Deep notes
- [agent-harness.md](agent-harness.md) — harness primitives: tool execution, memory, guardrails, observability. Cites LangChain, OpenAI, Interloom.
- [agents-design.md](agents-design.md) — agent architecture patterns: single-agent, multi-agent, tool routing.
- [agents-guardrails.md](agents-guardrails.md) — guardrails and safety constraints in harness design.
- [reliable-agents.md](reliable-agents.md) — reliability patterns: retry logic, graceful degradation, human-in-the-loop escalation.

### Interviewing guide
- [4-agents](../../interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [AI-Agentic-Design-Patterns-with-AutoGen-main](../../generative-ai/03-agentic-foundations/AI-Agentic-Design-Patterns-with-AutoGen-main/) — agentic design patterns.
- [AgenticAIFrameworks-master](../../generative-ai/03-agentic-foundations/AgenticAIFrameworks-master/) — framework survey.

### External reading queue
- Lilian Weng, "Harness Engineering for Self-Improvement": https://lilianweng.github.io/posts/2026-07-04-harness — authoritative; ties harness→loop→self-improvement.
- `awesome-harness-engineering`: https://github.com/ai-boost/awesome-harness-engineering — comprehensive; covers evals, memory, MCP, orchestration.

### Next layer
→ [04-loop/](../04-loop/README.md) — the loops the harness implements.
