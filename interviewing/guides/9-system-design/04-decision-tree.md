---
origin: synthesized
confidence: high
sources:
  - interviewing/rounds/system-design-round/study-guide.md (the 5-step process + component table)
  - interviewing/guides/3-rag/interview-guide.md
  - interviewing/guides/4-agents/interview-guide.md
  - interviewing/guides/5-context-cost/interview-guide.md
  - interviewing/guides/6-evals-observability/interview-guide.md
  - interviewing/guides/7-security-safety/interview-guide.md
cleaned: 2026-07-30
---
# System Design — Decision Tree

Pillar 9, detailed note 4. The middle layer between the [5-step process](../../rounds/system-design-round/study-guide.md)
(too abstract under pressure — "design the components") and the pillar guides (too deep —
127 lines on RAG when you have 40 seconds).

A component table answers by **noun**: "what is reranking?" This answers by **situation**:
"the interviewer just said 10K→1M docs — what changes and what do I say?" Those are
different retrieval operations, and only the second one is what a design round asks of you.

## How to use this

**The trunk lives in the round's [study guide](../../rounds/system-design-round/study-guide.md)** —
one fork, memorized, that picks your spine. You walk exactly one spine per interview.

```
"Design X for Y" → clarify → WHAT KIND OF SYSTEM IS THIS?
  ├─ looks things up in documents ──→ RAG spine
  ├─ takes multi-step actions ──────→ AGENT spine
  ├─ predicts / ranks / scores ─────→ ML spine
  └─ transforms a stream of events ─→ PIPELINE spine
```

Each node below gives you:

- **Fork** — the 2–3 real options (not every option; the ones that come up)
- **Ask** — the discriminator question you say *out loud* that picks the branch
- **Say** — the rehearsable sentence that narrates the trade-off
- **At 10×** — what changes when they scale the prompt on you
- **Breaks first** — the failure nobody notices until it's bad
- **Deeper** — one link down

Nodes deliberately repeat across spines (eval and guardrails appear in all four). A shared
"cross-cutting" section you have to jump to is a section you forget under pressure.

---

# RAG spine

Knowledge lookup: document QA, support search, internal-knowledge assistants.

### R1. Retrieval strategy

**Fork:** vector-only · hybrid (BM25 + vector) · graph

**Ask:** "Are queries semantic paraphrases, or do they name exact entities, IDs, error codes?"
- paraphrases only → vector-only (simplest; *defend* the simplicity)
- mixed / jargon / product codes → **hybrid + reranker** (the safe default)
- relationships, multi-hop → graph or graph+RAG

**Say:** "I'd start hybrid — pure vector misses exact-match on product codes, BM25 alone
misses paraphrase. Reranker on top, and I'd measure whether it earns its latency."

**At 10×:** index bloat → prune + rebuild cadence. Rerank cost dominates → cascade
(cheap top-100 → expensive top-10).

**Breaks first:** stale index. Nobody notices until faithfulness drops.

**Deeper:** [RAG guide §1–3](../3-rag/interview-guide.md) · [rag-system](../../rounds/system-design-round/examples/rag-system.md)

### R2. Chunking

**Fork:** fixed-size · semantic/recursive · parent-document

**Ask:** "Are the documents structured — headings, sections — or flat prose?"
- flat prose → fixed-size with overlap
- structured → recursive on the structure
- answers need surrounding context → parent-document (retrieve small, return large)

**Say:** "Chunking is where most RAG quality is won or lost — I'd retrieve on small chunks
for precision but return the parent section so the model has context."

**At 10×:** re-chunking the corpus is expensive; version the chunk strategy so you can
A/B without a full rebuild.

**Breaks first:** answers that cite the right doc but miss the sentence — chunk boundary
split the fact.

**Deeper:** [RAG guide §2](../3-rag/interview-guide.md)

### R3. Freshness

**Fork:** batch re-index · incremental upsert · read-through

**Ask:** "How stale can an answer be before it's wrong — a day, a minute, never?"
- day → nightly batch (cheapest)
- minute → incremental upsert on write
- never → read-through to source of truth, RAG for navigation only

**Say:** "For pricing or policy data I wouldn't trust the index at all — retrieve the doc,
then read the live record."

**Breaks first:** deleted source documents still answerable from the index.

**Deeper:** [RAG guide §4](../3-rag/interview-guide.md)

### R4. Grounding

**Fork:** citation enforcement · grounding score · CRAG retry gate

**Ask:** "What's the cost of a confident wrong answer here?"
- low → citations, let the user judge
- high → grounding score + refuse below threshold
- regulated → CRAG (grade retrieval, retry or escalate before generating)

**Say:** "I'd rather refuse than hallucinate in this domain — a grounding gate with an
escalation path beats a fluent wrong answer."

**Deeper:** [RAG guide §5](../3-rag/interview-guide.md) · [Evals §7](../6-evals-observability/interview-guide.md)

---

# AGENT spine

Multi-step action: support agents that *do* things, coding agents, workflow automation.

### A1. Single or multi-agent?

**Fork:** single agent · multi-agent

