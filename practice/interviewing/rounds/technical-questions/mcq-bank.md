# MCQ Bank — Full Topic Parity

Multiple-choice drill bank covering 19 topics. Standalone: it re-covers
ground the role-specific banks handle so it works on its own.

**How to use**: cover the answer key, take a section, then read the rationale for every
question you got wrong *and* every one you guessed right. The distractors are built from
the specific confusions the material flags — a lucky guess teaches nothing.

**Sourcing**: questions were written against topic guides that have since folded into the
pillar notes (mapped under Sources below), so a wrong answer points at a pillar to reread. Where the material explicitly warns that interviewers conflate two things (prefix vs semantic
caching, pass@k vs pass^k, CRAG vs Self-RAG), the bank tests that pair directly.

| Section | Topic | Questions |
|---|---|---|
| A | Programming (Python, DSA, SQL, concurrency) | 20 |
| B | ML foundations | 16 |
| C | LLM fundamentals | 23 |
| D | RAG | 20 |
| E | Agents | 20 |
| F | Context & cost | 16 |
| G | Evals & observability | 17 |
| H | Security & safety | 18 |
| I | Data engineering & MLOps | 14 |
| J | System design | 15 |
| K | Product & delivery | 12 |
| L | Probability and distributions | 16 |
| M | Statistics and A/B testing | 16 |
| N | Classical ML models | 15 |
| O | Bayesian inference and Markov chains | 7 |
| P | Unsupervised learning | 6 |
| Q | Neural networks | 7 |
| R | Retrieval, ranking and recommenders | 8 |
| S | Features, tuning, time series and metrics | 8 |
| **Total** | | **274** |

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

The course calls one thing "the #1 practical sin" in applied ML. It is:

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

The interview move the course says to make first when discussing any model result:

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

Why gradient boosting over a neural net on tabular data? The course names four reasons —
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

Model is excellent offline, poor in production. The course gives an ordered checklist.
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

Self-attention compares every token with every earlier one. That quadratic cost most directly explains:

A. Why models hallucinate
B. Why long contexts are expensive to process
C. Why token counts vary between languages
D. Why training can forget earlier data

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
B. Batching, floating point, hardware and version differences
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
B. Models using information at the start and end of a long context better than the middle
C. Retrieval returning mid-ranked documents
D. Positional embeddings failing past their trained length

### C20

The course's stated mitigation for long-context degradation:

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
  randomness but not nondeterminism from batching, floating point, and hardware or version
  differences.
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

## D. RAG (20 questions)

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

The course's stance on semantic chunking:

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
B. BM25 and cosine scores have incomparable distributions; rank fusion needs no score normalization
C. RRF is faster to compute
D. Weighted sums require normalized embeddings

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

GraphRAG restraint — the course's caution:

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

**Answers D**: D1-B · D2-B · D3-B · D4-B · D5-B · D6-B · D7-B · D9-B · D10-B ·
D11-B · D13-B · D14-B · D15-B · D16-B · D17-B · D18-B · D19-B · D20-B ·
D21-B · D22-D

**Rationale notes**

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

The course says the interview answer that "is always open here" is:

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

The course's concrete poka-yoke example:

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

For agent memory, the course's stated bias:

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

Building agent tools, the course's advice on how many:

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

The course insists cost be reported as:

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

## G. Evals & observability (17 questions)

### G1

The three components of an eval:

A. Dataset, metric, threshold
B. Task, trial, grader
C. Input, output, label
D. Baseline, candidate, judge

### G2

The grader ladder, cheapest first:

A. Human → LLM-judge → code
B. Code → LLM-judge → human
C. LLM-judge → code → human
D. Code → human → LLM-judge

### G3

Tier 1 (unit) evals are characterized by:

A. Full end-to-end runs against production dependencies
B. No LLM calls, and cheap enough to run on every commit
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

Why does `0.75³ ≈ 42%` appear in the eval notes?

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

When the eval and the agent both look broken, the course says:

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

After a model or prompt change, the course recommends:

A. Rolling back if any metric drops
B. A 48-hour full trace review
C. Doubling the sampling rate for a week
D. Freezing evals until metrics stabilize

### G16

The course's split of deployment effort:

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
G11-B · G12-B · G13-B · G14-B · G16-B · G17-B · G18-B

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

The course's framing of the core problem:

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

The three boundaries the course says to establish before shipping any agent:

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

The course names one word "interviewers listen for" in orchestration. It is:

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

