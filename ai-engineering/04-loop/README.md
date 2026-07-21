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

---

## Working References

Claude Code convention references that map to this pillar. These files live at `~/.claude/refs/` and can be consulted in any Claude Code session.

### `agent-architecture.md`
Conventions for loop shape selection, termination control, planning strategy, and multi-agent coordination.

Key topics for this pillar:
- Three loop shapes: ReAct (observe→reason→act, repeat), Plan-then-Act (fixed plan), Plan-and-Revise (plan→act→assess→replan) — prefer ReAct for ≤10 steps
- What terminates a turn: `end_turn`, `tool_use`, `max_tokens` (treat as error), context exhaustion — the harness (not the model) sets max iteration count
- Planning: plan-up-front vs. ReAct choice is architectural; hybrid: generate plan, execute, allow per-step replan flag
- Schema contracts: request/response/error schemas as the public API; add fields, never remove until all callers migrate
- State vs. context: context window (this turn), agent state (session), persistent store (cross-session)

### `agent-tools.md`
Conventions for tool design and the agent-loop integration points where tools are called and their results processed.

Key topics for this pillar:
- Promote-from-bash heuristic: when the loop needs a structured gate or retry hook, promote the tool
- Tool result handling: evict completed-step results from context; keep final outputs only (from `agent-context.md`)
- Parallel-safe tool design: tools called in the same loop turn must not race; document serialization strategy
- Observability hooks: each tool call emits a span with tool name, version, input hash, duration, return code, parent trace ID

### `agent-runtime.md`
Conventions for the deployment topology that hosts the agent loop — what each topology forces on loop design.

Key topics for this pillar:
- Three topologies: stateless function, long-lived process, managed runtime — each imposes different constraints on loop state and timeout
- Stateless function constraints: no in-memory session manager, strict timeout bound (Vercel: 10s/60s/300s by tier), no background tasks, state must be externalized
- Cost and latency levers: LLM input tokens (30–50%), output tokens (20–30%), retrieval (10–20%); prompt caching and model tier selection are highest-leverage
- Model routing: cheapest model that can do the job per step type; cascade on refusal or quality gate failure (last resort, not first-line)
- Streaming: stream early; close with structured error frame on mid-stream failure

### `agent-reliability.md`
Conventions for loop-level error recovery — what the loop does when a tool fails, when the model refuses, or when the context is exhausted.

Key topics for this pillar:
- Context exhaustion handling: compact and resume from last checkpoint (coordinated with `agent-context.md §3`)
- Resumability requirements: checkpoint after each plan step; deterministic step re-execution; log resume point on restart
- Refusals: never retry as-is; log, emit `refusal` span event, route to human or return structured error
- Schema violation: retry with rephrased prompt once; fail hard on second violation
