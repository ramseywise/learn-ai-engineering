# MCQ Bank — Full Topic Parity

Multiple-choice drill bank covering all 11 guide topics. Standalone: it re-covers
ground the role-specific banks handle so it works on its own.

**How to use**: cover the answer key, take a section, then read the rationale for every
question you got wrong *and* every one you guessed right. The distractors are built from
the specific confusions each guide flags — a lucky guess teaches nothing.

**Sourcing**: questions are grounded in `../../guides/` — the numbers, ladders and
terminology are the guides' own, so a wrong answer points at a specific section to reread.
Where a guide explicitly warns that interviewers conflate two things (prefix vs semantic
caching, pass@k vs pass^k, CRAG vs Self-RAG), the bank tests that pair directly.

| Section | Topic | Questions |
|---|---|---|
| A | Programming (Python, DSA, SQL, concurrency) | 20 |
| B | ML foundations | 16 |
| C | LLM fundamentals | 23 |
| D | RAG | 22 |
| E | Agents | 20 |
| F | Context & cost | 16 |
| G | Evals & observability | 18 |
| H | Security & safety | 18 |
| I | Data engineering & MLOps | 14 |
| J | System design | 15 |
| K | Product & delivery | 12 |
| **Total** | | **194** |

Answer keys are at the end of each section.

---

## A. Programming (20 questions)

### A1
A Python service runs four threads doing pure CPU-bound numeric work on an 8-core
machine. Throughput is no better than single-threaded. Why?

A. The threads are deadlocking on a shared lock
B. The GIL allows only one thread to execute Python bytecode at a time
C. Four threads is too few to saturate 8 cores
D. Thread creation overhead dominates the workload

### A2
Which change gives *true parallelism* for that CPU-bound Python workload?

A. Switch to `asyncio`
B. Increase the thread count to 8
C. Switch to `multiprocessing`
D. Release the GIL with a `threading.Lock`

### A3
What does async programming provide in Python?

A. Parallel execution across CPU cores
B. Concurrency, not parallel execution
C. Automatic GIL release for CPU work
D. Thread-safe access to shared mutable state

### A4
Inside an `async def` handler, which call is the classic pitfall that stalls every other
coroutine on the loop?

A. `await httpx.AsyncClient().get(url)`
B. `await asyncio.sleep(1)`
C. `requests.get(url)`
D. `await asyncio.gather(*tasks)`

### A5
A race condition arises when:

A. Two processes read the same immutable tuple
B. Multiple threads modify shared data simultaneously
C. An async task is awaited twice
D. A thread is starved by the scheduler

### A6
Which is *not* one of the three standard fixes for a race condition?

A. Locks/mutexes (`threading.Lock`)
B. Immutable data structures
C. Avoiding shared mutable state
D. Increasing the thread pool size

### A7
You need `popleft()` in a BFS inner loop. Why `collections.deque` over a list?

A. `deque` uses less memory per element
B. `deque` popleft is O(1); list popleft is O(n)
C. `deque` is thread-safe and lists are not
D. Lists cannot pop from the front

### A8
Sorting an array first, then applying two pointers, typically changes brute force from:

A. O(n log n) → O(n)
B. O(n²) → O(n log n)
C. O(n³) → O(n²)
D. O(2ⁿ) → O(n²)

### A9
Which traversal of a binary search tree yields values in sorted order?

A. Preorder (root → left → right)
B. Inorder (left → root → right)
C. Postorder (left → right → root)
D. Level-order (BFS)

### A10
How do you correctly validate a BST?

A. Check each node is greater than its immediate parent
B. Check each node's left child < node < right child, locally
C. Pass min/max bounds down the recursion
D. Inorder traverse and check the root is the median

### A11
After Floyd's fast/slow pointers meet inside a cycle, how do you find the cycle's start?

A. Continue advancing the fast pointer at speed 2
B. Reset one pointer to head, then advance both at speed 1
C. Reset both pointers to head and advance at speeds 1 and 2 again
D. Count the cycle length, then advance that many steps from head

### A12
Union-Find with path compression and union by rank costs, per operation:

A. O(log n)
B. O(α(n))
C. O(1) worst case
D. O(n) amortized

### A13
Which pair of conditions signals a dynamic-programming problem?

A. Sorted input + a monotonic predicate
B. Optimal substructure + overlapping subproblems
C. A recursive definition + a base case
D. Greedy choice property + matroid structure

### A14
Top-down memoization vs bottom-up tabulation:

A. Top-down is better for large inputs; bottom-up is easier to reason about
B. Top-down is easier to reason about; bottom-up is better for large inputs and space optimization
C. They have identical time and space profiles
D. Bottom-up always uses less time; top-down always uses less space

### A15
`WHERE` and `HAVING` differ how?

A. `WHERE` filters groups after aggregation; `HAVING` filters rows before
B. `WHERE` filters rows before grouping; `HAVING` filters groups after aggregating
C. They are interchangeable in a `GROUP BY` query
D. `HAVING` works only with `COUNT`

### A16
`ROW_NUMBER`, `RANK`, `DENSE_RANK` on tied values:

A. All three assign the same rank to ties
B. `ROW_NUMBER` no ties; `RANK` ties then skips; `DENSE_RANK` ties then does not skip
C. `ROW_NUMBER` ties then skips; `RANK` no ties; `DENSE_RANK` ties without skipping
D. `RANK` and `DENSE_RANK` are aliases; only `ROW_NUMBER` differs

### A17
The canonical "keep the latest row per user" idiom is:

A. `SELECT DISTINCT ON (user_id) ... ORDER BY created_at`
B. `GROUP BY user_id HAVING created_at = MAX(created_at)`
C. `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC)` then `WHERE rn = 1`
D. `SELECT user_id, MAX(created_at)` joined back on both columns

### A18
A `LEFT JOIN` returns more rows than the left table has. What happened?

A. The join key is null in some left rows
B. The right table has duplicate join keys — fan-out
C. `LEFT JOIN` always returns at least as many rows as the right table
D. The query needs `SELECT DISTINCT`

### A19
State the GIL's effect directly: what does it constrain?

A. It prevents a process from spawning child processes
B. It allows threads to execute Python bytecode in true parallel
C. It limits execution of Python bytecode to one thread at a time
D. It improves CPU-bound performance by pinning threads to cores

### A20
Multithreading in Python is the right tool for:

A. CPU-bound tasks only
B. I/O-bound tasks
C. Anything parallelizable — it is always worth trying
D. Math-heavy numerical workloads

**Answers A**: A1-B · A2-C · A3-B · A4-C · A5-B · A6-D · A7-B · A8-B · A9-B · A10-C ·
A11-B · A12-B · A13-B · A14-B · A15-B · A16-B · A17-C · A18-B · A19-C · A20-B

**Rationale notes**
- **A4**: `requests.get` is synchronous — it blocks the event loop. The fix is `httpx`
  or another async client. Forgotten `await` and CPU-heavy work in a coroutine are the
  other two named pitfalls.
- **A10**: The local check (B) wrongly accepts a node deeper in the left subtree that
  exceeds the root. Bounds must be threaded down.
