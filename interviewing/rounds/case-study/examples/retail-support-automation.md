# Worked Example: Retail Support Automation (Live Case)

**Format:** Live case, 45 minutes
**Prompt:** "A retailer wants to reduce support costs with AI — walk me through it."
**Template:** Full 8-section walkthrough

---

## Opening move: clarify before designing

*Do not start designing. Ask 4–5 targeted questions.*

> "Before I sketch anything, I want to make sure I'm solving the right problem. A few questions:
>
> 1. When you say 'reduce support costs' — is the goal headcount reduction, handling more volume without adding headcount, or improving deflection rate so agents spend time on complex issues only?
> 2. What's the current cost-per-ticket and ticket volume? And roughly what's the ticket mix — order status, product questions, complaints, returns?
> 3. Is there existing automation — a FAQ page, a chatbot, IVR?
> 4. Any constraints I should know about upfront: customer PII, regulated products (pharmaceutical, financial), multi-language requirements?
> 5. What's the timeline and budget — are we piloting or committing to production?"

*Interviewer responds:* "Mainly about handling volume without adding headcount. 8,000 tickets/month, $10 cost-per-ticket, mostly order status and FAQ (~60%), some complaints. There's a basic FAQ page but no automation. PII in transcripts. Timeline is 4 months to a working system, budget is flexible but we want to see ROI."

---

## Section 1: Objective & users

**Users:** Customers contacting support (via chat or email); support agents who escalate when AI can't resolve.

**Objective (stated as a number):**
Deflect 40% of tier-1 tickets (order status + FAQ — 60% of 8K = 4,800/month → target 1,920 deflections/month) to an AI channel, reducing average support cost from $10/ticket to $6.40/ticket blended.

**Value math:**
- Current: 8,000 tickets/month × $10 = $80K/month
- Target: 8,000 × (40% deflected at ~$0.50 variable cost + 60% at $10) = $800 + $48,000 = $48,800/month
- Monthly savings: ~$31K. Annual: ~$372K.

*Say this out loud to the interviewer. The number makes everything that follows concrete.*

---

## Section 2: Constraints

| Constraint | Detail |
|-----------|--------|
| Latency | Customer-facing: response must feel synchronous. Target <3 seconds end-to-end. |
| Cost | Token budget: at GPT-4o rates, 1,920 deflections/day × 1,500 tokens = ~$2.88M tokens/day = ~$14.40/day = $432/month. Well within ROI. |
| Privacy | Customer PII in transcripts — no PII to external APIs without consent framework. Consider: can we use OpenAI API with a data processing agreement, or do we need an on-premise model? |
| Budget | Pilot at $80K total (build + 6 months infra). Production threshold: payback < 6 months. |

*Privacy constraint drives a decision point: if DPA with OpenAI/Anthropic is acceptable, use hosted API. If not, we're looking at a self-hosted model (Llama 3, Mistral) — more ops overhead. I'll assume DPA is acceptable for now and note this as a decision to confirm.*

---

## Section 3: Data sources

| Source | What we have | Quality concerns |
|--------|-------------|-----------------|
| Historical tickets | 8,000/month for ~18 months = ~144K tickets with resolution | Variable format (email vs. chat); some manually annotated with category, some not |
| Order status API | Real-time order status, shipping events | Clean — existing integration |
| Product catalog | SKUs, descriptions, specs | Likely stale in some areas; needs freshness check |
| FAQ content | 40 FAQ pages | Static HTML; not structured as QA pairs — needs preprocessing |
| Agent resolution notes | Free text notes from agents | Low signal, high noise — treat as secondary |

**Missing:** labeled intent data at query level (not just resolution category), ground-truth QA pairs for eval.

---

## Section 4: Baseline first

**What exists now:** Static FAQ page. Customers must browse or search it manually. Estimated self-service rate: ~5% (customers who find the answer without contacting support).

**Baseline metric:** 5% deflection rate, $0 variable cost per deflection.

**Minimum viable win:** An AI system must beat 5% deflection at a cost that still generates positive ROI. At $0.50/deflection variable cost, breakeven is at ~8% deflection (above the 5% baseline). Our 40% target has a wide margin.

**Baseline model (for ML components, if needed):** Logistic regression on bag-of-words of query text → intent category. This will be our classifier baseline to validate that LLM routing is adding value.

---

## Section 5: MVP pipeline sketch

**Architecture decision:** RAG over FAQ + KB, with an order status tool call for real-time data. No fine-tuning in MVP — too slow to iterate, and the knowledge is in documents, not model weights.

```
Customer message
    → Intent router (LLM classifier: FAQ / order-status / complaint / other)

    [FAQ path]
    → Embed query → retrieve top-5 FAQ chunks → assemble context
    → GPT-4o: "Answer using only the provided FAQ content. If insufficient, say so."
    → Confidence check (based on retrieval score) → if low, escalate to agent
    → Response + source citation

    [Order status path]
    → Extract order_id from message → call order_status_api(order_id)
    → GPT-4o: "Compose a helpful response from this order status data: {data}"
    → Response

    [Complaint / other path]
    → Route to human agent with AI-drafted context summary
```

