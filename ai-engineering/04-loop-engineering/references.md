---
origin: curated
sources:
  - https://github.com/dair-ai/AI-Papers-of-the-Week
confidence: medium
cleaned: 2026-10-31
---
# Loop Engineering — Papers and Further Reading

> The papers behind the chapters in [notes/](notes/). PDFs of the arXiv papers are in [sources/](sources/). Course index: [README](README.md).

---

## Books

| | Source | Notes |
|---|---|---|
| ★ | Michael Albada, *Building Applications with AI Agents* (O'Reilly, 2025). Chapter PDFs in [sources/building-applications-with-ai-agents/](sources/building-applications-with-ai-agents/) (ch. 11, 13); ch. 3 is in [harness engineering's sources](../03-harness-engineering/sources/building-applications-with-ai-agents/). Folded in as: ch. 3 → [07](notes/07-autonomy-ladder.md#who-chooses-the-rung); ch. 11 → [08](notes/08-self-improving-loops.md); ch. 13 → [07](notes/07-autonomy-ladder.md#the-human-side-of-the-ladder). Ch. 11's escalation thresholds and bandit numbers are the author's rules of thumb, and its first DSPy snippet uses a retired API. Notes cite it as `(*Building Applications with AI Agents*, ch. N)` | 07, 08 |
| ★ | Mayo Oshin and Nuno Campos, *Learning LangChain* (O'Reilly, 2025). Chapter PDFs in [generative-ai/01-llm-fundamentals/sources/learning-langchain/](../../generative-ai/01-llm-fundamentals/sources/learning-langchain/). Folded in as: ch. 8 → [07](notes/07-autonomy-ladder.md#why-each-rung-costs-reliability), [10](notes/10-framework-bindings.md#langchain--langgraph). Its `interrupt_before` and `gpt-3.5-turbo` code is dated. Notes cite it as `(*Learning LangChain*, ch. N)` | 07, 10 |

## AI Papers of the Week

Recent papers picked up by the weekly [DAIR](https://github.com/dair-ai/AI-Papers-of-the-Week) sync (`make papers`, then `/papers`).

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| Ren et al. (KAUST), [*Self-Improvements in Modern Agentic Systems: A Survey*](https://arxiv.org/abs/2607.13104) (Jul 2026) | Sorts self-improvement into updates to model weights and updates to the scaffold. Recommends treating the critic as governed infrastructure that only changes monotonically (for example, by adding tests) behind a human audit trail, and warns that committed lessons can turn a one-off injection into a permanent one. A taxonomy with no new experiments | [2607.13104](sources/ren-2026-self-improvements-modern-agentic-systems.pdf) | [08](notes/08-self-improving-loops.md#self-modification-as-a-release-process) |
| ★ Wang et al. (Ai2, UW), [*Rethinking the Evaluation of Harness Evolution for Agents*](https://arxiv.org/abs/2607.12227) (Jul 2026) | On Terminal-Bench 2.1, at the same budget of five attempts per task, harness evolution (AHE) does not beat plain retries: 67.4% pass@1 without unit tests, against 72.3% for parallel sampling. Its held-out gain is flat on average (+1.2 / 0.0 / −1.4 points across three models). It does help on long-horizon games with rich feedback: ARC-AGI-3 rises from 43.3 to 77.5 with Claude Opus 4.8 | [2607.12227](sources/wang-2026-rethinking-evaluation-harness-evolution-agents.pdf) | [08](notes/08-self-improving-loops.md#measuring-the-evolve-loop-itself) · [08](notes/08-self-improving-loops.md#bilevel-autoresearch) |
| Liu et al. (Yale), [*Metacognition in LLMs: Foundations, Progress, and Opportunities*](https://arxiv.org/abs/2607.11881) (Jul 2026) | A survey: models predict their own success better than chance, but that signal rarely changes their behaviour, and they struggle to decide when to keep going or stop. Read it before trusting a model's own "done" | [2607.11881](sources/liu-2026-metacognition-llms.pdf) | [07](notes/07-autonomy-ladder.md#1--turn-based-hand-off-tool-approval) |
| ★ Zhang et al. (UBC, Sakana AI), [*Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents*](https://arxiv.org/abs/2505.22954) (May 2025) | A coding agent that edits its own code and keeps an archive of past versions to branch from. SWE-bench Verified goes from 20.0% to 50.0% over 80 iterations. Always branching from the current best reaches 39.7%, and keeping only the latest version reaches 23.0%. Also documents an agent hacking a hidden checker by deleting the markers the checker read. About USD 22,000 per run | [2505.22954](sources/zhang-2025-darwin-godel-machine.pdf) | [08](notes/08-self-improving-loops.md#updating-the-update-method) |
| Zelikman et al. (Microsoft, Stanford), [*Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation*](https://arxiv.org/abs/2310.02304) (Oct 2023) | A scaffold that improves programs is run on its own source code, while the model stays fixed. An improver tuned on one task carries over to others (3SAT: 21.2% → 75.1%), but it mostly fails with GPT-3.5. GPT-4 turned off the sandbox in 0.42% of 10,000 attempts, and budget limits written into the prompt got dropped | [2310.02304](sources/zelikman-2023-self-taught-optimizer-stop.pdf) | [08](notes/08-self-improving-loops.md#updating-the-update-method) |
