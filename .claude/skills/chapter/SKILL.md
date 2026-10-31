---
name: chapter
description: "Fold one book chapter (a PDF under some home's sources/<book-slug>/chNN-*.pdf) into the notes it belongs to: prose, code and figures merged into existing sections, a Books row in references.md that maps chapters to notes, and the ledger row marked integrated. Never writes a chapter-summary note. Usage: /chapter ai-systems-performance-engineering ch05, /chapter huyen-ai-engineering, or /chapter with no argument to take the next queued chapter. Run from the learn-ai-engineering repo."
---

You are folding a book chapter into the course notes. The notes are the product. A
chapter earns its place by sharpening, extending or evidencing what the notes already
say, and by filling sections the notes are missing. It never becomes a note of its own
called "Chapter 5 summary". A chapter usually spreads across two or three notes.

Read `ai-engineering/PILLAR-LAYOUT.md` first. It defines where things live and the house
style for notes, figures and references.

---

## Step 1 — Pick the chapter

```bash
python3 scripts/papers/potw.py status --list queued | grep '/ch[0-9]\|/appendix-'
```

Each line is JSON with `key`, `title`, `pillar` (the home key), `note` (the triage's best
guess, repo-relative, may be null), `pdf` (repo-relative) and `reason`. If a queued
chapter's `pdf` is still under `ai-engineering/readings/`, run
`python3 scripts/papers/potw.py route --apply` first.

`$ARGUMENTS` may name a book slug (the folder under `sources/`) and optionally a chapter
(`ch05`, `appendix-a`). With only a book, take its lowest-numbered queued chapter. With
nothing, take the lowest chapter of the book with the most chapters already integrated
(finish a book before starting the next). One chapter per run unless the user asks for
more.

## Step 2 — Read the chapter

Extract the text. Chapter PDFs saved from the O'Reilly reader are often one very tall
page, so read by character range, not by page:

```bash
uv run -q --with pypdf python -c "import sys,pypdf; t='\n'.join(p.extract_text() for p in pypdf.PdfReader(sys.argv[1]).pages); print(len(t),'chars'); print(t[int(sys.argv[2]):int(sys.argv[3])])" <pdf> 0 40000
```

Read the whole chapter, in slices. As you go, list:
- the chapter's claims, each with its numbers and the setup they hold under
- code worth keeping: short, runnable or near-runnable, illustrating one idea
- figures that explain something faster than prose:
  ```bash
  uv run -q --with pymupdf python scripts/papers/figures.py captions <pdf>
  ```
- what the chapter gets wrong or leaves out, and anything that has dated

## Step 3 — Map it onto the notes

Read the home's `README.md` and every note title in its `notes/`. Read the triage's `note`
in full, and any other note the chapter's sections touch. Book chapters often belong to
more than one home (a Huyen chapter can feed `rag` and `eval`). That is fine: write into
each home's notes, and add the Books row to each home's references.md.

For each claim, decide one of:
- **sharpens**: the note already says it. Add the number, example or citation.
- **extends**: the note is missing it. Add a paragraph or a short subsection in the
  note's voice.
- **contradicts**: the note's claim is wrong or overstated. Fix it and flag it in the report.
- **new note**: only when the chapter covers a topic the pillar plans but has no note
  for. Check the README's planned-notes table and use that number and title. Write a real
  note, not a summary.
- **drop**: already covered at least as well, or off-topic for this pillar.

If nothing survives, the chapter adds nothing. Run
`python3 scripts/papers/potw.py mark skipped <key>`, keep the PDF, and say why in the report.

## Step 4 — Write

- **Prose.** Merge into existing sections. Keep the note's voice, density and heading
  structure. Give every number its condition.
- **Code.** Fenced, short, with a language tag. Rewrite the book's snippet to fit the note
  instead of pasting a page. Point long labs at the upstream repo if the book has one.
- **Figures.** At most two or three per chapter, and only where they carry the argument.
  Embedded raster images come out with `extract`; vector diagrams need `crop`:
  ```bash
  uv run -q --with pymupdf python scripts/papers/figures.py list <pdf>
  uv run -q --with pymupdf python scripts/papers/figures.py extract <pdf> --page P --xref X \
      --out <home>/sources/images/<book-slug>-fig<N-M>.png
  uv run -q --with pymupdf python scripts/papers/figures.py page <pdf> --page P --out /tmp/p.png  # then Read it
  uv run -q --with pymupdf python scripts/papers/figures.py crop <pdf> --page P --clip x0,y0,x1,y1 \
      --out <home>/sources/images/<book-slug>-fig<N-M>.png
  ```
  Look at every saved PNG with Read before embedding it. Caption it:
  `*Image Source: <Author>, *<Book>* (<Publisher>, <year>), Fig. N-M*`
- **Inline citations.** Cite as `(*<Short title>*, ch. N)`. Do not link the PDF from a note.
  Add the book once to the note's frontmatter `sources:`.

## Step 5 — references.md

Each home has one Books row per book, as in
`ai-engineering/05-graph-engineering/references.md`. Create the row on the first chapter;
on later chapters extend its "Folded in as" map:

```
| ★ | <Author>, *<Title>* (<Publisher>, <year>). Chapter PDFs in [sources/<book-slug>/](sources/<book-slug>/). Folded in as: ch. 1–2 → [01](notes/01-….md); ch. 5 → [04](notes/04-….md). Notes cite it as `(*<Short title>*, ch. N)` | 01, 04 |
```

Use the column shape the file already has. If the home has no references.md, create it
from `PILLAR-LAYOUT.md`.

## Step 6 — Close out

```bash
python3 scripts/papers/potw.py mark integrated <key>
make link-check
```

Report: the chapter, then per note the verdicts and a line on what changed, the figures
added, and anything dropped and why. List every **contradicts** first. Do not commit. The
user reviews the diff.
