# Loop contract — <loop name>

> Fill this in before the loop's first pass. If a section is blank, the loop isn't ready.
> Rationale for each section: [notes/09 design checklist](../notes/09-failure-modes-and-guardrails.md#design-checklist).

## Worth a loop?

- Repeats how often: <daily / per PR / per event / until one goal is met>
- Why a single prompt isn't enough: <...>

## Goal

<One small, finishable outcome. "All tests in tests/auth/ pass", not "improve auth".>

Has an end? Yes → run-until-done (`/goal`). No, it's ongoing watching → timer (`/loop`).

## Acceptance criteria

Each one checkable by a command:

- [ ] `<test command>` passes
- [ ] `<lint / typecheck command>` clean
- [ ] `<coverage or other metric>` ≥ <threshold>

## Scorekeeper

- Command: `<e.g. pytest tests/auth -q>`
- Score: <what number or pass/fail it returns>
- Held-out check (final gate only): `<command>`
- Checker (if model-graded): <agent/model, different from the maker; rubric path>

## Write boundary

| May edit | Must not edit |
|---|---|
| `<src/auth/**>` | `<tests/**, scoring scripts, this file>` |

Enforced by: <hook / permissions / separate repo — not just this sentence>

## Trigger

<manual / `/goal` / `/loop 30m` / `/schedule` cron / event: ...>

## Stop rules

| Exit | Threshold | On trip |
|---|---|---|
| Success | scorekeeper green + held-out green | save, report |
| Iteration cap | <N> passes | escalate |
| Budget cap | <$ / tokens / minutes> | escalate, state saved |
| Stall | score unchanged for <K> passes | change strategy once, then escalate |

## Ratchet

- [ ] A lower score rolls the change back automatically
- [ ] Each green pass is committed before the next starts
- [ ] Breaks are fixed before new work

## Human gates

Pause and ask before: <irreversible actions, dependency changes, anything touching prod, judgment calls>

## How to work each pass

1. Read this contract and [loop-state.md](loop-state.md).
2. Do the one item in "What is next". One small change.
3. Run the scorekeeper. Up: commit. Down: revert.
4. If stuck on the same error for 2 passes, change approach or simplify.
5. Update loop-state.md before exiting.

Maker and checker prompts: [maker-prompt.md](maker-prompt.md), [checker-prompt.md](checker-prompt.md).
