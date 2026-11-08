---
origin: synthesis  # was: Deeplearning.ai-RAG-main
sources:
  - https://arxiv.org/abs/2310.05736
  - https://www.deeplearning.ai/courses/retrieval-augmented-generation-rag/
  - https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG (Module 4, "LLMs and Text Generation" + labs 4.1 sampling, 4.2 prompt engineering, Assignment 4 "Fashion Forward Hub")
  - https://arxiv.org/abs/2401.14887
  - Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 5, ch. 6
  - https://arxiv.org/abs/2311.09210
  - https://arxiv.org/abs/2410.05983
  - https://arxiv.org/abs/2301.00303
  - https://arxiv.org/abs/2007.01282
  - https://arxiv.org/abs/1907.09190
  - https://doi.org/10.18653/v1/2020.emnlp-main.272
  - https://arxiv.org/abs/2509.01092
  - https://arxiv.org/abs/2511.18659
  - https://arxiv.org/abs/2506.11555
  - https://arxiv.org/abs/2408.13533
  - https://arxiv.org/abs/2406.12824
  - https://arxiv.org/abs/2407.09252
confidence: high
cleaned: 2026-11-01
---
# 6 — Generation for RAG

Tallybook's retriever now returns the refund page, and the bot still tells a customer they have 45 days. The document says 30. Nothing in the retrieval metrics moved, because retrieval worked, and the mistake happened in the last step: a model given the right text can ignore it, blend it with what it remembers, or cite a page it never used. This chapter is about that last step, the settings and prompts that keep an answer tied to its evidence and the checks that catch it when it comes loose.

> The LLM half of RAG, part one: how a decoder-only transformer turns the augmented prompt into tokens, which sampling knobs control that, how to choose a model, and how to write and size prompts that keep answers grounded and cited. Hallucinations, citation checks, RAGAS, agentic workflows and RAG against fine-tuning are in [06b](06b-hallucinations-evaluation-and-fine-tuning.md).

---

## Why RAG works: attention

An LLM is a decoder-only transformer. For each new token it runs the whole context through 8–64 layers, each with many attention heads (8 to 100+) and a feed-forward block, then samples one token and repeats until an end-of-sequence token.

| Part | What it contributes |
|---|---|
| Token + **position** vectors | What each token is and where it sits |
| **Attention** heads | Each token looks at every other token and pulls in what is relevant |
| Feed-forward layers | Per-token processing of what attention gathered |
| Token loop | One token at a time, conditioned on all before |

RAG works because attention lets every generated token look at the retrieved documents. Three consequences:

