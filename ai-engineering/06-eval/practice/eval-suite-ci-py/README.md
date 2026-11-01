# Lab: an eval suite in CI (Python)

The Python twin of the [TypeScript lab](../eval-suite-ci/README.md). It reads that folder's
`cases.jsonl`, `kb.json` and `variants.json`, and it produces a byte-identical `baseline.json` and
report. Read the TypeScript README for the four variants, the three gates and the exercises.

```bash
uv run demo.py                     # all four variants against the baseline
uv run test.py                     # the assertions, including the exit codes

uv run run.py v2-tidied            # phase 1: run the agent, write results-v2-tidied.jsonl
uv run gate.py v2-tidied; echo $?  # phase 2: no model involved; exits 1
uv run run.py v1 --write-baseline  # deliberately accept a new baseline
```

The second phase is `gate.py`, where TypeScript has `assert.ts`, because `assert` is a Python keyword.
`ci.sample.yml` is a sample GitHub Actions job. It is not active, and it has not been run on GitHub.

Real output with the stub, identical to the TypeScript version:

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

## Swap in a real model

```bash
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 uv run --with anthropic run.py v1 --write-baseline   # 24 or more paid calls
MODEL=claude-opus-5-5 uv run --with anthropic run.py v2-tidied && uv run gate.py v2-tidied
```

`agent.py` holds a manual tool loop capped at 6 turns, so the trajectory is recorded exactly. It uses the
plain `messages.create` call without the fallback option.
