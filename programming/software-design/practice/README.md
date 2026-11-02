# Lab: refactoring a smelly module under tests

> One real-looking module, `usage_report.py`, reads a log of LLM calls and prints a cost and latency report. It has one long function, globals, flag arguments and three bugs. You'll pin what it does, restructure it in steps without changing its output, fix the bugs on their own, and add a feature.

The module was written for this lab, so its smells are deliberate. The numbers below come from the worked solution, an n of 1 where the same person wrote both versions. [Chapter 2](../notes/02-refactoring.md#what-the-lab-measured) discusses what they do and don't show. Do the lab after chapter 2, and come back for the [mutation step](#step-5-test-the-tests) after [chapter 5](../notes/05-testing-strategy.md).

## Run it

You need Python 3.14 and [uv](https://docs.astral.sh/uv/). From this folder:

```bash
bash check.sh              # the worked solution: every step against its tests
bash check.sh exercises    # your copy of the module against its characterization tests
```

```text
ok    solutions/usage_report_lab/  (94 passed in 0.16s)
ok    exercises/usage_report_lab/  (22 passed in 0.03s)
```

That's Python 3.14.7, on both the standard and free-threaded builds. `check.sh` removes the `.venv` and caches when it finishes.

## What you're given

`exercises/usage_report_lab/` holds the module and a safety net that already passes:

| File | What it is |
|---|---|
| `usage_report.py` | The module. The file is 95 lines, and `report()` has a McCabe score of 23 |
| `calls.jsonl` | 65 lines of call log, including 3 duplicate ids, 3 failed attempts and a truncated line |
| `golden.json`, `make_golden.py` | Output recorded from the original across 16 flag combinations, and the script that recorded it. Don't rerun it once you've started, because that would bless whatever you broke |
| `test_usage_report.py` | 22 tests: 16 golden-master cases, 3 pinning bugs (named `test_PINNED_…`), and 3 pinning other behaviour |

The tests reach 100% statement and branch coverage of the module. Chapter 5 explains why that alone wouldn't be enough, and step 5 here measures it.

## The steps

Work in a copy of `usage_report_lab/` under Git if you can, and make each step a commit that passes. Run `uv run pytest` after every small move, and revert a move that goes red rather than debugging it. Open the matching file in `solutions/usage_report_lab/steps/` only after you've tried.

### Step 1: split the phases

Keep behaviour exactly the same, bugs included. Separate parsing, aggregation and rendering into functions. Render to one string, then send it to stdout and to the file, so that the duplicated `print` and `write` branches collapse. All 22 tests should stay green with no edits to them.

### Step 2: name the data and tabulate prices

Still no behaviour change. Replace the four-element lists with dataclasses, and the `if` chain per model with a table of prices. Keep `report()`'s signature, because callers use it, and keep the globals, because removing them changes behaviour.

Then check that your net works. Change the `atlas-medium` completion price from `0.015` to `0.0015`, run the tests, watch them fail, and put it back.

### Step 3: fix the bugs, on their own

Now change behaviour on purpose, in a commit that does nothing else. The three `test_PINNED_` tests name the bugs: a second call in a process sees nothing, totals accumulate between calls, and a failed attempt hides its successful retry. Decide what each should do, update those tests and re-record the golden file, then read the difference in `golden.json` before accepting it.

### Step 4: add the feature

The feature that justified the work: bill `cached_tokens` at a tenth of the prompt price, and add `by_tenant=True` for a per-tenant breakdown. Then, for comparison, add the same feature to an untouched copy of the original.

### Step 5: test the tests

After chapter 5, run the small mutation tester, which swaps one operator at a time and reruns the tests:

```bash
cd exercises/usage_report_lab && uv run python ../../mutate.py
```

```text
37 mutants, 37 killed, 0 survived
```

Next, in a scratch copy, delete the golden-master test, leaving six tests, and run it again. The result was `37 mutants, 13 killed, 24 survived`, with survivors on the arithmetic of the pricing lines, the per-model counters, the `or` that prices `atlas-small-2`, and the `mode == "full"` check before the file write. Which of those would you actually care about? `mutate.py` restores `usage_report.py` when it finishes, including after an error, but use a clean Git state anyway.

## What the worked solution measured

Python 3.14.7, ruff 0.16.5 for McCabe scores.

```text
                       lines  worst McCabe  coverage  notes
step0_original            95            23      100%  (start)
step1_split_phases        94             6      100%  no behaviour change
step2_types_and_table    120             6      100%  no behaviour change
step3_fix_pinned_bugs    120             6       98%  calls 58 -> 60, total 0.7201 -> 0.7483
step4_add_feature        132             6      100%  cached tokens, by_tenant
feature_on_original      106            26       60%  same feature, no refactor
```

The feature's diff was about the same size either way:

```text
                               added   removed   hunks
on the original                  +24       -13       8
on the refactored step 3         +26       -14      11
```

So refactoring didn't shrink this diff or the line count. The gains are elsewhere: a worst score of 6 rather than 26 for the next change to land on, pricing that can be tested alone, and one place for each fact. Whether that pays depends on how many more changes are coming. Chapter 2 goes through this.

The deliberate price error from step 2, made in the worked solution, failed 16 of its 94 tests. Changing the p95 from `0.95` to `0.90` in the exercise module failed 8 of 22.

## Questions to answer when you've finished

1. At which step were you most tempted to fix a bug early? What would have happened to your golden test?
2. Which of your moves went red? Was reverting faster than debugging would have been?
3. Would you do this refactor for real if this module changed once a year? What about monthly?
