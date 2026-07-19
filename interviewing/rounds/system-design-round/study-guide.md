# System Design Round — Study Guide

The method for the highest-weight technical round. Domain content lives in the [RAG](../../guides/3-rag/interview-guide.md), [agents](../../guides/4-agents/interview-guide.md), [evals](../../guides/6-evals-observability/interview-guide.md), [context/cost](../../guides/5-context-cost/interview-guide.md), and [security](../../guides/7-security-safety/interview-guide.md) guides — this guide is the *process*.

## 1. The five-step process (45-55 min, ~8 min/step)

| Step | What to do | Time |
|------|-----------|------|
| **Clarify & scope** | Never design against the raw prompt. Three targets: requirements (what functions), scale (1K vs 1M), constraints (latency, budget, residency). Two openers that always land — see below. | 8 min |
| **Requirements split** | Functional (multi-turn? follow-ups? summarization?) vs non-functional (latency, consistency, scale, security). Write the non-functionals down — they're the trade-off axes. | 5 min |
| **Design** | Components, data flow, APIs. Connect every choice back to a requirement, out loud. Draw the reference architecture (§3) and customize. | 15 min |
| **Identify shortcomings** | Name your design's weaknesses before the interviewer does. Propose what changes under different constraints. | 8 min |
| **Close with measurement** | Success metrics with numbers + future improvements. Never stop at the design. | 5 min |

### The two opening questions

1. "Who are the primary users, and what's the top priority — latency, accuracy, cost, safety? That drives every trade-off downstream."
2. "Does the system touch personal/financial data — must it stay on-prem or can we call third-party model APIs?"

## 2. Trade-off narration (the actual skill being graded)

**Formula**: consider 2-3 solutions -> narrate pros/cons -> ask which priority wins -> justify the pick.

> "I'd compromise X for optimal Y — here's why that hurts least given the priority."

Trade-offs mostly live between non-functionals:

| Axis A | vs | Axis B |
|--------|----|----- --|
| Latency | ↔ | Accuracy |
| Cost | ↔ | Quality |
| Consistency | ↔ | Availability |
| Full automation | ↔ | Safety (HITL) |
| Read throughput | ↔ | Write throughput |
| Storage | ↔ | Caching |
| Model size | ↔ | Response time |
| Fine-tuning | ↔ | RAG freshness |

**If told your trade-off was wrong**: don't double down — adapt visibly. "With that requirement, option B's consistency guarantee wins." No points for stubbornness; growth mindset is scored.

**If you hit a knowledge gap**: say so plainly. "My understanding there is superficial" buys credibility and redirects time.

## 3. The LLM-system reference architecture (draw in under 3 min)

```
Client → API Gateway (authn, rate limits, quotas)
  → Orchestration (workflow/agent graph)
    → Retrieval: query rewrite → hybrid search → rerank
    → Generation: prompt assembly → streaming LLM (fallback chain)
  → Output validation / guardrails
  → Response

Sidecars:
  - Caches (prefix + semantic)
  - State store (session / checkpointer)
  - Trace / observability (Langfuse)
  - Eval pipeline (offline + online)
  - HITL queue
```

For each box, know its **failure mode** and its **scaling story**.

### Component deep-dive pointers

| Component | Study guide | Example |
|-----------|-----------|---------|
| Retrieval pipeline (chunking, embedding, hybrid search, reranking) | [RAG guide §1-3](../../guides/3-rag/interview-guide.md) | [rag-system](examples/rag-system.md), [support-agent](examples/support-agent.md) |
| Orchestration (workflow patterns, agent loops, tool design) | [Agents guide §1-4](../../guides/4-agents/interview-guide.md) | [agent-system](examples/agent-system.md), [forecasting-agent](examples/forecasting-agent.md) |
| Eval pipeline (graders, golden sets, online scoring) | [Evals guide §2-4](../../guides/6-evals-observability/interview-guide.md) | [eval-harness](examples/eval-harness.md), [support-agent](examples/support-agent.md) |
| Context management (token budgets, caching, compaction) | [Context/cost guide](../../guides/5-context-cost/interview-guide.md) | [scaling](examples/scaling.md) |
| Safety layer (guardrails, trust separation, HITL) | [Security guide §3-4](../../guides/7-security-safety/interview-guide.md) | [support-agent](examples/support-agent.md) |
| State & memory (checkpointers, session state, memory types) | [Agents guide §6](../../guides/4-agents/interview-guide.md) | [meeting-processor](examples/meeting-processor.md) |
| Data pipeline (ingestion, preprocessing, feature stores) | [Data eng guide §1](../../guides/8-data-eng-mlops/interview-guide.md) | [meeting-processor](examples/meeting-processor.md), [rag-system](examples/rag-system.md) |
| Observability & tracing (Langfuse vs Langsmith, metrics, cost) | [Evals guide §4-5](../../guides/6-evals-observability/interview-guide.md) | [eval-harness](examples/eval-harness.md) |
| Deployment & ops (Cloud Run, CI/CD, model versioning, drift) | [Data eng guide §2](../../guides/8-data-eng-mlops/interview-guide.md) | [forecasting-agent](examples/forecasting-agent.md) |
| Integration patterns (API, MCP, webhooks, event-driven) | [Agents guide §3](../../guides/4-agents/interview-guide.md) | [meeting-processor](examples/meeting-processor.md), [accounting-assistant](examples/accounting-assistant.md) |
| Knowledge graphs (structured retrieval, entity relationships) | [RAG guide §5](../../guides/3-rag/interview-guide.md) | [forecasting-agent](examples/forecasting-agent.md), [accounting-assistant](examples/accounting-assistant.md) |

