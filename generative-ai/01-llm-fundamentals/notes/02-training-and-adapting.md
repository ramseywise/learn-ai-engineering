---
origin: synthesis
sources:
  - https://arxiv.org/abs/2203.02155
  - https://arxiv.org/abs/2106.09685
  - https://arxiv.org/abs/2305.14314
  - https://arxiv.org/abs/2312.12148
  - "Raschka, Build a Large Language Model (From Scratch) (Manning, 2024), ch. 1, 5–7"
  - "Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 1, 5–8"
  - "Phoenix & Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 1–2"
  - "Huyen, AI Engineering (O'Reilly, 2025), ch. 1–2"
  - "Raieli & Iuculano, Building AI Agents with LLMs, RAG, and Knowledge Graphs (Packt, 2025), ch. 2–3"
  - https://github.com/rasbt/LLMs-from-scratch
  - https://arxiv.org/abs/2305.18290
  - https://arxiv.org/abs/2212.08073
  - https://arxiv.org/abs/2412.15115
  - https://arxiv.org/abs/2404.14219
  - https://arxiv.org/abs/2312.11805
  - https://arxiv.org/abs/2304.01373
  - https://arxiv.org/abs/2303.03378
  - https://arxiv.org/abs/2308.12966
  - https://arxiv.org/abs/2403.03507
  - https://arxiv.org/abs/2306.11695
  - https://arxiv.org/abs/2601.21571
  - https://arxiv.org/abs/2401.16380
  - https://arxiv.org/abs/2004.10964
  - https://arxiv.org/abs/2311.00176
  - https://arxiv.org/abs/2401.02415
  - https://arxiv.org/abs/2109.01652
  - https://arxiv.org/abs/2110.08207
  - https://arxiv.org/abs/2210.11416
  - https://arxiv.org/abs/2305.11206
  - https://arxiv.org/abs/2405.05904
  - https://arxiv.org/abs/2308.10792
  - https://arxiv.org/abs/2510.15103
  - https://arxiv.org/abs/2302.11529
  - https://arxiv.org/abs/2104.08691
  - https://arxiv.org/abs/2303.16199
  - https://arxiv.org/abs/2402.12354
  - https://arxiv.org/abs/2309.12307
  - https://arxiv.org/abs/2306.09782
  - https://arxiv.org/abs/2305.17333
  - https://arxiv.org/abs/2201.03514
  - https://arxiv.org/abs/2302.04870
  - https://arxiv.org/abs/2401.08565
  - https://arxiv.org/abs/2307.13269
  - https://arxiv.org/abs/2506.06105
  - https://arxiv.org/abs/2408.11796
  - https://arxiv.org/abs/1503.02531
  - https://arxiv.org/abs/2305.02301
  - https://arxiv.org/abs/2401.10491
  - https://doi.org/10.18653/v1/2021.acl-long.353
  - https://doi.org/10.18653/v1/2022.acl-short.1
  - https://arxiv.org/abs/2403.17887
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
| Pretraining | Web, books, code; trillions of tokens, unlabeled | Next-token cross-entropy | Knowledge, language, reasoning ability | This note; *LLMs from Scratch*, ch. 5 |
| Supervised fine-tuning (SFT) | Thousands to millions of (instruction, response) pairs | Same loss, on the response tokens | Format, instruction following, persona | This note; *LLMs from Scratch*, ch. 7; *LLM Engineer's Handbook*, ch. 5 |
| Preference optimization | Pairs of responses ranked by humans or a model | Reward model + PPO, or DPO directly | Which of several acceptable answers the model prefers | [05-RL](../../05-RL/README.md) |

