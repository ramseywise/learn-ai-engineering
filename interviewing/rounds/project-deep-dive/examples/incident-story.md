# Example: Incident Story — Retrieval Quality Degradation

**Question**: "Tell me about the hardest bug or incident you dealt with in a system you built."

This example demonstrates the detection → isolation → root cause → fix → prevention structure. The incident: silent retrieval quality degradation in a RAG pipeline after a document corpus update.

---

## The story

**Detection**

> "Three weeks after a major corpus update — we added about 200 new policy documents — a program manager came to me saying the system was 'giving wrong answers.' When I looked at her examples, the responses were confident and well-formatted, but they were citing outdated policy versions that we'd replaced. The system had no monitoring on retrieval quality, only on latency and error rate. Those were both green. We had a silent correctness failure."

**[Signal sent]**: Opens with symptoms, not cause. Names the specific failure mode (outdated citations, not errors). Immediately flags the monitoring gap.

---

**Isolation**

> "My first hypothesis was that the old documents hadn't been deleted from the index before re-ingestion. We had a process that was supposed to delete old vectors by document ID before adding new ones, and I thought it might have failed silently. I ran a query against the Pinecone index metadata filtering on document IDs that should no longer exist — and I found them. Old document vectors were still in the index alongside the new ones.
>
> But that still didn't explain why the retrieval was preferring old documents. The new documents should have been more semantically similar to current queries about current policy. So I pulled the retrieval traces — we were logging the top-5 chunks and their similarity scores — and compared old vs. new document chunks on a few representative queries. The new document chunks were appearing in position 4 or 5. The old ones were ranking higher.
>
> That's when I looked at the embedding timestamps in the metadata."

**[Signal sent]**: Shows reasoning in real time — a hypothesis, how it was tested, what it revealed, what it didn't explain, and what led to the next hypothesis. This is the forensics the interviewer is looking for.

---

**Root cause**

> "The new documents had been ingested using a different embedding model version. OpenAI had silently updated text-embedding-3-small and the new model produced vectors that weren't directly comparable to the vectors from the old model. When we searched the index with the new model, we got old-model vectors as the top results because they happened to sit closer in the space being searched.
>
> The root cause: no model version pinning in our ingestion pipeline. We were calling `openai.embeddings.create(model='text-embedding-3-small')` and trusting that the output was stable across time. It wasn't. The corpus now contained vectors from two incompatible model versions, and queries using the current model preferred the old-format vectors because of how the two generations' vector spaces overlapped."

**[Signal sent]**: Specific. Names the exact mechanism (two incompatible model version vector spaces coexisting in the same index). Not "there was a model update" but why that update caused the ranking failure.

---

**Fix**

> "Immediate fix: re-ingest the entire corpus with the pinned model version — we pinned to the specific snapshot version available through the API. That took six hours overnight. Before we re-ingested, we deleted all vectors from the index rather than trying to do a selective update.
>
> We also added a retrieval quality check to the post-ingestion process: after any bulk update, we run 20 hand-labeled queries from a golden set and check that the expected document appears in the top-3 results. If it doesn't, ingestion is flagged as degraded and we don't flip production traffic to the new index."

**[Signal sent]**: Both the immediate fix (re-ingest with pinned version) and the stabilizing change (golden set eval). Shows the fix was complete, not just a hotfix.

---

**Prevention**

> "Three things we added to prevent recurrence:
>
> One — model version pinning in the ingestion config, committed to version control. Upgrading the model now requires an explicit config change and re-ingestion of the full corpus.
>
> Two — corpus integrity check: after any ingestion run, verify that all vectors in the index share the same model version tag in their metadata. If they don't, alert.
>
> Three — a retrieval quality eval as a required step in the ingestion pipeline. Not a one-time golden set — a continuously maintained set of 50 query-document pairs that runs before any index swap is considered complete.
>
> The monitoring gap that let this go undetected for three weeks was the more important lesson. We had excellent latency and error-rate monitoring but no correctness signal. Adding the retrieval eval caught a smaller degradation two months later — a chunking change that fragmented a critical policy document — before any user saw it."

**[Signal sent]**: Three concrete preventions, each an artifact you can point to (config change, integrity check, eval harness). Closes by naming the broader lesson (correctness monitoring gap) and showing it paid off.

---

## Follow-up probes and brief answers

**"How long between the update and the user reporting it?"**
> "Three weeks. In retrospect, if we'd run a retrieval eval after the ingestion, we would have caught it that night. The latency between cause and detection was entirely a monitoring gap."

**"What was the customer impact?"**
> "Program managers were citing outdated policy to clients for three weeks. We don't know how many client interactions were affected. We sent a correction to the program team and they did a manual review of their case notes from that period. No formal complaints, but it was a significant trust event."

**"Did you consider a hybrid or versioned index approach instead of full re-ingestion?"**
> "We evaluated a blue-green index approach — maintain two indexes and swap the active pointer. It would have avoided the six-hour window and given us a clean rollback path. We didn't implement it because our ingestion frequency was low enough that the operational complexity wasn't justified. If we were ingesting daily or had stricter uptime requirements, blue-green would have been the right call."

---

## What this example demonstrates

| Part | What makes it work |
|------|--------------------|
| Detection | Opens with what monitoring showed (or didn't) — not the cause. Names the specific failure symptom. |
| Isolation | Shows a reasoning chain with intermediate hypotheses. What you ruled out matters as much as what you found. |
| Root cause | Specific mechanism, not a category ("model update" is too vague — the vector space incompatibility is the real cause). |
| Fix | Both immediate (re-ingest) and stabilizing (golden eval). Shows the thinking was complete. |
| Prevention | Three concrete artifacts. Closes with the broader lesson and evidence it was applied. |

**The hardest part to fake**: The isolation section. If you didn't actually debug this, you can't narrate the intermediate steps — what you tried first, what it ruled out, what led to the next hypothesis. Practice narrating your debugging process, not just your conclusions.
