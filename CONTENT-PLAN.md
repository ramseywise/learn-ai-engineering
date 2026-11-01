# Content plan — from notes to a course

Status: 2026-11-01, approved. All four decisions in section 6 were accepted. Companion to [CURRICULUM.md](CURRICULUM.md) (what the course is) and
[ai-engineering/PILLAR-LAYOUT.md](ai-engineering/PILLAR-LAYOUT.md) (what a pillar folder looks like).
This file says what is wrong with the material as coursework, the standard every area converges on,
and the order of work.

The audience is a self-learner working through librarian. Librarian imports every `.md` and
`.ipynb` under a subject as a lesson, so a note is a chapter and a slide deck is the lecture that
goes with it. The notes are the meat. The slides catch the idea and double as flashcards.

---

## 1. Where each area stands

Measured 2026-11-01 (`wc -w` on notes, `grep layout:` on decks).

| Area | Shape | Notes | Depth per note | Slides | Verdict |
|---|---|---|---|---|---|
| ai-engineering | 9 pillars | 90 | 1.5k–6k words, figures and code inline | 6 decks (01–06), 267 slides, 84 of them tables | Content is right. Decks read as reference cards, not a lecture. 07–09 have no deck; 08 has one note, 09 none |
| generative-ai | 7 pillars | 43 | Uneven: 01/01 is 19k words, 01/02 is 11.6k, 01/03–06 are under 1.3k; pillars 04 and 06 average 1.5k | none | Pillar skeleton is good, the notes inside are not yet a curriculum. No decks |
| data-analytics | flat `notes/` | 14 | 400 (4 skeletons) to 1.8k | none | Thinnest area. Statistics only. The pandas/DataFrame on-ramp left for `programming/python/04` on 2026-10-29 and is notebooks without notes. No visualisation, forecasting, credit or cohort analysis. No "what an analyst needs to know" |
| data-science | flat `notes/` + two raw Ng folders | 17 | 1.4k–3.2k | none | A note set beside a pile of coursework, not a curriculum. Gaps named in its CURRICULUM.md (boosting + SHAP, LLM embeddings as features, time series, recommenders). No decks |
| data-engineering | flat `notes/` + two raw DataTalks zoomcamps | 8 | 1.5k–2.7k | none | Same shape as data-science: notes are the synthesis, but the course folders are the bulk. Missing data modelling, contracts and quality, streaming depth, cost |
| programming | 3 tracks, 4 Python modules | 31 | 300–600, exercise-driven | none | Right shape and right depth for a language course. Needs decks for study, and a few diagrams |

Two cross-cutting problems:

1. **Three different folder shapes.** ai-engineering and generative-ai are pillars with README,
   references, notes, sources, slides. The four subjects are flat. The `/pillar`, `/slides`,
   `/chapter` and `/papers` skills were built for pillars, so the subjects cannot use them, and
   librarian shows the two shapes differently.
2. **No written standard for a note or a deck as teaching.** PILLAR-LAYOUT says what a note cites
   and where the figures go. It does not say what a chapter must contain, how long it is, or how a
   deck tells its story. That is why ai-engineering decks are 31% tables and why a 400-word
   skeleton and a 19k-word monolith both count as "a note".

---

## 2. The standard

### 2.1 Every area is pillars

Each subject becomes `<area>/<NN-pillar>/` in the PILLAR-LAYOUT shape, with one addition:
`practice/` for labs and coursework, which generative-ai already has. The "Subjects without
pillars" paragraph in PILLAR-LAYOUT is deleted. Raw course folders (Ng notebooks, DataTalks
zoomcamps, Coursera Bayesian ML) move into the `practice/` of the pillar that teaches them.

```
<area>/<NN-pillar>/
  README.md          what, why, order, rules of thumb, story of the pillar in one paragraph
  references.md      books, papers, courses, videos, mapped to notes
  notes/NN-*.md      the chapters
  slides/            deck.yaml + .pptx + .pdf
  practice/          notebooks, scripts, exercises, run-labelled
  sources/           PDFs and images/
```

CURRICULUM.md records this as a decision under Definition of done: the 2026-10-28 freeze froze the
six subjects, not their internal shape. Each subject's `CURRICULUM.md` stays as the sequenced path
across its pillars.

### 2.2 A note is a chapter

