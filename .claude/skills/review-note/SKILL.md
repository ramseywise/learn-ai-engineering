---
name: review-note
description: "Quality gate for notes: an independent reader for audience fit, a citation check against the sources, and the structural checks. Applies only fixes that cannot change meaning, and lists the rest for the user. Usage: /review-note <note path>, /review-note <pillar> for every note, /review-note <pillar> --report for no edits. Run from the learn-ai-engineering repo."
---

You run the quality gate on one note or one pillar. The reviewers report and you decide. They have not seen why the
note was written this way, so do not tell them.

## Step 1 — Scope and machine checks

`$ARGUMENTS` is a note path or a pillar path. `--report` means change nothing.

```bash
make chapter-check PILLAR=<pillar or note>
python3 scripts/curriculum_map.py issues --pillar <pillar>
```

## Step 2 — Dispatch

For each note, dispatch `audience-editor` (the path only) and `citation-checker` (the path, with "all"). Run at most
3 notes at a time: a pillar review is many full reads, and they count against the account's usage limit. Tell the user
the note count first if a pillar has more than 10 notes, and do not start a whole-subject review without being asked.

## Step 3 — Decide

Read every finding against the note. A reviewer can be wrong, so check before you apply.

- **Apply without asking**, only if it cannot change the meaning: a link to the chapter that teaches a term, a broken
  link, a missing frontmatter source, a venue the source confirms, a number or setup corrected to a verified quote.
- **List for the user**: a rewrite that shifts emphasis, a removed claim, any `setup-differs` where the note may be
  deliberate, a restructure, and every claim a source does not support. Never delete a claim on your own.
- **Reject** what you checked and found wrong. Say why: this is how the reviewers' false-positive rate gets measured.

A citation marked `unverifiable` stays unverified. Report it; do not count it as passed.

## Step 4 — Report

Keep a table per note: verdict, findings applied, listed, rejected, citations verified and unverifiable. Put anything a
source contradicts first. Re-run the checks in Step 1 if you edited, and `make link-check`.

Stage only the notes you changed, by explicit path. Show `git diff --staged --stat`, suggest a commit message. Do not commit.
