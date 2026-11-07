---
name: extract
description: "Backfill structured extractions for readings the pipeline already holds: dispatch source-readers on PDFs with no full extraction (or only a salvaged schema-0 report), check each file, and report what the readers found that contradicts the notes. Never edits notes, references.md or the ledger. Scope is tier 1, tier 2 and book chapters unless all is given. Usage: /extract (next 9, best first), /extract rag, /extract rag 15, /extract all 12, /extract 1706.03762. Run from the learn-ai-engineering repo."
---

You are filling `scripts/papers/extractions/` for readings that were integrated, or downloaded, before every
read left an extraction behind. The goal is one checked JSON per PDF: question, hypothesis, method in numbers,
results, limits and lineage, so the corpus can be mapped (who follows whom, who found the opposite) and every
empirical paper says what it would take to retrain it. See `scripts/papers/README.md`, section *Extractions*.

This skill reads and records. It does not change the notes. Notes are the source of truth, and a backfill
read that disagrees with one is a finding for the user, not an edit.

## Step 1 — Pick

```bash
python3 scripts/papers/extract.py status
python3 scripts/papers/extract.py next --n <N> [--home <home>]
```

Each line is `key`, `pdf`, `note`, state (`none`, or `salvaged` when an old text report exists), and the
extraction path. The order is: tier 1 and 2 papers, then book chapters, most cited first. That is the whole
backlog by default. Paper tiers 3-6 come in only with `all` in `$ARGUMENTS` (pass `--all` to `next` and
`status`): the nightly run reaches them once the core is empty, and a `/papers` read writes their extraction
anyway. `$ARGUMENTS` may give a home, `all`, a count (default 9) or explicit keys or arXiv ids (explicit keys
are always in scope). Never take more than 15 in one session.

## Step 2 — Read

Dispatch one `source-reader` per reading, at most 3 at a time, each with its PDF path and its `note`. Tell
each to read the whole PDF, write the extraction and run the check. A salvaged reading has an old report in
its file that the reader uses as a map, but it still reads the PDF: the old reports have no method block.

When a reader returns, confirm its `EXTRACTION` line says the check passed. If it failed, or `COVERAGE`
shows a partial read, send it back once with the failure. Still failing: leave it, and list it.

## Step 3 — Compare with the note

For each reading, look at the note it maps to (its `note`, and anything `grep` finds citing its key).
Compare only what the note says about this source with the extraction's `results` and `limits`.
Do not edit. Collect:

- **contradicts**: the note states a number or a claim the source does not support, or the opposite of it.
- **missing setup**: the note quotes a number from the source without the condition it holds under.

## Step 4 — Close out

```bash
python3 scripts/papers/extract.py check --all --quiet --schema-only
python3 scripts/papers/extract.py report        # refresh reports/lineage.md and reports/reproducible.md
python3 scripts/papers/extract.py status
```

Report: how many extractions were written and passed, which failed and why, the reproducibility score of
each empirical paper, and every **contradicts** and **missing setup** finding with the note, line and the
extraction's quote, contradictions first. These are proposals for the user. Do not commit.
