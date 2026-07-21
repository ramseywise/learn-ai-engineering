# Agents — Study Guide

The centerpiece topic for AIE/FDE loops in 2026. Interviewers test whether you can (a) pick
the simplest pattern that works, (b) design the *system around the model* (harness), and
(c) reason about reliability over long horizons and multiple agents.

## 1. Workflows vs agents — always open here

- **Workflow**: LLMs + tools orchestrated through *predefined code paths*.
- **Agent**: the LLM *dynamically directs* its own process and tool use.

Anthropic's production guidance: start with the simplest thing — a single call with
retrieval and examples is often enough; add agency only when it measurably improves
outcomes, because it trades cost and latency for capability. Saying this first signals
judgment, not weakness.

## 2. The five composable workflow patterns

| Pattern | Mechanism | Use when |
|---|---|---|
| Prompt chaining | sequential calls, gates between steps | fixed decomposition; accuracy > latency |
| Routing | classifier → specialized pipeline/model | distinct input classes (easy→small model, hard→large) |
| Parallelization | sectioning (independent subtasks) or voting (same task ×N) | independence, or confidence via consensus |
| Orchestrator–workers | central LLM decomposes dynamically, delegates, synthesizes | subtasks unpredictable (multi-file changes, research) |
| Evaluator–optimizer | generator + critic loop | clear criteria + feedback demonstrably helps |

## 3. Tool design (ACI) — the highest-leverage detail

Treat the agent-computer interface like HCI: tool descriptions written like docstrings for a
junior dev (usage examples, edge cases, boundaries from neighboring tools); careful parameter
naming; **poka-yoke** the arguments so misuse is impossible (canonical example: require
absolute paths — one of the highest-impact fixes in Anthropic's SWE-bench agent, where more
time went into tools than the prompt). Debugging heuristic: when the agent misuses a tool,
fix the tool description before blaming the model. Tool *quality* beats tool *quantity*; and
don't dump every tool message into context — the model needs user/assistant/tool_result, not
the plumbing.

## 4. Harness engineering — "Agent = Model + Harness"

The harness is everything around the model that makes intelligence useful: system
prompts/context policies, tools + skills + MCP servers, bundled infrastructure (filesystem,
sandbox, browser), orchestration logic (subagents, routing, HITL), hooks/middleware for
deterministic control, and a recovery path. Four load-bearing parts to name in interviews:
**acceptance baseline, execution boundary, feedback signals, rollback mechanism**.

Key moves:
- **Filesystem as durable state** — offload what doesn't fit in context; persist work across
  sessions; plan files as first-class artifacts.
- **Bash/code as the universal tool** — agents solve unforeseen problems by writing code, not
  by you pre-designing every tool.
- **Sandbox + self-verification loops** — run tests, read logs, iterate; verification is the
  feedback signal that makes long runs converge.
- **Progressive disclosure (skills)** — load capability descriptions on demand instead of
  bloating the system prompt; treat AGENTS.md/CLAUDE.md as a table of contents (~100 lines),
  details in on-demand docs.
- **Encode constraints, don't document them** — linters/types/CI enforce architecture;
  documentation is invisible to a busy agent. "Enforce invariants, don't micromanage
  implementations."
- The quotable thesis: **"a decent model with a great harness beats a great model with a bad
  harness"** — and harness engineering means every observed failure becomes a permanent
  engineering fix, not a prompt tweak.

## 5. Long-horizon reliability (loop engineering)

Long tasks outlive context windows. The pattern: externalize state to disk (task file,
progress log), make the working loop **reentrant** so a fresh context can resume from the
breakpoint, verify after every step. Rule of thumb from production notes: any task longer
than ~30 minutes must have crash recovery — it's a requirement, not an option. **Subagents
act as a context firewall**: discrete noisy work (search, debugging) runs in isolated
contexts that return only summaries, keeping the orchestrator thread coherent.

## 6. Memory

Taxonomy interviewers expect: **working** (in-context), **episodic** (past interactions),
**semantic** (facts about the world/user), **procedural** (how-to, skills). Design points:
MEMORY.md-style curated files + on-demand retrieval beats stuffing history; memory writes
should be reviewable/rollbackable; long-term store lives outside the context window
(DB/vector store) with session-start loading. Caution finding worth citing: added memory can
make chatbots *sound* smarter but reduce trust when it surfaces stale or misapplied facts —
retrieval precision matters more than recall here.

## 7. Multi-agent systems — protocols before parallelism