Target 2,000–5,000 words. Under 1,500 is a skeleton and says so in a status line. Over 7,000 is
two chapters. Every chapter has, in this order:

1. **Hook** (one paragraph): the problem this chapter solves and what goes wrong without it.
2. **Concepts in prose**, one H2 per concept, each with a worked example in code that runs as
   written. Numbers come with their setup.
3. **At least one figure or diagram**: a paper figure from `sources/images/`, or a Mermaid or
   ASCII diagram written for the note. A figure appears in a note before it appears on a slide.
4. **Pitfalls**: what practitioners get wrong, with the symptom.
5. **Try it**: two to four exercises or questions with answers folded or linked to `practice/`.
6. **Interview checklist**: the table the subject notes already use, answers filled in.
7. **Next**: the link to the following note.

This goes into PILLAR-LAYOUT as a "notes/ — the chapter" section, and the `/chapter`, `/papers`
and `/pillar` skills check for it. ai-engineering notes already meet it, minus items 5 and 7 in
places; the data-analytics skeletons and the generative-ai thin notes do not.

### 2.3 A deck tells the pillar's story

A deck is the lecture a teacher would give over the notes, not the notes compressed. Rules, added
to `.claude/skills/slides/references/deck-spec.md`:

- **Spine.** Every part follows problem → what breaks → principle → technique → evidence → what
  you do on Monday. The first slide of a part is a `statement` or `image` that poses the problem;
  the last is the `takeaway`.
- **Layout mix.** No layout above 25% of a deck; no three consecutive slides with the same layout.
  Each part has at least one `code` or worked example and one `image` or `flow`.
- **Flashcard pairs.** Every content slide has `title` (the prompt) and `takeaway` (the answer).
  `takeaway` becomes required. A `recall:` key holds an optional sharper question when the title
  is not one. Librarian reads `deck.yaml` and emits one flashcard per slide (importer change, see
  §4).
- **Coverage.** A deck covers every note in the pillar; the build warns when a note has no slide
  with `source:` pointing at it.
- **Size.** 30–45 content slides for a 10+ note pillar, 15–25 for a programming module.

`/slides` is generalised from `ai-engineering/<pillar>` to `<area>/<pillar>` and
`programming/<track>/<module>`. The Makefile target takes `PILLAR=data-analytics/02-statistics`.

### 2.4 Languages

- **Python is the course language** for generative-ai, data-analytics, data-science and
  data-engineering. The frameworks taught (LangGraph, ADK, PyMC, pandas, dbt, Spark) are
  Python-first, and the practice folders already are.
- **ai-engineering labs come in both TypeScript and Python**, side by side, so the two can be
  compared. Existing lab code stays in place. Notes stay language-neutral in prose.
- The generative-ai TypeScript SDK lab in 01-llm-fundamentals stays as the bridge, and its model
  id is updated.

This is a recommendation to decide in CURRICULUM.md. The alternative (Python everywhere, TS only
in programming) is simpler but leaves the TypeScript track with no destination.

### 2.5 References widen to courses and videos

Each pillar's `references.md` gains a **Courses and videos** table (course, platform, free or
paid, which notes it supports, which weeks to watch). Candidates per area are listed in §3. Videos
are linked, never vendored. The subject areas have almost no papers to cite, so these are their
primary external layer alongside books.

---

## 3. Per-area plan

Each table lists the target pillars, where the current material goes, and what is new. Note counts
are targets for a first full pass, not ceilings.

### 3.1 data-analytics (biggest gap, do first)

Framing in its README: *what a data analyst has to know*: get data into a frame, describe it, test
a claim, model a relationship, forecast it, explain it to someone, and know when the numbers lie.