- **A18**: Row count equals the left table only when the join key is unique on the
  right. Ask "how many rows does this join produce?" before running it.
- **A19/A20**: The GIL constrains *bytecode execution*, not the interpreter as a whole —
  which is exactly why threads still help for I/O. A blocking socket or file read
  releases the GIL while it waits, so other threads run. CPU work never yields it, so
  threads serialize (A1) and `multiprocessing` is the fix (A2). "Whenever possible" is
  the trap answer: threads add lock and shared-state hazards for no CPU gain.

---

## B. ML foundations (16 questions)

### B1
The guide calls one thing "the #1 practical sin" in applied ML. It is:

A. Overfitting the validation set
B. Data leakage
C. Choosing the wrong model family
D. Failing to tune hyperparameters

### B2
Which practice does *not* prevent leakage?

A. Fitting scalers and encoders on the training split only
B. Splitting before any target-aware transform
C. Using time-based splits for temporal data
D. Averaging cross-validation scores across more folds

### B3
Under heavy class imbalance, which is more informative?

A. ROC-AUC, because it is threshold-independent
B. PR-AUC, because it focuses on the positive class
C. Accuracy, with a tuned threshold
D. R², because it handles skew

### B4
The interview move the guide says to make first when discussing any model result:

A. Report the cross-validated standard deviation
B. Name the naive baseline (majority class / mean predictor)
C. State the model family and its hyperparameters
D. Show the confusion matrix

### B5
L1 vs L2 regularization:

A. L1 shrinkage, L2 sparsity
B. L1 sparsity (feature selection), L2 shrinkage
C. Both produce sparsity; L2 is just faster
D. L1 applies to trees, L2 to linear models

### B6
Why gradient boosting over a neural net on tabular data? The guide names four reasons —
which is *not* one?

A. Sample efficiency
B. Native missing/categorical handling
C. Guaranteed convexity of the loss surface
D. Less tuning, plus interpretability tooling

### B7
PCA vs UMAP:

A. PCA preserves neighborhood structure; UMAP preserves linear variance
B. PCA is linear variance; UMAP is neighborhood structure, and is "for looking, not for
   downstream features without care"
C. Both are linear; UMAP is just faster
D. UMAP is deterministic; PCA is stochastic

### B8
Covariate drift vs concept drift:

A. Covariate = the input distribution shifts; concept = the input→target relationship shifts
B. Covariate = the target relationship shifts; concept = the inputs shift
C. Both describe label noise increasing over time
D. Covariate applies to classification, concept to regression

### B9
Model is excellent offline, poor in production. The guide gives an ordered checklist.
What do you check *first*?

A. Drift
B. Leakage
C. Feedback loops
D. Whether the eval metric matches the business metric

### B10
Which metric pair correctly captures outlier sensitivity in regression?

A. MAE penalizes outliers more than RMSE
B. RMSE penalizes outliers more than MAE
C. Both are equally sensitive; only R² differs
D. MAPE is the most outlier-robust choice

### B11
MAPE's specific pitfall:

A. It is undefined for negative predictions
B. It blows up near zero actuals
C. It cannot be averaged across series
D. It requires normally distributed residuals

### B12
Calibration means:

A. The model's ranking is correct
B. The predicted probabilities mean what they say
C. The decision threshold is tuned to maximize F1
D. Features are standardized before training

### B13
Which tools assess calibration?

A. Silhouette score and elbow plots
B. Brier score and reliability curves
C. SHAP values and permutation importance
D. Precision@K and MRR

### B14
"Hidden Technical Debt in Machine Learning Systems" (NIPS 2015) names which failure modes?

A. Overfitting, underfitting, and leakage
B. Entanglement, feedback loops, pipeline jungles
C. Drift, staleness, and skew
D. Bias, variance, and irreducible error

### B15
From Ng's "Structuring ML Projects", human-level performance is used as:

A. A hard ceiling the model must not exceed
B. A proxy for Bayes error
C. The threshold for shipping
D. The baseline for the naive predictor

### B16
Choosing K in k-means, the honest senior answer adds what to elbow/silhouette?

A. The Bayesian information criterion
B. That K encodes a product decision — how many segments can ops actually act on
C. That K should equal the number of features
D. That K should be tuned against downstream AUC only

**Answers B**: B1-B · B2-D · B3-B · B4-B · B5-B · B6-C · B7-B · B8-A · B9-B · B10-B ·
B11-B · B12-B · B13-B · B14-B · B15-B · B16-B

**Rationale notes**
- **B9**: The order is load-bearing: leakage → train/serve skew → drift → survivorship →
  feedback loops → metric mismatch. Leakage is both most common and cheapest to check.
- **B6**: Neural nets win with huge data or mixed modalities; convexity is not a GBM property.

---

## C. LLM fundamentals (23 questions)

### C1
Scaled dot-product attention is:

A. `softmax(QKᵀ/d)V`
B. `softmax(QKᵀ/√d)V`
C. `softmax(QᵀK/√d)V`
D. `softmax(QKᵀ)V/√d`

### C2
Why divide by √d?

A. To normalize the output to unit length
B. To prevent softmax saturating in high dimensions
C. To make the operation numerically invertible
D. To match the residual stream scale

### C3
Self-attention's O(n²) cost is the stated reason for which *pair*?

A. Hallucination and reward hacking
B. Long-context expense and "context rot"
C. Tokenization drift and multilingual inflation
D. Catastrophic forgetting and mode collapse

### C4
Which is *not* a named way to inject positional information?

A. Learned positional embeddings
B. RoPE
C. ALiBi
D. Layer normalization

### C5
A decoder-only model (GPT family) is characterized by:

A. Bidirectional attention over the full sequence
B. A causal mask
C. Cross-attention to an encoder stack
D. Masked-token prediction as its objective

### C6
The KV cache is described as the mechanism underneath:

A. Speculative decoding
B. Prompt caching
C. Quantization
D. Mixture-of-experts routing

### C7
Even at temperature 0, production output isn't fully deterministic. Named causes:

A. Tokenizer drift, prompt truncation, retry logic
B. Batching, floating point, MoE routing
C. Sampling seeds, top-p, top-k
D. Load balancing, caching, streaming

### C8
Prefill vs decode:

A. Prefill is sequential and expensive per token; decode is parallel and cheap
B. Prefill is parallel and cheap per token; decode is sequential and expensive
C. Both are parallel; decode is just longer
D. Prefill dominates cost in long-output workloads

### C9
Given C8, which discipline follows directly?

A. Larger batch sizes
B. Output-length discipline and streaming
C. Higher temperature for diversity
D. Longer system prompts to amortize setup

### C10
Speculative decoding is primarily:

A. A memory-reduction technique
B. A latency technique
C. A quality-improvement technique
D. A training-efficiency technique

### C11
RLHF's characteristic failure mode:

A. Catastrophic forgetting
B. Reward hacking
C. Mode collapse to the base model
D. Gradient explosion

### C12
DPO differs from RLHF how?

A. It uses different data — ratings instead of preference pairs
B. It skips the reward model and optimizes preference pairs directly
C. It requires an on-policy RL loop with PPO
D. It only works on models under 7B parameters

