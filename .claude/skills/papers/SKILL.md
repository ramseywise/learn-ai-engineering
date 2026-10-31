---
name: papers
description: "Integrate queued or downloaded papers (DAIR AI Papers of the Week and PDFs already in the repo) into the course: read each PDF in its home's sources/, add a row to that home's references.md, write the finding into the note it maps to, and pull the key figure into sources/images/. Works for ai-engineering and generative-ai pillars. Optional filter: /papers loop, /papers rag, /papers 2610.28577, /papers cited (audit papers the notes already cite), /papers filed. Run from the learn-ai-engineering repo."
---

You are integrating research papers into the AI-engineering course notes. The weekly job
(`scripts/papers/potw.py run`, launchd `com.wiseer.potw`) has already fetched DAIR's AI
Papers of the Week, triaged each paper to a home and note, and downloaded the PDF into
the home's `sources/`. PDFs that were already in the repo (the `scripts/readings/`
inbox) are triaged the same way and moved home by `potw.py route`. Homes are the keys of
`HOMES` in `scripts/papers/potw.py`: the six ai-engineering pillars plus `inference`
(`ai-engineering/07-inference-engineering/`), the generative-ai pillars (`rag`, `agents`,
`post-training`, …) and two subject homes, `classical-ml` (`data-science/`) and
`ml-systems` (`data-engineering/`), which have notes like any other home. Book chapters go through `/chapter`, not this skill. Your job is the part that needs judgement: turn the
paper into citations and findings in the notes.

The notes are the product. A paper earns a place by changing, sharpening, or evidencing a
claim a note makes. It never earns a "Recent papers" list bolted onto the end.

---

## Step 1 — Pick the papers

```bash
python3 scripts/papers/potw.py status --list downloaded
python3 scripts/papers/potw.py status --list queued   # repo PDFs: already local, nothing to download
```

Each line is JSON: `key`, `title`, `pillar` (the home key), `note` (repo-relative path, or
null), `relevance`, `pdf` (repo-relative local PDF), `reason`, `url`. Take queued rows only
when `pdf` is set and outside `scripts/readings/`; if a queued PDF still sits in the
inbox, run `python3 scripts/papers/potw.py route --apply` first. Skip rows whose `pdf` is a
book chapter (`sources/<book-slug>/chNN-…`); those belong to `/chapter`. Filter by
`$ARGUMENTS` if given: a home key (`loop`, `rag`), one or more keys / arXiv ids, `cited`
(only rows whose arXiv id already appears in a note: audit these first) or `filed` (audit
`status --list filed` rows). If nothing is ready, say so and suggest `make papers`. Work
one home at a time.

A whole book that isn't split into chapters (a textbook PDF, not `sources/<book-slug>/chNN-…`)
or an exercise handout isn't a paper: run `potw.py mark filed <key>` and list it in the
report. A book becomes integrable once its chapters are split out for `/chapter`.

### Already cited?

Before reading, check whether the notes already cite the paper. The ledger lags: a paper
can be written into a note by an earlier session while its row still says `queued`.

```bash
grep -rn --include='*.md' '<arxiv-id>' ai-engineering generative-ai data-science data-engineering
```

Also grep a distinctive title phrase for rows without an arXiv id. A hit does **not**
mean the paper is integrated: notes often cite a classic from its abstract, without its
numbers or limits. Treat a hit as an audit. Read the citing passages and the
references.md row, then read the paper (Step 2) and check that the note carries its
finding with the number, the setup it holds under, and what it doesn't show. Note every
home that cites it; a paper cited in a second home may need its point made there too.

## Step 2 — Read

