# Sources — Technical / ML/LLM Breadth Round

This file is the master cross-reference for round content. Pointers only — go to the source for substance.

---

## Internal: Study guides

The ten domain study guides are the primary content source for this round. Each guide's question bank IS the drill set for its domain.

| Guide | What it covers for this round |
|-------|-------------------------------|
| `transformers-attention` | Attention mechanism, multi-head attention, positional encoding, transformer architecture. The LLM fundamentals Q1 backbone. |
| `hallucination-and-reliability` | Hallucination mechanisms, citation fabrication, mitigation strategies (RAG grounding, verifier agents, constrained decoding). Q2. |
| `rag` | Full RAG pipeline, chunking strategies, hybrid search, reranking, CRAG/self-RAG, eval (RAGAS). Q8–12 source. |
| `fine-tuning` | SFT, LoRA/QLoRA, RLHF, DPO, when fine-tuning vs RAG. Q3, Q4 depth. |
| `alignment` | RLHF vs DPO, reward modeling, PPO instabilities, IPO/ORPO variants. Q4 source. |
| `prompt-engineering` | CoT, zero-shot CoT, few-shot CoT, self-consistency. Q6 source. |
| `inference-and-sampling` | Temperature, top-p, top-k, beam search, nucleus sampling. Q7 source. |
| `context-engineering` | Context window management, lost-in-the-middle, prompt caching, token economics, context ordering. Q5, Q24–26 source. |
| `agents` | Workflow vs agent, tool design, loop engineering, multi-agent patterns. Q13–16 source. |
| `evals` | LLM-as-judge, RAGAS, golden sets, online vs offline eval, calibration. Q17–20 source. |
| `security` | Prompt injection, PII handling, trust boundaries, least-privilege tool design. Q21–23 source. |
| `ml-fundamentals` | Bias-variance, precision-recall, regularization, cross-validation. Q27–30 source. |

---

## Internal: Notes and planning docs

- `interviewing/notes/case-interview.md` — contains real screen question lists from actual interviews. Q7 of this round ("What is RAG? Graph+RAG? Chain of Thought? Reflection?") came from a real screen list documented there.
- `interviewing/README.md` — the role × round matrix. Drives the per-role weighting column in this folder's README.
- `interviewing/rounds/` — sibling round folders. This round overlaps with `system-design-round` (LLM system architecture questions surface in both) and `coding-challenge` (some coding screens include ML-adjacent implementation).

---

## External: Transformer / LLM fundamentals

- **"Attention Is All You Need" (Vaswani et al., 2017)** — the original transformer paper. Read the attention mechanism section (Section 3.2). Everything in Q1 traces to here.
- **The Illustrated Transformer (Jay Alammar)** — visual walkthrough of self-attention and multi-head attention. Better for interview prep than the paper itself.
- **"Lost in the Middle" (Liu et al., 2023)** — empirical study on position effects in long contexts. The specific finding driving Q5.
- **DPO paper (Rafailov et al., 2023)** — "Direct Preference Optimization: Your Language Model is Secretly a Reward Model." Required reading if interviewing at labs or fine-tuning-adjacent roles.

---

## External: RAG

- **RAGAS paper / docs** — the retrieval-augmented generation evaluation framework. Faithfulness, answer relevance, context precision, context recall metrics. Primary eval framework for Q17.
- **CRAG paper (Yan et al., 2024)** — "Corrective Retrieval Augmented Generation." Q11 source.
- **Self-RAG paper (Asai et al., 2023)** — "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection." Q11 alternative approach.
- **BGE / Cohere Rerank docs** — practical reranker models for Q10.

---

## External: Classical ML

- **"The Elements of Statistical Learning" (Hastie, Tibshirani, Friedman)** — canonical reference for bias-variance, regularization, cross-validation. Dense but authoritative. Chapters 2, 3, 7.
- **"Hands-On Machine Learning" (Géron)** — practical treatment of the same material. Better for interview prep because it connects theory to implementation.
- **ML interview question banks** — search "ML interview questions github" — multiple curated repositories. Useful for breadth drilling after you've covered the domains above.

---

## External: Security

- **"Prompt Injection" — Simon Willison's blog** — best practical treatment of indirect injection via retrieved content. Running series, search his site.
- **OWASP Top 10 for LLMs** — the canonical list of LLM security risks. Covers prompt injection, insecure output handling, training data poisoning, model DoS. Q21–23 aligns with items 1, 2, 6.