If neither condition holds, the course says:

A. Build a lightweight feature store anyway for future-proofing
B. A well-tested mart is enough
C. Use a caching layer instead
D. Compute features inline at request time

### I13

Batch vs streaming — the course's default:

A. Streaming, since it subsumes batch
B. Batch until a product need forces streaming
C. Lambda architecture from the start
D. Whichever matches the source system

### I14

LLM-era mappings the course says to state out loud — which is *wrong*?

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

Step 1 is Clarify & scope. The course's rule:

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

You hit a genuine knowledge gap mid-round. The course's tactic:

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

The course says "never stop at the design." Closing well means:

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

Nonprofit/mission-driven constraints the course names — which is *not* one?

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

## L. Probability and distributions (16 questions)

### L1

What is the variance of a Bernoulli variable with p = 0.2?

A. 0.20
B. 0.16
C. 0.04
D. 0.80

### L2

X is Binomial with n = 100 and p = 0.1. What are its mean and standard deviation?

A. 10 and 9
B. 10 and 3
C. 10 and 0.9
D. 1 and 3

### L3

Card payments are declined at a steady average rate, independently of one another. Which
distribution models the number declined in a given minute?

A. Binomial
B. Normal
C. Poisson
D. Geometric

### L4

A Poisson variable has mean 4. What is its variance?

A. 4
B. 2
C. 16
D. It depends on the sample size

### L5

What does the Central Limit Theorem state?

A. Any large dataset is approximately Normally distributed
B. The sample mean equals the population mean once n exceeds 30
C. The variance of the data shrinks as n grows
D. The mean of a large sample is approximately Normal even when the data are not

### L6

A and B are independent with P(A) = 0.5 and P(B) = 0.4. What is P(A or B)?

A. 0.9
B. 0.2
C. 0.7
D. 0.8

### L7

A condition has 1% prevalence. A test has 90% sensitivity and a 10% false positive rate.
Roughly what is the probability of the condition given a positive test?

A. About 8%
B. About 50%
C. About 90%
D. About 1%

### L8

X and Y are independent with variances 4 and 9. What is the standard deviation of X + Y?

A. 5
B. 13
C. About 3.6
D. 6.5

### L9

Var(X) = 2. What is Var(3X)?

A. 6
B. 9
C. 12
D. 18

### L10

E[X + Y] = E[X] + E[Y] holds when:

A. X and Y are independent
B. X and Y have the same distribution
C. Always, as long as both expectations exist
D. X and Y are both Normal

### L11

A sample of n = 100 has a standard error of the mean of 1. What sample size halves it?

A. 200
B. 400
C. 141
D. 1,000

### L12

How many rolls of a fair die do you expect to need to see the first six?

A. 6
B. 3
C. 3.5
D. 36

### L13

Which statement is true of two random variables?

A. Zero correlation implies independence
B. Independence implies zero correlation
C. Each implies the other
D. Neither implies the other

### L14

X is Normal. Roughly what is P(X > μ + 2σ)?

A. 5%
B. 2.5%
C. 16%
D. 0.3%

### L15

Which is the best approximation to a Binomial with n = 1,000 and p = 0.002?

A. Normal with mean 500
B. Poisson with mean 0.002
C. Geometric with p = 0.002
D. Poisson with mean 2

### L16

Can the value of a probability density function be greater than 1?

A. Yes: only the area under the density must equal 1
B. No: probabilities cannot exceed 1
C. Only for discrete variables
D. Only at the mean

**Answers L**: L1-B · L2-B · L3-C · L4-A · L5-D · L6-C · L7-A · L8-C · L9-D · L10-C ·
L11-B · L12-A · L13-B · L14-B · L15-D · L16-A

**Rationale notes**

