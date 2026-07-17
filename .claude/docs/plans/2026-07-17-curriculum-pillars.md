# Curriculum Pillars — restructure guides/ into a learner's journey
Date: 2026-07-17
Status: PLANNED

## Research
Basis: direct inspection + the executed consolidation plan
(`2026-07-17-interview-kb-consolidation.md` — F3 parity table, F7 source map, F8 role
matrix). No new research phase: sources and their depth are already mapped there.

**Problem**: `interviewing/guides/` is a flat list of 10 compressed exam-prep summaries.
Ramsey wants a scaffolded curriculum — a folder per pillar with room for detailed notes —
that could guide a beginner ("high-school student learning AI") step by step and point to
every resource: readings PDFs, runnable course code, wiki pages, cleaned notes. It should
also eventually reflect into librarian (`wiki/foundations/` is empty) and seed
ai-project-template design-system skills, and it doubles as the spine of the future
book-syllabus plan (end-to-end projects, nonprofit sector).

## Plan
Date: 2026-07-17
Based on: consolidation plan research + Ramsey's answers (2026-07-17)

### Goal
Turn the flat `interviewing/guides/` into numbered pillar folders, each with a
`00-overview.md` learning path + full resource map; align `readings/` folder names to the
pillars; scaffold only — detailed notes come pillar-by-pillar later.

### Open Questions
1. **Commit checkpoint first?** — Default: **yes** — Ramsey commits the staged Phase B+C
   work before this restructure runs, so the flat→pillar move is its own reviewable
   commit and rollback is trivial. (The alternative — restructure before any commit —
   leaves one big commit with no checkpoint.)
2. **Pillar order (journey order for a beginner).** — Default:
   `1-foundations → 2-llm-fundamentals → 3-rag → 4-agents → 5-context-cost →
   6-evals-observability → 7-security-safety → 8-data-eng-mlops → 9-system-design →
   10-product-delivery`. Deferred topics (stats/experimentation, coding patterns) get
   listed in `00-start-here.md` as "coming" but no folders yet.
3. **What the existing guide file becomes.** — Default: moves into its pillar folder
   unchanged as `interview-guide.md` (the exam-prep view). The new `00-overview.md` is
   the learner-facing entry; future detailed notes land beside them as `01-…`, `02-…`.
4. **readings/ rename mapping** (local-only, gitignored — cheap to rename). Default:
   - `0.rag` → `3-rag`
   - `1.prompt engineering` → `2-llm-fundamentals` (prompting chapters are LLM-era core)
   - `2.knowledge graphs` → `3-rag-knowledge-graphs` (KG-RAG sits in the RAG pillar)
   - `3.reinforcement_learning` → `2-llm-rlhf`
   - `ai_engineering/` → `4-agents-ai-engineering`
   - `data mesh/` → `8-data-eng-data-mesh`
   - `stats_recs/` → `0-cross-stats` (cross-cutting; feeds the deferred stats pillar)
   - `general/` → stays `general/` (classics span pillars; overviews cite exact files)
   RESOLVED 2026-07-17: separate stays separate — readings hold PDFs only, code stays in
   course folders; the curriculum points at both, never copies.

