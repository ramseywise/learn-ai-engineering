---
origin: web-authored
sources:
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
  - https://notes.kodekloud.com/docs/Loop-Engineering/Components/Memory/page.md
  - https://medium.com/@adnanmasood/loop-engineering-a-guide-for-engineers-and-practitioners-893bb65ea943
  - https://ghuntley.com/ralph/
  - https://www.aibuilderclub.com/blog/loop-engineering-anthropic-playbook
confidence: high
cleaned: 2026-10-28
---
# 5 — Long-Running Loops

> Context is a budget, not a bucket. A loop that runs for hours must forget on purpose and remember on disk.

---

## The problem

Every pass adds tool output, errors and reasoning to the transcript. Left alone, the loop hits one of three walls:

1. **Context rot.** Working memory degrades as the transcript grows; the agent loses the thread.
2. **Context anxiety.** Near the limit, models wrap up early and declare done ([harness note 06](../../03-harness-engineering/notes/06-long-horizon-execution.md#the-problem)).
3. **Session end.** The process stops, and the next one starts blank.

All three have the same fix: **progress lives in files, not in the context window.**

---

## Context is a budget

Anthropic's *Effective Context Engineering* treats context as a finite resource with diminishing returns: every token you add competes for the model's attention. The loop move:

> **Feed each pass the smallest set of high-signal tokens the next step needs.**

In practice:

- **Just-in-time retrieval.** Keep paths and IDs in context; load the file when the step needs it, not before.
- **Compact inside the loop**, not after it. Each pass ends by distilling what it learned and dropping raw output that has been acted on (the `compact context` line in the [skeleton](02-loop-shapes.md#the-canonical-skeleton)).
- **Offload big outputs.** Keep the head and tail of a long log in context and write the rest to a file.
- **Push heavy reads into sub-agents** so only their summaries come back ([note 04](04-building-blocks.md#sub-agents-separation-of-concerns)).

Depth: [02-context-engineering/notes/03 budgeting](../../02-context-engineering/notes/03-budgeting-the-window.md), [05 compaction](../../02-context-engineering/notes/05-compression-compaction.md).

---

## Memory: three tiers, five fields

Memory is the set of notes the loop reads at the start of every session so it can resume without redoing work or repeating mistakes. Keep it **small**. A few precise notes beat a transcript.

**Three tiers** (KodeKloud), closest first:

| Tier | Holds | Read |
|---|---|---|
| **Now** | Current goal and current task | Every pass |
| **Recent** | The last few steps and their outcomes | Every pass |
| **Archive** | Full history | Only when needed |

**Five fields** for the "now" and "recent" tiers:

| Field | Purpose | Example |
|---|---|---|
| **Goal** | What done looks like, so the aim doesn't drift | `All tests in tests/auth/ pass` |
| **Last score** | Latest scorekeeper result | `41/47 passing` |
| **What was tried** | Recent attempts, *especially failures* | `Mocking the clock in test_expiry: no change` |
| **What is next** | The very next step, so the next pass starts fast | `Check token refresh path in auth/session.py` |
| **Waiting for a human** | Items that need a decision or sign-off | `Approve dropping the legacy cookie` |

A ready-made file with these fields: [templates/loop-state.md](../templates/loop-state.md).

"What was tried" earns its place. Without it, a fresh pass reruns the attempt that failed an hour ago.

### Context drift

Memory must stay current. If the code, schema or goal changed and the notes didn't, the loop acts on a stale picture with full confidence. That failure is **context drift**. Fix it by updating or invalidating the affected notes whenever the world changes, and by recording *when* each note was written so stale ones are visible.

---

## The Ralph loop

Geoffrey Huntley's original, in its smallest form:

```bash
while :; do cat PROMPT.md | claude -p; done
```

Each run starts with a fresh context. The prompt tells the agent to read the plan and progress files, do the next item, update the files and exit. The filesystem carries everything between runs. That one-liner is the whole idea of re-entrant loops.

What it lacks: a stop condition, a budget and a scorekeeper. A production version (the [templates/ralph.sh](../templates/ralph.sh) template) adds:

- an **iteration cap** and a **wall-clock or cost cap**
- a **done check** that runs the scorekeeper, not the agent's own claim
- a **stall check**: stop if the score hasn't moved in N passes
- a log line per pass

Harnesses now ship this pattern: hooks catch the agent's attempt to finish and re-inject the prompt into a fresh context ([harness note 06](../../03-harness-engineering/notes/06-long-horizon-execution.md#ralph-loops)), and `/goal` does it as a built-in ([note 06](06-triggers-and-schedules.md#claude-code)).

---

## Initializer and worker

Anthropic's *Effective Harnesses for Long-Running Agents* splits long work into two roles:

- An **initializer** runs once: turns the task into files (a feature list, a progress log, scaffolding, an `init` script) and commits them.
- A **worker** runs every session: reads the progress log and git history, picks **one** unfinished item, implements and tests it, commits, updates the log, and exits cleanly.

Two rules from the essay that apply to any long loop:

- **One item per session.** Trying to do everything at once is how a session runs out of context halfway through a change and leaves the repo broken.
- **Leave the repo clean.** Every session ends in a state the next one can start from: committed, tests run, progress noted.

---

## Compaction vs reset

| | Compaction | Reset |
|---|---|---|
| How | Summarize the transcript in place | Clear the window; hand off through files |
| Good for | One long session | Multi-session or multi-day work |
| Risk | Summary-of-a-summary drift | Anything not written down is lost |

Loops lean toward **reset**, because the Ralph and initializer/worker patterns already keep state on disk. Details and the model-dependence of this choice: [harness note 06](../../03-harness-engineering/notes/06-long-horizon-execution.md#compaction-vs-context-reset).

---

## Working reference

`~/.claude/refs/agent-context.md` — compaction triggers and what must survive them; `~/.claude/refs/agent-memory.md` — durable state and memory hygiene.

---

→ Next: [06-triggers-and-schedules.md](06-triggers-and-schedules.md) — what starts a loop when you don't.
