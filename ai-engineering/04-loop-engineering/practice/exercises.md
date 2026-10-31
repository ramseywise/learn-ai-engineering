---
origin: web-authored
sources:
  - https://github.com/walkinglabs/learn-harness-engineering
  - https://notes.kodekloud.com/docs/Loop-Engineering/Tie-It-All-Together/Designing-Your-Own-Loop/page.md
  - https://github.com/karpathy/autoresearch
confidence: medium
cleaned: 2026-10-28
---
# P1 — Exercises

> Five labs that take you from inside the loop to outside it. Each one moves one rung up the autonomy ladder, and each is earned by the one before.

These labs continue the [harness labs](../../03-harness-engineering/notes/practice/04-exercises.md). Lab 7 there points here. Labs 1–3 adapt project 07 of *learn-harness-engineering* (goal loop → timer loop → maker/checker loop) for **any repo you have**. Labs 4–5 add a guarded Ralph loop and an evolve loop.

---

## Ground rules

- **Start from a working harness.** `AGENTS.md`, an `init.sh` that sets up the environment, and a test command that runs clean. If you did the harness labs, start from that commit.
- **One repo, one agent, one model** for all labs, so the loop design is the only thing that changes.
- **Branch per lab**: `loop-goal`, `loop-timer`, `loop-maker-checker`, `loop-ralph`, `loop-evolve`.
- **Contract before the first pass.** Fill in [loop-contract.md](../templates/loop-contract.md). A blank section means the loop isn't ready ([note 01](../notes/01-what-a-loop-is.md#two-things-before-anything-runs)).
- **Green first.** Get one saved, green pass before you scale anything ([note 01](../notes/01-what-a-loop-is.md#green-first)).
- **Set a budget cap** on every unattended run. Write down what it was and whether it tripped.

A run log, one row per run:

```markdown
| Lab | Run | Passes | Saved | Rolled back | Interventions (why) | Goal met? | Held-out passed? | Cost | Stop reason |
```

"Stop reason" is one of: success, iteration cap, budget cap, stall, human. A run that stopped on a cap is *not* a success, even if the code looks fine.

---

## Lab 1 — Goal loop: manual vs `/goal`

**Rung:** 1 → 2. **Notes:** [01](../notes/01-what-a-loop-is.md), [03](../notes/03-the-scorekeeper.md), [07](../notes/07-autonomy-ladder.md#2--goal-based-hand-off-the-stop-condition).

1. Pick a medium task with a clear end: "unit tests for every module in `src/parsers/` to 80% coverage", "input validation on every API endpoint."
2. Write the contract: goal, acceptance criteria as commands, write boundary (the tests you'll judge by are **outside** it), stop rules.
3. Hold back one check for the final gate, e.g. a few edge-case tests the agent never sees.
4. **Run A, manual:** you prompt each turn. Record turns, interventions and quality.
5. **Run B, `/goal`:** same contract, run-until-done. Record the same things.
6. Run the held-out check on both.
7. If B was poor, revise the contract and rerun. Keep both versions; the diff is the lesson.

**Learning outcome:** whether your stop condition can be trusted without you. If the held-out check fails while the visible ones pass, the scorekeeper is gameable.

---

## Lab 2 — Timer loop: monitoring as a heartbeat

**Rung:** 3. **Notes:** [06](../notes/06-triggers-and-schedules.md).

1. Pick something you check by hand that **has no end**: test suite health, stale TODOs, dependency advisories, style drift since the last commit.
2. Apply the test from [note 06](../notes/06-triggers-and-schedules.md#claude-code): *does it have an end?* If yes, it belongs in Lab 1, not here.
3. Write the per-run prompt: what to check, what to fix on its own, what to escalate.
4. Add a **cheap no-op path**: if nothing changed since the last run, exit before doing real work.
5. Run with `/loop 15m` (or 10–30 min) for at least two hours.
6. Record: issues found, fixed, false positives, made worse, and **your follow-up time**.

**Learning outcome:** whether the automation saves more time than it costs to follow up on. If not, decide whether you picked the wrong task or designed the loop badly.

---

## Lab 3 — Maker/checker: step outside the loop

**Rung:** 2–3, without you in the room. **Notes:** [03](../notes/03-the-scorekeeper.md#maker-and-checker), [04](../notes/04-building-blocks.md), [05](../notes/05-long-running-loops.md).

1. Set up: [maker-prompt.md](../templates/maker-prompt.md), [checker-prompt.md](../templates/checker-prompt.md), [loop-state.md](../templates/loop-state.md). The checker is a separate agent with no maker history, ideally a different model.
2. Write the control logic: who goes first, how the checker's report reaches the maker, when a round ends. Stop on two consecutive PASS verdicts with the scorekeeper green, or at the round cap.
3. Run at least **five rounds** without intervening unless a human gate fires.
4. Log each round in the state file: what the maker did, the checker's verdict and issues, the score, and whether you stepped in and why.
5. Retro:
   - What would have happened if you hadn't intervened?
   - Did the checker miss anything you or the held-out check caught?
   - Did the maker repeat the same mistake? (That's a missing skill or guard; see [note 04](../notes/04-building-blocks.md#add-them-in-order-and-only-when-needed).)
   - Is the quality ceiling set by the maker or the checker?
   - Did the checker ever pass clean work, or did it always find *something*?

**Learning outcome:** where the loop's quality comes from. Usually it's the checker.

---

## Lab 4 — Guarded Ralph loop

**Rung:** 2, re-entrant across context windows. **Notes:** [05](../notes/05-long-running-loops.md#the-ralph-loop), [09](../notes/09-failure-modes-and-guardrails.md#the-two-ratchet-rules).

1. Run the bare one-liner (`while :; do cat PROMPT.md | claude -p; done`) on a throwaway branch for **10 minutes**, then kill it. Note what it did after the work was finished.
2. Run [ralph.sh](../templates/ralph.sh) on the same task with `SCORE_CMD` set to a command that prints one number, plus `MAX_ITERS`, `MAX_MINUTES` and `STALL_LIMIT`.
3. Make `PROMPT.md` read and update `loop-state.md` every pass.
4. Deliberately break one thing mid-run (edit a test so it fails). Check that the loop fixes the break before new work, and that a pass which lowered the score was rolled back.
5. Compare `git log` from both runs.

**Learning outcome:** the ratchet. With guardrails, `git log` is a list of validated improvements. Without them it's a list of whatever happened.

---

## Lab 5 — Evolve loop

**Capability level:** 4, at rung 1 (you approve every diff). **Notes:** [08](../notes/08-self-improving-loops.md#the-evolve-loop).

1. Use the loop from Lab 2 or 3 once it has **5–10 logged runs**.
2. Start a separate evolve session. Inputs: the contract, the state file and logs, and the raw transcripts.
3. Its contract: propose edits to at most one of the four targets (contract, state, trigger, procedure), each tied to evidence in the logs. **"No change needed" is a successful outcome.**
4. Review the diff yourself. Apply it or reject it, and write down why.
5. Run the improved loop for another 5 runs. Did the targeted symptom go away?
6. Repeat once. Are the proposed diffs getting smaller and more boring?

**Learning outcome:** whether your loop's problems are structural (fixable by the evolve loop) or a matter of judgment (yours to fix). If the evolve session always proposes something, its contract doesn't really allow "no change."

---

## Drills

Short checks, one per note:

| Note | Drill |
|---|---|
| [01](../notes/01-what-a-loop-is.md) | Take three recurring tasks. For each, decide: loop, workflow, or one prompt? What's the scorekeeper? |
| [02](../notes/02-loop-shapes.md) | Annotate your Lab 1 contract against the five required parts. Which was weakest? |
| [03](../notes/03-the-scorekeeper.md) | Try to make your own scorekeeper pass without doing the work. Every way you find is a hole to close |
| [04](../notes/04-building-blocks.md) | List the parts your Lab 3 loop uses. For each, name the failure that made you add it |
| [05](../notes/05-long-running-loops.md) | Delete "What was tried" from the state file for one run. Does the loop repeat a failed attempt? |
| [06](../notes/06-triggers-and-schedules.md) | Measure what one no-op run of your timer loop costs. Multiply by runs per month |
| [07](../notes/07-autonomy-ladder.md) | Place each lab on the ladder. Which one would you trust at rung 4, and what evidence says so? |
| [09](../notes/09-failure-modes-and-guardrails.md) | After an hour of any loop, audit the silent costs: how much was "looks fine" vs machine-checked? Can you explain the last change it made? |

---

→ Back to the syllabus: [README](../README.md).
