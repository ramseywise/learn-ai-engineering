# System Design Round — Study Guide

The method for the highest-weight technical round. Domain content lives in the [RAG](../../../../generative-ai/02-rag-retrieval/README.md), [harness](../../../../ai-engineering/03-harness-engineering/README.md), [eval](../../../../generative-ai/08-eval/README.md), [context](../../../../ai-engineering/02-context-engineering/README.md) and [safety](../../../../ai-engineering/09-safety-and-security/README.md) pillars; this guide is the *process*.

## 1. The six-step process (45-55 min)

The backend track teaches a different six-step method for classic systems (requirements, estimate, API and data model, sketch, the hard part, failure): [backend chapter 8](../../../../programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md#a-method-to-repeat). That one is for working out a design; this one is for narrating it under interview time. Use the backend method to find the design, then this one to present it.

| Step | What to do | Time |
|------|-----------|------|
| **Clarify & scope** | Never design against the raw prompt. Three targets: requirements (what functions), scale (1K vs 1M), constraints (latency, budget, residency). Two openers that always land — see below. | 8 min |
| **Requirements split** | Functional (multi-turn? follow-ups? summarization?) vs non-functional (latency, consistency, scale, security). Write the non-functionals down — they're the trade-off axes. | 5 min |
| **Design** | Components, data flow, APIs. Connect every choice back to a requirement, out loud. Draw the reference architecture (§3) and customize. | 15 min |
| **Identify shortcomings** | Name your design's weaknesses before the interviewer does. Propose what changes under different constraints. | 8 min |
| **Iterate** | Curveballs test adaptability, so expect to revisit options and converge. If a new requirement changes the pick, say which option now wins and why. | Throughout |
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

## 2b. The trunk — pick your spine before you draw anything

The single fork that determines everything downstream. Ask it during clarification, and
say the answer out loud so the interviewer knows which system you're designing:

```text
"Design X for Y" → clarify → WHAT KIND OF SYSTEM IS THIS?
  ├─ looks things up in documents ──→ RAG spine
  ├─ takes multi-step actions ──────→ AGENT spine
  ├─ predicts / ranks / scores ─────→ ML spine
  └─ transforms a stream of events ─→ PIPELINE spine
```

Most real prompts are one spine plus a cameo from another ("support chatbot" = AGENT spine
with RAG for policy lookup). Name the primary spine, note the secondary, design the primary.

Walking a spine node-by-node — the fork, the discriminator question you ask aloud, what
breaks first, what changes at 10× — is the
[decision tree](decision-tree.md). Drill it there; this
file is the process wrapper around it.

## 3. The LLM-system reference architecture (draw in under 3 min)

```text
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

For each box, know its **failure mode** and its **scaling story**. [Backend chapter 10](../../../../programming/backend-and-system-design/notes/10-ai-system-reference-architecture.md) builds this architecture's gateway (token budget, fallback, streaming) and links to the note behind each box.

### Component deep-dive pointers

Lookup by component name. When you need *"which option do I pick and why"* rather than
*"where do I read about this"*, use the
[decision tree](decision-tree.md) instead — same
components, organized by the question you're being asked.

| Component | Study guide | Example |
|-----------|-----------|---------|
| Retrieval pipeline (chunking, embedding, hybrid search, reranking) | [RAG pillar](../../../../generative-ai/02-rag-retrieval/README.md) | [rag-system](examples/rag-system.md) |
| Orchestration (workflow patterns, agent loops, tool design) | [graph vs loop](../../../../ai-engineering/05-graph-engineering/notes/01-graph-vs-loop.md) | [agent-system](examples/agent-system.md) |
| Eval pipeline (graders, golden sets, online scoring) | [graders](../../../../generative-ai/08-eval/notes/04-graders.md) | [eval-harness](examples/eval-harness.md) |
| Context management (token budgets, caching, compaction) | [context pillar](../../../../ai-engineering/02-context-engineering/README.md) | [scaling](examples/scaling.md) |
| Safety layer (guardrails, trust separation, HITL) | [safety pillar](../../../../ai-engineering/09-safety-and-security/README.md) | — |
| State & memory (checkpointers, session state, memory types) | [memory](../../../../ai-engineering/02-context-engineering/notes/06-memory.md) | — |
| Data pipeline (ingestion, preprocessing, feature stores) | [data engineering](../../../../data-engineering/README.md) | [rag-system](examples/rag-system.md) |
| Observability & tracing (Langfuse vs Langsmith, metrics, cost) | [tracing and observability](../../../../generative-ai/08-eval/notes/08-tracing-and-observability.md) | [eval-harness](examples/eval-harness.md) |
| Deployment & ops (Cloud Run, CI/CD, model versioning, drift) | [ML platform](../../../../data-engineering/06-ml-platform/README.md) | — |
| Integration patterns (API, MCP, webhooks, event-driven) | [tool design](../../../../ai-engineering/03-harness-engineering/notes/03-tool-design.md) | — |
| Knowledge graphs (structured retrieval, entity relationships) | [RAG in production](../../../../generative-ai/02-rag-retrieval/notes/07-rag-in-production.md) | — |

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
| Trace storage growth | 100% tracing at scale → storage/cost explosion | Keep metadata for every trace; sample full text and quality scoring, and pick the rates from your budget |
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
> "At this scale I'd revisit fine-tuning autocomplete", followed by the figure you worked out for this design, with its volume and price assumptions.

## 6. Drills (systems you can already speak to)

Three interview-format writeups in the librarian wiki — rehearse as full 45-min answers:

1. **Shared code-index service** — centralized indexer + query API, MCP as thin read-only client, single-writer risk, pgvector escape hatch
2. **Unified eval harness** — golden set, two-tier grading (heuristic → LLM judge), regression vs capability, threshold governance
3. **Serverless agent backends** — stateless invocations, session state in Postgres, streaming within platform timeouts, phase-2 stateful handoff

Your own systems are the strongest material in an interview: prepare one or two the same way.

Classic prompts to dry-run:

- Support chatbot for a bank ([safety pillar](../../../../ai-engineering/09-safety-and-security/README.md) has the governance layer)
- Document-QA at 10K→1M docs
- Code-assistant for private enterprise code (residency → self-hosted vs vendor)
- Feed/notification ranking (classic + ML hybrid)

## Practice plan

1. **Draw the reference architecture** from memory 3x this week. Time yourself — under 3 min.
2. **Dry-run one classic prompt** per day: set a 40-min timer, talk through the 6 steps out loud, record yourself if possible.
3. **Memorize the bottleneck + failure tables** — interviewers ask "what breaks first?" and expect instant answers.
4. **Rehearse trade-off narration**: for each design decision, practice the formula (2-3 options → pros/cons → ask priority → justify pick).
5. **Prepare the recovery move**: have a friend challenge your trade-off, practice adapting visibly instead of defending.
6. **Know one cost number**: be able to say something like "$X/month at this scale, here's what I'd optimize."
7. **Read**: The [PRINCE case study](https://martinfowler.com/articles/reliable-llm-bayer.html) is the best single reference for production agentic RAG design with real engineering decisions.
