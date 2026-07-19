# Questions — Case Study Round

12 questions spanning live cases, take-homes, LLM cases, ML cases, defense rounds, and FDE customer-problem formats.

---

## Q1: Retailer reducing support costs with AI

**Prompt:** "A retailer wants to reduce support costs with AI — walk me through it."

**What they're testing:** Full template top-to-bottom; business framing discipline; clarify-first reflex; phased delivery.

**Model answer structure:**

1. **Clarify:** What does "reduce support costs" mean — headcount, ticket volume, time-to-resolution? What's the current cost-per-ticket? What's the ticket mix (order status vs. product questions vs. complaints)? Any compliance constraints on customer data?

2. **Objective:** "Deflect 40% of tier-1 tickets (order status, FAQ) to an AI channel, reducing cost-per-ticket from $12 to $7.20. Measure success at 90 days."

3. **Constraints:** Sub-3-second response time; customer PII in transcripts → data stays in-region; budget $50K for build + first 6 months infra.

4. **Data:** Historical ticket transcripts (label = resolution type), product catalog, order status API, customer account data.

5. **Baseline:** Keyword-routing rules already deflect 15% of tickets. Baseline: 15% deflection rate at $0 variable cost.

6. **MVP:** RAG pipeline over product FAQ + ticket KB → LLM generates draft response → human agent reviews (shadow mode) → deflection when confidence threshold met. No fine-tuning in MVP.

7. **Eval:** Offline: faithfulness score on 200 labeled queries, human eval on 50 tricky cases. Online: deflection rate, CSAT delta, escalation rate. Rollback trigger: CSAT drops >0.3 points.

8. **Risks:** Hallucinated order status (mitigation: order status from API, not LLM generation); PII in responses (mitigation: output filter + PII scrubber); over-deflection of complaints that need empathy (mitigation: sentiment classifier gates LLM for angry customers).

9. **Milestones:** Week 2: data audit + baseline established. Week 4: MVP pipeline, offline eval. Week 6: shadow mode. Week 10: 10% traffic A/B. Week 14: full rollout.

**Value math to narrate:** deflection_rate × ticket_volume × cost_per_ticket = savings. At 40% deflection × 5000 tickets/month × $12 = $24K/month savings. Build cost $50K → payback in ~2 months.

**Study refs:** [product-business guide](../../guides/10-product-delivery/interview-guide.md) §1 (framing), [system-design guide](../../guides/9-system-design/interview-guide.md) §3 (LLM architecture), [RAG guide](../../guides/3-rag/interview-guide.md)

---

## Q2: Churn prediction take-home

**Prompt:** "Here's 100K rows of churn data — what do you do in 3 hours?"

**What they're testing:** Take-home discipline — scoping, leakage check, baseline-first, honest validation, judgment about what to skip.

**Model answer structure:**

1. **First 5 minutes — frame the objective:** "Reduce churn 5%, from 8% monthly to 3.8%. My proxy metric is AUROC on a held-out test set. I'll target AUROC ≥ 0.82 as the bar that suggests production-grade discrimination."

2. **EDA (30 min):** Distribution checks on all features. **Leakage check first** — any feature that couldn't have been known at prediction time? (e.g., "days_since_last_contact" might be post-churn for churned users). Missing data map — note patterns, don't fill yet.

3. **Baseline (15 min):** Logistic regression on the 5 most obviously relevant features (tenure, usage frequency, support contacts, price tier, last login). Baseline AUROC: record it. This is your "is ML worth it?" anchor.

4. **Primary model (45 min):** LightGBM with 5-fold CV. Tune max_depth and learning_rate. Check calibration (the predicted probability of churn at 0.7 should match actual churn rate among those users). Top-3 feature importances with SHAP.

5. **Validation (20 min):** Holdout set eval. Confusion matrix at two thresholds: one for precision-optimized (we only call the highest-risk churners), one for recall-optimized (we call everyone likely to churn). State the business trade-off: "At threshold 0.6, precision = 71%, recall = 58%. At 0.4: precision = 52%, recall = 79%. Which fits the campaign budget?"

6. **Writeup (40 min):** Assumptions block first. Honest data issues. What I'd do next: threshold tuning on business cost matrix, SHAP for interpretability, test a neural net to validate that LightGBM is the right choice.

