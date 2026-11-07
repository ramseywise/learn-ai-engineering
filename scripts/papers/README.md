# Readings ledger and inbox

This folder holds the tooling (`potw.py`, `figures.py`) and the **index of every reading in
the repo**. It is not a library: PDFs live in their home's `sources/`. It covers all subjects.

| Path | What it is |
|---|---|
| `ledger.jsonl` | One row per reading, repo-wide: DAIR AI Papers of the Week (2023 onward) and every PDF found in the repo. The single source of truth for what we have, where it lives, and whether it has been worked into the notes. |
| `blurbs/<year>.jsonl` | A summary per ledger row, used only as triage input. The DAIR summary for papers, the first-page text for PDFs. Split by year to stay under the pre-commit size limit. |
| `inbox/` | Drop a new PDF here. `route` moves it to its home's `sources/` once triage gives it one. |
| `extractions/<key>.json` | What each PDF says, recorded when it is read: question, hypothesis, method in numbers, results, limits, lineage. See *Extractions* below. |
| `extraction-template.json` | The schema the source-reader fills. |

A PDF does not stay here. Once triage gives it a home, `route` moves it into that home's
`sources/` folder, where the notes that use it live.

## Homes

Each reading gets one *home*: the folder whose notes it feeds. The map is `HOMES` in
[`scripts/papers/potw.py`](potw.py).

| Home key | Folder |
|---|---|
| prompt, context, harness, loop, graph, eval, inference, multimodal, safety | `ai-engineering/01`–`09` |
| llm-fundamentals, rag, agents, frameworks, post-training, observability, agentic-apps | `generative-ai/01`–`07` |
| analytics | `data-analytics/sources/` |
| classical-ml | `data-science/sources/` |
| data-systems, ml-systems | `data-engineering/sources/` (two keys, one folder) |
| programming | `programming/sources/` |

The last five are the *subject homes* (`SUBJECT_HOMES` in potw.py). Their readings are mostly
books and classic papers that predate DAIR, so they come in through `discover.py` (below), not
the weekly fetch.

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

## Integration order

`relevance` barely separates downloaded papers, so `potw.py tier` ranks each PDF ready for
`/papers` from its citation-graph role, review status and citations (`TIERS` in potw.py): primary,
landmark, solid, too new to tell, low signal, then surveys and benchmarks. The nightly run works
through every home's tier 1, then ready book chapters one per session (`chapter_tier`: book in progress, filed, new
book), then every home's tier 2, and recomputes tiers when it starts. It stops when a session reports a usage limit.
Run `tier` yourself after `citegraph.py status --write`, which fills in the role and review status.

Only `sources/<book-slug>/chNN-*.pdf` counts as a `/chapter` chapter. Flat `<book>-chNN-*.pdf` files go through `/papers`.

## Ledger checks

`make ledger-check` (part of `make test`) fails on a bad `note` path, an unknown home, a PDF under `sources/` with no
row, an integrated row nothing cites, or two rows sharing a DOI or arXiv id. `make ledger-report` also lists what has a
backlog: integrated rows with no `references.md` row, rows cited only outside their home, a `note` that does not cite
its row, and duplicate titles. Duplicates merge by marking the loser `skipped` with `merged_into`, never by deleting.

`potw.py mark integrated` uses the same search, so it refuses a key its home does not cite (`--no-citation "<why>"` for
an exception) and sets `note` to the citing file. `potw.py scan --offline` registers new PDFs without calling arXiv.

## Extractions

Every PDF the pipeline reads leaves `extractions/<key>.json` (the name comes from `extract.py path <key>`). The
`source-reader` agent writes it during `/papers`, `/chapter` and `/extract`, from the template in
`extraction-template.json`:

- **question**, **hypothesis** and **contributions**.
- **method**, in numbers: datasets with sizes and splits, models with parameter counts and what they start from, the
  training recipe (objective, optimizer, learning rate and schedule, batch size, steps, sequence length, precision,
  hardware, compute, seeds), inference settings, and each eval metric with its definition and unit. A value the source
  does not give is `null`. The nulls are the point: they show what a paper leaves out. Work that trains nothing sets
  `trains: false` and records what a rerun needs instead: samples or runs, the method's own parameters, and the
  verbatim prompts.