- **L1**: Variance is p(1 − p) = 0.2 × 0.8 = 0.16.
- **L2**: Mean np = 10. Variance np(1 − p) = 9, so the standard deviation is 3. Answer A gives the variance.
- **L3**: A count of independent events in a fixed interval at a constant rate is Poisson. Binomial needs a fixed number of trials.
- **L4**: For a Poisson the mean and the variance are both λ.
- **L5**: The theorem is about the distribution of the sample mean, not of the data. The raw data keep their shape.
- **L6**: P(A or B) = P(A) + P(B) − P(A and B) = 0.5 + 0.4 − 0.5 × 0.4 = 0.7.
- **L7**: Bayes: 0.01 × 0.9 / (0.01 × 0.9 + 0.99 × 0.1) = 0.009 / 0.108, about 8%. False positives from the large healthy group dominate.
- **L8**: Variances add for independent variables: 4 + 9 = 13, and √13 is about 3.6. Standard deviations do not add.
- **L9**: Var(aX) = a²Var(X) = 9 × 2 = 18.
- **L10**: Linearity of expectation needs no independence. It is variances that need zero correlation to add.
- **L11**: The standard error is σ/√n, so halving it takes four times the sample.
- **L12**: The wait for the first success is Geometric with mean 1/p = 6.
- **L13**: Independence implies zero correlation. The reverse fails: with X standard Normal and Y = X², the correlation is 0 but Y is a function of X.
- **L14**: About 95% lies within 2σ, leaving 5% in the two tails and 2.5% in each.
- **L15**: Large n with small p goes to Poisson with λ = np = 2. A Normal fits badly because np is far below 10.
- **L16**: A density is not a probability. Uniform(0, 0.5) has density 2 everywhere on its interval.

---

## M. Statistics and A/B testing (16 questions)

### M1

A test returns p = 0.03. What does that mean?

A. There is a 3% chance the null hypothesis is true
B. There is a 97% chance the effect is real
C. If the null were true, data this extreme or more would occur 3% of the time
D. The effect size is 3%

### M2

What is a Type II error?

A. Rejecting a null hypothesis that is true
B. Failing to reject a null hypothesis that is false
C. Using a one-sided test on two-sided data
D. Running a test without a power calculation

### M3

The 95% confidence interval for a lift is 0.2 to 1.8 points. Which statement is correct?

A. There is a 95% probability the true lift is between 0.2 and 1.8
B. 95% of users saw a lift between 0.2 and 1.8
C. The result is not significant because the interval is wide
D. Intervals built this way cover the true lift 95% of the time, and this one excludes zero

### M4

The sample variance computed with divisor n is:

A. Unbiased
B. Biased high
C. Biased low
D. Unbiased but inconsistent

### M5

The mean squared error of an estimator equals:

A. Bias² + variance
B. Bias + variance
C. Variance − bias²
D. Bias × variance

### M6

You halve the minimum detectable effect of an A/B test. The required sample size:

A. Doubles
B. Quadruples
C. Rises by a factor of √2
D. Rises by a factor of 8

### M7

You test 20 independent metrics at α = 0.05 and the change has no real effect on any of
them. How many do you expect to come out significant?

A. 0.05
B. 5
C. 20
D. 1

### M8

A team checks its A/B test daily and stops the first time p < 0.05. The main consequence is:

A. Lower power and nothing else
B. A false positive rate well above 5%
C. An effect estimate biased towards zero
D. None, provided the sample is large

### M9

A 50/50 test logs 50,000 users in control and 52,000 in treatment, and a chi-square test on
the split gives p < 0.001. What should you do?

A. Reweight the arms and read the results
B. Extend the test until the split evens out
C. Investigate assignment and logging; do not trust the metrics
D. Switch to a one-sided test

### M10

Which change raises the power of a test?

A. Lowering α from 0.05 to 0.01
B. Reducing the variance of the metric
C. Using a smaller sample
D. Targeting a smaller effect

### M11

A test on 5 million users finds a lift of 0.02 points with p = 0.001. The right reading is:

A. Ship: the result is highly significant
B. Rerun: results this significant are suspicious
C. Statistically significant, but check whether a lift that small is worth acting on
D. Not significant, because the lift is small

### M12

A satisfaction survey is emailed to users active in the last week. Will a larger response
count remove the bias in the average score?

A. No: more data shrinks variance and leaves selection bias unchanged
B. Yes, by the Law of Large Numbers
C. Yes, once n exceeds 30
D. Only if the scores are Normally distributed

### M13

Which test compares conversion rates between two independent groups of 50,000 users each?

A. Paired t-test
B. Two-proportion z-test
C. Mann-Whitney U
D. One-way ANOVA

### M14

A test is not significant, and its confidence interval is wide enough to include the
minimum effect you care about. What do you conclude?

A. The change has no effect
B. The change has a negative effect
C. The test should be rerun one-sided
D. The test is inconclusive: it was underpowered for that effect

### M15

A consistent estimator is one that:

A. Converges to the true value as the sample grows
B. Equals the true value on average at every sample size
C. Has the smallest variance of any estimator
D. Gives the same value on every sample

