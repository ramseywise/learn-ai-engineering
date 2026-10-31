---
origin: web-authored
sources:
  - https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
  - https://www.anthropic.com/engineering/harness-design-long-running-apps
  - https://openai.com/index/harness-engineering/
  - https://github.com/walkinglabs/learn-harness-engineering
confidence: medium
cleaned: 2026-10-28
---
# P2 — The Session Lifecycle

> Treat the agent like an engineer whose short-term memory is wiped every shift. It clocks in from the repo and clocks out into the repo.

[Note 06](../06-long-horizon-execution.md) covers *why* long work has to be re-entrant: coherence decay, context anxiety, compaction vs. reset. This note is the routine that makes it so, covering how a session starts, how it ends, and the one-time setup that makes both cheap. Adapted from *learn-harness-engineering* lectures 05, 06 and 12 and its reference playbooks.

---

## What breaks at a session boundary

Each boundary loses something, and the losses compound:

- **The *why* goes first.** Code survives and reasoning doesn't. Compaction keeps *what* was done and drops *why option B beat option A*. The next session may "optimize away" a deliberate decision.
- **Duplicate and half-redone work.** Without a record of what's finished, the agent redoes it, or half-redoes it and collides with the existing version.
- **Verification amnesia.** Which tests passed, which failed and why all have to be rediscovered from scratch.
- **Drift.** The gap between the agent's picture and the real repo grows a little each session until the result no longer matches the original intent.

Two metrics name the problem:

| Metric | What it measures |
|---|---|
| **Rebuild cost** | Time for a fresh session to reach a state where it can act. A good harness gets this to a few minutes. |
| **Drift** | Distance between the agent's understanding and the repo's actual state. Unmanaged, it compounds per session. |

---

## Phase 0: initialization is its own session

Initialization and implementation optimize different things. Implementation maximizes *verified features*. Initialization maximizes *the reliability of every later session*. Combine them and the agent drifts toward visible output (feature code) and short-changes the infrastructure, whose payoff only shows up later. The usual results are a test framework configured but never run, and a choice of Vitest that the next session doesn't know about, so it adds Jest.

Anthropic's long-running-agent harness makes this a separate role: an **initializer agent** runs once, then a **coding agent** runs every session after. The initializer writes **no feature code.** It leaves behind:

1. A **root instruction file** (`AGENTS.md`), short and routing ([P1](01-repo-as-system-of-record.md#the-entry-file-is-a-router))
2. A **standard startup path**, `init.sh`: install, verify, print how to start
3. **One passing example test**, which proves the test harness itself works
4. A **machine-readable feature list** with every feature `not_started` ([P3](03-scope-and-done.md))
5. A **progress log** recording the starting state
6. A **clean baseline commit**

The startup path is a dozen lines of shell. The pillar's [init.sh](../../templates/init.sh) installs, runs the baseline verification, and prints the start command rather than running it, so a session can always boot and check before doing anything else:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

INSTALL_CMD=(npm install)     # replace per repo
VERIFY_CMD=(npm test)
START_CMD=(npm run dev)

"${INSTALL_CMD[@]}"
"${VERIFY_CMD[@]}"            # fails loudly if the baseline is broken
printf 'start with:'; printf ' %q' "${START_CMD[@]}"; echo
[ "${RUN_START_COMMAND:-0}" = "1" ] && exec "${START_CMD[@]}"
```

Start from a project template rather than an empty directory where possible, so only project-specific setup remains.

**Startup readiness**, the four conditions initialization must satisfy:

- [ ] **Can start.** `./init.sh` succeeds from a clean checkout.
- [ ] **Can test.** At least one test passes.
- [ ] **Can see progress.** A progress log and feature list exist.
- [ ] **Can pick up next steps.** A fresh session can name the next feature without asking.

The check is the [fresh session test](01-repo-as-system-of-record.md#the-fresh-session-test). A session with no chat history must be able to say what the repo does, how to start it, how to verify it, what is unfinished, and what's next.

---

## Clock in: the fixed startup sequence

Every session after initialization starts the same way:

```
1. pwd                          → confirm you're in the right repo
2. read progress.md             → recover durable state
3. read feature_list.json       → what's done, what's next
4. git log --oneline -5         → what changed most recently
5. ./init.sh                    → standardized startup, not memory
6. run the baseline smoke / e2e → is the starting state already broken?
7. if broken → fix that first   → never stack new work on a red baseline
8. pick ONE unfinished feature  → highest priority
9. work only on it until verified or explicitly blocked
```

The order is deliberate. State is recovered *before* any edits, and the baseline is verified *before* new work can hide an existing break. Step 7 is the one most often skipped, and skipping it is how a session ends up blamed for a failure it inherited.

---

## The state files

| File | Holds | Without it |
|---|---|---|
| **Progress log** | Current verified state, done / in progress / next, known issues | Every session re-diagnoses |
| **Decision log** | What was decided, why, rejected alternatives, constraints | Decisions get silently reversed |
| **Feature list** | Per-feature status and evidence ([P3](03-scope-and-done.md)) | Scope sprawl, false "done" |
| **Session handoff** | Compact "verified now / broken / next best step" for big sessions | Next session can't tell verified from assumed |
| **Git commits** | Exact repo state per atomic unit, message says *why* | No checkpoint to resume or roll back to |

A decision-log entry needs only four lines:

```markdown
## 2026-01-15: Redis for user-preference cache
- Why: read on every API call, small payload
- Rejected: Postgres materialized view (write churn makes upkeep costly)
- Constraint: TTL 5 min, invalidate on write
```

The decision log is the one people drop, and it's the one that holds the *why* that compaction loses.

Templates: [progress.md](../../templates/progress.md), [session-handoff.md](../../templates/session-handoff.md).

---

## When to hand off

Short tasks fit in one session. Long tasks need artifacts. A workable trigger: **once a task looks set to use more than ~60% of the window, start writing the handoff**, while there's still room to write it well and before context anxiety starts ending the work early.

Whether to *compact* or *reset* at that point depends on the model. Anthropic found resets necessary on Sonnet 4.5 and largely unnecessary on later models. Details in [note 06](../06-long-horizon-execution.md#compaction-vs-context-reset). Either way, the handoff file is what the next window reads.

---

## Clock out: clean state is part of done

Session completion = **the task passes verification AND the clean-state check passes.** A session with either missing isn't finished.

**The five clean-state conditions:**

1. **Build passes**
2. **All tests pass**, including tests that existed before this session
3. **Progress recorded** in the log and feature list, machine-readable
4. **No stale artifacts**: debug logs, temp files, commented-out code, stray `console.log`/`print`, unlabeled TODOs
5. **Standard startup path works**, so the next session can run `./init.sh` with no manual repair

```
## Session exit checklist          (lives in AGENTS.md)
- [ ] build passes
- [ ] all tests pass
- [ ] feature_list.json + progress.md updated
- [ ] no debug code / temp files left
- [ ] ./init.sh still works from clean
- [ ] safe work committed with a why-message
```

Treat a session like a transaction: commit a clean state, or roll back to the last one. Leaving a partial mess is not an allowed outcome.

**"Clean up later" means never.** The next session has its own goal. It builds on top of the mess instead of cleaning it, which adds more mess. And because **agents copy patterns already in the repo**, including bad ones (OpenAI's observation from their Codex work), a little slop becomes the template for more.

Template: [clean-state-checklist.md](../../templates/clean-state-checklist.md).

---

## Entropy management: two cleanup modes

Per-session cleanup isn't enough on its own. Combine two modes:

| Mode | When | Covers | Analogy |
|---|---|---|---|
| **Immediate** | End of every session | Temp artifacts, feature state, build/tests green | Reference counting: free as soon as you're done |
| **Periodic** | Weekly, or a background agent | Structural drift, quality-doc update, benchmark re-run, targeted refactor PRs | Tracing GC: sweep the whole heap on a cadence |

Make cleanup **idempotent**, so running it twice is safe (`rm -f`, restore to a known state, re-run tests). Retries are normal, and cleanup can't be something that breaks when it runs again.

OpenAI's version of the periodic mode: they started by spending a fifth of every Friday hand-cleaning "AI slop". That didn't scale, so they moved to:

1. **Golden rules encoded in the repo**, concrete and mechanically checkable (e.g. "use the shared utility, don't hand-roll helpers"; "validate boundaries, don't guess data shapes")
2. **Background agents** that scan for deviations, update quality scores and open small refactor PRs
3. **Human taste captured once and enforced continuously**: review comments become docs, and docs that aren't enough become checks ([note 05](../05-verification-loops.md#promote-review-feedback-into-checks))

The **quality document** that this loop updates is covered in [note 08](../08-maturity-and-failure-modes.md#the-quality-document).

---

## Diagnosing which artifact is missing

When a long-running harness misbehaves, add the **smallest artifact that addresses the observed failure**, not another paragraph in the root file:

| Failure | Looks like | Fix first with |
|---|---|---|
| Cold-start confusion | New session spends its time rediscovering setup and status | Progress log, repo as system of record |
| Fragile startup | Every session re-learns how to boot | `init.sh` |
| Scope sprawl | Several features started, none finished | Feature list + WIP=1 ([P3](03-scope-and-done.md)) |
| Premature completion | "Done" after edits, before runnable proof | Evidence-gated feature state, clean-state checklist |
| Weak handoff | Next session can't tell verified from broken | Session handoff |
| Subjective review | Quality depends on reviewer taste | Evaluator rubric ([note 05](../05-verification-loops.md#grading-criteria-beat-vibes)) |

---

## Working reference

`~/.claude/refs/agent-memory.md` — durable state and memory hygiene.
`~/.claude/refs/agent-context.md` — compaction triggers and what must survive them.
Templates: [init.sh](../../templates/init.sh), [progress.md](../../templates/progress.md), [session-handoff.md](../../templates/session-handoff.md), [clean-state-checklist.md](../../templates/clean-state-checklist.md).

---

→ Next: [03-scope-and-done.md](03-scope-and-done.md) — one feature at a time, and what "done" means.