| Pillar | From | New | Notes |
|---|---|---|---|
| 01-python-for-data-analysis | `programming/python/04-python-for-data/` moves back here: the seven `1_`–`7_` notebooks, McKinney ch06–11 and 14, course scripts. Programming keeps a pointer in its Python README and syllabus phase 4 | Written chapters for the first time: Series and DataFrame, loading and cleaning, indexing and selection, reshaping and joins, groupby and aggregation, time series, plotting. Each notebook becomes the `practice/` of one chapter | 7 |
| 02-probability-and-statistics | notes 01–05 | Fill the four skeletons (probability, estimation, regression and GLMs) to chapter depth with `/chapter` from Blitzstein & Hwang, Bruce & Bruce, ISLP, Gelman et al.; add a descriptive statistics and EDA chapter | 6 |
| 03-experimentation-and-causality | notes 06–08 | Fill 07 (experimentation at scale); add a metrics and KPI design chapter (north-star, guardrails, ratio metrics, the KDD 2017 pitfalls paper) | 4 |
| 04-bayesian-analysis | notes 09–14, `practice/BayesianML/`, `practice/AB-Bayes/` | Nothing new; already chapter depth | 6 |
| 05-visualisation-and-storytelling | Knaflic (held, uncited) | Grammar of graphics and chart choice; matplotlib and seaborn; plotly and interactive; JavaScript with D3, Vega-Lite and Observable Plot; dashboards (Streamlit, Metabase, Looker Studio); storytelling with data. Book list by language: Wilke *Fundamentals of Data Visualization*, Knaflic, Munzner, Healy *Data Visualization*, Murray *Interactive Data Visualization for the Web*, Meeks *D3.js in Action*, Cairo *The Truthful Art* | 5 |
| 06-applied-analyses | — | Worked end-to-end analyses, one chapter each: forecasting (Hyndman & Athanasopoulos *FPP3*, free; statsmodels, Prophet, baseline comparisons), credit scoring (logistic scorecard, WoE and IV, Gini and KS, PD/LGD, Basel vocabulary), cohort and retention, funnel and conversion, segmentation and RFM, SQL for analytics (window functions revisited for analysts, linking `programming/sql`) | 6 |

Courses and videos to add to `references.md`: StatQuest (statistics and ML playlists), 3Blue1Brown
probability and linear algebra, Khan Academy Statistics and Probability, MIT 18.650 Statistics for
Applications, Kaggle Learn (pandas, data visualisation, time series), Google Data Analytics
Certificate (syllabus as a checklist), Mode SQL tutorial, Hyndman's FPP3 lectures, Cassie Kozyrkov's
*Making Friends with Machine Learning*.

Decks: one per pillar, six decks.

### 3.2 data-science

Framing: *what a data scientist has to know beyond the analyst*: fit, evaluate and explain a model,
know the classical and neural families, and know what a text or an embedding is to a model.

| Pillar | From | New | Notes |
|---|---|---|---|
| 01-classical-ml | notes 01–06, `practice/Intro to Machine Learning in Python`, Ng ML `ex1–ex8` into `practice/` | Boosting in practice (sklearn HGB vs XGBoost vs LightGBM vs CatBoost, with SHAP) as a chapter with a notebook, closing the gap named in CURRICULUM.md; model interpretability (permutation importance, PDP, SHAP) | 8 |
| 02-deep-learning | note 07, Ng DL notebooks into `practice/`, note 14 | Split 07 into the five Ng courses as chapters where the notebooks exist (NN basics, optimisation and regularisation, structuring projects, CNNs, sequence models); PyTorch as the course framework with a translation table from the Ng NumPy and TF code | 6 |
| 03-nlp | notes 08–13, `practice/intro-to-nlp`, `practice/Text Analytics with Python` | LLM embeddings as features (planned note 18): classification, clustering, anomaly detection on sentence embeddings | 7 |
| 04-llms-from-scratch | notes 15–17, `practice/nn-zero-to-hero/` | Nothing new; link forward to generative-ai 01 | 3 |
| 05-time-series-and-recommenders | — | Time series ML (feature-based and sequence models, backtesting), recommender systems (collaborative filtering, matrix factorisation, two-tower, evaluation offline and online) | 3 |

Courses and videos: Ng ML Specialization and DL Specialization (already the practice), StatQuest
ML playlist, fast.ai *Practical Deep Learning*, Karpathy *nn-zero-to-hero* (already), Stanford
CS229 and CS224N lecture videos, Kaggle Learn (intro and intermediate ML, feature engineering).

Decks: five.

### 3.3 data-engineering

Framing: *a stage silently trusts the one before it*; the pillars follow the data.