### M16

Users are randomised, but the analysis treats every page view as an independent
observation. What is the effect?

A. Standard errors are too large, so real effects are missed
B. The point estimate is biased towards zero
C. Standard errors are too small, so false positives rise
D. None, if users were randomised correctly

**Answers M**: M1-C · M2-B · M3-D · M4-C · M5-A · M6-B · M7-D · M8-B · M9-C · M10-B ·
M11-C · M12-A · M13-B · M14-D · M15-A · M16-C

**Rationale notes**

- **M1**: A p-value is computed assuming the null is true. It is not the probability that the null is true, and it carries no information about effect size.
- **M2**: Type II is a missed effect, with rate β. Answer A is a Type I error.
- **M3**: The 95% describes the procedure over repeated experiments. Because the interval excludes zero, the result is significant at 5%.
- **M4**: Deviations are taken from the sample mean, which is closer to the data than the true mean, so the divisor n underestimates by the factor (n − 1)/n.
- **M5**: MSE = bias² + variance, which is why a biased estimator with low variance can beat an unbiased one.
- **M6**: Sample size is proportional to 1/δ², so half the effect needs four times the users.
- **M7**: Each test has a 5% false positive chance, so 20 × 0.05 = 1 expected. The chance of at least one is 1 − 0.95²⁰, about 64%.
- **M8**: Every look is another chance to cross the threshold. With 20 looks the false positive rate is roughly 25%.
- **M9**: A sample ratio mismatch means the arms differ in some way other than the treatment. No reweighting repairs that.
- **M10**: Power rises with sample size, effect size and α, and falls with variance. Lowering α reduces power.
- **M11**: With millions of users almost any difference is statistically significant. Compare the effect and its interval with the smallest lift worth the cost.
- **M12**: Bias comes from who is in the sample. A larger sample of the same kind gives a tighter interval around the wrong number.
- **M13**: Two independent proportions with large samples call for the two-proportion z-test. A chi-square test on the 2×2 table is equivalent.
- **M14**: Absence of evidence is not evidence of absence. Only an interval that excludes the minimum effect supports "no meaningful effect".
- **M15**: Consistency is about the limit as n grows. Answer B defines unbiasedness.
- **M16**: Page views from one user are correlated, so the effective sample is smaller than the row count. Analyse by user or correct the variance.

---

## N. Classical ML models (15 questions)

### N1

Bagging, as in a random forest, mainly reduces:

A. Bias
B. Variance
C. Irreducible noise
D. Training time

### N2

How does gradient boosting build its trees?

A. Independently, on bootstrap samples, then averages them
B. One deep tree, then prunes it
C. In sequence, each fitted to the errors of the ensemble so far
D. In parallel, each on a different subset of features

### N3

Which of these models needs its features scaled?

A. Random forest
B. Gradient-boosted trees
C. k-nearest neighbours
D. A single decision tree

### N4

Which penalty can set coefficients exactly to zero?

A. L1 (lasso)
B. L2 (ridge)
C. Both
D. Neither

### N5

A model scores 99% on training data and 72% on validation data. Which response fits?

A. Add more features
B. Train for longer
C. Use a more flexible model
D. Regularise, simplify the model or get more data

### N6

A fraud model reaches 99.8% accuracy on data where 0.2% of transactions are fraud. What
does that tell you?

A. The model is excellent
B. Very little: predicting "not fraud" every time scores the same
C. The model is overfitting
D. The threshold is too low

### N7

In a logistic regression, a binary feature has a coefficient of 0.69. Having the feature:

A. Raises the probability by 69 percentage points
B. Raises the probability by 0.69%
C. Roughly doubles the odds
D. Roughly doubles the probability

### N8

A classifier has a ROC-AUC of 0.5. This means:

A. Its ranking of positives over negatives is no better than random
B. It classifies half the cases correctly
C. Its precision is 50%
D. It is well calibrated

### N9

Compared with k = 50, a k-nearest-neighbours model with k = 1 has:

A. Higher bias and higher variance
B. Higher bias and lower variance
C. Lower bias and lower variance
D. Lower bias and higher variance

### N10

You are predicting next month's defaults from several years of loan data. How should you
validate?

A. Shuffled k-fold cross-validation
B. Train on earlier periods and test on later ones
C. Leave-one-out cross-validation
D. A random 80/20 split stratified by outcome

### N11

Which is a real weakness of a single decision tree?

