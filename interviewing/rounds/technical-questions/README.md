# Technical Questions — ML/LLM Breadth Round

## What's tested

Rapid-fire conceptual fluency: can you explain core mechanisms in 60 seconds with one level of depth in reserve? The follow-up question is where the signal is — memorized definitions collapse on the second "why?".

This is not a coding round. It's a verbal fluency check across a breadth of ML/LLM concepts, with the interviewer probing depth on whichever topics stall you.

## Format

30–45 min, often folded into another round's first half. 2026 loops front-load transformer/LLM-era questions: attention, tokenization, RLHF/DPO, RAG-vs-fine-tuning, hallucination mechanisms, context windows, chain-of-thought, temperature/sampling — with classical ML as the sanity-check layer.

Real screen question lists run: "What is RAG? Graph+RAG? Chain of Thought? Reflection? How do you manage memory and context? How do you ensure models don't hallucinate?"

## Per-role weighting

| AIE | MLE | DS | FDE |
|-----|-----|-----|-----|
| ●   | ●   | ◐   | ●   |

AIE/FDE versions skew LLM-era topics; MLE adds classical depth; DS versions fold into the stats/SQL screen.

## Folder contents

| File | Purpose |
|------|---------|
| `questions.md` | 25–30 questions organized by domain, each with 60-second answer + one level deeper + study ref |
| `study-guide.md` | Method, trade-off pairs, flashcard approach, per-role priorities, practice plan, anti-patterns |
| `sources.md` | Internal cross-reference (study guides, notes) + external resources |

**No `examples/` folder** — `questions.md` with 60-second + deeper answers IS the worked content for this round. The domain study guides carry the full treatment.

## Prep checklist

- Work the ●-topics for your role in the README matrix — each study guide's question bank is this round's drill set.
- For every concept, rehearse the 60-second version + the one-level-deeper version (`study-guide.md` covers the method).
- Practice the honest-gap move: "my understanding there is superficial" then redirect.
- Trade-off pairs on flashcards: RAG vs fine-tune, precision vs recall, batch vs streaming, LoRA vs full FT, on-prem vs API. Full list in `study-guide.md`.
- Claim audit: everything on your resume is fair game.

## Note on content placement

The substantive content for this round lives primarily in the domain study guides (all ten). This folder organizes the *method* (how to answer rapidly under pressure) and the *question index* (the drill set, with depth markers). Go to the study guides for the full treatment of any topic.
