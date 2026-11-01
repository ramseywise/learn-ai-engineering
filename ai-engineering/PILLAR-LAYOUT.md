# Pillar layout

The shape every pillar folder converges on, in all five pillared areas: `ai-engineering/`, `generative-ai/`,
`data-analytics/`, `data-science/` and `data-engineering/`. `programming/` keeps its tracks and modules.
The skills (`/chapter`, `/papers`, `/pillar`, `/slides`, `/readings`) read this file and write
to this shape. Pillars 01, 02 and 05 of ai-engineering are the worked examples.

```
<area>/<NN-pillar>/
  README.md
  references.md
  notes/NN-<topic>.md
  practice/                                notebooks, scripts, raw course folders
  sources/
    <author>-<year>-<short-title>.pdf      papers
    <book-slug>/chNN-<chapter-slug>.pdf    book chapters (appendix-<x>-<slug>.pdf for appendices)
    images/<author>-<short-title>-fig<N>.<ext>
  slides/deck.yaml, <topic>.pptx, <topic>.pdf   (.preview/ is gitignored)
```

## README.md

What the discipline is, where it sits in the stack, what it inherits the weaknesses of, the
mental model, rules of thumb, the order to read the notes in, and a link to `references.md`.
The README's groupings of the notes become the deck's parts.

## notes/

The notes are the product. Everything else in the folder serves them.

- **One topic per note**, numbered in reading order. A source never gets its own note
  ("Chapter 6 summary"). Its content is folded into the notes on the topics it covers.
- **Frontmatter**:
  ```yaml
  ---
  origin: synthesis            # synthesis | book-condensed | web-authored | curated
  sources:
    - https://arxiv.org/abs/2506.15841
    - "Huyen, AI Engineering (O'Reilly, 2025), ch. 6"
  confidence: high             # high | medium | low
  cleaned: 2026-10-31
  ---
  ```
- **Prose first**, with claims stated plainly and each number given with the setup it holds
  under ("on SWE-bench Verified", "at 7B").
- **Code** in fenced blocks, short enough to read in place. A runnable lab goes in
  `practice/` or links upstream.
- **Figures** sit next to the claim they support:
  ```markdown
  ![Agentic vs. non-agentic RAG](../sources/images/li-ai-agents-in-depth-fig3-12.svg)
  *Image Source: Li, [AI Agents in Depth](https://...) (2026), Fig. 3-12 (Apache-2.0)*
  ```
  Name the author, title, figure number, and the licence when there is one. A figure goes
  into a note before it goes onto a slide.
- **Inline citations** link the public URL, never the local PDF:
  `[arXiv:2610.28577](https://arxiv.org/abs/2610.28577) (Fu et al., 2026-10)`.
- **Venue in citations.** Say where a paper was reviewed: `(Karpukhin et al., EMNLP 2020)`.
  A paper that is only a preprint keeps the date and says so: `(Fu et al., 2026-10, preprint)`.
  `scripts/papers/citegraph.py upgrade` lists arXiv citations that have a published version.
- **Cite the origin as well as the recent paper.** When a note states an idea that started
  earlier, name the origin first, then the recent work: "dense retrieval (Karpukhin et al.,
  EMNLP 2020), extended to agents by …". The origins for each pillar are in the generated
  "Where the ideas come from" section of its `references.md`.
- **`confidence: high`** needs peer-reviewed evidence for the note's central claims, or a stated
  reason (a primary vendor report, a reproduced result) when they rest on preprints.

## notes/: the chapter

A note is a chapter of a book. Its target is 2,000 to 5,000 words. Under 1,500 is a skeleton and
says so in a `status: skeleton` frontmatter line. Over 7,000 is two chapters. A chapter has these
parts in this order. `make chapter-check PILLAR=<pillar>` checks them.

1. **Hook.** One paragraph before the first H2: the problem this chapter solves and what goes wrong
   without it.
2. **Concepts in prose.** One H2 per concept, each with a worked example in code that runs as
   written. Numbers come with their setup.
3. **At least one figure or diagram.** A paper figure from `sources/images/`, a Mermaid block, or
   an ASCII diagram in a `text` fence written for the note.
4. **`## Pitfalls`.** What practitioners get wrong, with the symptom.
5. **`## Try it`.** Two to four exercises with answers in a `<details>` block or linked to `practice/`.
6. **`## Interview checklist`.** A table of questions with the answers filled in.
7. **`## Next`.** The link to the following note, or to the next pillar on the last note.

Programming modules are exercise-driven at 300 to 600 words and are exempt from this section.

## references.md

Frontmatter (`origin: curated`, `sources:`, `confidence:`, `cleaned:`), then tables in this
order: **Books**, **Core papers**, **AI Papers of the Week**, **Courses and videos**.
Courses and videos are linked, never vendored, and each row gives the platform, free or paid, the
notes it supports, and which weeks or playlists to watch. Each row says why to read it,
links the local PDF, and maps to the notes that use it. **★** marks a reading that changed a
claim. The local PDF is linked from here and nowhere else.

Between `<!-- citegraph:origins start -->` and `<!-- citegraph:origins end -->` sits a
generated **Where the ideas come from** table: works that at least 3 of the pillar's papers cite,
at least 2 of them for the method, with venue, those counts, and whether we hold the PDF.
`python3 scripts/papers/citegraph.py refs --write` regenerates it; don't edit inside the markers.
Mark preprint-only rows in the hand-written tables with ⚑.

```markdown
| Book | Chapters | PDF | Maps to |
| Huyen, *AI Engineering* (O'Reilly, 2025) | ch. 6 RAG and Agents | [ch06](sources/huyen-ai-engineering/ch06-rag-agents.pdf) | [04](notes/04-retrieval.md#...) · [10](notes/10-tools-and-multi-agent.md) |
```

## sources/

- Every PDF lives in exactly one `sources/` folder, the one belonging to its home in the
  readings ledger. Duplicates are deleted.
- `scripts/papers/potw.py route` and `download` name the files. Don't rename by hand, or
  rerun `potw.py scan` afterwards so the ledger follows.
- Images sit flat in `sources/images/`. Subfolders there are leftovers from imports, and
  [image-assessment.md](image-assessment.md) tracks them.

## slides/

Built by `/slides` from `deck.yaml`. Never hand-edit the `.pptx`. The `.pdf` is committed once
per finished revision.

## Subject areas

`data-analytics/`, `data-science/` and `data-engineering/` are pillared like the others, with one
difference: their PDFs and images stay in one shared `<subject>/sources/` at the subject root. Their
books span several pillars and the readings ledger homes them by subject. So a note links figures as
`../../sources/images/<file>`, and `<subject>/references.md` holds the books shared across pillars
while each pillar's `references.md` maps its own notes. `<subject>/CURRICULUM.md` is the sequenced
path across the pillars.