A. It needs scaled features
B. It cannot model interactions
C. Small changes in the data can produce a very different tree
D. It cannot use categorical features

### N12

What does Naive Bayes assume?

A. Features are independent of each other given the class
B. Features are Normally distributed
C. Classes are balanced
D. The decision boundary is linear

### N13

You lower the decision threshold of a classifier. What typically happens?

A. Precision and recall both rise
B. Precision rises and recall falls
C. Neither changes; only accuracy moves
D. Recall rises and precision falls

### N14

Which loss does logistic regression minimise?

A. Mean squared error
B. Hinge loss
C. Log loss (cross-entropy)
D. Gini impurity

### N15

For a medium-sized tabular dataset with mixed feature types and non-linear effects, which
model is usually the strongest default?

A. k-nearest neighbours
B. Gradient-boosted trees
C. Naive Bayes
D. A linear support vector machine

**Answers N**: N1-B · N2-C · N3-C · N4-A · N5-D · N6-B · N7-C · N8-A · N9-D · N10-B ·
N11-C · N12-A · N13-D · N14-C · N15-B

**Rationale notes**

- **N1**: Averaging many high-variance trees trained on different bootstrap samples cancels their individual errors. Bias stays about the same.
- **N2**: Boosting is sequential and each tree corrects the current ensemble, which lowers bias. Answer A describes bagging.
- **N3**: Nearest neighbours uses distances, so a feature on a larger scale dominates. Tree splits depend only on the order of values.
- **N4**: The L1 penalty has a corner at zero, so the optimum often sits exactly there. L2 shrinks coefficients without zeroing them.
- **N5**: A large gap between training and validation scores is overfitting, a variance problem. The other options add capacity and widen the gap.
- **N6**: With 0.2% positives, a model that never flags fraud is 99.8% accurate. Use precision, recall and PR-AUC.
- **N7**: The coefficient is a change in log-odds, and e^0.69 is about 2. The change in probability depends on the starting point.
- **N8**: ROC-AUC is the probability that a random positive is scored above a random negative. 0.5 is a coin flip.
- **N9**: With k = 1 the model follows every training point: flexible, so low bias, and unstable, so high variance.
- **N10**: Shuffled splits let the model train on the future and overstate performance. Validate forward in time.
- **N11**: Trees are high-variance learners, which is the reason forests average them. They handle interactions and need no scaling.
- **N12**: The "naive" part is conditional independence of features given the class. Gaussian Naive Bayes adds a Normal assumption, but that is one variant.
- **N13**: A lower threshold flags more cases, catching more true positives and admitting more false ones.
- **N14**: Log loss is the negative log-likelihood of a Bernoulli outcome, so minimising it is maximum likelihood.
- **N15**: Boosted trees capture non-linear effects and interactions with no scaling or encoding of order, and usually lead on tabular data.

---

## O. Bayesian inference and Markov chains (7 questions)

### O1

You start with a uniform Beta(1, 1) prior on a success rate and observe 3 successes in 3 trials. What is the posterior mean?

A. 1.0
B. 0.8
C. 0.75
D. 0.6

### O2

What does a 95% credible interval state?

A. 95% of intervals built this way over repeated samples would cover the parameter
B. 95% of the observations fall inside it
C. The null hypothesis is rejected at the 5% level
D. Given the data and the prior, the parameter lies in it with probability 0.95

### O3

With a flat prior, the MAP estimate equals which other estimate?

A. The maximum likelihood estimate
B. The posterior mean
C. The prior mean
D. The posterior median

### O4

As the sample grows, what happens to the influence of the prior on the posterior?

A. It grows, because the prior is counted once per observation
B. It stays the same
C. It shrinks, because the likelihood dominates
D. It depends only on whether the prior is conjugate

### O5

What does the Markov property say?

A. Every state is visited equally often in the long run
B. The chain always returns to its starting state
C. Transition probabilities change at each step
D. The next state depends only on the current state, not on the path to it

### O6

In a transition matrix where entry (i, j) is the probability of moving from state i to state j, what must hold?

A. Each column sums to 1
B. Each row sums to 1
C. The diagonal sums to 1
D. The matrix is symmetric

### O7

What is an absorbing state?

A. A state the chain can never reach
B. The state with the highest long-run probability
C. A state that, once entered, is never left
D. A state the chain visits on a fixed cycle

**Answers O**: O1-B · O2-D · O3-A · O4-C · O5-D · O6-B · O7-C

