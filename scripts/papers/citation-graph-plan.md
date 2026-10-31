# Plan — citation graph, peer-review status, idea origins

Status: 2026-10-31. Steps 1–3 are built as [`citegraph.py`](citegraph.py) and have run on the RAG pillar
(report: [reports/citegraph-rag.md](reports/citegraph-rag.md)). See "Decisions after the RAG test" at the end.

## Why

The ledger tracks the PDFs we hold. It does not track what those papers cite. Most of the
repo's sources are arXiv preprints, so two gaps follow:

1. **Peer review.** ~290 arXiv ids are cited in notes (plus ~340 more in the ledger as
   integrated, filed or downloaded). We don't record which ones were later accepted at a
   venue, which were rejected, and which are only preprints or vendor tech reports.
   `confidence: high` in frontmatter currently says nothing about review.
2. **Origins.** Notes cite the paper we read, not the paper the idea came from. Nothing
   records lineage (some notes use the word "lineage" about 12 times, by hand). A 2026 preprint
   that "introduces" a technique is often restating something from a 2019 NeurIPS paper
   that all our papers cite.

## What we build

### 1. Seed set

Every paper the notes cite (arXiv ids grepped from `*.md`) plus ledger rows with status
`integrated | filed | downloaded`. About 500 unique papers. Queued rows stay out until they
are read. If we didn't do that, 1,081 unread papers would skew the counts.

### 2. Fetch references from APIs, not from PDFs

Parsing reference sections out of PDFs (GROBID and similar tools) is noisy. The APIs
already have clean, de-duplicated reference lists:

| Source | What it gives us |
|---|---|
| **Semantic Scholar** `/paper/batch` (already used by `potw.py cite`) | `references` with `externalIds`, `year`, `venue`, `publicationVenue`, `publicationTypes`, `journal`, `openAccessPdf`; per-edge `isInfluential`, `intents` (methodology / background / result) and `contexts` (the citing sentence) |
| **OpenAlex** | `referenced_works`; `locations[]` with `version` (submitted vs published) and `source.type` (journal / conference / repository). It merges an arXiv preprint with its published version, which S2 sometimes misses |
| **DBLP** | Ground truth for CS venues: decides ties when S2 and OpenAlex disagree |
| **OpenReview** | Accept or reject decision for ICLR, TMLR and NeurIPS papers. A paper that has an OpenReview page was not necessarily accepted |

Papers with no arXiv id (books, sha1-only rows) look up by DOI or by title search. If neither
matches, they stay in the graph without outgoing edges.

Get a free S2 API key first. The keyless pool is shared and returns 429 often (see `potw.py` line 512).

### 3. Storage: SQLite, not a graph server

At this size (~500 seeds × ~40 references ≈ 20k edges, ~12k nodes) Neo4j only adds a
server to run. Use one SQLite file, `scripts/papers/citations.db` (gitignored, rebuilt
by the script), queried with recursive CTEs. Export GraphML for Gephi, or build a static
HTML view.

```
paper(id, doi, arxiv, s2_id, openalex_id, title, year, venue, venue_type,
      review_status, oa_pdf_url, global_citations, in_repo, ledger_key)
author(id, name, openalex_id)          venue(id, name, kind, archival)
cites(src, dst, influential, intents, context)
authored(paper, author, position)       published_in(paper, venue, year)
same_work(preprint, published)          -- arXiv ↔ proceedings version
note_cites(note_path, paper)            -- our notes are nodes too
```

`note_cites` is the edge that matters most for us. It answers "which notes stand only on
preprints?"

### 4. Review status: one field, five values

`review_status ∈ {peer-reviewed, workshop, preprint, tech-report, book}`

- **peer-reviewed**: a journal, or the main track of an archival conference on an allowlist kept
  in the repo (NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, TACL, JMLR, TMLR, AAAI, IJCAI, KDD,
  SIGIR, WWW, CVPR, ICCV, ECCV, COLM, USENIX Security, IEEE S&P, CCS…).
- **workshop**: a NeurIPS or ICML workshop paper. S2 often labels these plain "NeurIPS", so check DBLP.
- **tech-report**: model cards and system reports from labs (GPT-4, Llama, Claude). They are primary
  sources but not reviewed.
- `review_overrides.jsonl` holds manual corrections, keyed by paper id.

Write the status back to the ledger (`venue`, `review_status`), so `/readings` can show it.

### 5. Metrics that find origins

- **Local in-degree**: how many of *our* papers cite X. This is the "what is everyone
  citing" number, and it is different from global citation count.
- **Methodology in-degree**: count only edges whose S2 `intents` include `methodology`.
  An idea's source gets methodology citations, while surveys and benchmarks get background
  citations.
- **Reference Publication Year Spectroscopy (RPYS)** (Marx et al., 2014) applied per pillar:
  peaks in the year distribution of cited references mark the historical roots of a field.
- **Co-citation clusters**: papers our corpus cites together form idea families. Name each
  cluster after its earliest high-in-degree member.
- **Origin candidate** for a concept is the earliest paper in its cluster with high methodology
  in-degree, confirmed by reading it. The metric proposes, a human (or `/papers`) confirms.

