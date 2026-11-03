# Sources — Technical / ML/LLM Breadth Round

This file is the master cross-reference for round content. Pointers only — go to the source for substance.

---

## Internal: Pillar notes

The pillar notes are the primary content source for this round, and their `Interview checklist` sections are the drill set for each domain.

| Pillar | What it covers for this round |
|-------|-------------------------------|
| [LLM fundamentals](../../../../generative-ai/01-llm-fundamentals/README.md) | Attention, positional encoding, hallucination, sampling, fine-tuning. Q1-Q4, Q7. |
| [RL](../../../../generative-ai/05-RL/README.md) | RLHF, reward modeling, PPO. Q4. |
| [prompting](../../../../ai-engineering/01-prompt-engineering/README.md) | CoT and self-consistency. Q6. |
| [RAG and retrieval](../../../../generative-ai/02-rag-retrieval/README.md) | Pipeline, chunking, hybrid search, reranking, RAG eval. Q8-Q12. |
| [context](../../../../ai-engineering/02-context-engineering/README.md) | Window management, lost in the middle, prompt caching, token economics. Q5, Q24-Q26. |
| [harness](../../../../ai-engineering/03-harness-engineering/README.md) and [graphs](../../../../ai-engineering/05-graph-engineering/README.md) | Workflow vs agent, tool design, multi-agent patterns. Q13-Q16. |
| [eval](../../../../generative-ai/08-eval/README.md) | LLM as judge, golden sets, online vs offline eval, calibration. Q17-Q20. |
| [safety and security](../../../../ai-engineering/09-safety-and-security/README.md) | Prompt injection, PII, trust boundaries, least privilege. Q21-Q23. |
| [classical ML](../../../../data-science/01-classical-ml/README.md) | Bias-variance, precision-recall, regularization, cross-validation. Q27-Q30. |
| [experimentation](../../../../data-analytics/03-experimentation-and-causality/README.md) | Distributions, intervals, p-values, A/B tests. |

---

## Internal: Notes and planning docs

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
