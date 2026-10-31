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
| Data Analytics | [data-analytics/CURRICULUM.md](data-analytics/CURRICULUM.md) | Programming: Python 01–04 | Linear, 10 notes: distributions → hypothesis testing → A/B testing → Bayesian inference → Bayesian A/B and ML |
| Data Engineering | [data-engineering/CURRICULUM.md](data-engineering/CURRICULUM.md) | Data analytics basics | Linear, 8 notes: ingest → transform → orchestrate → warehouse → monitor → feature-serve, then architectures and MLOps maturity; two DataTalks zoomcamps as runnable coursework |
| Data Science | [data-science/CURRICULUM.md](data-science/CURRICULUM.md) | Data analytics basics | Tree, 17 notes: classical-ML core, then the NLP, neural-net and from-scratch (micrograd → nanoGPT) arcs. Bayesian methods live in data-analytics |
| Generative AI | [generative-ai/README.md](generative-ai/README.md) | None required; DS/DE enrich it | 7-pillar sequential (LLM fundamentals → RAG → Agentic foundations → Agentic frameworks → RL → Observability → Agentic applications) |
| AI Engineering | [ai-engineering/README.md](ai-engineering/README.md) | Generative AI Pillar 1 | 6-pillar sequential (prompt → context → harness → loop → graph → eval), plus inference as the substrate and two cross-cuts: multimodal, safety and security |

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

**Decision 2026-10-31: `ai-engineering/07-inference-engineering/` added as a seventh
ai-engineering pillar.** The readings backlog held a whole book on AI systems performance
(20 chapters plus a checklist), Huyen's inference-optimization chapter and a steady flow of
serving papers. None of the six layers could hold GPU kernels, KV-cache management or
prefill/decode disaggregation without becoming a hardware course, and moving the material
out of the repo would have dropped it. Inference sits under the six layers as their
substrate: it prices every call they make. The freeze is relaxed in one direction only: a
new pillar is added when the readings triage finds a body of sources with no home.

