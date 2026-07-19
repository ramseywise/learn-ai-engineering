# System Design Round — Questions & Model Answers

## Format note
System design questions are deliberately vague — the first thing you do is clarify, not design. Model answers below show the *structure* of a strong response, not a script to memorize. The five-step process from the [study guide](study-guide.md) is the backbone.

---

## Q1: "Design a customer-support chatbot for a bank."

**What they're testing**: Can you handle the most common LLM design prompt with domain-specific constraints (security, compliance, trust)?

**Model answer structure**:

1. **Clarify**: Deflection-focused or CSAT-focused? Volumes? Languages? "Does it handle transactions or just information?" "What's the compliance environment — PCI-DSS? GDPR?"
2. **Requirements**: Multi-turn conversation, RAG over approved KB, escalation to human, session history. Non-functional: p95 < 2s, zero PII in logs, audit trail, 99.9% uptime.
3. **Design**: Reference architecture with governance emphasis:
   - Input guardrails (PII detection, injection defense) → contextual retrieval from approved corpora only → LLM with strict system prompt → output validation (PII redaction, toxicity filter) → response
   - Anonymized session memory (no PII in long-term store)
   - Escalation path with HITL for financial operations
   - Full audit trail for compliance
4. **Shortcomings**: Single-model dependency, latency under load, hallucination risk on financial questions
5. **Close**: Deflection rate, resolution rate, CSAT, p95 latency, hallucination rate on golden set. Future: distilled model for FAQ tier, A/B prompt testing, feedback loop to eval set.

**Study ref**: [security guide](../../guides/7-security-safety/interview-guide.md) §5 for compliance answers; [RAG guide](../../guides/3-rag/interview-guide.md) for retrieval design; [examples/rag-system.md](examples/rag-system.md) for a full walkthrough.

---

## Q2: "Design a document-QA system. Start with 10K docs, plan for 1M."

**What they're testing**: RAG pipeline depth + scaling story.

**Model answer structure**:

1. **Clarify**: Doc types (PDFs with tables? images?)? Query patterns (factual lookup vs synthesis)? Latency ceiling? Multi-tenant?
2. **Design at 10K**: Standard RAG — structure-aware chunking, hybrid search (vector + BM25 with RRF), cross-encoder rerank, CRAG-gated generation with confidence threshold. Cite latency budget: ~1.5-2s p95.
3. **Scale to 1M — what changes**:
   - Index: move from brute-force to ANN/HNSW, shard by tenant/collection
   - Ingestion: async pipeline with incremental embedding refresh
   - Retrieval: add semantic cache for repeat queries, pre-filter by metadata before vector search
   - Quality: eval set must grow with corpus — stale golden sets give false confidence
   - Cost: reranker N must be bounded, batch embedding jobs off-peak
4. **What breaks first**: Stale content ratio (→ recall ceiling), reranker becoming the bottleneck, eval set no longer representative of the query distribution.
5. **Close**: Hit rate@5, faithfulness on golden set, p95 latency, cost per query. Future: GraphRAG for relationship queries, user feedback → eval set enrichment.

**Study ref**: [RAG guide §1-5](../../guides/3-rag/interview-guide.md); [examples/rag-system.md](examples/rag-system.md).

---

## Q3: "Design an agent system that automates [X]."

**What they're testing**: Do you reach for the simplest pattern first? Can you design the harness, not just pick a model?

**Model answer structure**:

1. **Clarify**: Stakes/reversibility? "What happens if the agent makes a mistake — is it recoverable?" Scale? Human involvement expectations?
2. **Start simple**: "Before designing an agent, I'd ask whether a workflow suffices. If the task decomposition is predictable, a prompt chain with gates between steps is simpler, cheaper, and more reliable."
3. **If agency is justified**: Orchestrator-worker pattern with:
   - Typed state graph (LangGraph or similar) with explicit transitions
   - Tool design following ACI principles (descriptions like docstrings for a junior dev, poka-yoke parameters)
   - Verification after every step (test, check, compare)
   - State externalized to disk/DB so the loop is reentrant
   - Circuit breaker: max steps, max cost, error counter
   - HITL for irreversible actions
