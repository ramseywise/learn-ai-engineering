# 03 — Harness Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](../../interviewing/guides/4-agents/00-overview.md)
> Position in the stack: *harness implements loops*.
> Overview note: [harness-engineering.md](harness-engineering.md) · Topic depth: [notes/](notes/)

---

## What it is

Harness engineering is the scaffolding discipline: building the infrastructure that makes agent loops deployable, reliable, observable, and safe. A harness wraps one or more agent loops and provides tool execution, memory integration, guardrails, permissions, observability hooks, error handling, and verification. It is the layer at which eval/memory/observability become **first-class primitives** (not afterthoughts).

The governing equation: **Agent = Model + Harness.** The model holds the intelligence; the harness is the system that makes it useful — everything between request and output except the weights. The discipline nests: *prompt engineering ⊂ context engineering ⊂ harness engineering.*

Why the harness dominates: **reliability compounds negatively.** A 90%-reliable step chained five times lands near 60%, and real agents exceed five steps once tool calls and parses are counted. Hence the field's slogan — **a decent model with a great harness beats a great model with a bad harness** — and its evidence: LangChain moved a coding agent from 52.8% → 66.5% on Terminal Bench 2.0 with *harness-only* changes on a fixed model.

The operating reframe is that agent failures are **configuration problems, not model limitations**. Every failure gets engineered out permanently (*the ratchet*), so the harness tightens each time the agent slips.

**Inherits the weaknesses of:** context engineering — a harness that supplies poorly composed context to its loops will fail at scale regardless of how well the scaffolding itself is engineered.

---

## Resource map

### Deep notes
- [harness-engineering.md](harness-engineering.md) — pillar overview: Agent = Model + Harness, the failures-are-config reframe, the ratchet, the five components, convergent design.

#### Topic notes ([notes/](notes/))
1. [What a harness is](notes/01-what-a-harness-is.md) — Agent = Model + Harness, the four parts, the harness gap, the ratchet, convergent design.
2. [Harness anatomy](notes/02-harness-anatomy.md) — the nine components, filesystem as foundational primitive, bash-as-general-tool, the causal build order.
3. [Tool design as harness surface](notes/03-tool-design.md) — ACI over API, the five-section tool contract, the four gating questions, MCP vs. in-process.
4. [Execution boundaries and guardrails](notes/04-execution-boundaries.md) — sandboxes, hooks, silent-success/verbose-failure, encoded constraints, the five protection layers.
5. [Verification and feedback loops](notes/05-verification-loops.md) — self-verification, process/data/draft reflection, asymmetric QA, when to delete a verifier, generator/evaluator separation, sprint contracts, dataset vs. live-traffic eval, two-retry rule, loop detection.
6. [Long-horizon execution](notes/06-long-horizon-execution.md) — state externalization, compaction vs. context reset, context anxiety, Ralph loops, plans as artifacts.
7. [Orchestration and multi-agent harnesses](notes/07-orchestration.md) — subagents as context firewall, role separation, ADK 2.0 graph primitives, oscillation and deadlock.
8. [Harness maturity and failure modes](notes/08-maturity-and-failure-modes.md) — the five-stage model, the six-stage pipeline, production reliability primitives, five failure modes, iterative simplification.

#### Related
- [karpathy-method.md](karpathy-method.md) — Karpathy's AISN 2026 framing (via secondary video source): spec / verifier / environment layering, animals-vs-ghosts, rules-vs-requests.
- [agent-harness.md](agent-harness.md) — raw source note (Notion export) behind the overview; kept for provenance.
- [reliable-agents.md](reliable-agents.md) — raw source note (Notion export): the Bayer/Thoughtworks **PRINCE** case study, the pillar's only production system. Harness content extracted into [notes/05](notes/05-verification-loops.md) and [notes/08](notes/08-maturity-and-failure-modes.md); its RAG/Text-to-SQL pipeline detail is still unextracted and belongs to [02-context](../02-context/notes/03-retrieval-strategies.md).
- [agents-design.md](agents-design.md) — agent architecture patterns: single-agent, multi-agent, tool routing.
- [deep-agents.md](../04-loop/deep-agents.md) — depth on agentic architectures: planning, reflection, self-critique.
- [agents-guardrails.md](agents-guardrails.md) — guardrails and safety constraints in harness design.
- [skills-design.md](skills-design.md) — skills as a harness primitive: descriptions as routing logic, negative examples, bundled templates, explicit invocation, and the skills+networking risk posture.

### Interviewing guide
- [4-agents](../../interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [AI-Agentic-Design-Patterns-with-AutoGen-main](../../generative-ai/03-agentic-foundations/AI-Agentic-Design-Patterns-with-AutoGen-main/) — agentic design patterns.
- [AgenticAIFrameworks-master](../../generative-ai/03-agentic-foundations/AgenticAIFrameworks-master/) — framework survey.

### External sources

Read into [notes/](notes/) on 2026-07-29:

| Source | Contributes |
|---|---|
| [Anthropic — harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) | Planner/generator/evaluator, context anxiety, sprint contracts, grading criteria, iterative simplification |
| [LangChain — anatomy of an agent harness](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness) | The nine components; filesystem as foundational primitive |
| [LangChain — improving deep agents](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) | 52.8→66.5 Terminal Bench; middleware trio, reasoning sandwich, trace analyzer |
| [Addy Osmani — agent harness engineering](https://addyosmani.com/blog/agent-harness-engineering/) | Agent = Model + Harness, the ratchet, `AGENTS.md` rules, hook strategy, convergent design |
| [harness-engineering.ai — what is harness engineering](https://harness-engineering.ai/blog/what-is-harness-engineering/) | The five components; prompt ⊂ context ⊂ harness nesting |
| [AI-native playbook — harness engineering](https://ai-native-playbook.vercel.app/guides/the-machine/harness-engineering) | Five-stage maturity model, six-stage pipeline, five failure modes, asymmetric QA |
| [Vercel Academy — build an agent harness](https://vercel.com/academy/build-ai-agent-harness) | 38-lesson causal build order; five-section tool contract; sandbox abstraction |
| [Rob Earlam — introduction](https://robearlam.com/blog/an-introduction-to-harness-engineering) | Horse-and-harness framing; agents/roles/artifacts/standards |
| [Google ADK 2.0 multi-agent](https://medium.com/google-cloud/harness-engineering-for-multi-agent-systems-using-google-adk-2-0-e248b885cb95) | Graph primitives, typed state, event routing, multi-agent failure modes |
| [Anthropic — effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Agent-loop framing, compaction, structured note-taking, tool clarity test |
| [Martin Fowler — building reliable agentic AI systems (Bayer PRINCE)](https://martinfowler.com/articles/reliable-llm-bayer.html) | Process/data/draft reflection, deleting a false-positive verifier, live-traffic eval, node-level retry, resume-from-failure, provider fallback, confidence-scored HITL |

Queue (not yet read in):
- Lilian Weng, "Harness Engineering for Self-Improvement": https://lilianweng.github.io/posts/2026-07-04-harness — ties harness→loop→self-improvement.
- `awesome-harness-engineering`: https://github.com/ai-boost/awesome-harness-engineering — evals, memory, MCP, orchestration.

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
