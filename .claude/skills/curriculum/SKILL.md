---
name: curriculum
description: "Keep the course one coherent whole as it grows. Shows the curriculum map and its integration problems, decides where a new topic belongs, wires a new or moved note into READMEs, Next links, decks and syllabi, and audits a subject for overlap and order. Usage: /curriculum (status), /curriculum place \"vector databases\", /curriculum integrate <note path>, /curriculum audit <subject or pillar>, /curriculum fix <pillar>. Run from the learn-ai-engineering repo."
---

You keep the curriculum integrated. Every new note makes the course bigger, and only integration makes it better:
a chapter nobody links to, or one that repeats another under a new name, is a net cost.

The map (`scripts/curriculum_map.py`) answers structure, and the `curriculum-steward` agent answers what takes
reading. You make the edits, because the agent never does. Read
`.claude/skills/pillar/references/pillar-layout.md` first: it says which file does which job.

Other sessions may share this working tree. Before editing any file, check `git status --short`. If it already has
uncommitted changes that aren't yours, do not edit it: list the edit in your report.

## Status: no argument

```bash
make curriculum
```

Report notes and words per subject, the issues by kind, and the few worth fixing first. `no_inbound` is information. So is `concept_unlinked`: a note uses a maths concept from `scripts/concept_homes.json` without linking its home. Add a link only where the note needs the idea; passing mentions stay as they are. When a concept gets a new home, add it to that file.

## Place: `place "<topic>"`

Dispatch `curriculum-steward` with the topic and any sources the user named. Report its recommendation, what it
overlaps, and the prerequisites. Change nothing. If it recommends a new pillar, that is the user's decision: the
curriculum is frozen, and a new pillar needs a reason written into "Structure decisions" first.

## Integrate: `integrate <note path>`

Run this after any new or moved note. `/write-chapter` calls it. Make these edits, then re-run the checks:

1. **Pillar README.** Add the note to the reading order and any table that lists notes.
2. **Next chain.** The previous note's `## Next` points here, and this note's points on.
3. **Builds on, feeds into.** Update the pillar README's tables when the note crosses a pillar or subject.
4. **Other notes.** Dispatch `curriculum-steward` for the notes that should now link here. Add a link where a note
   mentions the idea in passing. Replace a duplicate explanation with a link only when the steward names which copy
   stays authoritative, and list that in your report.
5. **Syllabus.** Change `<subject>/README.md` or `CURRICULUM.md` only if an objective or learning path changes. The
   subject README has no chapter lists, so do not add one.
6. **Deck.** The map reports `deck_gap`. Revising a deck is a `/slides` run: name it in the report as the next step,
   unless the user asked for it.
7. **Practice.** If `programming/drills/` or `practice/` has drills on the topic, link them, and run `make crosswalk` if units changed.

```bash
python3 scripts/curriculum_map.py issues --pillar <pillar>
make chapter-check PILLAR=<pillar>
make link-check
```

## Audit: `audit <subject or pillar>`

Run `python3 scripts/curriculum_map.py issues --pillar <scope>`, then dispatch `curriculum-steward`. For a whole
subject, dispatch one per pillar, then one across the subject's boundaries, at most 3 at a time. Report findings
ranked by what a learner would suffer. Change nothing. Say how far each reader read: an audit that read only headings
says so.

## Fix: `fix <pillar>`

Fix what the map reports for one pillar, one kind at a time. Read each note's context before changing its Next link.
Some issues are deliberate: a closing note may point out of the pillar, and a number gap may be a reserved slot. Leave
those and say why. Never renumber or move a note without the user: links, the ledger, decks and librarian all use
the path.

## Close out

Stage only the files you changed, by explicit path, never `git add -A`, because other sessions may have work in this
tree. Show `git status` and `git diff --staged --stat` and suggest a commit message. Do not commit.