**Rationale notes**

- **O1**: The posterior is Beta(1 + 3, 1 + 0) = Beta(4, 1), with mean 4/5 = 0.8. The maximum likelihood estimate is 1.0, and the prior pulls it back.
- **O2**: A credible interval is a probability statement about the parameter. The first option is the confidence interval, a statement about the procedure.
- **O3**: MAP maximises likelihood × prior. A flat prior is a constant, so the maximum is where the likelihood peaks.
- **O4**: The likelihood multiplies in once per observation and the prior once in total, so with enough data two reasonable priors give nearly the same posterior.
- **O5**: Given the present, the future is independent of the past. That is what lets one transition matrix describe the whole process.
- **O6**: From state i the chain must go somewhere, so row i is a probability distribution. Columns need not sum to 1.
- **O7**: Its row in the transition matrix has a 1 on the diagonal. Churned or converted are typical absorbing states.

---

## P. Unsupervised learning (6 questions)

### P1

Why standardise features before PCA?

A. PCA cannot run on features with different units
B. A feature measured on a large scale would dominate the components
C. Standardising makes the components independent of each other
D. It reduces the number of components needed to one

### P2

Which reading of a t-SNE plot is unsafe?

A. Points that sit close together were similar in the original space
B. The plot shows whether the data have local grouping
C. Different perplexity settings can give different pictures
D. The distance between two clusters shows how different they are

### P3

When is DBSCAN a better choice than k-means?

A. The clusters have irregular shapes and the data contain noise points
B. The clusters are round and of similar size
C. You know the number of clusters in advance
D. The clusters differ widely in density

### P4

What does a Gaussian mixture model give you that k-means does not?

A. A guarantee of finding the global optimum
B. Clusters without choosing how many
C. Soft assignments and elliptical clusters
D. Faster fitting on large data

### P5

In the EM algorithm for a mixture model, what does the E step compute?

A. New means and covariances for each component
B. The probability that each component produced each point, under the current parameters
C. The number of components to use
D. The gradient of the likelihood

### P6

A point has a silhouette score close to 1. What does that mean?

A. It lies on the border between two clusters
B. It is probably assigned to the wrong cluster
C. The number of clusters is too high
D. It is much closer to its own cluster than to the nearest other cluster

**Answers P**: P1-B · P2-D · P3-A · P4-C · P5-B · P6-D

**Rationale notes**

- **P1**: PCA finds directions of greatest variance, and variance depends on units. Income in euros would swamp age in years.
- **P2**: t-SNE keeps local neighbourhoods and distorts global distances and cluster sizes, so gaps between clusters carry no reliable meaning.
- **P3**: DBSCAN grows clusters from dense regions, needs no k and labels sparse points as noise. Its weak spot is clusters of very different density.
- **P4**: A mixture model gives each point a probability for each component and fits a covariance per component. k-means is the special case of hard assignments and equal spherical clusters.
- **P5**: The E step computes responsibilities. The M step then re-estimates the parameters, weighting each point by them. Each round cannot lower the likelihood.
- **P6**: The silhouette compares the mean distance to the point's own cluster with that to the nearest other one. Near 0 is a border point, and negative suggests a wrong assignment.

---

## Q. Neural networks (7 questions)

### Q1

Why does a neural network need non-linear activation functions?

A. Without them, any stack of layers collapses to a single linear map
B. They make every layer's output sum to 1
C. They prevent overfitting
D. They make the loss convex

### Q2

What goes wrong if every weight in a layer starts at zero?

A. The gradients explode
B. The loss starts at infinity
C. Every unit computes the same output and gets the same update, so they never differ
D. Nothing: the biases break the tie

### Q3

Why do deep networks with sigmoid activations suffer from vanishing gradients?

A. Sigmoid outputs are not centred on zero
B. The sigmoid's derivative is at most 0.25, and backpropagation multiplies one per layer
C. The sigmoid is expensive to compute
D. Sigmoid units die when their input is negative

### Q4

How does dropout behave at inference time?

A. It drops units at the same rate as in training
B. It drops units at half the training rate
C. It drops only the units with the smallest weights
D. It is switched off, and all units are used

### Q5

What does batch normalisation do to a layer's inputs?

A. Standardises each feature over the mini-batch, then applies a learned scale and shift
B. Clips each value to between 0 and 1
C. Removes the features with the lowest variance
D. Normalises each example to unit length

### Q6

