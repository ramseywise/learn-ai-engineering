# Study Guide — Case Study Round

## The one-page template (memorize this)

```
1. Objective & users
2. Constraints (latency, cost/1K tokens, privacy, budget)
3. Data sources
4. Baseline first
5. MVP pipeline sketch
6. Offline + online eval plan
7. Risks & safety
8. Milestones
```

You should be able to write this in 2 minutes from memory. It is your skeleton for every case — live, take-home, or defense. The rest of this guide explains how to fill each section and how to adapt it by case type.

---

## Section-by-section breakdown

### 1. Objective & users

Never accept the stated solution. The interviewer says "a chatbot" — that's an answer, not a problem. Your first move is to interrogate:

- What business outcome is the client trying to move? ("Reduce support costs by 20%", "deflect 40% of tier-1 tickets", "cut time-to-answer from 4h to 5 min")
- Who uses this? Customers? Internal agents? Both?
- What does success look like in 6 months? In 1 year?

State the objective as a number before designing anything. "Reduce support cost per ticket from $12 to $8" is a design constraint. "Improve support" is not.

### 2. Constraints

Work through all four:

| Constraint | Key questions |
|-----------|---------------|
| Latency | "Does the user wait for a response in real time? Sub-second or async?" |
| Cost | "What's the token budget? At GPT-4 rates (~$30/1M output tokens), 1000 tickets/day × 500 tokens = $15/day — does that fit?" |
| Privacy | "Is there PII? Financial data? Healthcare? Does it need to stay on-premise?" |
| Budget | "Is this a pilot ($10K) or a production system ($200K+)?" |

If privacy = sensitive, this drives model selection (no public API → hosted model or on-premise). Say that out loud.

### 3. Data sources

Name what you have and what you need:

- Existing: historical tickets, transcripts, product docs, user data
- Missing: labels, feedback signals, ground truth
- Quality concerns: state them upfront — don't pretend the data is clean

For LLM cases: the retrieval corpus is a data source. Describe its format, freshness, and size order-of-magnitude.

### 4. Baseline first

This is the discipline that separates strong candidates. Before designing the ML system, ask: what's the baseline?

- **ML cases:** a simple heuristic rule, a logistic regression, or a lookup table. What accuracy does it achieve? This anchors the "is ML worth it?" question.
- **LLM cases:** keyword search + a static FAQ. Can it handle 40% of queries at $0/token? Then your LLM layer only needs to handle the remaining 60% — that changes the cost math.

State the baseline metric before the model metric. "Our baseline is 62% accuracy on the test set; we're targeting 78%." Numbers make this concrete.

### 5. MVP pipeline sketch

Describe the end-to-end data flow for the simplest thing that could work. Do not design the final system.

**ML pipeline sketch:**
```
raw data → feature engineering → train/val split → model → prediction → feedback loop
```

**LLM pipeline sketch:**
```
user query → retrieval (BM25 or dense) → context assembly → prompt → LLM → output parser → response
```

**Agent pipeline sketch:**
```
user intent → router → tool selection → tool call → result → synthesis → response
```

Name the components, not the vendors. Then name one vendor choice and justify it briefly ("Pinecone vs. pgvector — we're already on Postgres, pgvector reduces ops overhead").

### 6. Offline + online eval plan

Two separate things — do not conflate them.

**Offline eval (before deploy):**
- What labeled dataset are you evaluating against?
- What metric? And why not the obvious one? ("AUROC over accuracy because the positive class is 8% of the dataset." "Faithfulness over BLEU because we're grounding on retrieved docs.")
- For LLM: RAG-specific metrics — retrieval precision, context relevance, answer faithfulness, completeness

**Online eval (after deploy):**
- What's the leading indicator? (deflection rate, CSAT, error rate, latency p95)
- How do you detect drift? (distribution shift on inputs, degrading metrics week-over-week)
- What's the rollback trigger?

For take-homes: write out the eval plan explicitly. Interviewers treat a thorough eval plan as evidence of production judgment.

### 7. Risks & safety

Name at least three. For AI cases, common ones:

