---
origin: web-authored
sources:
  - https://www.anthropic.com/engineering/harness-design-long-running-apps
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://addyosmani.com/blog/agent-harness-engineering/
  - https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
  - https://docs.langchain.com/oss/python/deepagents/overview
  - https://www.promptingguide.ai/agents/deep-agents
confidence: high
cleaned: 2026-07-29
---
# 6 — Long-Horizon Execution

> Work that outlasts a single context window. The harness's job is to make the loop re-entrant.

---

## The problem

Long-horizon work requires **durable state, planning, observation, and verification to keep working across multiple context windows.** Two distinct degradations show up as sessions extend:

1. **Coherence decay** — models lose the thread as the window fills. See [02-context-engineering/notes/01](../../02-context-engineering/notes/01-why-context-is-finite.md).
2. **Context anxiety** — as the window approaches its limit, models **prematurely wrap up work**, declaring done rather than continuing. This one surprises people: the agent doesn't fail loudly, it *finishes early and confidently*.

Context anxiety is a harness problem with a harness fix. The agent stops because it perceives scarcity; give it a mechanism to continue and the perception goes away.

---

## State externalization

The foundational technique:

> **Progress lives in files, not in the context window.**

Once state is external, the loop becomes **re-entrant** — any fresh context can pick up where the last left off by reading the files. Context windows become disposable.

The canonical pattern:

- An **initializer agent** turns the task into filesystem state (plan, checklist, scaffolding).
- A **worker agent** runs a re-entrant loop: read state → do the next thing → write state.
- **Progress passes via files**, independent of any context window.