The InstructGPT paper ([arXiv:2203.02155](https://arxiv.org/abs/2203.02155), Ouyang et al., 2022) is the reference recipe: demonstrations → SFT, comparisons → reward model, reward model → PPO. Its headline result: labelers preferred outputs of the 1.3B InstructGPT model to the 175B GPT-3. Alignment, not size, made the difference users noticed.

---

## Pretraining

Pretraining is self-supervised: the label for each position is the next token in the text. Raschka writes the loop by hand (*LLMs from Scratch*, ch. 5; full code at [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch)):

```python
for input_ids, target_ids in train_loader:          # targets = inputs shifted one to the left
    logits = model(input_ids)                        # (batch, seq, vocab)
    loss = F.cross_entropy(logits.flatten(0, 1), target_ids.flatten())
    optimizer.zero_grad(); loss.backward(); optimizer.step()
```

One forward pass scores every position at once: the causal mask lets the model predict token 2 from token 1, token 3 from tokens 1–2, and so on, all in parallel. Feeding the true previous tokens rather than the model's own guesses is called *teacher forcing* (*Building AI Agents*, ch. 2). It is why training is parallel while generation (note 01, decode) is not.

Things worth knowing about the loss:

- **At initialization** the loss should be about `ln(vocab_size)`, the loss of a uniform guess: ≈ 10.8 for a 50,257-token vocabulary. Raschka's untrained GPT-2 scores 10.7940 on his first batch, a perplexity of about 48,725, close to the vocabulary size (*LLMs from Scratch*, ch. 5). If it starts far higher, the initialization is broken.
- **Perplexity** = `exp(loss)`: the effective number of tokens the model is choosing between.
- **Overfitting looks like this.** Raschka trains the 124M model for 10 epochs on one short story (Edith Wharton's "The Verdict", 5,145 tokens, 90/10 train/validation split, context cut to 256). It takes about five minutes on a MacBook Air. Training loss falls from 9.78 to 0.39 while validation loss stalls near 6.4, and the model starts reciting passages of the story verbatim. Real pretraining makes roughly one pass over a far larger corpus, with batch sizes of 1,024 or more.

![Line chart of training and validation loss against epochs (0–10) and tokens seen (0–45,000): both fall from about 10 to 7 in the first epoch, then training loss keeps falling to about 0.4 while validation loss flattens around 6 and creeps up after epoch 7](../sources/images/build-a-large-language-model-from-scratch-fig5-12.png)
*Image Source: Raschka, *Build a Large Language Model (From Scratch)* (Manning, 2024), Fig. 5-12*

- **Save the optimizer state with the weights.** AdamW keeps two running statistics per parameter. Resume from weights alone and the first steps behave like a fresh optimizer (*LLMs from Scratch*, ch. 5).

Real pretraining runs add data curation (deduplication, quality filtering, mixing code and text), learning-rate warmup and cosine decay, gradient clipping and mixed precision. Raschka also loads the released GPT-2 weights into the hand-built model, which proves the architecture in [note 01](01-how-llms-work.md) matches the real one (*LLMs from Scratch*, ch. 5).

Not every curation step is a guaranteed win. Pythia trained eight model sizes, from 70M to 12B parameters, twice each: once on the Pile (300B tokens) and once on a near-deduplicated Pile of 207B tokens, run for about 1.5 epochs so that it also reached 300B. Both runs used the same data order and saved 154 checkpoints ([arXiv:2304.01373](https://arxiv.org/abs/2304.01373) (Biderman et al., 2023-04)). On eight standard benchmarks, deduplication showed "no clear benefit", and seeing the data a second time did no visible harm. The same suite showed that memorized 32-token sequences turn up at a steady rate through training, fitting a Poisson process. So putting sensitive data early or late in training does not change how much of it gets memorized. Each size was trained with one seed; the authors estimate that 25 seeds would have cost about $10 million. The 12B model alone took 72,300 A100-hours.

### What the data is

Most pretraining text starts as Common Crawl, a scrape of billions of web pages, usually filtered into something like Google's C4. Filtering is crude: GPT-2's WebText kept only pages linked from Reddit posts with at least three upvotes (*AI Engineering*, ch. 2). The mix decides what the model is good at. English is 45.88% of Common Crawl and Russian, second, about 6%, which shows up later as worse quality and higher token cost in other languages (note 01, Tokens). Newer reports filter with a model instead. Qwen2.5 used Qwen2-Instruct as the quality filter, downsampled e-commerce, social media and entertainment, upsampled science and technology, and grew the corpus from 7T to 18T tokens ([arXiv:2412.15115](https://arxiv.org/abs/2412.15115) (Qwen Team, 2024-12)). Phi-3 pushed filtering hardest, keeping heavily filtered web data plus synthetic text in what Microsoft calls a "data optimal regime" ([arXiv:2404.14219](https://arxiv.org/abs/2404.14219) (Abdin et al., 2024-04)). **phi-3-mini (3.8B, 3.3T tokens) scored 68.8% on MMLU 5-shot, close to Mixtral 8x7B's 70.5%, but 64.0 on TriviaQA against Mixtral's 82.2.** Filtering kept reasoning and gave up stored facts. Both results come from Microsoft's internal eval pipeline, and the data was not released. Filtering can also remove a capability on purpose. With medicine as a proxy forget domain, dropping or loss-masking only the medical *tokens* hit medicine as hard as dropping whole documents and cost less on neighbouring biology. **At 1.8B parameters, matching an unfiltered model's medical loss would take about 7000× the compute.** It held up 10× better than an unlearning baseline against adversarial fine-tuning, and the filtered models still learned to refuse medical questions ([arXiv:2601.21571](https://arxiv.org/abs/2601.21571) (Rathi & Radford, 2026-01, preprint)). The evidence is that single proxy domain, at up to 1.8B parameters.

Two limits are closing in, according to Huyen (*AI Engineering*, ch. 2). **Data:** models consume public text faster than people write it (Villalobos et al., 2022), and sites are shutting crawlers out; Longpre et al. (2024) found 45% of C4 restricted by terms of service or robots.txt after 2023–24. Training on model-generated text is one answer, but *Building AI Agents* (ch. 3) warns of *model collapse*: studies in which models trained on synthetic data lost performance or forgot skills they had learned. Rephrasing real pages is safer than generating new ones. WRAP had Mistral-7B rewrite C4 in Wikipedia and Q&A styles and trained on the rewrites mixed with the originals. A 1.3B model reached the same zero-shot accuracy about 3x faster, and Pile perplexity fell by about half. Training on the rewrites alone hurt perplexity on messy real text ([arXiv:2401.16380](https://arxiv.org/abs/2401.16380) (Maini et al., ACL 2024)). **Electricity:** data centres used an estimated 1–2% of world electricity at the time of writing, projected to reach 4–20% by 2030.

### What it costs

Count training compute in **FLOPs** (operations) and hardware speed in **FLOP/s** (operations per second); the two are easy to confuse (*AI Engineering*, ch. 2). GPT-3 175B took 3.14 × 10²³ FLOPs. Huyen's estimate for redoing it on 256 H100s at a peak of 60 TFLOP/s, with no failures, is about 236 days, and at 70% utilization and $2 per H100-hour, over $4 million. Two cautions. First, 60 TFLOP/s is roughly the H100's 32-bit rate; training runs in BF16 on tensor cores, whose dense peak is on the order of 1,000 TFLOP/s, so the real time and cost would be an order of magnitude lower. Second, the book's cost formula multiplies by 256 days, not the 236 in its own text. Read the example as a method, not a quote.

Raschka's estimate for an open model (*LLMs from Scratch*, ch. 5): Llama 2 7B took 184,320 A100 GPU-hours on 2 trillion tokens, about $690,000 at $30 an hour for an 8×A100 cloud server. He cites an estimate of about $4.6 million in cloud credits for GPT-3's pretraining (*LLMs from Scratch*, ch. 1).

### Scaling, in practice

Chinchilla (note 01, Scale) trained 400 models from 70M to over 16B parameters on 5B to 500B tokens and found the compute-optimal ratio is about 20 training tokens per parameter, scaled together: double the model, double the data (*AI Engineering*, ch. 2). Three qualifications from Huyen:

- **Compute-optimal is not deployment-optimal.** Llama was deliberately trained past the Chinchilla point: a smaller model on more tokens costs more to train but less to run. Sardana et al. (2023) rewrote the scaling law to include expected inference demand. Llama 3 8B's 15T tokens is close to 2,000 tokens per parameter. Qwen2.5 trained every size on the same 18T tokens, which is about 36,000 tokens per parameter at 0.5B ([arXiv:2412.15115](https://arxiv.org/abs/2412.15115) (Qwen Team, 2024-12)). The payoff is at deployment. Quantized to 4 bits, phi-3-mini takes about 1.8GB and runs at more than 12 tokens per second on an iPhone 14 ([arXiv:2404.14219](https://arxiv.org/abs/2404.14219) (Abdin et al., 2024-04)).
- **Returns diminish.** Going from a cross-entropy of about 3.4 to 2.8 nats takes ten times more data, yet users notice the difference.
- **Hyperparameters cannot be searched at full size.** Teams tune on small models and extrapolate. Microsoft and OpenAI's μTransfer moved hyperparameters found on a 40M model to a 6.7B one.

*Building AI Agents* (ch. 3) adds the emergent-abilities debate covered in note 01 and the Kaplan law; it adds nothing to either.

### Continued pretraining

To add knowledge, run more pretraining: the same next-token loss on raw, unlabeled domain text, before any SFT. Gururangan et al. named it *domain-adaptive pretraining* (DAPT) ([arXiv:2004.10964](https://arxiv.org/abs/2004.10964) (Gururangan et al., ACL 2020)). A second pretraining phase of RoBERTa on domain text raised macro-F1 on ACL-ARC citation intent from 63.0 to 75.4, and micro-F1 on ChemProt from 81.9 to 84.2. **The gain tracks how far the domain is from the original corpus.** On AG News, whose news domain RoBERTa had already seen, the gain was zero, and adapting to an *unrelated* domain made most tasks worse. *Task-adaptive* pretraining, on just the task's own unlabeled text, cost far less and beat DAPT on five of the eight tasks.

The recipe scales to LLMs at a small fraction of the original cost:

- **ChipNeMo** ([arXiv:2311.00176](https://arxiv.org/abs/2311.00176) (Liu et al., 2023-11, preprint)) continued LLaMA 2 on 24B tokens of NVIDIA's internal chip-design documents and code, then ran SFT. For the 7B model, DAPT took 2,620 A100-hours and SFT 90, against 184,320 for the original pretraining: under 1.5% extra. ChipNeMo-70B beat GPT-4 on two of three internal tasks (an engineering-assistant chatbot and EDA script generation). DAPT through LoRA adapters left a significant accuracy gap against full-parameter DAPT. The benchmarks are NVIDIA's own and unreleased.
- **LLaMA Pro** ([arXiv:2401.02415](https://arxiv.org/abs/2401.02415) (Wu et al., ACL 2024)) attacks forgetting by adding parameters. It copies 8 transformer blocks into LLaMA2-7B, zero-initializes their output projections so the model starts unchanged, and trains only the new blocks, on 80B tokens of code and math. Against the base model, HumanEval pass@1 rose from 13.1 to 28.7 and GSM8K from 14.5 to 17.9, while MMLU held (46.9 to 47.9). In its law-domain ablation, the 8-block expansion kept general scores (56.7 average) better than full fine-tuning (55.0) and learned the domain task better than LoRA (75.1 vs 65.3 on Unfair-ToS). LoRA preserved general ability but struggled to learn the new domain.

---

## Supervised fine-tuning

Huyen's vocabulary (*AI Engineering*, ch. 1) is worth adopting. **Pre-training** builds the base model and is by far the expensive part: for InstructGPT it took about 98% of the compute, post-training 2%. **Post-training** is everything the model developer does afterwards (SFT, preference tuning). **Fine-tuning** is the same machinery when an application developer does it to someone else's model. Changing a prompt is not training of any kind; no weight moves.

SFT continues training on curated examples of the behaviour you want. The examples are expensive because they are written, not scraped: OpenAI used about 13,000 (prompt, response) pairs for InstructGPT, which at $10 a pair would come to $130,000 before task design and quality control. A pair can take up to 30 minutes to write, and about 90% of InstructGPT's demonstration writers had a college degree (*AI Engineering*, ch. 2). *Building AI Agents* (ch. 3) puts typical SFT sets at 10,000 to 100,000 pairs. The idea is older than chat. *Instruction tuning* began with FLAN ([arXiv:2109.01652](https://arxiv.org/abs/2109.01652) (Wei et al., ICLR 2022)) and T0 ([arXiv:2110.08207](https://arxiv.org/abs/2110.08207) (Sanh et al., ICLR 2022)), which fine-tuned on dozens of existing NLP datasets rewritten as instructions. FLAN's 137B model then beat zero-shot GPT-3 175B on 20 of 25 held-out datasets. The lineage, and what each successor learned, is in [05-RL note 02](../../05-RL/notes/02-rlhf-pipeline.md#stage-1--supervised-fine-tuning-sft). Raschka builds two flavours (*LLMs from Scratch*, ch. 6–7):

| | Classification fine-tuning (ch. 6) | Instruction fine-tuning (ch. 7) |
|---|---|---|
| Change to the model | Replace the output head with a small one (e.g. 2 classes); usually train only the last block(s) and the head | None; keep the language-model head |
| Data | Labeled examples (spam / not spam) | Instruction–response pairs in a fixed template (Alpaca-style) |
| Loss | Cross-entropy on the last token's class logits | Next-token loss on the response; padding and usually the prompt tokens are masked out |
| Evaluation | Accuracy | Hard; Raschka scores responses with a larger LLM as judge |

*Building AI Agents* (ch. 2) shows the classification route on a small decoder, with a linear head on the last token's hidden state; it is the same pattern as *LLMs from Scratch* ch. 6.

The *LLM Engineer's Handbook* (ch. 5) adds the practical side: building an instruction dataset from your own documents, deduplication, using an LLM to generate and filter pairs, chat templates, and choosing between full fine-tuning, LoRA and QLoRA by GPU budget.

**Rule:** SFT teaches the *form* of an answer far more than new facts. Fine-tuning on a knowledge base to make a model "know" it tends to produce confident paraphrases with errors. For facts that change or need citations, use retrieval ([02-rag-retrieval](../../02-rag-retrieval/README.md)); for a large, stable body of domain text, use continued pretraining (above).

The evidence for the rule:

- **Little data, mostly format.** Flan-PaLM's instruction tuning used 1.4B tokens, 0.2% of its 780B pretraining tokens, and most of its gain came from the first 282 of 1,836 tasks. The authors' reading is that the model was learning to express knowledge it already had ([arXiv:2210.11416](https://arxiv.org/abs/2210.11416) (Chung et al., JMLR 2024)). LIMA's *Superficial Alignment Hypothesis* says the same from 1,000 examples ([arXiv:2305.11206](https://arxiv.org/abs/2305.11206) (Zhou et al., NeurIPS 2023)).
- **New facts make it hallucinate.** In a controlled study on PaLM 2-S closed-book QA, examples the model didn't already know were fit far more slowly than known ones. **As they were fit, test accuracy fell linearly**, so the model got worse at using what it knew. Early stopping, or relabelling unknown answers "I don't know", avoided most of the damage ([arXiv:2405.05904](https://arxiv.org/abs/2405.05904) (Gekhman et al., EMNLP 2024)).
- **Not much semantics is needed either.** The instruction-tuning survey ([arXiv:2308.10792](https://arxiv.org/abs/2308.10792) (Zhang et al., 2023-08, preprint)) collects the critique. In Kung and Peng (2023), models tuned on task definitions stripped of meaning, or on examples with *wrong* input–output pairs, scored close to models tuned on the real ones.

Fine-tuning can also erase what pretraining taught. The effect shrinks with scale and can be offset by replaying old data. When PaLM-E unfroze its LLM for multimodal training, its language-generation score dropped by 87.3% (relative) at 12B but by only 3.9% at 562B ([arXiv:2303.03378](https://arxiv.org/abs/2303.03378) (Driess et al., 2023-03)). Qwen-VL mixed pure-text samples into its multimodal training and held MMLU at 50.7, against 49.9 for the LLM it started from ([arXiv:2308.12966](https://arxiv.org/abs/2308.12966) (Bai et al., 2023-08)).

Replay works, but it gets more expensive as a model accumulates training stages. The alternative is to limit which weights move. Two examples are LLaMA Pro's frozen-base block expansion (Continued pretraining, above) and sparse memory finetuning ([arXiv:2510.15103](https://arxiv.org/abs/2510.15103) (Lin et al., 2025-10, preprint)). Sparse memory finetuning needs a model with a *memory layer*: a pool of 1M slots, of which each token reads only 32. On each step it updates only the slots that the new data uses much more than pretraining data did (a TF-IDF ranking). **Trained on a stream of TriviaQA facts to the same recall, a 1.3B model lost 89% of its NaturalQuestions F1 under full fine-tuning, 71% under LoRA and 11% under sparse memory finetuning.** The result covers fact learning only, at 1.3B, on a memory-layer architecture you would have to pretrain yourself.

---

## Preference optimization, briefly

SFT can only imitate. To make a model prefer the better of two acceptable answers, you train on comparisons:

- **RLHF:** train a reward model on human rankings, then optimize the policy against it with PPO and a KL penalty to the SFT model.
  - *The data is comparisons, because they are cheaper than writing.* For Llama 2, each comparison cost Meta about $3.50, against $25 for a written response, and LMSYS found a careful comparison takes three to five minutes. Agreement is limited: InstructGPT's labelers agreed with each other about 73% of the time (*AI Engineering*, ch. 2).
  - *The reward model turns rankings into a score.* For a prompt `x` with a preferred answer `y_w` and a rejected one `y_l`, InstructGPT minimizes `−log σ(r_θ(x, y_w) − r_θ(x, y_l))`: push the winner's score above the loser's. Three ranked answers give three such pairs.
  - *A reward model is useful on its own.* Stitch Fix and Grab skip the RL step: they sample several answers and serve the one their reward model scores highest (best-of-N, note 01).
- **DPO** ([arXiv:2305.18290](https://arxiv.org/abs/2305.18290)): skip the reward model; optimize directly on (prompt, chosen, rejected) triples. The reward model's optimal policy has a closed form, so RLHF reduces to a classification loss with no sampling during training. It beat PPO-based RLHF at controlling sentiment and matched or beat it on summarization and single-turn dialogue. Meta used RLHF for Llama 2 and switched to DPO for Llama 3 (*AI Engineering*, ch. 2). *LLM Engineer's Handbook* ch. 6 walks through it.
- **Constitutional AI / RLAIF** ([arXiv:2212.08073](https://arxiv.org/abs/2212.08073)): a model critiques and ranks outputs against written principles in place of human labelers.

All three are covered in [05-RL notes 02–04](../../05-RL/README.md#syllabus).

---

## Parameter-efficient fine-tuning

Full fine-tuning updates every weight and needs optimizer state for all of them, several times the model's memory. PEFT methods train a small number of new parameters and freeze the rest ([arXiv:2312.12148](https://arxiv.org/abs/2312.12148), Xu et al., 2023, survey them). *Building AI Agents* (ch. 3) walks through the older options. Pfeiffer et al.'s survey ([arXiv:2302.11529](https://arxiv.org/abs/2302.11529) (Pfeiffer et al., TMLR 2023)) sorts them by where the new parameters go: into the existing weights (BitFit, LoRA), into the input (prompt and prefix tuning), or as new layers (adapters). All of them reduce to "frozen output plus a learned correction". Their reading of the comparisons: prompt tuning loses from limited capacity, bias-only tuning has the smallest footprint but lower scores, and adapters score best but add parameters.

- **Adapters** ([arXiv:1902.00751](https://arxiv.org/abs/1902.00751) (Houlsby et al., ICML 2019)) insert small bottleneck layers inside each block: for BERT, project 1,024 dimensions down to 24 and back up, under 50K parameters per adapter. Training only these (3.6% of the parameters) came close to full fine-tuning on GLUE. Unlike merged LoRA, adapters add a little latency at inference.
- **Prefix tuning** ([doi:10.18653/v1/2021.acl-long.353](https://doi.org/10.18653/v1/2021.acl-long.353) (Li & Liang, ACL 2021)) learns key/value vectors prepended at every layer: 250K parameters (0.1%) on GPT-2 Medium. It matched full fine-tuning on table-to-text and beat it by 2.9 BLEU on average with 50–500 training examples, an edge that shrank as the data grew. On XSUM summarization it trailed, 35.05 vs 37.25 ROUGE-L at 0.1%. Optimising the prefix directly was unstable, so the authors had to reparametrise it through an MLP during training.
- **Prompt tuning** ([arXiv:2104.08691](https://arxiv.org/abs/2104.08691) (Lester et al., EMNLP 2021)) keeps only the input-layer soft tokens: 20,480 parameters per task for a 5-token prompt on T5-XXL. **It works only at scale.** On SuperGLUE it lags model tuning badly at T5-Small through Large, and matches even multi-task model tuning only at 11B. The smaller sizes also depended on first continuing T5's training with a plain language-modelling objective; the 11B model worked without it. Its upside is robustness: trained on SQuAD, it beat model tuning on most out-of-domain QA sets, by 12.5 F1 on TextbookQA.
- **BitFit** ([doi:10.18653/v1/2022.acl-short.1](https://doi.org/10.18653/v1/2022.acl-short.1) (Ben Zaken et al., ACL 2022)) trains only the bias terms, 0.08% of BERT-Large, and matched full fine-tuning on the GLUE dev average (84.2 vs 84.1). The win is small-data only. It fell behind on the largest task, QQP (85.4 vs 87.5), and on SQuAD the ordering flipped once more training data was available. LLaMA-family models have no bias terms in their linear layers, so it does not carry over to them as is.
- **LLaMA-Adapter** ([arXiv:2303.16199](https://arxiv.org/abs/2303.16199) (Zhang et al., ICLR 2024)) brought prefix-style prompts to instruction tuning. It inserts learned prompts into the top 30 layers of a frozen LLaMA-7B, with a gate initialised at zero so they start out with no effect: 1.2M parameters and one hour on 8 A100s, against Alpaca's three hours of full fine-tuning on the same 52K examples. The zero gate is the trick. With random initialisation, ScienceQA validation accuracy was 40.77%, near chance; with the zero gate it was 83.85%. Its quality claim against Alpaca rests on GPT-4 judging 80 Vicuna questions, which is thin evidence.

**Where they lose to LoRA.** Hu et al. ran the old methods side by side on GPT-3 175B. On WikiSQL, full fine-tuning scored 73.8, BitFit 71.3, input-layer prompt tuning 63.1, per-layer prefixes 70.1, adapters 71.9–73.2 and LoRA 73.4–74.0 (Table 4). Only LoRA matched or beat full fine-tuning on that task.

**LoRA** ([arXiv:2106.09685](https://arxiv.org/abs/2106.09685), Hu et al., 2021) is the default. For a frozen weight matrix `W` (d × k), learn a low-rank update:

```
W' = W + ΔW,   ΔW = B · A,   B: d × r,  A: r × k,  r ≪ min(d, k)
```

- Only `A` and `B` are trained. On GPT-3 175B the paper reports 10,000× fewer trainable parameters and 3× less GPU memory than full fine-tuning, with comparable quality.
- The update can be merged into `W` after training, so inference costs nothing extra; or kept separate so one base model serves many adapters.
- What LoRA is *not*: *Prompt Engineering for GenAI* (ch. 2) calls it "low-rank approximations" that make the network run on consumer hardware. LoRA is low-rank *adaptation*. It shrinks the number of *trainable* parameters during fine-tuning; it does not make the model smaller or faster at inference. Shrinking the model is quantization, pruning or distillation (below).
- **QLoRA** ([arXiv:2305.14314](https://arxiv.org/abs/2305.14314)) keeps the frozen base in 4-bit and trains LoRA adapters on top, which brings 65B-parameter fine-tuning onto a single 48 GB GPU. Three tricks make it fit: a 4-bit NormalFloat data type, quantizing the quantization constants themselves (about 3 GB saved at 65B), and paged optimizers that absorb memory spikes. Its Guanaco models reached 99.3% of ChatGPT's score on the Vicuna benchmark after 24 hours on one GPU. The authors themselves warn that those chatbot benchmarks are not trustworthy, so read the number as "close", not "equal".
- **GaLore** ([arXiv:2403.03507](https://arxiv.org/abs/2403.03507) (Zhao et al., 2024-03)) targets optimizer memory instead of the trainable-parameter count. It projects each gradient into a low-rank subspace, cutting optimizer-state memory by up to 65.5%. That is enough to pre-train LLaMA-7B on a 24 GB consumer GPU. Unlike LoRA it updates all the weights, so it also works for pre-training. Its 8-bit 7B run on C4 reached a validation perplexity of 14.65 after 150K steps, a single run.
- **LoRA+** ([arXiv:2402.12354](https://arxiv.org/abs/2402.12354) (Hayou et al., ICML 2024)) gives `B` a larger learning rate than `A`. The authors' width-scaling argument says a shared rate under-trains `B`. It is the same compute as LoRA, with 1–2% better scores and up to 2× faster convergence, mostly on hard tasks. On Llama-7B trained on a 100K flan-v2 subset, MMLU rose about 1.3 points; on MNLI, which Llama finds easy, equal rates were already near-optimal. The best ratio varies by model and task: about 2⁴ for RoBERTa, 2¹–2² for Llama.
- **LongLoRA** ([arXiv:2309.12307](https://arxiv.org/abs/2309.12307) (Chen et al., ICLR 2024)) found the case where plain LoRA fails: **extending the context window**. Taking Llama 2 7B to 32K tokens, LoRA reached a PG19 perplexity of 11.44 at rank 8, against 8.08 for full fine-tuning, and rank 256 did no better (11.98). Making the embedding and normalisation layers trainable as well (about 2% of the parameters) brought it to 8.12. With shifted sparse attention during training it took Llama 2 7B to 100K tokens, or 70B to 32K, on one 8× A100 machine.
- **LOMO** ([arXiv:2306.09782](https://arxiv.org/abs/2306.09782) (Lv et al., ACL 2024)) keeps *full* fine-tuning and removes the optimizer state instead. It uses plain SGD and applies each layer's update as soon as its gradient is computed, so the full gradient is never held in memory. For LLaMA-7B (batch 8, length 512, activation checkpointing) that is 14.6 GB against 102.2 GB for AdamW. It also trained a 65B model on 8× RTX 3090s. On six SuperGLUE tasks with 1,000 examples it beat LoRA by 2.8 points on average at 13B. That is a narrow test, and it is SGD, not Adam.
- **MeZO** ([arXiv:2305.17333](https://arxiv.org/abs/2305.17333) (Malladi et al., NeurIPS 2023)) drops backpropagation altogether. It estimates the gradient from two forward passes with a shared random perturbation, so training needs only inference memory. One A100 80GB can then fine-tune a 30B model, where backprop with Adam fits 2.7B. On OPT-13B with 1,000 examples it came within 1% of full fine-tuning on 7 of 11 tasks, using 12× less memory. The gaps elsewhere were large: 67.9 vs 83.9 on CB, 60.1 vs 71.1 on MultiRC. It needs many more steps (20K vs 625) and works only when the task is phrased as a prompt.

**Without the weights.** Three methods adapt a model whose weights you cannot touch, and each needs something closed APIs do not give.
- Black-box tuning ([arXiv:2201.03514](https://arxiv.org/abs/2201.03514) (Sun et al., ICML 2022)) searches a 500-dimensional random projection of a soft prompt with CMA-ES, using 8,000 API calls. On RoBERTa-Large with 16 examples per class it averaged 73.0 across seven tasks, against 63.5 for gradient prompt tuning and 78.9 for full model tuning. It needs an API that accepts prompt embeddings and returns logits.
- Offsite-tuning ([arXiv:2302.04870](https://arxiv.org/abs/2302.04870) (Xiao et al., 2023-02, preprint)) has the model owner send a few top and bottom layers plus a compressed "emulator" of the middle. The data owner tunes those layers and sends them back. On GPT-2 XL and OPT-1.3B the plugged-back model came within a few points of full fine-tuning on most tasks. Combined with LoRA it trained GPT-2 XL 6.5× faster in 5.6× less memory than full fine-tuning. The authors say they have not shown that the emulator and adapter don't leak the model or the data.
- Proxy-tuning ([arXiv:2401.08565](https://arxiv.org/abs/2401.08565) (Liu et al., COLM 2024)) works at decoding time. It adds the logit difference between a small tuned model and its untuned base to a large base model's logits. Llama-2-7B-Chat minus Llama-2-7B, applied to Llama-2-70B, closed 88% of the gap to Llama-2-70B-Chat across the paper's benchmarks, and it beat the chat model on open-ended TruthfulQA (85.1 vs 79.6% informative and true), though not on the multiple-choice version (59.2 vs 68.3). Reasoning did not transfer: GSM8K was 32.0 against 51.8 for the real chat model. It needs a shared vocabulary and full logits (top-5 for their GPT-3.5 case), and it ran about 1.5× slower at 70B.

**Adapters as reusable parts.** With one base model and many LoRAs, new adapters can be assembled from old ones without training.
- LoraHub ([arXiv:2307.13269](https://arxiv.org/abs/2307.13269) (Huang et al., COLM 2024)) picks weights for a mix of existing LoRAs, with gradient-free search on five examples. On Big-Bench Hard with FLAN-T5-Large it scored 34.7, below 5-shot in-context learning (37.3), LoRA (37.7) and full fine-tuning (42.1). It used a fifth of in-context learning's tokens per example.
- Text-to-LoRA ([arXiv:2506.06105](https://arxiv.org/abs/2506.06105) (Charakorn et al., ICML 2025)) trains a hypernetwork on 479 tasks to write a LoRA from a task description in one forward pass. On Mistral-7B its adapters for unseen tasks averaged 73.9 on eight benchmarks, against 71.9 for a multi-task LoRA and 75.8 for LoRAs trained on each task. Its descriptions were written by GPT-4o-mini, and the authors expect worse results from what users actually type.

```python
from peft import LoraConfig, get_peft_model
config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"], lora_dropout=0.05)
model = get_peft_model(base_model, config)   # model.print_trainable_parameters() -> well under 1%
```

### Making the model smaller

Three ways to cut memory and latency once a model is trained (*Building AI Agents*, ch. 2–3):

- **Quantization** stores weights in fewer bits. The basic affine scheme maps a float `x` to an integer `x_q = round(x / s) + z`, with a scale `s` and zero point `z` chosen per tensor, channel or block. Halving the bits halves the weight memory (note 01, Reading a model's size).
- **Pruning** removes weights or whole layers. Classic prune-and-retrain cycles are too expensive at LLM scale, and the book reports that many one-shot methods fail to remove more than about 10% of weights before the model collapses. SparseGPT reached 60% sparsity on the 175B-class models OPT-175B and BLOOM-176B without retraining (the book says "170-billion-parameter models"). Wanda also needs no retraining. It holds LLaMA-7B at 7.26 perplexity at 50% unstructured sparsity, against 5.68 dense, but perplexity reaches 84.5 at 70% ([arXiv:2306.11695](https://arxiv.org/abs/2306.11695) (Sun et al., 2023-06)). Unstructured sparsity also gives no speedup on its own; see [inference 08](../../../ai-engineering/07-inference-engineering/notes/08-adaptive-inference.md#quantization). Gromov et al. dropped blocks of the deeper layers from open models and "healed" each pruned model with a small QLoRA fine-tune. **Llama-2-70B kept its 5-shot MMLU score until roughly half its layers were gone**, and across the Llama-2, Qwen, Mistral and Phi-2 models the collapse to chance came between 20% and 55% pruned. Larger, deeper models tolerated more pruning. "Little loss" holds only for knowledge question-answering, though. Next-token loss on C4 rose steadily with every layer removed, and GSM8K and HellaSwag dropped from the first layer cut. The authors read this as shallow layers storing knowledge and deeper layers doing reasoning ([arXiv:2403.17887](https://arxiv.org/abs/2403.17887) (Gromov et al., ICLR 2025)). Structured pruning pays off once distillation does the retraining. NVIDIA's Minitron recipe width-pruned Mistral NeMo 12B to 8B and retrained it on a KL loss against the teacher's logits. That took 380B tokens, against 15T to train Llama 3.1 8B from scratch, and the result scored 69.5 on 5-shot MMLU against Llama 3.1 8B's 65.3 ([arXiv:2408.11796](https://arxiv.org/abs/2408.11796) (Sreenivas et al., 2024-08, preprint)). Two practical findings. When you don't have the teacher's pretraining data, fine-tune the teacher on your distillation corpus first (about 100B tokens; they call it "teacher correction"), or its guidance is off-distribution. And at 4B from Llama 3.1 8B, width pruning beat depth pruning on accuracy, while depth pruning gave the larger speedup (2.7× vs 1.8×).
- **Distillation** trains a small *student* to match a large *teacher*'s output distribution. The recipe is Hinton, Vinyals and Dean's ([arXiv:1503.02531](https://arxiv.org/abs/1503.02531) (Hinton et al., 2015, NIPS 2014 Deep Learning Workshop)). Raise the softmax temperature T so that the teacher's *soft targets* show how it ranks the wrong answers. Train the student on those at the same T, add a lower-weighted cross-entropy on the true labels at T = 1, and multiply the soft-target gradients by T² so the mix stays balanced when T changes. Matching logits is the high-temperature limit of this loss. **Soft targets carry far more information per example than labels.** On an 85M-parameter speech model trained on only 3% of the data, hard labels overfit at 44.5% test frame accuracy, while soft targets reached 57.0%, against 58.9% for the full-data baseline. A single distilled model also kept more than 80% of a 10-model ensemble's accuracy gain. DistilGPT-2 is a distilled GPT-2. In the LLM era the cheaper variant is to fine-tune a small model on a large model's generated outputs, which is distillation without access to the teacher's logits. Distilling the teacher's *rationales* as well as its answers cuts the data the student needs. A 770M T5 trained to output PaLM-540B's chain-of-thought rationales as a second task beat few-shot PaLM-540B on ANLI using 80% of the labeled data, which standard fine-tuning of the same T5 could not match with all of it ([arXiv:2305.02301](https://arxiv.org/abs/2305.02301) (Hsieh et al., ACL Findings 2023)). The rationale is a training-only task, so at inference the student emits just the label. The teacher also needn't be bigger, or single. FuseLLM continually trained Llama-2 7B on the token distributions of three 7B models with different architectures (Llama-2, MPT, OpenLLaMA) and gained 5.16% (relative) on BBH. Distilling from Llama-2 13B gained 2.97%, and plain continued training on the same corpus gained 1.86% ([arXiv:2401.10491](https://arxiv.org/abs/2401.10491) (Wan et al., ICLR 2024)). Gains this small are worth trying only if the models are already on hand. Google's on-device Gemini Nano models (1.8B and 3.25B) were distilled from larger Gemini models and shipped with 4-bit weights ([arXiv:2312.11805](https://arxiv.org/abs/2312.11805) (Gemini Team, 2023-12)).

Quantization for *serving* (int8/int4 weights, KV-cache compression) is an inference topic; see *LLM Engineer's Handbook* ch. 8 and [ai-engineering/07-inference-engineering](../../../ai-engineering/07-inference-engineering/README.md).

---

## Prompt, retrieve or fine-tune?

| Symptom | First fix | Fine-tune when |
|---|---|---|
| Wrong format or tone | Better instructions and examples ([note 03](03-prompting-fundamentals.md)) | The format is still unstable after good prompting, or the prompt is too long to pay for on every call |
| Missing or stale facts | Retrieval | Almost never; fine-tuning is a poor fact store |
| Task needs a skill the model lacks | Decompose the task; use a stronger model | You have thousands of good examples. Phoenix & Taylor's rule of thumb (*Prompt Engineering for GenAI*, ch. 1) is that fine-tuning starts to beat prompting somewhere in the low thousands of examples |
| Cost or latency | Smaller model plus a good prompt | Distil a large model's outputs into a small one |

The *LLM Engineer's Handbook*'s framing (ch. 1) is useful for whole systems: separate **feature**, **training** and **inference** pipelines (the FTI architecture), so data preparation, fine-tuning runs and serving can change independently. Its running example, the "LLM Twin", fine-tunes a model on one person's writing and serves it behind RAG.

---

**Next:** [03 — Prompting fundamentals](03-prompting-fundamentals.md) covers the cheapest of these levers, and the one to try first.