- **Hallucination / incorrect answers** — especially in customer-facing contexts; mitigation: grounding checks, confidence thresholds, human fallback
- **Data leakage / PII in outputs** — mitigation: output filtering, no PII in prompts, audit logging
- **Model drift** — mitigation: scheduled eval runs, retraining triggers
- **Over-reliance / automation bias** — mitigation: UX design with uncertainty signals, human-in-the-loop for high-stakes decisions
- **Bias in training data** — mitigation: demographic breakdowns in eval, fairness metrics

For regulated sectors (finance, healthcare): name the compliance framework (GDPR, HIPAA, SOC 2) and how you'd address it.

### 8. Milestones

Show that you think in phases, not all-or-nothing:

| Week | Milestone |
|------|-----------|
| 1–2 | Data audit, baseline metric established |
| 3–4 | MVP pipeline, offline eval on held-out set |
| 5–6 | Shadow mode deploy (compare to human, no live traffic) |
| 7–8 | Limited A/B (10% traffic), measure deflection rate |
| 9–12 | Full rollout, feedback loop, retraining schedule |

The last milestone should include a measurement close: "We declare success when deflection rate reaches 40% and CSAT holds at ≥4.1/5."

---

## ML case vs. LLM case — how the template adapts

| Section | ML case | LLM case |
|---------|---------|----------|
| Objective | Numeric business target (churn -5%) | Same, but frame around automation rate or cost-per-query |
| Constraints | Inference latency, model size, retraining cadence | Token cost, context window, API rate limits, latency p95 |
| Data sources | Labeled training set, feature store | Retrieval corpus — format, freshness, size |
| Baseline | Heuristic rule or logistic regression | Keyword search + static FAQ |
| Pipeline | Feature eng → train → predict → monitor | Ingest → chunk → embed → index → retrieve → prompt → generate → parse |
| Eval | AUROC, F1, calibration, holdout split | Retrieval precision, faithfulness, completeness, human eval |
| Risks | Leakage, bias, drift | Hallucination, prompt injection, cost blowout, stale index |
| RAG-vs-fine-tune | N/A | Explicit decision: RAG if domain docs are large and changing; fine-tune if style/format is the gap, not knowledge |

---

## ROI arithmetic frameworks

These numbers should come out of your mouth cold. Practice them.

### Token math
```
cost = (input_tokens + output_tokens) × price_per_token
Example: 1000 queries/day × 1500 tokens/query × $0.015/1K tokens = $22.50/day = $675/month
```
At GPT-4 rates, a 1000-query/day system costs ~$600–900/month. A smaller model at 1/10th the price costs $60–90/month. The ROI question is: what's the accuracy gap, and what's the cost of errors?

### Hours-saved math
```
value = hours_saved_per_week × fully_loaded_hourly_rate × 52
Example: 10 hours/week × $80/hour × 52 = $41,600/year
```
A system that saves 10 hours/week of a $80/hr analyst's time is worth ~$42K/year. If the build + infra costs $30K, it pays back in under 9 months.

### Error-cost math
```
risk_exposure = error_rate × volume × cost_per_error
Example: 2% error rate × 5000 decisions/month × $200/error = $20,000/month risk
```
This frames the "how good is good enough?" question. If a 2% error rate on loan approvals costs $20K/month, reducing it to 0.5% is worth up to $15K/month in model improvement costs.

---

## Take-home best practices

### Time allocation (3-hour timebox)
| Phase | Time | What you produce |
|-------|------|-----------------|
| Problem framing + assumptions | 15 min | Written assumptions block, stated objective |
| EDA | 30 min | Distribution plots, leakage check, missing data map |
| Baseline model | 30 min | Logistic regression or simple heuristic, baseline metric |
| Primary model | 45 min | One strong model (XGBoost, LightGBM), tuned |
| Eval + validation | 20 min | Holdout eval, calibration check, top-3 drivers |
| Writeup | 40 min | Memo/notebook narrative (20% of total time) |