| Pillar | From | New | Notes |
|---|---|---|---|
| 01-storage-and-compute-foundations | DDIA chapters in `sources/` | Encoding and files (CSV, Parquet, Arrow), row vs column stores, distributed compute (MapReduce → Spark → DuckDB and Polars on one machine), partitioning and replication | 4 |
| 02-ingest-and-modelling | note 01, DataTalks DE 01 into `practice/` | Dimensional modelling (Kimball facts and dimensions, SCD types), Data Vault in one page, One Big Table and when it wins, data contracts | 4 |
| 03-transform-and-orchestrate | notes 02–03, DE 02 and 04 into `practice/` | dbt depth (tests, snapshots, incremental), idempotency and backfills, Dagster and Airflow compared with code | 4 |
| 04-warehouse-lakehouse-streaming | note 04, DE 03, 05, 06 into `practice/` | Table formats (Delta, Iceberg, Hudi), lakehouse vs warehouse, Kafka and stream processing semantics (exactly-once, watermarks), cost (bytes scanned, slots, egress) | 5 |
| 05-quality-and-observability | note 05 | Data quality dimensions, Great Expectations and dbt tests, freshness and volume monitors, lineage (OpenLineage), incident playbooks | 3 |
| 06-ml-platform | notes 06 and 08, DataTalks MLOps into `practice/` | Feature stores, model registry, batch vs online serving, drift, the maturity model | 5 |
| 07-architecture-and-governance | note 07 | Mesh, fabric, MDW (existing), plus access control, PII handling, GDPR basics for engineers | 2 |

Courses and videos: DataTalks DE and MLOps zoomcamps (already the practice), Kleppmann's DDIA
lecture series (YouTube), dbt Learn fundamentals, Confluent Kafka 101, Databricks lakehouse
fundamentals (free), Joe Reis and Matt Housley *Fundamentals of Data Engineering* as a book.

Decks: seven.

### 3.4 generative-ai

The pillars are right. The notes inside need to become chapters and the pillars need lectures.

| Pillar | Work |
|---|---|
| 01-llm-fundamentals | Split note 01 (19k words) into five chapters: tokens and embeddings, attention and the transformer block, scale and the model zoo, decoding and inference-time behaviour, hallucination and base vs assistant. Split note 02 (11.6k) into pretraining data and objectives, SFT and instruction tuning, preference optimisation overview (pointing to 05-RL), PEFT and fine-tuning in practice. Grow 03, 04 and 06 to chapter depth. Write planned 07 (open-weight models and local inference). About 14 chapters |
| 02-rag-retrieval | Chapter depth already in 01–07. Fold 12–14 (Bedrock, Vertex, ADR) into one "managed RAG" chapter. 12 chapters |
| 03-agentic-foundations | Already chapter depth. Fold the pending *Design Patterns* chapters 1, 5, 9 and the three routed book folders (listed in CURRICULUM.md status) |
| 04-agentic-frameworks | Every note is 0.9k–1.7k. Grow each with a worked lab: build the same research agent in LangGraph, then ADK, then compare; one chapter on LangSmith tracing of that agent |
| 05-RL | Chapter depth. Add a one-chapter plain-language on-ramp before 01 for readers without data-science 02 |
| 06-observability | Notes are 1.2k–1.7k. Grow with the support-agent case study threaded through 01–05; add a chapter on cost and latency dashboards |
| 07-agentic-applications | Add two application chapters: a coding agent, and a data-analysis agent over the analytics pillars' datasets |

Decks: seven, one per pillar, the same spine as ai-engineering.

### 3.5 ai-engineering

| Work | Detail |
|---|---|
| Decks 01–06: story pass | Revise each `deck.yaml` against §2.3: open every part with the problem, cut tables to at most a quarter, add a worked example and a figure per part, make every slide a flashcard pair, confirm every note has a slide |
| Decks 07–09 | 07 inference has nine notes and is ready for a deck now. 08 and 09 wait on their notes |
| Notes 08 and 09 | 08 multimodal: six planned chapters (image input, document understanding, multimodal RAG, speech and voice agents, generation (exists), evaluation of multimodal). 09 safety and security: six planned chapters (threat model, prompt injection and jailbreaks, guardrail models, tool and execution sandboxing, red-teaming tools, incident response). Both READMEs already list the planned notes; write them with `/papers multimodal` and `/papers safety` once those homes route |
| Chapter checklist | Add "Try it" exercises and a "Next" link where missing. Most notes already have the rest |
| TypeScript labs | Per §2.4, each pillar's README names one lab in `practice/` (TypeScript and Python, side by side): a prompt eval harness (01), a context budgeter (02), a tool server with sandboxing (03), a loop with a scorekeeper (04), a LangGraph graph (05, Python), an eval suite in CI (06) |

