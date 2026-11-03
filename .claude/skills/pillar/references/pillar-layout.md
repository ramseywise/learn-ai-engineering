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
mental model, rules of thumb, the order to read the notes in, its **Primary texts**, and a link to
`references.md`. The README's groupings of the notes become the deck's parts. The reading order is
the only chapter list in the repository: a subject syllabus never lists chapters or counts them.

**Primary texts.** A short section naming the books and sources the pillar is built on, each taken
from a `references.md` row and never from memory, ending with a link to `references.md` for the rest.

**Builds on and feeds into.** Every pillar README has two tables under one
`## Builds on and feeds into` heading, placed after the reading order. **Builds on** lists the earlier
chapters in other subjects the pillar assumes, with one line on why. **Feeds into** lists the later
chapters that use it. List only chapters that exist; a table with nothing to list says so in one row. In ai-engineering and generative-ai, a Builds on row from data analytics, data science or data engineering starts its reason with `Optional background:`, since Path D does not require those subjects first.
`scripts/check_chapters.py` warns when a README has neither table. Links at chapter level go inline
in the note, where the concept is first used:

```markdown
see [chapter](path) in data analytics for the derivation
```

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
  `[arXiv:2610.28577](https://arxiv.org/abs/2610.28577) (Fu et al., 2026-10, preprint)`.
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

Python, SQL and TypeScript modules under `programming/` are exercise-driven at 300 to 600 words and are exempt from the length and shape above. TypeScript 01-09 and the SQL capstone still need three of the sections, in chapter order: `## Pitfalls`, `## Try it` where the note names a lab under `practice/`, and `## Next`. `scripts/check_chapters.py` gates that subset in `make test`. New `programming/` chapters and tracks, such as `software-design/` and Python 03/08 and 03/09, follow the full standard.

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
- Images sit flat in `sources/images/`. Subfolders there are leftovers from imports.

## slides/

Built by `/slides` from `deck.yaml`. Never hand-edit the `.pptx`. The `.pdf` is committed once
per finished revision.

## Subject areas

`data-analytics/`, `data-science/` and `data-engineering/` are pillared like the others, with one
difference: their PDFs and images stay in one shared `<subject>/sources/` at the subject root. Their
books span several pillars and the readings ledger homes them by subject. So a note links figures as
`../../sources/images/<file>`, and `<subject>/references.md` holds the books shared across pillars
while each pillar's `references.md` maps its own notes.

## Which file does which job

| File | Job |
|---|---|
| `README.md` (root) | Landing page |
| `CURRICULUM.md` (root) | The program: outcomes, role map, paths, portfolio standard |
| `<subject>/README.md` | The syllabus: outcomes, prerequisites, units with objectives and evidence, rules of thumb, Primary texts. No chapter lists or counts |
| `<subject>/<NN-pillar>/README.md` | The unit: mental model, reading order, builds on and feeds into, labs, Primary texts |
| `references.md` | The full ledger, machine-maintained. `citegraph.py` writes its generated block, `/papers` and `/chapter` append rows |
| `THIRD_PARTY.md` (root) | What was copied in, its upstream and its licence |

## Definition of done

A pillar is **done** when all five hold:

1. **README**: what the pillar teaches, the order to read it in, prerequisites.
2. **Condensed**: no vendored snapshot left inside it. Upstream courses are synthesised into
   `notes/` with sources cited (note frontmatter or a `references.md`), then the snapshot is
   deleted and its row moves to [Removed snapshots](../../../../THIRD_PARTY.md#removed-snapshots).
3. **Runnable or labelled**: each notebook or practice lab runs offline, or says what it
   needs (API key, GPU, service).
4. **Imports cleanly**: `make import-courses` in librarian brings it in with no broken
   relative links.
5. **Cross-linked**: points to the [interviewing role map](../../../../practice/interviewing/README.md) that maps its checklists and, once they exist, to the
   drills that practise it (drills name their `concepts`).

### Status

Every pillar has a README, `references.md`, `notes/` written as chapters, `slides/` (deck.yaml, .pptx,
.pdf) and `practice/`. `data-analytics`, `data-science` and `data-engineering` share a subject-level
`sources/`.

| Subject | Left to do |
|---|---|
| ai-engineering | Labs run in TypeScript and Python on a stub and a local fake server, not yet against a live API |
| generative-ai | Illustrative code in some chapters not run |
| data-analytics | Several visualisation and credit books cited but not read in full |
| data-engineering | Cloud and cluster code illustrative; zoomcamps not re-run |
| data-science | See its [known gaps](../../../../data-science/README.md#known-gaps) |
| programming | None |

Remaining across subjects: run every notebook offline or label it (check 3), and tag drills with
`concepts` (check 5). `make chapter-check PILLAR=<path>` checks the chapters.

## Structure decisions

The curriculum is **structurally frozen** as of 2026-10-28: the six subjects and their pillars are the
full set. New material goes into an existing pillar; a new top-level folder or pillar needs a reason
written here first. The freeze is relaxed in one direction only: a new pillar is added when the
readings triage finds a body of sources with no home.

**Decision 2026-11-02: LLMs from scratch moves to generative-ai as pillar 09.** It was filed as a
second pillar 04 beside agentic frameworks, so it takes the next free number and reads after 01 LLM
fundamentals. data-science keeps its folder numbers, with 04 as a gap.

**Decision 2026-11-02: evaluation moves to generative-ai.** `ai-engineering/06-eval` is now
[`generative-ai/08-eval`](../../../../generative-ai/08-eval/README.md), its own pillar beside
[06-observability](../../../../generative-ai/06-observability/README.md). The ledger home key stays
`eval`. ai-engineering keeps its other pillar numbers, so it runs 01 to 05, then 07 to 09.

**Decision 2026-11-01: every subject is pillars, and a note is a chapter.** data-analytics,
data-science and data-engineering move from flat `notes/` to `<NN-pillar>/` folders with raw courses
under `practice/`, reversing the flat shape chosen 2026-10-31. Their PDFs stay in one shared
`sources/` per subject, since books span pillars. `programming/python/04-python-for-data` returns to
`data-analytics/01-python-for-data-analysis` with chapters written over the notebooks, reversing part
of the 2026-10-29 decision. Python is the language of the data areas and generative-ai. ai-engineering
labs come in both TypeScript and Python, side by side, so the two can be compared. See the
[deck spec](../../slides/references/deck-spec.md).

**Decision 2026-10-31: `ai-engineering/08-multimodal-engineering/` and
`ai-engineering/09-safety-and-security/` added.** Both were already watch topics in
`scripts/papers/potw.py`: off-syllabus buckets kept "so it is still in the ledger when the pillar
arrives". By 2026-10-31 the ledger held 205 multimodal and 83 safety papers with no home. A
roadmap.sh comparison found the same two gaps: the repo had nothing on image or document input,
multimodal RAG or speech outside one voice-agent note, and its security material was split across
three notes, with no threat modelling, guardrail models or red-teaming tools. Both are cross-cuts,
not layers: each changes all six foundations, so they are read after them. Alignment research
(scheming, alignment faking) and interpretability stay parked. The engineering pillar covers
the application side. Two smaller gaps from the same comparison went into existing homes:
open-weight models and local inference became a planned note in `generative-ai/01`, and LLM
embeddings as features (classification, clustering, anomaly detection) a planned note in
`data-science`.

**Decision 2026-10-31: `ai-engineering/07-inference-engineering/` added as a seventh
ai-engineering pillar.** The readings backlog held a whole book on AI systems performance
(20 chapters plus a checklist), Huyen's inference-optimization chapter and a steady flow of
serving papers. None of the six layers could hold GPU kernels, KV-cache management or
prefill/decode disaggregation without becoming a hardware course, and moving the material
out of the repo would have dropped it. Inference sits under the six layers as their
substrate: it prices every call they make.

**Decision 2026-10-29: `programming/` added as a sixth subject.** Python, SQL and TypeScript
are prerequisites for every other subject, but the repo only had seven pandas notebooks
(`data-analytics/python-basics/`) and no SQL or TypeScript at all. Language fluency doesn't belong in
any one pillar, and drills are practice, not teaching. So `programming/` holds the course (notes,
exercises, solutions), the practice layer holds the drills, and librarian shows both.
`python-basics/` moved to `programming/python/04-python-for-data/` along with the restored
McKinney notebooks and the Michigan/Wesleyan scripts.
