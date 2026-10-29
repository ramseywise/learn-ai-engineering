# 06 — Eval Engineering

> Depth layer. Summary: [interviewing/guides/6-evals-observability](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/6-evals-observability/00-overview.md)
> Position in the stack: *measures every layer below*.
> Jump to: [Rules of thumb](#rules-of-thumb) · [Topic notes](#topic-notes-notes) · [References](#references)

---

## What it is

Eval engineering is the discipline of measuring non-deterministic AI systems: defining what "correct" means, building tasks that represent real use, choosing graders you can trust, running them repeatedly, reading the results with error bars, and wiring them into CI, releases and production monitoring.

It's a peer layer, not a QA step. Every other layer makes claims ("this prompt is better", "this harness is more reliable"), and this is where they get checked. Each layer keeps its own chapter on *what* to measure ([01/09](../01-prompt-engineering/notes/09-evaluating-prompts.md), [02/12](../02-context-engineering/notes/12-evaluating-context.md), [03/05](../03-harness-engineering/notes/05-verification-loops.md), [04/03](../04-loop-engineering/notes/03-the-scorekeeper.md)). This topic owns *how*: the shared machinery.

**Inherits the weaknesses of:** all the layers it measures, plus its own. It can only grade what the harness exposes (no traces, no trajectory evals), and an eval is only as good as its tasks, its graders and its sample size.

Overview note: [eval-engineering.md](eval-engineering.md), covering the thesis, where evals sit in the stack and the core flow.

---

## The mental model

An eval is a **measurement of a non-deterministic system**, so it has the same parts as any experiment:

```
task  ×  k trials  →  trajectory + outcome  →  graders  →  scores  →  aggregate ± error bar  →  decision
```

Four questions, in order. Each one depends on the answer before:

| Question | If you skip it | Chapters |
|---|---|---|
| **What does correct mean?** | Graders measure noise; two experts disagree | [02](notes/02-defining-correct.md) |
| **Which tasks represent real use?** | Precise answers to the wrong question | [03](notes/03-eval-datasets.md) |
| **Can the grader be trusted?** | Confidently wrong scores | [04](notes/04-graders.md), [05](notes/05-llm-as-judge.md) |
| **Is the difference real?** | Shipping noise | [09](notes/09-reading-results.md) |

---

## Rules of thumb

The rules from the topic notes on one page. Each group links to the chapter that explains it.

**Before any grader** ([01](notes/01-what-an-eval-is.md), [02](notes/02-defining-correct.md))
- **Write success down first**: what the user needs, what must never happen, the unit of success, the cost of being wrong.
- **Two experts should reach the same verdict.** If they don't, fix the criteria, not the grader.
- **Read 50–100 traces before choosing metrics.** Open code, then axial code. Build graders for the failures you actually saw.
- Deterministic behavior gets **unit tests**. Non-deterministic behavior gets **evals**. Never assert an exact LLM string in a unit test.

**The dataset** ([03](notes/03-eval-datasets.md))
- **Start with 20–50 real failures**, hand-reviewed. Grow from production failures.
- Include **negative and boundary cases**, or "does it more often" looks like an improvement.
- A gate scores only rows that are **eligible** for it. Version the dataset; keep a held-out split.

**Graders** ([04](notes/04-graders.md), [05](notes/05-llm-as-judge.md))
- **Code first.** A judge only where code can't check it.
- **One judge, one criterion, binary verdict**, critique before verdict, a `CANNOT_GRADE` escape.
- **An uncalibrated judge never gates a release.** Calibrate against 100–200 human labels; report TPR and TNR.
- Judge with a **different model family** from the system under test. Run pairwise judges in both orders.

**Agents and RAG** ([06](notes/06-evaluating-agents.md), [07](notes/07-evaluating-rag-and-grounding.md))
- **Grade outcome and trajectory.** Check end state, not what the agent says it did.
- **Run each task k times.** Report pass^k for anything a user gets one try at.
- Score retrieval and generation **separately**, and generation only where retrieval succeeded. Check grounding **claim by claim**.

**Reading and gating** ([08](notes/08-tracing-and-observability.md), [09](notes/09-reading-results.md), [10](notes/10-evals-in-ci.md))
- **Trace every step**, with passage text and version attributes. Scores attach to spans.
- **Every number gets an error bar.** On 50 tasks, ±11 points. Compare versions **paired** on identical tasks; **slice** before concluding.
- **Run, then assert.** Gate on the CI against a baseline, with per-slice floors and an efficiency budget.

**Production** ([11](notes/11-production-and-the-maturity-ladder.md), [12](notes/12-failure-modes.md))
- **Sample 10–20% of traffic by rule** (👎, high cost, long conversations) plus a random slice for rates. Humans calibrate the judge layer.
- When a score drops, debug **infra → versions → traces → slices → only then the agent**.
- Saturated tasks graduate to regression. Every production failure becomes a row.

---

## Where to start

- **New to evals:** [eval-engineering.md](eval-engineering.md), then chapters 01–05 in order. **01–05 can be read right after [01-prompt-engineering](../01-prompt-engineering/README.md)**; they don't need the harness or loop layers.
- **Evaluating an agent now:** [02](notes/02-defining-correct.md#find-failure-modes-by-reading-error-analysis), [06](notes/06-evaluating-agents.md), [08](notes/08-tracing-and-observability.md), then [Labs 1–4](practice/01-exercises.md).
- **Evaluating RAG:** [07](notes/07-evaluating-rag-and-grounding.md) with [02/12](../02-context-engineering/notes/12-evaluating-context.md), and the [case study](notes/case-study/README.md).
- **A number moved and you don't know why:** [09](notes/09-reading-results.md), then [12](notes/12-failure-modes.md#the-debug-order).
- **Shipping:** [10](notes/10-evals-in-ci.md), [11](notes/11-production-and-the-maturity-ladder.md).

---

## Layout

```
06-eval/
├── README.md                     ← you are here: summary, rules of thumb, chapter index
├── eval-engineering.md           ← pillar overview
├── notes/                        ← the chapters (read in order)
│   └── case-study/               ← a real multi-agent support system's eval design, including its mistakes
├── notebooks/
│   └── evaluating-ai-agents/     ← DeepLearning.AI course notebooks (Phoenix), labs 1–5
├── practice/
│   ├── 01-exercises.md           ← eight labs, one system, vibes → monitored
│   └── 02-elo-leaderboard/       ← Elo / Bradley–Terry from pairwise votes (AI Agents in Depth, lab 6-6)
├── templates/                    ← dataset schema, taxonomy, judge prompt, calibration sheet, gate contract, CI workflow
├── sources/                      ← papers filed for this pillar
└── references.md                 ← papers and further reading, mapped to chapters
```

### Topic notes ([notes/](notes/))

**Foundations**
1. [What an eval is](notes/01-what-an-eval-is.md) — task, trial, trajectory, outcome, grader, suite; system under test vs. eval harness; test vs. eval; capability vs. regression; offline vs. online.
2. [Defining "correct"](notes/02-defining-correct.md) — success criteria, the two-expert test, error analysis (open and axial coding), criteria drift, the failure taxonomy, positive and negative cases, dimensions.
3. [Eval datasets](notes/03-eval-datasets.md) — size by stage, sources, synthetic data along dimensions, harvesting failures, coverage, row pools and eligibility, row schema, splits and versioning.

**Grading**

4. [Graders](notes/04-graders.md) — code, model and human graders; layering; the grader interface; grader states; combining scores; binary vs. scales.
5. [LLM-as-judge and calibration](notes/05-llm-as-judge.md) — judge shapes, prompt structure, decomposition, known biases, calibration against human labels (TPR, TNR, κ), correcting the pass rate, keeping it calibrated.

**Applying it**

6. [Evaluating agents](notes/06-evaluating-agents.md) — outcome vs. trajectory, state checks, tool-call matching, component evals, pass@k vs. pass^k, efficiency metrics, multi-turn and simulated users.
7. [Evaluating RAG and grounding](notes/07-evaluating-rag-and-grounding.md) — per-stage metrics, retrieval metrics, claim-level faithfulness, grounding tiers, citation checks, frameworks.
8. [Tracing and observability](notes/08-tracing-and-observability.md) — trace anatomy, the six questions, OTel GenAI conventions, tools, traces → evals → datasets, cost attribution.

**Deciding**

9. [Reading results](notes/09-reading-results.md) — error bars, how many tasks, paired comparisons, repeats and clustering, slicing, metric pitfalls, a report template.
10. [Evals in CI](notes/10-evals-in-ci.md) — what runs when, run-then-assert, regression gates, the gate ladder, a CI workflow, ownership.
11. [Production and the maturity ladder](notes/11-production-and-the-maturity-ladder.md) — the ladder (levels 0–4), online sampling, two-layer review, drift, A/B tests, feedback, the improvement loop.
12. [When evals go wrong](notes/12-failure-modes.md) — eval bugs that look like agent bugs, the debug order, saturation, Goodhart, overfitting, contamination, judge drift, eval debt.

### Notebooks

[notebooks/evaluating-ai-agents/](notebooks/evaluating-ai-agents/README.md): DeepLearning.AI's *Evaluating AI Agents* course. Lab 1 builds the sales-data agent the other labs evaluate; labs 2–5 trace it, add router and skill evals, add trajectory evals and run experiments in Phoenix.

### Practice

[practice/01-exercises.md](practice/01-exercises.md): eight labs on one system. Labs 2–5 pair with the course notebooks:

| Lab | Course notebook | Chapters |
|---|---|---|
| 1 — Error analysis | — | [02](notes/02-defining-correct.md), [03](notes/03-eval-datasets.md) |
| 2 — Tracing | [Lab 2](notebooks/evaluating-ai-agents/lab-2/Lab2.ipynb) | [08](notes/08-tracing-and-observability.md) |
| 3 — Router and skill evals | [Lab 3](notebooks/evaluating-ai-agents/lab-3/Lab3.ipynb) | [04](notes/04-graders.md), [06](notes/06-evaluating-agents.md) |
| 4 — Trajectory and repeats | [Lab 4](notebooks/evaluating-ai-agents/lab-4/Lab4.ipynb) | [06](notes/06-evaluating-agents.md) |
| 5 — Experiments | [Lab 5](notebooks/evaluating-ai-agents/lab-5/Lab5.ipynb) | [09](notes/09-reading-results.md) |
| 6 — Calibrate a judge | — | [05](notes/05-llm-as-judge.md) |
| 7 — Gate it in CI | — | [10](notes/10-evals-in-ci.md) |
| 8 — Online | — | [11](notes/11-production-and-the-maturity-ladder.md), [12](notes/12-failure-modes.md) |

[practice/02-elo-leaderboard](practice/02-elo-leaderboard/README.md): build a leaderboard from pairwise votes with online Elo and Bradley–Terry, recover a known ranking from simulated battles, then judge pairs with an order-swapping LLM judge. Pairs with [05](notes/05-llm-as-judge.md#pairwise-ranking-elo-and-bradleyterry). Runs offline: `python cli.py`.

### Templates

[templates/](templates/): [evalset.schema.json](templates/evalset.schema.json), [failure-taxonomy.md](templates/failure-taxonomy.md), [judge-prompt.md](templates/judge-prompt.md), [judge-calibration.md](templates/judge-calibration.md), [gate-contract.md](templates/gate-contract.md), [eval.yml](templates/eval.yml).

### Case study

[notes/case-study/](notes/case-study/README.md): the eval design for a multi-agent, RAG-grounded support system — routing vs. domain evals, the full gate contract, claim-level grounding, and judge calibration results (including inverted off-the-shelf metrics and a grounding check that failed for an eval reason).

### Related
- [support-agent-observability.md](../../generative-ai/06-observability/support-agent-observability.md) — trace metadata and experiment-tracking schema for the case-study system; two-layer human + judge strategy.
- [Learning-LangFuse-main](../../generative-ai/06-observability/Learning-LangFuse-main/) and [langfuse-evaluation-main](../../generative-ai/06-observability/langfuse-evaluation-main/) — Langfuse course code.

### Interviewing guide
- [6-evals-observability](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/6-evals-observability/00-overview.md) — compressed summary for interview prep. This folder is the source of depth; if they drift, this folder wins.

---

## References

Papers and guides mapped to chapters: [references.md](references.md). **★** marks the ones to read first.

- ★ Anthropic, [*Demystifying evals for AI agents*](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): the backbone of chapters 01, 04, 06
- ★ Husain & Shankar, [*A field guide to rapidly improving AI products*](https://hamel.dev/blog/posts/field-guide/): error analysis, chapter 02
- ★ Zheng et al., [*Judging LLM-as-a-Judge*](https://arxiv.org/abs/2306.05685): judge biases, chapter 05
- ★ Miller, [*Adding Error Bars to Evals*](https://arxiv.org/abs/2411.00640): statistics, chapter 09
- ★ Yao et al., [*τ-bench*](https://arxiv.org/abs/2406.12045): pass^k, chapter 06

---

## Working References

Claude Code convention references that map to this pillar. These files live at `~/.claude/refs/` and can be consulted in any Claude Code session.

### `agent-eval.md`
Knowing whether a change made the system better, at what confidence, and what is unit-testable vs. only eval-testable.
- Unit/eval seam: deterministic behavior → unit tests; non-deterministic behavior → evals ([01](notes/01-what-an-eval-is.md))
- Grader interface contract and grader states: heuristic, calibrated, experimental ([04](notes/04-graders.md))
- Gate ladder: data quality → retrieval → generation → grader calibration → release ([10](notes/10-evals-in-ci.md#the-gate-ladder))
- Failure taxonomy labels and golden dataset curation rules ([02](notes/02-defining-correct.md#the-failure-taxonomy), [03](notes/03-eval-datasets.md))

### `agent-observability.md`
What a trace must contain to debug a bad run after the fact, and how to attribute cost.
- Four span types (`invoke_agent`, `chat`, `execute_tool`, `retrieve`) under a root span ([08](notes/08-tracing-and-observability.md#anatomy-of-a-trace))
- Cost attribution by agent, route and user; cache hit rate ([08](notes/08-tracing-and-observability.md#cost-and-latency-attribution))
- `finish_reason: max_tokens` is an error, not a completion
- The six questions a complete trace must answer; OTel GenAI conventions and their gaps (quality, safety and grounding scoring are project-local)

### `verification.md`
The verification ladder and generator/evaluator separation, from the harness side ([03/05](../03-harness-engineering/notes/05-verification-loops.md)).
