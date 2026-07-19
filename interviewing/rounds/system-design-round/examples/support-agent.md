# Example: Customer Support Help Center Agent

## Prompt
"Design a customer support agent for a SaaS product. It answers user questions from a help center knowledge base, with citation enforcement and human escalation."

## Step 1: Clarify & scope (3 min)

**Questions I'd ask**:
- Help center size? (50 articles or 5,000?)
- Channels: web chat widget, email, Slack, all of the above?
- Languages: English only, or multilingual? (Affects retrieval + generation)
- Existing support tooling: Intercom, Zendesk, custom?
- Safety requirements: regulated industry? (Financial services, healthcare — different guardrail needs)
- Can the agent take actions (create tickets, update accounts) or is it information-only?

**Assumptions after clarify**:
- ~200 help articles (accounting/financial SaaS), web chat widget
- Information-only (no write actions in v1)
- Must cite sources — wrong financial advice is high-consequence
- Must escalate when confidence is low or when user explicitly asks for a human
- Multi-language (English + Danish), single-tenant for now

## Step 2: Requirements (2 min)

**Functional**: Natural-language Q&A over help center corpus, citations with article URLs, human escalation path, PII redaction (users may paste account numbers), injection defense.

**Non-functional**: p95 < 3s, grounding score > 0.95 (every claim must be supported by a cited passage), zero PII in logs/traces, escalation rate < 20% (too high = agent not useful; too low = suppressing escalation).

## Step 3: Design (15 min)

### Architecture

```
User message → Input guardrail pipeline:
    1. Unicode sanitize (homoglyphs, zero-width chars)
    2. PII detect + redact (CPR, email, phone, IBAN → [REDACTED])
    3. Injection detection (regex: ignore-previous, role-play, jailbreak)
    → blocked? → return error message

Clean message → Retrieval:
    → Query rewrite (coreference for multi-turn)
    → Hybrid search: vector (embedding) + BM25
    → Cross-encoder rerank top-20 → top-5
    → CRAG confidence gate:
        score ≥ 0.7 → generate with context
        score 0.4–0.7 → expand query, retry
        score < 0.4 → escalate ("I can't find relevant information")

Generate → AssistantResponse:
    {answer, sources: [{title, url, quote}], confidence, escalate}

Output guardrail pipeline:
    Tier 1: cited URLs ∈ retrieved URLs (set membership, O(n))
    Tier 2: claims cross-reference citations (structural check)
    Tier 3: supporting quotes appear in cited passages (token overlap)
    Missing citation guard: KB was called but no citations + no "insufficient info" → escalate
    → any hard fail → rewrite to escalation response

Response → User
```

### Key design decisions

**Three agents, one eval suite**: Build the same agent in three frameworks (ADK, LangGraph CRAG, vanilla LangGraph) sharing the same guardrail layer and eval harness. Why? Apples-to-apples comparison on the same golden set reveals which framework gives better retrieval quality, latency, and cost — not a theoretical choice but a measured one.

**Five-layer guardrail architecture**:

| Layer | When | What | Cost |
|-------|------|------|------|
| 1. Input sanitization | Pre-model | Unicode, PII redact, injection block | < 1ms, $0 |
| 2. Retrieval confidence gate | Pre-generation | CRAG score threshold | ~50ms, $0 |
| 3. System prompt constraints | During generation | "Only answer from provided context" | $0 (prompt tokens) |
| 4. Output grounding check | Post-generation | Citation verification (4 tiers) | < 1ms, $0 |
| 5. LLM-as-judge (offline) | Eval pipeline | Semantic grounding score | ~$0.05/query |

Layers 1-4 are deterministic, zero-cost, real-time. Layer 5 is expensive but runs only in eval, not on every request. This means safety doesn't add latency or cost in production.

**Citation enforcement over hallucination detection**: Don't try to detect hallucinations after the fact — enforce citations structurally. If the model can't cite a source for a claim, the output guardrail catches it and escalates. This is cheaper and more reliable than LLM-as-judge on every response.

**Escalation as a first-class output**: The `AssistantResponse` schema has an explicit `escalate: bool` field. Three triggers:
1. Retrieval confidence below threshold (CRAG gate)
2. Output guardrail hard fail (citation check)
3. User explicitly requests a human

The frontend receives the escalation signal and shows a handoff UI. The agent never says "I don't know" without also offering the human path.

### Observability

```
Every request traced (Langfuse):
  - Retrieval: query, top-k results with scores, reranker scores
  - Generation: model, tokens, latency
  - Guardrails: which layers triggered, pass/fail, rewrite details
  - Outcome: escalated? cited correctly? user satisfaction?

Dashboards:
  - Grounding score distribution (should be bimodal: high or escalated)
  - Escalation rate by topic (which categories need more content?)
  - PII detection rate (are users leaking sensitive data?)
  - Agent comparison (ADK vs LG CRAG vs LG vanilla: quality, cost, latency)
```

### Trade-off narrated

**Single agent vs multi-agent**: Single agent with guardrail layers, not a multi-agent system. The task is retrieval + generation + validation — one cognitive loop. Multi-agent adds latency and coordination complexity without proportional benefit here. The "multiple implementations" approach (3 frameworks) is for comparison during development, not for production routing.

**Strict grounding vs flexible responses**: Strict. In accounting/financial SaaS, a wrong answer about VAT rules or deductibility is worse than no answer. The citation enforcement means the agent can only say what the knowledge base says. Trade-off: the agent can't synthesize across articles as freely, and some nuanced questions will escalate. That's the right failure mode for this domain.

### Data pipeline

```
Help center articles (CMS) → Incremental sync:
  - New/updated articles: parse → chunk (heading-based) → embed → index
  - Deleted articles: remove from index + invalidate cached responses
  - Frequency: webhook on publish (real-time) or daily batch
  - Quality gate: alert if article count drops > 10% (mass deletion?)
```

## Step 4: Shortcomings (3 min)

- **Cross-article synthesis**: "Compare the VAT rules for these two expense types" requires information from multiple articles. The agent retrieves top-5 — may not get both. Mitigation: multi-query retrieval (reformulate into per-topic queries).
- **Stale content**: If the help center is updated but the index isn't refreshed, the agent cites outdated information. Mitigation: webhook-triggered re-indexing on article publish.
- **Domain knowledge gaps**: The agent can only answer what's in the KB. New features without documentation = guaranteed escalation. Mitigation: track "no relevant results" queries → feed to content team as documentation gaps.
- **Multi-turn context**: The CRAG confidence gate evaluates each turn independently. A follow-up like "what about the other one?" may lose context. Mitigation: query rewrite with coreference resolution using conversation history.

## Step 5: Close with measurement (2 min)

**Metrics**: Grounding score > 0.95 on golden set (50 QA pairs), escalation rate 10-20%, p95 < 3s, zero PII in traces, citation accuracy > 0.98 (Tier 1-2 hard fail rate < 2%).

**Future**: Write actions (create ticket, update account settings) with confirmation step, multi-language retrieval (cross-lingual embedding), topic routing to specialized sub-agents (billing vs product vs regulatory), proactive suggestions ("you might also want to know...").

---

**Study refs**: [RAG guide §1-5](../../../guides/3-rag/interview-guide.md) for retrieval pipeline and CRAG; [security guide §3-4](../../../guides/7-security-safety/interview-guide.md) for guardrail layers and trust boundaries; [agents guide §3](../../../guides/4-agents/interview-guide.md) for tool design; [evals guide](../../../guides/6-evals-observability/interview-guide.md) for grounding graders; librarian wiki: Production Hardening Patterns, Safeguards Architecture.
