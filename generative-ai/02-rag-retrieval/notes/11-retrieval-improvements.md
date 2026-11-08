---
origin: curated  # was: notion-export
sources:
  - https://arxiv.org/abs/2602.03442
  - https://arxiv.org/abs/2401.15884
  # own work notes (production support-agent evaluation, anonymised)
  - https://arxiv.org/abs/2212.10496
  - https://arxiv.org/abs/2305.18290
  - https://arxiv.org/abs/2301.12652
  - https://arxiv.org/abs/2409.12941
  - https://arxiv.org/abs/2310.01352
  - https://arxiv.org/abs/2404.08189
  - https://arxiv.org/abs/2501.15228
  - https://arxiv.org/abs/2506.10380
  - https://arxiv.org/abs/2604.18509
  - https://arxiv.org/abs/2603.04384
  - https://arxiv.org/abs/2411.07396
  - https://arxiv.org/abs/2410.04343
  - https://arxiv.org/abs/2311.08377
  - https://arxiv.org/abs/2404.19705
  - https://arxiv.org/abs/2411.19443
  - https://arxiv.org/abs/2501.07391
  - https://arxiv.org/abs/2410.18050
  - Lakshmanan & Hapke, *Generative AI Design Patterns* (O'Reilly, 2025), ch. 4
confidence: medium
cleaned: 2026-11-01
---
# 11 — Retrieval improvements: reading an ablation

Tallybook's support bot still gets refund questions wrong, and everyone on the team has a favourite fix: a newer model, multi-query, HyDE, a corrective loop, fine-tuning. An ablation is how you stop arguing. You change one thing at a time, score each configuration on the same labelled queries, and let the table choose. The catch is that a small eval set can only tell you about big differences, and most of the table is noise until you prove otherwise.

This chapter works through a real ablation from a production support-agent evaluation, with its identity removed: five retrieval configurations scored on MRR, precision at 1 and latency, the conclusions drawn, and the shortlist of improvements that came out of it. Those numbers are measurements, but the raw data is not in this repository, so you can't re-run them here, and they did not come from Tallybook. Four systems appear. The **deterministic pipeline** retrieves once, reranks and generates. The **graph agent** is a LangGraph agent with CRAG. The **tool-loop agent** is a Google ADK ReAct agent that decides for itself what to search. The **incumbent** is the existing assistant, used as the benchmark. Each research item then gets a small experiment on Tallybook, so that you can see the mechanism run. Metric definitions are in [03](03-keyword-semantic-and-hybrid-search.md) and the wider evaluation discipline is in the [Eval pillar](../../08-eval/README.md).

These notes were written after the first ablation run, while the options were still being evaluated. Items marked planned or not measured below were never run on that system, and their expected gains are estimates, not results.

## The baseline table

The eval had 44 tasks, of which 32 carried annotated gold URLs. MRR and P@1 are measured against those.

| Config | MRR | P@1 | Latency |
|--------|-----|-----|---------|
| Incumbent benchmark | 0.625 | 0.625 | ~9.3s (smoke/10) |
| Tool-loop + thinking1024 | 0.583 | 0.531 | 7.3s |
| Graph + CRAG | 0.547 | 0.531 | 7.7s |
| Graph no CRAG | 0.542 | 0.531 | 4.4s ← best latency/quality tradeoff |
| Tool-loop baseline | 0.418 | 0.219 | 2.6s |

Gap to the incumbent: **-0.042 MRR** (best local against the benchmark, on the smoke subset). The benchmark's latency comes from a ten-task smoke run, so treat that row as a rough target, not a like-for-like score.

### What the ablations showed

- **Thinking budget (+1024)**: a large gain for the tool-loop agent (+0.165 MRR), but it hurts the graph agent when combined with CRAG. That is an interaction effect: thinking changes the citation style, which breaks CRAG's grading alignment.
- **CRAG**: +0.005 MRR against no CRAG, at a cost of +3.4s. The confidence gate (threshold 0.7) short-circuits most runs because Bedrock returns decent scores. Marginal value.
- **What the paper's CRAG is.** The ablation's CRAG is a re-implementation: a confidence gate on knowledge-base scores. Corrective RAG proper trains a small T5-large (0.77B) evaluator that labels each retrieved document correct, incorrect or ambiguous, then refines, replaces with web search, or does both. Its evaluator classified retrieval quality at 84.3 accuracy on PopQA, against 58.0 to 64.7 for prompted ChatGPT, and the correction raised PopQA accuracy from 52.8 to 59.8 on Self-RAG's LLaMA2-7B with the same retrievals. Every generator is a LLaMA2-7B variant, thresholds were tuned per dataset, and the reported overhead (0.363 s to 0.512 s per instance) leaves out retrieval and web search. So the paper does not contradict a marginal result here: the tested gains came from a weak retriever and a trained evaluator, which this system lacked ([arXiv:2401.15884](https://arxiv.org/abs/2401.15884), Yan et al., 2024-01, preprint).

- **LLM planner**: -0.031 MRR against the regex router, and +4s latency. The regex is better for that corpus's edge-case vocabulary.
- **The incumbent's advantage** has three plausible sources: (1) `gemini-3-flash-preview`, a newer model, (2) `ThinkingLevel.LOW` internally, and (3) multi-query retrieval before the KB call.

### How much of that is signal

Before believing any line above, ask how much a mean over 32 queries can move by chance. Reciprocal rank is a score between 0 and 1, and a bounded score has a standard deviation of at most 0.5, so the standard error of a mean over 32 queries is at most 0.088. The table also has a second reading. P@1 times 32 is a count of queries.

```python
import math

runs = {  # config: (MRR, P@1), scored on the 32 annotated queries
    "tool-loop + thinking1024": (0.583, 0.531),
    "graph + CRAG": (0.547, 0.531),
    "graph no CRAG": (0.542, 0.531),
    "tool-loop baseline": (0.418, 0.219),
}
n = 32
worst_se = 0.5 / math.sqrt(n)
print(f"worst-case standard error of one MRR: {worst_se:.3f}\n")
for name, (mrr, p1) in runs.items():
    print(f"{name:24s} MRR {mrr:.3f}  rank-1 hits {p1 * n:4.1f} of {n}")

print()
for label, delta in [("CRAG", 0.547 - 0.542), ("thinking on tool-loop", 0.583 - 0.418)]:
    print(f"{label:21s} delta {delta:+.3f} = {delta / worst_se:4.2f} worst-case SEs")
```

```text
worst-case standard error of one MRR: 0.088

tool-loop + thinking1024 MRR 0.583  rank-1 hits 17.0 of 32
graph + CRAG             MRR 0.547  rank-1 hits 17.0 of 32
graph no CRAG            MRR 0.542  rank-1 hits 17.0 of 32
tool-loop baseline       MRR 0.418  rank-1 hits  7.0 of 32

CRAG                  delta +0.005 = 0.06 worst-case SEs
thinking on tool-loop delta +0.165 = 1.87 worst-case SEs
```

So CRAG's +0.005 is about 6% of one worst-case standard error, and the two graph configurations put the same 17 queries' worth of answers at rank 1. "CRAG adds nothing measurable here" is the honest statement. It does not prove CRAG is useless on other corpora or with a stricter gate, and the 3.4 s it costs is measured, so the decision to drop it is easy. The thinking gain is a different size: ten extra queries at rank 1 and getting on for two worst-case errors.

This bound is pessimistic for comparisons, because the same queries go through both configurations and most of the per-query noise cancels. The tool that uses this is the paired bootstrap: compute the difference per query, resample queries, and look at the interval. Tallybook's practice kit has 20 labelled queries, so here are its real results for three real retrievers.

```python
import numpy as np
from ragkit import QUERIES, Retriever, reciprocal_rank

retriever = Retriever()


def per_query_rr(search):
    return np.array([reciprocal_rank(search(q, k=3), relevant) for q, relevant, _ in QUERIES])


def paired_bootstrap(a, b, rounds=10_000, seed=0):
    diff = a - b
    rng = np.random.default_rng(seed)
    means = diff[rng.integers(0, len(diff), (rounds, len(diff)))].mean(axis=1)
    return diff.mean(), *np.percentile(means, [2.5, 97.5])


bm25, dense, hybrid = (per_query_rr(s) for s in (retriever.sparse, retriever.dense, retriever.hybrid))
print(f"MRR: bm25 {bm25.mean():.3f}, dense {dense.mean():.3f}, hybrid {hybrid.mean():.3f}\n")
for name, a, b in [("dense - bm25", dense, bm25), ("hybrid - bm25", hybrid, bm25), ("dense - hybrid", dense, hybrid)]:
    delta, low, high = paired_bootstrap(a, b)
    print(f"{name:15s} {delta:+.3f}  95% interval [{low:+.3f}, {high:+.3f}]  "
          f"wins {(a > b).sum()}, losses {(a < b).sum()}, ties {(a == b).sum()}")
```

```text
MRR: bm25 0.550, dense 0.867, hybrid 0.733

dense - bm25    +0.317  95% interval [+0.042, +0.592]  wins 9, losses 3, ties 8
hybrid - bm25   +0.183  95% interval [+0.008, +0.367]  wins 8, losses 3, ties 9
dense - hybrid  +0.133  95% interval [-0.017, +0.292]  wins 6, losses 3, ties 11
```

These scores cut each ranking at 3, so they sit slightly below the kit's scoreboard. Read the last line. Dense beats hybrid by 0.133 MRR on these 20 queries, more than twenty times the CRAG delta, and the interval still crosses zero. Eleven of the twenty queries tie, and the difference is carried by the other nine. Keep this in mind as you read the expected gains below: an improvement of 0.05 on 32 queries needs a large change in a handful of queries, or a much larger eval set, before you can call it real.

## The research items

Each item below is one independent variable. The figure shows where each one enters the pipeline, which is also what you would toggle in an ablation.

```mermaid
flowchart LR
    Q[User question] --> P[planner]
    P --> MQ["multi_query<br/>item 2"]
    P --> HY["HyDE<br/>item 3, pipeline only"]
    MQ --> R["retrieve<br/>item 4: Bedrock KB or own pipeline"]
    HY --> R
    R --> A["answer<br/>item 1: model<br/>item 5: DPO"]
    A --> E[Score against gold URLs]
```

### 1. Upgrade the model: gemini-3-flash-preview

**Expected gain**: about +0.04 to +0.08 MRR. It was rated the biggest single lever because it needs no engineering, though that range overlaps the multi-query estimate below.
**Cost**: same latency profile, slightly higher per-token cost.
**How**: change the model setting in the agent's environment and rerun the same eval set.
**Status**: Not measured. The run needs the original agent code, Gemini API access and the gold URL set, and none of those is in this public repository, so the gain above stays an estimate. Item 4 reports a local ablation that is measured, on a different question.

Why does a model change move a *retrieval* metric? Because MRR here is scored on the URLs the agent cites, and the agent chooses what to search for and what to cite. It is a reminder that this table measures the whole agent, not the index.

A published case of the same lever: A-RAG's agent (keyword search, semantic search and a chunk-read tool) scored LLM-Acc 74.1 vs 52.8 for naive RAG on MuSiQue with GPT-5-mini (top-k 5, same model as judge), yet with GPT-4o-mini it led on only 3 of 5 public QA sets, so a gain measured on one model need not carry to another ([arXiv:2602.03442](https://arxiv.org/abs/2602.03442), Du et al., 2026-02, preprint).

### 2. Multi-query retrieval

**What**: generate 2 or 3 reformulated queries per user question, retrieve for each, merge and deduplicate results by URL, and pass the top N to the answer node. This matches the incumbent's internal strategy, which generates keyword phrases in the corpus's language before retrieval.

**Expected gain**: +0.05 to +0.10 MRR, especially on:

- Short or vague queries, where a single query has high lexical variance
- Abstract accounting terms, with the compound and spelling variants a non-English language adds
- Cross-lingual queries, such as a question in one language against an article in another

**Cost**: +1 LLM call for query generation and +N Bedrock calls, one per variant. No grading loop.
**In a graph agent**: a new node `multi_query` between `planner` and `retrieve`.

```python
# illustrative: needs a Gemini API key and your own graph State, prompt and parser.
# Sketch: generate_queries node
async def generate_queries_node(state: State) -> State:
    llm = ChatGoogleGenerativeAI(model=_MODEL, temperature=0.3)
    result = await llm.ainvoke([
        ("system", MULTI_QUERY_PROMPT),
        ("human", state["query"])
    ])
    queries = parse_queries(result.content)  # extract list of reformulations
    return {**state, "queries": [state["query"]] + queries[:2]}

# retrieve node runs bedrock_kb.retrieve for each query, merges
```

**In a tool-loop agent**: change the search tool to accept and execute multiple queries.

**Status**: Planned, not run. It would follow the model upgrade ablation.

[05](05-chunking-query-parsing-and-reranking.md) shows the idea on one Tallybook query. Here it runs across all ten paraphrase queries, where keyword search suffers most, so you can see the size of the effect and where it stops. The rewrites are hand-written stand-ins for what an LLM would produce, and they were written with the corpus in view, so read these as a best case.

```python
from ragkit import QUERIES, Retriever, evaluate, rrf

REWRITES = {  # stand-ins for the LLM call
    "can I get my money back": ["refund policy", "how do I get a refund for a payment"],
    "access denied even though my token is valid": ["API authentication error 403", "invalid API key forbidden"],
    "too many requests from my integration": ["API rate limit", "HTTP-429 retry"],
    "the bank link stopped updating": ["bank connection error", "bank feed sync failed"],
    "my client says the bill never arrived": ["invoice email not delivered", "invoice email bounced"],
    "how do I close my account": ["cancel subscription", "cancelling your subscription"],
    "tax for a company in Germany": ["VAT on EU sales", "reverse charge VAT"],
    "chase customers who have not paid": ["payment reminders", "overdue invoice reminder"],
    "swap credentials safely without downtime": ["rotate API keys", "rotating API keys"],
    "move to a cheaper subscription": ["change plan", "downgrade plan"],
}


def multi_query(search):
    def run(question, k=3):
        versions = [question] + REWRITES.get(question, [])
        return rrf([search(v, k=5) for v in versions])[:k]
    return run


retriever = Retriever()
paraphrases = [row for row in QUERIES if row[2] == "paraphrase"]
for name, search in [("bm25", retriever.sparse), ("dense", retriever.dense), ("hybrid", retriever.hybrid)]:
    one, many = evaluate(search, paraphrases), evaluate(multi_query(search), paraphrases)
    print(f"{name:7s} MRR {one['mrr']:.3f} -> {many['mrr']:.3f}   recall@3 {one['recall@3']:.2f} -> {many['recall@3']:.2f}")
```

```text
bm25    MRR 0.175 -> 0.850   recall@3 0.20 -> 0.90
dense   MRR 1.000 -> 0.950   recall@3 1.00 -> 1.00
hybrid  MRR 0.650 -> 0.950   recall@3 0.90 -> 1.00
```

Multi-query takes BM25 from nearly useless to good on these queries, and it fixes hybrid, whose MRR was being dragged down by BM25's confident wrong answers. It does nothing for dense retrieval, and in fact costs a little, because the kit's stand-in embedder already handles paraphrase and the extra versions only add rank noise. That is the general pattern to test for: the lever helps the component that has the vocabulary gap. Since the production system's Bedrock KB runs `HYBRID` search, it has a keyword half to help, which fits the estimate that it could be worth more than the CRAG loop.

Li et al.'s 74-run sweep of RAG settings gives an outside number for query expansion. On TruthfulQA and MMLU with Mistral-7B-Instruct and a 1K-article Wikipedia index, a Flan-T5-small keyword expansion with a wider first-stage filter moved TruthfulQA ROUGE-L from 23.86 to 24.09 at best, and left MMLU factuality flat (63.73 to 63.75 for the largest filter). Shrinking the retrieval stride to 1 token hurt (TruthfulQA MAUVE 41.80 against 72.92). Its best variant retrieved gold question and answer pairs from the evaluation set itself, so it is a few-shot result, not retrieval from an independent corpus ([arXiv:2501.07391](https://arxiv.org/abs/2501.07391), Li et al., 2025-01, preprint).

Returning parent paragraphs has a measured cost ([05](05-chunking-query-parsing-and-reranking.md#index-small-return-large)). The LongRAG of Zhao et al. (a different paper from the long-retrieval-unit LongRAG in [02](02-why-rag-and-the-augmented-prompt.md)) retrieves 200-word chunks, maps them back to their source paragraphs, then runs an LLM extractor and a chain-of-thought relevance filter. With ChatGLM3-6B tuned on 2,600 samples, the mapped paragraphs fed the generator 10,669 tokens against 2,181 for plain chunks on HotpotQA, and did not reliably beat them (2WikiMQA F1 44.83 against 46.61). On 2WikiMQA the extractor recovered the gain (52.53) and extractor plus filter reached 54.85, at 1,233 tokens on HotpotQA. The filter alone helped little. Average F1 over three multi-hop sets (200 questions each) was 52.56 for GLM-4 against 45.96 for its vanilla RAG. The corpus held each question's own paragraphs, so every needed passage was in it, and two or three extra LLM calls per query are not costed ([arXiv:2410.18050](https://arxiv.org/abs/2410.18050), Zhao et al., 2024-10, v2 2024-11, preprint).

FRAMES gives an outside number for the sequential version. Krishna et al. built 824 multi-hop Wikipedia questions that need 2 to 15 articles. With Gemini-1.5-Pro-0514 and BM25 over Wikipedia, accuracy was 0.408 with no retrieval, 0.474 with four BM25 articles in one step and 0.729 with the gold articles. Five rounds of five generated queries, ten documents each, with planning instructions (example query sequences, no repeated queries, think step by step) reached 0.66. Without the planning instructions it climbed only from about 0.45 to about 0.52 at two documents per query, because the model's queries lacked diversity and it never corrected course. The multi-step runs cost six sequential model calls, used one model and one retriever, and did not ablate the parts of the planning prompt ([arXiv:2409.12941](https://arxiv.org/abs/2409.12941), Krishna et al., NAACL 2025).

### 3. HyDE (Hypothetical Document Embeddings)

**What**: instead of embedding the user query, generate a hypothetical ideal article that answers it, embed that, and retrieve by similarity ([arXiv:2212.10496](https://arxiv.org/abs/2212.10496) (Gao et al., ACL 2023)). The paper built it for retrieval with no relevance labels: an unsupervised encoder (Contriever) matches the generated document against real ones, and the encoder's dense bottleneck is expected to drop the invented details. On TREC DL19 web search it took Contriever from 44.5 to 61.3 nDCG@10, level with the MS MARCO fine-tuned Contriever (62.1), with InstructGPT as the generator. With Flan-T5-XXL as the generator it reached only 48.9. It stayed behind the fine-tuned model on DL20, FiQA, DBPedia and Climate-FEVER and on all four Mr.TyDi languages tested, and on DL19 ANCE and DPR beat it on nDCG@10 though not on recall. Each dataset got its own written instruction, and the authors blame the FiQA and DBPedia gaps partly on under-specified instructions. Put on top of the fine-tuned Contriever it still added 5.3 points on DL19 (62.1 to 67.4) but 0.3 on DL20, and every result is a single run. The authors frame it as a cold-start tool: once labels exist, a supervised retriever takes the in-domain queries and HyDE keeps the novel ones. Here the hope is that it bridges the domain gap between customer support language (informal phrasing) and help centre language (formal structured articles).

**Why it works**: accounting queries use informal vocabulary ("fee", "do my VAT") while articles use formal terms ("VAT return", "filing with the tax authority"). A generated article written in the formal register should land closer to the real one. The paper does not test vocabulary mismatch directly, so this is the case to measure on our queries.

**Cost**: +1 LLM call to generate the hypothetical article, no retrieval loop. The paper's method averages the embeddings of N sampled documents, optionally with the query's (N is not reported), so its call count is unstated, and it never measures latency.
**Limitation**: the paper tests it only with dense retrieval, as in the deterministic pipeline. Whether Bedrock HYBRID search (BM25 plus vector) dilutes the benefit is untested, since BM25 is keyword-based.

**When the guess is the problem**: HyDE finds fine details "only when those details are in a domain (such as well-known history) in which the foundational model can generate a plausible answer"; a hallucinated, stale or off-topic guess loses the grounding. In one LlamaIndex demo a question retrieved at chunk size 100, failed at the 1,024 default, and HyDE recovered it (*Generative AI Design Patterns*, ch. 4, Pattern 9). One query, so run the ablation at the real chunk size.

**Best implementation path**: the deterministic pipeline's retrieval step, not the agents on Bedrock.

**When the caller is an agent, its reasoning is the free expansion.** AgentIR embeds the agent's current reasoning trace together with its search query, using a Qwen3-Embedding-4B retriever tuned on 5,238 instances from 250 correct trajectories. On BrowseComp-Plus (top 5 snippets, LLM-judge accuracy) with Tongyi-DR it scored 66.27% against 48.67% for the untuned backbone, 50.72% for Qwen3-Embedding-8B and 33.98% for BM25, and beat the backbone plus a Qwen3-8B listwise reranker (55.66%) with no reranking call. Embedding the reasoning without any tuning gave 55.54%, and tuning without reasoning 59.40%. A HyDE-style rewriter that did not see the agent's state (31.08%) fell below BM25 because it guessed wrong readings of ambiguous queries. Adding retrieved documents to the query hurt (60.00%), and so did extra history turns. One benchmark, a fixed corpus, no seeds; the transfer to gpt-oss-120B and GLM-4.7 was tested without retraining, but the tuning used one agent ([arXiv:2603.04384](https://arxiv.org/abs/2603.04384), Chen et al., 2026-03, preprint).

```python
# illustrative: needs an LLM, the multilingual-e5-large model and a DuckDB index.
# Sketch for a deterministic pipeline
async def hyde_retrieve(query: str) -> list[dict]:
    hyp = await generate_hypothetical_doc(query)   # LLM call
    hyp_embedding = embed(hyp)                      # multilingual-e5-large
    return vector_search(hyp_embedding)             # DuckDB ANN
```

**Status**: Planned, not run. The natural form is a `RETRIEVAL_MODE=hyde` flag on the pipeline, added after multi-query.

The gamble in HyDE is that the model guesses the corpus's vocabulary. Here is the same question with two hand-written hypothetical documents, one in the help centre's words and one in the customer's.

```python
from ragkit import Retriever

retriever = Retriever()
question = "can I get my money back"
good_guess = "Refunds are available for a set number of days after payment and go back to the original card."
bad_guess = "You can get your money back by asking your bank to return the charge on your card statement."

for label, text in [("question", question), ("good guess", good_guess), ("bad guess", bad_guess)]:
    print(f"{label:11s} bm25 {retriever.sparse(text, k=3)}  dense {retriever.dense(text, k=3)}")
```

```text
question    bm25 ['kb-03']  dense ['kb-04', 'kb-18', 'kb-05']
good guess  bm25 ['kb-04', 'kb-05', 'kb-11']  dense ['kb-04', 'kb-05', 'kb-18']
bad guess   bm25 ['kb-13', 'kb-17', 'kb-10']  dense ['kb-04', 'kb-18', 'kb-05']
```

Gold here is `kb-04`. The good guess repairs BM25, and the bad guess sends it to bank errors and webhooks. The stand-in embedder survives both, because its synonym axes were built by hand for this corpus, so don't read that as evidence about real embedders. A hypothetical document changes what the search sees, for better or worse, and nothing downstream knows which happened. That is why HyDE needs its own row in the ablation, and why it covers a different failure mode from multi-query: multi-query spreads the bet over several short phrasings, while HyDE places one long bet. The concern about hybrid dilution is untested. The toy above shows keyword search can benefit from a good guess, so measure it on the real corpus.

### 4. The deterministic pipeline as the retrieval backend for both agents

**What**: route all Bedrock KB calls through the pipeline's local DuckDB plus multilingual-e5-large endpoint.
**Why**: zero Bedrock cost, full control over the embedding model, and it enables HyDE.
**Flags**: one retrieval-backend setting per agent, so the swap needs no code change.
**Baseline**: the pipeline alone scored MRR=0.42 on retrieval-only. LLM agents with local RAG were not measured.

**Status**: Not measured, for the same reason as item 1: the agents, Bedrock KB and gold set are not in this repository, and LLM agents on local RAG remain an open question.

What can run here is the local half of the decision: which embedding model, and whether fusing it with BM25 helps. This does not answer the production question. It swaps embedders and not LLMs, has no agent in it, and scores Tallybook's 18 pages and 20 queries, not the production corpus. Every number below is from this run, with no API key. The first run downloads about 2.5 GB of weights.

```bash
cd generative-ai/02-rag-retrieval/practice && uv run ablation.py
```

```text
config                MRR    P@1    R@3  ms/query
bm25                0.562  0.500  0.600       0.0
toy dense           0.877  0.850  0.900       0.0
minilm-l6           0.854  0.750  0.950       0.8
bge-small           0.912  0.850  0.950       1.5
bge-base            0.875  0.750  1.000       3.7
e5-large            0.925  0.900  0.950      17.9
toy dense + bm25    0.742  0.550  0.950       0.1
minilm-l6 + bm25    0.835  0.750  0.900       0.7
bge-small + bm25    0.840  0.750  0.950       1.4
bge-base + bm25     0.840  0.750  0.950       3.6
e5-large + bm25     0.842  0.750  0.950      18.0

e5-large - bm25                +0.362  95% interval [+0.188, +0.550]  wins 9, losses 0, ties 11
bge-small - bm25               +0.350  95% interval [+0.175, +0.537]  wins 9, losses 0, ties 11
bge-base - bge-small           -0.037  95% interval [-0.138, +0.062]  wins 2, losses 3, ties 15
e5-large - bge-small           +0.013  95% interval [-0.075, +0.100]  wins 2, losses 2, ties 16
minilm-l6 - bge-small          -0.058  95% interval [-0.158, +0.042]  wins 1, losses 4, ties 15
bge-small + bm25 - bge-small   -0.073  95% interval [-0.181, +0.029]  wins 1, losses 5, ties 14
e5-large + bm25 - e5-large     -0.083  95% interval [-0.183, +0.000]  wins 0, losses 3, ties 17
toy dense - bge-small          -0.036  95% interval [-0.180, +0.104]  wins 2, losses 3, ties 15
```

Dense retrieval beats BM25 on this set by a margin the interval can resolve. Among the real embedders it can't: e5-large and bge-small tie on 16 of 20 queries, and the interval on their difference spans zero, while e5-large took about twelve times as long per query on this machine. Fusing BM25 lowered MRR for all four real models, presumably because BM25's much weaker list drags the fusion down. The two intervals printed for that comparison reach zero, so this is no evidence that hybrid helps on these queries, and not proof that it hurts. The toy row is a hand-built stand-in, so don't rank it against real models. None of this moves the production pipeline's MRR of 0.42, or says what it would become.

**How many passages to pass.** A controlled study held the reader fixed and varied only what retrieval handed it. With Mistral-7B-Instruct-v0.3, BGE-base and two-shot ALCE-style prompts on ASQA, exact-match recall climbed to 38.7 at k=10 (27.3 closed-book, 50.7 with only gold passages in the prompt) and then declined (32.8 at k=100), while citation precision fell from 63.7 at k=1 to 24.0 at k=100. Gold passages typically sat 7th to 13th among the nearest neighbours. Gold-document recall mattered far more than how exactly the ANN search matched exact search: setting the search recall@10 to 0.7 cost only 2-3% of gold-document recall (BGE-base, graph ANN). The authors assert the speed and memory benefit of loosening ANN recall but report no latency or memory numbers. Noise never helped here: gold plus 5th-10th neighbours scored 49.9 and gold plus 95th-100th neighbours 49.2 against 50.7 for gold only, so the study does not replicate the earlier "power of noise" claim. One run per condition, temperature 1, two 7B readers ([arXiv:2411.07396](https://arxiv.org/abs/2411.07396), Leto et al., 2024-11, preprint).

**More context only pays if the loop uses it.** Yue et al. scaled test-time compute for RAG with Gemini 1.5 Flash on four multi-hop sets (1.2k sampled questions each), counting input tokens only, from 16k to 5M effective tokens. Standard RAG plateaued by about 128k. DRAG (more documents and demonstrations in one call) won at 16k-32k, and IterDRAG (iterative sub-query retrieval and generation) won from 128k up. IterDRAG at 5M against standard RAG at 128k scored 76.9 against 48.4 accuracy on 2WikiMultiHopQA and 30.5 against 16.8 on MuSiQue, with gains shrinking beyond 1M. Adding documents beyond roughly 100 raised recall but not NDCG or MRR. Their fitted allocation model reached 96.6% of the oracle on held-out datasets at 1M tokens. One generator, single runs, and the abstract's "up to 58.9%" gain does not match any table cell we found ([arXiv:2410.04343](https://arxiv.org/abs/2410.04343), Yue et al., 2024-10, preprint).

The managed side of this comparison is [12](12-managed-rag.md).

### 5. DPO and preference fine-tuning

**What**: curate (query, good_response, bad_response) preference pairs from the eval set and fine-tune with Direct Preference Optimization ([arXiv:2305.18290](https://arxiv.org/abs/2305.18290) (Rafailov et al., 2023); the method is covered in the [RL pillar](../../05-RL/notes/03-preference-optimization.md)). Fine-tune one of:

- Query generation (retrieval query construction): prefer queries that lead to the gold URL
- Answer synthesis: prefer responses that cite the golden article

**Blocked on**: sufficient annotated golden responses (200+ preference pairs).
**Current state**: 32 annotated queries in the eval set, 0 golden responses stored.

**Path to unblock**:

1. Run comparable agent configs through your eval runner or Langfuse experiments, to identify tasks where some configs hit and others miss.
2. For hit tasks, take the incumbent's or the graph agent with thinking as preferred, and the tool-loop baseline as rejected.
3. Collect 200+ pairs before starting DPO.

**Status**: Blocked until golden responses have been collected.

The arithmetic says how blocked it is. A query yields a pair only when one config hits and another misses, so with five configs a query gives at most 2 × 3 = 6 pairs, and those six come from the same question.

```python
def pairs_from(hits_by_query, configs):
    pairs = []
    for query, hits in hits_by_query.items():
        for good in sorted(hits):
            for bad in sorted(set(configs) - hits):
                pairs.append((query, good, bad))
    return pairs


configs = ["incumbent", "loop_think", "graph_crag", "graph_plain", "loop_base"]
# Made-up hit pattern, to show the counting. Real patterns come from the ablation runs.
hits = {
    "query-1": {"incumbent", "loop_think"},
    "query-2": set(configs),               # everyone hits: no preference to learn
    "query-3": {"incumbent", "loop_think", "graph_crag"},
    "query-4": set(),                      # everyone misses: no preferred answer
}
pairs = pairs_from(hits, configs)
print(len(pairs), "pairs from", len(hits), "queries")
print(pairs[0])
print("ceiling for 32 queries and 5 configs:", 32 * 2 * 3)
```

```text
12 pairs from 4 queries
('query-1', 'incumbent', 'graph_crag')
ceiling for 32 queries and 5 configs: 192
```

Even a perfect split of every query stops short of 200, at 192, and real queries where everyone hits or everyone misses contribute nothing. So the blocker is more annotated queries, and more configs would not help much: pairs from one question are not independent examples.

A retriever can also be trained with no human preference pairs at all, by letting the generator score the documents. REPLUG keeps the language model frozen, prepends each of the top-k retrieved documents to the prompt in a separate pass, and ensembles the next-token probabilities weighted by retrieval score. REPLUG LSR then trains the retriever to match a distribution over the top 20 documents given by how much each one raised the model's likelihood of the gold continuation, so the labels are the model's own probabilities on 800K Pile sequences, with no annotator. With Codex (175B) and ten Wikipedia passages, that took 5-shot MMLU from 68.3 to 71.8 and 16-shot Natural Questions from 40.6 to 45.5. The untrained Contriever retriever already gave 71.4 and 44.7, so retrieval itself is most of the gain and the training adds about a point. The supervising model was the 6.7B Curie, and the same retriever was then used with the 175B models. Every prediction costs k forward passes, the ensemble needs per-token output probabilities, which chat APIs do not return, and retrieval is always on whether or not the question needs it, which the authors list as a limit ([arXiv:2301.12652](https://arxiv.org/abs/2301.12652), Shi et al., NAACL 2024). For Tallybook the practical reading is that once the eval set stores golden answers, the answer model's likelihood of each one under each retrieved page is a retriever label that costs no annotation, provided the model exposes log probabilities.

RA-DIT trains both halves. Lin et al. fine-tune the LLaMA 65B reader on instruction data with retrieved chunks, wrong ones included, so it learns to ignore a bad chunk, and then fine-tune only the query encoder of DRAGON+ on the reader's preferences, which leaves the document index untouched (on the six KILT dev tasks at 5-shot, updating the query encoder alone scored 57.8 against 55.8 for updating both). With ten chunks, the average over MMLU, NQ, TriviaQA and ELI5 rose from 43.1 to 50.5 at 0-shot and from 52.7 to 55.2 at 5-shot against REPLUG. The retriever's share is small: on the 5-shot dev tasks the average went from 53.8 (REPLUG) to 53.9 with only the reader tuned, 54.4 with only the retriever tuned and 54.6 with both. The larger effect is the reader's, at 0-shot: retrieval-augmented instruction tuning beat plain instruction tuning 51.0 to 47.7. A single multi-task RA-DIT 65B beat Atlas 11B fine-tuned per task by 4.1 points on eight tasks (60.9 against 56.8), though the sizes are not matched. It needs per-token probabilities, hand-written retrieval templates and LLaMA-1-era models ([arXiv:2310.01352](https://arxiv.org/abs/2310.01352), Lin et al., ICLR 2024).

MMOA-RAG goes further and trains the query rewriter, the document selector and the generator together with multi-agent PPO on one shared reward, the F1 of the final answer, with the retriever frozen. On HotpotQA, 2WikiMultihopQA and AmbigQA with Llama-3-8B-Instruct, Contriever and ten candidate passages, it beat the authors' re-implemented baselines by 1.8, 1.9 and 2.7 F1 (HotpotQA F1 48.29 against 46.49), and joint training added about 3.5 F1 on the multi-hop sets over the same modules after supervised warm-up alone (HotpotQA 44.69 to 48.29). The untrained model gained nothing from retrieval (HotpotQA F1 30.67 with documents against 31.18 without), so the supervised step comes first. The margin shrank to between -0.1 and +1.4 points (the negatives are on exact-match or accuracy columns) when the Contriever-trained system was tested with BGE or E5 retrievers, and the paper reports no seeds or variance. Training cost grows with the number of agents, and inference cost does not ([arXiv:2501.15228](https://arxiv.org/abs/2501.15228), Chen et al., NeurIPS 2025). For Tallybook this is a reason to keep each stage's output inspectable, not a recipe: it needs a training set of questions with gold answers, and the paper tests only Wikipedia QA.

**Tables are a retrieval target of their own.** TableRAG stores each table twice, as a database table with a schema and as Markdown in the text index, then loops: decompose the question, retrieve text chunks, run SQL only when a retrieved chunk came from a table, and reconcile the two answers. With LLM-judged accuracy (Qwen-2.5-72B judge, one run), on HybridQA tables over 100 cells it scored 47.87 to 48.52 across three backbones against 20.28 to 26.56 for plain RAG over linearised tables, while on the single-table WikiTQ plain RAG was close (82.60 against 84.62 with Claude-3.5). The paper's text says it has lower latency than a ReAct baseline, but its own latency table shows higher latency on every column (HeteQA 45.65 s against 24.57 s). The authors built both the HeteQA benchmark (304 questions over Wikipedia tables) and the method, and every backbone is a frontier model ([arXiv:2506.10380](https://arxiv.org/abs/2506.10380), Yu et al., 2025, preprint).

**Several filters can beat one judge.** MASS-RAG, training-free, runs three agents over the retrieved passages (a summariser, an extractor and a reasoner), then a synthesis agent merges their outputs. With Llama3-8B, Contriever and ten passages, it beat the single-judge-filter MAIN-RAG by 16.8 points on ARC-Challenge (78.7 against 61.9), 7.8 on ASQA exact match and 2.6 on TriviaQA, and tied on PopQA (64.2 against 64.0). MAIN-RAG's ASQA MAUVE was higher (70.6 against 55.2). Plain RAG with Qwen3-8B already scored 86.4 on ARC-C, so the gain is partly the backbone. By the authors' token-based estimate it costs about 4 agent-call units on ARC-Challenge and 7 on TriviaQA, PopQA and ASQA, which add an optional answer agent, and MAIN-RAG's rows are copied from its paper ([arXiv:2604.18509](https://arxiv.org/abs/2604.18509), Xiao et al., 2026, preprint).

**Filtering can be trained instead of prompted.** FILCO trains a context filter that keeps only the sentences supporting the answer, then fine-tunes the generator on the filtered text. With the top-1 DPR passage on six Wikipedia-based tasks, FLAN-T5 XL (3B) and LLaMA2 7B (LoRA), inputs shrank by 44-64%, NQ exact match rose 4.3 (FLAN-T5) and 8.6 (LLaMA2) over the full passage, FEVER accuracy 6.2 and 4.3, but HotpotQA only 1.0 and 1.3 F1; the average gain was 2.8 and 3.0 points. The best way to label "useful" differed by task (string inclusion for NQ and TriviaQA, lexical overlap for Wow, conditional mutual information for FEVER, HotpotQA and ELI5). Single runs, Wikipedia only, and a filter and generator both need training; the main results are published only as a chart ([arXiv:2311.08377](https://arxiv.org/abs/2311.08377), Wang et al., 2023-11, preprint).

**Learning when to retrieve.** ADAPT-LLM fine-tunes Llama-2 7B (LoRA) on NQ or SQuAD to emit a `<RET>` token where its own zero-shot answer was wrong, and only then fetches Contriever's top-1 passage. On PopQA exact match it scored 38.15% (SQuAD-trained) and 36.77% (NQ-trained) against 36.59% and 35.86% for always retrieving and 21-21.4% for never retrieving. The margin is under 1.6 points on one run, it asked for context on 82-84% of questions, and a popularity-threshold baseline that retrieves for 99.9% scored 36.81%, (a separate base-model re-run, 37.29 and 35.30 for ADAPT-LLM against it), so the evidence is "comparable accuracy", not a measured cost saving. Context hurt on the questions the model chose not to retrieve for (62.4% without against 55.7% with, NQ-trained), and the gold passage lifted accuracy far above top-1 retrieval (89.4% against 22.5% on SQuAD dev), so the retriever stayed the bottleneck ([arXiv:2404.19705](https://arxiv.org/abs/2404.19705), Labruna et al., 2024-04, preprint).

**Training the loop itself.** Auto-RAG fine-tunes Llama-3-8B-Instruct on 10k synthesized reasoning traces (from NQ and 2WikiMultiHopQA) so the model plans, extracts, rewrites the query and decides when to stop. With E5-base-v2 over Wikipedia it averaged 44.3 on six QA sets (a mix of exact match and F1) against 38.4 for IRCoT, 35.5 for Iter-RetGen, 33.8 for standard RAG, 30.7 for Self-RAG and 30.2 for FLARE (baselines are FlashRAG's published runs, not rerun). Dropping training gave 38.5, dropping the reasoning 35.3 and dropping zero-shot query refinement 41.9, and about 0.5k instructions were enough to learn the behaviour. Short-form Wikipedia QA, one 8B family, no learning rate, batch size or training seeds; the efficiency claim is only a bar chart ([arXiv:2411.19443](https://arxiv.org/abs/2411.19443), Yu et al., 2024-11, preprint). This is the trained counterpart of the corrective loop above.

**Retrieval can supply the valid names for structured output.** A generator can also be paired with a retriever of valid names. Béchard and Marquez Ayala generated JSON workflows at ServiceNow, and fine-tuned StarCoderBase generators invented step and table names as often as 21% of the time without a retriever. A 110M retriever (all-mpnet-base-v2, fine-tuned on about 15,000 step pairs) put valid names in the prompt, and hallucination fell below 7.5% for steps and 4.5% for tables at 1B to 15.5B. With it, a 3B model matched the 15.5B model without it on trigger exact match (0.615 against 0.632) and hallucinated 0.017 of steps against 0.160. Fine-tuning the retriever mattered more than size: step recall@15 went from 0.425 untuned to 0.743, while a 4.8B off-the-shelf encoder reached 0.561. On out-of-domain deployments, removing the suggestions from the same model raised hallucinated tables from 0.066 to 0.428. All of this is one proprietary task on 157 evaluation examples, with no variance reported and no comparison against grammar-constrained decoding ([arXiv:2404.08189](https://arxiv.org/abs/2404.08189), Béchard & Marquez Ayala, NAACL 2024 Industry Track).

## Priority order

1. **gemini-3-flash-preview ablation** (zero engineering, big expected gain)
2. **Deterministic pipeline as backend** (free latency and cost benchmark)
3. **Multi-query retrieval** (best quality lever after the model upgrade)
4. **HyDE on the pipeline** (complements multi-query, different failure mode coverage)
5. **DPO** (long-term, blocked on data collection)

The rule behind that order is cheap information first. Items 1 and 2 are configuration flags. Item 3 is a node. Item 4 needs item 2's backend. Item 5 needs data that does not exist yet.

## The deterministic pipeline's baseline and what it can't see

A smoke run of the pipeline used 10 tasks from the golden set, drawn from the 32 annotated:

| Metric | Score |
|---|---|
| MRR | 0.26 |
| P@1 | 0.22 |
| R@3 | 0.33 |
| NDCG@3 | 0.28 |

3 of 9 annotated tasks hit in the top 5. **2 misses are product glossary URLs that were never ingested, so this is a coverage gap, not a ranking error.** With those filtered, the effective score on ingested content is higher. Note also that this MRR of 0.26 on ten smoke tasks and the 0.42 quoted under item 4 come from different runs, which is why you record the query set with every score.

This eval loop uses a different retrieval path from the citation proxy: `query → retrieval endpoint → ranked chunks → compare URLs to golden set → P@k / MRR / NDCG`. The existing retrieval proxy measures citation sentiment on historical support conversations, and it can't measure ranked chunk quality.

### URL normalization

Every number in this chapter depends on deciding when two URLs are the same article.

**Design decision:** a URL map is a stateless lookup table committed to the repo. Agents never contain version-aware URL logic, so KB migrations (a help centre moving to a new domain, say) are a data operation, not a code redeploy. This keeps agents KB-agnostic and prevents grounding false positives when the underlying domain changes.

Match on path only (`/nl/articles/1001-...`) to avoid protocol and domain drift between `help.old-domain.example` and `help.new-domain.example`.

**Aliasing rules:**

1. Help-centre platform articles: extract the numeric ID from `/articles?/(\d+)`, which is locale-agnostic.
2. `help.old-domain.example ↔ help.new-domain.example`: same article ID, rewrite domain and locale prefix. `help.old-domain.example/en/articles/<id>-<slug>` → `help.new-domain.example/nl/articles/<id>-<slug>`.
3. Product glossary (`www.old-domain.example/wiki/<slug>/`): **no canonical URL on the new domain**. These are excluded from grounding and citation coverage, tagged as a topic proxy in the coverage check. Do NOT alias them. Tag `content_type: "glossary_term"` if they are ever ingested.

The rules fit in a few lines, and running them shows the effect on the smoke score's hit rate.

```python
import re

ARTICLE = re.compile(r"/articles?/(\d+)")


def canonical(url):
    """Stable key for an article, or None if the URL has no canonical article."""
    if "/wiki/" in url:
        return None
    match = ARTICLE.search(url)
    return f"article:{match.group(1)}" if match else url


def new_domain_url(url):
    match = re.search(r"help\.old-domain\.example/\w+/articles/(\d+[^/]*)", url)
    return f"https://help.new-domain.example/nl/articles/{match.group(1)}" if match else url


a = "https://help.old-domain.example/en/articles/1001-create-an-invoice"
b = "https://help.new-domain.example/nl/articles/1001-factuur-maken"
wiki = "https://www.old-domain.example/wiki/vat/"

print(canonical(a), canonical(b), canonical(a) == canonical(b))
print(new_domain_url(a))
print("wiki:", canonical(wiki))

hits, annotated, wiki_misses = 3, 9, 2
print(f"hit rate as scored {hits}/{annotated} = {hits / annotated:.2f}; "
      f"on ingested content {hits}/{annotated - wiki_misses} = {hits / (annotated - wiki_misses):.2f}")
```

```text
article:1001 article:1001 True
https://help.new-domain.example/nl/articles/1001-create-an-invoice
wiki: None
hit rate as scored 3/9 = 0.33; on ingested content 3/7 = 0.43
```

### The product glossary: never the primary retrieval target

The product glossary is a flat list of concepts with no numeric article IDs and no equivalent on the new domain. For `definition` queries it provides a context frame only, and the actual answer still comes from help centre articles. This is why glossary misses in eval results are **expected and correct**, not ranking failures. The source router in [10 — semantic cache](10-semantic-cache.md#source-routing--tier-2) encodes this: `definition` intent → glossary as context enrichment, plus the help centre for the answer.

## Pitfalls

- **Reading a table without a noise estimate.** A delta of 0.005 on 32 queries is nothing, and even 0.133 on 20 queries left an interval that crossed zero above. Compute the paired interval before writing the conclusion.
- **Changing two things at once.** Thinking helped the tool-loop agent and hurt the graph agent with CRAG. With thinking and CRAG turned on together, nobody could have seen that interaction.
- **Scoring a coverage gap as a ranking failure.** Two of the six pipeline misses were documents that were never indexed. No retriever improvement could ever fix those. Separate "not ingested" from "not found".
- **Comparing runs on different query sets.** The smoke subset and the full set gave very different MRRs for the same pipeline. Store the query-set version next to each score.
- **Trusting URL equality.** A domain migration can make every hit look like a miss, or a false alias can make a miss look like a hit. Normalize through one committed table.
- **Believing the expected gains.** They are estimates that justify an order of work. Replace them with measured rows as soon as a run finishes.
- **Fine-tuning before you have data.** Thirty-two questions' worth of preference pairs is not a training set, however many pairs you can derive from them.

## Try it

1. In the bootstrap block, change `seed=0` to `seed=1` and `rounds` to `1000`. How much does the `dense - hybrid` interval move, and does the conclusion change?
2. Using the worst-case bound, how many queries would you need for one standard error to equal CRAG's +0.005?
3. In the multi-query block, delete the second rewrite from every entry so that each question has one rewrite. What happens to BM25's MRR? Predict first.
4. What does `canonical` return for `https://help.new-domain.example/nl/article/1001` (singular path) and for `https://www.old-domain.example/pricing`? Is the second one what you want?

<details>
<summary>Answers</summary>

1. The interval becomes about [-0.008, +0.292] against [-0.017, +0.292]. It still crosses zero, so the conclusion stands. The lower end moved by 0.009, which is the size of error you accept with fewer rounds. The width comes from the 20 queries, and more rounds will not narrow it.
2. 0.5 / sqrt(n) = 0.005 gives n = 10,000. That is the unpaired worst case, and a paired design needs fewer, but it shows why a +0.005 can't be judged on 32 queries.
3. BM25's MRR falls from 0.850 to 0.667, and recall@3 stays at 0.90. One rewrite finds the document, but the original question's noisy ranking now carries a larger share of the fused score, so the right document lands lower. The second rewrite was buying rank, not recall.
4. The singular path still gives `article:1001`, which is why the pattern has `s?`. `https://www.old-domain.example/pricing` has no article ID, so it comes back unchanged and only matches itself. That is safe for a comparison, but it is also a sign that this URL needs a decision in the URL map. A URL on the other domain would not match, so domain drift is unhandled for non-article pages.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What is an ablation? | Change one component at a time, score each configuration on the same queries, and compare. It separates each change's effect and shows interactions. |
| Why was CRAG judged marginal? | +0.005 MRR and identical P@1 against no CRAG, for +3.4 s. The confidence gate at 0.7 short-circuited most runs. |
| What interaction did the ablation find? | A thinking budget gained +0.165 MRR on the tool-loop agent but hurt the graph agent with CRAG, because thinking changed citation style and broke the grader's alignment. |
| How would you judge a +0.03 MRR on 32 queries? | Not yet real. Worst-case SE of one mean is 0.088. Compute a paired bootstrap interval on per-query differences. |
| Why a paired test? | The same queries go through both systems, so per-query difficulty cancels and the comparison is tighter. |
| How does multi-query help, and what does it cost? | It covers lexical variance by retrieving for 2 or 3 reformulations and merging. Cost: one LLM call and one retrieval per variant. It helps keyword search most. |
| How does HyDE differ? | It embeds a generated hypothetical answer in place of the query. At least one LLM call, one long bet on the corpus's vocabulary. The paper tested it only with pure vector search. |
| Why did the LLM planner lose to a regex? | -0.031 MRR and +4 s. For a narrow edge-case vocabulary the rule was simply better, so test before assuming an LLM wins. |
| What is a coverage gap? | A gold document that was never indexed. It lowers scores and no ranker can fix it, so filter or report it separately. |
| Why keep URL mapping in a data file? | KB migrations become a data change, not a redeploy, and agents stay KB-agnostic. |
| Why not alias the product glossary? | It has no canonical article equivalent, so it is excluded from coverage. Definition queries use it for context only. |
| Why is DPO last? | It needs 200+ pairs and golden responses. 32 queries with 5 configs cap out at 192 correlated pairs, and none were stored. |

## Next

[12 — Managed RAG](12-managed-rag.md): the managed backend these experiments ran against, compared with Vertex AI Search and with a pipeline you run yourself.
