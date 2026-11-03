# Drills: the gym

Practice by language and topic, not a sequence. Come in, pick a track, drill, log it. Learning
material lives in the [curriculum](../../README.md); interview format and round prep live in
[`practice/interviewing/`](../../practice/interviewing/README.md). This folder is reps. The dependency runs one way:
practice links to chapters, chapters never depend on practice. [`practice/CROSSWALK.md`](../../practice/CROSSWALK.md)
maps each curriculum unit to the drills and guides that test it.

librarian imports this folder as the **drills** module of its Programming course
(`make import-courses`): every tracked `.md` here becomes a lesson, each track folder a section. A
file with `track:` in its frontmatter feeds Practice mode. Notebooks, `.sql`, `.ts` and `.py` files
stay here and are linked, not imported.

## Tracks

| Track | Folder | What's there | Status |
|---|---|---|---|
| Python | [`python/`](python/README.md) | Track notes and gaps; for cold reps use HackerRank and LeetCode directly | Thin |
| SQL | [`sql/`](sql/README.md) | 1 window-functions drill | Started; CTEs and analytics patterns to add |
| TypeScript (+ HTML/CSS) | [`typescript/`](typescript/README.md) | ESLint reference, 1 types drill | Thin, biggest gap |
| Terraform | [`terraform/`](terraform/README.md) | Track plan, 1 review drill | Started |
| Tooling | [`tooling/`](tooling/README.md) | Git workflow reference | Bash and Docker to add |
| Coding rounds | `coding/` | [Prompts](coding/prompts/README.md), [seeded-bug problems](coding/problems/README.md), [Hello, Interview!](coding/dsa/README.md) as a DSA reference | Active |

`coding/` keeps its layout because the drill tooling depends on its paths.

Unlike `practice/`, this folder has no allowlist: the root `.gitignore` names what stays local. That is
solutions to site problems (`python/leetcode/` and the `hackerrank/` folders), personal attempts
(`coding/scratch/`) and the drill log. Check a new file's licence and contents before adding it.
[`THIRD_PARTY.md`](../../THIRD_PARTY.md) lists the tracked material whose licence is still not cleared.

## Drill schema

New drills are one Markdown file per drill, `programming/drills/<track>/<topic>/<slug>.md`, with
code alongside when the drill needs it (`<slug>.py`, `<slug>.sql`, `<slug>.ts`, `<slug>.tf`).

```yaml
---
title: Window functions — running total per user
track: sql                  # python | sql | typescript | terraform | tooling | coding
topic: window-functions     # folder name; free-form but reuse existing ones
difficulty: medium          # easy | medium | hard
timebox_min: 20
concepts: [window-functions, partitioning]   # librarian concept slugs
units: [programming/sql]    # curriculum folders or notes, repo-relative; leave out if unclear
source: original            # original | hackerrank | leetcode | <upstream URL>
---
```

The title lives in frontmatter only — no `# H1` in the body (markdownlint MD025 counts both).
Body sections, in order:

1. **Prompt** — the task, inputs, constraints. Safe to read before attempting.
2. **Starter** — given code or schema (or a link to the sibling file).
3. **Tests** — how to check an answer: expected output, a test file, or a query result.
4. **Hints** *(optional)* — a ladder, one `<details>` per rung, weakest first.
5. **Solution** — under a `<details>` block so it is not read by accident.
6. **Notes** — the pattern, common mistakes, follow-up variants.

Worked examples of the schema: [`sql/window-functions/top-orders-per-user.md`](sql/window-functions/top-orders-per-user.md),
[`typescript/types/group-by.md`](typescript/types/group-by.md),
[`terraform/review/web-stack.md`](terraform/review/web-stack.md).

`units` links a drill to the curriculum: `scripts/practice/crosswalk.py` checks every path exists and
generates [`practice/CROSSWALK.md`](../../practice/CROSSWALK.md). `concepts` links it to the wiki: librarian's Practice
mode uses it to draw concept → drill edges in the graph.

## Logging

`coding/drill-log.md` is the one append-only log (date, drill, stance, time, grade). It is personal
and gitignored; start your own there. Use the drill's file slug as the QID (`top-orders-per-user`).
librarian's Practice mode reads the Date/QID/Score columns live (never the Note column, never copied
into librarian) to show attempt counts per drill.

## Third-party material

[`coding/dsa/`](coding/dsa/README.md) is "Hello, Interview!" by Dileep Pandey, MIT licence, kept
in [`coding/dsa/LICENSE`](coding/dsa/LICENSE). Other upstreams are recorded in
[`THIRD_PARTY.md`](../../THIRD_PARTY.md).
