# System Design (ML/LLM/Agent) — Study Guide

The highest-weight technical round in 2026 AIE/MLE loops. This guide is the *method*; the
domain content lives in the [rag](../3-rag/interview-guide.md), [agents](../4-agents/interview-guide.md),
[evals](../6-evals-observability/interview-guide.md), and [context/cost](../5-context-cost/interview-guide.md) guides.
Round-day logistics: [rounds/system-design-round.md](../../rounds/system-design-round.md).

## 1. The process (45–55 min ≈ 8 min/step)

1. **Clarify & scope** — never design against the raw prompt. Three question targets:
   *requirements* (what functions matter), *scale* (1K vs 1M users; global?), *constraints*
   (latency ceilings, budget, data residency). Two openers that always land:
   - "Who are the primary users, and what's the top priority — latency, accuracy, cost,
     safety? That drives every trade-off downstream."
   - "Does the system touch personal/financial data — must it stay on-prem or can we call
     third-party model APIs?"
2. **Requirements split** — functional (multi-turn? follow-ups? autocomplete vs
   summarization?) vs non-functional (latency, consistency/hallucination tolerance, scale,
   security). Write the non-functionals down — they're the trade-off axes.
3. **Design** — components, data flow, APIs; connect every choice back to a requirement,
   out loud.
4. **Identify shortcomings** — name your design's weaknesses before the interviewer does;
   propose what you'd do differently under different constraints.
5. **Iterate** — the best interviews meander through options and converge; curveballs are
   deliberate adaptability tests.

## 2. Trade-off narration (the actual skill being graded)

Formula: **consider 2–3 solutions → narrate pros/cons → ask which priority wins → justify
the pick** ("I'd compromise X for optimal Y — here's why that hurts least given the
priority"). Trade-offs mostly live between non-functionals: latency↔accuracy, cost↔quality,
consistency↔availability, full-automation↔safety, read↔write throughput, storage↔caching.
If told your trade-off was wrong: don't double down — adapt visibly ("with that requirement,
option B's consistency guarantee wins"). No points for stubbornness; growth mindset is
scored.

If you hit a knowledge gap: say so plainly and move on — "my understanding there is
superficial" buys credibility and redirects time to areas you're strong in.

## 3. The LLM-system reference architecture (have it ready to draw)

Client → API gateway (authn, rate limits, quotas) → orchestration (workflow/agent graph) →
{retrieval: query rewrite → hybrid search → rerank} + {generation: prompt assembly →
streaming LLM with fallback chain} → output validation/guardrails → response; sidecars:
caches (prefix + semantic), state store (session/checkpointer), trace/observability, eval
pipeline, HITL queue. For each box, know its failure mode and its scaling story.

## 4. Bottlenecks & failure modes (memorize the tables)

| Bottleneck | Cause | Mitigation |
|---|---|---|
| Token overload | prompt/response too large | truncate, summarize, stream, paginate |
| Queue congestion | slow embedding/model service | shard queues, priority tiers |
| Vector index bloat | stale docs | prune, compress, periodic rebuild |
| Model cold start | on-prem spin-up | warm pools, pre-warming |
| Rate-limited APIs | vendor throttling | backoff retries, caching, multi-provider |

Failure modes: prompt crashes model (detect known patterns) · irrelevant retrieval
(thresholds, metadata filters) · mid-stream failure (graceful fallback to full response) ·
hallucination (grounding scores, double-pass validation). Edge-case reflexes: API-timeout
fallbacks, per-tenant rate limits, graceful degradation under GPU shortage.

## 5. Close with measurement + future

Never stop at the design. State success metrics with numbers ("p95 under 2s while holding
faithfulness above 0.9") and a future-improvements list: distilled model for the easy 80% of
traffic · personalization via summarized user memory · token-cost dashboards + hallucination
scoring · offline batch jobs · A/B framework for prompts/retrieval · feedback loop from
thumbs-down to eval set. One cost line lands well: "at this scale I'd revisit fine-tuning
autocomplete — roughly $30K/month off the API bill."

## 6. Drills (systems you can already speak to)

Three interview-format writeups exist in the librarian wiki — rehearse them as full answers:
- **Shared code-index service** — centralized indexer + query API, MCP as thin read-only
  client, single-writer risk, pgvector escape hatch.
- **Unified eval harness** — golden set, two-tier grading (heuristic → LLM judge),
  regression vs capability harnesses, threshold governance.
- **Serverless agent backends** — stateless invocations, session state in Postgres,
  streaming inside platform timeout budgets, phase-2 stateful handoff design.

Classic prompts to dry-run against the §1 process: support chatbot for a bank
([security guide](../7-security-safety/interview-guide.md) has the governance layer) · document-QA at 10K→1M
docs · code-assistant for private enterprise code (residency → self-hosted vs vendor with
privacy guarantees) · feed/notification ranking (classic + ML hybrid).

## 7. Question bank (answer sketches)

- *"Design a customer-support chatbot."* — clarify: deflection vs CSAT priority? volumes?
  languages? → RAG over approved KB + escalation paths + eval/monitoring + safety rails;
  measure deflection rate, resolution, p95.
- *"Agent system performance is below expectations — what do you do?"* — instrument first:
  traces → failure clustering → is it retrieval, tool design, or model? Fix eval before
  agent (see [evals](../6-evals-observability/interview-guide.md) §5); then targeted lever, re-measure.
- *"Design for 100× scale."* — separate read/write paths, cache tiers, async everything
  non-interactive, shard the index, degrade gracefully (smaller model under load), cost
  model per component.
- *"On-prem or API?"* — residency/compliance, volume economics (crossover math), capability
  gap, ops burden; hybrid: sensitive routes on-prem, general routes API.

## Sources

- notes: [case-interview.md](../../notes/case-interview.md) (System Design Interview Handbook section + bottleneck/failure tables + vantage-point framing)
- images: [case interview evaluation dimensions](../../images/case-interview-evaluation-dimensions.png)
- librarian wiki: System Design — Shared Code-Index Service · System Design — Unified Eval Harness · System Design — Serverless Agent Backends · Orchestration Architecture Decision · Runtime Topology and Checkpointer Alignment
- repo: `../../PORTFOLIO.md` (the deployed systems these drills describe)
- guides: [rag](../3-rag/interview-guide.md) §5 latency budgets · [agents](../4-agents/interview-guide.md) §9 PRINCE reference architecture
