---
name: slides
description: "Build a lecture deck (.pptx) for an ai-engineering pillar from its notes, in the course's house style (the LangGraph deck look). Writes ai-engineering/<pillar>/slides/deck.yaml, renders it with scripts/slides/build_deck.py, previews every slide and fixes overflow. Usage: /slides 02-context-engineering. Run from the learn-ai-engineering repo."
---

You are turning one pillar's notes into a lecture deck. The notes are the source of truth.
The deck is a talk built on them: one idea per slide, with the evidence kept in. It is not
the notes reflowed onto slides.

The rendering is deterministic. You write a YAML spec, and `scripts/slides/build_deck.py`
draws it. Never hand-edit the `.pptx`. Edit the YAML and rebuild.

Read `references/deck-spec.md` before writing the spec. It has the schema, the layout
catalogue, the palette and the writing rules. The worked example is
`ai-engineering/01-prompt-engineering/slides/deck.yaml`.

---

## Step 1 — Pick the pillar

`$ARGUMENTS` names a pillar directory under `ai-engineering/` (`02-context-engineering`, or
just `02`). If it is empty, list the pillars that have `notes/` but no `slides/deck.yaml`,
and pick the first. If `slides/deck.yaml` already exists, you are **revising** it. Read it
first and keep what still matches the notes.

## Step 2 — Read the pillar

- `README.md`. Its groupings of the notes (Foundations / Techniques / …) become the deck's
  **parts**. Its rules of thumb become the wrap-up slide.
- Every file in `notes/`, in order. For each note, write down:
  - the claim it makes
  - the numbers that back the claim
  - any contrast, table, pipeline or ladder it contains
- `sources/images/` (if present). Figures from the papers can go on `image` slides. Images
  sit flat in that folder, named `<first-author-lastname>-<short-title>-fig<N>.<ext>` (e.g.
  `li-ai-agents-in-depth-fig5-4.svg`). A figure the notes don't show yet goes into the note
  first, then onto a slide: the notes are the source of truth.

## Step 3 — Plan

- **Parts.** Mirror the README groupings, usually 3–5 parts. Add a closing part with
  `agenda: false, divider: false` containing a rules-of-thumb `cards` slide and a
  where-next `bullets` slide.
- **Slides.** Plan about 2–4 slides per note, and 30–45 content slides in total. Choose
  each slide's layout from the content's shape (see the writing rules in deck-spec.md).
  Avoid long runs of the same layout.
- **Order.** Follow the notes. Put a pillar's thesis first, as a `statement`.

## Step 4 — Write `ai-engineering/<pillar>/slides/deck.yaml`

- Put a header comment naming the notes the deck covers and the build command.
- Give every content slide `source:` (the note path) and `notes:` (what the speaker says,
  plus the context you cut from the slide).
- Set `output:` to `<topic>.pptx`, e.g. `context-engineering.pptx`.
- Watch the YAML traps listed in deck-spec.md. Quote cells that contain commas. Quote
  strings that start with `*` or `` ` ``.

## Step 5 — Build and look

```bash
make slides PILLAR=<pillar> PREVIEW=1
```

This writes the `.pptx` next to the YAML. With `PREVIEW=1` it also renders every slide to
PNG (macOS Quick Look, a few seconds for the whole deck) plus `sheet-NN.png` contact sheets, 6 slides
per sheet, in `ai-engineering/<pillar>/slides/.preview/`. That folder is gitignored.

1. Fix every `WARN slide N …` line. Each one means text didn't fit even at the minimum size.
   Cut words; don't fight the layout.
2. **Read every contact sheet** with the Read tool. A run with no warnings is not proof the
   slides look right. Check for:
   - text crowding a card edge
   - an orphaned word on its own line
   - a table that is too tall
   - an image that is too small
   - two adjacent slides that look identical
3. Rebuild until the deck is clean. `--strict` (`make slides … STRICT=1`) exits non-zero if
   any warning is left.
4. Add `PDF=1` on the final build. It writes `slides/<topic>.pdf`, one page per slide, which
   opens in a VS Code tab. The pages are images (1600 px, JPEG), with no speaker notes. The
   PDF is **committed** alongside the `.pptx`, at about 5 MB per deck. The size hook skips
   `.pdf`, but every rebuild adds a copy to history, so regenerate it once per finished
   revision, not on every iteration.
5. Check the size: `ls -la ai-engineering/<pillar>/slides/*.pptx`. **Keep the `.pptx` under
   1000 KB.** The pre-commit hook `check-added-large-files --maxkb=1000` rejects anything
   bigger, and the decks so far are 270–860 KB. The builder already shrinks every image to
   about 220 dpi at its size on the slide, and stores it as JPEG when that is smaller, so
   the original images can stay as they are. If a deck still goes over, the cause is too
   many image slides. Cut the weakest ones, or split the pillar into two decks. Don't raise
   the hook limit.

## Step 6 — Wire it in

- In the pillar README, add a line pointing to `slides/<topic>.pptx` and `slides/deck.yaml`
  in the Layout or Start-here section.
- Run `make link-check`.

## Step 7 — Stage, don't commit

`git add` the YAML, the `.pptx`, the `.pdf` and the README change, and nothing in `.preview/`. Show
`git status` and `git diff --staged --stat`, and suggest a commit message such as
`docs(<pillar>): lecture deck from notes`. Don't commit.

## When the builder is the problem

If a layout can't express the content, or renders it badly, fix `scripts/slides/build_deck.py`.
Don't contort the content to fit. Keep layouts generic, since every pillar uses them.
Document any new layout or key in `references/deck-spec.md`. Rebuild
`01-prompt-engineering` afterwards to check that the change didn't break the existing deck.