### C13
DPO's stated trade-off:

A. Trades stability for controllability
B. Trades some controllability for stability
C. Trades cost for alignment quality
D. Trades data efficiency for compute

### C14
Constitutional AI / RLAIF replaces human labels with:

A. Synthetic preference pairs sampled at random
B. AI feedback guided by principles, via a critique-and-revise loop
C. A larger reward model
D. Rule-based filters at inference time

### C15
Where does the adaptation ladder place LoRA?

A. Before RAG, since it is cheaper
B. After RAG, before full fine-tuning
C. After full fine-tuning, as a compression step
D. Outside the ladder — it is a serving optimization

### C16
QLoRA is:

A. LoRA with quantized adapter weights
B. LoRA with a quantized base model
C. Quantization applied after a LoRA merge
D. A quantization-aware training method

### C17
LoRA trains roughly what share of parameters?

A. ~0.001–0.01%
B. ~0.1–1%
C. ~5–10%
D. ~25%

### C18
For an API-only model where you cannot touch weights, preference data goes into:

A. A local reward model
B. Prompts and evals
C. A fine-tuning endpoint
D. The KV cache

### C19
"Lost in the middle" describes:

A. Truncation of the middle of a long prompt by the tokenizer
B. Attention dilution over long contexts
C. Retrieval returning mid-ranked documents
D. Positional embeddings failing past their trained length

### C20
The guide's stated mitigation for long-context degradation:

A. Bigger context windows
B. Context engineering, not bigger windows
C. Lower temperature
D. More attention heads

### C21
The `temperature` parameter controls:

A. The maximum token length of the response
B. The randomness of the model's output
C. The speed of inference
D. The size of the model being served

### C22
The main benefit of chain-of-thought prompting is that it:

A. Reduces token usage
B. Eliminates hallucination completely
C. Improves reasoning by breaking a problem into intermediate steps
D. Speeds up inference

### C23
For most tasks, the recommended number of few-shot examples is:

A. 0–1
B. 2–5
C. 5–10
D. 10+

**Answers C**: C1-B · C2-B · C3-B · C4-D · C5-B · C6-B · C7-B · C8-B · C9-B · C10-B ·
C11-B · C12-B · C13-B · C14-B · C15-B · C16-B · C17-B · C18-B · C19-B · C20-B ·
C21-B · C22-C · C23-B

**Rationale notes**
- **C8** is a favorite reversal. Prefill processes the whole prompt in parallel; decode
  emits one token at a time. That asymmetry is why output tokens cost more.
- **C12/C13**: DPO and RLHF consume the *same* preference data. The difference is no
  reward model and no RL loop — "the common industry default now."
- **C15**: The ladder is prompting → few-shot → RAG → PEFT/LoRA → full fine-tune,
  ordered cheapest and least invasive first. They compose.
- **C21**: Temperature scales the logits before sampling — low values concentrate mass on
  the top tokens, high values flatten the distribution. It is not a length, latency, or
  capacity control. Note the interaction with **C7**: temperature 0 removes *sampling*
  randomness but not nondeterminism from batching, floating point, and MoE routing.
- **C22**: CoT buys reasoning quality by spending intermediate tokens — so it *raises*
  token usage and latency, which is why A and D are inverted traps. It reduces reasoning
  errors; it does not eliminate hallucination (C), since a fluent wrong chain is still
  wrong. Pairs with the **C15** ladder: it is a prompting-tier move, tried before RAG or
  fine-tuning.
- **C23**: 2–5 is the working default. Below that the format is underspecified; past
  ~5 you pay context on every call for diminishing gains, and the model starts copying
  surface patterns of the examples rather than the task. If more examples keep helping,
  that is the signal to climb the **C15** ladder to retrieval or fine-tuning.

---

## D. RAG (22 questions)

### D1
The canonical pipeline, with optional stages in parentheses:

A. Ingest → embed → chunk → index; query → retrieve → generate
B. Ingest → chunk → embed → index; query → (rewrite) → retrieve → (rerank) → generate → (verify)
C. Chunk → ingest → index → embed; query → rerank → retrieve → generate
D. Ingest → chunk → index → embed; query → retrieve → (verify) → generate

### D2
Chunking priority order:

A. Fixed-size windows, then semantic splitting as a refinement
B. Document structure (headings) first, then recursive paragraph/sentence boundaries, to a token budget
C. Semantic chunking first, falling back to fixed windows
D. Sentence-level always, merged upward to fill the budget

### D3
The guide's stance on semantic chunking:

A. The recommended default for production corpora
B. Expensive at ingest and inconsistent — not the default
C. Required whenever documents lack headings
D. Equivalent to recursive splitting but faster

### D4
Typical chunk token budget and overlap:

A. ~256 tokens, ~32 overlap
B. ~512 tokens, ~64 overlap
C. ~1024 tokens, ~128 overlap
D. ~2048 tokens, ~256 overlap

### D5
Parent/child chunking means:

A. Index large chunks, generate from extracted sentences
B. Index small chunks, generate from their parent
C. Duplicate each chunk at two granularities in the same index
D. Chunk by document hierarchy only

### D6
A `min_tokens` filter at ingest can cause which silent failure?

A. Oversized chunks are truncated mid-sentence
B. Short-but-valid sections (one-line FAQ answers) are dropped from the index entirely
C. Embeddings drift toward the corpus mean
D. BM25 scores become incomparable with cosine

### D7
E5-family embedding models require:

A. L2-normalized inputs
B. `"query: "` / `"passage: "` prefixes
C. Lowercased text
D. A fixed 512-token pad

### D8
Violating that rule costs roughly:

A. 2–3% recall
B. 5–8% recall
C. 15–20% recall
D. 40%+ recall

### D9
Vector-only search and BM25-only search fail in which way?

A. Vector misses paraphrases; BM25 misses exact tokens
B. Vector misses exact tokens (product names, error codes); BM25 misses paraphrases
C. Both miss exact tokens; only reranking recovers them
D. Vector misses short queries; BM25 misses long ones

### D10
Reciprocal Rank Fusion uses which constant?

A. k = 10
B. k = 60
C. k = 100
D. k is tuned per corpus

### D11
Why RRF instead of a weighted sum of BM25 and cosine scores?

A. RRF is provably optimal for hit rate
B. BM25 and cosine scores have incomparable distributions; rank fusion is parameter-free
C. RRF is faster to compute
D. Weighted sums require normalized embeddings

### D12
In the guide's measured ladder, hybrid + cross-encoder reranking reached what hit rate,
from a dense-only baseline of 45%?

A. 55%
B. 58%
C. 68%
D. 80%

### D13
CRAG vs Self-RAG, in one line:

A. CRAG decides inside the LLM during generation; Self-RAG decides in the graph topology
B. CRAG decides in the graph topology before generation; Self-RAG decides inside the LLM during generation
C. Both decide before generation; CRAG adds a retry
D. Both decide during generation; Self-RAG adds a grader

### D14
Self-RAG's canonical mechanism (Asai et al.):

