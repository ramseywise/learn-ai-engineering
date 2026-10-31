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
