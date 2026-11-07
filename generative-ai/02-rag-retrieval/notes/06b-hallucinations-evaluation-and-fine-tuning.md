---
origin: synthesis  # split from 06-generation-for-rag.md (2026-11-07) so each part stays under the chapter length cap
sources:
  - https://www.deeplearning.ai/courses/retrieval-augmented-generation-rag/
  - https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG (Module 4, "LLMs and Text Generation", Assignment 4 "Fashion Forward Hub")
  - https://gradientscience.org/contextcite/ (ContextCite, cited by the course)
  - https://arxiv.org/abs/2204.06092
  - https://arxiv.org/abs/2305.14627
  - https://aclanthology.org/2024.naacl-industry.23/
  - https://arxiv.org/abs/2409.13741
  - https://arxiv.org/abs/2404.10198
  - https://arxiv.org/abs/2409.02897
  - https://arxiv.org/abs/2102.01454
  - https://arxiv.org/abs/2401.01313
  - https://arxiv.org/abs/2304.09848
  - https://arxiv.org/abs/2411.06037
  - https://arxiv.org/abs/2607.21627
  - https://arxiv.org/abs/2401.08406
  - https://arxiv.org/abs/2503.23513
  - https://arxiv.org/abs/2403.10131
  - https://arxiv.org/abs/2507.05714
  - https://arxiv.org/abs/2508.11386
  - Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 5, ch. 6
  - Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025), ch. 7
confidence: high
cleaned: 2026-11-07
---
# 6b — Hallucinations, evaluation and fine-tuning

Tallybook's retriever returns the refund page, the prompt says "answer only from the documents", and the bot still tells a customer they have 45 days. The document says 30. The answer even carries a citation, `[DOC 1]`, pointing at the right page. A grounded prompt lowers the odds of this and does not remove them. This part is about what happens after the prompt: the checks that catch an answer drifting from its evidence, the metrics that measure faithfulness, the workflows that split one call into several, and when fine-tuning belongs beside retrieval.

> The LLM half of RAG, part two. [06](06-generation-for-rag.md) covered attention, sampling, model choice and the grounded prompt. Here: hallucinations and citations, RAGAS and judge-free metrics, agentic workflows, and RAG against fine-tuning. RAG adds knowledge; fine-tuning changes behaviour.

---

## Hallucinations and citations

The course's example: a support bot asked "Do you offer student discounts?" invents one, because a discount is the probable answer.

| Defence | How | Cost / limit |
|---|---|---|
| Self-consistency | Sample several answers; distrust disagreement | Multiplies cost |
| Grounding via system prompt | "Answer only from the documents; say if you don't know" | Cheap; not a guarantee |
| **Citations** | Number documents, require `[1]`, `[2]` after claims | Citations themselves can be hallucinated |
| ContextCite | Attributes each statement to the context spans that caused it | Research tool; extra compute |
| ALCE benchmark | Scores citation quality, correctness and fluency; an NLI model (T5-11B) checks that each sentence's cited passages entail it | Mainly for evaluating systems. Its own best-of-4 rerank used the scorer at generation time and raised ChatGPT's ASQA citation recall from 73.6 to 84.8 (one seed). Human raters saw a smaller gain, 74.7 to 79.3, because the scorer was grading its own pick. Cost: 4 generations plus the NLI pass |

