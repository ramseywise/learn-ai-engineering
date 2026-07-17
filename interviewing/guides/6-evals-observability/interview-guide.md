# Evals & Observability — Study Guide

The topic that separates "built a demo" from "shipped a system." Nearly every 2026 loop asks
some form of *"how do you test non-deterministic outputs?"* — this guide is that answer.

## 1. Vocabulary (get these crisp)

- **Task / trial / grader**: a task is one test (inputs + success criteria); a trial is one
  attempt (outputs vary → run several); a grader scores one aspect (correctness, tool use,
  policy, efficiency). One task can have many graders.
- **Trajectory vs outcome**: outcome = did it achieve the goal (final environment state);
  trajectory = did it get there acceptably (full record: tool calls, reasoning, intermediate
  steps). Grade both — right answer via unsafe path fails; good process killed by a flaky
  tool isn't an agent bug.
- **Agent harness vs eval harness**: the runtime being tested vs the infrastructure that runs
  tasks, records traces, applies graders, aggregates. The eval harness treats the agent
  harness as the *system under test*.
- **Offline vs online eval**: curated dataset runs vs scored live traffic.

## 2. Grader types — choose the simplest reliable one

1. **Code/deterministic** — string/structure match, unit tests, state checks. Highest
   certainty; always prefer when a clear correct answer exists.
2. **LLM-as-judge** — rubric scoring, pairwise comparison, multi-model voting. For semantic
   quality. Judges have systematic biases → calibrate against a human-labeled set and
   re-check for drift.
3. **Human** — expert sampling, annotation. Slow, reliable; sets the ground truth that
   calibrates layer 2.

## 3. The three-tier taxonomy (cost-ordered)

| Tier | What | Properties | Coverage |
|---|---|---|---|
| 1 Unit | tool selection, param extraction, routing, formatting | deterministic, CI-safe, no LLM calls | **~70% of regressions** |
| 2 Trajectory | ordered node/tool sequence with mocked tools | semi-deterministic, traced, cost-gated | routing/path failures |
| 3 End-to-end | final answer quality (LLM judge, RAGAS/DeepEval) | most realistic, most expensive | release quality gates only |

Interview move: when asked "how would you eval this agent," walk the tiers bottom-up and say
where each failure class gets caught — cheap tiers first is the judgment being tested.

## 4. Non-determinism: pass@k vs pass^k

- **pass@k** — at least one of k trials succeeds. Measures the *capability ceiling*.
- **pass^k** — all k trials succeed. Measures *deployment reliability*: 75% per-trial success
  → pass^3 ≈ 0.75³ ≈ 42%. Customer-facing agents live and die by pass^k.

**Capability vs regression suites**: capability evals ask "what can it do?" (low pass rates
fine); regression evals ask "does it still do everything it used to?" (~100% required).
Saturated capability evals graduate into the regression suite.

## 5. Building an eval system from scratch (the checklist answer)

1. Define success criteria *before* collecting data.
2. Start with **20–50 real failures**, manually reviewed — not a big noisy benchmark.
3. Include **negative cases** (restraint/boundary behavior), or the agent "improves" by
   overacting.
4. Unambiguous tasks: two domain experts would reach the same verdict; vague rubric = noisy
   metric.
5. **Reset the environment every trial** — contamination makes env problems look like agent
   failures.
6. Simplest reliable grader per task (code → LLM → human).
7. **Read traces, not just scores** — aggregates say *that* something changed, traces say
   *why* (grader bugs, unexpected tool use, unsafe successes).
8. Keep expanding the frontier: regression suite of known failures + rolling discovery set
   from production.

**Maintenance rule that interviewers love:** when scores drop, **fix the eval system before
touching the agent**. Debug order: infra errors/timeouts → failed traces + grader decisions
→ concentration in one task category → only then the agent.

## 6. Observability

- **Hierarchy**: observability ⊃ tracing (per-request execution record) ⊃ monitoring
  (aggregated health) ⊃ alerting. Traces are the prerequisite for debugging agents at all.
- **Two-layer online evaluation**: layer 1 = rule-based *human sampling* (errors, long
  dialogues, negative feedback) producing labeled calibration data; layer 2 = LLM judge over
  broad traffic, calibrated by layer 1. Either alone fails: judge-only drifts, human-only
  doesn't scale.
- **Online sampling rules** (not random): score 10–20% of traces — negative-feedback
  triggers, high-token dialogues (agent circling), fixed time-window samples, and **48h full
  review after any model/prompt change**.
- **Drift monitoring**: baseline metrics at validation time, same scoring pipeline on
  production traffic, alert on divergence. Causes: model updates, input shift, upstream API
  changes, seasonality.
- **Platforms**: Langfuse vs LangSmith — Langfuse is open-source/self-hostable (GDPR-friendly,
  native ragas/deepeval integration); LangSmith is tighter with the LangChain stack. Have a
  reasoned pick; either answer works if justified.

## 7. RAG-specific metric suite (for RAG-heavy roles)

Runtime: faithfulness/groundedness, answer relevance, contextual relevance, naturalness.
Offline: completeness, recall@k, document precision, calibration. Retrieval ranking: MRR,
nDCG, hit rate. Claim-level grounding: verify each cited claim appears in retrieved evidence
(tiered hard-fail vs log-only). RAGAS covers the standard four (faithfulness,
answer_relevancy, context_precision, context_recall).

## 8. The production management layer (the "what else" answer)

The agent itself is ~40% of a production deployment; the other 60%: continuous evals in
CI + against live traffic · fallback boundaries + severity-aware escalation · drift
monitoring · **HITL checkpoints that double as the training-data pipeline** (every human
correction is logged signal) · full-trace logging for debugging/compliance/improvement ·
a defined handoff protocol (agent↔agent, agent↔human: what transfers, who owns the outcome).

## 9. Question bank (answer sketches)

- *"How do you test a non-deterministic system?"* — multiple trials per task; pass@k vs
  pass^k; deterministic tiers for what's deterministic; judges calibrated on human labels.
- *"Your agent's score dropped after a deploy."* — eval-system-first debug order (§5); check
  grader + infra before the agent; look for category concentration.
- *"Design the eval for a customer-support agent."* — tiers: intent routing (T1), tool
  trajectories (T2), answer quality + tone + turn-count constraints (T3); adversarial
  conversations; pass^k target; online two-layer scoring with sampling rules.
- *"LLM-as-judge risks?"* — bias (position, verbosity, self-preference), drift, domain shift;
  mitigate with calibration sets, pairwise designs, rubric specificity, periodic human audit.
- *"What do you log?"* — full trajectory: prompts, tool calls + args, retrieved context,
  intermediate outputs, final action; structured fields, not prose.

## Sources

- notes: [eval-harness.md](../../notes/eval-harness.md) (Anthropic demystifying-evals synthesis + production management layer), [observability.md](../../notes/observability.md)
- images: [two-layer eval](../../images/two-layer-eval-human-llm-calibration.png)
- librarian wiki: Anthropic Three-Tier Eval Taxonomy · RAG Eval Metrics Suite · RAG Evaluation · Grounding Claim Methodology · Observability & Evaluation Glossary · HITL Annotation Pipeline · Synthetic Dataset Generation for RAG Eval · Eval Gate Contract · LLM Grader Calibration Insights · Observability — LangFuse vs LangSmith Decision · System Design — Unified Eval Harness
- course refs: `generative-ai/coursera-references/langfuse-evaluation-main`, `DeepLearning.AI-Evaluating-AI-Agents-master`
- external: anthropic.com/engineering/demystifying-evals-for-ai-agents · langchain.com/blog/agent-evaluation-readiness-checklist