### 6. Outputs (`python3 scripts/papers/citegraph.py <cmd>`)

| Command | Output |
|---|---|
| `fetch` | Fills `citations.db` from S2, then OpenAlex, then DBLP; resumable and cached like `potw.py cite` |
| `status` | Review status for every seed; writes `venue` and `review_status` to the ledger |
| `roots [--pillar rag]` | Ranked "most cited by our corpus" list, with RPYS peaks and origin candidates |
| `acquire` | **The peer-reviewed reading list**: peer-reviewed works with local in-degree ≥ 3 that we don't hold, plus the open-access PDF URL (ACL Anthology, PMLR, NeurIPS proceedings, OpenAlex `best_oa_location`). Appends ledger rows `source: citegraph, status: queued` |
| `upgrade` | Cited arXiv ids that have a published version: a list of citations to rewrite as "(Wei et al., NeurIPS 2022)" with the proceedings link |
| `exposure` | Notes ranked by the share of their citations that are preprint-only |
| `export` | GraphML, and a JSON file for an HTML view |

## Changes to note-taking

We don't track origins today. Proposed conventions:

1. **Cite the origin and the paper we read.** When a note states an idea, it names
   where the idea came from and then the recent work: "Self-consistency (Wang et al., ICLR 2023),
   extended to agents by X (preprint, 2026-09)". This follows the existing rule to cite even
   when a point is already covered.
2. **Show venue in citations.** Inline: `(Wei et al., NeurIPS 2022)` or
   `(Fu et al., 2026-10, preprint)`. In references.md tables, add the venue to the source
   cell, and mark preprint-only rows with ⚑.
3. **Add a lineage section to each references.md.** A short table: concept → origin paper (venue,
   year) → key follow-ups → notes. It is generated from `roots` output, then edited by hand.
4. **Tie `confidence` to evidence.** A note whose central claims rest only on
   preprints can't be `confidence: high` without a stated reason.
5. **Skill updates.** `/papers` gets a "trace the origin" step: before writing a
   finding, look at the paper's methodology-intent references in `citations.db`; if the idea
   is older, cite the origin too and queue it if we don't hold it. `/readings` shows
   review status and the `acquire` queue.

## Order of work

1. **Spike (one pillar, about half a day).** Run `fetch` and `status` on `generative-ai/02-rag-retrieval`
   only. Hand-check 30 review statuses against DBLP and OpenReview to measure how accurate the
   classifier is before trusting it. If S2 venue strings turn out too unreliable, make
   OpenAlex and DBLP primary.
2. **Full fetch, then status write-back to the ledger.**
3. **`roots` and `acquire`.** Review the top ~50 acquisition candidates by hand, then run
   `/readings route` for the ones we keep.
4. **Conventions.** Update `PILLAR-LAYOUT.md` with the venue and lineage sections, and update the
   `/papers` and `/pillar` skills.
5. **Backfill.** Run `upgrade` and `exposure`, then fix the notes with the highest
   preprint share first, one pillar per pass.
6. **Optional:** an HTML view of the graph (pillar-coloured nodes, sized by local in-degree).

## Known limits

- S2 and OpenAlex reference lists miss some entries, especially for recent papers.
  Counts are lower bounds.
- Peer review is evidence, not proof. Some heavily cited preprints (e.g. vendor reports)
  are the actual primary source. The goal is to label sources honestly, not to exclude them.
- Venue allowlists are judgment calls. Keep the list in the repo so it can be challenged.

## Decisions after the RAG test (2026-10-31)

- **OpenAlex is the primary source, not Semantic Scholar.** There is no API key wait, and
  keyless use allows 1,000 requests a day. OpenAlex often keeps an arXiv preprint and its
  proceedings version as two works (RAG, NeurIPS 2020, shows only arXiv copies), so its venue
  data alone mislabels about half the papers.
- **DBLP decides peer review, through SPARQL** (`sparql.dblp.org`). The search API is behind a
  bot wall. The first pass matches by DOI and exact title. A second pass matches titles
  lowercased with punctuation removed, plus the title without a "Name:" prefix. It catches
  "Attention is All you Need" (NIPS 2017) and REALM (ICML 2020, whose venue title drops "REALM:").
  A DBLP record counts only if its year falls between one year before and three years after
  the work's year.
- **Any non-CoRR DBLP conference or journal record counts as peer-reviewed**, not just records
  on an allowlist. DBLP only indexes reviewed venues. `top_venue` marks the allowlist tier.
- **Hand check:** on 33 sampled labels, all 15 peer-reviewed labels were right, and 17 of 18
  preprint or workshop labels were right. The miss was CLIMATE-FEVER, a NeurIPS 2020 workshop
  paper labelled preprint, because DBLP doesn't index that workshop. Fix such cases in
  `review_overrides.jsonl`.
- **In-repo flag:** `work.in_repo` holds the path of our PDF. It is matched against ledger
  `local_pdf` by arXiv id, by a DOI recovered from the filename (ACL Anthology, ACM) or by
  title. A PDF of either the preprint or the published copy counts.
