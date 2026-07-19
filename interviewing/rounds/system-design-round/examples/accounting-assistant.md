# Example: Accounting Virtual Assistant

## Prompt
"Design a virtual assistant for an accounting SaaS product. It helps users with bookkeeping questions, VAT rules, and navigating the product — drawing from a knowledge graph of regulatory rules, help articles, and entity relationships."

## Step 1: Clarify & scope (3 min)

**Questions I'd ask**:
- Knowledge domains: product help (how-to), regulatory rules (VAT, tax), or both?
- Jurisdiction: single country or multi-country tax rules?
- Users: accountants (expert) or small business owners (novice)? Language?
- Can the assistant take actions (create invoices, post entries) or information-only?
- How are rules structured: flat articles, structured tables, or a knowledge graph?
- Liability: if the assistant gives wrong tax advice, what's the consequence?

**Assumptions after clarify**:
- Three knowledge layers: procedural (help articles), regulatory (Danish VAT/SKAT rules), entity relationships (VAT codes → expense types → accounts)
- Danish + English, small business owners (novice users)
- Information-only in v1 (no write actions)
- Wrong tax advice = high-consequence (user files incorrect VAT return)
- Hybrid knowledge: flat articles for how-to, structured graph for rule relationships

## Step 2: Requirements (2 min)

**Functional**: Natural-language Q&A across three knowledge layers, rule-based answers with citations to legislation, entity navigation ("which VAT code applies to this expense?"), multi-language (DA/EN).

**Non-functional**: Regulatory accuracy > 0.98 (wrong VAT rate is unacceptable), procedural accuracy > 0.90, p95 < 3s, explicit uncertainty ("I'm not sure about this rule — consult your accountant") when confidence is low.

## Step 3: Design (15 min)

### Architecture

```
User question → Input guardrails (PII, injection)
  → Intent classification:
      procedural ("How do I create a credit note?")
      regulatory ("What's the VAT rate on consulting services?")
      entity ("Which account does this expense post to?")
      out-of-scope ("What's the weather?")

  → Route to knowledge layer:
      Procedural → RAG over help articles (vector + BM25)
      Regulatory → Knowledge graph traversal + rule lookup
      Entity → Knowledge graph query (structured)
      Out-of-scope → polite decline + suggest help center

  → Generate answer with citations:
      Procedural: cite article URL + section
      Regulatory: cite SKAT legislation reference + rule table
      Entity: cite graph path (VAT code → account mapping)

  → Output guardrails (citation check, uncertainty flag)
  → Response
```

### Key design decisions

**Three knowledge layers, not one flat index**: Different knowledge types need different retrieval strategies:

| Layer | Knowledge type | Retrieval | Why not just RAG? |
|-------|---------------|-----------|-------------------|
| **Procedural** | Help articles (how-to, troubleshooting) | Vector + BM25 hybrid → rerank | RAG works well here — articles are natural language |
| **Regulatory** | Tax rules, rates, deadlines | Structured lookup in knowledge graph | Rules have precise values (25% VAT rate) — embedding similarity can't guarantee exact numbers. Graph gives exact answers |
| **Entity** | VAT codes ↔ expense types ↔ accounts | Graph traversal (Cypher query) | Relationships are structured data, not prose. Graph traversal is deterministic |

A flat RAG index would embed the VAT rate table and hope the vector search returns the right row. A knowledge graph query is deterministic: "VAT rate for consulting" → traverse `ServiceType → VATCode → Rate` → 25%. No hallucination possible on the structured path.

**Knowledge graph schema**:

```
(Service/Expense) -[HAS_VAT_CODE]→ (VATCode) -[HAS_RATE]→ (Rate)
(VATCode) -[POSTS_TO]→ (Account)
(FilingPeriod) -[APPLIES_TO]→ (TurnoverBracket)
(InvoiceRequirement) -[REQUIRED_FOR]→ (TransactionType)
```

The graph captures the relationships that users actually ask about: "If I buy consulting services, which VAT code do I use, and which account does it post to?" This is a three-hop traversal, not a retrieval problem.

**Intent classification as router**: A lightweight classifier (Haiku-tier model or fine-tuned small model) routes to the right knowledge layer. Misrouting is the biggest risk — a regulatory question sent to the article RAG pipeline might return a help article that mentions the rule casually instead of the authoritative rule table. The classifier is the critical component: test it as rigorously as the retrieval.