**Ask:** "Can one context hold all the tools and instructions this needs?"
- yes → **single agent** (default — defend the simplicity)
- no, and the domains are genuinely separate → multi-agent

**Say:** "I'd start single-agent. Multi-agent buys specialization but costs orchestration,
state, latency, and failure points — I'd want evidence one context can't hold it."

**At 10×:** more tools ≠ more agents. Split by *domain boundary*, not tool count.

**Breaks first:** agents talking past each other with no isolation boundary; one agent's
failure cascading silently.

**Deeper:** [Agents §7](../4-agents/interview-guide.md) · [agent-system](../../rounds/system-design-round/examples/agent-system.md)

### A2. Agent loop or pipeline?

**Fork:** deterministic pipeline · state machine · autonomous agent loop

**Ask:** "Are the steps known in advance?"
- yes → **pipeline** (cheaper, testable, predictable)
- mostly, with branches → state machine
- genuinely unknown → agent loop, and pay for it deliberately

**Say:** "Don't build an autonomous agent when a pipeline does it — the loop is what makes
this expensive and hard to test. I'd reach for it only where the path is truly unknown."

**At 10×:** loop costs scale superlinearly (each step re-reads context).

**Breaks first:** unbounded loops → denial-of-wallet. Circuit breakers and max-step limits
from day one.

**Deeper:** [Agents §1–2](../4-agents/interview-guide.md)

### A3. Tool design

**Fork:** read tools · write tools

**Ask:** "Can this tool mutate anything the user would care about?"
- read → freely available
- write → separate tool, explicit schema, approval gate for high-risk

**Say:** "I separate read and write tools so I can give the model broad read access and
gate the small set of destructive actions — refunds, deletes, sends."

**Breaks first:** the agent misusing a tool. Fix the *tool description* before blaming the
model — poka-yoke the arguments so misuse is impossible.

**Deeper:** [Agents §3](../4-agents/interview-guide.md)

### A4. State or memory?

**Fork:** workflow state · long-term memory

**Ask:** "Does this need to survive the session?"
- no → workflow state (checkpointer: Redis/Postgres)
- yes → memory store, with retrieval precision over recall

**Say:** "State and memory are different problems — current step and tool outputs go in a
checkpointer, user preferences go in a memory store. I wouldn't put either in a vector DB
by default."

**Breaks first:** `MemorySaver` in a multi-worker deploy → silently lost state.

**Deeper:** [Agents §6](../4-agents/interview-guide.md) · [meeting-processor](../../rounds/system-design-round/examples/meeting-processor.md)

### A5. Where do humans gate it?

**Fork:** full auto · propose-then-approve · human-in-the-loop throughout

**Ask:** "Which actions are irreversible, financial, or externally visible?"
- none → full auto with logging
- some → propose → code validates → human approves → execute
- most → HITL queue with batch review

**Say:** "Business rules live in application code, not in the prompt — the model proposes,
deterministic code validates, and the human approves anything irreversible."

**Deeper:** [Security §3–4](../7-security-safety/interview-guide.md) · [support-agent](../../rounds/system-design-round/examples/support-agent.md)

---

# ML spine

Prediction, ranking, scoring: churn, recommendations, forecasting, fraud, feed ranking.

### M1. Is this even an ML problem?

**Fork:** rules/heuristic · classical ML · deep learning · LLM

**Ask:** "What's the business decision this changes, and is there a labeled signal for it?"
- clear rules, no labels → heuristic baseline first
- tabular + labels → classical ML (gradient boosting is the honest default)
- unstructured input → DL or LLM

**Say:** "I'd want a heuristic baseline before a model — it sets the bar the model has to
beat, and sometimes it doesn't need beating."

**Breaks first:** an ML system solving a problem the business didn't have.

**Deeper:** [03-ml-system-design.md](03-ml-system-design.md) · [Foundations](../1-foundations/interview-guide.md)

### M2. Framing the ML problem

**Fork:** classification · regression · ranking · anomaly detection

**Ask:** "What does the system *output*, and what does someone *do* with it?"
- a decision → classification (pick the threshold with them, out loud)
- a number → regression
- an ordering → ranking (and the metric is not accuracy)
- rare deviations → anomaly detection

**Say:** "Framing drives the metric. If it's ranking, accuracy is meaningless — I'd
optimize NDCG or recall@k depending on how many slots the surface has."

**Deeper:** [03-ml-system-design.md](03-ml-system-design.md) §2 · [Foundations](../1-foundations/interview-guide.md)

### M3. Metric choice

**Fork:** precision-weighted · recall-weighted · calibrated probability

**Ask:** "Which is worse — a false positive or a false negative?"
- FP worse (spam, moderation) → precision, high threshold
- FN worse (fraud, disease) → recall, accept the review load
- the score feeds a downstream decision → calibration matters more than either

**Say:** "I'd ask what happens downstream of a wrong call — that tells us where to put the
threshold, and it's a product question as much as a modeling one."

**Breaks first:** a great AUC on an imbalanced set that's useless in production.

**Deeper:** [Foundations](../1-foundations/interview-guide.md)

### M4. Training & serving

**Fork:** batch scoring · online inference · streaming features

