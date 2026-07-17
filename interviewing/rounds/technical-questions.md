# Technical Questions (ML/LLM breadth round)

## What's tested
Rapid-fire conceptual fluency: can you explain core mechanisms in 60 seconds with one
level of depth in reserve? The follow-up question is where the signal is — memorized
definitions collapse on the second "why?".

## Format & trends
30–45 min, often folded into another round's first half. 2026 loops **front-load
transformer/LLM-era questions** (research F4): attention, tokenization, RLHF/DPO,
RAG-vs-fine-tuning, hallucination mechanisms — with classical ML (bias–variance, metrics)
as the sanity-check layer, weighted by role. Real screen lists (interviews.chat, notes)
run: "What is RAG? Graph+RAG? Chain of Thought? Reflection? How do you manage memory and
context? How do you ensure models don't hallucinate?" — breadth over depth, then depth on
whatever you claim.

## Prep checklist
- [ ] Work the ●-topics for your role in the [README matrix](../README.md) — each study
  guide's question bank *is* this round's drill set.
- [ ] For every concept, rehearse the 60-second version + the one-level-deeper version
  (e.g., attention → then KV cache; RLHF → then reward hacking and DPO).
- [ ] Practice the honest-gap move: "my understanding there is superficial" then redirect
  — credibility beats bluffing (notes: case-interview).
- [ ] Trade-off pairs on flashcards: RAG vs fine-tune, precision vs recall, batch vs
  streaming, LoRA vs full FT, on-prem vs API.
- [ ] Claim audit: everything on your resume is fair game — if you list it, you can
  explain it two levels deep.

## Question bank (samplers — full banks live in the guides)
- "Explain attention to a PM." → [llm-fundamentals](../guides/2-llm-fundamentals/interview-guide.md) §6
- "Why does the model hallucinate citations, and what do you do about it?" → llm-fundamentals §5, [rag](../guides/3-rag/interview-guide.md)
- "RAG or fine-tuning for X?" → llm-fundamentals §3 (the adaptation ladder)
- "Precision vs recall — when does each matter?" → [ml-foundations](../guides/1-foundations/interview-guide.md) §2
- "How do you evaluate an LLM system beyond accuracy?" → [evals-observability](../guides/6-evals-observability/interview-guide.md)
- "What is prompt injection and one real defense?" → [security-safety](../guides/7-security-safety/interview-guide.md)
- "What's in your context window and why does ordering matter?" → [context-engineering-cost](../guides/5-context-cost/interview-guide.md)

## Per-role weighting
| AIE | MLE | DS | FDE |
|---|---|---|---|
| ● | ● | ◐ | ● |

AIE/FDE versions skew LLM-era topics; MLE adds classical depth ([ml-foundations](../guides/1-foundations/interview-guide.md));
DS versions fold into the stats/SQL screen instead.

## Links
- Study guides: all ten — this round is the matrix row-by-row; start from the [README](../README.md).
- Research: F4 in `.claude/docs/plans/2026-07-17-interview-kb-consolidation.md`; notes: [case-interview.md](../notes/case-interview.md) (screen-question list)
