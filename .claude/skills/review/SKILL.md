---
name: review
description: "Quality gate for course content. Sends a note, deck, drill, guide or lab to the right independent reviewers, applies only fixes that cannot change meaning, lists the rest for the user and logs every decision. Usage: /review <note, deck.yaml, drill or practice path>, /review <pillar> for its notes, /review <pillar> --deck, /review <path> --report for no edits, /review status for the log, /review eval <reviewer> to test a reviewer on planted faults. Run from the learn-ai-engineering repo."
---

You run the quality gate on one piece of content or one pillar. The reviewers report and you decide. They have not
seen why the content was written this way, so do not tell them.

`$ARGUMENTS` is a path, plus `--report` to change nothing (decisions are still logged). `status` runs
`make review-findings` and stops. `eval <reviewer>` goes to "Testing a reviewer" below.

## Step 1 — Route and run the machine checks

| Target | Machine checks | Dispatch |
|---|---|---|
| A note, or a pillar | `make chapter-check PILLAR=<path>`, `python3 scripts/curriculum_map.py issues --pillar <pillar>` | `audience-editor` (the path only) and `citation-checker` (the path, with "all") per note |
| `slides/deck.yaml`, or `<pillar> --deck` | `make slides PILLAR=<pillar> PREVIEW=1` unless `--report`; with `--report`, use the existing `.preview/` | `deck-reviewer` (the pillar path) |
| `practice/` drill, prompt, problem, MCQ, guide or lab, including `<pillar>/practice/` | `make drill-check DRILL_PATH=<path>`, `make crosswalk-check` | `drill-reviewer` (the path only) |

Fix or report machine-check failures first. A reviewer shouldn't spend a full read on what a script already caught.

## Step 2 — Dispatch

Run at most 3 reviews at a time: each is a full read, and they count against the account's usage limit. Tell the user
the item count first if there are more than 10, and do not start a whole-subject review without being asked.

## Step 3 — Decide

Read every finding against the content. A reviewer can be wrong, so check before you apply.

- **Apply without asking**, only if it cannot change the meaning: a link to the chapter that teaches a term, a broken
  link, a missing frontmatter source, a venue the source confirms, a number or setup corrected to a verified quote, a
  deck fix that only cuts overflow.
- **List for the user**: a rewrite that shifts emphasis, a removed claim, any `setup-differs` where the note may be
  deliberate, a restructure, every claim a source does not support, and every changed drill answer or expected output.
  Never delete a claim on your own.
- **Reject** what you checked and found wrong, and say why.

A citation or drill check marked `unverifiable` stays unverified. Report it; do not count it as passed.

## Step 4 — Log every decision

Log every finding, including the ones you rejected. This is how reviewer precision and recurring faults get measured.
Use the reviewer's own `kind`, or its status for `citation-checker`. Don't log a citation that verified.

```bash
python3 scripts/review/findings.py patterns   # reuse a slug if one fits
python3 scripts/review/findings.py add <<'JSONL'
{"run": "2026-11-02-<short target>", "reviewer": "drill-reviewer", "target": "<path>", "line": 12, "kind": "wrong-answer", "decision": "applied", "summary": "<one line, no personal data>", "pattern": "<optional slug>"}
{"run": "...", "reviewer": "...", "target": "...", "kind": "prose", "decision": "rejected", "reason": "<why>", "summary": "..."}
JSONL
```

Set `pattern` only for a fault a script or spec could prevent, such as `preprint-missing`. When the user settles a
listed finding, record it with `findings.py decide <id> applied|rejected --reason "..."`.

## Step 5 — Report

Keep a table per item: verdict, findings applied, listed, rejected, and citations or checks verified and unverifiable.
Put anything a source contradicts, and any wrong drill answer, first. Re-run the Step 1 checks if you edited, and
`make link-check`. Then show `make review-findings`, and for each promotion candidate propose a script check or spec
change. Don't build it unless the user agrees. Once it exists, run `findings.py promote <pattern> --to <where>`.

Stage only the files you changed, by explicit path, plus `scripts/review/findings.jsonl`. Show
`git diff --staged --stat` and suggest a commit message. Do not commit.

## Testing a reviewer

Each reviewer with a case in `scripts/review/evals/cases.json` has fixtures with planted faults and a clean control.
Run this after changing a reviewer's definition, not on a schedule.

1. For each case for `<reviewer>`, dispatch the reviewer with only the fixture path. Don't mention that it is a test.
2. Save each report to `.claude/docs/evals/<case id>.txt`, which is gitignored.
3. Run `python3 scripts/review/score_eval.py <reviewer> --reports .claude/docs/evals --record`.

Report recall on planted faults and any findings on the clean control. A lower score than the last row in
`scripts/review/evals/results.jsonl` is a regression: say so rather than editing the fixture to pass.