- **results**, one number each, with its setup and a verbatim quote or a table reference whose number must occur in
  the text; **limits**; **lineage**, the earlier work it extends, replicates, contradicts, evaluates, uses as a
  baseline or takes data from.

The ledger does not record extraction state; the file and its `schema` do. `schema: 1` is a full extraction.
`schema: 0` is an older source-reader text report recovered from session transcripts by `extract.py salvage`
(2026-11-07: 768 readings). It has claims, limits and builds-on but no method block, so `/extract` still reads that PDF;
the old report is the reader's map.

```bash
uv run -q --with pymupdf --with pypdf python scripts/papers/extract.py text <key>   # cached text + section/table offsets
uv run -q --with pymupdf --with pypdf python scripts/papers/extract.py check <key>  # schema, quotes, method numbers vs the PDF
python3 scripts/papers/extract.py status                                          # coverage per home (make extract-status)
python3 scripts/papers/extract.py next --n 10                                     # the backlog, best first
python3 scripts/papers/extract.py report                                          # reports/lineage.md, reports/reproducible.md
```

`check` fails on a missing field, a result quote not found in the PDF text, or a file whose name does not match its
key. It warns on a method number that does not occur in the text: derived or misread. `make test` runs the schema part
on every file. `reports/lineage.md` lists each paper's relations and every recorded disagreement;
`reports/reproducible.md` scores each empirical paper 0 to 3 on how much of a rerun it states, with what is missing.
Training work is scored on the 11 training fields, work with `trains: false` on 8 rerun fields.
The PDF text cache, `.textcache/`, is gitignored.

The backlog is filled by `/extract` (reads and records, never edits notes) and by the nightly run's last pass.
`check_ledger.py` reports `no-extraction` (information only) until it is cleared; then it becomes gated and
`mark integrated` refuses a reading without one. Today `mark integrated` warns.

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
python3 scripts/papers/potw.py tier                       # rank the PDFs ready for /papers
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

## Discovery for the subject homes

The citation graph grows outward from papers we already hold, so a home that holds few gets
little from it. [`discover.py`](discover.py) searches by topic instead.

1. `queries` writes `discover/queries-<home>.json`, a few search queries per note. You edit that file first.
2. `search` runs each query through OpenAlex semantic search and adds the well-cited works the ledger lacks as `new` rows.
   `curated` resolves the hand-picked list in `discover/curated.jsonl` by title.
3. `potw.py triage --home <home>` scores them as usual.
4. `review` writes `discover/review-<home>.md`, one table per note. Mark keep and role, then `--apply`.

OpenAlex without a key gives each IP a small free daily budget (about 100 semantic searches);
set `OPENALEX_API_KEY` for more. Every response is cached in `discover/cache/` (gitignored).

```bash
python3 scripts/papers/discover.py search --home analytics data-systems ml-systems classical-ml programming
python3 scripts/papers/discover.py curated
python3 scripts/papers/potw.py triage --home analytics
python3 scripts/papers/discover.py review --home analytics            # then edit, then --apply
python3 scripts/papers/citegraph.py fetch --subject --include-queued  # graph for the subject homes
python3 scripts/papers/citegraph.py bridges                           # works both sides cite
```

## Citation graph

`citegraph.py` builds a graph of what our papers cite, so we can see where ideas come from and
cite the peer-reviewed version.

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
- Each `references.md` gets a generated **Where the ideas come from** table (`refs --write`). It is a reading list, not
  citations: its last column says read, held and unread, or not held. The block never counts as a citation in
  `check_ledger.py` or as a seed for the graph.
- `--subject` limits any command to the five subject homes. `fetch --include-queued` also
  seeds from queued rows, which those homes need while they hold few PDFs. A home seeded that
  way is marked *provisional* in its report.
- `bridges` writes [reports/bridges.md](reports/bridges.md): readings found for both a subject
  home and an AI home, and works cited from both sides.
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
| `/extract` | Backfill: one checked extraction per PDF read before extractions existed. Never edits notes. |
| `/pillar` | Bring a pillar folder to the standard layout (`notes/`, `sources/`, `references.md`). |
| `/slides` | One pillar's notes into a lecture deck, kept as `.pptx` and `.pdf`. |
| `/weekly` | Report only: tests, reviewer decisions, signals, backlog, stale decks. Changes no content. |

The standard layout every skill writes to is in [pillar-layout.md](../../.claude/skills/pillar/references/pillar-layout.md).

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
