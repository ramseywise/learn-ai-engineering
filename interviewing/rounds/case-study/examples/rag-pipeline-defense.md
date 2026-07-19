# Worked Example: RAG Pipeline Defense Round

**Format:** Defense round (30–45 min) — you present a take-home RAG system design, then the panel challenges it.
**Setup:** You built a RAG pipeline for a B2B SaaS company's internal knowledge base (500 docs, 50-page average). The panel has read your submission. Now they challenge it.

This example shows: (1) the original design briefly, (2) each challenge with a model response, and (3) how to adapt visibly when a challenge is valid.

---

## The original design (what you presented)

> "I built a RAG pipeline to help support engineers find answers in our internal knowledge base. The pipeline:
> 1. Ingests 500 docs (PDFs, Markdown) → parses text → chunks at 512 tokens with 64-token overlap
> 2. Embeds chunks with text-embedding-3-small → stores in pgvector
> 3. At query time: embed query → retrieve top-8 chunks → rerank with a cross-encoder → assemble context → GPT-4o mini prompt → response with source citations
> 4. Eval: faithfulness score on 100 labeled QA pairs, CSAT from support team
>
> Results on the eval set: 73% faithfulness, 68% completeness. CSAT from the shadow-mode pilot: 4.2/5."

---

## Challenge 1: "Why fixed-size chunking at 512 tokens?"

**What they're testing:** Did you think about chunking, or did you use the default?

**Model response:**

> "That's a fair challenge. I chose 512 tokens with 64-token overlap as a reasonable starting point for docs that mix prose and structured content — it's large enough to contain a full concept, small enough to fit comfortably in a context window.
>
> The known weakness of fixed-size chunking is that it can split mid-concept — a table or a step-by-step procedure gets truncated at an arbitrary token boundary. In my eval, 18% of the faithfulness failures were traceable to truncated chunks.
>
> If I were iterating, I'd move to semantic chunking: split on sentence and paragraph boundaries, not token count. This preserves concept integrity but requires a sentence segmenter and slightly larger average chunk sizes. I'd also evaluate parent-child retrieval — retrieve small chunks for precision, but expand to the parent section when assembling context."

*Adapts the design based on eval evidence. Does not defend the original choice when there's a clear improvement.*

---

## Challenge 2: "Your faithfulness score is 73%. That seems low for a production system."

**What they're testing:** Can you reason about the metric, diagnose the gap, and propose an improvement path?

**Model response:**

> "73% is not where I'd want it in production — I'd target 85%+ before full rollout. Let me break down why it's at 73% and what I'd do about it.
>
> I labeled 100 QA pairs and looked at the failures:
> - 18% of failures: truncated chunks missing the relevant detail (chunking issue, see above)
> - 31% of failures: the correct chunk ranked 9th or 10th — just outside the top-8 retrieval window (retrieval depth issue)
> - 28% of failures: the LLM synthesized across multiple chunks in a way that combined correct facts into an incorrect composite (generation issue)
> - 23% of failures: genuinely hard queries that span multiple documents with conflicting information
>
> The two biggest levers are: (1) increase retrieval depth from top-8 to top-12 and see if faithfulness improves — cheap to try. (2) Add a generation check: after the LLM produces an answer, run a second LLM call that checks each claim in the answer against the retrieved chunks. If any claim can't be grounded, replace with 'I don't have reliable information on this.' That directly addresses the synthesis failures.
>
> The multi-document conflicts (23%) are genuinely hard and need a different approach — probably a conflict detection step that flags when retrieved chunks contradict each other and presents both perspectives."

*Diagnoses the gap with specific numbers. Proposes a concrete improvement path. Names what's hard and doesn't pretend it's easy.*

---

## Challenge 3: "Why not fine-tune instead of RAG?"

**What they're testing:** Do you understand the RAG-vs-fine-tune trade-off at a mechanical level?

**Model response:**

> "For this specific case, RAG is the right architecture — but I want to walk through why, because fine-tuning wins in some scenarios.
>
> The case for RAG here:
> - The knowledge is in specific documents, not in general domain patterns. The model already 'knows' how to answer questions — it needs access to the right facts, not a different behavior.
> - Our docs are updated monthly when processes change. Fine-tuning requires retraining on every update. RAG lets us re-index in minutes.
> - Support engineers need to see the source — 'RAG said so' isn't trustworthy enough. They need a citation they can click. Fine-tuned models don't produce grounded citations naturally.
>
> The case for fine-tuning would be:
> - The gap is in format or style, not knowledge. If we needed the model to write in our specific support-ticket format consistently, fine-tuning on examples would be more reliable than prompt engineering.
> - The knowledge is stable and large enough that re-indexing is expensive (hundreds of millions of tokens at a time).
> - Latency constraints ruled out retrieval latency. Fine-tuned smaller models can be faster than RAG + GPT-4o.
>
> A hybrid approach — fine-tune for format and routing, RAG for knowledge — is what I'd consider after the MVP. For now, RAG with GPT-4o mini is the faster path to production."

---