- The model **may still ignore the context** if its weights pull harder. Prompting (below) and evaluation ([RAGAS, in 06b](06b-hallucinations-evaluation-and-fine-tuning.md#evaluating-the-generator-ragas)) are how you catch that.
- **What else is in the context matters.** On NQ-open with small open models (Llama2-7B, Falcon-7B, MPT-7B and Phi-2 at 2.7B, all 4-bit), retrieved passages that score high but lack the answer pulled accuracy down more than unrelated passages did. Adding a single such distractor to the gold passage cost up to 25%, and picking distractors with a retriever trained on hard negatives made it worse, not better. Adding *random* documents sometimes raised accuracy: +35% relative for Llama2-7B with four retrieved passages (about 0.19 → 0.25). Placing the gold passage next to the question also helped ([arXiv:2401.14887](https://arxiv.org/abs/2401.14887), Cuconasu et al., 2024-01). For the random-document effect the authors offer only a tentative lead (attention entropy rose about 3× with noise added) and say they can't explain it yet, so don't pad prompts with noise. The two findings to use: near-miss distractors are the real threat, and the best evidence goes closest to the question.
  Wu et al. report a second, partial instance of the effect ([arXiv:2408.13533](https://arxiv.org/abs/2408.13533), Wu et al., 2024-08, preprint). Their setup: zero-shot four-option multiple choice, five documents with the gold one in the middle, up to 500 items from each of seven QA datasets (RGB 300, Bamboogle 125, TempQA 186), one run per cell. Adding *synthetic* noise to the gold passage beat gold alone on the weighted average: random-vocabulary "illegal sentences" lifted Llama3-8B-Instruct from 86.57 to 89.89 and Qwen2-7B-Instruct from 86.46 to 88.11. On RGB (eight models) the ISN gain held at about +7 to +9 points as the orthographic-noise ratio rose from 0 to 0.8, while absolute accuracy fell. Counterfactual passages cost 41 (Llama3-8B) to 52 points (Qwen2-7B). Many single cells fell below gold-only, and the paper does not discuss them. Its explanation (clearer reasoning, firmer trust in the gold passage) rests on a manual check of 100 samples per dataset, with no controlled test. **This conflicts with Leto et al.**, who found real nearest-neighbour passages never beat gold-only (see [11](11-retrieval-improvements.md): ASQA, two 7B readers, one run). The setups differ: Wu's noise is synthetic and multiple-choice, Leto's is retrieved and free-form. Read it as "noise can sometimes steady a reader", not a reason to pad prompts.
- **Inside the model, context displaces memory.** With a context-only prompt ("not prior knowledge") on 50 factual prompts, causal tracing in Llama-2 7B showed MLP use at the subject token drop about 5x (indirect effect 0.2 to 0.0375), and blocking attention from the query subject changed the answer probability under 5%, against 95% (Llama-2; about 60% for Phi-2) without context. The attribute token inside the context mattered more (20% for Llama-2, 25% for Phi-2). This is a synthetic five-segment context on two small base models, so it does not show how instruction-tuned models treat noisy retrieval ([arXiv:2406.12824](https://arxiv.org/abs/2406.12824), Wadhwa et al., 2024-06, preprint).
- **Most of the cost is in the transformer.** Longer contexts mean more compute per token. This is the latency argument in note [07](07-rag-in-production.md).

---

## Sampling

The model outputs a probability for every vocabulary token. Sampling decides which one to emit.

| Knob | What it does | Lab observation |
|---|---|---|
| **Greedy** | Always the most likely token | Deterministic, can loop and repeat |
| **Temperature** | Rescales the distribution: p' ∝ exp(log p / T). < 1 sharpens, > 1 flattens | T = 0.3 and 1.5 start alike; T = 3 is nonsense |
| **top-k** | Sample only from the k most likely tokens | `top_k=0` behaves like greedy; `top_k=10` varies |
| **top-p** (nucleus) | Sample from the smallest set whose cumulative probability ≥ p | `top_p=0` gives identical outputs; `0.8` varies |
| Repetition penalty | Lowers probability of tokens already used | Stops loops in long answers |
| Logit bias | Push specific tokens up or down | Ban or force words, force a label vocabulary |

![The same next-token distribution at temperatures 0, 0.5, 1, 1.2 and 5: low temperature concentrates probability on the top token, high temperature flattens toward uniform](../sources/images/hasan-dlai-rag-temperature.png)
*Image Source: Hasan, DeepLearning.AI RAG course, Module 4*

top-p adapts to the model's confidence, which top-k does not. When the model is sure, the nucleus is one or two tokens; when unsure, it widens.

![top-p = 85%: candidate tokens sorted by probability, cumulative 32%, 57%, 75%, 87%; the first four are kept because 87% is the first total above 85%](../sources/images/hasan-dlai-rag-top-p.png)
*Image Source: Hasan, DeepLearning.AI RAG course, Module 4*

Temperature changes the **shape** of the distribution; top-p and top-k change **which tokens are eligible**. Setting `temperature=1` does not make output deterministic.

Both are small enough to compute by hand. Say the prompt ends "Annual plans can be refunded within", and the model's logits favour "30":

```python
import numpy as np

tokens = np.array(["30", "14", "60", "90", "soon"])
logits = np.array([3.0, 2.2, 1.0, 0.5, -1.0])

def probs(logits, temperature=1.0):
    scaled = logits / temperature
    return np.exp(scaled) / np.exp(scaled).sum()

def nucleus(p, top_p):
    order = np.argsort(-p)
    cut = np.searchsorted(np.cumsum(p[order]), top_p) + 1   # first total >= top_p
    return order[:cut]

for T in [0.3, 1.0, 3.0]:
    print(f"T={T:<4}", dict(zip(tokens.tolist(), probs(logits, T).round(3).tolist())))

p = probs(logits)
print("top_p=0.85 keeps:", tokens[nucleus(p, 0.85)].tolist())
confident = probs(np.array([6.0, 2.2, 1.0, 0.5, -1.0]))
print("same top_p, confident model keeps:", tokens[nucleus(confident, 0.85)].tolist())

rng = np.random.default_rng(0)
print("T=1 samples:", rng.choice(tokens, size=8, p=p).tolist())
```

```text
T=0.3  {'30': 0.934, '14': 0.065, '60': 0.001, '90': 0.0, 'soon': 0.0}
T=1.0  {'30': 0.593, '14': 0.267, '60': 0.08, '90': 0.049, 'soon': 0.011}
T=3.0  {'30': 0.336, '14': 0.257, '60': 0.172, '90': 0.146, 'soon': 0.089}
top_p=0.85 keeps: ['30', '14']
same top_p, confident model keeps: ['30']
T=1 samples: ['14', '30', '30', '30', '14', '60', '14', '14']
```

At T=1 the wrong "14" gets sampled regularly, which is how a correct context can still produce a wrong number if the model is unsure. Lower temperature concentrates on the favoured token, whichever token that is. The nucleus shrinks as the model gets confident, which is the adaptation top-k can't do. These logits are invented for illustration.

### Parameters by task

Lab 4.2 routes each query to a parameter set:

```python
# illustrative: needs the course's generate_params_dict, generate_with_single_input and a Together API key
def answer_query(query):
    label = decide_if_technical_or_creative(query).lower()   # one cheap LLM call
    if label == "technical":     # documentation, procedures: be precise
        kwargs = generate_params_dict(query, temperature=0,   top_p=0.1)
    elif label == "creative":    # "suggest three places to visit": allow variety
        kwargs = generate_params_dict(query, temperature=1.1, top_p=0.4)
    else:                        # classifier failed: neutral fallback
        kwargs = generate_params_dict(query, temperature=0.5, top_p=0.5)
    return generate_with_single_input(**kwargs)["content"]
```

The course's warning: keep temperature below about 1.3, and if you go near it, lower top_p to compensate.

---

## Choosing an LLM

| Factor | Question |
|---|---|
| Size | Bigger knows more and reasons better; costs more |
| Cost | Per input and output token, at your volume |
| Context window | Fits your top_k chunks plus history? |
| Latency | Time to first token and tokens per second |
| Knowledge cutoff | Matters less with RAG, but not zero |

| Benchmark type | Example | Watch out for |
|---|---|---|
| Automated | MMLU (57 subjects, multiple choice) | **Saturation** (everyone scores 90%+) and **contamination** (test set in training data) |
| Human preference | LMArena, Elo ratings | Measures preference, not correctness |
| LLM-as-judge | One model grades another | Judges favour their own model family |

Use public benchmarks to shortlist; decide on your own eval set.

---

## Prompting for RAG

### The messages format

Chat models take a list of `{role, content}` messages (`system`, `user`, `assistant`). Under the hood each model family wraps them in special tokens (Llama uses `<|begin_of_text|>`, `<|start_header_id|>system<|end_header_id|>` and so on). The API hides this; know it exists when a raw-completion endpoint misbehaves.

### A RAG prompt template

| Section | Contents |
|---|---|
| **System** | Use only the retrieved documents. Judge whether each is relevant. Cite sources. Say so if the answer is not there |
| **History** | Prior turns, pruned to the last N messages |
| **Retrieved** | `[DOC 1] … (source: …)`, `[DOC 2] …` |
| **Query** | The user's current question |

| Technique | Use in RAG |
|---|---|
| In-context learning | Retrieve *examples* of good past answers, not just facts |
| Chain of thought / scratchpad | Let the model reason over conflicting documents before answering |
| Reasoning models | Few-shot examples tend to *hurt*; drop prior reasoning tokens from history |
| Context pruning | Keep the last N messages; summarise or drop older ones |

The first row has been measured in one form. RAG+ pairs each knowledge item in the corpus, offline, with a worked example of that item in use, and retrieves the pair, with no change to the retriever or the model. With BGE-M3 and top-3 chunks, Qwen2.5-72B rose from 76.5 to 83.0 on 200 Chinese sentencing questions (one statute, three answer intervals) and from 77.5 to 87.5 with a reranker. On a 430-question numerical-analysis set it rose from 70.47 to 73.72. **Gains were mostly a few points and not uniform:** Qwen2.5-7B fell from 59.2 to 57.6 on 500 MedQA questions. Examples alone, without the knowledge, helped less (65.0 against 76.5 for the 7B on the legal set). The sets are small and built by the authors, the examples were written by the same model family that is evaluated, and there is no comparison with more knowledge chunks at the same token budget ([arXiv:2506.11555](https://arxiv.org/abs/2506.11555), Wang et al., 2025-06, v4 2025-09, preprint). Note [08](08-agentic-rag-prince.md#retrieved-few-shot-examples) keys its examples to the query instead, which is the cheaper thing to try first.

Here is the template over Tallybook. The system message, the numbered documents and the id they carry are the parts that later checks depend on:

```python
from ragkit import DOC_BY_ID, Retriever

SYSTEM = ("Answer only from the documents below. Judge whether each is relevant. "
          "Cite documents as [DOC n] after each claim. If the answer is not in them, "
          "say the documents do not contain it.")

def build_messages(query, doc_ids, history=(), keep_turns=4):
    numbered = "\n".join(f"[DOC {n}] {DOC_BY_ID[i].full} (source: {i})"
                         for n, i in enumerate(doc_ids, 1))
    return ([{"role": "system", "content": SYSTEM}]
            + list(history)[-keep_turns:]
            + [{"role": "user", "content": f"{numbered}\n\nQuestion: {query}"}])

query = "How long do refunds take to arrive?"
doc_ids = Retriever().hybrid(query, k=2)
for message in build_messages(query, doc_ids):
    print(message["role"].upper(), "|", message["content"][:150])
```

```text
SYSTEM | Answer only from the documents below. Judge whether each is relevant. Cite documents as [DOC n] after each claim. If the answer is not in them, say th
USER | [DOC 1] Refund policy. Annual plans can be refunded in full within 30 days of payment. After 30 days we refund the unused months minus a 10 percent fe
```

### Order and size of the context

Liu et al.'s lost-in-the-middle result (models use information at the start and end of a long context better than in the middle) gives a cheap reordering trick. Raieli and Iuculano describe an alternating pattern: chunks at even ranks go to the front of the list and odd ranks to the back, so the strongest chunks sit at both edges. It matters most with a wide top-k (*Building AI Agents*, ch. 6).

```python
def edges_first(ranked):
    # Rank 1 at the front, rank 2 at the back, working in toward the middle.
    front = ranked[0::2]           # ranks 1, 3, 5...
    back = ranked[1::2][::-1]      # ranks 6, 4, 2...
    return front + back

print(edges_first([f"rank{i}" for i in range(1, 8)]))
```

```text
['rank1', 'rank3', 'rank5', 'rank7', 'rank6', 'rank4', 'rank2']
```

How many passages to pass depends on whether the reader can combine them. Fusion-in-Decoder (FiD) encodes each retrieved passage separately, with the question prepended, and lets the decoder attend over all of them at once, so encoder cost grows linearly with the number of passages. With a fine-tuned T5-base reader, trained and tested at each passage count on DPR-retrieved passages, going from 10 to 100 passages raised exact match by about 3.5 on Natural Questions and 6 on TriviaQA (validation sets; the paper writes these as %). The authors cite earlier work in which extractive readers peaked at 10–20 passages. FiD-large (770M) reached 51.4 EM on the NQ test set with DPR and 100 passages, against 44.5 for RAG and 36.6 for closed-book T5 at 11B. Even with BM25 retrieval it scored 44.1 ([arXiv:2007.01282](https://arxiv.org/abs/2007.01282), Izacard & Grave, EACL 2021). The result holds for a reader trained to fuse, on short factoid answers. The paper never tests passage order and never measures how cost scales with passage count (it reports only 147 against 425 training GPU-hours for two schedules), so it says nothing about how a prompted LLM handles 100 chunks.

Long answers need more evidence than short ones, and a short context runs out first. ELI5 asks for explanations averaging 130 words. Its support document is the 15 passages most TF-IDF-similar to the question, taken from the top 100 Common Crawl pages and averaging 858 words. On 500 sampled training questions it contained the answer 65% of the time. An extractive oracle picking the best sentences from it reached 27.4 ROUGE-1, against 54.8 from all 100 pages. When the authors rebuilt the document from 500 passages for 1,000 questions, under 9% of the oracle's sentences came from the 20 top-ranked ones. The evidence a long answer needs is spread deep in the ranking. The abstractive model wrote more relevant answers than the extractive one (84% vs 68%), but only 19% of its answers were fully accurate against the support document, against 40% (100 answers rated by the authors) ([arXiv:1907.09190](https://arxiv.org/abs/1907.09190), Fan et al., ACL 2019). These are 2019 models trained from scratch and scored with ROUGE, which the authors concede can't compare extractive and abstractive systems.

A reader that only concatenates behaves the opposite way to FiD: extra text costs it quality even when the right sentence is there. On Wizard of Wikipedia the retrieved knowledge averaged 61 sentences and 1,626 tokens per turn, more than GPT-2's 1,024-token window, and plain truncation cut the gold sentence in 53% of test examples. With the gold sentence forced in, growing GPT-2's input limit from 128 to 1,024 tokens took unigram F1 from 30.9 to 19.7 (seen topics), as the gold sentence's share of the input fell from 62% to 4%. Letting the model's selector keep two or three sentences instead of one also lowered F1 while it improved perplexity ([what perplexity measures](../../01-llm-fundamentals/notes/06-pretraining-data-and-objectives.md#entropy-cross-entropy-kl-and-perplexity)). A BERT selector that passed GPT-2 just one sentence, trained without knowledge labels, scored 22.0 F1 against 18.7 for truncation ([EMNLP 2020](https://doi.org/10.18653/v1/2020.emnlp-main.272), Zhao et al., KnowledGPT). This is a 117M GPT-2 scored by word overlap against one human reply, and the forced-gold sweep is an oracle no real system has. Still, the pattern matches the noise results above: pass less, better-selected text.

When the retrieved text is too long, compress it before generation (*Building AI Agents*, ch. 6):

| Method | How |
|---|---|
| Selective context | Score each token or sentence by self-information under a small LM; keep the top percentile |
| LLMLingua | A small LM (Alpaca-7B) first drops whole low-perplexity demonstrations, then drops low-perplexity tokens segment by segment under a per-section budget. On an 8-shot GSM8K chain-of-thought prompt for GPT-3.5-Turbo, 20× compression (2,366 → 117 tokens) cost 1.5 EM points (77.3 vs 78.9), where Selective Context scored 44.2 at 15×. On BBH, 7× cost 13.2 points, and every method collapsed at 25–30× on GSM8K. End-to-end latency fell from 8.6 s to 2.3 s at 5× on one V100. Tested on reasoning prompts, conversations and arXiv summaries, not retrieved passages ([arXiv:2310.05736](https://arxiv.org/abs/2310.05736), Jiang et al., EMNLP 2023) |
| LongLLMLingua | Question-aware version: compresses and reorders documents using both context and query |
| AutoCompressors | Fine-tune the model to summarise long text into summary vectors used as soft prompts |

The last row has grown into its own line of work: compress each retrieved chunk into a few vectors once, offline, and have a trained reader consume those vectors in place of the chunk's tokens. AutoCompressors (Chevalier et al., EMNLP 2023) and CEPE (Yen et al., ACL 2024) came first. REFRAG encodes each 16-token chunk with RoBERTa-large and feeds one projected vector per chunk to LLaMA-2-7B. A small RL policy picks the few chunks to keep as raw tokens. At 16x compression and a 16,384-token context, time to first token fell **16.53x with the chunk embeddings precomputed and 8.59x without**, against 2.01x and 1.04x for CEPE, on one A100 at batch size 1. Per-token decoding sped up only about 3x. On 16 RAG tasks with 400M passages it matched the fine-tuned LLaMA at 10 passages with a 5.26x faster first token, and at equal latency (8 passages against 1) gained 1.22% on average. Perplexity came close to full context only at 8x (at or below it in some of its tables, not stated as a finding), and getting there took 20B tokens of continued pretraining, then fine-tuning and the RL policy ([arXiv:2509.01092](https://arxiv.org/abs/2509.01092), Lin et al. (Meta), 2025-09, preprint). CLaRa trains the reranker through the same compressed vectors with a straight-through top-k, so the generator's next-token loss is the only relevance label. With Mistral-7B, BGE's top 20 cut to 5, and Wikipedia QA, 16x compression averaged 40.30 F1 against 41.96 for DRO, a jointly trained raw-text system whose numbers are copied from its paper, so comparable, not better. Decoding took about 40% of the raw-text time on one H100, with compression done offline and not counted ([arXiv:2511.18659](https://arxiv.org/abs/2511.18659), He et al. (Apple), 2025-11, v3 2026-02, preprint). COCOM compresses each of five passages into 4 to 128 embeddings with the same Mistral-7B as compressor and decoder (LoRA, 493K fine-tuning examples). Averaged over NQ, TriviaQA, HotpotQA, ASQA and PopQA, exact match was 0.585 at 4 embeddings per passage and 0.540 at 128, against 0.623 uncompressed. Decoding on NQ took 187 ms at 128 embeddings against 1,064 ms uncompressed (5.69x, one A100, batch 16), and the 24M-passage index was 6.06 TB at 4 embeddings per passage and 0.19 TB at 128. Freezing the decoder cost about 10 points of NQ EM at 128 (0.519 to 0.421). The frozen-decoder baselines saw only one passage or a truncated concatenation, so method and tuning are confounded; 7B only, one run ([arXiv:2407.09252](https://arxiv.org/abs/2407.09252), Rau et al., 2024-07, preprint). Both need open weights and a training run, so neither applies to a hosted model. Both store vectors whose size is not reported and must be recomputed when the compressor changes. What carries over is the measurement. Most of a RAG prompt is passages that barely attend to one another, so first-token latency is where context compression pays.

And when one call over all chunks is the wrong shape, a response synthesizer makes several (*Building AI Agents*, ch. 6):

- **Refine:** answer from the first chunk, then send the answer plus the next chunk to improve it, one chunk at a time.
- **Concatenate:** answer from each chunk separately, then join the answers, or summarise them into one.
- **Hierarchical:** summarise groups of answers, then summarise the summaries.

### Classification and structured output

Two pieces of Lab 4.2 that the assignment reuses:

```python
# illustrative: needs the course's generate_with_single_input and generate_with_multiple_input,
# a Together API key, and `query` and `transcript` from the lab
# 1. LLM as a classifier: precise instructions, labelled examples (incl. edge cases),
#    and max_tokens 1–2 so it can only emit the label
prompt = f"""Label the following instruction as an FAQ-related query or a product-related query.
Examples:
    Is there a refund for incorrectly bought clothes? Label: FAQ
    Do you have blue T-shirts under 100 dollars? Label: Product
Return only one of the two labels: FAQ or Product.
Instruction: {query}"""
label = generate_with_single_input(prompt, temperature=0, max_tokens=1)["content"].strip()
label = label if label in ("FAQ", "Product") else None    # always validate the label

# 2. Structured output: pass a JSON schema instead of begging for JSON in the prompt
from pydantic import BaseModel, Field

class VoiceNote(BaseModel):
    title: str = Field(description="A title for the voice note")
    summary: str = Field(description="A short one sentence summary of the voice note.")
    actionItems: list[str] = Field(description="A list of action items from the voice note")

result = generate_with_multiple_input(
    messages=[{"role": "system", "content": "The following is a voice message transcript. Only answer in JSON."},
              {"role": "user", "content": transcript}],
    response_format={"type": "json_schema", "schema": VoiceNote.model_json_schema()},
)
```

The schema also gives you a validator on your side of the call, and that is what the code path after the model depends on. These two strings stand in for model responses. The second has the wrong shape:

```python
from pydantic import BaseModel, Field, ValidationError

class CitedAnswer(BaseModel):
    answer: str
    citations: list[str] = Field(min_length=1)

good = '{"answer": "Refunds take 5 to 10 working days.", "citations": ["kb-04"]}'
bad = '{"answer": "Refunds take 5 to 10 working days.", "citations": []}'

for raw in [good, bad]:
    try:
        print("ok:", CitedAnswer.model_validate_json(raw).citations)
    except ValidationError as err:
        print("rejected:", err.errors()[0]["msg"])
```

```text
ok: ['kb-04']
rejected: List should have at least 1 item after validation, not 0
```

A schema guarantees shape only. A hallucinated citation like `["kb-99"]` passes, and the checks in the next section are what catch it.

The "old-fashioned way" in the lab (a smart-home prompt listing every device ID with JSON examples, `{{ }}` escaped inside the f-string) works but is long and fragile; the schema parameter guarantees parseable output.

---

## Rules of thumb

| Rule | Why |
|---|---|
| Temperature ≈ 0, low top_p for factual RAG answers | Faithfulness over variety |
| Classifier calls: `max_tokens` 1–2, validate the label | Can't ramble, failures are explicit |
| Use the schema parameter for JSON | Parsing never fails |
| Tell the model to cite and to say "not in the documents" | Cheapest hallucination defence |
| Put the strongest chunks at the edges or next to the question | Lost in the middle; near-miss distractors hurt |
| Pass fewer, better-selected passages to a reader that only concatenates | Extra text dilutes the gold sentence |

---

## Labs

| Lab | Label |
|---|---|
| M4 Lab 4.1 (sampling parameters), Lab 4.2 (classification, params by task, structured output) ([upstream](https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG)) | needs an API key (Together.ai); not copied |

---

## Pitfalls

- **Expecting sampling to fix a wrong answer.** Symptom: lowering temperature makes the answer consistent and still wrong. Sampling chooses among what the model already believes; fix the context instead.
- **High temperature on factual answers.** Symptom: the same question gets a different number on reruns. Use near-zero temperature and a low top-p.
- **Sending every retrieved chunk to a concatenating reader.** Symptom: answers get worse as top-k grows, even when the right passage is in the set. KnowledGPT saw F1 fall from 30.9 to 19.7 as GPT-2's input grew with the gold sentence forced in. Select or compress before generation.
- **Padding the prompt because one paper saw noise help.** Cuconasu et al.'s random-document effect has no agreed explanation. Use the safe findings: near-miss distractors hurt, and best evidence goes next to the question.

---

## Try it

1. In the sampling block, set the logits to `[1.2, 1.0, 1.0, 0.9, 0.8]`. How many tokens does `top_p=0.85` keep, and what does that mean about asking this model a factual question?
2. Call `edges_first` on four ranks. Where does rank 2 land, and why is that the right place for it?
3. Pass `build_messages` a history of six messages with the default `keep_turns=4`. How many user turns reach the model, and what does the name `keep_turns` hide?

<details>
<summary>Answers</summary>

1. All five, since the distribution is nearly flat and the cumulative total is still 0.834 at the fourth token. The model has no firm belief. Sampling settings can make it consistent and can't make it right, so the fix is better context.
2. `['rank1', 'rank3', 'rank4', 'rank2']`. Rank 2 goes last, at the far edge, which lost-in-the-middle says models read better than the middle. With four chunks the effect is small; it matters with a wide top-k.
3. The slice keeps the last four *messages*, so two user turns and their two replies. The parameter counts messages, not turns, and a tool call or system note in the history would take a slot too. Name it for what it counts, or prune by turn.

</details>

---

## Interview checklist

| Question | Answer |
|---|---|
| Temperature vs top-p? | Temperature reshapes the distribution. top-p restricts which tokens are eligible, keeping the smallest set whose cumulative probability reaches p, so it adapts to the model's confidence. |
| Settings for factual RAG? | Temperature near 0 and a low top-p, with an "only from the documents, cite, say if absent" prompt. |
| Which retrieved passages hurt most? | High-scoring ones that lack the answer. Cuconasu et al. saw up to a 25% drop from a single such distractor added to the gold passage. |
| How would you order the context? | Put the strongest chunks at the edges (lost in the middle), or nearest the question (Cuconasu et al.). It matters most with a wide top-k. |
| Why does RAG work at all? | Attention lets every generated token look at the retrieved documents, so the context can change the output without changing the weights. |
| How many passages should the reader get? | Depends on the reader. FiD, trained to fuse, gained from 10 to 100 passages; a reader that only concatenates loses quality as text is added, even with the gold sentence in. |
| Why use a JSON schema over a prompt request? | The schema makes output parseable and gives you a validator. It doesn't make the content true. |

---

## Next

[06b — Hallucinations, evaluation and fine-tuning](06b-hallucinations-evaluation-and-fine-tuning.md): the prompt is grounded. Now catch the answers that drift from it anyway, measure faithfulness, split the call into a workflow, and decide when fine-tuning belongs beside retrieval.
