# Vendored Course Repos

Upstream snapshots kept in this repo for reference. These are ZIP downloads of other
people's public repositories (hence the `-main` / `-master` suffixes) — read-reference
material, not source authored here.

**These directories are currently tracked in git.** This file is documentation, not a
policy change: it records where each snapshot came from so the provenance is not lost,
and so any future decision to untrack them is reversible by re-clone rather than
guesswork.

Verified 2026-08-14: 14 directories, 886 tracked files, ~127.1 MB. Every commit touching
these paths is authored by `ramseywise`, `Ramsey Wise`, or `dependabot[bot]` — there are
no third-party edits and no hand-authored changes inside them.

Because the snapshots were taken as ZIP downloads, no nested `.git/config` records the
upstream. The URLs below were resolved by matching directory contents against the
candidate repository — not by name similarity — and each is marked with how it was
confirmed.

| Directory | Upstream | Snapshot date | Tracked | Notes |
|---|---|---|---|---|
| `ai-engineering/02-context/Context-Engineering-main` | https://github.com/davidkimai/Context-Engineering | 2026-08-14 | 298 files / 45.1 MB | Largest snapshot. Curation of the useful subset is #105. |
| `generative-ai/03-agentic-foundations/AgenticAIFrameworks-master` | https://github.com/adv-11/AgenticAIFrameworks | 2026-08-14 | 124 files / 1.3 MB | Content-matched (upstream adds `sf_ml_th/`). |
| `generative-ai/03-agentic-foundations/LLMs-as-Operating-Systems--Agent-Memory-main` | https://github.com/frankwwu/LLMs-as-Operating-Systems--Agent-Memory | 2026-08-14 | 109 files / 16.1 MB | Includes 1 PDF (`handbook.pdf`). Exact content match. DeepLearning.AI × Letta course. |
| `generative-ai/02-rag-retrieval/Deeplearning.ai-RAG-main` | https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG | 2026-08-14 | 103 files / 27.2 MB | Includes 6 PDFs (5 module slide decks + certificate). Exact content match. |
| `generative-ai/06-observability/langfuse-evaluation-main` | https://github.com/gustavobrieva1/langfuse-evaluation | 2026-08-14 | 56 files / 0.8 MB | Exact content match. Dependabot entry removed (see below). |
| `generative-ai/07-agentic-applications/internet-search-agent-main` | https://github.com/omidreza-amrollahi/internet-search-agent | 2026-08-14 | 39 files / 0.1 MB | Content-matched. Dependabot entry removed (see below). |
| `generative-ai/04-agentic-frameworks/Long-Term-Agentic-Memory-With-LangGraph-main` | https://github.com/YunghuiHsu/Long-Term-Agentic-Memory-With-LangGraph | 2026-08-14 | 39 files / 0.8 MB | Exact content match. Dependabot entry removed (see below). |
| `generative-ai/06-observability/langfuse-mcp-python-main` | https://github.com/Log-LogN/langfuse-mcp-python | 2026-08-14 | 36 files / 0.2 MB | Content-matched. Dependabot entry removed (see below). |
| `ai-engineering/05-graph/Knowledge_Graphs_for_RAG-main` | https://github.com/kaushikacharya/Knowledge_Graphs_for_RAG | 2026-08-14 | 34 files / 27.3 MB | Exact content match. Contains a 22 MB `neo4j_L7.dump`. |
| `generative-ai/03-agentic-foundations/AI-Agentic-Design-Patterns-with-AutoGen-main` | https://github.com/ksm26/AI-Agentic-Design-Patterns-with-AutoGen | 2026-08-14 | 14 files / 1.7 MB | Exact content match. |
| `generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main` | https://github.com/ksm26/AI-Agents-in-LangGraph | 2026-08-14 | 12 files / 0.5 MB | Exact content match. |
| `generative-ai/06-observability/Learning-LangFuse-main` | https://github.com/pedroalexleite/Learning-LangFuse | 2026-08-14 | 9 files / 0.1 MB | Exact content match. |
| `data-analytics/Bayes/BayesianML-master` | ⚠️ unresolved — see note below | 2026-08-14 | 8 files / 0.1 MB | **Not a vendored snapshot — appears to be your own coursework.** Course: https://www.coursera.org/learn/bayesian-methods-in-machine-learning |
| `data-analytics/Bayes/bayesian_inference_talk-main` | https://github.com/prasoon2211/bayesian_inference_talk | 2026-08-14 | 5 files / 5.8 MB | Exact content match. |

