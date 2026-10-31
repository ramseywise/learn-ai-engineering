---
name: pillar
description: "Bring one pillar (ai-engineering/NN-* or generative-ai/NN-*) to the standard layout in ai-engineering/PILLAR-LAYOUT.md and the definition of done in CURRICULUM.md: README with reading order, notes/ with frontmatter, references.md, sources/ with flat images/, vendored course snapshots folded into notes and listed for removal. Usage: /pillar generative-ai/02-rag-retrieval, or /pillar new <name> to scaffold a new pillar. Run from the learn-ai-engineering repo."
---

You are normalising one pillar so it looks and works like the others. Read
`ai-engineering/PILLAR-LAYOUT.md` (the target tree and house style) and the "Definition of
done" section of `CURRICULUM.md` first. The best worked examples are
`ai-engineering/02-context-engineering/` and `ai-engineering/05-graph-engineering/`.

The pillar's content is the point. Do not rewrite notes that already work. Move, rename,
add frontmatter, write the missing README and references.md, and fold vendored material
in. Content changes beyond that are for `/papers` and `/chapter`.

---

## Step 1 — Inventory

`$ARGUMENTS` is a pillar path (`generative-ai/02-rag-retrieval`, or `ai-engineering/04`).
`new <name>` scaffolds a new pillar instead (skip to Step 4, then add it to `HOMES` in
`scripts/papers/potw.py`, to the subject map in `CURRICULUM.md` and to the parent README).

List everything in the pillar:

```bash
find <pillar> -not -path '*/.git/*' -not -name .DS_Store | sort
git ls-files <pillar> | wc -l
```

Sort each item into one of these:
- **note**: a markdown file of teaching content. Belongs in `notes/NN-<slug>.md`.
- **source**: a PDF or an image. PDFs go in `sources/`, images in `sources/images/`.
- **practice**: a lab or notebook that runs offline. Belongs in `practice/`.
- **vendored snapshot**: an upstream course or repo copied in (`*-main/`, `*-master/`).
- **stray**: build output, caches, duplicates.

## Step 2 — Plan, then stop

Write the plan as a table: item, what it is, where it goes, and why. For each vendored
snapshot, say which notes it feeds and what of it is worth keeping (concepts, short code,
figures), and check its licence. Show the plan to the user and wait. Moving files is
reversible with git, but deleting a snapshot is not when it is untracked or gitignored.

## Step 3 — Fold vendored snapshots

For each snapshot the user approves:
1. Read it the way `/chapter` reads a chapter: claims, code worth keeping, figures.
2. Merge that into the pillar's notes. Cite the upstream URL in the note frontmatter
   `sources:` and inline as the notes already do.
3. Copy figures you use into `sources/images/` with the
   `<author>-<short-title>-fig<N>.<ext>` name and a caption line.
4. Keep a lab only if it runs offline. Otherwise link it upstream from the note.
5. Add a row to the "Vendored snapshots" table in `CURRICULUM.md` saying what went where
   and what was dropped, in the style of the rows already there.
6. Delete the snapshot only after the user confirms.

## Step 4 — The layout

- `README.md`: what the pillar teaches, prerequisites, a table of notes in reading order
  grouped into parts, and links to references.md and slides. Copy the shape of
  `ai-engineering/02-context-engineering/README.md`.
- `notes/NN-<slug>.md`: number in reading order. Every note gets frontmatter with
  `title`, `origin`, `sources:` and `confidence:`. Use `git mv` so history follows, then fix
  every link to the old path:
  ```bash
  grep -rln '<old-name>.md' --include='*.md' .
  ```
- `references.md`: Books / Core papers / AI Papers of the Week tables, as in
  `PILLAR-LAYOUT.md`. Seed it from the sources the notes already cite and from any PDFs
  in `sources/`.
- `sources/` and `sources/images/`: flat, with the naming rules from `PILLAR-LAYOUT.md`.
  Rename with `git mv` and update the image links in the notes.
- `slides/`: leave alone unless it exists. Decks are built with `/slides`.

## Step 5 — Check

```bash
make link-check
python3 scripts/papers/potw.py status --list queued | grep '"pillar": "<home key>"' | wc -l
```

The second command shows how much reading is waiting for this pillar, which goes in the report.

Report: what moved, what was created, which snapshots were folded (and which are waiting on
the user's go-ahead to delete), which done criteria now hold, and the queued readings for
this home. Do not commit. The user reviews the diff.
