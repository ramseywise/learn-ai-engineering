# Third-party material

What this repository copied from other people, recorded so its origin and licence are not lost.
Notes written here cite their own sources in frontmatter or in a pillar's `references.md`. This file
covers only material that was **copied in**, and it does not grant any rights in that material.

## Still in this repository

`programming/`, one data-analytics pillar and `programming/drills/coding/dsa/` vendor **exercises and data**,
not course snapshots. They are the practice surface, so they stay, and each keeps its licence. The full list of sources is in
[programming/references.md](programming/references.md).

| Path | Upstream | Licence | What's here |
|---|---|---|---|
| `programming/typescript/practice/typescript-exercises/` | https://github.com/typescript-exercises/typescript-exercises | MIT | 15 exercises with solutions. Patches for TypeScript 7 are listed in its `NOTICE.md` |
| `programming/typescript/practice/type-challenges/challenges/` | https://github.com/type-challenges/type-challenges | MIT | 26 easy and medium challenges with their test cases. The solutions are written here |
| `programming/sql/practice/data/survey.db` | https://github.com/swcarpentry/sql-novice-survey | CC-BY 4.0 | The Antarctic survey database (committed, 8 KB) |
| `programming/sql/practice/data/clubdata.sql` | https://pgexercises.com/ | CC BY-SA 3.0 | PGExercises club data converted from Postgres to SQLite. `clubdata.db` is built from it and gitignored |
| `programming/sql/practice/data/sql-murder-mystery.db` | https://github.com/NUKnightLab/sql-mysteries | MIT | Downloaded by `setup.sh`, gitignored |
| `programming/drills/coding/dsa/` | https://github.com/dileeppandey/hello-interview | MIT, (c) 2019 Dileep Pandey | "Hello, Interview!" data structures and algorithms material, with its `LICENSE` kept alongside. Its problem statements derive from LeetCode, which the licence does not cover |
| `data-analytics/01-python-for-data-analysis/practice/mckinney/` | https://github.com/wesm/pydata-book (`2nd-edition`) | MIT (code) | Chapter notebooks restored from history (they were deleted in commit `1c72b00`). `examples/` and `datasets/` (~240 MB) are downloaded by `fetch_data.sh` and gitignored |

**Paraphrased, not vendored:** Charles Severance's *Python for Everybody* (CC BY-NC-SA 3.0) and the
TypeScript Handbook (CC-BY 4.0). No book text, slides or `mbox` data files are copied. Practice files
use their own sample data.

`data-analytics/04-bayesian-analysis/practice/BayesianML/` is **not** a snapshot despite its old
`-master` suffix. It is Coursera coursework with a `final_assignment/` that exists nowhere else, so it
was renamed on 2026-10-28 to keep suffix-based rules from sweeping it up.

## Vendored snapshots