## `BayesianML-master` is misfiled

This directory carries a `-master` suffix, which makes it *look* like a vendored snapshot,
but it is almost certainly not one. Its `README.md` links a Coursera course rather than a
repository, and its structure (`week_2`, `week_4`–`week_6`, `final_assignment`,
`bayesian.yml`) matches no public GitHub repo checked — including every repo named
`BayesianML` and the official `hse-aml/bayesian-methods-for-ml`, which uses `week2` (no
underscore) and has no `final_assignment`.

It reads as a **personal MOOC working copy containing completed assignments**. The course
notebooks are re-obtainable from `hse-aml/bayesian-methods-for-ml`; the work in
`final_assignment/` is not obtainable from anywhere.

Practical consequence: any future rule keyed on the `-main`/`-master` suffix would sweep
this directory up with the genuine snapshots and put irreplaceable work at risk. Renaming it
(dropping `-master`) or moving it out of `Bayes/` alongside the vendored talk repo would make
its status self-evident.

## Nested repositories

Three directories contain their own `.git` directory. They are **not** submodules and their
contents are not tracked:

- `ai-engineering/readings/AI-Papers-of-the-Week/.git`
- `programming/Leet-Code/.git`
- `programming/Leet-Code/LeetCodeCheat/.git`

Verified 2026-08-14: `git ls-files -s | awk '$1=="160000"'` returns **0 gitlink entries**,
and all three paths have **0 tracked files** — they are already covered by existing
`.gitignore` rules (`programming/Leet-Code/`, `*ai-engineering/readings/AI-Papers-of-the-Week`).

`.gitmodules` is intentionally absent. Earlier analysis (LAE-106 research) described these as
"a live hazard"; verification shows there is nothing broken to repair — they are plain
untracked directories on disk. No action needed. This note exists so the state is not
re-investigated.

## Dependabot

`.github/dependabot.yml` previously carried 13 `directory:` entries, four of which pointed
into vendored snapshots above (`Long-Term-Agentic-Memory-With-LangGraph-main`,
`langfuse-evaluation-main`, `langfuse-mcp-python-main`, `internet-search-agent-main`).
Those four were removed — bumping dependencies inside a read-only upstream snapshot produces
PR noise with no benefit, and it was the source of the 10–29 commit counts on those
directories. Nine entries remain, all pointing at real project directories.

## Repository size context

Measured 2026-08-14 while investigating LAE-106, recorded here because it is the useful part
of that analysis:

- `size-pack` is **1.42 GiB**; the working tree is ~1.5 GB.
- **414 tracked PDFs account for ~1.10 GiB — 73% of tracked bytes.** The vendored source
  snapshots documented above total ~127 MB, an order of magnitude less.
- PDFs are spread across pillars: `ai-engineering` 248, `generative-ai` 134,
  `data-analytics` 13, `data-science` 12, `data-engineering` 6.
- The single largest tracked blob is `generative-ai/05-RL/2-llm-rlhf/RLbook2020.pdf` at 70 MB.

Two consequences worth knowing before any future cleanup:

1. **Untracking files does not shrink a clone.** Blobs remain in history, so `size-pack`
   stays 1.42 GiB regardless. Reclaiming space requires rewriting history
   (`git filter-repo` / `git lfs migrate`), which force-pushes a public repo with a live fork.
2. **If size ever becomes the problem, the PDFs are the target, not these directories.**