A. LLM-driven query expansion into N paraphrases
B. Reflection tokens (`[Retrieve]`, `[IsRel]`, `[IsSup]`) emitted mid-generation
C. A confidence gate on retrieved chunks with fallback
D. Entity-graph traversal alongside vector search

### D15
Some blogs use "Self-RAG" to mean LLM query expansion. In an interview you should:

A. Use the blog definition, since it is more common
B. Surface the ambiguity and name the canonical version — that itself scores
C. Avoid the term entirely
D. Correct the interviewer firmly and move on

### D16
HyDE works by:

A. Embedding the question and expanding with synonyms
B. Generating a hypothetical answer and embedding *that* for search
C. Retrieving twice and fusing the ranks
D. Reranking with a cross-encoder on hypothetical pairs

### D17
HyDE's cost:

A. Roughly doubles total pipeline latency
B. One extra small-model call, ~100–200ms
C. Negligible — it reuses the main generation call
D. One extra embedding call only

### D18
Multi-query (RAG-Fusion) recall gain and its diminishing-returns point:

A. +5%, past 2 variants
B. +10–15%, past 3 variants
C. +20–25%, past 5 variants
D. +30%, past 10 variants

### D19
GraphRAG restraint — the guide's caution:

A. GraphRAG is always preferable for enterprise corpora
B. It is overkill for factual lookup; for wiki-shaped corpora existing link structure already gives a traversable graph
C. It should replace vector search once entity extraction is available
D. It only works with proprietary graph databases

### D20
Debugging poor retrieval, what do you measure *first*?

A. Whether the LLM prompt includes the retrieved context
B. recall@k on a golden set
C. Cross-encoder reranker latency
D. Chunk overlap settings

### D21
RAGAS's four standard metrics:

A. precision, recall, F1, accuracy
B. faithfulness, answer_relevancy, context_precision, context_recall
C. groundedness, hallucination rate, MRR, nDCG
D. hit rate, coverage, calibration, naturalness

### D22
Which is *not* one of the three named cases for skipping RAG?

A. Stable narrow knowledge that fits the context window
B. Latency-critical paths
C. Poor-quality corpora
D. Corpora larger than 1M documents

**Answers D**: D1-B · D2-B · D3-B · D4-B · D5-B · D6-B · D7-B · D8-C · D9-B · D10-B ·
D11-B · D12-C · D13-B · D14-B · D15-B · D16-B · D17-B · D18-B · D19-B · D20-B ·
D21-B · D22-D

**Rationale notes**
- **D12**: The full ladder is dense 45% → BM25 50% → hybrid RRF 58% → hybrid +
  cross-encoder 68%. Cross-encoder reranking is "the single highest-leverage add-on."
  Cite numbers like this — measured claims beat vibes.
- **D20**: The order matters — golden-set recall@k, then embedding/corpus language match,
  prefix rules, chunk truncation, *then* hybrid + reranker, all before touching the LLM.
- **D22**: Scale is a reason to change the index (ANN/HNSW), not to abandon RAG.

---

## E. Agents (20 questions)

### E1
Anthropic's distinction between workflows and agents:

A. Workflows use one model call; agents use many
B. Workflows orchestrate through predefined code paths; agents let the LLM dynamically direct its own process and tool use
C. Workflows are stateless; agents are stateful
D. Workflows run locally; agents run as services

### E2
The guide says the interview answer that "is always open here" is:

A. "Use an agent — it generalizes better"
B. Naming the workflow/agent distinction and defending the cheaper option
C. "It depends on the model"
D. Choosing whichever the interviewer's company ships

### E3
Which is *not* one of the five workflow patterns?

A. Prompt chaining
B. Routing
C. Retrieval augmentation
D. Evaluator–optimizer

### E4
Parallelization splits into which two variations?

A. Sharding and replication
B. Sectioning and voting
C. Fan-out and fan-in
D. Map and reduce

### E5
Orchestrator–workers differs from sectioning because:

A. It runs workers sequentially
B. Subtasks are determined dynamically by the orchestrator, not fixed in advance
C. Workers share a single context window
D. It requires a human in the loop

### E6
"Agent = Model + Harness" — the harness contributes:

A. The system prompt and tool definitions
B. Acceptance baseline, execution boundary, feedback signals, rollback mechanism
C. Retry logic, caching, logging, and metrics
D. Memory, planning, tools, and reflection

### E7
ACI (agent–computer interface) design borrows "poka-yoke" to mean:

A. Fail fast on invalid input
B. Design the tool so the mistake is impossible to make
C. Log every tool call for later review
D. Require confirmation before destructive actions

### E8
The guide's concrete poka-yoke example:

A. Enum-typed arguments instead of free-form strings
B. Requiring absolute paths so relative-path errors cannot occur
C. A dry-run flag on every write tool
D. Rate limiting per tool

### E9
Task length is a design threshold. Beyond roughly what duration does crash recovery
become mandatory?

A. ~5 minutes
B. ~30 minutes
C. ~2 hours
D. ~1 day

### E10
The four memory types:

A. Short-term, long-term, cache, archive
B. Working, episodic, semantic, procedural
C. Scratchpad, vector, graph, relational
D. Session, user, org, global

### E11
For agent memory, the guide's stated bias:

A. Recall over precision — better to surface too much than miss something
B. Precision over recall — a wrong memory is worse than a missing one
C. Recency over relevance
D. Completeness over compactness

### E12
Subagents' primary architectural value:

A. Parallel speedup
B. Acting as a context firewall — the parent sees only the summary
C. Model diversity
D. Cost reduction through smaller models

### E13
MCP vs A2A:

A. MCP is agent↔agent; A2A is model↔tool
B. MCP is model↔tool; A2A is agent↔agent
C. Both are model↔tool; A2A adds authentication
D. Both are agent↔agent; MCP adds a schema layer

### E14
pass@k vs pass^k:

A. pass@k is deployment reliability; pass^k is the capability ceiling
B. pass@k is the capability ceiling (succeeds at least once in k); pass^k is deployment reliability (succeeds all k times)
C. They are the same metric under different notation
D. pass@k applies to code; pass^k applies to tool use

### E15
Which does a *production* SLA actually depend on?

A. pass@k
B. pass^k
C. mean reward per episode
D. Single-shot accuracy

### E16
PRINCE (Bayer × Thoughtworks, Fowler 2026) is cited as evidence for:

A. Multi-agent reinforcement learning in production
B. A real-world agent architecture pattern — Search → Ask → Do
C. Graph-based memory outperforming vector memory
D. Fine-tuning beating prompting for tool use

### E17
Multi-agent reinforcement learning (MARL) in production LLM stacks is:

A. The standard coordination approach
B. Not used — a common interview trap when someone conflates "multi-agent" with MARL
C. Used only for evaluator–optimizer loops
D. Used by orchestrator–workers under the hood

### E18
Evaluator–optimizer is the right pattern when:

A. Subtasks are independent and can run concurrently
B. There are clear evaluation criteria and iterative refinement adds measurable value
C. Input classification determines which specialized path to take
D. The task decomposes into fixed sequential steps

### E19
Building agent tools, the guide's advice on how many:

A. As many as possible — the model will pick
B. Few, well-described, hard to misuse
C. One generic tool with a large argument schema
D. One tool per API endpoint, mirroring the backend

### E20
Grading agents on trajectory as well as outcome matters because:

A. Trajectory grading is cheaper
B. An agent can reach the right answer by an unsafe or non-reproducible path
C. Outcome grading requires human labels
D. Trajectory is the only observable signal in production

**Answers E**: E1-B · E2-B · E3-C · E4-B · E5-B · E6-B · E7-B · E8-B · E9-B · E10-B ·
E11-B · E12-B · E13-B · E14-B · E15-B · E16-B · E17-B · E18-B · E19-B · E20-B

**Rationale notes**
- **E14/E15** is the highest-yield pair in this section. Demos are sold on pass@k;
  on-call is lived in pass^k. Naming both, and saying which one the SLA is written
  against, is a senior signal.
- **E17**: "Multi-agent" in industry means orchestration patterns, not MARL. If an
  interviewer uses the term loosely, disambiguate rather than play along.

---

## F. Context & cost (16 questions)

### F1
Prefix caching requires:

A. Semantically similar prompts
B. A byte-identical prefix
C. The same model and temperature
D. A dedicated cache endpoint

### F2
The layout rule that follows:

A. Dynamic content first, static content last
B. Static content first, dynamic content last
C. Alphabetical ordering of message blocks
D. Shortest blocks first

### F3
Prefix caching's approximate input-cost saving:

A. ~30%
B. ~50%
C. ~90%
D. ~99%

### F4
How do you verify a cache hit?

A. Compare latency against a baseline
B. Read `cache_read_input_tokens` in the response usage
C. Check the response `id` prefix
D. Enable debug logging on the SDK

### F5
Prefix caching and semantic caching are:

A. The same mechanism at different layers
B. Different — prefix caching reuses exact-prefix computation; semantic caching returns a stored response for a similar query
C. Different — prefix caching is client-side, semantic caching is provider-side
D. Sequential stages of the same optimization

### F6
Semantic caching's characteristic risk:

A. Cache stampede under load
B. Serving a stored answer to a query that is similar but not equivalent
C. Unbounded memory growth
D. Higher input token cost

### F7
Prefix cache TTL is on the order of:

A. Seconds
B. Minutes
C. Hours
D. Days

### F8
In the rank-ordered cost levers, which is #1?

A. Model routing
B. Prefix caching
C. Semantic caching
D. Compaction and offloading

### F9
Which lever reduces *perceived* rather than actual cost?

A. Model routing
B. Streaming
C. Batch/offline processing
D. Output-length discipline

### F10
The guide insists cost be reported as:

A. Cost per API call
B. Cost per successful task
C. Cost per thousand tokens
D. Cost per user session

### F11
Why does that framing matter?

A. It is easier to compute
B. A cheaper model that fails and retries can cost more per successful task than an expensive one that succeeds first time
C. It aligns with provider billing
D. It removes the need to track token counts

### F12
"Context rot" refers to:

A. Stale cache entries returning outdated answers
B. Degrading model performance as the context window fills
C. Corrupted serialization of conversation state
D. Memory entries becoming inconsistent across sessions

### F13
In compaction, which content is *never* summarized away first?

A. Tool outputs
B. Intermediate reasoning
C. Architectural decisions and constraints
D. Earlier user turns

### F14
Which is dropped *first* under compaction pressure?

A. Architectural decisions
B. Tool outputs
C. The system prompt
D. The current task statement

### F15
Skill/tool descriptions should be sized at roughly:

A. ~10 tokens
B. ~45 tokens
C. ~100 tokens
D. As long as needed for clarity

### F16
Why does that budget matter at all?

A. Long descriptions confuse the tokenizer
B. Every description sits in the prefix of every call — it is a fixed tax per request
C. Providers cap tool schema length
D. Shorter descriptions improve tool-selection accuracy monotonically

**Answers F**: F1-B · F2-B · F3-C · F4-B · F5-B · F6-B · F7-B · F8-B · F9-B · F10-B ·
F11-B · F12-B · F13-C · F14-B · F15-A · F16-B

**Rationale notes**
- **F5** is a deliberate interviewer conflation. Prefix caching is lossless — same
  prefix, same computation reused. Semantic caching is a *correctness* trade: you accept
  the risk that "similar" isn't "equivalent."
- **F8**: The full order is prefix caching → model routing → streaming → semantic cache
  → compaction/offloading → output-length discipline → batch/offline. Lead with #1
  because it is lossless and large.

---

## G. Evals & observability (18 questions)

### G1
The three components of an eval:

A. Dataset, metric, threshold
B. Task, trial, grader
C. Input, output, label
D. Baseline, candidate, judge

### G2
The grader ladder, cheapest and most reliable first:

A. Human → LLM-judge → code
B. Code → LLM-judge → human
C. LLM-judge → code → human
D. Code → human → LLM-judge

### G3
Tier 1 (unit) evals are characterized by:

A. Full end-to-end runs against production dependencies
B. No LLM calls, and catching roughly 70% of regressions
C. Mocked tools with trajectory assertions
D. Human review of sampled traces

### G4
Tier 2 evals are:

A. Unit-level assertions on parsing and formatting
B. Trajectory evals with mocked tools
C. End-to-end release gates
D. Online A/B tests

### G5
Tier 3 (end-to-end) evals should run:

A. On every commit
B. On release gates only
C. Continuously in production
D. Nightly on a full corpus

### G6
Why does `0.75³ ≈ 42%` appear in the evals guide?

A. It is the expected pass rate across three eval tiers
B. It shows how per-step reliability compounds across a multi-step agent
C. It is the observed accuracy of LLM judges
D. It is the sampling rate for trace review

### G7
Capability evals vs regression evals:

A. Both should sit near 100% before shipping
B. Capability evals may have a low pass rate (that's fine); regression evals should be near 100%
C. Regression evals may fail; capability evals must pass
D. They differ only in how often they run

### G8
The graduation rule says:

A. Capability evals become regression evals once they pass reliably
B. Regression evals are retired after three green runs
C. Tier 2 evals graduate to Tier 3 at release
D. LLM-judge graders graduate to code graders

### G9
How many examples to start an eval set with?

A. 5–10 synthetic cases
B. 20–50 real failures
C. 200–500 stratified samples
D. As many as the corpus allows

### G10
Why real failures rather than synthetic cases?

A. Synthetic data is more expensive to produce
B. Real failures encode the distribution you actually fail on; synthetic cases encode your assumptions
C. Synthetic cases cannot be graded by code
D. Real failures are already labeled

### G11
Between trials you must:

A. Reuse the environment to save setup cost
B. Reset the environment so trials are independent
C. Increase temperature to sample diversity
D. Carry forward memory to test continuity

### G12
When the eval and the agent both look broken, the guide says:

A. Fix the agent first — the eval is a measurement, not a product
B. Fix the eval system before the agent
C. Fix both in the same change
D. Escalate to human review

### G13
What share of production traces should be scored?

A. 1–2%
B. 10–20%
C. 50%
D. 100%

### G14
After a model or prompt change, the guide recommends:

A. Rolling back if any metric drops
B. A 48-hour full trace review
C. Doubling the sampling rate for a week
D. Freezing evals until metrics stabilize

### G15
The correct containment ordering:

A. monitoring ⊃ observability ⊃ tracing ⊃ alerting
B. observability ⊃ tracing ⊃ monitoring ⊃ alerting
C. tracing ⊃ observability ⊃ alerting ⊃ monitoring
D. alerting ⊃ monitoring ⊃ tracing ⊃ observability

### G16
The guide's split of deployment effort:

A. Agent ~80%, management layer ~20%
B. Agent ~40%, management layer ~60%
C. Agent ~60%, management layer ~40%
D. Evenly split

### G17
Langfuse's differentiator versus LangSmith, as cited:

A. Better LLM-judge templates
B. Self-hostable, which matters for GDPR/data-residency constraints
C. Native support for trajectory evals
D. Lower per-trace pricing

### G18
Outcome evals and trajectory evals should be:

A. Chosen based on whether the task is deterministic
B. Both graded — the answer and the path taken
C. Merged into a single composite score
D. Run in separate tiers, never together

**Answers G**: G1-B · G2-B · G3-B · G4-B · G5-B · G6-B · G7-B · G8-A · G9-B · G10-B ·
G11-B · G12-B · G13-B · G14-B · G15-B · G16-B · G17-B · G18-B

**Rationale notes**
- **G6**: Three steps at 75% each gives 42% end-to-end. This is the arithmetic behind
  "agents fail at the seams" — and the argument for per-step reliability targets rather
  than a single end-to-end number.
- **G12**: If you tune the agent against a broken eval you optimize toward noise. Fix
  the measurement first, always.
- **G16**: The number is the point of the section — most of the work is not the agent.

---

## H. Security & safety (18 questions)

### H1
Direct vs indirect prompt injection:

A. Direct comes from the model's own output; indirect from the user
B. Direct comes from the user's input; indirect arrives via content the agent retrieves or reads
C. Direct targets the system prompt; indirect targets tools
D. Direct is deliberate; indirect is accidental

### H2
The guide's framing of the core problem:

A. Detection quality — better classifiers close the gap
B. Source → sink: "you contain it, you don't detect it"
C. Model alignment — a well-aligned model resists injection
D. Input sanitization — escaping untrusted content is sufficient

### H3
Given H2, which answer is explicitly called wrong in an interview?

A. Any answer proposing capability restriction
B. Detection-only answers
C. Answers naming the dual-LLM pattern
D. Answers that mention human approval gates

### H4
In the dual-LLM pattern (Willison), the privileged LLM:

A. Reads untrusted content and summarizes it for the quarantined LLM
B. Holds the tools and never reads untrusted content
C. Validates the quarantined LLM's outputs before execution
D. Runs with a stricter system prompt but the same inputs

### H5
The quarantined LLM:

A. Has read-only tool access
B. Reads untrusted content but cannot act
C. Acts only after human approval
D. Runs a smaller model to limit damage

### H6
In the 9-step defense stack, input guardrails sit at position:

A. 1st
B. 4th
C. 8th
D. 9th

### H7
Output validation sits at:

A. 2nd
B. 5th
C. 8th
D. 9th

### H8
Continuous trace grading sits at:

A. 1st
B. 3rd
C. 6th
D. 9th

### H9
Memory poisoning vs context poisoning:

A. Memory poisoning affects the working context; context poisoning persists across sessions
B. Memory poisoning persists across sessions; context poisoning affects working memory within one
C. Both are within-session; they differ by attack vector
D. Both persist; they differ by which store is targeted

### H10
Denial-of-wallet describes:

A. Exhausting a rate limit to deny service
B. Driving up an attacker-controlled volume of expensive model calls to inflate cost
C. Stealing API keys to bill a victim
D. Blocking payment flows in an agentic commerce system

### H11
The three boundaries the guide says to establish before shipping any agent:

A. Model, data, and network
B. Who can trigger it, where it can act, what it did
C. Input, output, and audit
D. Identity, authorization, and encryption

### H12
"What it did" maps to which requirement?

A. Rate limiting
B. Audit logging / traceability
C. Least-privilege scopes
D. Authentication

### H13
The degradation ladder, in order:

A. Human → retry → fallback model → simpler baseline
B. Retry → fallback model → simpler baseline → human
C. Fallback model → retry → human → simpler baseline
D. Simpler baseline → retry → fallback model → human

### H14
Best-of-N jailbreaking (Hughes et al.) reported attack success rates of:

A. 45% on GPT-4o, 38% on Claude 3.5 Sonnet
B. 89% on GPT-4o, 78% on Claude 3.5 Sonnet
C. 99% on both
D. 60% on GPT-4o, 20% on Claude 3.5 Sonnet

### H15
What does that result imply for guardrail strategy?

A. Better prompt-level filters can close the gap
B. Prompt-level defenses are probabilistic — architectural containment must carry the load
C. Only frontier models are safe against BoN
D. Sampling temperature should be set to 0

### H16
"Typoglycemia" as an attack refers to:

A. Injecting invisible Unicode characters
B. Scrambling word interiors so filters miss the string but the model still reads it
C. Overwhelming the tokenizer with rare tokens
D. Homoglyph substitution in domain names

### H17
The three guardrail placements:

A. Ingest, index, retrieve
B. Input, output, action
C. Client, gateway, model
D. Pre-flight, in-flight, post-flight

### H18
The PII detection ladder, and its hard case:

A. LLM → NER → regex → hybrid; hard case is structured identifiers
B. Regex → NER → LLM → hybrid; hard case is contextual PII
C. Hybrid → regex → NER → LLM; hard case is multilingual text
D. NER → regex → hybrid → LLM; hard case is nested JSON

**Answers H**: H1-B · H2-B · H3-B · H4-B · H5-B · H6-A · H7-C · H8-D · H9-B · H10-B ·
H11-B · H12-B · H13-B · H14-B · H15-B · H16-B · H17-B · H18-B

**Rationale notes**
- **H2/H3**: This is the section's thesis. Injection is not a spam-filtering problem.
  Trace the untrusted *source* to the dangerous *sink* and cut the path — capability
  restriction, dual-LLM, human approval on the sink.
- **H14/H15**: Cite the numbers. 89%/78% is the argument that no prompt-level filter is
  a boundary; it is a speed bump in front of one.
- **H18**: Contextual PII ("the patient in room 4 who came in Tuesday") defeats regex
  and mostly defeats NER. Naming it is the senior signal.

---

## I. Data engineering & MLOps (14 questions)

### I1
The guide names one word "interviewers listen for" in orchestration. It is:

A. Atomicity
B. Idempotency
C. Durability
D. Determinism

### I2
Its three named mechanisms:

A. Transactions, savepoints, rollbacks
B. Upserts, partition overwrites, dedup keys
C. Locks, leases, fencing tokens
D. Checksums, retries, backoff

### I3
The MLOps maturity ladder, in order:

A. Notebook → automated pipeline → scripted + tracked → CI/CD-gated → monitored
B. Notebook → scripted + tracked → automated pipeline → CI/CD-gated → monitored/self-healing
C. Scripted → notebook → CI/CD-gated → automated pipeline → monitored
D. Notebook → CI/CD-gated → scripted + tracked → automated → self-healing

### I4
The rollout ladder:

A. Canary → shadow → full
B. Shadow → canary → full
C. Blue/green → canary → full
D. Canary → blue/green → full

### I5
Shadow deployment means:

A. A small percentage of live traffic is routed to the new model
B. The new model receives production traffic but its output is not served
C. The new model runs on a replica of yesterday's data
D. Two models serve alternately by request hash

### I6
The training pipeline DAG, in order:

A. Featurize → validate corpus → train → register → evaluate
B. Validate corpus → featurize → train → evaluate against baseline → register on pass
C. Validate → train → featurize → evaluate → register
D. Featurize → train → evaluate → validate → register

### I7
The four monitoring layers:

A. Logs, metrics, traces, alerts
B. Service metrics, data drift, concept drift, model quality against delayed labels
C. Latency, throughput, accuracy, cost
D. Ingest, transform, serve, audit

### I8
Alert thresholds should be tied to:

A. Historical percentiles only
B. Retrain triggers
C. On-call rotation capacity
D. SLA penalties

### I9
Debugging "the dashboard number is wrong", the ordered lineage walk is:

A. Metric definition → join fan-out → ingest dedup → source freshness
B. Source freshness → ingest dedup → join fan-out → metric definition drift
C. Join fan-out → source freshness → metric definition → ingest dedup
D. Ingest dedup → metric definition → source freshness → join fan-out

### I10
The principle behind that ordering:

A. Check the layer closest to the user first
B. Check the cheapest layer first
C. Check the most recently changed layer first
D. Check in pipeline execution order always

### I11
A feature store is justified by which two conditions?

A. Data volume above 1TB and more than 10 models
B. Online/offline consistency (train/serve skew) and feature reuse across teams
C. Streaming ingestion and sub-second serving
D. Regulatory lineage and PII classification

### I12
If neither condition holds, the guide says:

A. Build a lightweight feature store anyway for future-proofing
B. A well-tested mart is enough
C. Use a caching layer instead
D. Compute features inline at request time

### I13
Batch vs streaming — the guide's default:

A. Streaming, since it subsumes batch
B. Batch until a product need forces streaming
C. Lambda architecture from the start
D. Whichever matches the source system

### I14
LLM-era mappings the guide says to state out loud — which is *wrong*?

A. Embedding pipelines are ETL
B. Prompt/config versioning is model-registry thinking applied to prompts
C. Eval suites in CI/CD are the MLOps monitoring story in new clothes
D. Vector databases replace the data warehouse for analytics

**Answers I**: I1-B · I2-B · I3-B · I4-B · I5-B · I6-B · I7-B · I8-B · I9-B · I10-B ·
I11-B · I12-B · I13-B · I14-D

**Rationale notes**
- **I6**: "Evaluate against baseline → register *on pass*" is the load-bearing part. A
  registry that accepts unevaluated models is a filing cabinet, not a gate.
- **I14**: The AIE-with-MLOps-roots advantage is showing that the new stack is the old
  stack renamed — but vector search is retrieval infrastructure, not analytics.

---

## J. System design (15 questions)

The design round is graded on narration, not recall. These questions test the *method* —
which move a senior engineer makes first.

### J1
The time budget for the round:

A. 30–40 min, ~10 min/step
B. 45–55 min, ≈8 min/step across 5 steps
C. 60 min, ~15 min/step
D. However long the interviewer allows

### J2
Step 1 is Clarify & scope. The guide's rule:

A. Restate the prompt, then design
B. Never design against the raw prompt
C. Ask at most one clarifying question to save time
D. Start with the data model

### J3
The three clarification targets:

A. Users, data, and model choice
B. Requirements, scale, constraints
C. Latency, cost, accuracy
D. Functional, non-functional, operational

### J4
The strongest opening question is closest to:

A. "What's the expected QPS?"
B. "Who are the primary users, and what's the top priority — latency, accuracy, cost, or safety?"
C. "Which cloud provider are we on?"
D. "Should this use RAG or fine-tuning?"

### J5
Why write the non-functional requirements down explicitly?

A. Interviewers score completeness of the requirements list
B. They *are* the trade-off axes for the rest of the round
C. They determine the database choice
D. They are needed for the cost model

### J6
The trade-off narration formula:

A. Pick the best option, then defend it against objections
B. Consider 2–3 solutions → narrate pros/cons → ask which priority wins → justify the pick
C. Enumerate all options, then let the interviewer choose
D. State the trade-off, then move on

### J7
Step 4 asks you to:

A. Optimize the design for scale
B. Name your design's weaknesses before the interviewer does
C. Estimate cost
D. Draw the sequence diagram

### J8
The interviewer says your trade-off was wrong. The scored behavior is:

A. Defend it — consistency signals conviction
B. Adapt visibly; there are no points for stubbornness
C. Ask them to justify their objection first
D. Abandon the whole design and restart

### J9
You hit a genuine knowledge gap mid-round. The guide's tactic:

A. Reason from first principles without flagging it
B. Say "my understanding there is superficial", then redirect
C. Ask to skip that component
D. Guess confidently and correct later if challenged

### J10
Which is *not* one of the six trade-off axes?

A. Latency ↔ accuracy
B. Cost ↔ quality
C. Consistency ↔ availability
D. Recall ↔ precision

### J11
In the reference architecture, the API gateway carries:

A. Prompt assembly and streaming
B. Authn, rate limits, quotas
C. Query rewriting and reranking
D. Output validation

### J12
Which is *not* one of the five named sidecars?

A. Caches (prefix + semantic)
B. State store (session/checkpointer)
C. Feature store
D. HITL queue

### J13
From the bottleneck table, "model cold start" is mitigated by:

A. Backoff retries and multi-provider routing
B. Warm pools and pre-warming
C. Sharded queues and priority tiers
D. Pruning and periodic index rebuild

### J14
The guide says "never stop at the design." Closing well means:

A. Summarizing the components you drew
B. Stating success metrics with numbers — e.g. p95 under 2s while holding faithfulness above 0.9
C. Listing the technologies you would use
D. Asking what the interviewer would have done differently

### J15
Which pattern exists specifically to prevent *cascading* failures in a distributed
system?

A. Retry pattern
B. Circuit breaker pattern
C. Timeout pattern
D. Exception handling

**Answers J**: J1-B · J2-B · J3-B · J4-B · J5-B · J6-B · J7-B · J8-B · J9-B · J10-D ·
J11-B · J12-C · J13-B · J14-B · J15-B

**Rationale notes**
- **J10**: Precision/recall is a *model* trade-off, not a system non-functional. The six
  axes are latency↔accuracy, cost↔quality, consistency↔availability,
  full-automation↔safety, read↔write throughput, storage↔caching.
- **J14**: Numbers close the round. "p95 < 2s, faithfulness > 0.9" plus a
  future-improvements list separates a design from a drawing.
- **J15**: All four distractors are real practices — the question is which one targets
  *cascading* failure. A circuit breaker tracks the failure rate of a dependency and,
  once it crosses a threshold, **opens**: calls fail fast without touching the sick
  service. After a cooldown it goes **half-open**, admits a few probes, and either closes
  (recovered) or re-opens. That containment is the point. Timeouts (C) bound a *single*
  call and are necessary but insufficient — with a dead dependency and a 30s timeout,
  in-flight requests still pile up until threads, connections, or queue depth are
  exhausted, and the caller dies too. Retries (A) make cascades *worse* by multiplying
  load on an already-failing service unless paired with a breaker and jittered backoff.
  Exception handling (D) is local error propagation, not a load-shedding mechanism. In
  the LLM stack this is the pattern behind provider fallback (**J13**, **H-tier
  degradation ladders**): trip the breaker on the primary model endpoint, route to the
  fallback, probe for recovery.

---

## K. Product & delivery (12 questions)

### K1
The framing habit — every design answer opens with:

A. Architecture → data → model → deployment
B. User → problem → success metric → constraint
C. Requirements → scale → constraints → design
D. Cost → value → risk → timeline

### K2
Which is the better-framed problem statement?

A. "Build a RAG chatbot for support"
B. "Reduce support cost 20% while holding CSAT"
C. "Deploy an LLM over the knowledge base"
D. "Improve first-response time using AI"

### K3
The napkin token-cost formula:

A. queries/day × latency × $/hour
B. tokens/query × $/M tokens × queries/day
C. model size × requests × utilization
D. context length × users × sessions

### K4
"Mistral 7B gives 90% of the accuracy — why still pick it over GPT-4?" The intended answer:

A. Open weights avoid vendor lock-in
B. The last 10% costs 20× and the use case's error tolerance doesn't need it
C. Smaller models are easier to fine-tune
D. Latency is lower

### K5
When should you reverse that answer?

A. When traffic volume is high
B. When errors are expensive
C. When the model is self-hosted
D. When the corpus is multilingual

### K6
Where does AI belong first, and last?

A. First in high-stakes decisions, last in drafting
B. First in high-volume, tolerant-of-review workflows; last in irreversible/high-stakes actions
C. First wherever data is cleanest; last where data is sparse
D. First in customer-facing flows; last in internal tooling

### K7
The metrics tree:

A. Input → output → outcome
B. North star → driver metrics → guardrail metrics
C. Leading → lagging → composite
D. Adoption → retention → revenue

### K8
Which of these is a *guardrail* metric for an agent, not a driver metric?

A. Goal completion rate
B. No-touch rate
C. Hallucination rate
D. Time-to-trust

### K9
Failure UX on low confidence — the triad:

A. Retry, escalate, log
B. Abstain, cite, escalate
C. Degrade, notify, queue
D. Warn, proceed, review

### K10
The prioritization formula:

A. (impact + confidence) − effort
B. impact × confidence ÷ effort, with guardrail metrics as veto
C. reach × impact × confidence ÷ effort
D. value ÷ (cost × risk)

### K11
"The model is 92% accurate — ship it?" The structured answer requires:

A. Comparing against the human baseline only
B. 8% errors × volume × cost-per-error, plus the error *distribution* (harmless vs catastrophic), plus mitigation UX — then yes/no with conditions
C. Re-running evals on a larger test set before deciding
D. Shipping behind a feature flag and measuring

### K12
Nonprofit/mission-driven constraints the guide names — which is *not* one?

A. Grant-cycle budgets make opex unpredictable, so API bills need caps
B. Volunteer/rotating maintainers favor boring tech and managed services
C. Success ≠ revenue; funders need reportable impact numbers from day one
D. Compliance burden is lower, so PII handling can be lighter-weight

**Answers K**: K1-B · K2-B · K3-B · K4-B · K5-B · K6-B · K7-B · K8-C · K9-B · K10-B ·
K11-B · K12-D

**Rationale notes**
- **K8**: Drivers are goal completion, no-touch rate, escalation rate, time-to-trust.
  Guardrails are hallucination rate, complaint rate, cost/interaction. The distinction
  matters: you optimize drivers and *veto* on guardrails.
- **K12**: The opposite is true — beneficiary PII (immigration status, health, benefits)
  is higher-stakes, and consent/minimization is about trust with vulnerable populations,
  not a compliance checkbox.
- **K4/K5**: "ROI, not model maximalism" — but the reversal is what shows judgment
  rather than a memorized slogan.

---

## Rapid-fire distinction drill

Say each distinction in one sentence, out loud, in under ten seconds. These are the
pairs interviewers use to separate memorization from understanding.

1. Prefill vs decode
2. Prefix caching vs semantic caching
3. pass@k vs pass^k
4. CRAG vs Self-RAG
5. Workflow vs agent
6. RLHF vs DPO
7. LoRA vs QLoRA
8. Direct vs indirect prompt injection
9. Memory poisoning vs context poisoning
10. Covariate drift vs concept drift
11. Capability evals vs regression evals
12. Outcome evals vs trajectory evals
13. MCP vs A2A
14. Working vs episodic vs semantic vs procedural memory
15. Sectioning vs voting (parallelization)
16. Orchestrator–workers vs sectioning
17. Vector search vs BM25 failure modes
18. RRF vs weighted score fusion
19. Chunk parent vs child
20. Shadow vs canary deployment
21. Batch vs online vs streaming serving
22. OLTP vs OLAP
23. Star schema vs wide table
24. At-least-once vs exactly-once
25. `WHERE` vs `HAVING`
26. `RANK` vs `DENSE_RANK` vs `ROW_NUMBER`
27. Concurrency vs parallelism
28. Threads vs processes vs async (in Python)
29. L1 vs L2 regularization
30. PCA vs UMAP
31. MAE vs RMSE vs MAPE
32. Calibration vs discrimination
33. Precision vs recall — and which one agent memory optimizes for
34. Observability vs monitoring
35. Driver metrics vs guardrail metrics
36. Functional vs non-functional requirements
37. Build vs buy vs wait
38. Detection vs containment (injection defense)
39. Privileged vs quarantined LLM
40. Golden set vs production traces

---

## Sources

Every question is grounded in the guides under `../../guides/`:

| Section | Guide |
|---|---|
| A | `0-programming/interview-guide.md` |
| B | `1-foundations/interview-guide.md` |
| C | `2-llm-fundamentals/interview-guide.md` |
| D | `3-rag/interview-guide.md` |
| E | `4-agents/interview-guide.md` |
| F | `5-context-cost/interview-guide.md` |
| G | `6-evals-observability/interview-guide.md` |
| H | `7-security-safety/interview-guide.md`, `7-security-safety/prompt-injection.md` |
| I | `8-data-eng-mlops/interview-guide.md` |
| J | `9-system-design/interview-guide.md`, `9-system-design/06-component-cheatsheet.md` |
| K | `10-product-delivery/interview-guide.md` |

Open-ended companions to this bank live in [questions.md](questions.md); the
study plan is in [study-guide.md](study-guide.md).
