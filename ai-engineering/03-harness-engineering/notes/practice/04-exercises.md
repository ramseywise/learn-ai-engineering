---
origin: web-authored
sources:
  - https://github.com/walkinglabs/learn-harness-engineering
confidence: medium
cleaned: 2026-10-28
---
# P4 — Exercises

> Every claim in this module can be tested on a repo you own. Change one harness variable, run the same task, and compare.

Six labs that build a harness step by step, plus short drills per topic. They adapt the *learn-harness-engineering* projects (originally an Electron knowledge-base app with starter/solution folders) for **any repo you have.** Pick a codebase with real but modest work left, and keep it the same across every lab so the harness is the only thing that changes.

---

## Ground rules

- **One agent, one model, all labs.** Claude Code or Codex. Don't switch partway through.
- **Branch per run.** `lab1-baseline`, `lab1-harness` and so on, so runs can be diffed.
- **Same task across a comparison.** Change the harness, not the work.
- **Record each run:** wall time, your interventions, retries, features claimed done, features *actually* passing on independent check, and premature "done" claims.
- **Attribute every failure** to a subsystem (instructions, tools, environment, state, feedback; [note 02](../02-harness-anatomy.md#the-five-subsystems)). An unattributed failure teaches you nothing.

A run log, one per run:

```markdown
| Run | Harness | Time | Interventions | Claimed done | Actually passing | Premature "done" | Failure → subsystem |
```

---

## Lab 1 — Prompt only vs. minimal harness

**Mechanism:** `AGENTS.md` + `init.sh` + `feature_list.json`. Notes: [01](../01-what-a-harness-is.md), [P1](01-repo-as-system-of-record.md), [P3](03-scope-and-done.md).

1. Pick 3–4 small concrete features and write them as **one vague sentence** (the original used "Build an app that can show documents and answer questions").
2. **Run A:** give the agent only that sentence. No harness files.
3. Reset the branch. Add [AGENTS.md](../../templates/AGENTS.md), [init.sh](../../templates/init.sh) and a [feature_list.json](../../templates/feature_list.json) that turns the sentence into those 3–4 features, each with verification steps.
4. **Run B:** same agent, same sentence, plus "read AGENTS.md first".
5. Compare: completion, retries, and how often it claimed "done" too early.

**Learning outcome:** the measured difference, not a finished app.

---

## Lab 2 — Agent-readable workspace across two sessions

**Mechanism:** system-of-record docs + session handoff. Notes: [P1](01-repo-as-system-of-record.md), [P2](02-session-lifecycle.md).

1. Choose a feature slice that takes **two sessions** (e.g. import → detail view → persist across restart).
2. **Run A:** thin docs and no handoff. End session 1 mid-slice and start session 2 cold.
3. **Run B:** expand `ARCHITECTURE.md` and a product doc, and end session 1 with a [session-handoff.md](../../templates/session-handoff.md).
4. Measure **rebuild cost**, the time from session-2 start to the first useful edit, and count rediscovery actions (files read just to orient).

---

## Lab 3 — Multi-session continuity with WIP=1

**Mechanism:** progress log + handoff + one feature at a time + evidence-gated `passing`. Notes: [P2](02-session-lifecycle.md), [P3](03-scope-and-done.md).

1. Pick **four related features** spanning 3+ sessions.
2. **Run A:** a feature list exists but there's no WIP rule and no restart artifacts.
3. **Run B:** WIP=1 in `AGENTS.md`, a [progress.md](../../templates/progress.md), a handoff, a [clean-state checklist](../../templates/clean-state-checklist.md), and `passing` only with recorded evidence.
4. Compare drift (features started vs. finished per session), state loss after restart, and whether each `passing` has evidence behind it.

---

## Lab 4 — Runtime feedback and boundaries

**Mechanism:** structured logs + architecture check + a seeded bug. Notes: [P1](01-repo-as-system-of-record.md#make-the-map-enforceable), [05](../05-verification-loops.md), [08](../08-maturity-and-failure-modes.md#runtime-vs-process-observability).

1. **Seed a runtime bug** that only shows up when the app runs, e.g. a failure on large inputs.
2. **Run A:** weak diagnostics and no boundary check. Ask the agent to find and fix it.
3. **Run B:** add structured logs on startup and the critical path, an `ARCHITECTURE.md` with layer rules, and **one** script that enforces the costliest boundary with a WHAT/WHY/FIX error message.
4. Compare time to root cause, and whether the fix stayed in the owning layer.

---

## Lab 5 — Role separation

**Mechanism:** generator → +evaluator → +planner. Notes: [05](../05-verification-loops.md#separating-generation-from-evaluation), [07](../07-orchestration.md).

1. Pick **one substantive feature** (e.g. multi-turn history, a filter UI) and keep it fixed.
2. **Run A:** one agent plans, builds and self-reviews.
3. **Run B:** generator + separate evaluator scoring against the [evaluator rubric](../../templates/evaluator-rubric.md), with at least one revision round.
4. **Run C:** planner writes a [sprint contract](../05-verification-loops.md#sprint-contracts), then the generator builds and the evaluator grades against it.
5. Compare rubric scores, defects found, and cost. (In the original runs the scores rose from 1.6 to 3.3 to 4.9 out of 5. Check whether your repo shows the same shape, and at what cost.)

---

## Lab 6 — Capstone: full harness, cleanup, ablation

**Mechanism:** everything above + [quality document](../../templates/quality-document.md) + ablation. Notes: [08](../08-maturity-and-failure-modes.md#iterative-simplification), [P2](02-session-lifecycle.md#entropy-management-two-cleanup-modes).

1. Fix a multi-feature task set covering your repo's core slice.
2. **Baseline:** weak harness (basic `AGENTS.md` only).
3. **Strong:** your full harness from labs 1–5.
4. **Cleanup pass:** run a periodic cleanup, update the quality document, re-run.
5. **Ablation:** remove **one** component at a time (instructions, feature list, handoff, init.sh, evaluator, logs) and re-run. Rank components by how much each removal hurts.

**Learning outcome:** which parts of *your* harness are load-bearing, and which you can delete.

---

## Lab 7 — From harness to loop

This lab belongs to the loop layer: turn the harness you built here into a goal loop, then a timer loop, then a maker/checker loop. See [04-loop-engineering practice](../../../04-loop-engineering/practice/01-exercises.md).

---

## Drills

Short exercises, each tied to one note.

**Why agents fail** ([01](../01-what-a-harness-is.md))
- *Verification gap.* For 5 tasks, record whether the agent claims done, then check independently. The share of false "done" claims is your verification gap. Which check would have caught each one?
- *Diagnostic loop.* Take a task that keeps failing. Run, attribute the failure to one subsystem, fix that subsystem, and re-run. Do 3–5 rounds and log what changed.

**Anatomy** ([02](../02-harness-anatomy.md))
- *Five-subsystem audit.* Score instructions, tools, environment, state and feedback from 1 to 5. Spend 30 minutes on the lowest, then re-run a task.
- *Execution vs. evaluation gap.* Find a spot where the agent "wants to but can't". Is it missing *how to act* (execution) or *how to tell if it worked* (evaluation)? Fix whichever one it is.

**Repo as system of record** ([P1](01-repo-as-system-of-record.md))
- *Fresh session test.* With no verbal context, ask the five questions. Fix the repo until all five are answerable.
- *Visibility gap.* List the decisions and constraints that matter, mark each in-repo or not, and get the gap under 10%.
- *Entry-file SNR.* For 5 task types, mark each `AGENTS.md` rule relevant or noise. Move rules that are noise for most tasks into topic docs.
- *Lost in the middle.* Put one critical rule at the top, middle and bottom of a long instruction file, with ≥5 runs each. Compare compliance.

**Session lifecycle** ([P2](02-session-lifecycle.md))
- *Handoff template.* Use four fields: commit, test status, blockers, next actions. Restore a fresh session from only that, log the ambiguities, and iterate.
- *Initialization.* Write the startup-readiness checklist, have a fresh session execute it, and treat each failure as a missing clause.
- *Exit checklist.* Apply the five clean-state conditions across 5 sessions and count violations per condition.

**Scope and done** ([P3](03-scope-and-done.md))
- *Atomize.* Break "implement user management" into ≥5 units, each with behavior, a verification command and dependencies.
- *Loose vs. strict.* For 3 features, write a loose check and a strict check, and compare false positives.
- *Single source audit.* Find scope hiding in TODOs, chat or side docs, and move it into the feature list or delete it.

**Verification** ([05](../05-verification-loops.md))
- *Termination check.* For a task touching a migration and an API, define static, test and runtime signals with pass/fail criteria. Run it and log which hidden issues it catches.
- *Layered defense.* Run the same tasks with static analysis only, then + unit tests, then the full three layers. Compare premature "done" claims.
- *Promote a review comment.* Take a recurring review comment, turn it into a check with an agent-oriented message, and compare how often it recurs before and after.

**Observability** ([08](../08-maturity-and-failure-modes.md#runtime-vs-process-observability))
- *Gap audit.* List system states your current signals can't tell apart, and add the signal that separates them.
- *Session trace.* Record every step of one task as a trace. Find the decisions that were made without enough signal.

---

→ Next layer: [04-loop-engineering/](../../../04-loop-engineering/README.md) — the loops this harness implements.