**What to explicitly say in the writeup:** "I did not tune exhaustively — I prioritized a clean validation story over squeezing out 1 more point of AUROC. I would revisit tuning in week 2 with business input on the cost of false positives vs. false negatives."

**Study refs:** [ml-foundations guide](../../guides/1-foundations/interview-guide.md) §7 (boosting, AUROC), [product-business guide](../../guides/10-product-delivery/interview-guide.md) §2 (ROI)

---

## Q3: Why not deep learning?

**Prompt:** "Your take-home model gets challenged: why not deep learning?"

**What they're testing:** Defense round depth — do you know when boosting beats neural nets on tabular data? Can you state the conditions under which you'd change your answer?

**Model answer structure:**

1. **Acknowledge the concern:** "That's a fair challenge. Deep learning can outperform gradient boosting in some tabular settings."

2. **State why boosting was the right choice here:**
   - Sample size: 100K rows is in the "boosting sweet spot." Neural nets on tabular data typically need millions of rows to justify their parameter count.
   - Feature type: structured tabular features with mixed types (categorical, numeric) — boosting handles this natively; neural nets require more feature engineering.
   - Interpretability: the business likely needs to explain churn predictions to stakeholders. SHAP on LightGBM is far cleaner than attribution on a neural net.
   - Tabular SOTA: on public benchmarks (TabZilla, OpenML), tree-based methods match or exceed neural nets on datasets of this size and type.

3. **State the conditions under which you'd switch:**
   - "If the dataset were 10M rows with dense temporal features (click sequences, event logs), I'd look at TabNet or a simple LSTM."
   - "If we had image or text features embedded in the data, neural nets would be the clear choice."
   - "If the business had zero interpretability requirement and the accuracy gap were >3 points, I'd re-evaluate."

4. **Adapt if pressed:** "If you're seeing evidence in your data that a neural net would outperform, I'd want to see that comparison. I'd run a 2-layer MLP on the same holdout set and compare AUROCs. If it wins by more than 1 point, we switch."

**Study refs:** [ml-foundations guide](../../guides/1-foundations/interview-guide.md) §7

---

## Q4: Messy data curveball

**Prompt:** "The client's data turns out to be much messier than the brief said."

**What they're testing:** Ambiguity handling — do you panic and redesign, or do you triage and renegotiate scope? This is the adaptability test.

**Model answer structure:**

