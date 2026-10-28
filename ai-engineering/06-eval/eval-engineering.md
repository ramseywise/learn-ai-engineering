---
origin: synthesis
sources:
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - https://hamel.dev/blog/posts/field-guide/
confidence: high
cleaned: 2026-10-28
---
# Eval Engineering

> Pillar overview. Chapters: [notes/](notes/). Index: [README](README.md).

---

## The thesis

**Every other layer makes claims. Evals are how you check them.** A prompt "works better", a context strategy "reduces hallucination", a harness "is more reliable", a loop "converges". Each of these is a hypothesis about a non-deterministic system, and only a measurement settles it.

Eval engineering is building that measurement: deciding what correct means, collecting tasks that represent real use, choosing graders you can trust, running them repeatedly, reading the results honestly, and wiring them into the places decisions get made (CI, releases, production monitoring).

It's an engineering discipline, not a QA afterthought, for three reasons:

1. **The outputs are non-deterministic.** One run proves nothing. You need rates, repeats and error bars ([09](notes/09-reading-results.md)).
2. **"Correct" is often a judgment.** So graders are themselves models or people, and need to be measured too ([05](notes/05-llm-as-judge.md)).
3. **The eval is software.** It has bugs, drifts and gets gamed. Treat a score drop as a claim about the eval before a claim about the system ([12](notes/12-failure-modes.md)).

---

## Where it sits in the stack

```
01 prompt  →  02 context  →  03 harness  →  04 loop  →  05 graph
    │             │              │             │
    └─────────────┴──────┬───────┴─────────────┘
                         ▼
                 06 eval: the shared machinery
```

Each layer has its own eval chapter that says **what to measure** at that layer:

| Layer | Its eval chapter | Measures |
|---|---|---|
| Prompt | [01/09](../01-prompt-engineering/notes/09-evaluating-prompts.md) | Output quality per prompt version |
| Context | [02/12](../02-context-engineering/notes/12-evaluating-context.md) | Whether the right content reached and was used |
| Harness | [03/05](../03-harness-engineering/notes/05-verification-loops.md) | Verification inside a run |
| Loop | [04/03](../04-loop-engineering/notes/03-the-scorekeeper.md) | The stop condition a loop optimizes against |

This topic owns **how** to measure, for all of them: datasets, graders, judge calibration, statistics, CI gates and production monitoring. That's why it's separate rather than spread across the layers: the machinery is the same everywhere, and duplicating it would let it drift.

---

## The core flow

```
define correct → build tasks → run k trials → capture trajectory + outcome → grade → aggregate with error bars → decide
      ▲                                                                                                      │
      └──────────────────────────── production failures become new tasks ◀───────────────────────────────────┘
```

Each arrow is a chapter:

| Step | Chapter |
|---|---|
| Vocabulary, test vs. eval, eval types | [01](notes/01-what-an-eval-is.md) |
| Define correct, error analysis, failure taxonomy | [02](notes/02-defining-correct.md) |
| Build tasks | [03](notes/03-eval-datasets.md) |
| Grade | [04](notes/04-graders.md), [05](notes/05-llm-as-judge.md) |
| Agent trajectories, k trials | [06](notes/06-evaluating-agents.md) |
| RAG and grounding | [07](notes/07-evaluating-rag-and-grounding.md) |
| Capture traces | [08](notes/08-tracing-and-observability.md) |
| Aggregate and decide | [09](notes/09-reading-results.md) |
| Gate in CI | [10](notes/10-evals-in-ci.md) |
| Production and the loop back | [11](notes/11-production-and-the-maturity-ladder.md) |
| When the eval is wrong | [12](notes/12-failure-modes.md) |

---

## Five ideas that carry the topic

1. **Read before you measure.** Failure modes come from error analysis on real traces, not from a list of generic metrics ([02](notes/02-defining-correct.md#find-failure-modes-by-reading-error-analysis)).
2. **Simplest trustworthy grader.** Code first. A judge only where code can't reach, and only after calibration against people ([04](notes/04-graders.md)).
3. **Grade the path and the destination.** For agents, outcome and trajectory fail independently ([06](notes/06-evaluating-agents.md#outcome-and-trajectory)).
4. **A score without an error bar is an anecdote.** Pair, repeat, slice ([09](notes/09-reading-results.md)).
5. **The suite is alive.** Production failures become rows, saturated tasks graduate to regression, and the maturity ladder is climbed one rung at a time ([11](notes/11-production-and-the-maturity-ladder.md#the-ladder)).

---

## Inherits the weaknesses of

Everything it measures, plus its own: an eval is only as good as its tasks (coverage), its graders (calibration) and its statistics (sample size). A well-built eval on an unrepresentative dataset gives precise answers to the wrong question.