This is why the filesystem is *"arguably the most foundational harness primitive"* ([note 02](02-harness-anatomy.md#why-the-filesystem-is-foundational)). Every other long-horizon technique depends on it.

### Shallow vs. deep agents

A **shallow** agent runs a tool-calling loop inside one window and falls apart on long, multi-step work. A **deep** agent adds four things. DAIR (Saravia) names them, and Claude Code, the Claude Agent SDK, LangChain Deep Agents and the deep-research products all converge on them:

| Pillar | What it means | Covered in |
|---|---|---|
| **Explicit planning** | A living to-do list the agent updates and recovers from | [Plans as artifacts](#plans-as-first-class-artifacts) |
| **Orchestrator + subagents** | Specialists with clean contexts; the orchestrator integrates their results | [07](07-orchestration.md#subagents-as-context-firewall) |
| **External memory** | Intermediate work goes to files and stores, not the conversation history | This section, [02-context/06](../../02-context-engineering/notes/06-memory.md) |
| **Verification** | A judge, verifier subagent or human checks output before it's accepted | [05](05-verification-loops.md) |

Deep Agents ships all four as defaults on top of the LangGraph runtime: a `write_todos` tool (statuses `pending`, `in_progress`, `completed`), a virtual filesystem (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`, plus `execute` on sandbox backends), a `task` tool for subagents, automatic summarization and large-result offloading, and `AGENTS.md` memory loaded at startup. The agent loop is the same as anywhere else. The defaults are the harness:

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search, fetch_page],           # your domain tools
    memory=["./AGENTS.md"],               # always loaded, unlike skills
    system_prompt="You are a research analyst.",
)   # write_todos, file tools, task (subagents) and summarization come built in
agent.invoke({"messages": [{"role": "user", "content": "Survey the 2026 agent-eval papers"}]})
```

---

## Plans as first-class artifacts

Planning is the model decomposing a goal into steps. The harness's contribution is making the plan **durable and inspectable**:

- **Ephemeral lightweight plans** for small changes — in-context, discarded after.
- **Execution plans checked into the repository** for complex work, carrying **progress logs and decision logs**.
- Active plans, completed plans, and known tech debt **versioned and co-located**, so agents operate without external context.

Harnesses support this by prompting for a plan file and **injecting reminders about how to use it**. A plan the agent forgets to update is a plan that doesn't exist — the reminder is the mechanism.

The decision log deserves emphasis: it records *why*, which is exactly what a summary drops and what a resumed session needs most.

The pillar's [progress.md](../templates/progress.md) template keeps the plan's state in a shape the next session can read in one pass. The first block is the part every session reads. The session log below it is append-only:

```markdown
## Current Verified State
- Standard startup path:      ./init.sh
- Standard verification path: npm test && npm run e2e
- Current highest-priority unfinished feature:
- Current blocker:

### Session 004
- Goal / Completed / Verification run / Evidence captured:
- Commits:
- Known risk or unresolved issue:
- Next best step:
```

---

## Compaction vs. context reset

Two strategies for hitting the limit — genuinely different, not variations:

| | **Compaction** | **Context reset** |
|---|---|---|
| Mechanism | Summarize earlier conversation in place | Clear the window entirely, hand off via structured state |
| Preserves | A lossy trace of everything | Only what the handoff document captures |
| Failure mode | Summary-of-summary drift over many cycles | Anything not written down is gone |
| Best for | Single long session | Multi-day / multi-session work |

Anthropic's finding: **context resets outperformed compaction for Claude Sonnet 4.5**, though newer models (Opus 4.6) mitigate the underlying issue naturally. This is a live example of harness scaffolding whose necessity is model-dependent — precisely the kind of component to re-test on each model upgrade ([note 08](08-maturity-and-failure-modes.md#iterative-simplification)).

Compaction tuning, when you use it: **maximize recall first, then improve precision** by cutting superfluous content. Distill architectural decisions and unresolved issues; discard redundant tool outputs. A reset's handoff document is subject to the same discipline, written deliberately rather than generated.

The [session-handoff.md](../templates/session-handoff.md) template is that document. Its point is to separate *verified* from *assumed*, which a generated summary blurs:

```markdown
## Verified Now        what works · what verification actually ran
## Changed This Session code or behaviour added · harness changes
## Broken Or Unverified known defect · unverified path · risk for next session
## Next Best Step      feature · why next · what counts as passing · what must not change
## Commands            startup · verification · focused debug command
```

When to write it, and the clean-state exit check that goes with it: [practice/02](practice/02-session-lifecycle.md#when-to-hand-off).

Depth on both: [02-context-engineering/notes/05](../../02-context-engineering/notes/05-compression-compaction.md).

---

## Tool-call offloading

Large tool outputs clutter the window without adding signal — a 2,000-line log contributes maybe five useful lines.

The harness keeps the **head and tail tokens** of any output above a threshold, **offloads the full result to the filesystem**, and leaves a path the model can read if it needs more. Bounded cost, no information destroyed.

Pair with **message pruning** — dropping stale tool results from history entirely once they've been acted on — and **cache control headers** so the stable prefix stays cacheable across a long session ([02-context-engineering/notes/02](../../02-context-engineering/notes/02-context-anatomy.md#ordering-stable-before-dynamic)).

---

## Structured note-taking

Agents maintain **persistent memory outside the context window** — markdown notes, memory files, scratchpads — tracking progress across complex tasks without token bloat.

Notably, this behavior is **partly emergent**: Claude playing Pokémon developed its own note structures, maintaining strategic notes and tallies across thousands of steps without being told to. The harness's job is to *provide the medium* and prompt for its use; the model will often organize it sensibly.

Design guidance in [02-context-engineering/notes/06](../../02-context-engineering/notes/06-memory.md): index-plus-detail rather than transcripts, and memory that is editable and auditable.

---

## Ralph loops

A continuation pattern for work that exceeds any single session:

> **Hooks intercept the agent's completion attempt and re-inject the original prompt into a fresh context.**

The agent believes it's starting over; the filesystem holds everything it accomplished. Combined with state externalization, this runs a task across arbitrarily many context windows without human intervention between them.

It also directly defeats **context anxiety** — premature wrap-up becomes harmless, because "done" triggers a fresh window rather than ending the work. The verification gate ([note 05](05-verification-loops.md)) is what decides whether the loop actually terminates.

---

## Autonomous end-to-end execution

What the assembled techniques enable, per OpenAI's account of their internal harness — agents that run the full chain with **no human intervention**:

```
verify current state → reproduce the bug → implement the fix
→ verify in the running application → open a PR
→ handle review feedback → merge
```

Logs, metrics, and traces checked proactively by the agent throughout.

The enabling decision is **minimizing merge resistance**: occasional flaky test failures are handled by *rerunning* rather than *blocking*. In a high-throughput environment, the cost of waiting for manual review exceeds the cost of fixing the occasional small error. Correctness discipline doesn't disappear — it moves into machine-executed constraints ([note 04](04-execution-boundaries.md#encode-constraints-dont-document-them)).

This posture only works if the constraint layer is genuinely strong. Adopting the throughput without the enforcement is how architectures erode quickly.

---

## Decomposition and specialization

For long-running work, **breaking complex tasks into tractable chunks and assigning specialized personas** prevents coherence degradation and improves output.

The caveat from Anthropic's own results: decomposition is **scaffolding around a model limitation.** When Opus 4.6 arrived, sprint decomposition could be **removed entirely** with no quality loss. Build it when the model needs it; re-test when the model changes.

Multi-agent depth: [note 07](07-orchestration.md).

---

## Working reference

`~/.claude/refs/agent-context.md` — compaction triggers (80% limit, phase boundaries, before subagent spawn), what must survive compaction.
`~/.claude/refs/agent-memory.md` — durable state and memory hygiene.

---

→ Next: [07-orchestration.md](07-orchestration.md) — many agents, one harness.
