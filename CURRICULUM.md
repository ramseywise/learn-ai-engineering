# Curriculum — learn-ai-engineering

A coordinator, not a syllabus. This file maps the subjects, names the prerequisites, and
routes you to the right starting point. Per-subject `CURRICULUM.md` files hold the
sequenced learning paths for each domain.

> **Self-learner?** Start with the [Learning Paths](#learning-paths) section below.
> **Interview prep?** Interview guides and coding drills live in the private
> [sisyphus](https://github.com/ramseywise/sisyphus) repo — start at
> [interviewing/guides/00-start-here.md](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md).

---

## Subject-area map

| Subject | CURRICULUM.md | Prerequisites | Structure |
|---|---|---|---|
| Programming | [programming/CURRICULUM.md](programming/CURRICULUM.md) | None — entry point | Three tracks (Python 01–04, SQL 01–10, TypeScript 01–09), partly in parallel; practice drills live in [sisyphus `drills/`](https://github.com/ramseywise/sisyphus/blob/main/drills/README.md) |
| Data Analytics | [data-analytics/CURRICULUM.md](data-analytics/CURRICULUM.md) | Programming: Python 01–04 | Linear (wrangling → statistics → domain branches) |
| Data Engineering | [data-engineering/CURRICULUM.md](data-engineering/CURRICULUM.md) | Data analytics basics | Linear (pipeline stages) |
| Data Science | [data-science/CURRICULUM.md](data-science/CURRICULUM.md) | Data analytics basics | Tree (statistical foundations splits into supervised / unsupervised / Bayesian) |
| Generative AI | [generative-ai/README.md](generative-ai/README.md) | None required; DS/DE enrich it | 7-pillar sequential (LLM fundamentals → RAG → Agentic foundations → Agentic frameworks → RL → Observability → Agentic applications) |
| AI Engineering | [ai-engineering/README.md](ai-engineering/README.md) | Generative AI Pillar 1 | 6-pillar sequential (prompt → context → harness → loop → graph → eval) |

**Reading the table:** "Prerequisites" are recommendations, not gates. You can start
generative-ai cold — you'll just revisit data-science concepts as they come up rather than
having them in memory already.

---

## Learning Paths

### Path A: AI Engineering (recommended for new AI engineers)

Goal: build reliable, production-grade LLM systems.

1. **Python fluency** — [`programming/python/`](programming/python/README.md) 01–03, then 04 (6–8 weeks)
   Language, engineering idioms (types, async, packaging), then pandas. Add TypeScript 01–09 if
   you'll build in TS. Skip what you already know: each module's exercises double as a placement test.

2. **What LLMs are** — `generative-ai/01-llm-fundamentals/` (3–4 weeks)
   Build a tiny GPT (Karpathy's `nn-zero-to-hero`), read the attention paper,
   understand RLHF and prompting. This is the theory foundation everything else rests on.

3. **Engineering discipline** — `ai-engineering/` pillars 01–06 (4–6 weeks)
   Prompt → context → harness → loop → graph → eval. Six numbered foundations.
   Each has a depth README, a cleaned note, and an interview guide summary.

4. **Build things** — `generative-ai/02-rag-retrieval/` through `07-agentic-applications/` (4–6 weeks)
   The application layer: RAG (the first killer app pattern), agentic foundations and
   frameworks, RL/alignment, observability, then full agentic applications.
   After the ai-engineering discipline, the code patterns will make sense structurally.

Interview guide: start at [interviewing/guides/00-start-here.md](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md),
pillars 0–4 are the core loop for this path.

---

### Path B: Data Engineering

Goal: build data pipelines and ML infrastructure.

1. **Python and SQL fluency** — [`programming/`](programming/README.md): Python 01–04 and SQL 01–10

2. **Data Engineering sequence** — `data-engineering/CURRICULUM.md`
   Ingest → transform → orchestrate → warehouse → monitor → feature-serve.
   Follows the DataTalks modules (Docker, workflow, DWH, batch, streaming) + MLOps track.

3. **Optional depth** — `data-science/CURRICULUM.md` for the ML side of data pipelines
   (feature engineering, model evaluation), or `generative-ai/` for LLM-native pipelines.

Interview guide: [interviewing/guides/8-data-eng-mlops/00-overview.md](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/8-data-eng-mlops/00-overview.md).

---

### Path C: Full-Stack Data

Goal: broad foundation across the full data/AI stack.

1. `programming/CURRICULUM.md` — Python, SQL, TypeScript
2. `data-analytics/CURRICULUM.md` — analytics and statistics basics
3. `data-science/CURRICULUM.md` — classical ML, stats, model evaluation (tree-shaped: go deep on 1–2 branches)
4. `data-engineering/CURRICULUM.md` — pipelines and infrastructure
5. `generative-ai/` + `ai-engineering/` — the LLM application and engineering layer

This path takes 6–12 months at 10–15 hours/week. It's broad first, deep second — plan
to revisit each subject's depth READMEs once you've seen the whole landscape.

Interview guide: all 10 pillars in [interviewing/guides/00-start-here.md](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md)
are relevant; prioritize by role (see the role × topic matrix in [interviewing/README.md](https://github.com/ramseywise/sisyphus/blob/main/interviewing/README.md)).

---

## Three-layer architecture

This repo has three layers that each serve a different purpose:

| Layer | What it is | Where |
|---|---|---|
| **Depth** | Hands-on code, notebooks, course material — the actual learning | Subject dirs (`programming/`, `data-analytics/`, `generative-ai/`, `ai-engineering/`, etc.) |
| **Summary** | Compressed exam-prep view: concepts, trade-offs, question banks | sisyphus `interviewing/guides/` (10 pillars + Pillar 0 programming) |
| **Reference** | PDFs, papers, book chapters — theory to anchor the code | `readings/` and `sources/` inside each pillar (see the README's Readings list) |

**How to use the three layers:** Go deep first (subject dirs + CURRICULUM.md). Use the
summary layer (interview guides) as self-tests after each pillar, not as the primary
learning surface. Use readings to anchor specific concepts when a code exercise leaves a
"why does this work?" gap.

The layers point at each other — every interview guide's `00-overview.md` has a resource
map that links back to the depth dirs and the readings that support it.

---

## Definition of done

The curriculum is **structurally frozen** as of 2026-10-28: the six subjects and their
pillars above are the full set. New material goes into an existing pillar; a new top-level
folder or pillar needs a reason written here first.

**Decision 2026-10-29: `programming/` added as a sixth subject.** Python, SQL and TypeScript
are prerequisites for every other subject, but the repo only had seven pandas notebooks
(`data-analytics/python-basics/`) and no SQL or TypeScript at all. Language fluency doesn't belong in
any one pillar, and sisyphus `drills/` is practice, not teaching. So `programming/` holds the
course (notes, exercises, solutions), sisyphus holds the drills, and librarian shows both.
`python-basics/` moved to `programming/python/04-python-for-data/` along with the restored
McKinney notebooks and the Michigan/Wesleyan scripts.

A pillar is **done** when all five hold:

1. **README** — what the pillar teaches, the order to read it in, prerequisites.
2. **Condensed** — no vendored snapshot left inside it. Upstream courses are synthesised into
   `notes/` with sources cited (note frontmatter or a `references.md`), then the snapshot is
   deleted and its row moves to [Removed snapshots](#removed-snapshots) below.
3. **Runnable or labelled** — each notebook or practice lab runs offline, or says what it
   needs (API key, GPU, service).
4. **Imports cleanly** — `make import-courses` in librarian brings it in with no broken
   relative links.
5. **Cross-linked** — points to its sisyphus interview guide (the summary layer) and, once
   they exist, to the drills that practise it (drills name their `concepts`).

### Status

| Pillar | Left to do |
|---|---|
| ai-engineering 01–06 | Done on 1–2. Restructured 2026-10-31: each pillar is README + `references.md` + `notes/` (images and code inline) + `slides/` (deck.yaml, .pptx, .pdf) + `sources/` (PDFs, flat `images/`). `templates/`, `notebooks/` and code labs were folded into notes or linked upstream; the `practice/exercises.md` files were deleted. Check 3–5. |
| generative-ai 01 LLM fundamentals · 05 RL | No snapshots. README is thin for 01 (3 files) — check 1 and 3–5 |
| generative-ai 02 RAG | Condense `Deeplearning.ai-RAG-main` (27 MB, 6 slide PDFs) |
| generative-ai 03 agentic foundations | Condense 3 snapshots: `AgenticAIFrameworks-master`, `LLMs-as-Operating-Systems--Agent-Memory-main`, `AI-Agentic-Design-Patterns-with-AutoGen-main` |
| generative-ai 04 agentic frameworks | Condense `AI-Agents-in-LangGraph-main`, `Long-Term-Agentic-Memory-With-LangGraph-main` |
| generative-ai 06 observability | Condense 3 Langfuse snapshots into one note set |
| generative-ai 07 agentic applications | Condense `internet-search-agent-main` |
| data-analytics | `bayesian_inference_talk-main` to condense; `BayesianML/` is your own coursework (renamed from `BayesianML-master` 2026-10-28; see [Sources](#sources)) |
| data-engineering · data-science | No snapshots. Check 3–5 |
| programming | No snapshots (vendored TS exercises are kept as exercises, see [Sources](#sources)). Check 4–5 once librarian imports it and drills tag `concepts` |

Order: the AI-engineering path (Path A) first — generative-ai 02 → 03 → 04 → 06 → 07, then
ai-engineering 05. One snapshot per session; each follows the
`02-context-engineering` precedent (notes + references, then delete).

---

## Sources

Upstream material copied into this repo, recorded so its origin and license aren't lost. Notes
written here cite their own sources in frontmatter or a pillar `references.md`; this section covers
only material that was **copied in**.

### Vendored snapshots

ZIP downloads of other people's public repositories (hence the `-main` / `-master` suffixes):
read-reference material, not authored here, and tracked in git. They were downloaded as ZIPs, so
no nested `.git/config` records the upstream. Each URL was resolved by matching directory
contents, not names. Verified 2026-08-14: no third-party or hand-authored edits inside them.
Each one is condensed into notes and then deleted (see [Definition of done](#definition-of-done)).

| Directory | Upstream | Snapshot date | Tracked | Notes |
|---|---|---|---|---|
| ~~`ai-engineering/02-context/Context-Engineering-main`~~ | https://github.com/davidkimai/Context-Engineering | 2026-08-14 | **removed 2026-10-28** (was 298 files / 45.1 MB) | Synthesized into `02-context/notes/01–13` + `99` (speculative appendix); raw course files deleted. Its `templates/` and `notebooks/` were kept until 2026-10-31, then folded into the notes and deleted (in history at `6ee939f`). Cited paper PDFs in `02-context/sources/`, links in `02-context/references.md`. |
| `generative-ai/03-agentic-foundations/AgenticAIFrameworks-master` | https://github.com/adv-11/AgenticAIFrameworks | 2026-08-14 | 124 files / 1.3 MB | Content-matched (upstream adds `sf_ml_th/`). |
| `generative-ai/03-agentic-foundations/LLMs-as-Operating-Systems--Agent-Memory-main` | https://github.com/frankwwu/LLMs-as-Operating-Systems--Agent-Memory | 2026-08-14 | 109 files / 16.1 MB | Includes 1 PDF (`handbook.pdf`). Exact content match. DeepLearning.AI × Letta course. |
| `generative-ai/02-rag-retrieval/Deeplearning.ai-RAG-main` | https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG | 2026-08-14 | 103 files / 27.2 MB | Includes 6 PDFs (5 module slide decks + certificate). Exact content match. |
| `generative-ai/06-observability/langfuse-evaluation-main` | https://github.com/gustavobrieva1/langfuse-evaluation | 2026-08-14 | 56 files / 0.8 MB | Exact content match. Dependabot entry removed (see below). |
| `generative-ai/07-agentic-applications/internet-search-agent-main` | https://github.com/omidreza-amrollahi/internet-search-agent | 2026-08-14 | 39 files / 0.1 MB | Content-matched. Dependabot entry removed (see below). |
| `generative-ai/04-agentic-frameworks/Long-Term-Agentic-Memory-With-LangGraph-main` | https://github.com/YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph | 2026-08-14 | 39 files / 0.8 MB | Exact content match. Dependabot entry removed (see below). |
| `generative-ai/06-observability/langfuse-mcp-python-main` | https://github.com/Log-LogN/langfuse-mcp-python | 2026-08-14 | 36 files / 0.2 MB | Content-matched. Dependabot entry removed (see below). |
| `ai-engineering/05-graph-engineering/notebooks/knowledge-graphs-for-rag` | https://github.com/kaushikacharya/Knowledge_Graphs_for_RAG | 2026-08-14 | 34 files / 27.3 MB | **Removed 2026-10-31**: folded into `05-graph-engineering/notes/09–11` (in history at `6ee939f`, incl. the 22 MB `neo4j_L7.dump`). |
| `generative-ai/03-agentic-foundations/AI-Agentic-Design-Patterns-with-AutoGen-main` | https://github.com/ksm26/AI-Agentic-Design-Patterns-with-AutoGen | 2026-08-14 | 14 files / 1.7 MB | Exact content match. |
| `generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main` | https://github.com/ksm26/AI-Agents-in-LangGraph | 2026-08-14 | 12 files / 0.5 MB | Exact content match. |
| `generative-ai/06-observability/Learning-LangFuse-main` | https://github.com/pedroalexleite/Learning-LangFuse | 2026-08-14 | 9 files / 0.1 MB | Exact content match. |
| `data-analytics/Bayes/bayesian_inference_talk-main` | https://github.com/prasoon2211/bayesian_inference_talk | 2026-08-14 | 5 files / 5.8 MB | Exact content match. |

### Removed snapshots

| Directory | Upstream | Removed | What was kept |
|---|---|---|---|
| `ai-engineering/01-prompt-engineering/Prompt-Engineering-Guide-main` (originally `01-prompt/`) | https://github.com/dair-ai/Prompt-Engineering-Guide (MIT) | 2026-10-28 | Its English `pages/` content was merged into `ai-engineering/01-prompt-engineering/notes/`, with sources in each note's frontmatter. The notebooks were kept as `ai-engineering/01-prompt-engineering/notebooks/` and the lecture PDF as `notes/dair-prompt-engineering-lecture.pdf` (deleted 2026-10-30, superseded by `01-prompt-engineering/slides/`). The upstream `img/` folder was restored on 2026-10-28 (upstream commit `5767372`) as `sources/dair-prompt-engineering-guide/images/`. The Next.js site code and translations were dropped. Re-clone the upstream repo if you need them. |
| `ai-engineering/03-harness/learn-harness-engineering-main` (gitignored, never tracked) | https://github.com/walkinglabs/learn-harness-engineering (MIT) | 2026-10-28 | English lectures L01–L12 and projects 01–06 were folded into `ai-engineering/03-harness/notes/` (practice track `notes/practice/P1–P4` plus additions to notes 01, 02, 05, 07, 08). Templates from the course and the harness-creator skill were merged into `03-harness/templates/` (removed 2026-10-31: key snippets inline in notes 06, 09, 10; the rest is on the galactus handoff list, in history at `6ee939f`). The practice track became notes 09–10 (the exercises built on it were deleted 2026-10-31). Mapping and dropped material are in `03-harness/references.md`. The Electron projects, translations, site tooling and the rest of the skill were dropped. L13 and project 07 (loop engineering) were set aside for `04-loop/`. |
| `ai-engineering/readings/ai-agent-book-main` (vendored 2026-07-30) | https://github.com/bojieli/ai-agent-book (Apache-2.0) | 2026-10-28 | Bojie Li, *AI Agents in Depth*. The English chapters were synthesised into the pillar notes, each citing its chapter upstream: ch. 1 → `generative-ai/03-agentic-foundations/agent-fundamentals.md` and `03-harness-engineering` note 01; ch. 2 → `01-prompt-engineering` notes 02, 10 and `02-context-engineering` notes 02, 05; ch. 3 → `02-context-engineering` notes 04, 06 and `05-graph-engineering` note 11; ch. 4–5 → `03-harness-engineering` notes 01–07; ch. 6 → `generative-ai/07-agentic-applications/real-time-multimodal-agents.md`; ch. 7 → `06-eval`; ch. 8 → `generative-ai/05-RL/post-training-for-agents.md`; ch. 9 → `04-loop-engineering` note 08 (upstream has since renumbered its chapters; these are the current numbers); ch. 10 → `05-graph-engineering` notes 05, 07. The reference answers were condensed into `interviewing/guides/*/interview-guide.md`. Labs that run offline were copied, translated where needed. On 2026-10-31 the BM25, Elo-leaderboard, trajectory-verifier and self-modifying-agent labs were folded into worked examples (`generative-ai/02-rag-retrieval/rag.md`, `06-eval` note 05, `04-loop-engineering` note 08) and their copies deleted; they are linked upstream. `generative-ai/05-RL/practice/01-q-learning-treasure-hunt/` remains. Every other lab is linked upstream from the note it supports, because it needs an API key, a GPU or hardware, or is in Chinese. Translations, Chinese originals, site tooling and the local `READING-MAP.md` were dropped. |

### Programming course material (added 2026-10-29)

`programming/` vendors **exercises and data**, not course snapshots. They are kept on purpose because
they are the practice surface, and each keeps its license. Notes are written for this repo and cite
their sources in frontmatter. The full list is in [programming/references.md](programming/references.md).

| Path | Upstream | License | What's here |
|---|---|---|---|
| `programming/typescript/practice/typescript-exercises/` | https://github.com/typescript-exercises/typescript-exercises | MIT | 15 exercises with solutions. Patches for TypeScript 7 are listed in its `NOTICE.md` |
| `programming/typescript/practice/type-challenges/challenges/` | https://github.com/type-challenges/type-challenges | MIT | 26 easy and medium challenges with their test cases. The solutions are written here |
| `programming/sql/practice/data/survey.db` | https://github.com/swcarpentry/sql-novice-survey | CC-BY 4.0 | The Antarctic survey database (committed, 8 KB) |
| `programming/sql/practice/data/clubdata.sql` | https://pgexercises.com/ | CC BY-SA 3.0 | PGExercises club data converted from Postgres to SQLite. `clubdata.db` is built from it and gitignored |
| `programming/sql/practice/data/sql-murder-mystery.db` | https://github.com/NUKnightLab/sql-mysteries | MIT | Downloaded by `setup.sh`, gitignored |
| `programming/python/04-python-for-data/mckinney/ch*.ipynb` | https://github.com/wesm/pydata-book (`2nd-edition`) | MIT (code) | Chapter notebooks restored from history (they were deleted in commit `1c72b00`). `examples/` and `datasets/` (~240 MB) are downloaded by `fetch_data.sh` and gitignored |

**Paraphrased, not vendored:** Charles Severance's *Python for Everybody* (CC BY-NC-SA 3.0) and the
TypeScript Handbook (CC-BY 4.0). No book text, slides or `mbox` data files are copied. Practice
files use their own sample data.

`data-analytics/Bayes/BayesianML/` is **not** a snapshot despite its old `-master` suffix. It is
personal Coursera coursework with a `final_assignment/` that exists nowhere else, so it was renamed
on 2026-10-28 to keep suffix-based rules from sweeping it up. Nested `.git` directories, the
Dependabot cleanup and repo-size analysis are recorded in
`.claude/docs/research/2026-08-14_LAE-106_vendored-findings.md`.

---

## Role-based sequencing

If your goal is interview prep rather than learning progression, use the role × topic
matrix in [interviewing/guides/00-start-here.md](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md).
That file maps each pillar to prerequisites and tells you which pillars matter most for
which roles (AI engineer, data engineer, data scientist, ML engineer).

The self-learner paths above and the interview-prep sequence are complementary — the paths
build deep understanding; the pillar sequence builds exam-ready breadth. Most people want
both.