Natural language coordinates *within* a task; **protocols coordinate between tasks**. Without
them you get: forgotten commitments, double ownership, dependency violations, silently
dropped failures, duplicate execution on retries, unrecoverable crashes. Three foundations
to name: **communication protocol** (message semantics, acks, failure reporting), **task
graph** (what exists, who owns it, dependencies), **isolation boundary** (which files/tools/
resources each agent may touch). Give each subagent minimum context, authority, and budget.
Known failure mode: **hallucinations amplify across agents** — mitigate with
cross-validation between agents. Decomposition patterns: functional (by expertise) vs
spatial (by data/region partition).

Protocol standards: **MCP** (model↔tool: resources, tools, prompts; runtime discovery) and
**A2A** (agent↔agent: agent cards, task lifecycle states, `input-required` maps to
interrupt/HITL).

## 8. Frameworks — have a selection story

- **Direct API + simple loops** first; frameworks obscure prompts and complicate debugging.
- **LangGraph** when you need explicit state machines: typed state, checkpointers (memory ≠
  prod: align checkpointer with runtime), conditional edges, streaming, time-travel.
- **Deep Agents** (LangChain) when you want the batteries-included harness: planning tool,
  virtual filesystem, subagent delegation, HITL middleware.
- **Google ADK** for GCP-native: workflow agents (Sequential/Parallel/Loop), SKILL.md
  progressive disclosure, Agent Engine/Cloud Run deployment.
- Vercel AI SDK for TS/serverless products (stateless functions + DB-backed session state).

## 9. Case study to cite: PRINCE (Bayer × Thoughtworks)

Public, quotable production example (Fowler blog, 2026): pharma research assistant evolving
**Search → Ask → Do**. Architecture: LangGraph orchestration; clarify-intent step as
fail-fast ambiguity gate; Think & Plan node doing *process* reflection (trajectory, not
data); Researcher (RAG + Text-to-SQL over OpenSearch/Athena); Reflection agent validating
data sufficiency; Writer agent; Postgres checkpointer state; LLM fallback chains with
node-level *and* call-level retries, error context fed back so the agent replans; Langfuse
traces + RAGAS evals (daily on live traffic). Design principle to quote: **context
discipline** — each stage gets stage-specific context; big windows don't remove the need
for selection.

## 10. Question bank (answer sketches)

- *"Design an agent to automate X."* — clarify stakes/reversibility first → simplest pattern
  that works → tools with ACI care → verification signal → HITL for irreversible actions →
  eval plan. Name the harness parts explicitly.
- *"Your agent works in demos, fails in production — why?"* — non-determinism unmeasured (no
  Pass^k), context rot on long tasks, tool descriptions ambiguous under real inputs, no
  recovery path, eval set unrepresentative. Fix measurement first (see OpenClaw tip: if the
  eval system is broken, fix it before touching the agent).
- *"When do you add a second agent?"* — only with a task graph + isolation boundary + protocol;
  single agent with good tools beats premature multi-agent.
- *"How do you keep an agent working for 3 hours?"* — state externalization, reentrant loop,
  plan file, per-step verification, subagent context firewall, compaction.
- *"Pass@k vs Pass^k?"* — Pass@k = capability ceiling (any of k succeeded); Pass^k =
  deployment reliability (all k succeeded). Production cares about Pass^k.

## Sources

- notes: [agent-harness.md](../../../ai-engineering/03-harness/agent-harness.md) (harness anatomy + OpenClaw 10 principles), [reliable-agents.md](../../../ai-engineering/03-harness/reliable-agents.md) (PRINCE case study), [agents-design.md](../../../ai-engineering/03-harness/agents-design.md) (protocol-driven multi-agent, decomposition), [loop-engineering.md](../../../ai-engineering/04-loop/loop-engineering.md), [deep-agents.md](../../../ai-engineering/04-loop/deep-agents.md), [memory.md](../../../ai-engineering/05-graph/memory.md), [agents-google-adk.md](../../../generative-ai/03-agentic-foundations/agents-google-adk.md)
- librarian wiki: Agentic Workflow Patterns · ACI (Agent-Computer Interface) · ReAct Pattern · Plan and Execute Pattern · Multi-Agent Orchestration Patterns · Agent Memory Types · Deep Agents Framework · Framework Selection (LangChain vs LangGraph vs Deep Agents) · ADK Workflow Agents · MCP Protocol · A2A Agent Protocol · HITL and Interrupt Patterns
- readings: `ai-engineering/readings/ai_engineering/` (building agents, multi-agent context, mcp), `ai-engineering/readings/general/` (ReAct, generative agents, Gorilla, ToolLLM)
- external: martinfowler.com/articles/reliable-llm-bayer.html · anthropic.com/engineering/building-effective-agents · openai.com/index/harness-engineering