4. **Shortcomings**: Non-determinism, context rot on long tasks, tool description ambiguity under real inputs
5. **Close**: Pass^k (deployment reliability, not just capability), task completion rate, cost per task, human-override frequency. Future: subagent context firewall for noisy subtasks, trace-based failure clustering.

**Study ref**: [agents guide §1-5](../../guides/4-agents/interview-guide.md); [examples/agent-system.md](examples/agent-system.md); PRINCE case study.

---

## Q4: "Your agent system performance is below expectations — what do you do?"

**What they're testing**: Debugging methodology, measurement-first thinking.

**Model answer**: "I wouldn't touch the agent until I can measure what's failing.

1. **Instrument first**: Traces → failure clustering. Where do tasks fail? Tool errors? Wrong tool selection? Hallucination? Retrieval misses?
2. **Fix eval before agent**: If the eval system is broken (stale golden set, wrong graders), I'm debugging against distorted signals. Fix measurement first.
3. **Decompose the pipeline**: Is it retrieval (low recall@k on golden set)? Tool design (model misusing tools → fix the description, not the prompt)? Model capability (try a larger model on the failing subset)? Context rot (works at turn 3, fails at turn 30)?
4. **Targeted lever, re-measure**: One change at a time. Reranker added? Measure. Tool description rewritten? Measure. Model swapped? Measure.
5. **Don't default to 'bigger model'**: A decent model with a great harness beats a great model with a bad harness."

**Study ref**: [evals guide §5](../../guides/6-evals-observability/interview-guide.md); [agents guide §4](../../guides/4-agents/interview-guide.md) on harness engineering; OpenClaw principle #8 ("fix the eval system first").

---

## Q5: "Design for 100x scale."

**What they're testing**: Do you know which parts of the architecture change and which don't?

**Model answer**: "At 100x, the *logic* doesn't change but the *infrastructure* does:

| What changes | How |
|---|---|
| Read/write paths | Separate them — reads scale horizontally, writes need consistency |
| Caching | Add prefix cache (repeat system prompts) + semantic cache (similar queries) |
| Processing | Async everything non-interactive — embedding, indexing, eval |
| Index | Shard by tenant/collection, ANN instead of brute-force |
| Model serving | Priority tiers: fast-small for simple queries, large for complex; queue management |
| Degradation | Smaller model under load, reduced reranker N, cache-only mode as last resort |
| Cost | Per-component cost model becomes critical — know where the spend is |

What *doesn't* change: the eval pipeline (just runs on a sample), the safety layer, the HITL path, the fundamental data flow."

**Study ref**: [study guide §4](study-guide.md) bottleneck tables; [context/cost guide](../../guides/5-context-cost/interview-guide.md).

---

## Q6: "You have half the budget."

**What they're testing**: Deliberate degradation, not panic.

**Model answer**: "I'd degrade deliberately and state what quality I'm trading:
- **Model tier**: Route easy queries (FAQ, factual lookup) to a smaller/cheaper model; reserve the expensive model for complex reasoning. This alone can cut 50-70% of model costs.
- **Caching**: Aggressive semantic cache — many support queries are near-duplicates
- **Batch vs realtime**: Move non-interactive work (embedding refresh, eval runs, summarization) to off-peak batch
- **Retrieval**: Reduce reranker N, skip reranking for high-confidence first-pass results
- **What I wouldn't cut**: Eval pipeline, safety layer, observability — these are cheap relative to model costs and losing them creates invisible quality drift"

**Study ref**: [context/cost guide](../../guides/5-context-cost/interview-guide.md); model routing in [agents guide §2](../../guides/4-agents/interview-guide.md).

---

## Q7: "On-prem or API?"

**What they're testing**: Compliance awareness, cost reasoning, pragmatism.

