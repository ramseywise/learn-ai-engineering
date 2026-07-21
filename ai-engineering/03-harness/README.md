# 03 — Harness Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](../../interviewing/guides/4-agents/00-overview.md)
> Position in the stack: *harness implements loops*.
> Deep note: [agent-harness.md](../../interviewing/notes/agent-harness.md)

---

## What it is

Harness engineering is the scaffolding discipline: building the infrastructure that makes agent loops deployable, reliable, observable, and safe. A harness wraps one or more agent loops and provides: tool execution, memory integration, guardrails, permissions, observability hooks, error handling, and verification. The harness is the layer at which eval/memory/observability become **first-class primitives** (not afterthoughts).

Per `awesome-harness-engineering`: verification & CI/evals, memory & state, observability, permissions, and tool design are essential harness primitives — they determine agent reliability.

**Inherits the weaknesses of:** context engineering — a harness that supplies poorly composed context to its loops will fail at scale regardless of how well the scaffolding itself is engineered.

---

## Resource map

### Deep notes
- [agent-harness.md](../../interviewing/notes/agent-harness.md) — harness primitives: tool execution, memory, guardrails, observability. Cites LangChain, OpenAI, Interloom.
- [agents-design.md](../../interviewing/notes/agents-design.md) — agent architecture patterns: single-agent, multi-agent, tool routing.
- [deep-agents.md](../../interviewing/notes/deep-agents.md) — depth on agentic architectures: planning, reflection, self-critique.
- [agents-guardrails.md](../../interviewing/notes/agents-guardrails.md) — guardrails and safety constraints in harness design.

### Interviewing guide
- [4-agents](../../interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [AI-Agentic-Design-Patterns-with-AutoGen-main](../../generative-ai/coursera-references/AI-Agentic-Design-Patterns-with-AutoGen-main/) — agentic design patterns.
- [AgenticAIFrameworks-master](../../generative-ai/coursera-references/AgenticAIFrameworks-master/) — framework survey.

### External reading queue
- Lilian Weng, "Harness Engineering for Self-Improvement": https://lilianweng.github.io/posts/2026-07-04-harness — authoritative; ties harness→loop→self-improvement.
- `awesome-harness-engineering`: https://github.com/ai-boost/awesome-harness-engineering — comprehensive; covers evals, memory, MCP, orchestration.

### Next layer
→ [04-loop/](../04-loop/README.md) — the loops the harness implements.

---

## Working References

Claude Code convention references that map to this pillar. These files live at `~/.claude/refs/` and can be consulted in any Claude Code session.

### `agent-tools.md`
Conventions for what makes a tool call gateable, auditable, and parallel-safe — and when a capability should become an MCP server rather than an in-process tool.

Key topics for this pillar:
- Four tool design questions: reversible, idempotent, observable, parallel-safe — tools that fail #1 need a confirmation gate
- Promote-from-bash heuristic: start with shell, promote when you need gate/render/audit/parallelize/retry
- Tool schema rules: `snake_case` verb-noun names, side-effects declared in description, typed return structure, structured error returns
- MCP vs. in-process decision table: latency, caller diversity, security boundary, state, discovery, deployment independence
- Write-operation safety: description declares side-effect, confirmation step before irreversible execution, idempotency key on retries

### `agent-safety.md`
Conventions for threat modeling and protection layers in the harness.

Key topics for this pillar:
- Five protection layers: pre-input, pre-retrieval, pre-generate, post-generate, escalation — each independently toggleable
- Threat model: trust zones for user input (untrusted), retrieved content (semi-trusted), tool inputs/outputs (agent-composed / semi-trusted), agent state (trusted)
- Tool input validation: validate model-generated tool inputs against schema before execution
- Sandboxing: isolated execution for code-running agents; explicit egress rules
- PII handling: redact before logging, do not pass to unapproved third-party endpoints

### `agent-reliability.md`
Conventions for what happens on tool error, rate limit, refusal, or timeout — and how to make a run resumable.

Key topics for this pillar:
- Failure taxonomy: transient (retry with backoff), tool error (retry once then escalate), model refusal (never retry), schema violation, context exhaustion, fatal
- Retry policy defaults: max 3 retries (transient), exponential backoff 2×, jitter ±20%; retry budget is per-invocation not per-tool
- Idempotency: caller-generated idempotency keys on write/mutate/send operations; tools without keys must not be retried
- Graceful degradation: partial result with `degraded: true` flag; never degrade silently
- Circuit breaking: open after 5 consecutive failures; 60s cooldown; fail fast with `circuit_open` code
- Structured error returns: stable `error_code`, `is_fatal`, `retry_after`, `run_id`, `step` fields on every error path
