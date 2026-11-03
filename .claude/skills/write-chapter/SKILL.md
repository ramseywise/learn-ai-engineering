---
name: write-chapter
description: "Write one new chapter from scratch to the chapter standard: place it in the curriculum, research it from real sources, draft it, run an independent review, test its code and wire it into the course. Never cites what was not read. Usage: /write-chapter <pillar> <NN-slug> [PDF paths or a brief], or /write-chapter \"<topic>\" to place it first. Run from the learn-ai-engineering repo."
---

You are writing one chapter of the course. Agents read and review; you hold the outline, the argument and every
sentence. Read `.claude/skills/pillar/references/pillar-layout.md` ("notes/" and "notes/: the chapter") and
`.claude/skills/pillar/references/audience-profiles.md`. Reading sources into a note that already exists is `/chapter`
or `/papers`, not this skill.

## Step 1 — Place it

Check that nobody owns this chapter. Other sessions share this tree:

```bash
git status --short
ls <pillar>/notes
grep -rn '<NN-slug>' .claude/docs/plans/ <pillar>/README.md
```

If the file exists, or a plan or a live session has it, stop and report that. Dispatch `curriculum-steward` to confirm
the placement, the overlap and the prerequisites. If the topic is already taught well, say so and do not write a second
version. Use the plan's number and title if one is assigned.

## Step 2 — Gather evidence

Plan the outline first: the problem, 3 to 6 concepts, the worked example for each. Then dispatch together, at most 3
agents at a time:

- `source-reader`, one per PDF the course holds on the topic. Look in the ledger and in the subject's `sources/`.
- `web-researcher`, one per open question, for what the local sources do not settle.

**Everything cited must be read.** A source you know of but no agent has read is not a citation. Add it to the report
as a candidate instead. Add new readings to the ledger with `scripts/papers/discover.py curated` rather than citing them
unread. If evidence on a concept is thin, say so in the chapter and in the report, and set `confidence` to match.

## Step 3 — Draft

Write `<pillar>/notes/<NN-slug>.md` in the voice of the two neighbouring notes, using the seven chapter parts in order.
Frontmatter: `origin: synthesis`, `sources:` with every source, `confidence:` by the rule in the layout, `cleaned:` today.

- Each number comes from an agent's quote, with its setup. If you find yourself writing a number nobody quoted, cut it
  or mark it as your own arithmetic and show the arithmetic.
- **Code runs as written.** Put longer labs in `<pillar>/practice/`. Run every block, and paste real output instead of
  output you expect. If a block cannot run here, say what it needs.
- Exercise answers and interview answers must follow from this chapter.

## Step 4 — Review

Dispatch `audience-editor` (path only: no reasoning) and `citation-checker` (the path, with "all"), then apply `/review`
Step 3's rules for what to fix. Do not stop at the first pass if a fix was substantial: re-check that part.

## Step 5 — Integrate

Run `/curriculum integrate <note path>`, and add the `references.md` rows. Then:

```bash
make chapter-check PILLAR=<note path>
python3 scripts/curriculum_map.py issues --pillar <pillar>
make link-check
```

Then mark any ledger readings you folded in, with `potw.py mark integrated`, if their rows map to this chapter.

## Step 6 — Report and stage

Report what you read, what you could not verify, the review's findings and what you did with them, and any candidates
left unread. Stage only this chapter's files by explicit path. Show `git status` and suggest a commit message. Do not
commit. A chapter is **not** done until its code has run and its citations have been checked: if either was skipped, say
so at the top of the report.