### Writeup structure
1. **Assumptions** — first paragraph, always. "I assumed X because Y." Interviewers cannot penalize you for an assumption they didn't correct.
2. **Objective restated as a number** — "I targeted 78% AUROC on the holdout set as a proxy for reducing churn by 5%."
3. **What I built and why** — brief, not exhaustive.
4. **What I found** — the metrics, honestly.
5. **What went wrong / data issues** — shows judgment.
6. **Next steps / not done** — this reads as maturity, not incompleteness. "With two more hours I would: (1) tune the threshold on the validation set, (2) add SHAP values for the top-5 features, (3) test a simple neural net to validate that boosting is the right choice."

### Common take-home failures
- No stated assumptions → every modeling choice looks arbitrary
- Overbuilt model, no baseline → can't demonstrate the ML is adding value
- No eval story → just accuracy on training data = instant fail
- Writeup is an afterthought → graders spend 5 min on your work; the memo is the artifact
- "Not done" section is empty → suggests you think it's complete, which is worse

---

## Defense round preparation

Defense rounds test two things: **depth of understanding** and **growth mindset under challenge**.

### Anticipate the challenge categories

| Challenge | What they're really asking |
|-----------|---------------------------|
| "Why not deep learning?" | Do you know when boosting beats nets on tabular data? |
| "What breaks at 10× scale?" | Can you reason about infrastructure, not just models? |
| "Why this chunking strategy?" | Did you think about it, or just use the default? |
| "What would you cut with one week left?" | Can you prioritize ruthlessly by business value? |
| "The retrieval quality is poor — now what?" | Do you have a systematic debug process? |
| "What went wrong in this project?" | Are you honest and self-aware? |

### How to respond to a challenge

1. **Acknowledge the concern specifically** — don't give a generic "great question." "You're right that gradient boosting typically outperforms at tabular sizes under 100K rows — let me explain why I chose it here."
2. **State the conditions under which you'd change your answer** — "If the dataset were 10M rows and we had 3 months, I'd revisit neural nets. At 50K rows with a 3-week timeline, boosting is the safer default."
3. **Adapt visibly** — if the challenge is valid, update your design on the spot. "Actually, that's a better approach — I'd revise the chunking strategy to use semantic boundaries rather than fixed-size tokens."
4. **Don't defend when you're wrong** — "I missed that. My original assumption was X, but given what you've said, the correct approach is Y."

### "What went wrong" — prepare an honest answer

Pick a real failure from your experience. Structure it:
- What you tried
- What broke (and when you found out)
- What you changed
- What you learned

Consulting-style loops ask for this explicitly. The candidates who pass are specific and undefensive.

---

## Per-format drills

### Live case drill (45 min, solo)
Pick one of the question bank prompts. Set a timer. Run the full template out loud, as if talking to an interviewer. Record yourself. Play it back and check: did you clarify before designing? Did you anchor on a number? Did you name a baseline? Did you close with a measurement story?

### Take-home drill (twice before your loop)
Pick a Kaggle classification dataset. Set a 3-hour timer. Follow the time allocation table above. Write the memo. Then put it away. The next day, read it as if you were the interviewer: does it communicate judgment? Would you hire this person?

### Defense drill
Give your take-home output to a trusted peer. Ask them to challenge: "Why not X?", "What breaks at 10×?", "What would you cut?" Practice adapting out loud rather than defending.

---

## Common mistakes

### Solution-first thinking
Jumping to "we'll use RAG" or "we'll build a classifier" before establishing the objective and constraints. Interviewers see this constantly. It signals that you solve before you understand.

### No numbers
"We'll reduce churn" is not a design anchor. "Reduce churn by 5%, from 8% monthly to 3.8%, which at $200 LTV = $1.2M/year" is. Every claim should have an order-of-magnitude number attached.

### Overbuilding
Designing the ideal final system instead of the MVP. Interviewers want to see phased thinking. "Here's what ships in week 4; here's what we add in week 12 based on what we learned."

### Ignoring constraints
Building the technically elegant solution that violates the latency or cost constraint stated in minute 2. Write down constraints; check your design against them before you present it.

### Not using the interviewer as a resource
Interviewers drop hints. They ask clarifying questions that contain information. Listen for it. "Does that concern you?" from an interviewer means "that's a real problem — address it."

### Defending instead of adapting
When challenged, doubling down reads as brittleness. Adapting visibly reads as production experience. The correct response to a valid challenge is to update your answer, not justify your original one.
