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
| ★ | Raschka, [*Build a Large Language Model (From Scratch)*](https://www.manning.com/books/build-a-large-language-model-from-scratch) (Manning, 2024). Code at [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch). Notes cite it as `(*LLMs from Scratch*, ch. N)` | Ch. 1 LLMs · 2 text data · 3 attention · 4 GPT model · 5 pretraining · 6 classification fine-tuning · 7 instruction fine-tuning · App. A PyTorch · App. B references. Folded in as: ch. 1–4 → 01 (tokens, causal-attention snippet and Fig. 3-19, Pre-LN, weight tying, GPT-3 data); ch. 5 → 01 (sampling counts, top-k/temperature snippet), 02 (loss at init, overfitting run and Fig. 5-12, Llama 2 cost), 05 (GPT-2 sizes, `qkv_bias`, generate settings). App. B is a reading list, not folded in | ✓ [build-a-large-language-model-from-scratch/](sources/build-a-large-language-model-from-scratch/) | [01](notes/01-how-llms-work.md) (ch. 1–5) · [02](notes/02-training-and-adapting.md) (ch. 1, 5–7) · [05](notes/05-build-a-tiny-gpt.md) (ch. 2–5, App. A) |
| ★ | Phoenix & Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024). Notes cite it as `(*Prompt Engineering for GenAI*, ch. N)` | Ch. 1 five principles · 2 intro to LLMs · 3 standard practices · 4 LangChain · 10 building an app. Ch. 5 (vector DBs) → 02-rag, ch. 6 (agents) → 03. Ch. 2 → 01 (tokens) and 02 (its LoRA description, corrected); its model-landscape section is dated (GPT-4 dated to 2024, an unconfirmed 1.7T parameter count). Ch. 7 (diffusion) and 9 (Stable Diffusion) → [ai-engineering/08 note 06](../../ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video.md). Ch. 8 (Midjourney) not used | ✓ [prompt-engineering-for-generative-ai/](sources/prompt-engineering-for-generative-ai/) | [01](notes/01-how-llms-work.md) (ch. 2) · [02](notes/02-training-and-adapting.md) (ch. 1–2) · [03](notes/03-prompting-fundamentals.md) (ch. 1, 3, 10) · [04](notes/04-langchain-basics.md) (ch. 4) |
| ★ | Huyen, *AI Engineering* (O'Reilly, 2025). Notes cite it as `(*AI Engineering*, ch. N)` | Ch. 1 building applications with foundation models · 2 understanding foundation models. Folded in as: ch. 1 → 01 (why subwords, self-supervision, decode latency), 02 (pre-/post-/fine-tuning terms); ch. 2 → 01 (tokenization cost by language, weight composition and Fig. 2-6, Llama shapes, prefill/decode, MoE and alternative architectures, temperature and Fig. 2-16, top-k/top-p/min-p, test-time compute and Fig. 2-19, structured output, inconsistency and hallucination), 02 (data, compute cost, Chinchilla in practice, SFT and comparison-data costs, reward-model loss), 03 (self-consistency). Its GPT-3 compute example and top-k rationale are corrected in the notes. Ch. 1's use-case, planning and stack material belongs to ai-engineering; later chapters live in other pillars | ✓ [huyen-ai-engineering/](sources/huyen-ai-engineering/) | [01](notes/01-how-llms-work.md) (ch. 1–2) · [02](notes/02-training-and-adapting.md) (ch. 1–2) · [03](notes/03-prompting-fundamentals.md) (ch. 2) |
| | Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025). Notes cite it as `(*Building AI Agents*, ch. N)`. Less reliable than the others on fundamentals: several errors are corrected in the notes | Ch. 2 the transformer · 3 LLMs as an AI engine. Folded in as: ch. 2 → 01 (BERT, cross-attention, greedy decoding; three corrections), 02 (teacher forcing, classification head, distillation); ch. 3 → 01 (where parameters sit, context cost, MoE, size definitions; two corrections), 02 (model collapse, SFT data size, adapters, prompt/prefix tuning, quantization, pruning), 03 (self-consistency). Its multimodal and hallucination/ethics sections belong to ai-engineering/08 and 09 | ✓ [building-ai-agents-llms-rag-kgs/](sources/building-ai-agents-llms-rag-kgs/) | [01](notes/01-how-llms-work.md) (ch. 2–3) · [02](notes/02-training-and-adapting.md) (ch. 2–3) · [03](notes/03-prompting-fundamentals.md) (ch. 3) |
| | Oshin & Campos, *Learning LangChain* (O'Reilly, 2025) | Ch. 1 fundamentals · 8 patterns · 11 building with LLMs. Ch. 2–3 → 02-rag; ch. 4–7 → 03/04; ch. 9–10 → 06-observability | ✓ [learning-langchain/](sources/learning-langchain/) | [04](notes/04-langchain-basics.md) |
| | Iusztin & Labonne, [*LLM Engineer's Handbook*](https://www.packtpub.com/en-us/product/llm-engineers-handbook-9781836200079) (Packt, 2024) | Ch. 1 LLM Twin / FTI · 5 SFT · 6 preference alignment · 7 evaluation · 8 inference optimization. Ch. 3–4, 9 → 02-rag; ch. 10–12 → 06-observability / ai-engineering. Ch. 2 (tooling and installation: Poetry, ZenML, Docker, AWS setup) read, not folded: setup instructions for the book's own repo | ✓ [llm-engineers-handbook/](sources/llm-engineers-handbook/) | [02](notes/02-training-and-adapting.md) |
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

## AI Papers of the Week

From DAIR AI's weekly list, read in full and folded into the notes. Newest first. ★ marks a paper that changed a claim.

| | Paper | arXiv | PDF | Maps to |
|---|---|---|---|---|
| | Arriola et al., *Block Diffusion* (ICLR 2025) | [2503.09573](https://arxiv.org/abs/2503.09573) | ✓ [arriola-2025-block-diffusion.pdf](sources/arriola-2025-block-diffusion.pdf) | [01](notes/01-how-llms-work.md#reading-a-models-size) |
| | Geiping et al., *Scaling up Test-Time Compute with Latent Reasoning* (2025) | [2502.05171](https://arxiv.org/abs/2502.05171) | ✓ [geiping-2025-scaling-up-test-time-compute.pdf](sources/geiping-2025-scaling-up-test-time-compute.pdf) | [01](notes/01-how-llms-work.md#spending-more-compute-at-inference) |
| | Qwen Team, *Qwen2.5 Technical Report* (2024) | [2412.15115](https://arxiv.org/abs/2412.15115) | ✓ [qwen-2024-qwen2-5-technical-report.pdf](sources/qwen-2024-qwen2-5-technical-report.pdf) | [01](notes/01-how-llms-work.md#the-transformer-block-and-the-gpt-stack), [02](notes/02-training-and-adapting.md#what-the-data-is), [02](notes/02-training-and-adapting.md#scaling-in-practice) |
| | Polyak et al., *Movie Gen: A Cast of Media Foundation Models* (Meta, 2024) | [2410.13720](https://arxiv.org/abs/2410.13720) | ✓ [movie-gen-2024.pdf](sources/movie-gen-2024.pdf) | [mm 06](../../ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video.md#video) |
| | Zhou et al., *Transfusion* (2024) | [2408.11039](https://arxiv.org/abs/2408.11039) | ✓ [zhou-2024-transfusion.pdf](sources/zhou-2024-transfusion.pdf) | [mm 06](../../ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video.md#how-a-diffusion-model-makes-an-image) |
| | Dao & Gu, *Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality* (Mamba-2, ICML 2024) | [2405.21060](https://arxiv.org/abs/2405.21060) | ✓ [dao-2024-transformers-ssms.pdf](sources/dao-2024-transformers-ssms.pdf) | [01](notes/01-how-llms-work.md#reading-a-models-size) |
| | Beck et al., *xLSTM: Extended Long Short-Term Memory* (2024) | [2405.04517](https://arxiv.org/abs/2405.04517) | ✓ [beck-2024-xlstm.pdf](sources/beck-2024-xlstm.pdf) | [01](notes/01-how-llms-work.md#reading-a-models-size) |
| | Abdin et al., *Phi-3 Technical Report* (2024) | [2404.14219](https://arxiv.org/abs/2404.14219) | ✓ [abdin-2024-phi-3-technical-report.pdf](sources/abdin-2024-phi-3-technical-report.pdf) | [02](notes/02-training-and-adapting.md#what-the-data-is), [02](notes/02-training-and-adapting.md#scaling-in-practice) |
| | Gemma Team, *Gemma: Open Models Based on Gemini Research and Technology* (2024) | [2403.08295](https://arxiv.org/abs/2403.08295) | ✓ [gemma-2024.pdf](sources/gemma-2024.pdf) | [01](notes/01-how-llms-work.md#the-transformer-block-and-the-gpt-stack) |
| | Zhao et al., *GaLore: Memory-Efficient LLM Training by Gradient Low-Rank Projection* (ICML 2024) | [2403.03507](https://arxiv.org/abs/2403.03507) | ✓ [zhao-2024-galore.pdf](../../ai-engineering/07-inference-engineering/sources/zhao-2024-galore.pdf) | [02](notes/02-training-and-adapting.md#parameter-efficient-fine-tuning) |
| | Zhang et al., *MM-LLMs: Recent Advances in MultiModal Large Language Models* (2024) | [2401.13601](https://arxiv.org/abs/2401.13601) | ✓ [zhang-2024-mm-llms.pdf](sources/zhang-2024-mm-llms.pdf) | [mm references](../../ai-engineering/08-multimodal-engineering/references.md#ai-papers-of-the-week) (planned 01, 02) |
| ★ | Gemini Team, *Gemini: A Family of Highly Capable Multimodal Models* (2023) | [2312.11805](https://arxiv.org/abs/2312.11805) | ✓ [gemini-1-0-2023.pdf](sources/gemini-1-0-2023.pdf) | [01](notes/01-how-llms-work.md#spending-more-compute-at-inference), [02](notes/02-training-and-adapting.md#making-the-model-smaller) |
| | Bai et al., *Qwen Technical Report* (2023) | [2309.16609](https://arxiv.org/abs/2309.16609) | ✓ [bai-2023-qwen-technical-report.pdf](sources/bai-2023-qwen-technical-report.pdf) | [01](notes/01-how-llms-work.md#embeddings-and-position), [01](notes/01-how-llms-work.md#the-transformer-block-and-the-gpt-stack) |
| | Darcet et al., *Vision Transformers Need Registers* (ICLR 2024) | [2309.16588](https://arxiv.org/abs/2309.16588) | ✓ [darcet-2023-vision-transformers-need-registers.pdf](sources/darcet-2023-vision-transformers-need-registers.pdf) | [01](notes/01-how-llms-work.md#attention) |
| | Bai et al., *Qwen-VL: A Versatile Vision-Language Model* (2023) | [2308.12966](https://arxiv.org/abs/2308.12966) | ✓ [bai-2023-qwen-vl.pdf](../../ai-engineering/08-multimodal-engineering/sources/bai-2023-qwen-vl.pdf) | [02](notes/02-training-and-adapting.md#supervised-fine-tuning) |
| | Guo et al., *AnimateDiff: Animate Your Personalized Text-to-Image Diffusion Models without Specific Tuning* (ICLR 2024) | [2307.04725](https://arxiv.org/abs/2307.04725) | ✓ [guo-2023-animatediff.pdf](sources/guo-2023-animatediff.pdf) | [mm 06](../../ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video.md#video) |
| | Sun et al., *A Simple and Effective Pruning Approach for Large Language Models* (Wanda, ICLR 2024) | [2306.11695](https://arxiv.org/abs/2306.11695) | ✓ [sun-2023-simple-effective-pruning-approach-large.pdf](../../ai-engineering/07-inference-engineering/sources/sun-2023-simple-effective-pruning-approach-large.pdf) | [02](notes/02-training-and-adapting.md#making-the-model-smaller) |
| | Copet et al., *Simple and Controllable Music Generation* (MusicGen, NeurIPS 2023) | [2306.05284](https://arxiv.org/abs/2306.05284) | ✓ [copet-2023-simple-controllable-music-generation.pdf](sources/copet-2023-simple-controllable-music-generation.pdf) | [01](notes/01-how-llms-work.md#prefill-decode-and-the-kv-cache) |
| | Wang et al., *CodeT5+: Open Code Large Language Models for Code Understanding and Generation* (2023) | [2305.07922](https://arxiv.org/abs/2305.07922) | ✓ [wang-2023-codet5.pdf](sources/wang-2023-codet5.pdf) | [01](notes/01-how-llms-work.md#prefill-decode-and-the-kv-cache) |
| | Blattmann et al., *Align your Latents: High-Resolution Video Synthesis with Latent Diffusion Models* (Video LDM, CVPR 2023) | [2304.08818](https://arxiv.org/abs/2304.08818) | ✓ [blattmann-2023-align-your-latents.pdf](sources/blattmann-2023-align-your-latents.pdf) | [mm 06](../../ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video.md#video) |
| | Biderman et al., *Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling* (ICML 2023) | [2304.01373](https://arxiv.org/abs/2304.01373) | ✓ [biderman-2023-pythia.pdf](sources/biderman-2023-pythia.pdf) | [02](notes/02-training-and-adapting.md#pretraining) |
| | Kang et al., *Scaling up GANs for Text-to-Image Synthesis* (GigaGAN, CVPR 2023) | [2303.05511](https://arxiv.org/abs/2303.05511) | ✓ [kang-2023-scaling-up-gans-text-image.pdf](sources/kang-2023-scaling-up-gans-text-image.pdf) | [mm 06](../../ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video.md#how-a-diffusion-model-makes-an-image) |
| | Driess et al., *PaLM-E: An Embodied Multimodal Language Model* (2023) | [2303.03378](https://arxiv.org/abs/2303.03378) | ✓ [driess-2023-palm-e.pdf](../../ai-engineering/08-multimodal-engineering/sources/driess-2023-palm-e.pdf) | [02](notes/02-training-and-adapting.md#supervised-fine-tuning) |
| | Chang et al., *Muse: Text-To-Image Generation via Masked Generative Transformers* (Google, 2023) | [2301.00704](https://arxiv.org/abs/2301.00704) | ✓ [chang-2023-muse.pdf](sources/chang-2023-muse.pdf) | [01](notes/01-how-llms-work.md#prefill-decode-and-the-kv-cache), [mm 06](../../ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video.md#how-a-diffusion-model-makes-an-image) |

## Source quality

- Papers are primary. The O'Reilly, Manning and Packt chapters are purchased, secondary and partly dated (both LangChain books predate current LangChain APIs; the Prompt Engineering book's model landscape is 2023–24). Where a book disagrees with the paper it cites, the notes follow the paper and say so. Notes paraphrase them; nothing is copied.
- Numbers in the notes are given with their setup (model, benchmark) as reported in the cited paper. The O'Reilly 0.2 vs 0.6 thumbs-up comparison is a toy sample, flagged as such in [03](notes/03-prompting-fundamentals.md).
- Constitutional AI was stored twice here and twice in 05 (identical files); the single copy now lives in 05-RL/sources.
