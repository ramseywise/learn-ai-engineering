---
origin: curated
sources:
  - generative-ai/resources.md (01 section)
  - local PDFs in sources/
confidence: high
cleaned: 2026-10-31
---

# References — LLM Fundamentals

> Every source the notes cite, mapped to notes. **★** = read first. ✓ = local copy in [sources/](sources/). The book-chapter PDFs are purchased copies: keep them local, do not redistribute.

---

## Books

| | Book | Chapters | PDF | Maps to |
|---|---|---|---|---|
| ★ | Alammar & Grootendorst, [*Hands-On Large Language Models*](https://www.llm-book.com/) (O'Reilly, 2024) | Visual intro to tokens, embeddings, attention | — | 01 |
| ★ | Raschka, [*Build a Large Language Model (From Scratch)*](https://www.manning.com/books/build-a-large-language-model-from-scratch) (Manning, 2024) | Ch. 1 LLMs · 2 text data · 3 attention · 4 GPT model · 5 pretraining · 6 classification fine-tuning · 7 instruction fine-tuning · App. A PyTorch · App. B references | ✓ [build-a-large-language-model-from-scratch/](sources/build-a-large-language-model-from-scratch/) | [01](notes/01-how-llms-work.md) (ch. 1–4) · [02](notes/02-training-and-adapting.md) (ch. 5–7) · [05](notes/05-build-a-tiny-gpt.md) (ch. 2–5, App. A) |
| ★ | Phoenix & Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024) | Ch. 1 five principles · 2 intro to LLMs · 3 standard practices · 4 LangChain · 10 building an app. Ch. 5 (vector DBs) → 02-rag, ch. 6 (agents) → 03, ch. 7–9 (image generation) not used | ✓ [prompt-engineering-for-generative-ai/](sources/prompt-engineering-for-generative-ai/) | [01](notes/01-how-llms-work.md) (ch. 2) · [02](notes/02-training-and-adapting.md) (ch. 1) · [03](notes/03-prompting-fundamentals.md) (ch. 1, 3, 10) · [04](notes/04-langchain-basics.md) (ch. 4) |
| | Oshin & Campos, *Learning LangChain* (O'Reilly, 2025) | Ch. 1 fundamentals · 8 patterns · 11 building with LLMs. Ch. 2–3 → 02-rag; ch. 4–7 → 03/04; ch. 9–10 → 06-observability | ✓ [learning-langchain/](sources/learning-langchain/) | [04](notes/04-langchain-basics.md) |
| | Iusztin & Labonne, [*LLM Engineer's Handbook*](https://www.packtpub.com/en-us/product/llm-engineers-handbook-9781836200079) (Packt, 2024) | Ch. 1 LLM Twin / FTI · 5 SFT · 6 preference alignment · 7 evaluation · 8 inference optimization. Ch. 3–4, 9 → 02-rag; ch. 10–12 → 06-observability / ai-engineering | ✓ [llm-engineers-handbook/](sources/llm-engineers-handbook/) | [02](notes/02-training-and-adapting.md) |
| | Burkov, [*The 100-Page Language Models Book*](https://www.thelmbook.com/) | Compact end-to-end | — | 01 |
| | Prince, [*Understanding Deep Learning*](https://udlbook.github.io/udlbook/) · Bishop, [*Deep Learning: Foundations and Concepts*](https://www.bishopbook.com/) · Goodfellow et al., [*Deep Learning*](https://www.deeplearningbook.org/) | Deep-learning foundations | — | 01, 05 |
| | Jurafsky & Martin, [*Speech and Language Processing*](https://web.stanford.edu/~jurafsky/slp3/) (3rd ed. draft) | Tokenization, n-grams, transformers | — | 01 |
| | *Generative AI and LLMs for Dummies* (vendor e-book) | A gentle first pass before the papers | ✓ [generative-ai-and-llms-for-dummies.pdf](sources/generative-ai-and-llms-for-dummies.pdf) | — |

## Courses

| | Course | Maps to |
|---|---|---|
| ★ | Karpathy, [*Neural Networks: Zero to Hero*](https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ). Code in [data-science/practice/nn-zero-to-hero](../../data-science/practice/nn-zero-to-hero/README.md) | [05](notes/05-build-a-tiny-gpt.md) |
| | [Stanford CS336: Language Modeling from Scratch](https://cs336.stanford.edu/) | 01, 02, 05 |
| | [Hugging Face LLM Course](https://huggingface.co/learn/llm-course/chapter1/1) | 01, 02 |
| | [fast.ai Practical Deep Learning](https://course.fast.ai/) · [MIT 6.S191](https://introtodeeplearning.com/) · [Full Stack Deep Learning](https://fullstackdeeplearning.com/) | 01 |
| | [DeepLearning.AI Neural Networks and Deep Learning](https://www.coursera.org/learn/neural-networks-deep-learning) · [DeepLearning.AI short courses](https://learn.deeplearning.ai/) | 01, 04 |
| | [Google Generative AI learning path](https://www.cloudskillsboost.google/paths/118) | 01 |
| | [TensorFlow NLP Zero to Hero](https://youtube.com/playlist?list=PLQY2H8rRoyvzDbLUZkbudP-MFQZwNmU4S) | 01 |

## First-party docs

| Source | Maps to |
|---|---|
| Anthropic [Messages API](https://docs.anthropic.com/en/api/messages) and [TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript) | [06](notes/06-calling-models-from-code.md) |
| [LangChain concepts](https://python.langchain.com/docs/concepts/) | [04](notes/04-langchain-basics.md) |
| Hugging Face [PEFT](https://huggingface.co/docs/peft) | [02](notes/02-training-and-adapting.md) |

## Core papers

| | Paper | arXiv | PDF | Maps to |
|---|---|---|---|---|
| ★ | Vaswani et al., *Attention Is All You Need* (2017) | [1706.03762](https://arxiv.org/abs/1706.03762) | ✓ [vaswani-2017-attention-all-you-need.pdf](sources/vaswani-2017-attention-all-you-need.pdf) | 01 |
| | Devlin et al., *BERT* (2018) | [1810.04805](https://arxiv.org/abs/1810.04805) | ✓ [devlin-2018-bert.pdf](sources/devlin-2018-bert.pdf) | 01 |
| | Holtzman et al., *The Curious Case of Neural Text Degeneration* (nucleus sampling, 2019) | [1904.09751](https://arxiv.org/abs/1904.09751) | — | 01 |
| ★ | Kaplan et al., *Scaling Laws for Neural Language Models* (2020) | [2001.08361](https://arxiv.org/abs/2001.08361) | — | 01 |
| ★ | Brown et al., *Language Models are Few-Shot Learners* (GPT-3, 2020) | [2005.14165](https://arxiv.org/abs/2005.14165) | — | 01, 03 |
| | Su et al., *RoFormer* (rotary embeddings, 2021) | [2104.09864](https://arxiv.org/abs/2104.09864) | — | 01 |
| ★ | Hoffmann et al., *Training Compute-Optimal LLMs* (Chinchilla, 2022) | [2203.15556](https://arxiv.org/abs/2203.15556) | — | 01 |
| | Touvron et al., *LLaMA* (2023) | [2302.13971](https://arxiv.org/abs/2302.13971) | ✓ [touvron-2023-llama.pdf](sources/touvron-2023-llama.pdf) | 01 |
| | OpenAI, *GPT-4 Technical Report* (2023) | [2303.08774](https://arxiv.org/abs/2303.08774) | ✓ [openai-2023-gpt-4-technical-report.pdf](sources/openai-2023-gpt-4-technical-report.pdf) | 01; 05-RL/02 |
| ★ | Ouyang et al., *InstructGPT* (2022) | [2203.02155](https://arxiv.org/abs/2203.02155) | in [05-RL/sources](../05-RL/references.md#core-papers) | 02 |
| | Bai et al., *Constitutional AI* (2022) | [2212.08073](https://arxiv.org/abs/2212.08073) | in [05-RL/sources](../05-RL/references.md#core-papers) | 02 |
| | Rafailov et al., *DPO* (2023) | [2305.18290](https://arxiv.org/abs/2305.18290) | in [05-RL/sources](../05-RL/references.md#core-papers) | 02 |
| ★ | Hu et al., *LoRA* (2021) | [2106.09685](https://arxiv.org/abs/2106.09685) | ✓ [hu-2021-lora.pdf](sources/hu-2021-lora.pdf) | 02 |
| | Dettmers et al., *QLoRA* (2023) | [2305.14314](https://arxiv.org/abs/2305.14314) | — | 02 |
| | Xu et al., *Parameter-Efficient Fine-Tuning Methods for Pretrained LMs: A Critical Review* (2023) | [2312.12148](https://arxiv.org/abs/2312.12148) | ✓ [xu-2023-peft-review.pdf](sources/xu-2023-peft-review.pdf) | 02 |
| ★ | Wei et al., *Chain-of-Thought Prompting* (2022) | [2201.11903](https://arxiv.org/abs/2201.11903) | ✓ [wei-2022-chain-of-thought.pdf](sources/wei-2022-chain-of-thought.pdf) | 03 |
| | Kojima et al., *Large Language Models are Zero-Shot Reasoners* (2022) | [2205.11916](https://arxiv.org/abs/2205.11916) | ✓ [kojima-2022-zero-shot-reasoners.pdf](sources/kojima-2022-zero-shot-reasoners.pdf) | 03 |
| | Yao et al., *ReAct* (2022) | [2210.03629](https://arxiv.org/abs/2210.03629) | in [05-RL/sources](../05-RL/references.md#core-papers) | 03 |
| | Manakul et al., *SelfCheckGPT* (2023) | [2303.08896](https://arxiv.org/abs/2303.08896) | ✓ [manakul-2023-selfcheckgpt.pdf](sources/manakul-2023-selfcheckgpt.pdf) | 01 |
| | Bubeck et al., *Sparks of Artificial General Intelligence: Early experiments with GPT-4* (2023; read: abstract, §1, §8) | [2303.12712](https://arxiv.org/abs/2303.12712) | ✓ [bubeck-2023-sparks-artificial-general-intelligence.pdf](sources/bubeck-2023-sparks-artificial-general-intelligence.pdf) | 01 |
| | Zhao et al., *A Survey of Large Language Models* (2023, v16 2025; read: abstract, §2.1) | [2303.18223](https://arxiv.org/abs/2303.18223) | ✓ [zhao-2023-survey-large-language-models.pdf](sources/zhao-2023-survey-large-language-models.pdf) | 01 |

### Routed in, not yet integrated

Placed in [sources/](sources/) by the readings router (`scripts/papers/potw.py route`) on 2026-10-31 and queued in the ledger for `/papers` and `/chapter`. Not yet folded into the notes.

| Source | arXiv | PDF | Likely note |
|---|---|---|---|
| Huyen, *AI Engineering* (O'Reilly, 2025), ch. 1 Introduction to Building AI Applications with Foundation Models | — | [ch01](sources/huyen-ai-engineering/ch01-introduction-building-ai-applications-foundation-models.pdf) | 01, 02 |
| Huyen, *AI Engineering*, ch. 2 Understanding Foundation Models | — | [ch02](sources/huyen-ai-engineering/ch02-understanding-foundation-models.pdf) | 01, 02 |
| *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt), ch. 2 The Transformer | — | [ch02](sources/building-ai-agents-llms-rag-kgs/ch02-transformer-model-behind-modern-ai-revolution.pdf) | 01 |
| Same book, ch. 3 Exploring LLMs as a Powerful AI Engine | — | [ch03](sources/building-ai-agents-llms-rag-kgs/ch03-exploring-llms-as-powerful-ai-engine.pdf) | 01, 02 |
| Mikolov et al., *Efficient Estimation of Word Representations* (word2vec, 2013) | [1301.3781](https://arxiv.org/abs/1301.3781) | [mikolov-2013-…](sources/mikolov-2013-efficient-estimation-word-representations-vector.pdf) | 01 |
| Press et al., *Train Short, Test Long* (ALiBi, 2021) | [2108.12409](https://arxiv.org/abs/2108.12409) | [press-2021-…](sources/press-2021-train-short-test-long.pdf) | 01 |
| Goodfellow et al., *Generative Adversarial Networks* (2014) | [1406.2661](https://arxiv.org/abs/1406.2661) | [goodfellow-2014-…](sources/goodfellow-2014-generative-adversarial-networks.pdf) | — (generative models beyond text) |
| Kingma & Welling, *Auto-Encoding Variational Bayes* (2013) | [1312.6114](https://arxiv.org/abs/1312.6114) | [kingma-2013-…](sources/kingma-2013-auto-encoding-variational-bayes.pdf) | — |
| Dosovitskiy et al., *An Image is Worth 16x16 Words* (ViT, 2020) | [2010.11929](https://arxiv.org/abs/2010.11929) | [dosovitskiy-2020-…](sources/dosovitskiy-2020-image-worth-16x16-words.pdf) | — |
| Rombach et al., *High-Resolution Image Synthesis with Latent Diffusion Models* (2021) | [2112.10752](https://arxiv.org/abs/2112.10752) | [rombach-2021-…](sources/rombach-2021-high-resolution-image-synthesis-latent.pdf) | — |

### Held here, used elsewhere

These PDFs came in with the old `readings/` folder. They are not cited by the 01 notes; each has a better home, and the owning pillar can move it with `git mv`.

| Paper | arXiv | PDF | Better home |
|---|---|---|---|
| Park et al., *Generative Agents* (2023) | [2304.03442](https://arxiv.org/abs/2304.03442) | ✓ [park-2023-generative-agents.pdf](sources/park-2023-generative-agents.pdf) | 03-agentic-foundations (memory, reflection) |
| Patil et al., *Gorilla* (2023) | [2305.15334](https://arxiv.org/abs/2305.15334) | ✓ [patil-2023-gorilla.pdf](sources/patil-2023-gorilla.pdf) | 03-agentic-foundations / ai-engineering/03-harness (tool use) |
| Qin et al., *ToolLLM* (2023) | [2307.16789](https://arxiv.org/abs/2307.16789) | ✓ [qin-2023-toolllm.pdf](sources/qin-2023-toolllm.pdf) | 03-agentic-foundations (tool use) |
| Fang et al., *LLM Agents can Autonomously Hack Websites* (2024) | [2402.06664](https://arxiv.org/abs/2402.06664) | ✓ [fang-2024-llm-agents-hack-websites.pdf](sources/fang-2024-llm-agents-hack-websites.pdf) | ai-engineering/04-loop (guardrails) or 01-prompt-engineering/10 (adversarial) |
| Zhao et al., *Optimizing LLM-based RAG Pipelines in the Financial Domain* (NAACL Industry 2024) | — | ✓ [zhao-2024-optimizing-rag-financial-domain.pdf](sources/zhao-2024-optimizing-rag-financial-domain.pdf) | 02-rag-retrieval |
| Miller, *Explanation in AI: Insights from the Social Sciences* (2019) | [1706.07269](https://arxiv.org/abs/1706.07269) | ✓ [miller-2019-explanation-in-ai-social-sciences.pdf](sources/miller-2019-explanation-in-ai-social-sciences.pdf) | data-science (interpretability) |
| Bansal et al., *Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance* (2021) | [2006.14779](https://arxiv.org/abs/2006.14779) | ✓ [bansal-2021-ai-explanations-team-performance.pdf](sources/bansal-2021-ai-explanations-team-performance.pdf) | data-science (interpretability) |

## Source quality

- Papers are primary. The O'Reilly, Manning and Packt chapters are purchased, secondary and partly dated (both LangChain books predate current LangChain APIs; the Prompt Engineering book's model landscape is 2023–24). Notes paraphrase them; nothing is copied.
- Numbers in the notes are given with their setup (model, benchmark) as reported in the cited paper. The O'Reilly 0.2 vs 0.6 thumbs-up comparison is a toy sample, flagged as such in [03](notes/03-prompting-fundamentals.md).
- Constitutional AI was stored twice here and twice in 05 (identical files); the single copy now lives in 05-RL/sources.