**Model answer**: "Decision axes:
- **Data residency/compliance**: If regulated data (PII, PHI, financial) can't leave the network → on-prem or private endpoints with BAAs
- **Volume economics**: At low volume, API is cheaper (no GPU ops burden). Crossover point depends on usage — typically 1M+ calls/month for dedicated inference to break even
- **Capability gap**: Frontier models (Claude, GPT-4) still outperform open models on complex reasoning. If quality matters, API unless compliance forbids it.
- **Ops burden**: On-prem means GPU management, model updates, scaling, monitoring — real engineering cost

**Hybrid is usually the answer**: Sensitive routes on-prem (or private cloud), general routes via API. Route by data classification, not by query type."

**Study ref**: [security guide §5](../../guides/7-security-safety/interview-guide.md) on compliance; [data eng guide](../../guides/8-data-eng-mlops/interview-guide.md).

---

## Q8: "How do you know it works?" (the measurement close)

**What they're testing**: Whether you think about eval unprompted — the strongest candidates state metrics before being asked.

**Model answer**: "Three layers:
1. **Offline eval**: Golden set with human-labeled examples. Two-tier grading: deterministic checks first (format, required fields, no PII), then LLM-as-judge for semantic quality (faithfulness, relevance). Calibrate the judge against human labels. Run on every deploy.
2. **Online eval**: Trace graders scoring live traffic — continuous, not just pre-launch. Alert on quality regression, latency spikes, cost anomalies.
3. **Human feedback**: Thumbs up/down from users → enrich the golden set → close the loop.

Success metrics with numbers: 'p95 under 2s, faithfulness above 0.9 on golden set, deflection rate > 60%, hallucination rate < 5%.' One cost metric: 'cost per query under $0.03 at current volume.'"

**Study ref**: [evals guide §2-5](../../guides/6-evals-observability/interview-guide.md); [examples/eval-harness.md](examples/eval-harness.md).

---

## Q9: "Design the observability stack for your LLM system."

**What they're testing**: Do you understand LLM-specific monitoring beyond standard APM? Can you reason about cost/quality trade-offs in tracing?

**Model answer**: "Two separate tools, different audiences:
- **Infrastructure APM** (Datadog/CloudWatch): uptime, endpoint health, container metrics — same as any service
- **LLM-specific observability** (Langfuse): per-request traces with spans for retrieval/generation/tools, token counts, quality scores, prompt versioning

**Three pillars for LLM systems**: traces (structured single-request path), logs (discrete events via structlog), metrics (aggregates: error rate, tokens/req, cost/query).

**What to trace 100% vs sample**: Metadata (tokens, latency, model) on every request — cheap. Full prompt/response text on 10-20% — storage cost. LLM-as-judge quality scores on 1-5% — compute cost. Increase sampling when investigating.

**Key signals**: routing accuracy (< 85% → alert), tool call latency (p95 > 3s → investigate), context window usage (> 80% → truncate), guardrail hit rate (2x baseline → security review).

**Platform decision**: Langfuse if you need self-hosting or multi-framework support. LangSmith if deeply LangChain-native. Custom (OpenTelemetry + Postgres) only for strict data residency AND custom trace schema needs."

**Study ref**: [evals guide §4-5](../../guides/6-evals-observability/interview-guide.md); librarian wiki: Langfuse Platform, Observability — Langfuse vs Langsmith, Observability Runtime Patterns.

---

## Q10: "How would you design the API for this AI service?"

**What they're testing**: Can you design clean integration boundaries? Do you think about async, idempotency, schema evolution?

**Model answer**: "Key decisions:

1. **Sync vs async**: Both. Short tasks (< 30s) → synchronous REST. Long tasks → async with job ID + polling or webhook callback. The boundary is processing time, not payload size.

2. **Idempotency**: Every mutating endpoint accepts an `idempotency_key`. AI processing is expensive — a retry shouldn't cost another $0.12. Return cached result on duplicate key.