ZIP downloads of other people's public repositories (hence the `-main` and `-master` suffixes):
read-reference material, not authored here. They were downloaded as ZIPs, so no nested `.git/config`
records the upstream. Each URL was resolved by matching directory contents, not names. Verified
2026-08-14: no third-party or hand-authored edits inside them. Each one is condensed into notes and
then deleted, as the [definition of done](https://github.com/ramseywise/librarian/blob/main/.claude/skills/pillar/references/pillar-layout.md#definition-of-done)
requires.

None remain. Every snapshot listed on 2026-08-14 was condensed into notes and removed by 2026-10-31,
and each now has a row below.

## Removed snapshots

Paths in this table are as they stood on the removal date. Some pillars have since been renamed or
moved.

| Directory | Upstream | Removed | What was kept |
|---|---|---|---|
| `ai-engineering/01-prompt-engineering/Prompt-Engineering-Guide-main` (originally `01-prompt/`) | https://github.com/dair-ai/Prompt-Engineering-Guide (MIT) | 2026-10-28 | Its English `pages/` content was merged into `ai-engineering/01-prompt-engineering/notes/`, with sources in each note's frontmatter. The notebooks were kept as `ai-engineering/01-prompt-engineering/notebooks/` and the lecture PDF as `notes/dair-prompt-engineering-lecture.pdf` (deleted 2026-10-30, superseded by `01-prompt-engineering/slides/`). The upstream `img/` folder was restored on 2026-10-28 (upstream commit `5767372`) as `sources/dair-prompt-engineering-guide/images/`. The Next.js site code and translations were dropped. Re-clone the upstream repo if you need them. |
| `ai-engineering/03-harness/learn-harness-engineering-main` (gitignored, never tracked) | https://github.com/walkinglabs/learn-harness-engineering (MIT) | 2026-10-28 | English lectures L01–L12 and projects 01–06 were folded into `ai-engineering/03-harness/notes/` (practice track `notes/practice/P1–P4` plus additions to notes 01, 02, 05, 07, 08). Templates from the course and the harness-creator skill were merged into `03-harness/templates/` (removed 2026-10-31: key snippets are inline in notes 06, 09 and 10; the rest is in history at `6ee939f`). The practice track became notes 09–10 (the exercises built on it were deleted 2026-10-31). Mapping and dropped material are in `03-harness/references.md`. The Electron projects, translations, site tooling and the rest of the skill were dropped. L13 and project 07 (loop engineering) were set aside for `04-loop/`. |
| `ai-engineering/readings/ai-agent-book-main` (vendored 2026-07-30) | https://github.com/bojieli/ai-agent-book (Apache-2.0) | 2026-10-28 | Bojie Li, *AI Agents in Depth*. The English chapters were synthesised into the pillar notes, each citing its chapter upstream: ch. 1 → `generative-ai/03-agentic-foundations/notes/01-agent-fundamentals.md` and `03-harness-engineering` note 01; ch. 2 → `01-prompt-engineering` notes 02, 10 and `02-context-engineering` notes 02, 05; ch. 3 → `02-context-engineering` notes 04, 06 and `05-graph-engineering` note 11; ch. 4–5 → `03-harness-engineering` notes 01–07; ch. 6 → `generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md`; ch. 7 → `06-eval`; ch. 8 → `generative-ai/05-RL/notes/05-post-training-for-agents.md`; ch. 9 → `04-loop-engineering` note 08 (upstream has since renumbered its chapters; these are the current numbers); ch. 10 → `05-graph-engineering` notes 05, 07. The reference answers were condensed into the interview guides under `practice/interviewing/`. Labs that run offline were copied, translated where needed. On 2026-10-31 the BM25, Elo-leaderboard, trajectory-verifier and self-modifying-agent labs were folded into worked examples (`generative-ai/02-rag-retrieval/notes/01-rag-pipeline.md`, `06-eval` note 05, `04-loop-engineering` note 08) and their copies deleted; they are linked upstream. `generative-ai/05-RL/practice/01-q-learning-treasure-hunt/` remains. Every other lab is linked upstream from the note it supports, because it needs an API key, a GPU or hardware, or is in Chinese. Translations, Chinese originals, site tooling and the local `READING-MAP.md` were dropped. |
| `ai-engineering/02-context/Context-Engineering-main` | https://github.com/davidkimai/Context-Engineering | 2026-10-28 | Synthesized into `02-context-engineering/notes/01–13` + `99` (speculative appendix). Its `templates/` and `notebooks/` were kept until 2026-10-31, then folded into the notes and deleted (in history at `6ee939f`). Cited paper PDFs are in `sources/`, links in `references.md`. |
| `ai-engineering/05-graph-engineering/notebooks/knowledge-graphs-for-rag` | https://github.com/kaushikacharya/Knowledge_Graphs_for_RAG | 2026-10-31 | Folded into `05-graph-engineering/notes/09–11` (in history at `6ee939f`, including the 22 MB `neo4j_L7.dump`). |
| `generative-ai/02-rag-retrieval/Deeplearning.ai-RAG-main` | https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG (MIT) | 2026-10-31 | Condensed into `02-rag-retrieval/notes/02–07`; 6 figures kept in `sources/images/`. The slide decks and certificate were dropped. |
| `generative-ai/03-agentic-foundations/AgenticAIFrameworks-master` | https://github.com/adv-11/AgenticAIFrameworks | 2026-10-31 | Condensed into `03-agentic-foundations/notes/05-framework-survey.md`. A nested `.github/workflows/pdd-secrets-dispatch.yml` that posts repo secrets to a callback URL was found inside it; it never ran (nested workflows are inert) and is deleted, but remains in history. |
| `generative-ai/03-agentic-foundations/LLMs-as-Operating-Systems--Agent-Memory-main` | https://github.com/frankwwu/LLMs-as-Operating-Systems--Agent-Memory | 2026-10-31 | Condensed into `03-agentic-foundations/notes/03-memory-as-an-operating-system.md`; the Letta handbook PDF kept in `sources/`. |
| `generative-ai/03-agentic-foundations/AI-Agentic-Design-Patterns-with-AutoGen-main` | https://github.com/ksm26/AI-Agentic-Design-Patterns-with-AutoGen | 2026-10-31 | Condensed into `03-agentic-foundations/notes/04-multi-agent-design-patterns.md`. |
| `generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main` | https://github.com/ksm26/AI-Agents-in-LangGraph | 2026-10-31 | Condensed into `04-agentic-frameworks/notes/01–02`. |
| `generative-ai/04-agentic-frameworks/Long-Term-Agentic-Memory-With-LangGraph-main` | https://github.com/YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph | 2026-10-31 | Condensed into `04-agentic-frameworks/notes/03-long-term-memory-with-langgraph.md`. |
| `generative-ai/06-observability/Learning-LangFuse-main` | https://github.com/pedroalexleite/Learning-LangFuse | 2026-10-31 | Condensed into `06-observability/notes/02-scoring-datasets-experiments.md`. |
| `generative-ai/06-observability/langfuse-evaluation-main` | https://github.com/gustavobrieva1/langfuse-evaluation | 2026-10-31 | Condensed into `06-observability/notes/03-judge-pipelines-over-trace-exports.md`. Only the generic design was kept. |
| `generative-ai/06-observability/langfuse-mcp-python-main` | https://github.com/Log-LogN/langfuse-mcp-python | 2026-10-31 | Condensed into `06-observability/notes/04-langfuse-mcp-server.md`. |
| `generative-ai/07-agentic-applications/internet-search-agent-main` | https://github.com/omidreza-amrollahi/internet-search-agent (MIT) | 2026-10-31 | Condensed into `07-agentic-applications/notes/01-internet-search-agent.md`; the code is linked upstream as legacy (the Bing Search API was retired in August 2025). |
| `data-analytics/Bayes/CamDavidsonPilon-Probabilistic-Programming-and-Bayesian-Methods-for-Hackers-5b33f77` | https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers (MIT) | 2026-10-31 | Condensed into `data-analytics/notes/09-bayesian-inference.md` and the Bayesian notes after it. |
| `data-analytics/Bayes/bayesian_inference_talk-main` | https://github.com/prasoon2211/bayesian_inference_talk | 2026-10-31 | Condensed into `data-analytics/notes/09-bayesian-inference.md`. |
| `data-engineering/06-ml-platform/practice/datatalks-mlops` (not listed above before its removal) | https://github.com/DataTalksClub/mlops-zoomcamp (**no licence**; matches commit `e34bf8f` plus line-ending, link and dependency-pin changes) | 2026-11-03 | No files. Coverage was already in `data-engineering/06-ml-platform/notes/`, `03-transform-and-orchestrate/notes/02-orchestrate.md` and `05-quality-and-observability/notes/02-monitors-and-lineage.md`; three small gaps were paraphrased with citations. Ledger: `.claude/docs/datatalks-mlops-fold.md` |

## Practice material: upstreams with no licence

Drills and interview material were condensed from these upstream repositories. **None of these
upstreams carries a licence**, and a repository with no licence grants no right to copy or redistribute
it. This table records where the material came from. It is not permission to reuse it, and clearing it is
still open.

What is published differs by folder. Under `practice/`, only files named in `practice/.gitignore` are
tracked, so the condensed interview material stays ignored until rewritten or cleared. Under
`programming/drills/` there is no allowlist: `coding/algorithms/`, `coding/implementation/`,
`coding/ml-coding/` and `python/advanced/` have been tracked since they moved there in commit `0edb94cf`,
before any of them was cleared.

Upstreams were confirmed through the GitHub API on 2026-10-28. The snapshots were condensed on
2026-10-29 and then deleted, so re-clone an upstream to see the original.

| Snapshot | Upstream | Licence | Condensed into |
|---|---|---|---|
| `ai-engineering-gym-main` | https://github.com/alexeygrigorev/ai-engineering-gym | None | Coding drills in `programming/drills/coding/` (`algorithms/`, `implementation/`, `ml-coding/`); the theory bank in `practice/interviewing/rounds/technical-questions/` |
| `ai-engineering-field-guide-main` | https://github.com/alexeygrigorev/ai-engineering-field-guide | None | `practice/interviewing/question-bank.md`; take-home field data in `practice/interviewing/rounds/case-study/` |
| `ai-system-design-interview-studio-main` | https://github.com/alexeygrigorev/ai-system-design-interview-studio | None | Interviewer personas and topic briefs in `practice/interviewing/rounds/system-design-round/` |
| `fifty-advanced-python-concepts-master` | https://github.com/gostak-dd/fifty-advanced-python-concepts (formerly under `GGyll/`; GitHub redirects) | None | `programming/drills/python/advanced/` |

Two more items have the same gap:

- `ai-engineer-test-main`, an "AI Property Search" take-home with **no known upstream** and so no
  known licence. The copy in `practice/interviewing/rounds/coding-challenge/examples/` is ignored by git.
  The copy in `programming/drills/coding/problems/property-search/` has been tracked since commit
  `0edb94cf`, and clearing it is still open.
- `programming/drills/coding/algorithms/`: besides the `ai-engineering-gym` row above, 87 of its 89 drills
  name a LeetCode problem as their `source:`. Their prompts derive from LeetCode, and no licence here
  covers those problem statements.

## Kept locally because no licence covers them

These stay on disk for personal practice and are listed in the root `.gitignore`. No licence covers
them, so they are not published. They were tracked from commit `0edb94cf` until they were removed from
the index, and they remain in git history from that commit.

| Path | What's there |
|---|---|
| `programming/drills/python/hackerrank/` | Solutions to HackerRank Python problems |
| `programming/drills/sql/hackerrank/` | Solutions to HackerRank SQL problems |
| `programming/drills/typescript/hackerrank/` | Solutions to HackerRank TypeScript problems |

`programming/drills/python/leetcode/` is ignored for the same reason and was never tracked. It is a nested
git repository holding another nested repository (`zqfang/LeetCode`), personal notebooks and a PDF of
*Competitive Programmer's Handbook*.
