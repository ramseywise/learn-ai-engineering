# Readings inbox

This folder is the **index and inbox for every reading in the repo**, not a library. It
lives under `ai-engineering/` only because the tooling points here. It covers all subjects.

| Path | What it is |
|---|---|
| `ledger.jsonl` | One row per reading, repo-wide: DAIR AI Papers of the Week (2023 onward) and every PDF found in the repo. The single source of truth for what we have, where it lives, and whether it has been worked into the notes. |
| `blurbs/<year>.jsonl` | A summary per ledger row, used only as triage input. The DAIR summary for papers, the first-page text for PDFs. Split by year to stay under the pre-commit size limit. |
| `general/`, `ai_engineering/` | PDFs still waiting to be routed. These folders should empty out. |

A PDF does not stay here. Once triage gives it a home, `route` moves it into that home's
`sources/` folder, where the notes that use it live.

## Homes

Each reading gets one *home*: the folder whose notes it feeds. The map is `HOMES` in
[`scripts/papers/potw.py`](../../scripts/papers/potw.py).

| Home key | Folder |
|---|---|
| prompt, context, harness, loop, graph, eval, inference | `ai-engineering/01`–`07` |
| llm-fundamentals, rag, agents, frameworks, post-training, observability, agentic-apps | `generative-ai/01`–`07` |
| classical-ml | `data-science/readings/` |
| ml-systems | `data-engineering/readings/` |

Topics with no home (mechanistic interpretability, safety research, robotics and other
multimodal work, domain applications) are kept in the ledger as `skipped` and never routed.

## Status lifecycle

```
new ──triage──▶ queued ──download / route──▶ downloaded ──/papers or /chapter──▶ integrated
          └───▶ skipped (no home, or a DAIR paper below relevance 2)
```

## Commands

```bash
make papers-status                                        # counts, and how many PDFs are left in this inbox
python3 scripts/papers/potw.py route                      # dry run: where each triaged PDF would go
python3 scripts/papers/potw.py route --apply              # move them (git mv) and drop duplicate copies
python3 scripts/papers/potw.py triage --status skipped --source repo   # re-triage after HOMES changes
make papers                                               # weekly: fetch DAIR, triage, download
```

## Skills

| Skill | Unit of work |
|---|---|
| `/readings` | Work the inbox: status, route, and pick what to integrate next. |
| `/chapter` | One book chapter into the notes of its home: prose, code and figures. |
| `/papers` | One paper into a `references.md` row and a sentence or paragraph in a note. |
| `/pillar` | Bring a pillar folder to the standard layout (`notes/`, `sources/`, `references.md`). |
| `/slides` | One pillar's notes into a lecture deck, kept as `.pptx` and `.pdf`. |

The standard layout every skill writes to is in [PILLAR-LAYOUT.md](../PILLAR-LAYOUT.md).

## Adding a reading

Drop the PDF anywhere in this folder, then run `make papers` (or
`python3 scripts/papers/potw.py scan --deep` followed by `triage --source repo`). Then
`route --apply`. If triage finds a body of readings with no home, that is the signal to
discuss a new pillar, as happened with `07-inference-engineering` on 2026-10-31.