**Components:**
- Embedding model: text-embedding-3-small (fast, cheap, sufficient for FAQ retrieval)
- Vector store: pgvector on existing Postgres (avoids adding a new service for MVP)
- LLM: GPT-4o mini for intent routing and FAQ answers (lower cost); GPT-4o for complex synthesis if needed
- PII handling: scrub PII from context before sending to LLM (regex + NER pipeline for email/phone/SSN patterns)

**Trade-off narrated:** "I chose pgvector over Pinecone because we're already on Postgres — that's one less service to operate in a pilot. At 10× scale or with more complex retrieval needs, I'd revisit Pinecone."

---

## Section 6: Offline + online eval plan

### Offline eval (before deploy)

**Retrieval:** Sample 200 real customer queries with known correct answers. Measure retrieval precision@5 (are the right FAQ chunks in the top 5?). Target: >70%.

**Generation:** Human eval on 50 generated responses: (1) factually correct? (2) cites the right FAQ? (3) complete answer? Target: >85% pass rate on all three.

**Intent routing:** Confusion matrix across the 4 intent categories on 300 labeled queries. Target: >90% accuracy on FAQ vs. non-FAQ routing (because misrouting order status to FAQ → wrong answer → worse than no automation).

### Online eval (after deploy)

| Metric | Measurement | Rollback trigger |
|--------|-------------|-----------------|
| Deflection rate | % of AI-handled tickets with no human escalation within 10 min | Not a rollback trigger — it's the goal |
| CSAT | Post-resolution survey (1–5) | Drop >0.3 points below pre-AI baseline |
| Escalation rate | % of AI-handled conversations escalated to human | Exceeds 60% → the AI is failing at routing |
| Response accuracy (sampled) | Weekly human review of 50 AI responses | >5% factual errors → pause rollout |
| Latency p95 | End-to-end response time | Exceeds 5 seconds → performance investigation |

---

## Section 7: Risks & safety

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hallucinated order status | Customer gets wrong delivery info → escalates angry, damages trust | Order status ALWAYS from API, never generated by LLM. Zero tolerance. |
| PII in LLM outputs | Customer sees another customer's data | PII scrubber on inputs; no customer data in shared prompt context; audit log all completions |
| Over-deflection of complaints | Angry customer gets a bot response → CSAT collapse | Sentiment classifier gates: if negative sentiment detected, route to human with AI context summary |
| Stale FAQ content | AI answers from outdated FAQ → wrong info | FAQ has a freshness date; if >30 days old, auto-flag for review; include "as of [date]" in responses |
| Prompt injection by adversarial users | Malicious input manipulates bot behavior | Strict system prompt; user content in a clearly delimited message block; output filter for off-topic responses |
| Confidence threshold too low | AI deflects queries it can't actually answer | Default to escalation when retrieval score < 0.70; tune threshold upward in week 2 |

---

## Section 8: Milestones

| Week | Milestone | Success signal |
|------|-----------|---------------|
| 1–2 | Data audit: label 300 historical tickets by intent; measure existing self-service rate; PII audit | Baseline metrics established |
| 3–4 | FAQ preprocessing + index build; MVP pipeline deployed to staging; offline eval run | Retrieval precision >70%; human eval pass rate >85% |
| 5–6 | Shadow mode: AI generates responses but agents review all before sending | Agree on response quality; catch edge cases; tune confidence threshold |
| 7–10 | Limited A/B: 10% of new ticket traffic goes AI-first | Deflection rate >20% (MVP threshold); CSAT holds |
| 11–14 | Ramp to 50% → 100% AI-first for tier-1 queue; measure at each step | 40% deflection rate; CSAT ≥ baseline; escalation rate <40% |
| 15–16 | Retro + sprint 2 planning: multi-turn conversation state, personalization, automated FAQ refresh | System declared production |

---

## Measurement close

*Always close the live case with this.*

> "We declare success when:
> - Deflection rate reaches 40% sustained over 30 days
> - CSAT holds at ≥4.1/5 (baseline: 4.3/5, we're allowing a 0.2-point degradation during ramp)
> - Monthly support cost drops from $80K to under $52K
>
> If those three hold at the end of month 4, we've proven the system. The next question is how far above 40% we can push deflection with better retrieval — I'd estimate 55–60% is achievable with a reranker and multi-turn state."

---

## Trade-off narration (interviewers listen for this)

Three explicit trade-offs to name in a live case:

1. **RAG vs. fine-tune:** "I chose RAG because our FAQ content will be updated monthly. Fine-tuning would require retraining on every update — RAG lets us refresh the index in minutes."

2. **pgvector vs. Pinecone:** "pgvector avoids a new service in the pilot. At 10× query volume or with more complex hybrid retrieval needs, the dedicated vector store's performance profile would justify the ops overhead."

3. **GPT-4o mini vs. GPT-4o:** "Mini handles routing and FAQ answers at 10× lower cost. We escalate to GPT-4o only for multi-document synthesis or complex complaint summarization — that keeps the cost math in our favor."