**Decision 2026-10-31: `ai-engineering/08-multimodal-engineering/` and
`ai-engineering/09-safety-and-security/` added.** Both were already watch topics in
`scripts/papers/potw.py`: off-syllabus buckets kept "so it is still in the ledger when the pillar
arrives". By 2026-10-31 the ledger held 205 multimodal and 83 safety papers with no home. A
roadmap.sh comparison found the same two gaps: the repo had nothing on image or document input,
multimodal RAG or speech outside one voice-agent note, and its security material was split across
three notes, with no threat modelling, guardrail models or red-teaming tools. Both are cross-cuts,
not layers: each changes all six foundations, so they are read after them. Alignment research
(scheming, alignment faking) and interpretability stay parked. The engineering pillar covers
the application side. Two smaller gaps from the same comparison went into existing homes:
open-weight models and local inference became a planned note in `generative-ai/01`, and LLM
embeddings as features (classification, clustering, anomaly detection) a planned note in
`data-science`.

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
| ai-engineering 07–09 | Scaffolded 2026-10-31: README with scope and planned notes, `references.md` seeded, empty `notes/` and `sources/`. 07 has its book in `sources/`; 08 and 09 wait on `multimodal` and `safety` becoming homes in `potw.py` so their parked papers route. Checks 1–5 open. |
| generative-ai 01 LLM fundamentals | Done 2026-10-31 on 1–2: README, references, notes 01–06 (07 open-weight models planned), `practice/01-typescript-sdk/`, book chapters in `sources/`. Check 3–5. The TypeScript lab pins an old model id. |
| generative-ai 02 RAG | Done 2026-10-31: README, references, notes 01–14, `sources/`. The DLAI snapshot was condensed into notes 02–07 and removed. Check 3–5. |
| generative-ai 03 agentic foundations | Done 2026-10-31 on 1–2: notes 01–06, three snapshots removed. Left: fold *Design Patterns* chapters 1, 5 and 9, and integrate the three routed book folders in `sources/`. Check 3–5. |
| generative-ai 04 agentic frameworks | Done 2026-10-31: notes 01–06, two snapshots removed. Check 3–5. |
| generative-ai 05 RL | Done 2026-10-31 on 1–2: notes 01–05; six off-topic papers parked in `sources/misfiled/`. Check 3–5. |
| generative-ai 06 observability | Done 2026-10-31: notes 01–05, three Langfuse snapshots removed. Check 3–5. |
| generative-ai 07 agentic applications | Done 2026-10-31: notes 01–03, references, `practice/` (deep-research-bot, deep_research_bench). The internet-search-agent snapshot was condensed into note 01 and removed. Check 3–5. |
| data-analytics | Done 2026-10-31: README, CURRICULUM (path only), references, notes 01–14 (01, 03, 05, 07 are stats-gap skeletons added 2026-10-31; see `scripts/papers/subject-areas-plan.md`), `sources/` (14 PDFs), `practice/` (4 items, run-labelled). Both Bayes snapshots removed; `readings/` became `sources/`. Check 4–5. |
| data-engineering | Done 2026-10-31: README, CURRICULUM (path and prerequisites only), references (with licences), notes 01–08, `sources/` (6 PDFs). The two DataTalks zoomcamp folders stay in place as runnable coursework, run-labelled per module. `sources/` also holds 7 queued ml-systems PDFs from the router: integrate with `/papers` or `/chapter`. Check 4–5. |
| data-science | Done 2026-10-31: README, CURRICULUM (path and prerequisites only), references, notes 01–17 (classical ML, the NLP arc, Ng neural nets, micrograd → makemore → nanoGPT). `practice/` keeps Müller & Guido, Sarkar, nn-zero-to-hero and own notebooks; Ng coursework untouched. `intro-to-nlp` (own coursework) kept in `practice/`; `readings/` became `sources/`. Check 3 partly: stale APIs are labelled per note. Check 4–5. |
| programming | No snapshots (vendored TS exercises, SQL data and McKinney notebooks are kept as practice, see [Sources](#sources)). Checks 1, 3 and 5 verified 2026-10-31: track READMEs have Layout and Syllabus, every practice set and script is run-labelled, interview guide Pillar 0 and drills are linked. Check 4 waits on librarian import and drills tagging `concepts`. |

Every pillar is now condensed (check 2). What remains is check 3 (run every notebook offline or
label it), check 4 (librarian import) and check 5 (drills tagged with `concepts`).

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

None remain. Every snapshot listed here on 2026-08-14 was condensed into notes and removed by
2026-10-31; each now has a row in [Removed snapshots](#removed-snapshots).

### Removed snapshots

| Directory | Upstream | Removed | What was kept |
|---|---|---|---|
| `ai-engineering/01-prompt-engineering/Prompt-Engineering-Guide-main` (originally `01-prompt/`) | https://github.com/dair-ai/Prompt-Engineering-Guide (MIT) | 2026-10-28 | Its English `pages/` content was merged into `ai-engineering/01-prompt-engineering/notes/`, with sources in each note's frontmatter. The notebooks were kept as `ai-engineering/01-prompt-engineering/notebooks/` and the lecture PDF as `notes/dair-prompt-engineering-lecture.pdf` (deleted 2026-10-30, superseded by `01-prompt-engineering/slides/`). The upstream `img/` folder was restored on 2026-10-28 (upstream commit `5767372`) as `sources/dair-prompt-engineering-guide/images/`. The Next.js site code and translations were dropped. Re-clone the upstream repo if you need them. |
| `ai-engineering/03-harness/learn-harness-engineering-main` (gitignored, never tracked) | https://github.com/walkinglabs/learn-harness-engineering (MIT) | 2026-10-28 | English lectures L01–L12 and projects 01–06 were folded into `ai-engineering/03-harness/notes/` (practice track `notes/practice/P1–P4` plus additions to notes 01, 02, 05, 07, 08). Templates from the course and the harness-creator skill were merged into `03-harness/templates/` (removed 2026-10-31: key snippets inline in notes 06, 09, 10; the rest is on the galactus handoff list, in history at `6ee939f`). The practice track became notes 09–10 (the exercises built on it were deleted 2026-10-31). Mapping and dropped material are in `03-harness/references.md`. The Electron projects, translations, site tooling and the rest of the skill were dropped. L13 and project 07 (loop engineering) were set aside for `04-loop/`. |
| `ai-engineering/readings/ai-agent-book-main` (vendored 2026-07-30) | https://github.com/bojieli/ai-agent-book (Apache-2.0) | 2026-10-28 | Bojie Li, *AI Agents in Depth*. The English chapters were synthesised into the pillar notes, each citing its chapter upstream: ch. 1 → `generative-ai/03-agentic-foundations/notes/01-agent-fundamentals.md` and `03-harness-engineering` note 01; ch. 2 → `01-prompt-engineering` notes 02, 10 and `02-context-engineering` notes 02, 05; ch. 3 → `02-context-engineering` notes 04, 06 and `05-graph-engineering` note 11; ch. 4–5 → `03-harness-engineering` notes 01–07; ch. 6 → `generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md`; ch. 7 → `06-eval`; ch. 8 → `generative-ai/05-RL/notes/05-post-training-for-agents.md`; ch. 9 → `04-loop-engineering` note 08 (upstream has since renumbered its chapters; these are the current numbers); ch. 10 → `05-graph-engineering` notes 05, 07. The reference answers were condensed into `interviewing/guides/*/interview-guide.md`. Labs that run offline were copied, translated where needed. On 2026-10-31 the BM25, Elo-leaderboard, trajectory-verifier and self-modifying-agent labs were folded into worked examples (`generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md`, `06-eval` note 05, `04-loop-engineering` note 08) and their copies deleted; they are linked upstream. `generative-ai/05-RL/practice/01-q-learning-treasure-hunt/` remains. Every other lab is linked upstream from the note it supports, because it needs an API key, a GPU or hardware, or is in Chinese. Translations, Chinese originals, site tooling and the local `READING-MAP.md` were dropped. |
| `ai-engineering/02-context/Context-Engineering-main` | https://github.com/davidkimai/Context-Engineering | 2026-10-28 | Synthesized into `02-context-engineering/notes/01–13` + `99` (speculative appendix). Its `templates/` and `notebooks/` were kept until 2026-10-31, then folded into the notes and deleted (in history at `6ee939f`). Cited paper PDFs are in `sources/`, links in `references.md`. |
| `ai-engineering/05-graph-engineering/notebooks/knowledge-graphs-for-rag` | https://github.com/kaushikacharya/Knowledge_Graphs_for_RAG | 2026-10-31 | Folded into `05-graph-engineering/notes/09–11` (in history at `6ee939f`, including the 22 MB `neo4j_L7.dump`). |
| `generative-ai/02-rag-retrieval/Deeplearning.ai-RAG-main` | https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG (MIT) | 2026-10-31 | Condensed into `02-rag-retrieval/notes/02–07`; 6 figures kept in `sources/images/`. The slide decks and certificate were dropped. |
| `generative-ai/03-agentic-foundations/AgenticAIFrameworks-master` | https://github.com/adv-11/AgenticAIFrameworks | 2026-10-31 | Condensed into `03-agentic-foundations/notes/05-framework-survey.md`. A nested `.github/workflows/pdd-secrets-dispatch.yml` that posts repo secrets to a callback URL was found inside it; it never ran (nested workflows are inert) and is deleted, but remains in history. |
| `generative-ai/03-agentic-foundations/LLMs-as-Operating-Systems--Agent-Memory-main` | https://github.com/frankwwu/LLMs-as-Operating-Systems--Agent-Memory | 2026-10-31 | Condensed into `03-agentic-foundations/notes/03-memory-as-an-operating-system.md`; the Letta handbook PDF kept in `sources/`. |
| `generative-ai/03-agentic-foundations/AI-Agentic-Design-Patterns-with-AutoGen-main` | https://github.com/ksm26/AI-Agentic-Design-Patterns-with-AutoGen | 2026-10-31 | Condensed into `03-agentic-foundations/notes/04-multi-agent-design-patterns.md`. |
| `generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main` | https://github.com/ksm26/AI-Agents-in-LangGraph | 2026-10-31 | Condensed into `04-agentic-frameworks/notes/01–02`. |
| `generative-ai/04-agentic-frameworks/Long-Term-Agentic-Memory-With-LangGraph-main` | https://github.com/YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph | 2026-10-31 | Condensed into `04-agentic-frameworks/notes/03-long-term-memory-with-langgraph.md`. |
| `generative-ai/06-observability/Learning-LangFuse-main` | https://github.com/pedroalexleite/Learning-LangFuse | 2026-10-31 | Condensed into `06-observability/notes/02-scoring-datasets-experiments.md`. |
| `generative-ai/06-observability/langfuse-evaluation-main` | https://github.com/gustavobrieva1/langfuse-evaluation | 2026-10-31 | Condensed into `06-observability/notes/03-judge-pipelines-over-trace-exports.md`. Only the generic design was kept; the client-specific material was dropped. |
| `generative-ai/06-observability/langfuse-mcp-python-main` | https://github.com/Log-LogN/langfuse-mcp-python | 2026-10-31 | Condensed into `06-observability/notes/04-langfuse-mcp-server.md`. |
| `generative-ai/07-agentic-applications/internet-search-agent-main` | https://github.com/omidreza-amrollahi/internet-search-agent (MIT) | 2026-10-31 | Condensed into `07-agentic-applications/notes/01-internet-search-agent.md`; the code is linked upstream as legacy (the Bing Search API was retired in August 2025). |
| `data-analytics/Bayes/CamDavidsonPilon-Probabilistic-Programming-and-Bayesian-Methods-for-Hackers-5b33f77` | https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers (MIT) | 2026-10-31 | Condensed into `data-analytics/notes/09-bayesian-inference.md` and the Bayesian notes after it. |
| `data-analytics/Bayes/bayesian_inference_talk-main` | https://github.com/prasoon2211/bayesian_inference_talk | 2026-10-31 | Condensed into `data-analytics/notes/09-bayesian-inference.md`. |

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

`data-analytics/practice/BayesianML/` (formerly `Bayes/BayesianML/`) is **not** a snapshot despite its old `-master` suffix. It is
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
