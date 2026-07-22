# Curriculum — learn-ai-engineering

A coordinator, not a syllabus. This file maps the subjects, names the prerequisites, and
routes you to the right starting point. Per-subject `CURRICULUM.md` files hold the
sequenced learning paths for each domain.

> **Self-learner?** Start with the [Learning Paths](#learning-paths) section below.
> **Interview prep?** Go to [interviewing/guides/00-start-here.md](interviewing/guides/00-start-here.md).

---

## Subject-area map

| Subject | CURRICULUM.md | Prerequisites | Structure |
|---|---|---|---|
| Data Analytics | [data-analytics/CURRICULUM.md](data-analytics/CURRICULUM.md) | None — entry point | Linear (Python basics → domain branches) |
| Data Engineering | [data-engineering/CURRICULUM.md](data-engineering/CURRICULUM.md) | Data analytics basics | Linear (pipeline stages) |
| Data Science | [data-science/CURRICULUM.md](data-science/CURRICULUM.md) | Data analytics basics | Tree (statistical foundations splits into supervised / unsupervised / Bayesian) |
| Generative AI | [generative-ai/README.md](generative-ai/README.md) | None required; DS/DE enrich it | 7-pillar sequential (LLM fundamentals → RAG → Agentic foundations → Agentic frameworks → RL → Observability → Agentic applications) |
| AI Engineering | [ai-engineering/README.md](ai-engineering/README.md) | Generative AI Pillar 1 | 6-pillar sequential (prompt → context → harness → loop → graph → eval) |
| Programming | [programming/README.md](programming/README.md) | None | Topic + difficulty library (not sequential) |

**Reading the table:** "Prerequisites" are recommendations, not gates. You can start
generative-ai cold — you'll just revisit data-science concepts as they come up rather than
having them in memory already.

---

## Learning Paths

### Path A: AI Engineering (recommended for new AI engineers)

Goal: build reliable, production-grade LLM systems.

1. **Python fluency** — `programming/Python Basics/` (2–3 weeks)
   Data wrangling, pandas, basic plotting. Skip if you already write Python daily.

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

Interview guide: start at [interviewing/guides/00-start-here.md](interviewing/guides/00-start-here.md),
pillars 0–4 are the core loop for this path.

---

### Path B: Data Engineering

Goal: build data pipelines and ML infrastructure.

1. **Python fluency** — `programming/Python Basics/` (see Path A step 1)

2. **Data Engineering sequence** — `data-engineering/CURRICULUM.md`
   Ingest → transform → orchestrate → warehouse → monitor → feature-serve.
   Follows the DataTalks modules (Docker, workflow, DWH, batch, streaming) + MLOps track.

3. **Optional depth** — `data-science/CURRICULUM.md` for the ML side of data pipelines
   (feature engineering, model evaluation), or `generative-ai/` for LLM-native pipelines.

Interview guide: [interviewing/guides/8-data-eng-mlops/00-overview.md](interviewing/guides/8-data-eng-mlops/00-overview.md).

---

### Path C: Full-Stack Data

Goal: broad foundation across the full data/AI stack.

1. `data-analytics/CURRICULUM.md` — Python + analytics basics
2. `data-science/CURRICULUM.md` — classical ML, stats, model evaluation (tree-shaped: go deep on 1–2 branches)
3. `data-engineering/CURRICULUM.md` — pipelines and infrastructure
4. `generative-ai/` + `ai-engineering/` — the LLM application and engineering layer

This path takes 6–12 months at 10–15 hours/week. It's broad first, deep second — plan
to revisit each subject's depth READMEs once you've seen the whole landscape.

Interview guide: all 10 pillars in [interviewing/guides/00-start-here.md](interviewing/guides/00-start-here.md)
are relevant; prioritize by role (see the role × topic matrix in [interviewing/README.md](interviewing/README.md)).

---

## Three-layer architecture

This repo has three layers that each serve a different purpose:

| Layer | What it is | Where |
|---|---|---|
| **Depth** | Hands-on code, notebooks, course material — the actual learning | Subject dirs (`data-analytics/`, `generative-ai/`, `ai-engineering/`, etc.) |
| **Summary** | Compressed exam-prep view: concepts, trade-offs, question banks | `interviewing/guides/` (10 pillars + Pillar 0 programming) |
| **Reference** | PDFs, papers, book chapters — theory to anchor the code | `readings/` (organized by interview-pillar topic) |

**How to use the three layers:** Go deep first (subject dirs + CURRICULUM.md). Use the
summary layer (interview guides) as self-tests after each pillar, not as the primary
learning surface. Use readings to anchor specific concepts when a code exercise leaves a
"why does this work?" gap.

The layers point at each other — every interview guide's `00-overview.md` has a resource
map that links back to the depth dirs and the readings that support it.

---

## Role-based sequencing

If your goal is interview prep rather than learning progression, use the role × topic
matrix in [interviewing/guides/00-start-here.md](interviewing/guides/00-start-here.md).
That file maps each pillar to prerequisites and tells you which pillars matter most for
which roles (AI engineer, data engineer, data scientist, ML engineer).

The self-learner paths above and the interview-prep sequence are complementary — the paths
build deep understanding; the pillar sequence builds exam-ready breadth. Most people want
both.