### Approach
Scaffold, don't author: every pillar folder gets a `00-overview.md` that (a) states the
learning path *within* the pillar (read/build order with prerequisites), and (b) maps
every known resource — specific readings PDFs, specific notebooks/course modules,
librarian wiki page titles, `notes/` files, and the pillar's `interview-guide.md` — each
with one line on what it teaches and when to reach for it. Richness comes from precision
of pointers, not from copied content (that's the later per-pillar deepening work). The
trade-off: guides move paths, so every link in `rounds/`, `README.md`, and cross-guide
references must be rewritten in the same step; the librarian scrape glob
(`interviewing/**/*.md`) already covers the new layout.

### Out of Scope
- Writing detailed pillar notes (`01-…` files) — later, pillar-by-pillar.
- Stats/experimentation and coding-patterns pillars (deferred milestones).
- Librarian wiki ingest, ai-project-template skills, the book syllabus — downstream
  consumers, separate plans.
- Any change to `rounds/`, `notes/`, `images/` beyond link-path fixes.

### Steps

#### Step 1: Pillar folders + moves
**Files**: `interviewing/guides/` — create 10 numbered pillar dirs (Open Q2 order);
`git mv` each `<topic>.md` → `<pillar>/interview-guide.md`.
**Test**: `ls -d interviewing/guides/*/ | wc -l` → 10; `ls interviewing/guides/*.md | grep -v 00-start-here | wc -l` → 0.
**Done when**: no flat guide files remain; every pillar dir holds `interview-guide.md`.

#### Step 2: Pillar overviews (the scaffold)
**Files**: `interviewing/guides/<pillar>/00-overview.md` × 10.
**What**: Per pillar: 2–3 sentence "what and why" for a beginner → learning path (ordered:
concept → notebook/course module → reading → wiki page) → resource map table (resource ·
type (pdf/code/wiki/note) · path or page title · one-line "what it teaches") → "then test
yourself" pointer to `interview-guide.md` + relevant `rounds/` file. Resource inventory
comes from the consolidation plan's F7 table + each guide's existing Sources footer.
**Test**: `for d in interviewing/guides/*/; do test -f "$d/00-overview.md" || echo MISSING:$d; done` → empty; every overview greps "Resource map".
**Done when**: 10 overviews, each mapping ≥1 reading + ≥1 code + ≥1 wiki resource (where they exist).

#### Step 3: Journey map
**Files**: `interviewing/guides/00-start-here.md` (new).
**What**: The beginner's route: pillar order with prerequisites and "you can now build X"
milestones per pillar; how the three layers work (overview → detailed notes (coming) →
interview-guide); deferred pillars listed; pointer back to `interviewing/README.md` for
the interview-prep entry point.
**Test**: file exists; links to all 10 pillar overviews resolve.
**Done when**: a newcomer can navigate start-here → pillar → resources without the README.

#### Step 4: Link rewrite
**Files**: `interviewing/README.md` (guide table + matrix links), `interviewing/rounds/*.md`
(all `../guides/<topic>.md` refs), cross-references inside moved guides.
**Test**: extended dead-link loop over README + rounds + guides (every `guides/…​.md` and
`../guides/…​.md` ref resolves); private-scrub grep → 0.
**Done when**: zero dead links repo-wide under `interviewing/`.

#### Step 5: readings/ rename + index
**Files**: `generative-ai/readings/` folder renames (Open Q4 mapping),
`generative-ai/readings/README.md` (index update), pillar overviews' paths (written
against new names in Step 2 — verify).
**Test**: `ls generative-ai/readings/`; grep overviews for old folder names (`0.rag\|1.prompt\|2.knowledge\|3.reinforcement\|stats_recs\|data mesh\|ai_engineering`) → 0 hits.
**Done when**: folder names match pillar numbering; index README reflects them; local-only
invariant intact (`git status` shows only readings/README.md under readings/).

#### Step 6: Re-scrape + final checks
**Files**: none (run only).
**What**: `cd ~/workspace/librarian && uv run python etl/scrape_repos.py` — new pillar
paths land in `raw/repos/learn-ai-engineering/`. Note: previously scraped flat-guide
copies remain in raw/ (append-only, gitignored) — stale but harmless; ingest dedupes by
content.
**Test**: `ls raw/repos/learn-ai-engineering/ | grep "guides--.*00-overview" | wc -l` → 10.
**Done when**: scrape picks up the new layout; learn-ai-engineering staged for Ramsey.

### Test Plan
Per-step checks above; final sweep = consolidation plan's Test Plan (private scrub,
readings tracking check, dead-link loop) over the new layout.

### Risks & Rollback
- **Link churn misses a ref** — mitigated by the Step 4 grep loop over all three surfaces.
- **Staged-work churn** — mitigated by Open Q1 checkpoint commit; rollback = `git reset --hard` to it.
- **readings/ renames break nothing in git** (untracked/ignored) but overview paths must
  match — Step 5 grep guards it.
- All moves are `git mv` on a clean checkpoint; rollback is a single revert.

## Execution Log