## 4. Bottlenecks & failure modes (memorize the tables)

| Bottleneck | Cause | Mitigation |
|---|---|---|
| Token overload | Prompt/response too large | Truncate, summarize, stream, paginate |
| Queue congestion | Slow embedding/model service | Shard queues, priority tiers |
| Vector index bloat | Stale/excessive docs | Compress, prune, periodic rebuild |
| Model cold start | On-prem spin-up | Warm pools, pre-warming |
| Rate-limited APIs | Vendor throttling | Backoff retries, caching, multi-provider |
| Context rot | Long session accumulates stale context | Compaction, sliding window, subagent isolation |
| Denial-of-wallet | Unbounded agent loops | Circuit breakers, per-user token quotas, max-step limits |
| Embedder cold start | Serverless spin-up loads model (30-60s) | Warm pools, min-instances=1, API-based embeddings |
| Checkpointer mismatch | MemorySaver in multi-worker deploy → lost state | Postgres checkpointer, topology-aligned state store |
| Trace storage growth | 100% tracing at scale → storage/cost explosion | Sample metadata 100%, full text 10-20%, quality scores 1-5% |
| Knowledge graph staleness | Graph not updated after data change → wrong structured answers | Atomic pipeline (train + graph update in same transaction) |

### Failure modes

| Failure | Detection | Recovery |
|---------|-----------|---------|
| Prompt crashes model | Known pattern detection | Input sanitization, fallback model |
| Irrelevant retrieval | Relevance threshold, golden-set regression | Hybrid search, reranker, metadata filters |
| Streaming fails mid-output | Error event detection | Graceful fallback to full response |
| Hallucination | Grounding score, double-pass validation | Citation enforcement, CRAG retry |
| Tool failure in agent loop | Error counter, circuit breaker | Honest error feedback to model, retry with backoff |
| Cascading agent failure | Inter-agent monitoring | Isolation boundaries, fail-fast propagation |
| Multi-tenant data leakage | Missing RLS, unscoped queries | Tenant FK + RLS from migration one, scoped service credentials |
| Silent model drift | Provider updates model without notice | Pin model version, re-eval on version change, track `model_version` in traces |
| Webhook delivery failure | Partner system down, payload rejected | Retry with backoff, dead-letter queue, idempotent handlers |

## 5. Close with measurement + future

Never stop at the design. State success metrics with numbers:

> "p95 under 2s while holding faithfulness above 0.9"

Future improvements list (show you think beyond MVP):
- Distilled model for the easy 80% of traffic
- Personalization via summarized user memory
- Token-cost dashboards + hallucination scoring
- Offline batch jobs (embedding refresh, summarization)
- A/B framework for prompts/retrieval strategies
- Feedback loop from thumbs-down to eval set

One cost line lands well:
> "At this scale I'd revisit fine-tuning autocomplete — roughly $30K/month off the API bill."

## 6. Drills (systems you can already speak to)

Three interview-format writeups in the librarian wiki — rehearse as full 45-min answers:

1. **Shared code-index service** — centralized indexer + query API, MCP as thin read-only client, single-writer risk, pgvector escape hatch
2. **Unified eval harness** — golden set, two-tier grading (heuristic → LLM judge), regression vs capability, threshold governance
3. **Serverless agent backends** — stateless invocations, session state in Postgres, streaming within platform timeouts, phase-2 stateful handoff

Portfolio case studies (your own systems — strongest in interviews):
- [Customer support agent](examples/support-agent.md) — 5-layer guardrails, 3-framework comparison, CRAG gate
- [Financial forecasting](examples/forecasting-agent.md) — self-learning agentic loop, classical ML + LLM hybrid, knowledge graph
- [Meeting intelligence](examples/meeting-processor.md) — event-driven pipeline, sole-writer state machine, multi-tenant
- [Accounting assistant](examples/accounting-assistant.md) — three knowledge layers, graph vs RAG, regulatory accuracy

Classic prompts to dry-run:
- Support chatbot for a bank ([security guide](../../guides/7-security-safety/interview-guide.md) has the governance layer)
- Document-QA at 10K→1M docs
- Code-assistant for private enterprise code (residency → self-hosted vs vendor)
- Feed/notification ranking (classic + ML hybrid)

## Practice plan

1. **Draw the reference architecture** from memory 3x this week. Time yourself — under 3 min.
2. **Dry-run one classic prompt** per day: set a 40-min timer, talk through the 5 steps out loud, record yourself if possible.
3. **Memorize the bottleneck + failure tables** — interviewers ask "what breaks first?" and expect instant answers.
4. **Rehearse trade-off narration**: for each design decision, practice the formula (2-3 options → pros/cons → ask priority → justify pick).
5. **Prepare the recovery move**: have a friend challenge your trade-off, practice adapting visibly instead of defending.
6. **Know one cost number**: be able to say something like "$X/month at this scale, here's what I'd optimize."
7. **Read**: The [PRINCE case study](https://martinfowler.com/articles/reliable-llm-bayer.html) is the best single reference for production agentic RAG design with real engineering decisions.
