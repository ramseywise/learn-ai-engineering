# 01 — LLM Fundamentals

> Interview recall: the checklists in these notes. Role map: [interviewing](../../practice/interviewing/README.md).
> Position: first pillar of [generative-ai](../README.md). Everything else in generative-ai presumes it. Prompting technique depth lives in [ai-engineering/01-prompt-engineering](../../ai-engineering/01-prompt-engineering/README.md).

---

## What it is

What a large language model is, how it is trained and adapted, and how to instruct, call and run it. An LLM is a decoder-only transformer trained to predict the next token. Pretraining gives it knowledge, supervised fine-tuning gives it the assistant format, and preference optimization gives it judgment. Prompts, the API and local runtimes are how you put that to work.

## Why it matters

Most of an LLM's surprising behaviour (hallucination, sensitivity to wording, in-context learning, trouble with counting characters) follows from next-token prediction over subword tokens. Once you have that model of it, you can tell which lever a problem calls for: a prompt, retrieval, a fine-tune or a different model. Every other pillar in generative-ai presumes this.

## The story

A team wants a support-ticket assistant. It starts with one word: what does the model see when a customer types "refund"? That leads to tokens and embeddings, then to attention, which lets a token weigh its context, and then to why size, context length and sampling behave as they do. Then the model gives a confident, wrong refund policy, and the team learns why a base model isn't an assistant. So they follow the weights through training: pretraining for knowledge, instruction tuning for format, preference optimization for judgment, and LoRA for the budget. With that, they stop reaching for fine-tuning first. They fix the prompt and measure it, wrap it in a chain, write a tiny GPT to find out what a real bug looks like, and call a hosted model with a capped loop. When legal asks whether tickets may leave the network, they know how to weigh a local model. The assistant still doesn't know this company's refund policy, and that is the next pillar's job.

---

## Reading order

Read in order on a first pass. Each chapter ends with pitfalls, exercises and an interview checklist. If you already use LLMs and want to skip ahead, take 01, 05, 09, 10 and 13.

**How a model works**

| # | Chapter | Covers |
|---|---|---|
| 01 | [Tokens and embeddings](notes/01-tokens-and-embeddings.md) | Next-token prediction, BPE tokens and cost, embeddings, positional encodings (learned, sinusoidal, RoPE) |
| 02 | [Attention and the transformer block](notes/02-attention-and-the-transformer-block.md) | Scaled dot-product, causal and multi-head attention, the block and GPT stack |
| 03 | [Architectures, scale and the model zoo](notes/03-scale-and-the-model-zoo.md) | Encoder and decoder, reading a model's size, scaling laws, mixture of experts, alternatives to transformers |
| 04 | [Decoding and inference behaviour](notes/04-decoding-and-inference-behaviour.md) | Prefill and decode, KV cache, temperature, top-k and top-p, test-time compute, structured output |
| 05 | [Hallucination and base vs assistant](notes/05-hallucination-and-base-vs-assistant.md) | Why models confabulate, what a base model is not, detection and mitigation |

**How it is trained and adapted**

| # | Chapter | Covers |
|---|---|---|
| 06 | [Pretraining: data and objectives](notes/06-pretraining-data-and-objectives.md) | The training pipeline, loop and loss checks, overfitting, curation and data |
| 15 | [The pretraining run: batch, cost and scale](notes/15-pretraining-runs-cost-and-scale.md) | Batch size and newer optimizers, cost and carbon, Chinchilla in practice, pricing a run |
| 07 | [SFT and instruction tuning](notes/07-sft-and-instruction-tuning.md) | Classification and instruction fine-tuning, chat templates, continued pretraining |
| 08 | [Preference optimisation: an overview](notes/08-preference-optimisation-overview.md) | Reward models and PPO, DPO, distillation |
| 09 | [PEFT and fine-tuning in practice](notes/09-peft-and-fine-tuning-in-practice.md) | LoRA, QLoRA, adapters, quantization, prompt or retrieve or fine-tune |

**How you use it**

| # | Chapter | Covers |
|---|---|---|
| 10 | [Prompting fundamentals](notes/10-prompting-fundamentals.md) | Why naive prompts fail, the five principles, chain of thought, standard practices, evaluating variants |
| 11 | [LangChain basics](notes/11-langchain-basics.md) | Chat models, templates, parsers, Runnables, LCEL and `@chain`, document chains |
| 12 | [Build a tiny GPT](notes/12-build-a-tiny-gpt.md) | Karpathy and Raschka mapped step by step, a GPT that trains on a CPU, the checks that catch most bugs |
| 13 | [Calling models from code](notes/13-calling-models-from-code.md) | Request and response shape, streaming, structured output, the tool loop, conversation state, production habits |

**How you run it yourself**

| # | Chapter | Covers |
|---|---|---|
| 14 | [Open-weight models and local inference](notes/14-open-weight-models-and-local-inference.md) | Licences, choosing a model, model cards, memory, GGUF, transformers, Ollama and llama.cpp, when local beats the API |

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [DS 03/01 Text representation](../../data-science/03-nlp/notes/01-text-representation.md) | Optional background: the word counts that came before embeddings |
| [DS 03/04 Embeddings and similarity](../../data-science/03-nlp/notes/04-embeddings-and-similarity.md) | Optional background: word2vec and similarity |
| [DS 02/01 Neural networks fundamentals](../../data-science/02-deep-learning/notes/01-neural-networks-fundamentals.md) | Optional background: backprop, which [GA 09/01](../09-llms-from-scratch/notes/01-micrograd.md) also builds from scratch |
| [DS 02/02 Optimisation and regularisation](../../data-science/02-deep-learning/notes/02-optimisation-and-regularisation.md) | Optional background: AdamW and the learning-rate sweep, which [pretraining](notes/06-pretraining-data-and-objectives.md) uses |
| [DS 02/05 Sequence models](../../data-science/02-deep-learning/notes/05-sequence-models.md) | Optional background: the recurrent networks attention grew out of |

