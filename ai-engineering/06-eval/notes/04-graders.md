---
origin: synthesis
sources:
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - https://www.aibuilderclub.com/blog/how-to-evaluate-ai-agents
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 10"
  - case-study/gate-contract.md
confidence: high
cleaned: 2026-10-28
---
# 4 — Graders

> A grader turns one trial into a score for one dimension. Use the simplest grader that can be trusted: code first, a model above that floor, people to calibrate both.

---

## The three kinds

| Grader | How it scores | Strength | Weakness | Use when |
|---|---|---|---|---|
| **Code** | String/regex match, schema check, unit tests, state check, numeric tolerance | Deterministic, fast, free, hard to argue with | Only checks what you can express exactly | There's a clear right answer or a checkable property |
| **Model** (LLM-as-judge) | A model scores against a rubric, compares two outputs, or votes | Handles meaning, tone, completeness | Biased, costly, needs calibration ([05](05-llm-as-judge.md)) | The quality is semantic and no code can check it |
| **Human** | Expert review, annotation | The ground truth for subjective quality | Slow, expensive, inconsistent at scale | Building the reference, calibrating judges, ambiguous cases |

A fourth kind sits between code and model: the **separated evaluator agent**, which *operates* the output (runs the app, clicks through it, runs the code) instead of reading it ([03/05](../../03-harness-engineering/notes/05-verification-loops.md#separating-generation-from-evaluation)). It's a model, but its verdict rests on observed behavior.

### Layer them, don't choose

The four are layers, not alternatives:

| Layer | Scales | Cost | Role |
|---|---|---|---|
| Code | Fully | ~0 | First line. Catches structural failures cheaply |
| Separated evaluator | Well | Medium | Behavioral verification |
| LLM judge | Fully | Medium | Subjective criteria at volume |
| Human sample | Poorly | High | **Calibrates** the judge. 5–10% of graded rows, not a review queue |

Run code graders first and stop early: an answer that fails the schema doesn't need a judge to tell you it's bad. That saves judge budget for the rows that need judgment.

---

## Code graders: more than you think

Teams reach for a judge too early. Most systems have more checkable properties than they use:

| Property | Code check |
|---|---|
| Output format | JSON parses, matches schema, required fields present |
| Tool use | Right tool name, arguments parse, argument values match ([06](06-evaluating-agents.md#scoring-tool-calls)) |
| Citations | Every cited ID is in the retrieved set. Quoted text appears verbatim in the source ([07](07-evaluating-rag-and-grounding.md#citation-checks-in-code)) |
| Final state | Row exists in the DB, file was written, test suite passes |
| Code output | Compiles, runs, passes the repo's tests |
| Language | Response language matches query language (a language-ID library) |
| Boundaries | Didn't call a forbidden tool, didn't exceed N turns, didn't leak a regex-detectable secret |
| Efficiency | Steps, tokens, latency, cost from the trace |
| Exact facts | Number within tolerance, date matches, entity in an allowed set |

For tool calls, check **in order** and stop at the first failure: *called a tool? → right tool? → valid arguments? → right values?* An early failure makes the later checks meaningless ([01/09](../../01-prompt-engineering/notes/09-evaluating-prompts.md#scoring-outputs)).

### Reference-based text metrics

BLEU, ROUGE and embedding similarity compare an output to a reference string. They're cheap and deterministic but correlate poorly with quality for open-ended answers: a correct answer worded differently scores low. The case study ruled out ROUGE-L for conversational answers for this reason ([case study](../case-study/eval-architecture.md#why-we-use-custom-graders-instead-of-adks-built-in-eval)). Use them for tightly constrained outputs (translation of fixed strings, extraction) or as a cheap tracking signal, not a gate.

---

## The grader interface

Make every grader implement one contract. Then graders are swappable, composable and reportable the same way.

**Input** (what any grader may need):

| Field | Contents |
|---|---|
| `task` | The row: input, reference, labels |
| `output` | The final response / outcome |
| `trajectory` | Tool calls, intermediate messages (optional per grader) |
| `retrieved_context` | Passage **text**, not just IDs or URLs |
| `metadata` | Model, prompt version, config, run ID |

**Output:**

| Field | Contents |
|---|---|
| `score` | Number in [0, 1] (or the native scale, documented) |
| `passed` | Boolean against the grader's threshold |
| `reasoning` | Why. For judges, the explanation. For code, the failing check |
| `dimensions` | Sub-scores, if the grader checks several things |
| `labels` | Failure taxonomy labels this trial earned ([02](02-defining-correct.md#the-failure-taxonomy)) |
| `grader_version` | Name + prompt/code version, so scores are traceable |

```python
class Grader(Protocol):
    name: str
    version: str
    requires: set[str]            # e.g. {"retrieved_context"}: skip, don't guess, if missing
    def grade(self, task, output, trajectory=None, context=None) -> GraderResult: ...
```

The `requires` field matters. A grounding grader handed URLs instead of passage text should return "can't grade" (`context_missing`), not a made-up score ([case study](../case-study/grader-methodology.md#why-the-cross-check-showed-low-agreement)).

---

## Grader states: which ones can block a release

Not every grader is trustworthy enough to gate on. Give each one an explicit state:

| State | Meaning | Can gate releases? |
|---|---|---|
| **Heuristic** | Deterministic code check | Yes |
| **Calibrated** | LLM judge with evidence it agrees with humans ([05](05-llm-as-judge.md)) | Yes, at the calibrated threshold |
| **Experimental** | New or uncalibrated judge | **No.** Tracking and investigation only |

A threshold change without fresh calibration evidence moves the grader back to experimental. Release decisions must name which state each cited metric is in.

---

## Combining graders: scoring design

A task often has several graders. Decide up front how they combine:

| Scheme | Rule | Use when |
|---|---|---|
| **Binary (all-pass)** | Task passes only if every grader passes | Any failure is unacceptable (safety, format, policy) |
| **Weighted** | Weighted sum of scores must clear a threshold | Dimensions trade off legitimately |
| **Hybrid** | Must-pass gates + weighted score on the rest | Most production systems |
| **Report separately** | No composite. Show each dimension | Diagnosis. Always do this alongside any composite |

Hybrid example: *schema valid AND no citation hallucination AND (0.5 × grounding + 0.3 × completeness + 0.2 × relevance ≥ 0.75)*.

Don't let a composite hide a regression. A model that gains 5 points of relevance while losing 5 points of grounding scores flat on the composite and is worse for users who need correct answers. Always report the dimensions too.

---

## Binary vs. scales

For judges and humans, prefer **binary pass/fail** per dimension over 1–5 scales:

- Graders disagree more on the middle of a scale. "Is this a 3 or a 4?" has no stable answer.
- Pass/fail forces you to define the bar, which is the point of [02](02-defining-correct.md).
- Rates of binary outcomes have simple statistics ([09](09-reading-results.md)).

Use an ordinal scale only when the levels are each *described* (what a 2 looks like vs. a 4), and only when the extra resolution changes a decision. If you have a scale, you can always threshold it into pass/fail later.

---

## Checklist

- [ ] Every checkable property has a code grader before any judge is added
- [ ] Code graders run first; failures short-circuit expensive graders
- [ ] All graders implement one interface, with `requires` and `grader_version`
- [ ] Each grader has a state (heuristic / calibrated / experimental)
- [ ] Composite scoring rule written down; dimensions always reported alongside
- [ ] Binary pass/fail by default; scales only with described levels

---

## Working reference

[case-study/harness-patterns.md](../case-study/harness-patterns.md) — four suite types and a tool-trajectory scorer in pytest.

---

→ Next: [05-llm-as-judge.md](05-llm-as-judge.md) — making model graders trustworthy.
