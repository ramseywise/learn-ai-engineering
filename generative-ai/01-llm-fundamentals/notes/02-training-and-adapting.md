---
origin: synthesis
sources:
  - https://arxiv.org/abs/2203.02155
  - https://arxiv.org/abs/2106.09685
  - https://arxiv.org/abs/2305.14314
  - https://arxiv.org/abs/2312.12148
  - "Raschka, Build a Large Language Model (From Scratch) (Manning, 2024), ch. 5–7"
  - "Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 1, 5–8"
  - "Phoenix & Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 1–2"
confidence: high
cleaned: 2026-10-31
---

# 2 — Training and Adapting Models

> Pretraining buys knowledge, supervised fine-tuning buys format, preference optimization buys judgment, and LoRA makes the last two affordable. Know which stage a problem belongs to before you reach for fine-tuning.

---

## The pipeline

```
raw text ──pretrain──▶ base model ──SFT──▶ instruction model ──preference optimization──▶ assistant
 (trillions of tokens)   (continues text)   (follows the format)   (RLHF / DPO / RLAIF)    (helpful, harmless)
```

| Stage | Data | Objective | What it changes | Depth |
|---|---|---|---|---|
| Pretraining | Web, books, code; trillions of tokens, unlabeled | Next-token cross-entropy | Knowledge, language, reasoning ability | This note; Raschka ch. 5 |
| Supervised fine-tuning (SFT) | Thousands to millions of (instruction, response) pairs | Same loss, on the response tokens | Format, instruction following, persona | This note; Raschka ch. 7; Handbook ch. 5 |
| Preference optimization | Pairs of responses ranked by humans or a model | Reward model + PPO, or DPO directly | Which of several acceptable answers the model prefers | [05-RL](../../05-RL/README.md) |

