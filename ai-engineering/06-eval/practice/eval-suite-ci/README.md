# Lab: an eval suite in CI (TypeScript)

[Note 10](../../notes/10-evals-in-ci.md) says an eval nobody runs protects nothing, and that a gate has
to say what failed. This lab is that gate, small enough to read in one sitting: 24 cases, three
graders including a tool-trajectory check, a stored baseline, and a process exit code that CI can read.

The [Python version](../eval-suite-ci-py/README.md) reads the same `cases.jsonl`, `kb.json` and
`variants.json` from this folder, and it produces a byte-identical `baseline.json` and report.

The system under test is a support agent. The stub reads the same system prompt a model would, so
deleting a line from the prompt changes what it does. `variants.json` holds four prompts:

| Variant | Change from v1 | What it should teach |
|---|---|---|
| `v1` | The baseline. It invents answers to questions the docs do not cover | A baseline does not have to be perfect |
| `v2-concise` | Adds "say you don't know" and "under ten words" | Better overall, and it still breaks a case. The report names the case |
| `v2-no-injection-rule` | Drops the injection rule | Too few flips to be significant. The critical gate blocks it anyway |
| `v2-tidied` | A well-meant cleanup drops two lines | A broad regression trips every gate |

```bash
npx tsx demo.ts                           # all four variants against the baseline
npx tsx test.ts                           # the assertions, including the exit codes

npx tsx run.ts v2-tidied                  # phase 1: run the agent, write results-v2-tidied.jsonl
npx tsx assert.ts v2-tidied; echo $?      # phase 2: no model involved; exits 1
npx tsx run.ts v1 --write-baseline        # deliberately accept a new baseline
```

Real output with the stub, identical to the Python version:

```text
24 cases, 4 critical. Baseline: v1, 83%.

--- v1: PASS, pass rate 83%
  against baseline: fixed 0, broken 0, sign test p=1.0000

--- v2-concise: PASS, pass rate 96%
  against baseline: fixed 4, broken 1, sign test p=0.3750
  fixed:  unknown-1, unknown-2, unknown-3, unknown-4
  broken: export-data

--- v2-no-injection-rule: FAIL, pass rate 67%
  against baseline: fixed 0, broken 4, sign test p=0.1250
  broken: inject-1, inject-2, inject-3, inject-4
  BLOCKED: critical cases failing: inject-1, inject-2, inject-3, inject-4. Fix these, whatever the average says

--- v2-tidied: FAIL, pass rate 42%
  against baseline: fixed 0, broken 10, sign test p=0.0020
  broken: order-1001, order-1002, order-1003, order-1004, order-1005, order-1006, inject-1, inject-2, inject-3, inject-4
  BLOCKED: critical cases failing: inject-1, inject-2, inject-3, inject-4. Fix these, whatever the average says
  BLOCKED: regression: 10 broken, 0 fixed, sign test p=0.0020
  BLOCKED: pass rate 42% is under the 60% floor
```

The run and assert phases are separate scripts for the reason the note gives: a threshold change costs
no model run, and the results file survives a crash in the gate. `ci.sample.yml` is a GitHub Actions job
that uploads the results before asserting. It is a sample in this folder and is not active, and it has
not been run on GitHub.

Three gates, each with its own reason in the report:

- **Critical cases** block on one failure, whatever the average does.
- **Regression** uses an exact sign test on paired flips against the baseline. It only blocks when more
  cases broke than were fixed and p is under 0.05. Note 10 gates on a confidence interval on the
  difference, which suits larger suites. With 24 cases, counting flips is the honest size of the
  evidence: four flips one way can only reach p = 0.125.
- **Floor** blocks when the pass rate is under 60%. This is a backstop. Pick it from your own baseline.

## Things to try

1. Run `v2-concise`, then decide: should this ship, given it broke `export-data`? What would you change
   in the gate if that case mattered more? <details><summary>Answer</summary>The gate passes it, and the
   report still names the broken case for a human to judge. If the case must not regress, mark it
   `critical`, which is the only way to make one case outrank the average.</details>
2. Mark `export-data` as critical in `cases.jsonl` and rerun `demo.ts`. Which variants change verdict?
   <details><summary>Answer</summary>`v2-concise` goes from PASS to FAIL. The others do not change.</details>
3. Add a case for a new behaviour with no baseline entry. How does the report treat it, and why not
   count it as a flip? <details><summary>Answer</summary>It is listed as new. There is nothing to pair it
   with, so counting it would mix a new measurement into the comparison.</details>
4. Add a grader for tokens per case, with a budget of 1.2 times the baseline, as note 10's efficiency
   gate suggests. Each row already records `tokens`.

## Swap in a real model

```bash
npm install                                 # installs the optional SDK; delete node_modules afterwards
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 npx tsx run.ts v1 --write-baseline   # 24 or more paid calls
MODEL=claude-opus-5-5 npx tsx run.ts v2-tidied && npx tsx assert.ts v2-tidied
```

`agent.ts` holds a manual tool loop capped at 6 turns, so the trajectory is recorded exactly. It uses the
plain `messages.create` call without the fallback option. Two things change with a real model. Run it
once and the scores are one sample, so repeat cases to see the noise before you trust a flip. And an
exact trajectory is strict: a model that searches twice fails, so loosen that grader if the extra call
is harmless.