## Challenge 4: "What if retrieval quality degrades over time as docs grow?"

**What they're testing:** Operational thinking — can you reason about the system's lifecycle, not just its initial design?

**Model response:**

> "Good question — this is a real operational risk. A few things can degrade retrieval quality as the doc collection grows:
>
> 1. **Index staleness:** New docs aren't indexed yet, so queries that should retrieve new content return old answers. Mitigation: automated re-index trigger on doc upload. I'd add a webhook from the doc management system to the ingestion pipeline.
>
> 2. **Embedding space drift:** If we switch embedding models (for cost or quality reasons), old embeddings and new embeddings are in different vector spaces — retrieval breaks. Mitigation: version the index; run a full re-embed when switching models. This is why I'd treat the embedding model as a dependency with a formal upgrade process.
>
> 3. **Precision decay from volume:** At 500 docs, top-8 retrieval works well. At 5,000 docs, the relevant chunk may rank lower because there are more near-miss chunks competing. Mitigation: (a) add metadata filters (document type, product area) so the query searches a smaller subspace; (b) add a reranker if we don't already have one (I do — the cross-encoder should help); (c) consider a two-tier index: a coarse retriever (BM25) that narrows to 50 candidates, then dense retrieval on those 50.
>
> 4. **Stale content:** Docs that are outdated but not deleted will continue to be retrieved. Mitigation: document freshness metadata in the index, downweight old content in retrieval scoring.
>
> At 10× volume (5,000 docs), I'd rebuild the retrieval layer with the metadata-filtered two-tier design. The cost is maybe 2 weeks of engineering. I'd plan for it explicitly rather than treating it as a surprise."

---

## Challenge 5: "What would you cut if you had one week left before launch?"

**What they're testing:** Prioritization under pressure — what's essential vs. nice-to-have?

**Model response:**

> "One week to launch — I'd ruthlessly cut to: can the system answer questions correctly, and does it fail safely?
>
> **Keep:**
> - Core pipeline (query → retrieve → generate → respond with citation). Non-negotiable.
> - Confidence threshold + 'I don't know' fallback. If retrieval score is low, the system should say 'I don't have reliable information on this' rather than hallucinate. This is a trust feature, not a nice-to-have.
> - Basic monitoring: error rate, latency p95, and a daily sample of 10 responses reviewed by a human. Without monitoring, I can't know when things break.
> - PII scrubber (if customer data could enter the pipeline). Compliance is non-negotiable.
>
> **Cut:**
> - The second-pass generation check (faithfulness verifier). Would help quality but adds 1–2 seconds of latency and complexity. Sprint 2.
> - Multi-document conflict detection. Genuinely hard, would take weeks to do well. Flag as known limitation.
> - Full A/B framework. Manual logging and weekly review is sufficient for a pilot with 20 users.
> - Automated retraining pipeline. Manual re-index on doc update is fine for a 500-doc corpus with monthly updates.
>
> The system I'd launch in a week: it works for 70% of queries, fails gracefully for 30%, and I can see when it breaks. That's a pilot, not production — I'd label it as such and set expectations accordingly."

---

## Challenge 6: "What went wrong in this project?"

**What they're testing:** Honesty, self-awareness, growth mindset. This is an explicit defense-round question in consulting-style loops.

**Model response:**

> "The biggest mistake I made was not doing the failure-mode analysis before starting. I built the pipeline, ran the initial eval, got 73% faithfulness, and then had to reverse-engineer why. If I'd spent 30 minutes at the start thinking 'what are the most likely ways this fails?' I would have known to look at chunk truncation and retrieval depth before writing the first line of code.
>
> Concretely: I would have tested different chunk sizes on a small sample before committing to 512 tokens. That's a 2-hour experiment that would have saved me a week of debugging.
>
> The other thing I'd change: I should have defined the evaluation before building, not after. I wrote the eval set after the pipeline was done, which means I might have unconsciously built the eval to match what the pipeline is good at. In a production setting, the eval set should come from the business — real queries that support engineers actually ask — not generated by me. I'd establish that before writing any code."

*Specific failure, honest diagnosis, concrete counterfactual. Does not blame the prompt or the data. Does not say "everything went perfectly."*

---

## Defense round meta-notes

**The pattern across all good responses:**
1. Acknowledge the challenge specifically, not generically.
2. Explain the original reasoning briefly.
3. State the conditions under which you'd change your answer.
4. Adapt visibly when the challenge is valid — update the design on the spot.
5. Name what's genuinely hard rather than pretending everything has a clean solution.

**The pattern across all failing responses:**
- "That's a great question." (filler, wastes time, reads as stalling)
- Defending the original choice without engaging the challenge.
- "It depends." without specifying what it depends on.
- Solving the challenge by adding more complexity rather than by prioritizing.
- Backpedaling completely without explaining why — "you're right, I'd do X instead" with no reasoning is just as weak as rigid defense.

**The key insight:** interviewers in defense rounds are not trying to trick you. They are testing whether you're the kind of engineer who can receive feedback in a design review and update your thinking in real time. That's the job. Show them you can do it.
