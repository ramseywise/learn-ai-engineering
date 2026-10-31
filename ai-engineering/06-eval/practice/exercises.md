---
origin: synthesis
sources:
  - https://www.deeplearning.ai/short-courses/evaluating-ai-agents/
  - https://hamel.dev/blog/posts/field-guide/
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
confidence: medium
cleaned: 2026-10-28
---
# P1 — Exercises

> Eight labs that take one system from "vibes" to a gated, calibrated, monitored eval suite. Each lab climbs one rung of the [maturity ladder](../notes/11-production-and-the-maturity-ladder.md#the-ladder), and each needs the one before.

Labs 2–5 use the DeepLearning.AI *Evaluating AI Agents* notebooks ([upstream repo](https://github.com/ginny100/DeepLearning.AI-Evaluating-AI-Agents); data and helpers included) (Arize Phoenix, a sales-data agent). Run those as written first, then **repeat each lab on a system of your own**: a RAG bot, a tool-using agent, a prompt pipeline. The repeat is where the learning is. Labs 1, 6, 7 and 8 are on your system only.

---

## Ground rules

- **One system for all labs**, so the eval is the only thing that changes. Pin the model and prompt version at the start.
- **Branch per lab**: `eval-error-analysis`, `eval-tracing`, `eval-components`, `eval-trajectory`, `eval-experiments`, `eval-judge`, `eval-ci`, `eval-online`.
- **Version the dataset** from Lab 1. Every result records the dataset version ([03](../notes/03-eval-datasets.md#splits-versioning-contamination)).
- **Error bars on every number** from Lab 5 on ([09](../notes/09-reading-results.md)).
- **Set a spend cap** on the API key you use for evals. Record what each lab cost.

A results log, one row per run:

```markdown
| Lab | Run | Dataset ver | n tasks × k trials | Headline (95% CI) | Worst slice | Infra errors | Cost | Decision |
```

---

## Lab 1 — Error analysis: find what's actually broken

**Rung:** 0 → ready for 1. **Notes:** [02](../notes/02-defining-correct.md), [03](../notes/03-eval-datasets.md).

1. Write the success criteria: what the user needs, never-events, unit of success, cost of error ([02](../notes/02-defining-correct.md#success-criteria-before-code)).
2. Collect 50–100 traces: real if you have them, otherwise synthetic along 3 dimensions ([03](../notes/03-eval-datasets.md#synthetic-data-done-right)).
3. **Open code**: one free-text note per trace on the *first* thing that went wrong.
4. **Axial code**: group into 5–15 categories. Write it up with the taxonomy skeleton in [02](../notes/02-defining-correct.md#the-failure-taxonomy).
5. Rank by count × cost. Pick the top three.
6. **Two-expert test**: give 20 outputs and your criteria to someone else. Compare verdicts. Fix the criteria where you disagreed.
7. Turn the 20–50 clearest failures into rows matching the row schema in [03](../notes/03-eval-datasets.md). Include negative and boundary cases.

**Learning outcome:** whether the failures you *expected* are the ones that actually happen. They usually aren't.

---

## Lab 2 — Tracing: make every step visible

**Rung:** prerequisite for 3. **Notes:** [08](../notes/08-tracing-and-observability.md). **Course:** [Lab 2](https://github.com/ginny100/DeepLearning.AI-Evaluating-AI-Agents/blob/master/Lab%202/Lab2.ipynb).

1. Run the course notebook: instrument the agent with Phoenix / OpenInference and inspect the span tree.
2. On your system, instrument model calls, tool calls and retrieval. Use OTel GenAI conventions or OpenInference.
3. Check your traces against the six questions ([08](../notes/08-tracing-and-observability.md#the-questions-a-trace-must-answer)). Fix every gap.
4. Confirm retrieval spans carry passage **text**, not just IDs.
5. Add version attributes (prompt, model, config) on the root span.
6. Re-read five of your Lab 1 failures as traces. Does the trace show *where* each went wrong?

**Learning outcome:** whether you can locate a failure from the trace alone, without re-running anything.

---

## Lab 3 — Component evals: router and skills

**Rung:** 1–2. **Notes:** [04](../notes/04-graders.md), [06](../notes/06-evaluating-agents.md#evaluate-the-components-then-the-whole). **Course:** [Lab 3](https://github.com/ginny100/DeepLearning.AI-Evaluating-AI-Agents/blob/master/Lab%203/Lab3.ipynb).

1. Run the course notebook: the router judge (`TOOL_CALLING_PROMPT_TEMPLATE`), the SQL and analysis judges, and the `exec()` code check.
2. On your system, list every component: router, each tool / skill, final answer.
3. For each, write the **code grader first**. Add a judge only where code can't check it.
4. Implement them against one interface ([04](../notes/04-graders.md#the-grader-interface)), with `requires` and `grader_version`.
5. Give each grader a state: heuristic / experimental. (None are calibrated yet; that's Lab 6.)
6. Run on your Lab 1 rows. Which component fails most?

**Learning outcome:** how many of your "judgment" checks turned out to be code checks.

---

## Lab 4 — Trajectory evals and repeats

**Rung:** 3. **Notes:** [06](../notes/06-evaluating-agents.md). **Course:** [Lab 4](https://github.com/ginny100/DeepLearning.AI-Evaluating-AI-Agents/blob/master/Lab%204/Lab4.ipynb).

1. Run the course notebook: the convergence metric (optimal path ÷ actual path) over repeated runs.
2. On your system, add `expected_tool_calls` and a `tool_match_mode` to 20 rows. Label them from confirmed-good traces.
3. Add one invariant check ("never X before Y") and one end-state check.
4. Run every task **k = 5** times. Report pass@1, pass@5 and pass^5.
5. Plot the per-task pass-rate distribution. How much is flakiness and how much is a capability gap ([06](../notes/06-evaluating-agents.md#non-determinism-run-every-task-k-times))?
6. Log steps, tokens and cost per success.

**Learning outcome:** the gap between pass@1 and pass^5 for your system, and what it means for users who get one try.

---

## Lab 5 — Experiments: compare two versions properly

**Rung:** 3. **Notes:** [09](../notes/09-reading-results.md). **Course:** [Lab 5](https://github.com/ginny100/DeepLearning.AI-Evaluating-AI-Agents/blob/master/Lab%205/Lab5.ipynb).

1. Run the course notebook: a Phoenix experiment with several evaluators, compared across a prompt change.
2. On your system, make one change you believe helps.
3. Run A and B on the **same** tasks, k trials each. Compute the paired Δ with its CI ([09](../notes/09-reading-results.md#compare-on-the-same-tasks-paired-differences)).
4. Break results down by slice, with n per slice.
5. Read every flipped task.
6. Fill in the report template ([09](../notes/09-reading-results.md#report-template)) and make a ship / don't-ship call.
7. Using the sample-size table, work out how many tasks you'd need to detect a difference half the size you saw.

**Learning outcome:** whether your change was real or noise, and how big your suite needs to be to tell.

---

## Lab 6 — Calibrate a judge

**Rung:** 3, trustworthy. **Notes:** [05](../notes/05-llm-as-judge.md).

1. Pick the judge from Lab 3 that matters most.
2. Rewrite it from the judge prompt in [05](../notes/05-llm-as-judge.md#writing-the-judge-prompt): one criterion, binary, critique first, `CANNOT_GRADE`.
3. Label 100–150 outputs yourself (or use real 👍/👎 if you have it). Split train / dev / test.
4. Iterate on dev. Read every disagreement and classify it: prompt problem, criteria problem, or hard case.
5. Measure on test **once**. Write the calibration record described in [05](../notes/05-llm-as-judge.md#calibrate-against-human-labels).
6. Run the bias checks: length correlation, and order swap if it's pairwise.
7. Cross-check against one off-the-shelf metric (RAGAS or a Phoenix template). Do they agree with each other? With your labels?
8. Decide: calibrated (for which job?) or experimental.

**Learning outcome:** your judge's TNR. If it's low, every pass rate it reported before this lab was inflated by how much?

---

## Lab 7 — Gate it in CI

**Rung:** 3, enforced. **Notes:** [10](../notes/10-evals-in-ci.md).

1. Write a gate contract ([10](../notes/10-evals-in-ci.md#the-gate-ladder)) for your suite: pools, gates in pipeline order, thresholds against the baseline.
2. Split your runner into `run` → `results.jsonl` → `assert`.
3. Add a CI workflow ([10](../notes/10-evals-in-ci.md#a-ci-workflow)): smoke on every PR, regression on relevant paths, nightly full.
4. Store a baseline from your current main branch.
5. Open a PR that deliberately regresses one slice. Confirm the per-slice floor catches it, and the gate output names the slice and failure label.
6. Open a PR that changes only a README. Confirm no eval runs.
7. Kill the API mid-run (bad key, low rate limit). Confirm infra errors are counted separately, not as task fails.

**Learning outcome:** whether a gate failure tells the next person what to do without them asking you.

---

## Lab 8 — Online: sample, monitor, harvest

**Rung:** 4. **Notes:** [11](../notes/11-production-and-the-maturity-ladder.md), [12](../notes/12-failure-modes.md).

If you don't have production traffic, replay logs or have a simulated user generate a day of "traffic".

1. Implement the sampling rules: negative feedback, high cost, long conversations, plus a separate random sample ([11](../notes/11-production-and-the-maturity-ladder.md#sampling-live-traffic)).
2. Run your calibrated graders on the sample. Attach scores to spans.
3. Store a baseline. Define one drift alert on a rolling window.
4. Review 20 sampled traces by hand. Measure human–judge agreement.
5. Turn every confirmed failure into a discovery-set row. Fix one, re-run, move it to the regression set.
6. Run the [debug order](../notes/12-failure-modes.md#the-debug-order) on the biggest score movement you saw across all labs. Was it the agent or the eval?

**Learning outcome:** the full loop: a production failure becomes a row, a fix, a gate, and a regression test.

---

## Retro

After all eight labs, answer in writing:

- Which ladder level is your system honestly on now?
- Which grader was most valuable for the least effort?
- What's the smallest difference your suite can detect?
- Which number did you believe that turned out to be noise or an eval bug?
- What would you build first on the next system?
