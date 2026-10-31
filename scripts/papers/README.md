# Readings ledger and inbox

This folder holds the tooling (`potw.py`, `figures.py`) and the **index of every reading in
the repo**. It is not a library: PDFs live in their home's `sources/`. It covers all subjects.

| Path | What it is |
|---|---|
| `ledger.jsonl` | One row per reading, repo-wide: DAIR AI Papers of the Week (2023 onward) and every PDF found in the repo. The single source of truth for what we have, where it lives, and whether it has been worked into the notes. |
| `blurbs/<year>.jsonl` | A summary per ledger row, used only as triage input. The DAIR summary for papers, the first-page text for PDFs. Split by year to stay under the pre-commit size limit. |
| `inbox/` | Drop a new PDF here. `route` moves it to its home's `sources/` once triage gives it one. |

A PDF does not stay here. Once triage gives it a home, `route` moves it into that home's
`sources/` folder, where the notes that use it live.

## Homes

Each reading gets one *home*: the folder whose notes it feeds. The map is `HOMES` in
[`scripts/papers/potw.py`](potw.py).

| Home key | Folder |
|---|---|
| prompt, context, harness, loop, graph, eval, inference, multimodal, safety | `ai-engineering/01`–`09` |
| llm-fundamentals, rag, agents, frameworks, post-training, observability, agentic-apps | `generative-ai/01`–`07` |
| classical-ml | `data-science/sources/` |
| ml-systems | `data-engineering/sources/` |

Topics with no home are kept in the ledger and never routed. Interpretability and alignment
research are *watched*: a notable paper there is `parked`, so it is still waiting when a pillar
for it arrives. Multimodal and safety were watched until 2026-10-31, when they got pillars 08 and 09.
Domain applications, robotics and everything else are `skipped`.

## How triage scores a reading

Haiku gives every reading two scores, 0–3:

- **relevance** is fit to the home: 3 sharpens a claim a note makes, 2 is solid evidence or a
  core reading for the home's scope, 1 fits loosely. A home with few notes yet is judged by its
  scope, so a new pillar is not starved.
- **interest** is how much an AI engineer should know it, whatever the curriculum covers today:
  3 is a landmark, 2 a notable new idea, 1 incremental, 0 not for this audience. Haiku weighs
  the method (new idea or tweak), the results (broad gains or a narrow benchmark) and the
  citation count.
- **citations** come from Semantic Scholar (`potw.py cite`, run weekly by `make papers`). A
  paper cited 300 times a year or more counts as interest 3 whatever the model said. The free
  tier is rate-limited; set `S2_API_KEY` to a free key to lift it. `cite` resumes where it
  stopped.

| Has a home? | Rule | Status |
|---|---|---|
| yes | relevance at or above the floor (2 for DAIR, 1 for a PDF we hold), or interest 3 | `queued` |
| yes | below the floor, interest 2 | `parked` |
| no | interest 3, or interest 2 in a watched topic | `parked` |
| either | anything else | `skipped` |

`parked` and `skipped` are both re-triaged with `triage --status parked` or `--status skipped`,
for example after a pillar gets notes or HOMES changes. `status --list parked` shows the
candidates for a new pillar, with each paper's `reason`.

## Status lifecycle

```
new ──triage──▶ queued ──download (DAIR, arXiv)──▶ downloaded ──/papers──────────▶ integrated
          │        └──route (PDF already in the repo; stays queued)──/papers or /chapter──▶ integrated
          ├───▶ parked (worth knowing, but no home or fit yet; re-triage when a pillar grows)
          └───▶ skipped (not for this course)
```

## Commands

```bash
make papers-status                                        # counts, and how many PDFs are left in inbox/
python3 scripts/papers/potw.py where lewis retrieval-augmented   # where a paper's PDF lives (id, key or title words)
python3 scripts/papers/potw.py route                      # dry run: where each triaged PDF would go
python3 scripts/papers/potw.py route --apply              # move them (git mv) and drop duplicate copies
python3 scripts/papers/potw.py triage --status skipped --source repo   # re-triage after HOMES changes
python3 scripts/papers/potw.py triage --status parked --backlog        # re-triage after a pillar grows
python3 scripts/papers/potw.py status --list parked                    # candidates for a new pillar
python3 scripts/papers/potw.py triage --local --backlog   # DAIR rows whose PDF is already in the repo
python3 scripts/papers/potw.py download --backlog --limit 30          # the 30 best queued papers
python3 scripts/papers/potw.py download --backlog --home multimodal safety  # one or more homes only
make papers                                               # weekly: fetch DAIR, cite, triage, download
```

## Citation graph

`citegraph.py` builds a graph of what our papers cite, so we can see where ideas come from and
cite the peer-reviewed version. Plan and reasoning: [citation-graph-plan.md](citation-graph-plan.md).