Why do skip connections make very deep networks trainable?

A. They halve the number of parameters
B. They remove the need for activation functions
C. The gradient has an identity path back, and each block only learns a residual
D. They make every layer the same width

### Q7

What does the Adam optimiser combine?

A. Weight decay and dropout
B. Momentum and a per-parameter step size from a running average of squared gradients
C. Batch normalisation and gradient clipping
D. A line search and second derivatives

**Answers Q**: Q1-A · Q2-C · Q3-B · Q4-D · Q5-A · Q6-C · Q7-B

**Rationale notes**

- **Q1**: A product of matrices is a matrix, so depth adds nothing without a non-linearity between layers.
- **Q2**: This is the symmetry problem. Random initialisation breaks it, scaled by He for ReLU or Glorot for tanh and sigmoid.
- **Q3**: A product of many factors below 0.25 shrinks towards zero, so early layers barely learn. ReLU has a derivative of 1 on its active side.
- **Q4**: Dropout is a training-time regulariser. With the usual inverted form, activations are scaled up by 1/(1 − p) during training so that nothing needs to change at inference.
- **Q5**: Stable input distributions let you use higher learning rates. At inference it uses running averages from training, not the batch's statistics.
- **Q6**: With y = x + F(x), the gradient flows through the addition unchanged, so it reaches early layers. A block that has nothing to add can learn F = 0.
- **Q7**: Adam keeps a running mean of gradients (momentum) and of squared gradients (as RMSprop does), with a bias correction for the first steps.

---

## R. Retrieval, ranking and recommenders (8 questions)

### R1

What does an inverted index map?

A. Each document to the terms it contains
B. Each term to the documents that contain it
C. Each query to its cached results
D. Each document to its embedding

### R2

In BM25, what does the parameter b control?

A. How quickly repeated occurrences of a term stop adding score
B. The weight of rare terms
C. The number of results returned
D. How strongly the score is normalised for document length

### R3

When does embedding search beat keyword search?

A. The query and the document express the same meaning in different words
B. The query is an exact product code
C. The corpus is small
D. The query contains a rare name

### R4

What does reciprocal rank fusion need from each result list?

A. Scores on a common scale
B. A trained weight for each retriever
C. Only each document's rank
D. Relevance labels

### R5

How does MRR differ from NDCG?

A. MRR needs graded relevance labels and NDCG does not
B. MRR looks only at the first relevant result, and NDCG scores the whole ranking
C. MRR ignores rank and NDCG does not
D. MRR is only for recommenders

### R6

A new item has just been added to the catalogue. Why does collaborative filtering struggle with it?

A. Its embedding is too large
B. It makes the interaction matrix dense
C. It is too similar to existing items
D. It has no interactions yet, so there is no signal to learn from

### R7

Why are large recommenders built in two stages?

A. A cheap retrieval stage cuts millions of items to hundreds, so a costlier ranker can score those
B. The first stage trains the second
C. It removes the need for negative examples
D. One stage handles new users and the other returning users

### R8

How does implicit feedback differ from explicit ratings?

A. It is rarer
B. It is always more accurate
C. It has no true negatives: an item never clicked is not known to be disliked
D. It cannot be used for matrix factorisation

**Answers R**: R1-B · R2-D · R3-A · R4-C · R5-B · R6-D · R7-A · R8-C

**Rationale notes**

- **R1**: A query looks up the posting list of each of its terms, so the search touches only documents that share a term with it.
- **R2**: b = 0 ignores length and b = 1 normalises fully. Term-frequency saturation is the job of k1.
- **R3**: Embeddings match on meaning. Keyword search wins on exact identifiers and rare names, which is why hybrid search runs both.
- **R4**: RRF sums 1/(k + rank) across lists. Ignoring the scores is what makes it robust when BM25 and cosine scores are on different scales.
- **R5**: MRR suits tasks with one right answer. NDCG takes graded relevance and discounts every position, so it suits lists the user reads through.
- **R6**: This is the cold-start problem. The usual fixes are content features, popularity fallbacks and some exploration.
- **R7**: Scoring every item with a heavy model is too slow. Retrieval is tuned for recall and ranking for precision at the top.
- **R8**: Clicks and views are plentiful but only positive. Missing entries are treated as weak negatives or sampled, with a confidence weight.

---

## S. Features, tuning, time series and metrics (8 questions)

### S1

What does the kernel trick let a support vector machine do?

