# Pillar layout

The shape every pillar folder converges on, in `ai-engineering/` and `generative-ai/` alike.
The skills (`/chapter`, `/papers`, `/pillar`, `/slides`, `/readings`) read this file and write
to this shape. Pillars 01, 02 and 05 of ai-engineering are the worked examples.

```
<area>/<NN-pillar>/
  README.md
  references.md
  notes/NN-<topic>.md
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

## references.md

Frontmatter (`origin: curated`, `sources:`, `confidence:`, `cleaned:`), then tables in this
order: **Books**, **Core papers**, **AI Papers of the Week**. Each row says why to read it,
links the local PDF, and maps to the notes that use it. **★** marks a reading that changed a
claim. The local PDF is linked from here and nowhere else.

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

## Subjects without pillars

`data-science/` and `data-engineering/` are not split into pillars. Readings homed there
(`classical-ml`, `ml-systems`) go in `<subject>/readings/` until those subjects get pillars.
