---
origin: synthesis
sources:
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 10"
  - https://www.promptingguide.ai/applications/workplace_casestudy
  - https://arxiv.org/abs/2303.07142
confidence: high
cleaned: 2026-10-28
---
# 9 — Evaluating Prompts

> How you know a prompt change helped. This is the prompt-level view; eval systems for whole agents and harnesses are in [06-eval](../../06-eval/README.md).

---

## Build the eval first

The evaluation framework is the oldest part of the GitHub Copilot codebase — older than the prompts or the UI. Without one, every change is a guess. **Always log latency and token counts too**: they're cheap to capture and catch regressions that have nothing to do with quality.

What you're testing determines the shape of the eval:

| Target | Decision | Test style |
|---|---|---|
| **The model** | Swap or upgrade | Broad regression suite |
| **A single prompt** | Wording, examples, parameters | Small unit tests on one model call |
| **The composition** (chain, loop) | Architecture | End-to-end regression — no unit-level substitute |

If you can build only one, build the **end-to-end** one, then add unit tests on the critical path.

---

## Offline: the tech tree

**Level 1 — the example suite.** 5–20 realistic inputs, plus a script that renders each one into your prompt, calls the model, and writes prompt + completion to files. Commit them and review with `git diff`. It isn't pass/fail — you eyeball each change. It works from your very first draft, and repeated exposure to the same examples teaches you the failure modes.

**Level 2 — the harness.** Hundreds to thousands of examples with **automatic scoring**, needed to see subtle effects. It has two independent problems: **where samples come from** and **how outputs are scored**.

### Sourcing samples

| Source | Strength | Watch out for |
|---|---|---|
| **Existing records** — data from people solving the same problem without AI | Realistic and plentiful | Similarity vs. scale. Copilot stripped function bodies out of open-source repos to simulate "cursor here" |
| **App telemetry** | Real inputs | Doesn't exist before launch; app changes invalidate it; consent and privacy; outputs are biased by what your app suggested |
| **Synthetic** (LLM-generated) | Cheap, controllable coverage — combine aspects (n × m × l) for spread | Tropes and misconceptions; **bias toward the generating model** if it's also a candidate under test |

### Scoring outputs

From most to least rigorous:

1. **Gold-standard match.** Exact match for labels; *partial* match on the one aspect that matters for free text. Choose an aspect that separates breaking from benign divergence. For tool calls, test in order — *called a tool? → right tool? → valid syntax? → right values?* — because an early failure invalidates the later checks.
2. **Functional test.** Does it parse, compile, pass the repo's own unit tests, and call only tools that exist with correctly typed arguments? The domain supplies the oracle.
3. **LLM-as-judge** — for qualities like helpfulness and tone. See below.

**Multi-turn:** use **canned conversations** (score each turn against a scripted history — isolates turns but misses compounding errors) or an **LLM-mocked user** (end-to-end, but inherits the mock's biases).

---

## LLM-as-judge

**Never let the model know it's grading its own work.** Self-grading gets pulled two ways at once: forum-style pretraining data isn't known for objective self-reflection, and RLHF trains the model to defer at any hint of doubt. Frame the work as a third party's.

**SOMA** — a rubric recipe:

| | Rule | Why |
|---|---|---|
| **S**pecific questions | "Did it pick the heating system?" — not "Is this right?" | A generic question is as hard as the task, and more ambiguous |
| **O**rdinal scale | 1–5, with each level described | Yes/no hides degrees; undefined levels drift between runs |
| **M**ulti-**A**spect | Score each dimension separately — e.g. **intent** (right plan?) vs. **execution** (carried out correctly?); Copilot used relevance / truth / completeness | One composite score lets the judge silently switch criteria |

Also:
- **Rubric before content.** The judge reads once, forward only ([01](01-how-models-read-prompts.md#property-3--left-to-right-attention-order-matters)), so put the aspects first, then the example.
- **Scores are relative.** "81% correct" means little alone; "B is judged correct more often than A" is the valid claim.
- **Calibrate against humans.** Use several annotators, not one. The bar is that adding the model (temperature 0) to the pool *doesn't increase* disagreement (e.g., Kendall's τ).
- Reasoning models make strong judges ([07](07-prompting-reasoning-models.md#where-reasoning-models-earn-their-cost)), and pairing a judge with a prompt rewriter gives you an optimizer ([08](08-prompt-optimization.md)).

---

## Online evaluation

Offline eval is a lab. Live traffic is the only valid test — but its bandwidth is scarce, so **whittle candidates down offline first**.

**A/B testing:** define **success metrics** and **guardrail metrics** *before* starting. Compare randomly assigned users only — "already updated" vs. "not yet" is a biased split.

Metrics, from most direct to most incidental:

| Kind | Example | Note |
|---|---|---|
| Direct feedback | 👍/👎, "which is better?" | High quality but intrusive; captures frustration more than delight |
| Functional correctness | Compiled, booked, sent | Concrete, often binary |
| **User acceptance** | Suggestion kept, link clicked | For Copilot, it predicted productivity better than fancier measures |
| Achieved impact | Share of the final email written by the assistant | Outcome-side |
| Incidental | Latency, conversation length | Ambiguous alone; track them to catch shifts |

---

## Case study: small changes, large effects

Clavié et al. (2023) classified job postings as "graduate-suitable" with `gpt-3.5-turbo`, adding one prompt modification at a time:

| Prompt | F1 | Template adherence |
|---|---|---|
| Baseline (posting + question) | 65.6 | 79% |
| Few-shot CoT | 78.4 | 87% |
| Zero-shot CoT | 81.4 | 65% |
| + role in system, task in user | 87.5 | 71% |
| + mocked acknowledgement turn + reiterated key points | 89.3 | 75% |
| + **strict output template** | 86.3 ↓ | **98%** |
| + "reach the right conclusion" + info on common failures | 90.3 | 77% |
| + give the model a name + positive feedback | **91.7** | 81% |

Lessons:
- **Prompt wording moved F1 by 26 points** — more than the gap to a strong fine-tuned DeBERTa baseline, which the LLM beat.
- **Zero-shot CoT beat few-shot CoT** on a task that needed no expert knowledge. The examples anchored the model ([03](03-core-techniques.md#few-shot)).
- **Forcing a strict template lowered accuracy** while raising adherence. Parse loosely, or constrain the format in a separate step ([04](04-controlling-output.md#structured-output)).
- Instructions plus **reiteration** of the key points was the biggest single driver.
- The tiny gains (a name, +0.6) are model-specific and dated. **The methodology is the lesson: change one thing, re-score.**

---

## Go deeper

- Book: [Ch 10](../sources/prompt-eng-for-llms/10-evaluating-llm-applications.md) (offline tech tree, SOMA, online metrics)
- Eval systems and grounding methodology: [06-eval](../../06-eval/README.md) · [eval-harness.md](../../06-eval/eval-harness.md) · [eval-maturity-ladder.md](../../06-eval/eval-maturity-ladder.md)
- Papers and tools: [references.md](../references.md#evaluation)

---

→ Next: [10-adversarial-prompting.md](10-adversarial-prompting.md) — prompts that attack your prompts.
