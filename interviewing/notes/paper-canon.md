---
origin: web-article
confidence: high
sources:
  - https://reliable-data-engineering.netlify.app/posts/article_10_research_papers_ai_engineer_interview/
    ("10 Research Papers Every AI Engineer Must Read Before Their Next Interview",
    Reliable Data Engineering, 2026-03-29)
added: 2026-07-29
---

# Paper Canon — the 10 interview-standard papers

The architecture papers an AI-engineering interviewer can reasonably expect you to
name, date, and explain in two sentences. Sourced from the article above; every PDF is
held in this repo (paths below), so nothing here needs a network fetch.

Complements [reading-list.md](reading-list.md) (broad link dump) — this file is the
short, closed list you can actually finish before an interview.

## The list

| # | Paper | Year | ID | Local copy | The one-sentence answer |
|---|---|---|---|---|---|
| 1 | Attention Is All You Need (Transformer) — Vaswani et al., Google Brain | 2017 | [1706.03762](https://arxiv.org/abs/1706.03762) | `ai-engineering/readings/general/1706.03762v7.pdf` | Replaced sequential RNNs with self-attention: parallel training + direct long-range dependencies |
| 2 | BERT: Pre-training of Deep Bidirectional Transformers — Devlin et al., Google AI | 2018 | [1810.04805](https://arxiv.org/abs/1810.04805) | `ai-engineering/readings/general/1810.04805v2.pdf` | Bidirectional pretraining via masked LM — the encoder branch, for understanding tasks |
| 3 | Improving Language Understanding by Generative Pre-Training (GPT-1) — Radford et al., OpenAI | 2018 | [OpenAI PDF](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) | `ai-engineering/readings/general/gpt1-improving-language-understanding.pdf` | Decoder-only next-token prediction at scale yields general-purpose models — the branch that won |
| 4 | LoRA: Low-Rank Adaptation of LLMs — Hu et al., Microsoft | 2021 | [2106.09685](https://arxiv.org/abs/2106.09685) | `generative-ai/01-llm-fundamentals/readings/2106.09685.pdf` | Fine-tune by learning low-rank weight *updates*, leaving base weights frozen |
| 5 | PEFT: Parameter-Efficient Fine-Tuning Methods — a survey, Xu et al. | 2023 | [2312.12148](https://arxiv.org/abs/2312.12148) | `generative-ai/01-llm-fundamentals/readings/2312.12148.pdf` | Maps the adapter / prefix-tuning / prompt-tuning landscape around LoRA |
| 6 | Retrieval-Augmented Generation for Knowledge-Intensive NLP — Lewis et al., FAIR | 2020 | [2005.11401](https://arxiv.org/abs/2005.11401) | `generative-ai/02-rag-retrieval/3-rag/2005.11401v4.pdf` | Ground generation in retrieved documents — non-parametric knowledge you can update without retraining |
| 7 | An Image is Worth 16x16 Words (ViT) — Dosovitskiy et al., Google Brain | 2020 | [2010.11929](https://arxiv.org/abs/2010.11929) | `ai-engineering/readings/general/2010.11929.pdf` | Transformers on image patches; beats CNNs only once the dataset is large enough |
| 8 | Auto-Encoding Variational Bayes (VAE) — Kingma & Welling, Amsterdam | 2013 | [1312.6114](https://arxiv.org/abs/1312.6114) | `ai-engineering/readings/general/1312.6114.pdf` | Continuous structured latent spaces via probabilistic encoding + the reparameterization trick |
| 9 | Generative Adversarial Networks — Goodfellow et al., Montréal | 2014 | [1406.2661](https://arxiv.org/abs/1406.2661) | `ai-engineering/readings/general/1406.2661.pdf` | Generation as a minimax game between generator and discriminator |
| 10 | High-Resolution Image Synthesis with Latent Diffusion — Rombach et al. | 2022 | [2112.10752](https://arxiv.org/abs/2112.10752) | `ai-engineering/readings/general/2112.10752.pdf` | Run diffusion in a compressed latent space — what made high-res synthesis affordable |

Also cited by the article as background, not a paper: **Designing Data-Intensive
Applications** (Kleppmann) — the distributed-systems substrate under large-scale ML.

## Reading order (not the article's order)

The article lists these chronologically-ish. For interview prep the useful order is by
lineage — each one answers a question the previous one leaves open:

1. **Transformer (1)** — the substrate. Everything else assumes it.
2. **BERT (2) → GPT-1 (3)** — the encoder/decoder fork. Know *why* decoder-only won for
   generation and where encoders still live (embeddings, rerankers).
3. **LoRA (4) → PEFT survey (5)** — adaptation without full fine-tuning. The survey is
   the map; LoRA is the one they'll ask you to explain.
4. **RAG (6)** — the alternative to adaptation: change the context, not the weights.
   The "fine-tune vs RAG" question is the most-asked of the set.
5. **VAE (8) → GAN (9) → Latent Diffusion (10)** — the generative-modelling lineage.
   Read as a progression: what each fixes about the last (blurry samples → unstable
   training → compute cost).
6. **ViT (7)** — the transformer generalizing past text; the bridge to multimodal.

## Pillar mapping

| Papers | Pillar |
|---|---|
| 1, 2, 3, 4, 5 | [2-llm-fundamentals](../guides/2-llm-fundamentals/00-overview.md) |
| 6 | [3-rag](../guides/3-rag/00-overview.md) |
| 7, 8, 9, 10 | [1-foundations](../guides/1-foundations/00-overview.md) (DL architectures) |

## Gaps this list has

Worth knowing that the article's canon is architecture-heavy and skips what an
*AI-engineering* (rather than ML-research) interview actually dwells on. Already covered
elsewhere in this repo:

- **Alignment/training** — InstructGPT, DPO, Constitutional AI
  (`generative-ai/01-llm-fundamentals/readings/`)
- **Reasoning/agents** — CoT (2201.11903), ReAct, Reflexion, Tree of Thoughts
  (same folder) — see [4-agents](../guides/4-agents/00-overview.md)
- **Eval** — RAGAS, ARES, TruthfulQA — see [6-evals-observability](../guides/6-evals-observability/00-overview.md)
- **Systems reality** — Hidden Technical Debt in ML (NIPS 2015), KDD metric pitfalls