The InstructGPT paper ([arXiv:2203.02155](https://arxiv.org/abs/2203.02155), Ouyang et al., 2022) is the reference recipe: demonstrations → SFT, comparisons → reward model, reward model → PPO. Its headline result: labelers preferred outputs of the 1.3B InstructGPT model to the 175B GPT-3. Alignment, not size, made the difference users noticed.

---

## Pretraining

Pretraining is self-supervised: the label for each position is the next token in the text. Raschka ch. 5 writes the loop by hand:

```python
for input_ids, target_ids in train_loader:          # targets = inputs shifted one to the left
    logits = model(input_ids)                        # (batch, seq, vocab)
    loss = F.cross_entropy(logits.flatten(0, 1), target_ids.flatten())
    optimizer.zero_grad(); loss.backward(); optimizer.step()
```

Things worth knowing about the loss:

- **At initialization** the loss should be about `ln(vocab_size)`, the loss of a uniform guess: ≈ 10.8 for a 50,257-token vocabulary. If it starts far higher, the initialization is broken.
- **Perplexity** = `exp(loss)`: the effective number of tokens the model is choosing between.
- Training loss dropping while validation loss rises is overfitting; on a small corpus it happens within a few epochs (Raschka trains on one short story to show it).

Real pretraining runs add data curation (deduplication, quality filtering, mixing code and text), learning-rate warmup and cosine decay, gradient clipping and mixed precision. Raschka ch. 5 also loads the released GPT-2 weights into the hand-built model, which proves the architecture in [note 01](01-how-llms-work.md) matches the real one.

---

## Supervised fine-tuning

SFT continues training on curated examples of the behaviour you want. Two flavours appear in Raschka:

| | Classification fine-tuning (ch. 6) | Instruction fine-tuning (ch. 7) |
|---|---|---|
| Change to the model | Replace the output head with a small one (e.g. 2 classes); usually train only the last block(s) and the head | None; keep the language-model head |
| Data | Labeled examples (spam / not spam) | Instruction–response pairs in a fixed template (Alpaca-style) |
| Loss | Cross-entropy on the last token's class logits | Next-token loss on the response; padding and usually the prompt tokens are masked out |
| Evaluation | Accuracy | Hard; Raschka scores responses with a larger LLM as judge |

The LLM Engineer's Handbook (ch. 5) adds the practical side: building an instruction dataset from your own documents, deduplication, using an LLM to generate and filter pairs, chat templates, and choosing between full fine-tuning, LoRA and QLoRA by GPU budget.

**Rule:** SFT teaches the *form* of an answer far more than new facts. Fine-tuning on a knowledge base to make a model "know" it tends to produce confident paraphrases with errors. For facts that change or need citations, use retrieval ([02-rag-retrieval](../../02-rag-retrieval/README.md)).

---

## Preference optimization, briefly

SFT can only imitate. To make a model prefer the better of two acceptable answers, you train on comparisons:

- **RLHF:** train a reward model on human rankings, then optimize the policy against it with PPO and a KL penalty to the SFT model.
- **DPO** ([arXiv:2305.18290](https://arxiv.org/abs/2305.18290)): skip the reward model; optimize directly on (prompt, chosen, rejected) triples. Handbook ch. 6 walks through it.
- **Constitutional AI / RLAIF** ([arXiv:2212.08073](https://arxiv.org/abs/2212.08073)): a model critiques and ranks outputs against written principles in place of human labelers.

All three are covered in [05-RL notes 02–04](../../05-RL/README.md#syllabus).

---

## Parameter-efficient fine-tuning

Full fine-tuning updates every weight and needs optimizer state for all of them, several times the model's memory. PEFT methods train a small number of new parameters and freeze the rest ([arXiv:2312.12148](https://arxiv.org/abs/2312.12148), Xu et al., 2023, survey them).

**LoRA** ([arXiv:2106.09685](https://arxiv.org/abs/2106.09685), Hu et al., 2021) is the default. For a frozen weight matrix `W` (d × k), learn a low-rank update:

```
W' = W + ΔW,   ΔW = B · A,   B: d × r,  A: r × k,  r ≪ min(d, k)
```

- Only `A` and `B` are trained. On GPT-3 175B the paper reports 10,000× fewer trainable parameters and 3× less GPU memory than full fine-tuning, with comparable quality.
- The update can be merged into `W` after training, so inference costs nothing extra; or kept separate so one base model serves many adapters.
- **QLoRA** ([arXiv:2305.14314](https://arxiv.org/abs/2305.14314)) keeps the frozen base in 4-bit and trains LoRA adapters on top, which brings 65B-parameter fine-tuning onto a single 48 GB GPU.

```python
from peft import LoraConfig, get_peft_model
config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"], lora_dropout=0.05)
model = get_peft_model(base_model, config)   # model.print_trainable_parameters() -> well under 1%
```

Quantization for *serving* (int8/int4 weights, KV-cache compression) is an inference topic; see Handbook ch. 8 and [ai-engineering/07-inference-engineering](../../../ai-engineering/07-inference-engineering/README.md).

---

## Prompt, retrieve or fine-tune?

| Symptom | First fix | Fine-tune when |
|---|---|---|
| Wrong format or tone | Better instructions and examples ([note 03](03-prompting-fundamentals.md)) | The format is still unstable after good prompting, or the prompt is too long to pay for on every call |
| Missing or stale facts | Retrieval | Almost never; fine-tuning is a poor fact store |
| Task needs a skill the model lacks | Decompose the task; use a stronger model | You have thousands of good examples. Phoenix & Taylor's rule of thumb (O'Reilly ch. 1) is that fine-tuning starts to beat prompting somewhere in the low thousands of examples |
| Cost or latency | Smaller model plus a good prompt | Distil a large model's outputs into a small one |

The Handbook's framing (ch. 1) is useful for whole systems: separate **feature**, **training** and **inference** pipelines (the FTI architecture), so data preparation, fine-tuning runs and serving can change independently. Its running example, the "LLM Twin", fine-tunes a model on one person's writing and serves it behind RAG.

---

**Next:** [03 — Prompting fundamentals](03-prompting-fundamentals.md) covers the cheapest of these levers, and the one to try first.