1. **Triage first (don't redesign yet):** "I'd start by categorizing the data quality issues — missing values vs. inconsistent formats vs. leakage vs. wrong labels. Different problems have different severity."

2. **Map issues to the objective:** "Which features are critical to the model? Can I build an MVP without the messy features, using only the clean subset?"

3. **Renegotiate scope:** "I'd go back to the client and say: 'The data quality issues in [X, Y, Z] will add 2 weeks to the timeline if we want to clean them. Here's the MVP I can ship with the clean subset in the original timeline — it gets us to 60% of the target, not 100%. Do you want to hold the timeline or hold the performance target?'"

4. **Narrate the re-plan out loud:** Show the revised milestone table. Show what's in vs. out of scope. Show what assumptions changed.

5. **Close with honesty:** "The right answer is often to ship the reduced MVP and add data quality as a sprint 2 item. A 60%-of-target system that's live in 4 weeks beats a 100%-of-target system that's 3 months late."

**Study refs:** [product-business guide](../../guides/10-product-delivery/interview-guide.md) §1

---

## Q5: RAG what-if chain

**Prompt:** "What if retrieval quality is poor? What if chunks truncate answers? What if docs grow 10×?"

**What they're testing:** RAG depth and systematic debugging process. Do you have a chain of responses, or just "it depends"?

**Model answer structure:**

**If retrieval quality is poor:**
- Diagnose first: is it embedding quality, index staleness, or a relevance problem?
- Check retrieval precision: how many of the top-k chunks are actually relevant to the query?
- Mitigations: (1) add a reranker (cross-encoder) on top of dense retrieval; (2) add metadata filters (date, document type); (3) try hybrid BM25 + dense retrieval; (4) lower the similarity threshold with a "no results" fallback.

**If chunks truncate answers:**
- The problem is usually fixed-size chunking that breaks mid-concept.
- Mitigations: (1) switch to semantic chunking (split on sentence/paragraph boundaries); (2) overlap chunks by 20%; (3) increase chunk size and accept the context overhead; (4) implement parent-child retrieval (retrieve small chunks, but assemble parent-document context around them).

**If docs grow 10×:**
- 10× doc volume is a retrieval + cost problem, not a model problem.
- Mitigations: (1) tiered indexing — recent/high-priority docs get more thorough chunking; (2) scheduled index rebuilds rather than continuous; (3) document freshness signals in the retrieval scoring; (4) consider a smaller embedding model if latency grows.

**Study refs:** [RAG guide](../../guides/3-rag/interview-guide.md), [system-design guide](../../guides/9-system-design/interview-guide.md)

---

## Q6: Design a RAG pipeline

**Prompt:** "Design a document QA system for a 500-document legal knowledge base."

**What they're testing:** LLM case template — end-to-end pipeline design, RAG-vs-fine-tune decision, cost + latency reasoning, eval.

**Model answer structure:**

1. **Clarify:** Who are the users (lawyers, paralegals, clients)? What's the query type — point lookups or multi-document synthesis? What's the acceptable latency? Is the doc set static or constantly updated?

2. **Objective:** "Answer 80% of legal research queries without requiring a lawyer to read the source doc, reducing research time from 2 hours to 15 minutes per query. Accuracy bar: no hallucinated citations."

3. **RAG-vs-fine-tune decision:** "RAG — the knowledge is in specific documents, not general legal reasoning. Fine-tuning would bake in the knowledge but lose the ability to update when docs change. RAG lets us update the index without retraining."

4. **Pipeline:** Ingest 500 PDFs → parse (PDF → text, handle tables + images separately) → semantic chunk at section/paragraph level → embed (text-embedding-3-large or equivalent) → Pinecone or pgvector index → at query time: user query → embed → retrieve top-8 chunks → rerank with a cross-encoder → assemble context → GPT-4o prompt → output with source citations.

5. **Eval:** Offline: faithfulness (do citations match the generated answer?) + completeness (does the answer address the full question?) on 100 human-labeled QA pairs. Online: thumbs-up/down, citation click-through rate, escalation to a lawyer.

6. **Risks:** Hallucinated citations (mitigation: ground the generation — "only cite documents returned in the retrieval context"); stale docs (mitigation: document hash change → immediate re-index trigger); confidentiality (mitigation: row-level access control on the index — users only retrieve from docs they're authorized for).

7. **Cost math:** 500 docs × 50 pages avg × 1000 tokens/page = 25M tokens to embed. At $0.02/1M tokens (text-embedding-3-small) = $0.50 one-time. Query cost: 8 chunks × 800 tokens + 200-token query + 500-token response = ~7K tokens/query. At GPT-4o rates (~$5/1M) = $0.035/query. At 100 queries/day = $3.50/day = $105/month.

**Study refs:** [RAG guide](../../guides/3-rag/interview-guide.md), [system-design guide](../../guides/9-system-design/interview-guide.md) §3

---

## Q7: Build an agent system

**Prompt:** "Design an AI agent that can research a company and produce a competitive analysis report."

**What they're testing:** Agent system design — orchestration, tool design, state management, safety, eval.

**Model answer structure:**

1. **Clarify:** How long should the report be? What sources are in scope — web search, internal docs, APIs? What's the latency expectation — real-time or async background job? Who reviews before it ships?

2. **Objective:** "Produce a 2-page competitive analysis (strengths, weaknesses, market position, recent moves) in under 5 minutes, requiring <10 min of analyst review before publishing."

3. **Agent architecture:**
   - Orchestrator: LLM-based planner (Claude or GPT-4o) that receives the task, decomposes it into subtasks, and assigns tools.
   - Tools: web_search(query), news_search(company, date_range), sec_filings_fetch(ticker), internal_db_query(company_id), report_writer(sections).
   - State: task graph — which subtasks are complete, which are in-flight, what evidence has been collected.
   - Loop: plan → execute tool → observe result → update state → plan next step. Max 20 turns; fail safe after.

4. **Safety:** Tool call budget — max 15 search queries per run. Output goes through a fact-check pass: every claim requires a source citation. Human review gate before report is emailed. Rate limiting on external APIs.

5. **Eval:** Offline: golden-set reports on 10 known companies — compare agent output to analyst-written reports on factual accuracy and claim coverage. Online: analyst correction rate (how many facts were changed in review?), time saved vs. manual.

6. **Risks:** Hallucinated company facts (mitigation: citation-required generation); tool errors propagating (mitigation: tool result validation before using in next step); runaway loops (mitigation: turn budget + explicit termination condition).

**Study refs:** [agents guide](../../guides/4-agents/interview-guide.md), [system-design guide](../../guides/9-system-design/interview-guide.md)

---

## Q8: Defense — why this architecture?

**Prompt:** "You designed a RAG system. Why not fine-tune the model instead?"

**What they're testing:** Defense depth — do you understand the RAG-vs-fine-tune trade-off at a mechanical level? Can you state when fine-tuning wins?

**Model answer structure:**

1. **State the RAG reasoning for this case:** "The knowledge is in the documents, not in general domain patterns. The docs update regularly. Fine-tuning would require retraining every time a doc changes — RAG lets us update the index in minutes."

2. **When fine-tuning wins:**
   - The gap is style/format/task behavior, not knowledge. ("Write responses in our legal brief format" → fine-tune on examples.)
   - The knowledge is stable and doesn't change. ("Understand our proprietary taxonomy" → fine-tune once.)
   - RAG latency is too high for the use case. ("Sub-100ms responses" → a fine-tuned smaller model may win on latency + cost.)
   - The context window is insufficient to fit the needed docs. ("Each query requires 50 full documents" → fine-tune the model on those docs.)

3. **Hybrid option:** "In practice, the two aren't mutually exclusive. I'd fine-tune on format and task behavior, then use RAG for the knowledge retrieval. That's the production pattern at scale."

4. **Adapt if challenged:** "If you've found that fine-tuning achieves better faithfulness on your specific domain than RAG, I'd want to see that data. My baseline assumption was that RAG is easier to maintain, but if faithfulness metrics favor fine-tuning in your environment, I'd revise the architecture."

**Study refs:** [system-design guide](../../guides/9-system-design/interview-guide.md) §3, [RAG guide](../../guides/3-rag/interview-guide.md)

---

## Q9: Defense — what breaks at scale?

**Prompt:** "Your churn model works in production. What breaks at 10× the current volume?"

**What they're testing:** Infrastructure reasoning, not ML reasoning. Can you think about the system around the model?

**Model answer structure:**

1. **Identify the bottlenecks by layer:**
   - **Data ingestion:** at 10× volume, batch feature pipelines may take too long. Daily retraining might need to become weekly with online feature updates.
   - **Inference:** if scoring 10× more customers daily, single-instance inference becomes a queue. Need autoscaling or batch scoring with SLA-aware scheduling.
   - **Monitoring:** 10× events means the anomaly detection on model outputs needs to be statistical sampling, not full-scan.
   - **Retraining triggers:** drift detection is sampling-based at scale; fixed-window retraining becomes a bottleneck.

2. **The model itself:** "The model doesn't break at 10× volume — it's stateless inference. What breaks is the infrastructure around it."

3. **Mitigations:**
   - Feature store: move from on-demand feature computation to a precomputed feature store (Feast, Hopsworks, or a BigQuery materialized view).
   - Inference: batch scoring job overnight vs. real-time; autoscaling if real-time is required.
   - Monitoring: statistical sampling + control charts for input distribution drift.

4. **Close with a question:** "At 10× volume, the batch vs. real-time scoring decision matters a lot. Are we scoring at prediction time (user opens app) or overnight? That changes the architecture significantly."

**Study refs:** [system-design guide](../../guides/9-system-design/interview-guide.md), [ml-foundations guide](../../guides/1-foundations/interview-guide.md)

---

## Q10: Defense — what would you cut?

**Prompt:** "You have one week left and need to cut scope. What stays, what goes?"

**What they're testing:** Business prioritization, MVP discipline, ability to reason about value vs. cost.

**Model answer structure:**

1. **Anchor on the objective:** "I'd cut everything that doesn't move the core metric. Our success criterion is 40% deflection rate. Everything else is optimization."

2. **Framework — keep vs. cut:**

| Keep | Cut |
|------|-----|
| Core pipeline (query → retrieve → generate → respond) | A/B testing framework (can add in week 2) |
| Confidence threshold and human escalation path | Advanced reranker (BM25 baseline is good enough for MVP) |
| PII scrubber (compliance is non-negotiable) | Personalization / user memory |
| CSAT collection (feedback loop is critical) | Multi-turn conversation state (stateless MVP first) |
| Basic monitoring (latency + error rate) | Automated retraining pipeline (manual retrain is fine for 90 days) |

3. **State the logic:** "The things I cut are all 'better version of X' improvements. They improve performance but they don't change the baseline question: does an AI-assisted deflection system work at all? Let's answer that first."

4. **Commit with a next-step:** "I'd document the cut features as sprint 2 tickets with priority rankings based on expected impact. They're not lost — they're queued."

**Study refs:** [product-business guide](../../guides/10-product-delivery/interview-guide.md) §1

---

## Q11: Take-home presentation structure

**Prompt:** "Walk us through your take-home submission."

**What they're testing:** Communication, presentation discipline, ability to lead with findings not methodology, readiness for challenges.

**Model answer structure:**

1. **Open with the outcome, not the process:** "I set out to build a churn predictor that could identify the 20% highest-risk customers before their renewal date. The model achieves AUROC 0.81 on a held-out test set. Here's what that means in business terms: if we intervene with the top-decile predictions, we'd target 72% of actual churners."

2. **Walk the template sections, briefly:**
   - Assumptions stated upfront — what you assumed and why.
   - Data: what you found, what problems you saw, how you handled them.
   - Model: what you chose and why over alternatives.
   - Eval: the metric, the honest result, calibration.
   - Risks: at least three, with mitigations.
   - Next steps: what you'd do with two more weeks.

3. **Anticipate the panel's three most likely challenges and build them into the narrative:** "You might ask why I chose LightGBM over a neural net — I'll address that in the model section." Pre-empting challenges reads as confidence.

4. **Close with a forward-looking question:** "The biggest open question in my mind is the threshold setting — the right precision-recall trade-off depends on the campaign budget. I've prepared the sensitivity analysis; I'd like your input on the business cost of a false positive vs. a false negative."

**Study refs:** [product-business guide](../../guides/10-product-delivery/interview-guide.md)

---

## Q12: FDE customer-problem case

**Prompt:** "A healthcare client wants to use AI to help doctors find relevant patient history during appointments. Design the solution."

**What they're testing:** FDE signature format — customer empathy, problem before solution, regulatory constraints, business framing layered on technical design.

**Model answer structure:**

1. **Clarify the customer problem first:** "Before I design, I want to understand the workflow. When does a doctor look for patient history — at the start of the appointment? During a specific moment? Is the pain point finding history across multiple systems, or reading long notes quickly?" (Pause and let them answer.)

2. **Restate the objective from the customer's perspective:** "The doctor's goal is: in a 15-minute appointment, retrieve the 3 most relevant pieces of patient history in under 30 seconds. Not 'search the EMR' — arrive at the right 3 items."

3. **Constraints — healthcare is different:**
   - HIPAA compliance is non-negotiable. No PHI to external APIs.
   - Latency: must be usable in-flow during an appointment. Sub-5-second response.
   - Trust: if the system surfaces wrong history, a doctor may make a clinical error. Confidence signals matter.

4. **Solution — on-premise RAG with strict grounding:**
   - Ingest EMR notes, lab results, imaging reports per patient into an on-premise vector index (no cloud API).
   - At appointment time: query by patient_id + appointment_context (current complaint) → retrieve top-5 relevant history items → LLM summarizes with source citations.
   - Output: 3-bullet summary with source citations, confidence indicator, and link to full record.

5. **Eval:** Offline: clinician-labeled relevance on 50 patient case samples. Online: did the doctor open the cited records? Did they override the summary? Escalation rate.

6. **Risks:** Wrong history surfaced (mitigation: citation-required, confidence threshold, "I'm not sure — see full record" fallback); PHI breach (mitigation: on-premise only, audit logging, no external LLM API calls); over-trust by doctors (mitigation: explicit UX labeling that this is AI-assisted, not AI-decided).

7. **Business framing:** "The value isn't just time saved. A doctor who misses a critical allergy in the chart creates liability. If AI reduces missed-allergy incidents by 30%, that's a risk-reduction story, not just an efficiency story. I'd frame the ROI in both dimensions."

**Study refs:** [product-business guide](../../guides/10-product-delivery/interview-guide.md), [system-design guide](../../guides/9-system-design/interview-guide.md), [RAG guide](../../guides/3-rag/interview-guide.md)