A. Train without labels
B. Use inner products in a high-dimensional feature space without ever computing the features
C. Skip regularisation
D. Handle missing values

### S2

What is the main risk of target encoding a categorical feature?

A. It creates too many columns
B. It cannot handle unseen categories
C. It removes the order of the categories
D. It leaks the label into the feature unless computed inside each training fold

### S3

What is the test set for?

A. One final estimate of performance after every modelling choice is made
B. Choosing hyperparameters
C. Early stopping
D. Selecting features

### S4

Why does random search often beat grid search for the same budget?

A. It evaluates each configuration faster
B. It guarantees the optimum
C. Usually only a few hyperparameters matter, and random search tries more distinct values of each
D. It needs no validation set

### S5

How should you cross-validate a forecasting model?

A. Shuffle the rows and use k folds
B. Train on the past and validate on the block that follows, rolling the origin forward
C. Validate on the earliest block and train on the rest
D. Use leave-one-out on random rows

### S6

A forecast has a MASE of 1.2. What does that mean?

A. It is 20% better than the naive forecast
B. Its errors are 1.2 units on average
C. It explains 20% more variance than the naive forecast
D. Its errors are 20% larger than the naive forecast's

### S7

What is a guardrail metric in an experiment?

A. A metric that must not get worse while you try to move the target metric
B. The metric the experiment is designed to move
C. A metric that checks the randomisation
D. The long-term metric the company steers by

### S8

What is Simpson's paradox?

A. A significant result that does not replicate
B. A correlation produced by a hidden common cause
C. A trend that holds in every segment and reverses in the combined data
D. An effect that fades over time

**Answers S**: S1-B · S2-D · S3-A · S4-C · S5-B · S6-D · S7-A · S8-C

**Rationale notes**

- **S1**: The algorithm only needs inner products between examples, and a kernel returns them directly, so a non-linear boundary costs no explicit feature map.
- **S2**: The encoding is built from the target. Fitted on all rows, each row's own label leaks into its feature, most of all for rare categories.
- **S3**: Any choice made on the test set biases its estimate upwards. Tuning belongs to the validation set or to cross-validation.
- **S4**: A grid repeats the same few values of the important hyperparameter across every setting of the unimportant ones.
- **S5**: Shuffled folds let the model train on the future. A rolling origin keeps every validation block after its training data.
- **S6**: MASE divides the model's mean absolute error by that of a naive forecast, so anything above 1 loses to the naive baseline.
- **S7**: Latency, unsubscribes and refunds are typical guardrails. The last option is the north star.
- **S8**: It arises when the segments differ in size between the groups compared, so the mix drives the aggregate. Compare within segments.

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

Each section was written against a topic guide that has since folded into the pillar notes. Check an answer against the note:

| Section | Pillar notes |
|---|---|
| A | [programming](../../../../programming/README.md) |
| B | [classical ML](../../../../data-science/01-classical-ml/README.md) |
| C | [LLM fundamentals](../../../../generative-ai/01-llm-fundamentals/README.md) |
| D | [RAG](../../../../generative-ai/02-rag-retrieval/README.md) |
| E | [harness](../../../../ai-engineering/03-harness-engineering/README.md), [loop](../../../../ai-engineering/04-loop-engineering/README.md), [graph](../../../../ai-engineering/05-graph-engineering/README.md) |
| F | [context](../../../../ai-engineering/02-context-engineering/README.md) |
| G | [eval](../../../../generative-ai/08-eval/README.md), [observability](../../../../generative-ai/06-observability/README.md) |
| H | [safety](../../../../ai-engineering/09-safety-and-security/README.md) |
| I | [data engineering](../../../../data-engineering/README.md) |
| J | [system-design round](../system-design-round/study-guide.md) |
| K | [scoping an AI product](../../../../generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product.md) |
| L | [probability and statistics](../../../../data-analytics/02-probability-and-statistics/README.md) |
| M | [probability and statistics](../../../../data-analytics/02-probability-and-statistics/README.md), [experimentation](../../../../data-analytics/03-experimentation-and-causality/README.md) |
| N | [classical ML](../../../../data-science/01-classical-ml/README.md) |

Open-ended companions to this bank live in [questions.md](questions.md); the
study plan is in [study-guide.md](study-guide.md). Sections L, M and N pair with the short-answer
and worked problems in [stats-ml-bank.md](stats-ml-bank.md) and the [cheat sheet](stats-ml-cheat-sheet.md).