**Feeds into**

| Chapter | Why |
|---|---|
| [AIE 01 Prompt engineering](../../ai-engineering/01-prompt-engineering/README.md) | Prompting starts from how the model reads tokens |
| [AIE 07 Inference engineering](../../ai-engineering/07-inference-engineering/README.md) | Serving what this pillar explains |
| [AIE 08 Multimodal engineering](../../ai-engineering/08-multimodal-engineering/README.md) | Extends the model beyond text |

---

## Rules of thumb

| Rule | Chapter |
|---|---|
| The model predicts plausible tokens, not true ones. Design for hallucination; do not hope it away | 05 |
| Tokens are the unit of cost, latency and context. 100 tokens ≈ 75 English words | 01 |
| Long context costs quadratic attention; do not fill the window because you can | 02, 03 |
| Loss at step 0 should be about ln(vocab size). If not, the bug is in initialization or the target shift | 06, 12 |
| Fine-tuning teaches form, not facts. Facts that change or need citations belong in retrieval | 09 |
| LoRA first; full fine-tuning only with a reason | 09 |
| Give direction before adding examples; add 3–5 varied examples when format must be reliable | 10 |
| Never judge a prompt from one run. Run variants several times and rate blind | 10 |
| Split tasks so each step can be checked; ask for reasoning before the answer on multi-step problems | 10 |
| Use structured output when code consumes the answer, and still validate | 11, 13 |
| Check `stop_reason` before trusting an output; truncation passes silently in prose | 13 |
| Cap tool-loop iterations and log `usage` on every call | 13 |
| Read the licence of the exact repo and its `base_model`. "Open" is not a licence | 14 |
| Decide local vs API on data rules and volume, with your own numbers | 14 |

---

## Deck and practice

**Deck:** [slides/llm-fundamentals.pptx](slides/llm-fundamentals.pptx), built from [slides/deck.yaml](slides/deck.yaml). Rebuild it with `make slides PILLAR=generative-ai/01-llm-fundamentals`.

| Lab | What it shows | Run |
|---|---|---|
| Code in every chapter | Each Python block runs as written. `# illustrative` marks the few that need a key, a GPU or a local server | Copy a block to a file, then `uv run --with torch --with transformers python file.py`. Chapter 14's Hub blocks need network access |
| [01-typescript-sdk](practice/01-typescript-sdk/) | The bridge for TypeScript readers: one request, streaming, structured output via a strict tool, the tool loop, multi-turn history | Needs Node, `npm install @anthropic-ai/sdk tsx typescript` and `ANTHROPIC_API_KEY`; makes paid API calls. `npx tsx 01-api-call.ts` |
| [data-science/practice/nn-zero-to-hero](../09-llms-from-scratch/practice/nn-zero-to-hero/README.md) | micrograd → makemore → nanoGPT | Notebooks; nanoGPT's full config wants a GPU, shrink it for CPU |

---

## Layout

```text
01-llm-fundamentals/
├── README.md
├── references.md           every source, mapped to chapters
├── notes/                  01–14, read in order
├── slides/                 deck.yaml and the built deck
├── practice/
│   └── 01-typescript-sdk/  four Anthropic SDK examples
└── sources/                local PDFs (purchased chapters and papers)
    ├── build-a-large-language-model-from-scratch/   Raschka, ch. 1–7 + appendices A–B
    ├── building-ai-agents-llms-rag-kgs/             Raieli & Iuculano, ch. 2–3
    ├── huyen-ai-engineering/                        Huyen, ch. 1–2
    ├── learning-langchain/                          Oshin & Campos, ch. 1–11
    ├── llm-engineers-handbook/                      Iusztin & Labonne, ch. 1–12
    ├── prompt-engineering-for-generative-ai/        Phoenix & Taylor, ch. 1–10
    └── images/                                      figures used in the notes
```

---

## Primary texts

- Alammar and Grootendorst, *Hands-On Large Language Models*
- Raschka, *Build a Large Language Model (From Scratch)*
- Huyen, *AI Engineering*
- Vaswani et al., *Attention Is All You Need*

Everything else: [references.md](references.md).

## Resource map

- [ai-engineering/01-prompt-engineering](../../ai-engineering/01-prompt-engineering/README.md): technique depth (anatomy, output control, tools, reasoning models, optimization, adversarial prompting).
- [ai-engineering/02-context-engineering](../../ai-engineering/02-context-engineering/README.md): what goes in the window once history and documents grow.
- [ai-engineering/07-inference-engineering](../../ai-engineering/07-inference-engineering/README.md): KV cache, quantization, serving.
- [05-RL](../05-RL/README.md): the post-training stages of chapters 07–08 in depth (RLHF, DPO, Constitutional AI).
- [04-agentic-frameworks](../04-agentic-frameworks/README.md): LangGraph, the step after chapter 11.

**Readings:** every book, course and paper in [references.md](references.md), with local PDFs in [sources/](sources/). Papers held here but owned by other pillars are listed under [Held here, used elsewhere](references.md#held-here-used-elsewhere).

**Interviewing:** [role map](../../practice/interviewing/README.md) to these checklists, and the rounds.

**Next:** [02-rag-retrieval](../02-rag-retrieval/README.md): RAG was the first killer app built on LLMs, and it presumes you can prompt a model reliably.