### 3.6 programming

Shape and depth stay. Add:

- **Decks** for Python 01, 02, 03, SQL and TypeScript, 15–25 slides each, built as flashcards:
  the title is the concept or a question, the takeaway is the rule. These are the study decks.
- **Diagrams** where a note describes a mechanism: names vs objects (Python 03/01), the
  iterator protocol (03/02), the event loop (03/07 and TS 06), a query plan (SQL 08), type
  narrowing (TS 03).
- Python 04 moves to data-analytics (§3.1). Programming's phase 4 becomes "hand off to
  data-analytics 01".

---

## 4. Tooling changes

| Change | Where | Why |
|---|---|---|
| Generalise `/slides` to `<area>/<pillar>` and `programming/<track>/<module>`; Makefile `slides` target takes the full path | `.claude/skills/slides/SKILL.md`, `Makefile` | Decks for every area |
| Add §2.3 rules to the deck spec: required `takeaway`, optional `recall`, layout-mix and coverage warnings in the builder | `deck-spec.md`, `scripts/slides/build_deck.py` | Story and flashcards |
| Add the §2.2 chapter section to PILLAR-LAYOUT; `/pillar`, `/chapter`, `/papers` check for hook, figure, try-it, next | `ai-engineering/PILLAR-LAYOUT.md`, the three skills | One definition of a note |
| `/pillar` learns the four subject areas and `practice/` | `.claude/skills/pillar/SKILL.md` | Restructure with the same tool |
| `scripts/link_check.py` runs after every `git mv` batch | — | The restructure moves about 60 notes |
| Ledger homes for the new pillars (`analytics` split by pillar if useful, `data-systems`, `programming`) per `scripts/papers/subject-areas-plan.md` Phase 1 | `scripts/papers/potw.py` | Papers route to the new folders |
| Librarian: `import_courses.py` reads `slides/deck.yaml` and emits flashcards (title/recall → takeaway) attached to the lesson named in `source:` | `../librarian/core/import_courses.py` | Out of this repo; the user's flashcard ask depends on it |

---

## 5. Order of work

Each phase ends with `make link-check` green, a staged diff, and the CURRICULUM.md status table
updated. Estimates assume the skills do the mechanical work and each chapter gets a real read of
its sources, as the readings rules require.

| Phase | Work | Size |
|---|---|---|
| 0 | Standards: §2.2 into PILLAR-LAYOUT, §2.3 into deck-spec and the builder, `/slides` and `/pillar` generalised, §2.1 and §2.4 decisions recorded in CURRICULUM.md | 1–2 sessions |
| 1 | Restructure: subjects into pillars by `git mv`, raw course folders into `practice/`, Python 04 to data-analytics 01, READMEs and CURRICULUM paths rewritten, link check | 2 sessions |
| 2 | data-analytics: fill the four skeletons, write pillar 01 chapters over the notebooks, write 05 and 06, references with courses and videos, six decks | 8–10 sessions |
| 3 | ai-engineering: deck 07, story pass on 01–06 | 3–4 sessions |
| 4 | generative-ai: split 01, grow 04 and 06, seven decks | 6–8 sessions |
| 5 | data-science: restructure chapters, boosting and embeddings chapters, 05 pillar, five decks | 5–6 sessions |
| 6 | data-engineering: foundations and modelling chapters, quality pillar, seven decks | 5–6 sessions |
| 7 | programming: five decks and the diagrams | 2–3 sessions |
| 8 | ai-engineering 08 and 09 notes and decks, as their papers route | ongoing |

Phases 2 onward are independent once 0 and 1 are done, so the order can follow interest. The
librarian importer change can land any time after Phase 0 fixes the deck format.

---

## 6. Decisions needed

1. **§2.1** Subjects become pillars, and raw course folders move under `practice/`. Reverses the
   "flat notes" shape chosen 2026-10-31 for the four subjects.
2. **§3.1** `programming/python/04-python-for-data` moves back to data-analytics as its first
   pillar, with chapters written over the notebooks. Reverses part of the 2026-10-29 decision.
3. **§2.4** Python for the data and generative-ai areas, TypeScript-first labs in ai-engineering.
4. **§3.4** Fold generative-ai 02 notes 12–14 into one managed-RAG chapter.
