# 01 — LLM Fundamentals

> Depth layer. Summary: [interviewing/guides/2-llm-fundamentals](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/2-llm-fundamentals/00-overview.md)
> Position: first pillar of [generative-ai](../README.md). Everything else in generative-ai presumes it. Prompting technique depth lives in [ai-engineering/01-prompt-engineering](../../ai-engineering/01-prompt-engineering/README.md).

---

## What it is

What a large language model is, how it is trained and adapted, and how to instruct and call it from code. An LLM is a decoder-only transformer trained to predict the next token; pretraining gives it knowledge, supervised fine-tuning gives it the assistant format, and preference optimization gives it judgment. Prompting changes what it produces without touching the weights, and the API is a stateless request carrying the whole conversation.

Most of an LLM's surprising behaviour (hallucination, sensitivity to wording, in-context learning, trouble with counting characters) follows from next-token prediction over subword tokens. This pillar builds that mental model, then puts it to work: prompting principles, LangChain's building blocks, a tiny GPT written by hand and the four SDK patterns every application uses.

---

## Start here

1. [01 — How LLMs work](notes/01-how-llms-work.md): tokens, attention, the GPT stack, scale.
2. [03 — Prompting fundamentals](notes/03-prompting-fundamentals.md): the five principles.
3. [06 — Calling models from code](notes/06-calling-models-from-code.md), then run the [TypeScript lab](practice/01-typescript-sdk/).
4. When you have an evening: [05 — Build a tiny GPT](notes/05-build-a-tiny-gpt.md).

---

## Layout

```
01-llm-fundamentals/
├── README.md
├── references.md           every source, mapped to notes
├── notes/                  01–06, read in order
├── practice/
│   └── 01-typescript-sdk/  four runnable Anthropic SDK examples
└── sources/                local PDFs (purchased chapters + papers)
    ├── build-a-large-language-model-from-scratch/   Raschka, ch. 1–7 + appendices A–B
    ├── learning-langchain/                          Oshin & Campos, ch. 1–11
    ├── llm-engineers-handbook/                      Iusztin & Labonne, ch. 1–12
    └── prompt-engineering-for-generative-ai/        Phoenix & Taylor, ch. 1–10
```

---

## Syllabus

| # | Note | Covers |
|---|---|---|
| 01 | [How LLMs work](notes/01-how-llms-work.md) | Next-token prediction; BPE tokens; embeddings and positional encodings (learned, sinusoidal, RoPE); scaled dot-product, causal and multi-head attention; the transformer block and GPT stack; encoder vs decoder; scaling laws, GPT-3, Chinchilla, LLaMA, GPT-4; decoding (temperature, top-k, top-p); base vs assistant models |
| 02 | [Training and adapting models](notes/02-training-and-adapting.md) | Pretraining loop and loss sanity checks; SFT (classification and instruction); InstructGPT recipe; RLHF/DPO/RLAIF in brief; LoRA, QLoRA and PEFT; prompt vs retrieve vs fine-tune; the FTI architecture |
| 03 | [Prompting fundamentals](notes/03-prompting-fundamentals.md) | Why naive prompts fail; the five principles (direction, format, examples, evaluation, division of labor); chain-of-thought and zero-shot CoT; standard practices for lists, JSON/YAML, style unbundling, summarization, chunking, classification; links to technique depth |
| 04 | [LangChain basics](notes/04-langchain-basics.md) | Chat models and messages; prompt templates; `with_structured_output` and output parsers; the Runnable interface; LCEL vs `@chain`; sequential and document chains; where the rest of *Learning LangChain* lives |
| 05 | [Build a tiny GPT](notes/05-build-a-tiny-gpt.md) | Karpathy's Zero to Hero and Raschka mapped step by step; the nanoGPT config; bug-catching checks; what building it teaches |
| 06 | [Calling models from code](notes/06-calling-models-from-code.md) | Messages API request and response shape; single call, streaming, forced-tool structured output, the tool loop, conversation state; production habits |

---

## Rules of thumb

| Rule | Note |
|---|---|
| The model predicts plausible tokens, not true ones. Design for hallucination; do not hope it away | 01 |
| Tokens are the unit of cost, latency and context. 100 tokens ≈ 75 English words | 01 |
| Long context costs quadratic attention; do not fill the window because you can | 01 |
| Loss at step 0 should be about ln(vocab size). If not, the bug is in initialization or the target shift | 02, 05 |
| Fine-tuning teaches form, not facts. Facts that change or need citations belong in retrieval | 02 |
| LoRA first; full fine-tuning only with a reason | 02 |
| Give direction before adding examples; add 3–5 varied examples when format must be reliable | 03 |
| Never judge a prompt from one run. Run variants several times and rate blind | 03 |
| Split tasks so each step can be checked; ask for reasoning before the answer on multi-step problems | 03 |
| Use structured output (a forced tool or `with_structured_output`) when code consumes the answer, and still validate | 04, 06 |
| Check `stop_reason` before trusting an output; truncation passes silently in prose | 06 |
| Cap tool-loop iterations and log `usage` on every call | 06 |

---

## Resource map

**Related notes**

- [ai-engineering/01-prompt-engineering](../../ai-engineering/01-prompt-engineering/README.md): technique depth (anatomy, output control, tools, reasoning models, optimization, adversarial prompting).
- [ai-engineering/02-context-engineering](../../ai-engineering/02-context-engineering/README.md): what goes in the window once history and documents grow.
- [ai-engineering/07-inference-engineering](../../ai-engineering/07-inference-engineering/README.md): KV cache, quantization, serving.
- [05-RL](../05-RL/README.md): the post-training stage of note 02 in depth (RLHF, DPO, Constitutional AI).
- [04-agentic-frameworks](../04-agentic-frameworks/README.md): LangGraph, the step after note 04.

**Books and courses:** Raschka (★), Phoenix & Taylor (★), Alammar & Grootendorst (★), *Learning LangChain*, *LLM Engineer's Handbook*, Karpathy Zero to Hero (★), CS336. Chapter → note mapping in [references.md](references.md).

**Practice**

| Lab | What it shows | Run |
|---|---|---|
| [01-typescript-sdk](practice/01-typescript-sdk/) | One request, streaming, structured output via a forced tool, the tool loop, multi-turn history | needs Node, `npm install @anthropic-ai/sdk tsx typescript` and `ANTHROPIC_API_KEY`; makes paid API calls. `npx tsx 01-api-call.ts` |
| [data-science/practice/nn-zero-to-hero](../../data-science/practice/nn-zero-to-hero/README.md) | micrograd → makemore → nanoGPT | notebooks; nanoGPT's full config wants a GPU, shrink it for CPU |

**Readings:** local PDFs in [sources/](sources/), indexed with arXiv ids in [references.md](references.md#core-papers). Papers held here but owned by other pillars are listed under [Held here, used elsewhere](references.md#held-here-used-elsewhere).

**Interviewing guide:** [2-llm-fundamentals](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/2-llm-fundamentals/00-overview.md): attention, RLHF, prompting and model behaviour compressed for interview prep.

**Next:** [02-rag-retrieval](../02-rag-retrieval/README.md): RAG was the first killer app built on LLMs, and it presumes you can prompt a model reliably.
