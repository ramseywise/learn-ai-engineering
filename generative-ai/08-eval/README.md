# 08 — Eval Engineering

> Interview recall: the checklists in these notes. Role map: [interviewing](../../practice/interviewing/README.md).
> Position in the path: eighth pillar of generative-ai, moved from ai-engineering. It *measures every layer*: the five ai-engineering foundations (prompt, context, harness, loop, graph) and the generative-ai pillars that build on them.
> Jump to: [Rules of thumb](#rules-of-thumb) · [Topic notes](#topic-notes-notes) · [References](#references)

---

## What it is

Eval engineering is the discipline of measuring non-deterministic AI systems: defining what "correct" means, building tasks that represent real use, choosing graders you can trust, running them repeatedly, reading the results with error bars, and wiring them into CI, releases and production monitoring.

It's a peer layer, not a QA step. Every other layer makes claims ("this prompt is better", "this harness is more reliable"), and this is where they get checked. Each layer keeps its own chapter on *what* to measure ([01/09](../../ai-engineering/01-prompt-engineering/notes/09-evaluating-prompts.md), [02/12](../../ai-engineering/02-context-engineering/notes/12-evaluating-context.md), [03/05](../../ai-engineering/03-harness-engineering/notes/05-verification-loops.md), [04/03](../../ai-engineering/04-loop-engineering/notes/03-the-scorekeeper.md)). This topic owns *how*: the shared machinery.

**Inherits the weaknesses of:** all the layers it measures, plus its own. It can only grade what the harness exposes (no traces, no trajectory evals), and an eval is only as good as its tasks, its graders and its sample size.

The thesis, where evals sit in the stack and the core flow open [chapter 01](notes/01-what-an-eval-is.md#why-evals-are-their-own-discipline).

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
| **Can the grader be trusted?** | Confidently wrong scores | [04](notes/04-graders.md), [05](notes/05-llm-as-judge.md), [15](notes/15-calibration-against-human-labels.md), [14](notes/14-calibrating-judges-with-checks-and-critiques.md) |
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

**Graders** ([04](notes/04-graders.md), [05](notes/05-llm-as-judge.md), [15](notes/15-calibration-against-human-labels.md))
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

- **Lecture deck:** [slides/eval-engineering.pptx](slides/eval-engineering.pptx) — the notes as a 5-part talk (source: [slides/deck.yaml](slides/deck.yaml); rebuild with `make slides PILLAR=generative-ai/08-eval`).
- **New to evals:** chapters [01](notes/01-what-an-eval-is.md)–05 in order. **01–05 can be read right after [01-prompt-engineering](../../ai-engineering/01-prompt-engineering/README.md)**; they don't need the harness or loop layers.
- **Evaluating an agent now:** [02](notes/02-defining-correct.md#find-failure-modes-by-reading-error-analysis), [06](notes/06-evaluating-agents.md), [08](notes/08-tracing-and-observability.md).
- **Evaluating RAG:** [07](notes/07-evaluating-rag-and-grounding.md) with [02/12](../../ai-engineering/02-context-engineering/notes/12-evaluating-context.md), and the [case study](notes/13-case-study-support-agent.md).
- **A number moved and you don't know why:** [09](notes/09-reading-results.md), then [12](notes/12-failure-modes.md#the-debug-order).
- **Shipping:** [10](notes/10-evals-in-ci.md), [11](notes/11-production-and-the-maturity-ladder.md).
- **See it all on one real system:** [13](notes/13-case-study-support-agent.md), a multi-agent support system's eval design, including its mistakes.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DA 02/02 Probability foundations](../../data-analytics/02-probability-and-statistics/notes/02-probability-foundations.md) | Base rates under a judge's pass rate |
| [DA 02/04 Estimation](../../data-analytics/02-probability-and-statistics/notes/04-estimation.md) | Standard errors, Wilson intervals and the bootstrap |
| [DA 02/05 Hypothesis testing](../../data-analytics/02-probability-and-statistics/notes/05-hypothesis-testing.md) | Paired tests and multiple comparisons |
| [DA 03/01 A/B testing](../../data-analytics/03-experimentation-and-causality/notes/01-ab-testing.md) | Sample size and peeking |
| [DA 03/03 Experimentation at scale](../../data-analytics/03-experimentation-and-causality/notes/03-experimentation-at-scale.md) | SRM, CUPED and looking early |
| [DS 01/04 Model evaluation](../../data-science/01-classical-ml/notes/04-model-evaluation.md) | The confusion matrix under judges and retrieval metrics |
| [DS 02/03 Structuring ML projects](../../data-science/02-deep-learning/notes/03-structuring-ml-projects.md) | Error analysis and dev and test sets |
| [DS 01/12 Reading the errors](../../data-science/01-classical-ml/notes/12-reading-the-errors.md) | The procedure behind 02's error analysis and 14's reading of a judge |
| [GA 06/03 Judge pipelines over trace exports](../06-observability/notes/03-judge-pipelines-over-trace-exports.md) | The planted failures and rule judges behind note 14's exercise |
| [DS 05/02 Collaborative filtering](../../data-science/05-time-series-and-recommenders/notes/02-collaborative-filtering-and-matrix-factorisation.md) | Recall and NDCG |

**Feeds into**

| Chapter | Why |
|---|---|
| [AIE 01/09 Evaluating prompts](../../ai-engineering/01-prompt-engineering/notes/09-evaluating-prompts.md) | Evals for prompts |
| [AIE 02/12 Evaluating context](../../ai-engineering/02-context-engineering/notes/12-evaluating-context.md) | Evals for context |
| [AIE 03/05 Verification loops](../../ai-engineering/03-harness-engineering/notes/05-verification-loops.md) | Graders and CI in the harness |
| [AIE 04/03 The scorekeeper](../../ai-engineering/04-loop-engineering/notes/03-the-scorekeeper.md) | Scoring a loop's passes |
| [AIE 09/05 Red-teaming tools](../../ai-engineering/09-safety-and-security/notes/05-red-teaming-tools.md) | Judges and CI gates for red teaming |

---

## Lab

An eval suite with a CI gate: 24 cases, three graders, a stored baseline, paired regression testing and an exit code. It comes in both languages, side by side, on the same inputs. Both run offline with a stub by default, and each README says how to swap in a real model.

| Language | Folder | Run |
|---|---|---|
| TypeScript | [practice/eval-suite-ci/](practice/eval-suite-ci/README.md) | `cd practice/eval-suite-ci && npx tsx demo.ts` |
| Python | [practice/eval-suite-ci-py/](practice/eval-suite-ci-py/README.md) | `cd practice/eval-suite-ci-py && uv run demo.py` |

Note 14 has its own script, [practice/judge_checks_and_critiques.py](practice/judge_checks_and_critiques.py). It tests the procedure on GA 06's rule judges and measures no real model. Its cue and edit tests need your own model. Run it with `cd practice && uv run judge_checks_and_critiques.py`.

## Layout

```
08-eval/
├── README.md                     ← you are here: summary, rules of thumb, chapter index
├── notes/                        ← chapters 01–14, read in order; figures and code inline
├── slides/                       ← lecture deck (deck.yaml → eval-engineering.pptx)
├── practice/                     ← the lab, in TypeScript and Python
├── sources/                      ← papers filed for this pillar
│   └── images/                   ← every figure the notes and deck use (unreferenced/ holds unused course images)
└── references.md                 ← papers and further reading, mapped to chapters
```

### Topic notes ([notes/](notes))

**Foundations**
1. [What an eval is](notes/01-what-an-eval-is.md) — task, trial, trajectory, outcome, grader, suite; system under test vs. eval harness; test vs. eval; capability vs. regression; offline vs. online.
2. [Defining "correct"](notes/02-defining-correct.md) — success criteria, the two-expert test, error analysis (open and axial coding), criteria drift, the failure taxonomy, positive and negative cases, dimensions.
3. [Eval datasets](notes/03-eval-datasets.md) — size by stage, sources, synthetic data along dimensions, harvesting failures, coverage, row pools and eligibility, row schema, splits and versioning.

**Grading**

4. [Graders](notes/04-graders.md) — code, model and human graders; layering; the grader interface; grader states; combining scores; binary vs. scales.
5. [LLM as judge](notes/05-llm-as-judge.md) — judge shapes, prompt structure, decomposition, known biases, pairwise ranking with Elo and Bradley–Terry, judge cost.

Read straight after 05:

15. [Calibrating a judge against human labels](notes/15-calibration-against-human-labels.md) — the procedure, TPR, TNR and κ, correcting the pass rate, keeping it calibrated, multi-family judging.

**Applying it**

6. [Evaluating agents](notes/06-evaluating-agents.md) — outcome vs. trajectory, state checks, tool-call matching, component evals, pass@k vs. pass^k, efficiency metrics, multi-turn and simulated users.
7. [Evaluating RAG and grounding](notes/07-evaluating-rag-and-grounding.md) — per-stage metrics, retrieval metrics, claim-level faithfulness, grounding tiers, citation checks, frameworks.
8. [Tracing and observability](notes/08-tracing-and-observability.md) — trace anatomy, the six questions, OTel GenAI conventions, tools, traces → evals → datasets, cost attribution.

**Deciding**

9. [Reading results](notes/09-reading-results.md) — error bars, how many tasks, paired comparisons, repeats and clustering, slicing, metric pitfalls, a report template.
10. [Evals in CI](notes/10-evals-in-ci.md) — what runs when, run-then-assert, regression gates, the gate ladder, a CI workflow, ownership.
11. [Production and the maturity ladder](notes/11-production-and-the-maturity-ladder.md) — the ladder (levels 0–4), online sampling, two-layer review, drift, A/B tests, feedback, the improvement loop.
12. [When evals go wrong](notes/12-failure-modes.md) — eval bugs that look like agent bugs, the debug order, saturation, Goodhart, overfitting, contamination, judge drift, eval debt.

**Worked example**

13. [Case study: a multi-agent support system](notes/13-case-study-support-agent.md) — routing vs. domain evals, free labels from metadata, an eight-gate ladder with row pools and a failure taxonomy, claim-level grounding, grader selection against user sentiment, calibration results (including inverted off-the-shelf metrics and a grounding check that failed for an eval reason).

**Going deeper**

14. [Calibrating judges with checks and critiques](notes/14-calibrating-judges-with-checks-and-critiques.md) — code checks against the judge, errors by slice, coding the critiques, and cue and edit tests of whether a critique reports what drove the verdict. It comes after the case study because it needs 09's multiple comparisons and uses 13's cases, but you can read it straight after 05 if you're calibrating a judge now.

### Course code

DeepLearning.AI's [*Evaluating AI Agents*](https://www.deeplearning.ai/short-courses/evaluating-ai-agents/) course ([runnable notebooks upstream](https://github.com/ginny100/DeepLearning.AI-Evaluating-AI-Agents), with the data and helpers they need). Lab 1 builds the sales-data agent the other labs evaluate; labs 2–5 trace it, add router and skill evals, add trajectory evals and run experiments in Phoenix. The instructive code is folded into the notes: router and skill evals and convergence in [06](notes/06-evaluating-agents.md#evaluate-the-components-then-the-whole), tracing in [08](notes/08-tracing-and-observability.md#anatomy-of-a-trace), the v1-vs-v2 experiment in [09](notes/09-reading-results.md#a-worked-example-that-needs-this).

Pairwise ranking (Elo and Bradley–Terry) is a worked example in [05](notes/05-llm-as-judge.md#worked-example-online-elo-vs-a-bradleyterry-fit). The full runnable lab is upstream at [ai-agent-book/chapter7/elo-leaderboard](https://github.com/bojieli/ai-agent-book/tree/main/chapter7/elo-leaderboard): run `pip install -r requirements.txt && python quickstart.py`, offline, with no API key.

### Copy-ready snippets

Trimmed templates live inline in the chapter that teaches them: the failure-taxonomy skeleton in [02](notes/02-defining-correct.md#the-failure-taxonomy), the row schema and its enums in [03](notes/03-eval-datasets.md), the judge prompt in [05](notes/05-llm-as-judge.md#writing-the-judge-prompt), the calibration record in [15](notes/15-calibration-against-human-labels.md#the-procedure), and the gate contract and CI workflow in [10](notes/10-evals-in-ci.md).

### Related
- [support-agent-observability.md](../06-observability/notes/05-support-agent-observability.md) — trace metadata and experiment-tracking schema for the case-study system; two-layer human + judge strategy.
- [Learning-LangFuse-main](../06-observability/notes/02-scoring-datasets-experiments.md) and [langfuse-evaluation-main](../06-observability/notes/03-judge-pipelines-over-trace-exports.md) — Langfuse course code.

### Interviewing guide
- [Interviewing](../../practice/interviewing/README.md): role map to these checklists, and the rounds.

---

## Primary texts

- Huyen, *AI Engineering*
- Anthropic, *Demystifying evals for AI agents*
- Husain and Shankar, *A field guide to rapidly improving AI products*
- Li, *AI Agents in Depth*, ch. 7

Everything else: [references.md](references.md).

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
The verification ladder and generator/evaluator separation, from the harness side ([03/05](../../ai-engineering/03-harness-engineering/notes/05-verification-loops.md)).
