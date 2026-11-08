---
origin: synthesis  # split from 02-why-rag-and-the-augmented-prompt.md (2026-11-08) so each part stays under the chapter length cap
sources:
  - https://arxiv.org/abs/2012.04584
  - https://arxiv.org/abs/2002.08909
  - https://arxiv.org/abs/1911.00172
  - https://arxiv.org/abs/2102.02557
  - https://arxiv.org/abs/2112.04426
  - https://arxiv.org/abs/2208.03299
  - https://arxiv.org/abs/2310.07713
  - https://arxiv.org/abs/2310.14820
  - https://arxiv.org/abs/2301.02828
  - https://arxiv.org/abs/2306.13421
  - Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 6
  - Huyen, *AI Engineering* (O'Reilly, 2025), ch. 6
confidence: high
cleaned: 2026-11-08
---
# 2b — Training the retriever and the reader

Everything in the course so far is training-free: an off-the-shelf embedder, an off-the-shelf LLM and a prompt that joins them. That is a choice, and this part is about what the other choices are. You can train the retriever, the reader or both, and a line of research has done each. The results are mostly language-modelling and open-domain QA numbers at research scale, so they tell you what is possible and what it costs, and not what your Tallybook bot needs.

> Part two of "why RAG". [02](02-why-rag-and-the-augmented-prompt.md) built the augmented prompt and the case for retrieval. Here: the five ways to train the two halves (RETRO, Izacard and Grave, REALM, kNN-LM, Atlas), then four later papers that sharpen them. InstructRetro scales retrieval-augmented pretraining to 48B, a re-implementation explains why kNN-LM works, RPT trains a retriever from the language model's own likelihood, and ALCUNA tests what a reader does with knowledge it has never seen.

---

## The paradigms, from training-free to joint

Raieli and Iuculano sort the ways the two halves can be trained (*Building AI Agents*, ch. 6):

| Paradigm | What is trained | Example |
|---|---|---|
| Training-free | Nothing; off-the-shelf retriever and LLM | The course, most production RAG |
| Independent | Each half on its own objective | A fine-tuned embedder plus a separately fine-tuned LLM |
| Sequential, retriever first | Retriever fixed, then the LLM learns to use what it returns | RETRO: frozen BERT retriever, language model pretrained to attend to what it finds |
| Sequential, LLM first | LLM fixed, then the retriever learns from the LLM's signal | Izacard & Grave: the reader's attention scores supervise the retriever |
| Joint | Both, end to end | Lewis et al. ([02](02-why-rag-and-the-augmented-prompt.md#the-two-components)); REALM, below |

The "LLM first" row needs less labelling than it sounds. Izacard and Grave trained a retriever with no question–passage labels at all, only question–answer pairs. The reader (a T5 Fusion-in-Decoder model reading 100 passages) attends to some passages more than others. Its cross-attention, averaged over layers, heads and the passage's tokens for the first output token, became the target the retriever was trained to match with a KL loss ([KL](../../01-llm-fundamentals/notes/06-pretraining-data-and-objectives.md#entropy-cross-entropy-kl-and-perplexity)). Starting from BM25's passages and iterating two or three times, the retriever beat supervised DPR on test-set retrieval: top-20 recall 80.0 vs 79.4 on Natural Questions and 81.4 vs 79.4 on TriviaQA ([arXiv:2012.04584](https://arxiv.org/abs/2012.04584), Izacard & Grave, ICLR 2021). It depends on a decent start. From untrained BERT it reached 68.8 on NQ, well short of DPR, and the authors state outright that they assume attention scores measure relevance. Their one direct test: keeping the top 10 of 100 passages by attention gave 46.8 EM, against 42.9 for DPR's top 10 and 48.2 with all 100. Huyen notes that fine-tuning the retriever and generator together improves results. The price is that the pair now has to be retrained together, which is one reason most systems stay training-free.

REALM shows what the joint row costs. It pretrained a BERT-base retriever and reader together, masking named entities and dates so the reader needed the retrieved text. Each retriever update makes the stored document vectors stale, so a second job re-embedded all 13M Wikipedia chunks about every 500 training steps. With an index 30× staler, Natural Questions dev exact match fell from 38.2 to 28.7, below the ORQA baseline it set out to beat. Trained properly, the 330M model scored 39.2–40.4 on NQ test, ahead of closed-book T5-11B's 34.5 (REALM's figure, from an earlier version of Roberts et al.) at 30 times the size, while reading only 5 documents ([arXiv:2002.08909](https://arxiv.org/abs/2002.08909), Guu et al., ICML 2020). Even REALM froze the document index during fine-tuning, for simplicity, and the authors guess that refreshing it there too might have helped.

Retrieval can also act on the model's output, with no training at all. kNN-LM stores one entry per training token: the model's hidden state for the preceding text, paired with the token that came next. At each step it looks up the 1,024 nearest stored states and mixes their next tokens into the model's own prediction. On WikiText-103 that took a 247M model's test perplexity from 18.65 to 16.12. A model trained on 100M Wikipedia tokens and given a 3B-token datastore reached 13.73, better than the same model trained on all 3B tokens (15.17). Swapping in a datastore of books, with no retraining, cut a Wikipedia model's perplexity on books from 34.84 to 20.47, still well short of a model trained on books (11.89) ([arXiv:1911.00172](https://arxiv.org/abs/1911.00172), Khandelwal et al., ICLR 2020). The evidence is perplexity at one model size. The datastore holds one entry per token, and a lookup runs at every generated token. SPALM moved the mix inside the network: a learned gate decides, token by token, how much of the retrieved next tokens to blend into the hidden state, where kNN-LM uses one fixed weight tuned on the dev set. Both were run on the same 142M Transformer-XL with 4 neighbours, not kNN-LM's original 1,024. On WikiText-103 the gate alone did not beat kNN-LM (18.3 vs 18.0 test perplexity at a 3,072-token memory). On news with a later test month it did (14.0 vs 15.2, at 148M), and the authors suggest that kNN-LM's weight, tuned on a dev month, suffered when the test month differed; they did not test that. Neither gap was significance-tested. Finding the neighbours for every training token took 6–8 hours on 1,000 CPUs for WikiText-103 ([arXiv:2102.02557](https://arxiv.org/abs/2102.02557), Yogatama et al., TACL 2021).

Retrieval can also be built into pretraining. RETRO splits the input into 64-token chunks, looks up the nearest chunks in a database with a frozen BERT encoder, and trains the language model to cross-attend to them. With a 2-trillion-token database, the 7.5B model beat the 178B Jurassic-1 on most Pile subsets in bits-per-byte. The abstract calls it comparable to GPT-3 and Jurassic-1 with 25× fewer parameters. On C4, the gain from retrieval was about what a 10× larger model without retrieval would give, and it stayed constant from 172M to 7.5B parameters ([arXiv:2112.04426](https://arxiv.org/abs/2112.04426), Borgeaud et al., ICML 2022). Read those multipliers as language-modelling numbers. On Natural Questions RETRO scored 45.5 exact match, below FiD's 51.4. Part of its advantage comes from finding the test text in the database: it exploits overlap more than the baselines do, and the authors call its Wikitext103 perplexity of 3.92 partly leakage. It still won on chunks sharing no more than 8 contiguous tokens with the training data. The claim that updating the database keeps the model current, or removes data, is argued, not measured.

Atlas, a T5 Fusion-in-Decoder reader trained together with a Contriever retriever, measured the update half of that claim. It also tested how far retrieval substitutes for size. The 11B model scored 42.4 exact match on Natural Questions from 64 examples, ahead of the 540B PaLM's 39.6 ([arXiv:2208.03299](https://arxiv.org/abs/2208.03299), Izacard et al., JMLR 2023). Atlas was fine-tuned on those 64 examples while PaLM was only prompted with them, so method differs as well as size. Its four ways of training the retriever from the reader made no systematic difference. Refreshing the index during training cost about 30% extra compute, and product quantisation shrank the Wikipedia index from 49 GB to 4 GB with a negligible drop. Its index swap is in the table under [What RAG buys you](02-why-rag-and-the-augmented-prompt.md#what-rag-buys-you).

---

## Scaling the "retriever first" row: InstructRetro

RETRO, above, was pretrained from scratch with retrieval. InstructRetro asks whether that is worth doing at 48B, and whether it pays off after instruction tuning. It does not train from scratch. *Retro-fitting* takes a 43B GPT pretrained on 1.1T tokens and continues for 100B more tokens with RETRO's chunked cross-attention over a 1.2T-token database. The database is the pretraining corpus itself (19 billion chunks of 64 tokens, BERT keys, 2 neighbours per chunk), minus a held-out 1%. The decoder is unfrozen. Instruction tuning then runs with the retrieval encoder switched off, because instruction data has no retrieved neighbours ([arXiv:2310.07713](https://arxiv.org/abs/2310.07713), Wang et al., ICML 2024).

![Three-stage pipeline: a decoder-only transformer is pretrained on 1.1T tokens into GPT 43B, continued for 100B tokens with retrieval from a 1.2T-token database into Retro 48B, then instruction-tuned into InstructRetro 48B, and the encoder is disabled to give InstructRetro 43B](../sources/images/wang-instructretro-fig1.png)
*Image Source: Wang et al., [InstructRetro: Instruction Tuning post Retrieval-Augmented Pretraining](https://arxiv.org/abs/2310.07713) (2024), Fig. 1*

Three results matter for the table.

- **The retrofit is cheap.** Retro 48B reached lower perplexity than GPT 43B for 2.58% extra GPU hours, and the gap to GPT did not shrink from 8B to 48B (held-out 1% of the pretraining corpus, 823M to 48B). It is not a matched comparison: Retro has about 10% more parameters in its encoder and cross-attention, and costs about 35% more compute on the continued tokens (27–37% across sizes).
- **Instruction tuning is what unlocks it.** Before instruction tuning, the retrieval benefit on zero-shot Natural Questions saturated with scale. After it, InstructRetro 43B beat an instruction-tuned GPT 43B given the same retrieved passages (InstructGPT-RAG) by 7% on average over eight short-form QA and reading-comprehension tasks (zero-shot, same instruction data and prompts). NQ exact match was 38.9 against 37.0, and TriviaQA 78.3 against 78.1, so the average hides small gaps. Long-form QA improved 10% over four datasets (three of them proprietary), and three summarisation sets 16%, for example GovReport ROUGE 17.46 against 12.59.
- **The encoder was not needed at inference.** InstructRetro 43B, decoder only, matched the 48B model with its encoder (NQ 38.9 against 38.6; average +7% against +6%). The benefit had moved into the decoder's weights.

Read it with its limits. Downstream retrieval used top-5 DRAGON+ passages from each task's own corpus, not the pretraining database, so the BERT retriever that RETRO-style pretraining uses was never the one evaluated. Retrieval-augmented instruction tuning is left as future work. These are single runs with no significance tests.

---

## Why kNN-LM works: a second softmax

The kNN-LM paragraph above reads as "retrieval from a datastore lowers perplexity". Xu et al. re-implemented it on a 268M-parameter Transformer over WikiText-103 (BPE, 33K vocabulary, datastore of all 150M training tokens, k = 1,024) and ablated one design choice at a time. They treat kNN-LM as an interpolation of two [softmaxes](../../01-llm-fundamentals/notes/04-decoding-and-inference-behaviour.md#decoding), the model's own and one built from neighbours, so that every piece can be varied. Perplexity went from 21.750 to 19.174 with L2 distance and 19.095 with inner product. That base is worse than Khandelwal et al.'s 18.65 (it is their own from-scratch BPE model with a 33K vocabulary and a standard softmax; the paper gives no cause), so compare relative gains and never raw perplexities across the two papers ([arXiv:2301.02828](https://arxiv.org/abs/2301.02828), Xu et al., preprint).

What they found:

- **Which hidden state you query with matters.** Using the feed-forward output instead of the attention output left kNN-LM at 20.734 (L2) and 21.101 (inner product).
- **Part of the gain needs no retrieval.** A separate trainable output matrix on the attention output, interpolated with the base model, recovered about 55% of kNN-LM's gain (20.353 against 19.095). Giving each word type several trained embeddings did about half as well and did not improve steadily as embeddings were added.
- **Approximate search beat exact search**, 19.174 against 19.735 for the exact mask and exact score. The authors suggest approximate neighbours regularise against overfitting to a datastore built from the training set. That is a hypothesis backed by token-level correlations, not a causal test.
- **Temperature is a real knob.** The default of 1 is near-optimal only by coincidence in the original settings, and the gap between default and tuned can reach 3.7% relative perplexity.
- **More datastore keeps helping, close to linearly.** Even a 5% sample (about 15 GB) beat the base model.

The scope is narrow: one model family, one dataset, perplexity only, no seeds or intervals, and a datastore that is the model's own training set. It explains why kNN-LM helps there. It does not show how retrieval from fresh or external text helps, which was the point of the book swap in the paragraph above. Treat "retrieval" in kNN-LM's gain as partly a better output layer.

```python
# illustrative: kNN-LM's two softmaxes, mixed. Khandelwal et al. fix lam on a dev set.
import math
from collections import defaultdict

def knn_mix(p_lm, neighbours, lam=0.25, temp=1.0):
    """p_lm: {token: prob}. neighbours: [(distance, next_token)] from the datastore."""
    w = defaultdict(float)
    for dist, tok in neighbours:
        w[tok] += math.exp(-dist / temp)       # closer neighbours count more
    z = sum(w.values())
    p_knn = {t: v / z for t, v in w.items()}
    vocab = set(p_lm) | set(p_knn)
    return {t: lam * p_knn.get(t, 0.0) + (1 - lam) * p_lm.get(t, 0.0) for t in vocab}

p_lm = {"30": 0.40, "14": 0.35, "45": 0.25}
nbrs = [(0.5, "30"), (0.7, "30"), (1.5, "14")]
for temp in (1.0, 0.25):
    out = knn_mix(p_lm, nbrs, lam=0.5, temp=temp)
    print(temp, {k: round(v, 3) for k, v in sorted(out.items())})
# 1.0  {'14': 0.259, '30': 0.616, '45': 0.125}
# 0.25 {'14': 0.181, '30': 0.694, '45': 0.125}
```

The only change between the two lines is the temperature, and the mixed distribution moves. That is the knob Xu et al. found worth tuning.

---

## A retriever trained by the language model: RPT

The "LLM first" row trains a retriever from a reader's signal, and the "joint" row trains both. The Retrieval-Pretrained Transformer (RPT) does something in between, for long documents. It splits each document into 64-token chunks and retrieves earlier chunks of the *same* document, using a learned bilinear score over pooled states from the lower decoder layers, and fuses them with RETRO-style chunked cross-attention. So the index is the document's own earlier text and no external corpus is involved. Neighbours pass through a learned gate with a floor of 0.1, which keeps gradients flowing, and training uses scheduled sampling ([arXiv:2306.13421](https://arxiv.org/abs/2306.13421), Rubin and Berant, TACL 2024).

The retriever's supervision is the part to keep. BM25 proposes 20 candidate chunks. A frozen Pythia-1.4B scores each by how much the candidate raises the likelihood of the *next* chunk, log P(next chunk | candidate) minus log P(next chunk | the two preceding chunks). Candidates scoring above 0 are positives, and a LambdaRank loss trains the retriever alongside the language-model loss. The language model's own likelihood defines relevance, so no labels are needed, in the spirit of Izacard and Grave's attention signal but taken from a separate scoring model.

```python
# illustrative: RPT's positive-chunk rule (Rubin and Berant); the log-probs come from a frozen scoring LM
def is_positive(logp_next_given_candidate, logp_next_given_two_preceding):
    return logp_next_given_candidate - logp_next_given_two_preceding > 0

print(is_positive(-42.0, -45.5), is_positive(-47.0, -45.5))   # True False
```

All numbers below are at 242M parameters and 500K steps with 2 neighbours, against the authors' own implementations, on test perplexity (ArXiv / CodeParrot / PG19 / Books3).

| Model | ArXiv | Code | PG19 | Books3 |
|---|---|---|---|---|
| Transformer-XL (no retrieval) | 3.11 | 2.30 | 11.48 | 15.00 |
| RETRO with BM25 | 2.94 | 2.17 | 11.44 | 14.60 |
| RPT-Lex (lexical training signal) | 2.92 | 2.23 | 11.59 | 14.32 |
| RPT-Sem (semantic training signal) | 2.77 | 2.17 | 10.96 | 13.91 |

Three things follow from the paper's ablations.

- **The training signal matters more than the architecture.** RPT-Lex is not reliably better than RETRO with BM25, while RPT-Sem is better on all four sets. On retrieval itself, average Precision@2 was 25.2% for BM25, 23.2% for RPT-Lex and 30.0% for RPT-Sem.
- **Joint training matters.** Swapping in a separately trained DPR-style retriever made every dataset worse (Books3 13.91 to 14.66, ArXiv 2.77 to 2.98). This is the joint row's argument measured, at small scale.
- **Training tricks matter.** Removing neighbour gating raised Books3 perplexity from 13.91 to 18.68, and removing teacher forcing raised PG19 from 10.96 to 13.10.

The retriever is still the limit: with oracle neighbours chosen by the scoring model, Books3 fell to 12.74 (the paper's text mixes baseline columns, so take the gap as about one perplexity point, not a precise delta). Training costs 1.51× the time per update of the baseline, against 1.35× for RETRO with BM25, and needs a frozen scoring LM. Retrieval is only within a document, the models are small, only perplexity is reported, and the supervision can only re-rank BM25's top 20, so BM25's recall caps it. There is no downstream task or factuality result.

---

## What a reader does with knowledge it has never seen: ALCUNA

Every paradigm above assumes the reader can use what it is handed. ALCUNA tests that directly, and not through a retriever. It builds artificial biological entities from EOL taxonomy data, with properties that cannot be in any training set, puts their properties in the prompt as structured JSON, and asks template-generated questions on three abilities: understanding the new entity (KU), telling it apart from its parent (KD), and linking it to existing knowledge across several hops (KA). Four models were tested: ChatGPT and three small open models (Alpaca 7B, Vicuna 13B, ChatGLM 6B) ([arXiv:2310.14820](https://arxiv.org/abs/2310.14820), Yin et al., EMNLP 2023). It tests zero-shot and few-shot prompts, each plain and with chain-of-thought (the averages above are few-shot plain), with no retriever and no GPT-4-class model, and a 100-question human check found 98% (one-hop) and 95% (multi-hop) of questions correct.

- **Multi-hop use is the weak point.** ChatGPT averaged 64.37 few-shot but only 41.52 on association (KA). The open models averaged 35.09, 42.74 and 42.56. Association was the hardest ability for ChatGPT, Vicuna and ChatGLM in every setting, and for Alpaca in the few-shot settings, and chain-of-thought did not fix it for ChatGPT (37.88 against 41.52).
- **Context on the reasoning chain helps, other context hurts.** Adding the entities on the chain to the prompt lifted KA for ChatGLM from 27.47 to 44.43 and for Vicuna from 30.10 to 33.25. Irrelevant entities lowered it (ChatGLM 18.56).
- **The parent entity confuses the model.** Putting the parent's knowledge in the context cut differentiation (KD) from 41.42 to 24.71 for ChatGLM and from 46.76 to 35.04 for Vicuna. The more an entity's properties overlap its parent's, the worse the models did. Only ChatGPT was nearly insensitive.
- **Format matters for small models.** Structured JSON beat natural language for all three open models, for example ChatGLM 42.56 against 20.54 on the average.

The lesson for retrieval is about the reader, and it does not follow from a retrieval experiment. A retriever that returns the chunk and also the near-duplicate "parent" chunk (the old policy beside the new one) can lower accuracy, and linking two retrieved facts is harder than quoting one. The study covers biological taxonomy only, and questions are template-generated and scored by matching.

---

## Rules of thumb

| Rule | Why |
|---|---|
| Start training-free and train only against a measured gap | Huyen: joint training helps but forces the pair to be retrained together. Most systems stay training-free |
| Tune the kNN softmax temperature and mixing weight | Xu et al.: the default can sit up to 3.7% relative perplexity from the optimum |
| Judge a retriever trained on LM signal by retrieval and by perplexity | RPT-Sem moved Precision@2 from 25.2% (BM25) to 30.0% and perplexity with it |
| Keep the index fresh while a retriever trains | REALM's 30× staler index cost 9.5 points of NQ exact match (38.2 to 28.7) |
| Put the facts on the reasoning chain in the context and leave the near-duplicates out | ALCUNA: related-entity context raised KA, the parent entity cut KD |

---

## Pitfalls

- **Crediting retrieval for the whole kNN-LM gain.** Symptom: a perplexity drop is attributed to the datastore when a trained output layer would give about half of it. Xu et al.'s separate output matrix recovered about 55%. Run the no-retrieval control.
- **Comparing perplexities across tokenizers.** Symptom: "18.65 beats 21.75". Khandelwal's and Xu's base models use different vocabularies. Compare relative gains within one paper.
- **Reading language-modelling multipliers as QA results.** Symptom: "RETRO matches a model 25× larger" is quoted for a question-answering use case. On Natural Questions RETRO scored 45.5 EM against FiD's 51.4.
- **Letting the index go stale during joint training.** Symptom: retrieval quality collapses mid-run. REALM's index 30× staler dropped NQ dev EM from 38.2 to 28.7. Atlas paid about 30% extra compute to refresh.
- **Crediting the pretraining retriever for InstructRetro's gains.** Symptom: the downstream numbers are read as proof of RETRO-style retrieval. Downstream retrieval was DRAGON+ over task corpora, with the encoder switched off.
- **Handing the reader a near-duplicate of the answer.** Symptom: accuracy drops when the parent or old version sits in the prompt. ALCUNA's KD scores fell by 12 and 17 points for Vicuna and ChatGLM when the parent entity was added (Alpaca barely moved).
- **Treating retrieval-only-in-document as retrieval from a corpus.** Symptom: RPT's gains are cited for a web-scale index. Its index was the document's own earlier chunks.

---

## Try it

1. In the table at the top, which half is frozen in "Sequential, retriever first", and which row of the table does Izacard and Grave's reader-attention training fall under?
2. Run `knn_mix` with `lam=0.5` and temperature 0.25, then with `lam=0.0`. What does each do to the probability of `"30"`, and which paper says the temperature is worth tuning?
3. A joint retriever is updated every step. Why does a stored index go stale, and what did REALM do about it?
4. A candidate chunk gives the next chunk a log-probability of -47.0, and -45.5 given only the two preceding chunks. Is it a positive for RPT? What would the training signal be if you used BM25 rank instead?

<details>
<summary>Answers</summary>

1. The retriever is frozen and the LLM learns to use what it returns (RETRO's frozen BERT). Izacard and Grave fall under "Sequential, LLM first": the reader is fixed and its attention scores supervise the retriever.
2. At 0.25 the mix gives `"30"` 0.694, against 0.616 at temperature 1.0, because sharper weights favour the nearest neighbours. With `lam=0.0` the output equals the model's own 0.40. Xu et al. report that the temperature gap can reach 3.7% relative perplexity.
3. Each retriever update changes the embeddings, so the stored document vectors no longer match the query encoder. REALM ran a second job that re-embedded all 13M Wikipedia chunks about every 500 steps, and an index 30× staler dropped NQ dev EM from 38.2 to 28.7.
4. No. -47.0 minus -45.5 is -1.5, so the candidate made the next chunk less likely and falls outside the positives. Using BM25 rank would only reward lexical overlap, which is the RPT-Lex variant. RPT-Sem, trained on the LM-likelihood signal, did better on all four datasets.

</details>

---

## Interview checklist

| Question | Answer |
|---|---|
| What are the ways to train the two halves of RAG? | Training-free, independent, sequential (retriever first or LLM first) and joint. Most production RAG is training-free |
| How can a retriever learn without question–passage labels? | Izacard and Grave use the reader's cross-attention as the target. RPT uses a scoring LM's likelihood gain on the next chunk. Both need a decent starting retriever |
| What did REALM show about joint training? | The index goes stale as the retriever updates. A 30× staler index cut NQ dev EM from 38.2 to 28.7 |
| Why is kNN-LM's gain not all retrieval? | Xu et al.: a separate trained output matrix recovers about 55% of it, and the kNN softmax temperature changes results by up to 3.7% |
| What does InstructRetro show? | Retrofitting a 43B GPT with retrieval for 100B tokens, then instruction tuning, beat instruction-tuned GPT with RAG by 7% on average zero-shot. The gap on NQ was 38.9 against 37.0 |
| Does RETRO's multiplier carry over to QA? | No. It is a language-modelling result, and RETRO scored 45.5 EM on NQ against FiD's 51.4 |
| What does ALCUNA say about readers? | Few-shot models misuse in-context new knowledge, mostly when linking it to existing knowledge and when the parent entity is also in the prompt. It does not test a retriever |

---

## Next

[03 — Keyword, semantic and hybrid search](03-keyword-semantic-and-hybrid-search.md): what `retrieve()` actually does, with BM25, embeddings, hybrid fusion and how to measure a retriever.
