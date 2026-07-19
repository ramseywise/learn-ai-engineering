# Example: Eval Pipeline for an LLM Product

## Prompt
"Design an evaluation system for an LLM-powered product. How do you know the system is working, and how do you catch regressions?"

## Step 1: Clarify & scope (3 min)

**Questions I'd ask**:
- What kind of product? (RAG QA, agent, chatbot, summarization — eval strategy differs)
- What does "working" mean for this product? (Accuracy? Safety? User satisfaction? All?)
- How often do changes ship? (Daily deploys need automated gates; monthly releases can include human review)
- Existing eval infrastructure? (Nothing? Ad hoc scripts? Langfuse/Braintrust?)
- Budget for eval compute? (LLM-as-judge costs real money at scale)

**Assumptions after clarify**:
- RAG-based product with agent capabilities, daily deploys
- "Working" means: faithful answers, relevant retrieval, no safety violations, acceptable latency
- Starting from ad hoc scripts — need to build a real pipeline
- Moderate budget — can afford LLM-as-judge but need to be smart about it

## Step 2: Requirements (2 min)

**Functional**: Automated eval gate on every deploy, regression detection, capability benchmarking, online quality monitoring, human feedback integration.

**Non-functional**: Eval run completes in < 15 min (doesn't block deploy pipeline), false-alarm rate < 10% (noisy gates get bypassed), cost < $5/eval run.

## Step 3: Design (15 min)

### Three-tier eval architecture

```
Tier 1: Deterministic checks (every deploy, < 2 min, $0)
  → Format validation (JSON schema, required fields)
  → Safety pattern matching (PII in output, blocked phrases)
  → Latency regression (p95 vs baseline)
  → Basic assertion tests (known-answer queries)

Tier 2: LLM-as-judge (every deploy, < 10 min, ~$2)
  → Golden set: 100 curated query-answer-context triples
  → Graders:
    - Faithfulness: "Does the answer make claims not supported by the retrieved context?"
    - Relevance: "Does the answer address the question?"
    - Completeness: "Does the answer cover the key points from the context?"
  → Each grader: rubric + 1-5 scale + reasoning
  → Aggregate: per-grader mean + standard deviation
  → Gate: fail if any grader mean drops > 0.3 from baseline

Tier 3: Human evaluation (weekly sample, ~$50)
  → Random sample of 20 live queries
  → Expert annotators score on same rubric as LLM-as-judge
  → Purpose: calibrate the judge, detect systematic judge bias
  → Output: updated calibration weights for Tier 2
```

### Golden set design

The golden set is the foundation — if it's wrong, everything downstream is wrong.

- **Construction**: Start from real user queries (sampled from logs, anonymized). Expert writes the reference answer and marks the expected retrieval evidence.
- **Size**: 100 examples minimum. Stratified by query type (factual, synthesis, multi-hop, adversarial).
- **Maintenance**: Review quarterly. Add examples from production failures (every thumbs-down that reveals a real issue gets a golden-set entry). Remove stale examples when the product scope changes.
- **Versioning**: Golden set has a version number. Historical eval results reference which version they ran against — comparisons across versions are flagged.

### Online monitoring (continuous, not just at deploy)

```
Live traffic → Sample 5% of queries
  → Run Tier 1 checks on every sampled query
  → Run Tier 2 graders on 1% (cost control)
  → Dashboard: quality score over time, latency percentiles, cost per query
  → Alerts:
    - Quality score drops > 2 stddev from 7-day rolling mean
    - Latency p95 exceeds SLA
    - Safety violation detected (any count > 0)
```

### Feedback loop

```
User thumbs-down → Human reviews the query+response
  → If real issue: add to golden set, tag the failure type
  → If false alarm: note as "user disagreed, quality acceptable"
  → Monthly: analyze failure types → prioritize fixes
```

### Key trade-off narrated

**LLM-as-judge vs human eval**: LLM judges are fast and cheap but have systematic biases (position bias, length bias, verbosity preference). Human eval is reliable but slow and expensive. Solution: use LLM-as-judge for continuous monitoring, human eval for periodic calibration. The human layer detects when the judge drifts.

**Golden set size vs maintenance cost**: Larger golden sets catch more regressions but are expensive to maintain. 100 well-curated examples with quarterly review beats 1000 stale ones. Quality over quantity.

**Gate sensitivity**: Too sensitive → false alarms → team bypasses the gate. Too lenient → regressions ship. Start strict, tune based on false alarm rate. Target: < 10% false alarms.

## Step 4: Shortcomings (3 min)

- **Distribution drift**: Golden set represents the query distribution at creation time. If user behavior shifts, the golden set becomes unrepresentative. Mitigation: periodic refresh from live traffic samples.
- **Adversarial blind spot**: Golden set doesn't include adversarial inputs (prompt injection, edge cases). Need a separate adversarial test suite.
- **Judge calibration drift**: The LLM-as-judge may change behavior across model versions. Mitigation: re-calibrate against human labels whenever the judge model is updated.
- **Multi-turn gap**: Single-turn eval is easier than multi-turn conversation eval. For chat products, need trajectory-level grading, not just per-turn.

## Step 5: Close with measurement (2 min)

**Eval system's own metrics**: Gate false alarm rate < 10%, eval run time < 15 min, Tier 2 judge correlation with human labels > 0.85, golden set freshness (% of examples < 6 months old).

**Product metrics enabled by eval**: Faithfulness > 0.9 on golden set, safety violation rate = 0, latency p95 < SLA, regression detection within 1 deploy.

**Future**: Capability benchmarks (new-feature testing beyond regression), A/B eval framework for prompt/model experiments, automated golden-set enrichment from production failures.

---

**Study refs**: [evals guide §2-5](../../../guides/6-evals-observability/interview-guide.md) for grader types, three-tier taxonomy, and calibration; librarian wiki: System Design — Unified Eval Harness, RAG Evaluation; [agents guide §8](../../../guides/4-agents/interview-guide.md) on Pass@k vs Pass^k.