**Uncertainty as a first-class signal**: For regulatory questions, the system must distinguish between:
1. **Confident answer**: rule found in graph, exact match → state the rule with citation
2. **Partial answer**: related rule found, but user's specific case may differ → answer + caveat ("this is the general rule — your case may differ, consult an accountant")
3. **No answer**: no matching rule → explicit "I don't have information about this specific case" + escalation

Never guess at a tax rule. The cost of a wrong VAT rate (financial penalty for the user) far exceeds the cost of saying "I don't know."

### Data pipeline

```
Help articles (CMS):
  - Webhook on publish → re-chunk + re-embed → update vector index
  - Monthly: full re-index to catch orphaned chunks

Regulatory rules (SKAT):
  - Semi-annual review: tax rates, filing deadlines, threshold changes
  - Manual update by domain expert → graph update + version tag
  - Alert on rate/threshold changes detected in SKAT publications

Entity relationships (product data):
  - API sync from accounting SaaS backend (daily)
  - VAT codes, chart of accounts, expense categories
  - Schema validation: alert if new codes appear without graph mappings
```

### Observability

```
Per-request:
  - Intent classification: predicted layer + confidence
  - Retrieval: which layer queried, results, scores
  - Regulatory: graph query path, exact rule returned
  - Generation: answer + citations
  - Uncertainty flag: confident / partial / no-answer

Dashboards:
  - Intent distribution: what are users actually asking?
  - Regulatory accuracy: graded sample of rule-based answers (monthly)
  - Misroute detection: queries where user rephrased after getting a non-answer
  - Knowledge gaps: topics with high "no answer" rate → content backlog
  - Language distribution: DA vs EN (inform localization investment)
```

### Trade-off narrated

**Knowledge graph vs structured RAG**: Knowledge graph for regulatory and entity layers. Structured RAG (embed rule tables, hope for exact retrieval) would work for some queries but fails on precision-critical ones. "What's the VAT rate?" needs to return "25%" deterministically, not "approximately 25% based on similar passages." The graph adds infrastructure cost (Neo4j or similar) but eliminates a class of hallucination that's unacceptable in this domain.

**Multi-agent vs single agent with routing**: Single agent with intent-based routing. Three separate agents (one per knowledge layer) would add coordination overhead and make it harder to handle queries that span layers ("How do I create an invoice for this VAT-exempt service?" = procedural + regulatory). A single agent with routing can combine information from multiple layers in one response.

## Step 4: Shortcomings (3 min)

- **Cross-jurisdiction**: Adding a second country (e.g., expanding from Denmark to Germany) means a second regulatory graph with different rules, rates, and entity relationships. The architecture supports it (tenant-per-jurisdiction), but the content work is substantial.
- **Rule interpretation**: Tax rules have edge cases that require professional judgment. "Is this service VAT-exempt?" may depend on context the user hasn't provided. The system should surface the rule and flag uncertainty, not make the judgment call.
- **Graph maintenance**: The regulatory graph must be manually updated when tax laws change. If the SKAT changes the VAT filing threshold, the graph is wrong until a domain expert updates it. Mitigation: monitor SKAT publications, alert on detected changes, flag answers from rules older than 6 months.
- **Novice users**: Small business owners may not know the correct terminology. "How do I do taxes?" is too vague to route. Mitigation: clarification flow ("Are you asking about VAT filing, corporate tax, or personal income tax?").

## Step 5: Close with measurement (2 min)

**Metrics**: Regulatory accuracy > 0.98 on graded sample (monthly review by domain expert), procedural accuracy > 0.90 on golden set, intent classification accuracy > 0.95, uncertainty flag recall > 0.90 (never confidently state a wrong rule), p95 < 3s.

**Future**: Write actions (create invoice with correct VAT code, auto-fill expense categorization), proactive compliance alerts ("your quarterly VAT filing is due in 10 days"), multi-jurisdiction expansion (Germany, Sweden), integration with bank feeds for auto-categorization.

---

**Study refs**: [RAG guide §1-5](../../../guides/3-rag/interview-guide.md) for retrieval pipeline; [agents guide §1-3](../../../guides/4-agents/interview-guide.md) for routing and tool design; [security guide §5](../../../guides/7-security-safety/interview-guide.md) for compliance and data governance; [evals guide §2-4](../../../guides/6-evals-observability/interview-guide.md) for graded samples; librarian wiki: RAG Retrieval Strategies, Agentic RAG — Advanced Patterns; [data eng guide](../../../guides/8-data-eng-mlops/interview-guide.md) for pipeline patterns.
