---
name: papers
description: "Integrate downloaded AI Papers of the Week into the course: read each PDF in a pillar's sources/, add a row to that pillar's references.md, and write the finding into the note it maps to. Optional filter: /papers loop, /papers 2610.28577. Run from the learn-ai-engineering repo."
---

You are integrating research papers into the AI-engineering course notes. The weekly job
(`scripts/papers/potw.py run`, launchd `com.wiseer.potw`) has already fetched DAIR's AI
Papers of the Week, triaged each paper to a pillar and note, and downloaded the PDF into
`ai-engineering/<pillar>/sources/`. Your job is the part that needs judgement: turn the
paper into citations and findings in the notes.

The notes are the product. A paper earns a place by changing, sharpening, or evidencing a
claim a note makes. It never earns a "Recent papers" list bolted onto the end.

---

## Step 1 — Pick the papers

```bash
python3 scripts/papers/potw.py status --list downloaded
```

Each line is JSON: `key`, `title`, `pillar`, `note` (path under `ai-engineering/`),
`relevance`, `pdf`, `reason`, `url`. Filter by `$ARGUMENTS` if given: a pillar name
(`loop`), or one or more arXiv ids. If nothing is downloaded, say so and suggest
`make papers`. Work one pillar at a time.

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
   - **sharpens** — the note already says this; add the evidence (number + citation)
   - **extends** — a new point the section is missing; add a short paragraph
   - **contradicts** — the note's claim is wrong or over-stated; fix the claim, keep the
     old view only if it's still the common belief, and flag it to the user
   - **doesn't hold up** — on reading, it's weaker or off-topic. Run
     `python3 scripts/papers/potw.py mark skipped <key>`, leave the PDF in place, and
     list it in the report so the user can delete it

## Step 3 — references.md

Each pillar has (or gets) `ai-engineering/<pillar>/references.md`. If missing, create it
in the shape of `02-context-engineering/references.md`: frontmatter
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

## Step 5 — Close out

```bash
python3 scripts/papers/potw.py mark integrated <key> [<key> ...]
make link-check
```

Report, per paper: verdict (sharpens / extends / contradicts / skipped), the note and
section changed, and one line on what changed. Call out every **contradicts** first.
Don't commit — the user reviews the diff.
