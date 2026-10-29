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
   deleted and its row moves to "Removed snapshots" in [VENDORED.md](VENDORED.md).
3. **Runnable or labelled** — each notebook or practice lab runs offline, or says what it
   needs (API key, GPU, service).
4. **Imports cleanly** — `make import-courses` in librarian brings it in with no broken
   relative links.
5. **Cross-linked** — points to its sisyphus interview guide (the summary layer) and, once
   they exist, to the drills that practise it (drills name their `concepts`).

### Status

| Pillar | Left to do |
|---|---|
| ai-engineering 01 prompt · 02 context · 03 harness · 04 loop · 06 eval | Done on 1–2. Check 3–5. |
| ai-engineering 05 graph | Condense `notebooks/knowledge-graphs-for-rag` (27 MB, incl. a 22 MB Neo4j dump) |
| generative-ai 01 LLM fundamentals · 05 RL | No snapshots. README is thin for 01 (3 files) — check 1 and 3–5 |
| generative-ai 02 RAG | Condense `Deeplearning.ai-RAG-main` (27 MB, 6 slide PDFs) |
| generative-ai 03 agentic foundations | Condense 3 snapshots: `AgenticAIFrameworks-master`, `LLMs-as-Operating-Systems--Agent-Memory-main`, `AI-Agentic-Design-Patterns-with-AutoGen-main` |
| generative-ai 04 agentic frameworks | Condense `AI-Agents-in-LangGraph-main`, `Long-Term-Agentic-Memory-With-LangGraph-main` |
| generative-ai 06 observability | Condense 3 Langfuse snapshots into one note set |
| generative-ai 07 agentic applications | Condense `internet-search-agent-main` |
| data-analytics | `bayesian_inference_talk-main` to condense; `BayesianML/` is your own coursework (renamed from `BayesianML-master` 2026-10-28; see VENDORED.md) |
| data-engineering · data-science | No snapshots. Check 3–5 |
| programming | No snapshots (vendored TS exercises are kept as exercises, see VENDORED.md). Check 4–5 once librarian imports it and drills tag `concepts` |

Order: the AI-engineering path (Path A) first — generative-ai 02 → 03 → 04 → 06 → 07, then
ai-engineering 05. One snapshot per session; each follows the
`02-context-engineering` precedent (notes + references, then delete).

---

## Role-based sequencing

If your goal is interview prep rather than learning progression, use the role × topic
matrix in [interviewing/guides/00-start-here.md](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/00-start-here.md).
That file maps each pillar to prerequisites and tells you which pillars matter most for
which roles (AI engineer, data engineer, data scientist, ML engineer).

The self-learner paths above and the interview-prep sequence are complementary — the paths
build deep understanding; the pillar sequence builds exam-ready breadth. Most people want
both.