The grounding prompt is weakest exactly when retrieval misses. In a banking-QA study (GPT-4, GPT-3.5 and Llama-2, two document sets, 800 queries each), the models kept answering when the gold passage was absent, with loosely related context or with invention. The authors call this *pseudo-helpfulness*. Nine prompt variants (verbose, quote-first, citation-required) made no salient difference to answer quality ([Zhao et al., NAACL 2024 Industry](https://aclanthology.org/2024.naacl-industry.23/), 2024-06). Catch missing evidence upstream, in the retriever and in evaluation, rather than with more prompt wording.

**Copied numbers are reliable; inferences from them are not.** In DataGemma, a fine-tuned Gemma 2 (9B or 27B) writes Data Commons queries, and the retrieved tables go to Gemini 1.5 Pro. On the authors' synthetic query set those tables averaged 38K tokens per prompt. Statistical claims copied from the tables were 98.6–98.9% accurate. Claims *inferred* from them were right only 71.9–76.4% of the time, wrong 6–20% of the time (a country missing from a top 5) and unsubstantiated 4–22% of the time ("a median age of 35 indicates many young families"). The base model without retrieval made statistical claims on 9% of 101 queries, and only 39% of them were accurate. Two other caveats apply. Data Commons had an answer for only 24–29% of queries, and the authors' own team graded most of the 101 hand-written queries ([arXiv:2409.13741](https://arxiv.org/abs/2409.13741) (Radhakrishnan et al., 2024-09)). So check derived claims (rankings, comparisons, interpretations) separately from quoted ones. A citation to the table doesn't make the conclusion drawn from it correct.
Joren et al. call this *sufficient context*: whether the context can answer the question, labelled by an autorater without the gold answer. At 6,000 tokens only 44.6% (Musique) to 77.4% (FreshQA) of contexts were sufficient. Models hallucinated even with sufficient context (3.2% Claude 3.5 Sonnet to 25.4% Gemma 27B) yet were right 35 to 62% of the time without it. Abstaining on low sufficiency plus confidence raised accuracy on answered questions 2 to 10%; QA only ([arXiv:2411.06037](https://arxiv.org/abs/2411.06037), Joren et al., ICLR 2025).

**Context against the model's prior.** A second failure runs the other way: the evidence is there and the model overrides it. Raieli and Iuculano summarise Wu et al. ([arXiv:2404.10198](https://arxiv.org/abs/2404.10198)) with a dosage example. The model learned 20 µg as a drug's maximum dose. Given a context that says 30, it answers 30; given one that says 100, it falls back to 20. The further the context departs from the prior, the more the model trusts itself (*Building AI Agents*, ch. 6). The book adds that larger models do so more than smaller ones, but the paper itself reports no such size effect; its measured numbers are in [02](02-why-rag-and-the-augmented-prompt.md#what-rag-buys-you). Prompt strength shifts the balance. In the paper's comparison of a standard, a loose and a strict prompt, the strict one, which tells the model to rely on the context, pushes the model toward the context and the loose one toward its prior. Whether you want that depends on how far you trust your corpus over the model. The same chapter names *negative rejection* as the matching retrieval failure: when nothing relevant is found, the model answers anyway. Its other causes of hallucination are training that rewards long outputs, which makes models verbose, and high sampling temperature (*Building AI Agents*, ch. 5).

Training can install the same failure. Cao et al. trained a two-module pipeline (query generator, then a Qwen2.5-3B reader over a fixed term-matching retriever) end to end with REINFORCE on final-answer reward only. On 176 HotpotQA yes/no questions, accuracy rose while the share of answers that followed a swapped-in passage fell **from 0.86 to 0.54, close to the 0.506 of a reader that ignores passages**. Given an unrelated passage, the trained reader still answered 0.19 correctly from memory, against 0.03 for one trained with their Role Anchor penalty, which holds the module's role-prompt preference near its pre-training value. The anchor cost 0.067 accuracy (0.447 against 0.380). This is one small study (models of 0.5–7B, 3 seeds, no real corpus update), and the anchor needs log-probabilities and trainable weights, so it does not apply to an API model ([arXiv:2607.21627](https://arxiv.org/abs/2607.21627), Cao et al., 2026-07, preprint). The test carries over without the training, though: swap in a passage that implies the opposite answer and check that the answer flips.

Mitigations come in layers. A survey of over thirty techniques sorts them by when they act: before generation (retrieval, clarifying questions), during it (sentence-level verification, since one hallucinated sentence raises the odds of the next), after it (post-editing against retrieved evidence, as RARR does), and in training (refusal-aware tuning such as R-Tuning). It names Context-Aware Decoding, which contrasts output probabilities with and without the context, as a training-free counter to the prior-overrides-context failure above. The survey runs no experiments of its own and reports almost no numbers, so read it as a map and take any figure from the method's own paper, and it stops at late 2023 ([arXiv:2401.01313](https://arxiv.org/abs/2401.01313), Tonmoy et al., 2024-01, preprint).

**Citations are only as honest as their plumbing.** Rothman's research agent builds citations the robust way, with a weak spot (*Context Engineering for MAS*, ch. 7):

1. Every chunk is upserted with `"source": doc_name` in its metadata, so each retrieved chunk knows its file.
2. After generation, the agent appends a `**Sources:**` list programmatically from the retrieved chunks' metadata, instead of trusting the LLM to name them.

The weak spot is in the book's own trace. Asked about the Juno mission, the answer cites `[1]` and lists both `juno_mission_overview.txt` and `perseverance_rover_tools.txt`. The Perseverance file was retrieved but contributed nothing. Appending every retrieved source records what the model saw, not what it used. Citation is not attribution. ALCE measured the gap: ChatGPT answering closed-book and attaching citations afterwards scored 26.7 citation recall on ASQA, against 73.6 when it wrote from the retrieved passages. Its answers were about as correct (38.3 vs 40.4 exact-match recall) but rarely matched any passage. Even then, about half of ChatGPT's and GPT-4's ELI5 answers were not fully supported by what they cited ([arXiv:2305.14627](https://arxiv.org/abs/2305.14627), Gao et al., EMNLP 2023; 2023 models, top-5 passages). For attribution you need per-claim matching, such as ContextCite above or the fuzzy citation matching Raieli and Iuculano describe, which matches the response against the chunks with n-gram TF-IDF (*Building AI Agents*, ch. 6).

The gap is measured in production-style products too. Human annotators audited four commercial generative search engines (Bing Chat, NeevaAI, perplexity.ai, YouChat; 1,450 queries each, early 2023). Averaged over the four, only **51.5% of sentences were fully supported by their citations (recall) and 74.5% of citations supported their sentence (precision)**. Recall ranged from 68.7 (perplexity.ai) to 11.1 (YouChat), and precision correlated with perceived utility at r = -0.96, across only four systems, so treat that as a hint: the authors suspect systems that copy their cited page earn precision but answer less. Verifiability is not factuality; a supported sentence can still be false ([arXiv:2304.09848](https://arxiv.org/abs/2304.09848), Liu et al., Findings of EMNLP 2023).

Granularity and the single pass matter too. LongCite asked models to answer and cite in one pass over a long context (LongBench-Cite, GPT-4o as judge). GPT-4o's citations averaged 220 tokens, about six sentences, and proprietary models reached citation F1 of only about 0.5 on two datasets. In-context citing cut answer correctness to 88% of the no-citation level for GPT-4o. The paper's CoF pipeline (post-hoc: answer first, then retrieve and extract sentence-level citations), run with GLM-4, kept correctness at 100% with F1 65.8; simpler post-hoc variants scored 57 to 63. Fine-tuning Llama-3.1-8B and GLM-4-9B on 44.6k such examples gave F1 72.0 and 69.2 at citation lengths of 85 and 91 tokens, and correctness rose to 107% and 109%. Synthetic data, a GPT-4o judge and 128k-token contexts, not retrieval ([arXiv:2409.02897](https://arxiv.org/abs/2409.02897), Zhang et al., 2024-09, preprint).

Three of these checks cost no model call, so run them on every answer. Does each `[DOC n]` exist? Does each claim have one? Does every number in the answer appear in the cited text? The answers below stand in for model output, and the third has the error from the opening of this chapter:

```python
import re
from ragkit import DOC_BY_ID

docs = [DOC_BY_ID["kb-04"], DOC_BY_ID["kb-06"]]         # [DOC 1], [DOC 2]

def check_answer(answer, docs):
    problems = []
    for sentence in re.split(r"(?<=[.\]])\s+(?!\[)", answer.strip()):
        cited = [int(n) for n in re.findall(r"\[DOC (\d+)\]", sentence)]
        if not cited:
            problems.append(f"no citation: {sentence!r}")
        for n in cited:
            if n > len(docs):
                problems.append(f"no such document: [DOC {n}]")
        text = " ".join(docs[n - 1].full for n in cited if n <= len(docs))
        for number in re.findall(r"\d+", re.sub(r"\[DOC \d+\]", "", sentence)):
            if cited and number not in text:
                problems.append(f"number {number} not in cited text")
    return problems or ["ok"]

print(check_answer("Annual plans are refundable within 30 days. [DOC 1]", docs))
print(check_answer("Annual plans are refundable within 30 days. [DOC 7]", docs))
print(check_answer("Annual plans are refundable within 45 days. [DOC 1]", docs))
print(check_answer("Refunds are usually quick.", docs))
```

```text
['ok']
['no such document: [DOC 7]', 'number 30 not in cited text']
['number 45 not in cited text']
["no citation: 'Refunds are usually quick.'"]
```

Each check covers one failure and misses others. It can't tell that a sentence reasons badly from a correct number, which is DataGemma's inferred-claim problem, so an LLM judge still has a job to do.

To get closer to attribution without another LLM call, match each answer sentence to the chunk it most resembles. This is a small version of the fuzzy matching Raieli and Iuculano describe, with character n-gram TF-IDF. Two documents were retrieved and the answer used one:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ragkit import DOC_BY_ID

retrieved = ["kb-04", "kb-02"]
answer = ["Annual plans can be refunded within 30 days of payment.",
          "The money reaches the original card in 5 to 10 working days."]

vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
matrix = vectorizer.fit_transform([DOC_BY_ID[i].full for i in retrieved] + answer)
scores = cosine_similarity(matrix[len(retrieved):], matrix[:len(retrieved)])

for sentence, row in zip(answer, scores):
    print(f"{retrieved[row.argmax()]}  {row.max():.2f}  {sentence}")
print("appended by a naive Sources list:", retrieved)
print("actually matched:", sorted({retrieved[row.argmax()] for row in scores}))
```

```text
kb-04  0.57  Annual plans can be refunded within 30 days of payment.
kb-04  0.37  The money reaches the original card in 5 to 10 working days.
appended by a naive Sources list: ['kb-04', 'kb-02']
actually matched: ['kb-04']
```

Rothman's negative-result test is worth copying. With only Juno and Perseverance documents loaded, ask for a story about the Apollo 11 landing. A grounded system replies that the provided documents do not contain this information, rather than writing the story from the model's memory. Keep a few such out-of-corpus questions in every regression set.

---

## Evaluating the generator: RAGAS

| Metric | How it is computed | What it misses |
|---|---|---|
| **Response relevancy** | An evaluator LLM writes several prompts that *could* have produced the response; embed them and the real prompt; average cosine | Does not check facts |
| **Faithfulness** | An LLM extracts every factual claim in the response, then checks each against the retrieved docs; share supported | Depends on judge quality |
| Others | Noise sensitivity, citation metrics, context precision/recall | All lean on LLM-as-judge |

Raieli and Iuculano add a few metrics in the same family (*Building AI Agents*, ch. 5). **Context entities recall** is the share of entities in the ground-truth answer that appear in the retrieved context; it suits fact-heavy domains. **Summarization score** asks whether the answer keeps the context's important information. **Fluency** scores individual sentences and **coherence** the response as a whole.

Long answers can also be scored without an LLM judge. ASQA's questions are ambiguous ("who ruled France in 1830?"), and a good answer covers every reading. Its DR score runs a SQuAD v2-trained RoBERTa reader over the answer to see which disambiguated questions it can answer (Disambig-F1), then takes the geometric mean with ROUGE-L, so pasting a long passage or writing fluent filler can't max it alone. On 45 dev questions DR tracked the authors' own pairwise judgments at 95.0 Pearson, against 86.4 for ROUGE-L alone and 92.9 for Disambig-F1 alone (not a significant difference). A T5-large reader on 5 JPR passages scored 32.1 DR, against 40.6 for humans who searched Wikipedia themselves and 61.8 for humans handed the disambiguations (the paper's upper bound). Its Disambig-F1 also fell further behind the passages it read as K grew, so the generator lost information it had been given ([arXiv:2204.06092](https://arxiv.org/abs/2204.06092), Stelmakh et al., EMNLP 2022). Its Disambig-F1 half measures recall only: an answer that adds a hallucinated reading keeps its Disambig-F1 and is penalised only indirectly, through ROUGE-L and a confused reader. The correlation rests on six systems.

ALCE's fluency column is MAUVE, which scores a whole set of outputs, not one answer. It embeds the model's texts and human texts with GPT-2 large, clusters them together with k-means, and measures how far apart the two cluster histograms are. On open-ended web-text continuation by eight GPT-2 settings, it rank-correlated 0.952 with crowdworkers' judgments of which text was more human-like, against 0.810 for generation perplexity ([arXiv:2102.01454](https://arxiv.org/abs/2102.01454), Pillutla et al., NeurIPS 2021). Only the ranking is stable. The absolute value moves with the number of clusters, the embedding model and the sample size, and small samples inflate it. It never checks facts. ALCE's own shortcut test shows the gap: answering with the first two sentences of the top retrieved passage scored 67.2 MAUVE on ASQA (and 98.7 citation recall), against 66.6 for ChatGPT reading five passages, at 18.9 exact-match recall instead of 40.4 ([arXiv:2305.14627](https://arxiv.org/abs/2305.14627), Gao et al., EMNLP 2023, Table 11). ALCE's authors use MAUVE mainly as a sanity check, because it is sensitive to output length and style.

Measure indirectly too: thumbs up/down and A/B tests that change only the LLM, so you capture its effect alone. The RAGAS paper is in `sources/` (arXiv 2309.15217); see [references](../references.md).

---

## Agentic RAG

One LLM call can be split into several specialised ones. The course's support-bot flowchart:

| Step | Model | Job |
|---|---|---|
| Router | Small | Does this prompt need retrieval at all? |
| Retriever | — | Fetch candidates |
| Evaluator | Small | Are these documents relevant? |
| Generator | Large | Write the answer from the augmented prompt |
| Citation | Specialised | Attach sources |

| Workflow shape | Pattern |
|---|---|
| Sequential | parser → rewriter → retriever → generator → citation |
| Conditional | Router picks one branch |
| Iterative | Writer and evaluator loop N times |
| Parallel | Orchestrator fans out; synthesiser merges |

Build simple ones by hand; reach for a framework as they grow. These are Anthropic's *Building Effective Agents* shapes; the house treatment is [ai-engineering 05 — graph vs loop](../../../ai-engineering/05-graph-engineering/notes/01-graph-vs-loop.md) and [01 § agentic vs single-pass](01b-index-structures-and-agentic-rag.md#agentic-vs-single-pass-li-experiment-3-9).

Assignment 4 builds exactly this for a clothing store ("Fashion Forward Hub"):

```python
# illustrative: needs the assignment's helpers, a Together API key and embedded Weaviate
def answer_query(query: str) -> dict:
    label = check_if_faq_or_product(query)          # router, max_tokens=1, temperature=0
    if label not in ("FAQ", "Product"):             # router failed: answer from history
        return {"role": "assistant",
                "prompt": f"User provided a question that does not fit FAQ or Product "
                          f"related questions. Answer it based on the context you already "
                          f"have so far. Query provided by the user: {query}"}
    if label == "FAQ":
        return query_on_faq(query)                  # FAQ pairs in the prompt
    try:
        # decide_task_nature → get_params_for_task (technical 0.3/0.7, creative 1.0/0.9)
        # → LLM extracts metadata (gender, articleType, baseColour, season, usage, price)
        # → Weaviate filters on it → product prompt
        return query_on_products(query)
    except Exception:
        return {"role": "assistant", "prompt": "…Instruct them to rephrase it…"}
```

The metadata step is query parsing (note [05](05-chunking-query-parsing-and-reranking.md)) done with structured output: the LLM sees the allowed values for each field and returns JSON that becomes a Weaviate filter.

The control flow matters more than the model, and it runs without one. Here is a router for Tallybook that sends questions to the retriever or to smalltalk and treats a bad label as an event, with a stand-in for the small classifier:

```python
from ragkit import Retriever

retriever = Retriever()
ALLOWED = {"HELP", "SMALLTALK"}

def classify(query):                     # stand-in for a one-token LLM call
    if "weather" in query:
        return "Sure! I think"           # what a small model can really return
    return "SMALLTALK" if query.lower().startswith(("hi", "thanks")) else "HELP"

def answer_query(query):
    label = classify(query).strip()
    if label not in ALLOWED:             # never let a bad label pick a branch
        return {"route": "fallback", "docs": []}
    if label == "SMALLTALK":
        return {"route": "smalltalk", "docs": []}
    return {"route": "retrieval", "docs": retriever.hybrid(query, k=2)}

for q in ["thanks, that fixed it", "how do I rotate an API key", "what's the weather"]:
    print(f"{q:<30}", answer_query(q))
```

```text
thanks, that fixed it          {'route': 'smalltalk', 'docs': []}
how do I rotate an API key     {'route': 'retrieval', 'docs': ['kb-01', 'kb-02']}
what's the weather             {'route': 'fallback', 'docs': []}
```

---

## RAG vs fine-tuning

| | RAG | Fine-tuning |
|---|---|---|
| Changes | The prompt | The weights |
| Good for | **Knowledge**: facts, private data, freshness | **Behaviour**: domain style, format, tone, task skill |
| Update cost | Re-index documents | Retrain |
| Citations | Natural | None |

Fine-tuning changes how the model talks, not reliably what it knows. Microsoft's agriculture study is the measured version. On 273 expert-curated Washington-state farming questions, graded by GPT-4 against a rubric, LoRA fine-tuning GPT-4 on generated Q&A raised accuracy from 75% to 81%, and RAG added 5 points on top (86%). But fine-tuning Llama2-13B base dropped it below the off-the-shelf chat model (68% vs 76%), and RAG did more for fully correct answers than fine-tuning did (GPT-4: 36% → 60% with RAG, 45% fine-tuned) ([arXiv:2401.08406](https://arxiv.org/abs/2401.08406), Balaguer et al., 2024-01). Use RAG for knowledge, fine-tuning for domain adaptation, and both when you need both. "Both" can also mean fine-tuning with the retrieved documents in the prompt and masked from the loss, so the model learns to reason over them. RARE did this with reasoning traces distilled from QwQ-32B. Llama-3.1-8B reached 84.1% on MedQA, against 83.0% for the same model fine-tuned and then given RAG at inference, and 73.5% with RAG alone ([arXiv:2503.23513](https://arxiv.org/abs/2503.23513), Wang et al., KDD 2026).

The recipe both build on is RAFT's. It trains with one golden document among four distractors and a chain-of-thought answer that quotes the golden one. That took LLaMA2-7B to 74.0 on HuggingFace APIBench, where the same model fine-tuned without documents fell from 61.1 to 42.6 once documents were added at test time ([arXiv:2403.10131](https://arxiv.org/abs/2403.10131), Zhang et al., 2024-03, preprint). HIRAG asks which reading skill the training data teaches. It trains on three tasks in order, each with its own thought format: filtering (quote and cite the passage that answers), combining (relate several passages) and reasoning (chain facts across them, with the model's own knowledge where documents fall short). With total data held constant on Llama3-8B, the filtering-only mix scored 48.0 on RGB's information-integration test. Adding combination data raised it to 58.0, and the chosen 1:2:2 mix reached 66.0, while noise robustness stayed at 94–97 throughout. **Distractor training teaches the model to ignore noise, and only combination and reasoning data teach it to merge sources.** The tuned 8B scored 66.6 on PopQA against 67.2 for Llama3-70B-Instruct, but stayed behind GPT-4o-mini on MuSiQue (27.8 against 37.7). About 120K examples were synthesised by GPT-4-class models, and training took about 32 hours on 8 A100s. The authors fixed errors in RGB and share the corrected set only on request, every number is a single run, and the cited quotes are never scored for accuracy. They also concede the model does worse when documents help without containing the answer ([arXiv:2507.05714](https://arxiv.org/abs/2507.05714), Jiao et al. (AntGroup), 2025-07, v3 2025-09, preprint).

Model size decides how much the tuning adds. The Turing Institute's t0 models follow the s1 recipe (Muennighoff et al., 2025): fine-tune on about 2,000 DeepSeek-R1 reasoning traces written over the top 5 retrieved documents. On 1,000 synthetic NHS symptom queries over 989 condition pages, Qwen2.5-32B-Instruct named the right condition 0.38 of the time without retrieval and 0.54 with it. The tuned 32B reached 0.56, level with GPT-4o and DeepSeek-R1, so at 32B **retrieval supplied almost all of the gain and the tuning about 2 points**, around two standard deviations. Smaller tuned models held the level (0.53 at 1.5B, 0.56 at 3B). The authors credit the reasoning training for most of that, but the untuned small models with retrieval appear only in a figure. Retrieval set the ceiling: with 5 documents, the right page was in the context for only 76% of queries. Indexing LLM-written summaries instead of full pages raised precision@5 from 0.68 to 0.76 and cut training examples from 74,641 to 7,544 tokens. The queries were written by GPT-4o, and only some were reviewed by a clinician. Hallucination and faithfulness are never measured ([arXiv:2508.11386](https://arxiv.org/abs/2508.11386), Chan et al. (Alan Turing Institute), 2025-08, preprint).

Raieli and Iuculano's examples by task (*Building AI Agents*, ch. 5). Specialised summarization depends on understanding the domain, so fine-tune. Question answering needs transparency and low hallucination more than customisation, so use RAG. Code generation needs both a changing codebase and close task adaptation, so use both. "Both" can also mean fine-tuning the embedder rather than the LLM. That is far cheaper than training an embedder, and when labelled pairs are scarce, an LLM can generate synthetic (query, positive, negative) data for it ([03 § how embedders are trained](03-keyword-semantic-and-hybrid-search.md#how-embedders-are-trained-and-where-cosine-misleads)). Fine-tuning in depth: [01-llm-fundamentals](../../01-llm-fundamentals/README.md) (training and adapting) and [05-RL](../../05-RL/README.md) (preference tuning).

---

## Rules of thumb

| Rule | Why |
|---|---|
| Tell the model to cite and to say "not in the documents" | Cheapest hallucination defence |
| Check citations and numbers in code on every answer | No model call, catches whole classes of failure |
| Measure faithfulness, not only relevancy | A relevant answer can still be invented |
| Small models for routers and evaluators | They run on every request |
| RAG for knowledge, fine-tuning for behaviour | Facts change; format and tone don't |

---

## Labs

| Lab | Label |
|---|---|
| M4 Assignment 4 (Fashion Forward Hub chatbot) ([upstream](https://github.com/MohammadWasiq0786/Deeplearning.ai-RAG)) | needs Together API key + embedded Weaviate; not copied |

---

## Pitfalls

- **Assuming a grounding prompt handles missing evidence.** Symptom: confident answers to questions the corpus can't answer. Zhao et al.'s nine prompt variants made no salient difference, so test with out-of-corpus questions and handle them upstream.
- **Treating citations as attribution.** Symptom: every answer lists sources, and some contributed nothing (Rothman's Juno trace). Match claims to chunks if you need to know what was used.
- **Trusting a number because it has a citation.** Symptom: rankings and comparisons are wrong while quotes are right. DataGemma's inferred claims ran 71.9–76.4% against 98.6–98.9% for copied ones. Check derived claims separately.
- **Unvalidated router output.** Symptom: a stray label sends a query down the wrong branch silently. Validate against an allowed set and have an explicit fallback.
- **Fine-tuning to teach facts.** Symptom: costly retraining and stale answers. Fine-tune for behaviour and use RAG for knowledge. Balaguer et al. saw fine-tuning Llama2-13B land below the off-the-shelf chat model.
- **Trusting one LLM judge.** Symptom: faithfulness scores move when only the judge model changes. RAGAS faithfulness and relevancy both depend on the evaluator; pin the judge, and spot-check its verdicts against a labelled sample.

---

## Try it

1. Add `"Annual plans are refundable within 30 days, which is the longest in the industry. [DOC 1]"` to `check_answer`. What does it report, and is that right?
2. A hallucination appears in 3% of answers, and your faithfulness score says 0.97. List two cheaper checks you'd run before adding a second LLM judge.
3. Your corpus is Tallybook's help centre, which changes weekly, and the bot's tone is too formal. Which of the two problems is a fine-tuning job, and which is retrieval's?

<details>
<summary>Answers</summary>

1. It reports `['ok']`, and that's wrong. "Longest in the industry" is an unsupported claim attached to a correct number and a real citation. Regex checks catch mechanical failures only, which is why claim-level judging exists.
2. Citation existence and number containment, as in the block above, plus a regression set of out-of-corpus questions that must return "not in the documents". They catch whole classes of failure on every request at almost no cost.
3. The tone is behaviour, so fine-tuning (or a prompt) fixes it. The weekly-changing policy is knowledge, so it stays in retrieval, where an update is a re-index and not a retrain. Balaguer et al. found the two add up rather than compete.

</details>

---

## Interview checklist

| Question | Answer |
|---|---|
| Why can a model still ignore good context? | Its weights can pull harder than the context. Wu et al. show that the further a context departs from the model's prior, the more it trusts itself. |
| What is pseudo-helpfulness? | Zhao et al.'s term for models answering when the gold passage is absent, using loosely related context or invention. Nine prompt variants made no salient difference. |
| Are citations proof of attribution? | No. Appending all retrieved sources records what the model saw. Per-claim matching such as ContextCite records what it used. |
| What do RAGAS relevancy and faithfulness measure? | Relevancy: generate prompts that could have produced the answer and compare with the real prompt. Faithfulness: the share of extracted claims supported by the documents. Both lean on an LLM judge. |
| RAG or fine-tuning? | RAG for knowledge and freshness, fine-tuning for behaviour and format. Balaguer et al.: GPT-4 went 75% → 81% fine-tuned and 86% with RAG on top. RARE trains with retrieved documents in the prompt to get both. |
| When do you split one call into a workflow? | When small steps such as routing and relevance checks can run on a cheap model, or the task needs branches or loops. Start simple and validate each output. |
| What can a no-LLM check catch, and what does it miss? | Missing or invalid `[DOC n]` ids, uncited claims, and numbers absent from the cited text. It misses unsupported claims attached to a correct number, which still need a judge. |

---

## Next

[07 — RAG in production](07-rag-in-production.md): the system works on a laptop. Now evaluate it with traces, cut its cost and latency, secure it, and extend it to images and PDFs.