**Ask:** "How fresh do the features need to be at prediction time?"
- daily is fine → batch, write to a table
- request-time → online inference + feature store
- sub-minute signals → streaming features (and accept the complexity)

**Say:** "Batch scoring covers more production ML than people expect — I'd only take on
online serving and a feature store if the freshness requirement demands it."

**Breaks first:** train/serve skew — features computed differently in the two paths.

**Deeper:** [Data eng §1–2](../8-data-eng-mlops/interview-guide.md) · [forecasting-agent](../../rounds/system-design-round/examples/forecasting-agent.md)

### M5. Drift & retraining

**Fork:** scheduled retrain · triggered retrain · monitor-only

**Ask:** "How fast does the world this model describes change?"
- seasonal → scheduled
- shock-prone (fraud, abuse) → triggered on drift alarm
- stable → monitor, retrain when it degrades

**Say:** "I'd baseline metrics at validation and run the same scoring pipeline on
production traffic — drift alerts on divergence, not on a calendar."

**Deeper:** [Data eng §3](../8-data-eng-mlops/interview-guide.md)

---

# PIPELINE spine

Event transformation: ingestion, ETL, meeting/document processing, enrichment.

### P1. Trigger model

**Fork:** scheduled batch · event-driven · streaming

**Ask:** "What starts the work — a clock, a message, or a continuous feed?"
- clock → batch (simplest, most debuggable)
- discrete events → event-driven (queue + workers)
- continuous → streaming

**Say:** "I'd default to batch and move to event-driven only where latency requires it —
batch failures are far easier to reason about and replay."

**At 10×:** queue congestion → shard queues, priority tiers.

**Breaks first:** silent backlog growth with no queue-depth alarm.

**Deeper:** [Data eng §1](../8-data-eng-mlops/interview-guide.md) · [meeting-processor](../../rounds/system-design-round/examples/meeting-processor.md)

### P2. Delivery guarantees

**Fork:** at-most-once · at-least-once · effectively-once

**Ask:** "What happens if this runs twice on the same input?"
- harmless → at-least-once with retries (usually right)
- duplicates visible to users → idempotent handlers keyed on a request ID
- financial → effectively-once with a dedup table

**Say:** "At-least-once plus idempotent handlers is the pragmatic answer — exactly-once is
mostly a marketing term, so I'd make the handler safe to re-run instead."

**Breaks first:** retries producing duplicate side effects (double emails, double charges).

**Deeper:** [Data eng §1](../8-data-eng-mlops/interview-guide.md) · [01-distributed-systems.md](01-distributed-systems.md)

### P3. Failure handling

**Fork:** fail-fast · retry with backoff · dead-letter queue

**Ask:** "Is failure here transient or structural?"
- transient (rate limit, timeout) → backoff retry
- structural (bad payload) → dead-letter queue + alert, don't retry forever
- both → retry N times, then DLQ

**Say:** "Retries for transient failures, a dead-letter queue for poison messages — without
the DLQ a single bad payload blocks the pipeline."

**Breaks first:** poison message in an infinite retry loop, consuming the whole worker pool.

**Deeper:** [01-distributed-systems.md](01-distributed-systems.md)

### P4. State ownership

**Fork:** stateless workers · sole-writer state machine · distributed transaction

**Ask:** "Can two workers touch the same record at once?"
- no → stateless workers (scale freely)
- yes → sole-writer state machine, one owner per record
- across services → saga/compensation, not a distributed transaction

**Say:** "I'd give each record a single writer and model the lifecycle as explicit states —
concurrent partial writes are the bug you can't reproduce."

**Breaks first:** two workers racing on the same row, last-write-wins corruption.

**Deeper:** [meeting-processor](../../rounds/system-design-round/examples/meeting-processor.md) · [01-distributed-systems.md](01-distributed-systems.md)

---

# Cross-cutting (every spine)

Repeated here on purpose — these come up in all four, and jumping to a shared section
mid-interview is how you forget them.

| Question | Default answer | Deeper |
|---|---|---|
| How do you know it works? | Golden set + regression on every change | [Evals §5](../6-evals-observability/interview-guide.md) |
| How do you know it broke? | Traces + drift alerts, 10–20% online scoring | [Evals §6](../6-evals-observability/interview-guide.md) |
| What does it cost? | Cost per *successful task*, not per call | [Context/cost §5](../5-context-cost/interview-guide.md) |
| What's the blast radius? | Least privilege, untrusted input never reaches a dangerous sink | [Security §2–3](../7-security-safety/interview-guide.md) |
| What happens at 10×? | Name the bottleneck *before* they ask | [Round study guide §4](../../rounds/system-design-round/study-guide.md) |

## Test yourself

Walk one spine end to end, out loud, against a classic prompt — 8 minutes per step:

- "Design a support chatbot for a bank" → AGENT spine (+ RAG for policy lookup)
- "Design document QA for 10K→1M docs" → RAG spine
- "Design feed ranking" → ML spine
- "Design a meeting-notes processor" → PIPELINE spine

If you can't name the discriminator question at each node from memory, that node isn't
learned yet.