- **Seeds** are the papers a home's markdown links (arXiv, DOI, ACL Anthology), every PDF in
  its folder, and its ledger rows marked `integrated`, `filed` or `downloaded`. The status
  table's **In notes** column separates papers a note links from PDFs we only hold.
- **OpenAlex** supplies reference lists, venues and open-access PDF links. **DBLP** (SPARQL)
  decides the peer-reviewed venue. **Semantic Scholar** adds per-citation intents, which mark a
  methodology citation as a sign of where an idea came from.
- **In repo**: every table marks a work we hold with ✓ and its path. The match is by arXiv id,
  DOI or title, against the ledger's `local_pdf`.
- **Get it**: for each peer-reviewed paper we lack, whether a legal free copy exists: the
  OpenAlex/Unpaywall open-access link (ACL Anthology, PMLR, NeurIPS, OpenReview, publisher OA),
  else an arXiv preprint (found by title with `preprints` when OpenAlex has only the
  proceedings record), else "no free copy found" (paywalled).
- The graph is `citations.db` (SQLite, gitignored). Reports go in `reports/`, one per home,
  indexed by [reports/README.md](reports/README.md).
- Fix a wrong review status in `review_overrides.jsonl`.
- **Roles**: a work is *primary* when at least 3 of our papers cite it and at least 2 cite it for
  its method, so an idea most likely starts there. Surveys and benchmarks are labelled by title;
  *new* means too recent to judge; everything else is *secondary*. `status --write` puts `role`
  and `local_citations` on ledger rows. A label, not a folder: PDFs stay in `sources/`.
- **Primary sources** across the corpus are in [reports/primary.md](reports/primary.md):
  `primary --download` fetches the free ones into the pillar that cites them most. The rest
  are listed to fetch by hand: drop the PDF in `downloads/` (gitignored, any file name) and
  run `ingest`, which matches it by title and files it.
- Each `references.md` gets a generated **Where the ideas come from** table (`refs --write`).
- `export --html` writes an interactive graph per pillar, `reports/graph-<home>.html`
  (gitignored; open it in a browser).

```bash
python3 scripts/papers/citegraph.py fetch --home rag      # seeds, OpenAlex works and references
python3 scripts/papers/citegraph.py dblp --home rag       # peer-review status (~1 min per 500 works)
python3 scripts/papers/citegraph.py intents --home rag    # S2 intents; slow without S2_API_KEY
python3 scripts/papers/citegraph.py preprints            # arXiv copies of paywalled reading-list papers
python3 scripts/papers/citegraph.py report --home rag     # reports/citegraph-rag.md
python3 scripts/papers/citegraph.py report --all          # every home, plus reports/README.md
python3 scripts/papers/citegraph.py status --home rag --write   # venue + review_status into the ledger
python3 scripts/papers/citegraph.py acquire --home rag --queue     # queue peer-reviewed papers we lack
python3 scripts/papers/citegraph.py acquire --home rag --download  # fetch the free ones into sources/
python3 scripts/papers/citegraph.py primary --download           # free primary sources; reports/primary.md
uv run --with pypdf python scripts/papers/citegraph.py ingest    # file the PDFs you put in downloads/
python3 scripts/papers/citegraph.py refs --write                 # origins table in every references.md
python3 scripts/papers/citegraph.py export --html                # reports/graph-<home>.html
```

## Skills

| Skill | Unit of work |
|---|---|
| `/readings` | Work the inbox: status, route, and pick what to integrate next. |
| `/chapter` | One book chapter into the notes of its home: prose, code and figures. |
| `/papers` | One paper into a `references.md` row and a sentence or paragraph in a note. |
| `/pillar` | Bring a pillar folder to the standard layout (`notes/`, `sources/`, `references.md`). |
| `/slides` | One pillar's notes into a lecture deck, kept as `.pptx` and `.pdf`. |

The standard layout every skill writes to is in [PILLAR-LAYOUT.md](../../ai-engineering/PILLAR-LAYOUT.md).

## Running sessions side by side

Triage, download and `/papers` or `/chapter` can run at the same time. Triage writes only
the ledger and never moves a file. Download writes PDFs straight into the home's `sources/`.
`/papers` and `/chapter` read from `sources/` and end with `potw.py mark`. Every save takes a
lock on `.ledger.lock`, rereads the ledger and writes only the fields that process changed.
When two processes changed the same field, the one already on disk wins, so a stale
`downloaded` never overwrites a `mark integrated`. Edit the ledger only through `potw.py`.
A hand edit made while a potw.py command is running is kept only if it touches fields that
command doesn't change.

## Adding a reading

Drop the PDF in `inbox/`, then run `make papers` (or
`python3 scripts/papers/potw.py scan --deep` followed by `triage --source repo`). Then
`route --apply`. If triage finds a body of readings with no home, that is the signal to
discuss a new pillar, as happened with `07-inference-engineering` on 2026-10-31.