For each paper:
1. Extract the PDF text (poppler isn't installed, so the Read tool can't render PDFs):
   ```bash
   uv run -q --with pypdf python -c "import sys,pypdf; r=pypdf.PdfReader(sys.argv[1]); print(len(r.pages),'pages'); print('\n'.join(p.extract_text() for p in r.pages[:int(sys.argv[2])]))" <pdf> 5
   ```
   The first ~5 pages usually cover abstract, setup and results; read the limitations
   section too. Pull out: the claim, the headline numbers, the setup they hold under,
   and what the paper does *not* show.
2. Read the target note in full. Find the section where the claim lives — not just the
   note the triage picked; if a different note or section fits better, use that.
3. Decide, and say which in your report:
   - **verified** — (audit only) the note already carries the finding, with its number and
     setup, cited correctly. Change nothing beyond the frontmatter `sources:` and the
     references.md row if either is missing
   - **sharpens** — the note already says this; add the evidence (number + citation)
   - **extends** — a new point the section is missing; add a short paragraph
   - **contradicts** — the note's claim is wrong or over-stated; fix the claim, keep the
     old view only if it's still the common belief, and flag it to the user
   - **doesn't hold up** — on reading, it's weaker or off-topic. Run
     `python3 scripts/papers/potw.py mark skipped <key>`, leave the PDF in place, and
     list it in the report so the user can delete it

## Step 3 — references.md

Each pillar has (or gets) `<home folder>/references.md` (see
`ai-engineering/PILLAR-LAYOUT.md`). If missing, create it in the shape of
`ai-engineering/02-context-engineering/references.md`: frontmatter
(`origin: curated`, `sources:`, `confidence:`), `# <Pillar> — Papers and Further
Reading`, a one-line intro pointing at `sources/` and the README.

Add the paper to a `## AI Papers of the Week` section (create it after the existing paper
sections), newest first, matching the column shape the file already uses. For the
02-style table:

```
| Fu et al., [*Cache Engineering for Agents*](https://arxiv.org/abs/2610.28577) (Oct 2026) | <the finding, with its number, in one sentence> | [2610.28577](sources/fu-2026-cache-engineering-agents.pdf) | [05](notes/05-compression-compaction.md#<anchor>) |
```

Use **★** only for papers that change a claim (contradicts / strong extends).

## Step 4 — The note

- Write in the note's voice and density. Most integrations are one to three sentences;
  a paragraph is the ceiling unless the paper overturns the section.
- Cite inline the way the notes already do:
  `[arXiv:2610.28577](https://arxiv.org/abs/2610.28577) (Fu et al., 2026-10)` with the
  finding in **bold** where it's the point of the sentence.
- State the number and the condition it holds under ("on SWE-bench-style coding tasks",
  "at 7B"). No number without its setup.
- Add the arXiv URL to the note's frontmatter `sources:` list.
- Link the PDF only from references.md, not from the note body.
- **Figures.** If the paper has one figure that explains the claim better than a sentence
  (an architecture, the headline plot), add it next to the paragraph. Use
  `scripts/papers/figures.py`:
  ```bash
  uv run -q --with pymupdf python scripts/papers/figures.py captions <pdf>
  uv run -q --with pymupdf python scripts/papers/figures.py list <pdf> --pages 1-8
  uv run -q --with pymupdf python scripts/papers/figures.py extract <pdf> --page P --xref X \
      --out <home>/sources/images/<author>-<short-title>-fig<N>.png
  ```
  Use `crop --clip x0,y0,x1,y1` for vector figures (no xref); render the page with `page`
  first and look at it with Read to choose the box. Look at the saved PNG before embedding
  it. Caption it the way the notes already do:
  `*Image Source: <Author>, [<Title>](https://...) (<year>), Fig. <N>*`, plus the licence when there is one.
  At most one figure per paper; none is fine.

## Step 5 — Close out

```bash
python3 scripts/papers/potw.py mark integrated <key> [<key> ...]
make link-check
```

Report, per paper: verdict (verified / sharpens / extends / contradicts / skipped), the note and
section changed, and one line on what changed. Call out every **contradicts** first.
Don't commit — the user reviews the diff.
