---
name: practice
description: "Author and wire one piece of practice material: a drill in programming/drills/, a coding prompt, or a round file in practice/interviewing/rounds/. Places it by the split rule, applies the schema and units, clears the licence and allowlist, runs the checks and the drill-reviewer, and logs findings. Usage: /practice <path> to wire an existing file, /practice drill <track> <topic> \"<idea>\", or /practice round <round> \"<idea>\". Run from the learn-ai-engineering repo."
---

You add one piece of practice material and leave it wired in, checked and reviewed. Practice tests what the notes
teach, so a new file never becomes the only home of a topic.

`$ARGUMENTS` is a path to wire, or `drill <track> <topic> "<idea>"`, or `round <round> "<idea>"`.

## Step 1 — Place it

Ask the split rule: "Is this true regardless of whether I'm being interviewed?"

- **Yes, and it's knowledge**: it belongs in a pillar note. Add a row to that note's `Interview checklist` only if the
  answer is findable in the note above it, in the table format the note already uses and under the 7000-word cap. If
  no note answers it, report a gap for `/write-chapter` and stop. Don't write the answer here.
- **Yes, and it's something to practise**: a drill under `programming/drills/<track>/<topic>/`.
- **No**: a file in `practice/interviewing/rounds/<round>/`. The rounds are listed in
  [the role map](../../../practice/interviewing/README.md). Check that round's `study-guide.md` and `questions.md`
  first, and add to them rather than repeat them.

## Step 2 — Write to the schema

**Drills** follow [the drill schema](../../../programming/drills/README.md): frontmatter `title`, `track`, `topic`,
`difficulty`, `timebox_min`, `concepts`, and `source` where it applies. No H1 in the body. `## Prompt`, `## Starter`
and `## Tests`, in that order, then optional `## Hints`, a solution inside `<details>`, and notes. The tests must fail
bad code, and the solution must pass them.

**Round files** start at the `#` heading, with no preamble. Worked examples say what the interviewer is checking. Keep
the topic content in the notes, and link to it. Numbers carry their setup, and a number with no read source doesn't go
in. Never write in a personal anecdote, employer or private project.

## Step 3 — Link it to the curriculum

Add `units:` to the frontmatter: repo-relative paths to the pillars or notes it tests, only where the mapping is clear.
Name a note rather than a pillar when one note covers it. `concepts` on a drill are what connect it to the wiki.

## Step 4 — Clear the licence and allowlist

`practice/.gitignore` fails closed, and the root `.gitignore` names the drill folders that stay local. Before a
`practice/` file gets a line in the allowlist:

1. **Licence.** Written here, or copied from an upstream with a licence that allows it, recorded in `THIRD_PARTY.md`.
   An upstream with no licence, a Notion export or a scraped question bank stays ignored. Never paraphrase one to get
   around this. Ask the user.
2. **Personal data.** No drill logs, attempts, employers, deployments or names. Scrub it, or leave the file ignored.
3. **Add one line**, `!/interviewing/rounds/<round>/<file>.md`, in sorted order.

A tracked file that links to an ignored one fails `make crosswalk`. Don't list the ignored file to fix that: remove the
link. Never delete an untracked or ignored file, since git can't restore it.

## Step 5 — Check

```bash
make drill-check DRILL_PATH=<path>
make crosswalk
```

`make crosswalk` validates units and links and regenerates `practice/CROSSWALK.md`. Fix failures before going further.
`make drill-check` applies the schema to files under a `drills/` folder. It only checks that a round file parses, so a
round example is held to the schema by your reading alone.

## Step 6 — Review

Dispatch `drill-reviewer` with the path only. Don't pass your reasoning. It runs the code in a temporary copy and works
the material as a learner would. Fix what can't change the meaning, and list the rest for the user.

Log every finding, rejected ones included, in the format in [/review Step 4](../review/SKILL.md):

```bash
python3 scripts/review/findings.py patterns
python3 scripts/review/findings.py add <<'JSONL'
{"run": "<date>-<short target>", "reviewer": "drill-reviewer", "target": "<path>", "line": 12, "kind": "wrong-answer", "decision": "applied", "summary": "<one line, no personal data>"}
JSONL
```

## Step 7 — Hand over

Run `make test`, stage by explicit path, and report: the file, the units, any licence question and any gap. The user
commits.