3. **Schema evolution**: URL path versioning (`/v1/`, `/v2/`). Additive-only changes within a version. Breaking changes = new version. Output schemas carry a `schema_version` field so consumers know which version produced the result.

4. **Integration patterns**: REST for human-built consumers (universally understood), MCP for AI-to-AI integration (typed schemas, self-describing), webhooks for event-driven consumers (idempotent handlers, dead-letter for failures), message queue for pipeline integration (fully decoupled, handles backpressure).

5. **Cost transparency**: Return `usage: {input_tokens, output_tokens, model, cost_usd}` in every response. Consider an `/estimate` endpoint for cost prediction before processing."

**Study ref**: [agents guide §3](../../guides/4-agents/interview-guide.md) for tool design / ACI; [security guide §2](../../guides/7-security-safety/interview-guide.md) for auth; librarian wiki: System Design — Serverless Agent Backends.

---

## Q11: "Walk me through your deployment and CI/CD for this system."

**What they're testing**: MLOps maturity, production readiness thinking.

**Model answer**: "Deployment topology depends on who uses it and what it costs:
- **Cloud Run / serverless** for most AI services — auto-scales, pay-per-use, handles the bursty pattern of LLM workloads well. Key constraint: request timeout (manage with async jobs for long tasks).
- **Split service** when scaling needs diverge (API server vs GPU embedding worker vs batch jobs).

**CI/CD pipeline**: PR → lint + unit tests → eval Tier 1 (deterministic, < 3 min, $0) → eval Tier 2 (LLM-as-judge, < 10 min, ~$2) → merge → build → deploy staging → smoke tests → gradual traffic shift → monitor → production.

**What's different about AI CI/CD**: The eval gate is the model-specific addition. Code tests verify the plumbing; eval gates verify the output quality. A prompt change that passes tests but fails the golden set is a regression — same as a code bug.

**Ops concerns specific to AI**: embedder warmup (30-60s cold start → min-instances=1), model version pinning (silent drift without it), prompt versioning (as rigorous as code versioning), checkpointer/topology alignment (MemorySaver fails silently in multi-worker deploys)."

**Study ref**: [data eng & MLOps guide §2](../../guides/8-data-eng-mlops/interview-guide.md); librarian wiki: Cloud Run + Cloud SQL Pattern, Production Hardening Patterns.

---

## Q12: "Design the data pipeline for ingesting documents into your AI system."

**What they're testing**: Pipeline thinking — idempotency, incremental processing, quality gates, failure handling.

**Model answer**: "Four pipeline patterns, choice depends on freshness needs:
- **Batch**: stable corpus, daily/weekly refresh. Simplest, cheapest.
- **Event-driven**: webhook/upload triggers processing. Minutes latency.
- **Streaming**: real-time (WebSocket/SSE). Only when genuinely needed — most 'real-time' needs are actually 'within minutes.'
- **Hybrid**: batch corpus + event-driven updates. Almost always the right answer for production systems.

**Incremental embedding**: Hash each chunk's content. If hash matches → skip embedding. At 70% unchanged content, this saves 70% of embedding cost. Store `content_hash` + `last_embedded` per chunk.

**Idempotency**: Document ID = `(source, source_id, content_hash)`. Processing the same document twice produces the same chunks → upsert, not insert. Safe to retry any stage.

**Quality gates at each stage**: reject corrupt files (ingest) → flag failed OCR (parse) → detect unexpected PII (validate) → alert on abnormal chunk counts (chunk) → verify embedding dimensions (embed) → spot-check retrieval (index). Failed documents → dead-letter queue, never silent drops.

**Schema evolution**: When the embedding model changes, the entire corpus needs re-embedding. Design for it: version embeddings in metadata, support dual-index during migration, run re-embedding as background job."

**Study ref**: [RAG guide §1-2](../../guides/3-rag/interview-guide.md); [data eng guide §1](../../guides/8-data-eng-mlops/interview-guide.md); librarian wiki: Production Hardening Patterns, Embedder Warmup.
