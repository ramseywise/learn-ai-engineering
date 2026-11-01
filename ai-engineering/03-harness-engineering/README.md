# 03 — Harness Engineering

> Depth layer. Summary: [interviewing/guides/4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md)
> Position in the stack: *harness implements loops*.
> Start with [notes/01](notes/01-what-a-harness-is.md) · Sources: [references.md](references.md)

---

## What it is

Harness engineering is the scaffolding discipline: building the infrastructure that makes agent loops deployable, reliable, observable, and safe. A harness wraps one or more agent loops and provides tool execution, memory integration, guardrails, permissions, observability hooks, error handling, and verification. It is the layer at which eval/memory/observability become **first-class primitives** (not afterthoughts).

The governing equation: **Agent = Model + Harness.** The model holds the intelligence; the harness is the system that makes it useful — everything between request and output except the weights. The discipline nests: *prompt engineering ⊂ context engineering ⊂ harness engineering.*

Why the harness dominates: **reliability compounds negatively.** A 90%-reliable step chained five times lands near 60%, and real agents exceed five steps once tool calls and parses are counted. Hence the field's slogan — **a decent model with a great harness beats a great model with a bad harness** — and its evidence: LangChain moved a coding agent from 52.8% → 66.5% on Terminal Bench 2.0 with *harness-only* changes on a fixed model.

The operating reframe is that agent failures are **configuration problems, not model limitations**. Every failure gets engineered out permanently (*the ratchet*), so the harness tightens each time the agent slips.

**Inherits the weaknesses of:** context engineering — a harness that supplies poorly composed context to its loops will fail at scale regardless of how well the scaffolding itself is engineered.

---

## Start here

Read the notes in order. 01–08 are the harness as components; 09–10 put it into a real repo.

1. [What a harness is](notes/01-what-a-harness-is.md) — Agent = Model + Harness, the four parts, three data points (LangChain, Agent S4, Vercel), five no-harness failures, the ratchet, convergent design.
2. [Harness anatomy](notes/02-harness-anatomy.md) — the nine components, the five subsystems and ablation, one real harness (the Gemini Minecraft run) read through them, Deep Agents capability groups, the filesystem as foundational primitive.
3. [Tool design as harness surface](notes/03-tool-design.md) — ACI over API, the five-section tool contract, the four gating questions, tool discovery at scale, writing a skill, MCP vs. in-process.
4. [Execution boundaries and guardrails](notes/04-execution-boundaries.md) — the isolation ladder, shell vs. interpreter, hooks, rules vs. requests, tool allowlists, reviewers, the five protection layers, the canary pattern.
5. [Verification and feedback loops](notes/05-verification-loops.md) — the three-layer termination check, three kinds of reflection, asymmetric QA, generator/evaluator separation and an observer agent, sprint contracts, loop detection and injected nudges, retry taxonomy.
6. [Long-horizon execution](notes/06-long-horizon-execution.md) — state externalization, the session lifecycle (initialization, clock in, state files, handoff, clean-state exit, entropy management), compaction vs. reset, Ralph loops, a 27-hour run.
7. [Orchestration and multi-agent harnesses](notes/07-orchestration.md) — subagents as context firewall, protocols before collaboration, role separation, ADK 2.0 graphs, handoff design, coordination without a coordinator.
8. [Harness maturity and failure modes](notes/08-maturity-and-failure-modes.md) — the five-stage model, production reliability primitives, the quality document, five failure modes, iterative simplification, a family of harnesses and a router.
9. [The repo as system of record](notes/09-repo-as-system-of-record.md) — the fresh-session test, `AGENTS.md` as a router (and how long it should be), Karpathy's environment layer, making the map enforceable.
10. [Scope and done](notes/10-scope-and-done.md) — the spec first, WIP = 1, the feature list as a primitive, the behavior/verification/state triple, pass-state gating.

Lecture deck: [slides/harness-engineering.pptx](slides/harness-engineering.pptx), a 5-part talk that grows one refund agent from demo to production harness, built from [slides/deck.yaml](slides/deck.yaml) with `make slides PILLAR=03-harness-engineering`.

## Lab

A tool server with sandboxing: file tools behind a sandbox boundary, with the attempts it refuses in the output. It comes in both languages, side by side, on the same inputs. Both run offline with a stub by default, and each README says how to swap in a real model.

| Language | Folder | Run |
|---|---|---|
| TypeScript | [practice/tool-server-sandbox/](practice/tool-server-sandbox/README.md) | `cd practice/tool-server-sandbox && npx tsx run.ts` |
| Python | [practice/tool-server-sandbox-py/](practice/tool-server-sandbox-py/README.md) | `cd practice/tool-server-sandbox-py && uv run run.py` |

## Layout

```
README.md         this file
references.md     primary sources, upstream course, what was kept and dropped
notes/            01–10, the course; figures and code inline
slides/           deck.yaml + harness-engineering.pptx
practice/         the lab, in TypeScript and Python
sources/          paper PDFs + images/ (figures used by notes and deck)
```

Related outside this pillar: PRINCE's retrieval stack (RAG, Text-to-SQL, NER) is in [generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince.md](../../generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince.md).

---

## Resource map

### Interviewing guide
- [4-agents](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/4-agents/00-overview.md) — compressed summary for interview prep.

### Coursera code
- [AI-Agentic-Design-Patterns-with-AutoGen-main](../../generative-ai/03-agentic-foundations/notes/04-multi-agent-design-patterns.md) — agentic design patterns.
- [AgenticAIFrameworks-master](../../generative-ai/03-agentic-foundations/notes/05-framework-survey.md) — framework survey.

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

Read in on 2026-10-28 for notes 09–10 (details in [references.md](references.md)):

| Source | Contributes |
|---|---|
| [OpenAI — harness engineering](https://openai.com/index/harness-engineering/) | Repo as system of record, `AGENTS.md` as a map, enforced layering, golden rules and background cleanup |
| [Anthropic — effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Initializer agent, JSON feature list, one feature per session, progress file + git continuity |
| [walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering) | Course structure behind notes 06, 09, 10 |

Queue (not yet read in):
- Lilian Weng, "Harness Engineering for Self-Improvement": https://lilianweng.github.io/posts/2026-07-04-harness — ties harness→loop→self-improvement.
- `awesome-harness-engineering`: https://github.com/ai-boost/awesome-harness-engineering — evals, memory, MCP, orchestration.

Read in on 2026-10-31 from `sources/`: Faldor et al. (Minecraft run), Li G. et al. (Object-Oriented Harness), Agashe et al. (Agent S4). Details in [references.md](references.md).

### Next layer
→ [04-loop-engineering/](../04-loop-engineering/README.md) — the loops the harness implements.

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
