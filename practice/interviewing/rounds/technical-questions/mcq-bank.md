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

A Python service runs four threads doing pure CPU-bound numeric work on an 8-core
machine, and throughput is no better than single-threaded. Which change gives *true
parallelism* for that workload?

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

State the effect of Python's global interpreter lock (GIL) directly: what does it
constrain?

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

- **A1**: CPython's global interpreter lock (GIL) lets one thread run Python bytecode at
  a time, so CPU-bound threads take turns instead of using the eight cores. Nothing is
  deadlocked, and more threads would only add switching.
- **A2**: Each process has its own interpreter and its own GIL, so the work runs on
  several cores at once. `asyncio` and extra threads still execute one stream of
  bytecode at a time, and a `threading.Lock` has nothing to do with the GIL.
- **A3**: One thread switches between tasks while they wait on I/O, so many tasks make
  progress but only one runs at any instant. It does nothing for CPU work, and shared
  state can still change between two `await`s.
- **A4**: `requests.get` is synchronous — it blocks the event loop. The fix is `httpx`
  or another async client. Forgotten `await` and CPU-heavy work in a coroutine are the
  other two named pitfalls.
- **A5**: The result depends on the order in which threads interleave their reads and
  writes of the same data. Immutable data cannot race, and starvation is a scheduling
  problem, not a data one.
- **A6**: A race needs shared mutable state and unsynchronised access. A lock, immutable
  data and not sharing each remove one of those; more threads only add more
  interleavings.
- **A7**: A deque removes from the left in constant time. `list.pop(0)` shifts every
  remaining element, which is O(n) per pop and turns a BFS quadratic. Lists can pop from
  the front; it is the cost that rules them out.
- **A8**: Brute force checks every pair, O(n²). After an O(n log n) sort the two
  pointers cross the array once in O(n), so the sort dominates the total.
- **A9**: In a binary search tree everything in the left subtree is smaller than the
  node and everything in the right is larger, so visiting left, node, right emits the
  values in ascending order.
- **A10**: The local child check wrongly accepts a node deeper in the left subtree that
  exceeds the root. Bounds must be threaded down.
- **A11**: The distance from the head to the cycle's start equals the distance from the
  meeting point to the start, modulo the cycle length. Two pointers leaving the head and
  the meeting point at one step each therefore meet at the start.
- **A12**: With both optimisations the amortised cost is the inverse Ackermann function,
  which stays below 5 for any input you could store. That is effectively constant but
  not O(1) in the worst case; either optimisation alone gives O(log n).
- **A13**: Optimal substructure lets you build the answer from answers to subproblems,
  and overlapping subproblems are what make storing them pay. Sorted input with a
  monotonic predicate signals binary search, and the greedy-choice property signals a
  greedy algorithm.
- **A14**: Top-down follows the recurrence as written and computes only the states it
  needs, but deep recursion and call overhead hurt on large inputs. Bottom-up has no
  recursion and lets you keep only the last row or two of the table.
- **A15**: `WHERE` runs before `GROUP BY`, so it sees rows and cannot use an aggregate.
  `HAVING` runs after, so it sees groups and can filter on any aggregate, not only
  `COUNT`.
- **A16**: For the values 10, 10, 20: `ROW_NUMBER` gives 1, 2, 3; `RANK` gives 1, 1, 3;
  `DENSE_RANK` gives 1, 1, 2.
- **A17**: It numbers each user's rows newest first and keeps the whole row. `DISTINCT
  ON` is PostgreSQL only, the `HAVING` form is invalid because `created_at` is not
  grouped, and joining back on `MAX(created_at)` returns two rows when timestamps tie.
- **A18**: The row count stays at the left table's when each left row matches at most
  one right row. Ask "how many rows does this join produce?" before running it.
- **A19**: The GIL constrains *bytecode execution*, not the interpreter as a whole,
  which is why threads still help for I/O: a blocking socket or file read releases the
  GIL while it waits, so other threads run. CPU work never yields it, so CPU-bound
  threads run one at a time and `multiprocessing` is the fix.
- **A20**: The GIL constrains *bytecode execution*, not the interpreter as a whole —
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

- **B1**: Leakage is information in training that will not exist at prediction time. It
  makes every offline score better, so nothing looks wrong until the model fails in
  production, which is why it does more damage than the other three.
- **B2**: More folds only steady the estimate. If the leak is in the features or the
  preprocessing, every fold is leaked the same way. The other three each keep test
  information out of training.
- **B3**: Precision and recall ignore true negatives, so PR-AUC shows how well the rare
  class is found. ROC-AUC divides false positives by the huge number of negatives and
  keeps looking good, and accuracy rewards predicting the majority class.
- **B4**: A score means nothing until you know what a trivial predictor gets: 95%
  accuracy is no achievement when 95% of the rows are one class.
- **B5**: The L1 penalty has a corner at zero, so it pushes some weights exactly to zero
  and removes those features. L2 penalises squared weights, which shrinks all of them
  smoothly and almost never to zero.
- **B6**: Neural nets win with huge data or mixed modalities; convexity is not a GBM property.
- **B7**: PCA finds the linear directions of greatest variance and can transform new
  data. UMAP keeps near neighbours near, but the sizes of clusters and the distances
  between them in its plot are not reliable, so its output needs care before it is used
  as model features.
- **B8**: In covariate drift the inputs change while the rule from input to target
  holds, for example a new mix of customers. In concept drift the rule itself changes,
  so the same input now means a different outcome.
- **B9**: The order is load-bearing: leakage → train/serve skew → drift → survivorship →
  feedback loops → metric mismatch. Leakage is both most common and cheapest to check.
- **B10**: RMSE squares each error before averaging, so one large miss counts far more
  than several small ones. MAE counts each error in proportion to its size.
- **B11**: MAPE divides each error by the actual value, so an actual near zero gives an
  enormous or infinite percentage. Negative predictions are no problem, and no
  distribution of residuals is assumed.
- **B12**: Of the cases given a probability of 0.8, about 80% should turn out positive.
  A model can rank cases perfectly and still be miscalibrated, so a ranking metric does
  not show it.
- **B13**: The Brier score is the mean squared error of the predicted probabilities, and
  a reliability curve plots predicted probability against observed frequency. The other
  pairs measure clustering, feature attribution and ranking.
- **B14**: Sculley et al. describe debt that is specific to ML systems: entanglement
  (changing anything changes everything), hidden feedback loops where a model shapes its
  own future training data, and pipeline jungles of data-preparation glue. The other
  options are modelling problems, not system debt.
- **B15**: Bayes error is the lowest error any predictor could reach and cannot be
  measured directly. On tasks people do well, human error is close to it, so the gap
  between human and training error shows how much bias is avoidable. A model can beat
  human level, so it is not a ceiling.
- **B16**: Elbow and silhouette say how well separated the clusters are, not whether
  anyone can use them. If the operations team can run four campaigns, seven segments are
  no use to them.

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

In LLM inference, prefill processes the whole prompt in parallel and is cheap per token,
while decode emits one token at a time and is expensive. Which discipline follows
directly?

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

DPO skips the reward model and optimises preference pairs directly, where RLHF trains a
reward model and runs an RL loop. What is DPO's stated trade-off?

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

- **C1**: Each query is compared with each key by dot product, the scores are divided by
  √d (the key dimension) and passed through softmax, and the weights average the values.
  The scaling goes inside the softmax and uses √d, not d.
- **C2**: Dot products of d-dimensional vectors spread out more as d grows. Large scores
  push softmax towards putting all the weight on one token, where gradients vanish;
  dividing by √d keeps the spread roughly constant.
- **C3**: With n tokens there are about n² comparisons, so doubling the context roughly
  quadruples the attention work. Hallucination, tokenisation and forgetting have other
  causes.
- **C4**: Layer normalisation rescales activations and knows nothing about order.
  Learned embeddings add a vector per position, RoPE rotates queries and keys by
  position, and ALiBi subtracts a distance penalty from attention scores.
- **C5**: The causal mask stops each token attending to later ones, which is what lets
  the model be trained on next-token prediction and generate left to right.
  Bidirectional attention and masked-token prediction describe encoders such as BERT,
  and cross-attention describes encoder–decoder models.
- **C6**: The KV cache stores each layer's keys and values for tokens already processed,
  so they are not recomputed for the next token. Prompt caching keeps that stored state
  for a shared prefix from one request to the next.
- **C7**: Temperature 0 removes sampling, but the arithmetic still varies:
  floating-point sums come out slightly differently depending on batch, hardware and
  library version, and a tiny difference can flip the choice between two near-tied
  tokens. Seeds, top-p and top-k do not apply at temperature 0.
- **C8**: Prefill reads the whole prompt in one parallel pass. Decode produces one token
  per pass, and each pass waits for the one before, which is why output tokens cost more
  and set most of the latency.
- **C9**: Each output token is another sequential step, so latency grows with output
  length. Keep outputs short, and stream them so the reader sees the first token early.
- **C10**: A small draft model proposes several tokens and the large model checks them
  in one parallel pass, keeping those it agrees with. The output is what the large model
  would have produced, only sooner, and it uses more memory, not less.
- **C11**: The policy is optimised against a learned reward model, so it learns whatever
  that model scores highly, which is not always what people wanted, for example answers
  that sound agreeable or confident.
- **C12**: DPO and RLHF consume the *same* preference data. The difference is no reward
  model and no RL loop — "the common industry default now."
- **C13**: DPO drops the reward model and the RL loop and trains on the preference pairs
  directly, so training is steadier. What it gives up is the separate reward model, and
  with it some direct control over what is rewarded.
- **C14**: The model critiques and revises its own responses against a written set of
  principles, and preferences produced by a model replace those of human raters in
  training. This happens during training, not as a filter at inference time.
- **C15**: The ladder is prompting → few-shot → RAG → PEFT/LoRA → full fine-tune,
  ordered cheapest and least invasive first. They compose.
- **C16**: QLoRA loads the frozen base model in 4-bit precision and trains ordinary
  full-precision LoRA adapters on top, so a large model fits on one GPU. The adapters
  are not what is quantised.
- **C17**: LoRA freezes the base weights and trains two small low-rank matrices for each
  adapted layer. At typical ranks that comes to between a tenth of a percent and about
  one percent of the parameters.
- **C18**: Without access to the weights you cannot train on the preferences. The
  preferred answers become instructions and few-shot examples in the prompt, and test
  cases in the evals that check the behaviour holds.
- **C19**: Liu et al. (2023) found accuracy highest when the relevant passage sat at the
  start or the end of a long context and lowest when it sat in the middle. It concerns
  how the model uses its context, not truncation or retrieval.
- **C20**: A bigger window only gives more middle to lose things in. The fix is to put
  less, more relevant material in the context and to place what matters at the start or
  the end.
- **C21**: Temperature scales the logits before sampling — low values concentrate mass on
  the top tokens, high values flatten the distribution. It is not a length, latency, or
  capacity control. Note the interaction with **C7**: temperature 0 removes *sampling*
  randomness but not nondeterminism from batching, floating point, and hardware or version
  differences.
- **C22**: CoT buys reasoning quality by spending intermediate tokens — so it *raises*
  token usage and latency, which is why the token-usage and speed options are inverted
  traps. It reduces reasoning errors; it does not eliminate hallucination, since a
  fluent wrong chain is still wrong. It is a prompting-tier move, tried before RAG or
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

As an illustrative estimate rather than a benchmark, HyDE's cost is:

A. Roughly doubles total pipeline latency
B. One extra small-model call, ~100–200ms
C. Negligible — it reuses the main generation call
D. One extra embedding call only

### D18

As illustrative rule-of-thumb figures rather than benchmarks, multi-query (RAG-Fusion)
recall gain and its diminishing-returns point are:

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

- **D1**: Text has to be chunked before it can be embedded, and embedded before it can
  be indexed. Each optional stage sits where it acts: rewrite before retrieval, rerank
  after it, verify after generation.
- **D2**: Headings mark where the author changed topic, which is the cheapest reliable
  boundary. A section over the budget is then split at paragraphs and sentences, so no
  chunk breaks in the middle of a thought.
- **D3**: Semantic chunking embeds every sentence to find topic shifts, which adds cost
  at ingest, and where it cuts depends on a threshold that behaves differently from
  corpus to corpus. Structure-first splitting stays the default.
- **D4**: This is the bank's starting point, not a law: a chunk long enough to hold one
  complete idea and short enough that its embedding is about one thing, with an overlap
  of about an eighth so a sentence cut at a boundary survives whole in one chunk. Tune
  both on your own corpus.
- **D5**: A small chunk has a precise embedding, so it matches the query well. Its
  parent section gives the model enough surrounding text to answer from.
- **D6**: A minimum length meant to drop stray headers also drops a complete one-line
  answer, and nothing raises an error: the question simply never retrieves it.
- **D7**: E5 models were trained with those prefixes on each side, so leaving them out
  at inference quietly lowers retrieval quality.
- **D9**: Embeddings capture meaning, so they match paraphrases but blur a rare exact
  string such as an error code. BM25 matches tokens, so it does the opposite. This is
  the case for hybrid search.
- **D10**: RRF scores a document as the sum of 1/(k + rank) over the result lists. k =
  60 comes from the original paper (Cormack et al., 2009) and is the usual default; it
  flattens the gap between top ranks so one list cannot dominate.
- **D11**: BM25 scores are unbounded and change with query length, while cosine
  similarities sit in a narrow band. A weighted sum needs a normalisation tuned per
  corpus; ranks can be compared as they are.
- **D13**: CRAG grades the retrieved documents in a separate step and routes on the
  grade before generating, which is control flow you write. Self-RAG trains the model to
  make those decisions itself while it generates.
- **D14**: The model is fine-tuned to emit special tokens that say whether to retrieve,
  whether a passage is relevant and whether the output is supported. The other options
  describe multi-query expansion, a CRAG-style gate and GraphRAG.
- **D15**: The term is used loosely. Saying which meaning you intend stops you and the
  interviewer talking past each other, and shows you know the paper.
- **D16**: A question and its answer are worded differently. A made-up answer, even with
  the facts wrong, is written like the documents, so its embedding lands nearer to them
  than the question's does.
- **D17**: The hypothetical answer is one short generation by a small model before the
  search. It cannot reuse the main call, which runs after retrieval. The latency figure
  is the bank's estimate; measure it on your own stack.
- **D18**: Each rewrite reaches documents the original wording missed, but later
  variants overlap with earlier ones while each still costs a retrieval. The figures are
  the bank's rule of thumb; measure on your own corpus.
- **D19**: Building an entity graph costs model calls over the whole corpus and pays off
  for questions that connect many documents. A single fact is answered by one chunk, and
  a wiki's links are already a graph.
- **D20**: The order matters — golden-set recall@k, then embedding/corpus language match,
  prefix rules, chunk truncation, *then* hybrid + reranker, all before touching the LLM.
- **D21**: Faithfulness asks whether the answer is supported by the context, and answer
  relevancy whether it addresses the question. Context precision asks whether the
  relevant chunks rank high, and context recall whether the context holds what was
  needed. Two score the generator and two the retriever.
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

Task length is a design threshold. By the rule of thumb in the context-engineering note
on compression and compaction, beyond roughly what duration does crash recovery become
mandatory?

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

PRINCE (Bayer with Thoughtworks; Kulkarni, martinfowler.com, 2026) is cited as evidence
for:

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

- **E1**: From Anthropic's "Building effective agents": in a workflow your code decides
  the steps, and in an agent the model does. The number of calls and whether state is
  kept are not the distinction.
- **E2**: A task whose steps are known is cheaper, faster and easier to debug as a
  workflow. An agent earns its cost only when the steps cannot be known in advance.
- **E3**: The five are prompt chaining, routing, parallelization, orchestrator–workers
  and evaluator–optimizer. Retrieval is something you add to the model as a building
  block, not a workflow pattern.
- **E4**: Sectioning splits a task into independent parts that run at the same time.
  Voting runs the same task several times and combines the results.
- **E5**: In sectioning you write the split into the code. An orchestrator reads the
  task and decides the subtasks at run time, for example which files a code change has
  to touch.
- **E6**: The harness is what makes the model's work checkable and safe: what counts as
  done, what it may touch, the signals that tell it whether it is right, and a way to
  undo. The other lists are features of a framework or abilities of an agent.
- **E7**: Poka-yoke is the manufacturing term for mistake-proofing: shape the part so it
  only fits the right way round. For a tool that means changing the arguments so the
  error cannot be expressed, not catching it afterwards.
- **E8**: From Anthropic's "Building effective agents": the model made mistakes with
  relative paths once it had moved out of the root directory, so the tool was changed to
  require absolute paths and the mistakes stopped.
- **E9**: The longer a run, the more work a crash throws away and the more likely one
  is. Half an hour is the course's rule of thumb for where checkpoint-and-resume stops
  being optional.
- **E10**: Working memory is the current context, episodic is what happened in earlier
  sessions, semantic is facts, and procedural is how to do things, such as skills and
  instructions.
- **E11**: A missing memory makes the agent ask or look again. A wrong one is acted on
  with confidence and is hard to trace, so store less and check it.
- **E12**: A subagent's searching and tool output stay in its own context, and the
  parent receives only the result, which keeps the parent's window small. Speed and cost
  are side benefits.
- **E13**: MCP standardises how a model reaches tools and data. A2A standardises how
  separate agents find each other and hand over work.
- **E14**: At a 70% success rate per trial and k = 3, pass@k is 1 − 0.3³ ≈ 97% and
  pass^k is 0.7³ ≈ 34%. The same agent looks nearly perfect on one and unreliable on the
  other.
- **E15**: Users need it to work every time, not at least once in k tries. pass^k falls
  as k grows and shows the unreliability that pass@k hides.
- **E16**: It is cited as a production agent system, not as a research result: the
  system first searches, then answers questions over what it found, then acts. It is not
  evidence about reinforcement learning, memory stores or fine-tuning.
- **E17**: "Multi-agent" in industry means orchestration patterns, not MARL. If an
  interviewer uses the term loosely, disambiguate rather than play along.
- **E18**: A second call can only improve a draft if it can say what is wrong with it,
  which takes clear criteria. The other options describe parallelization, routing and
  prompt chaining.
- **E19**: Every tool adds description tokens and one more way to choose wrongly, and
  overlapping tools make the choice ambiguous. One generic tool moves the difficulty
  into its arguments, and mirroring endpoints exposes the backend's shape instead of the
  task's.
- **E20**: A right final answer may have come from deleting a test, skipping a check or
  luck. Only the path shows which.

---

## F. Context & cost (16 questions)

### F1

Prefix caching requires:

A. Semantically similar prompts
B. A byte-identical prefix
C. The same model and temperature
D. A dedicated cache endpoint

### F2

Prefix caching reuses only a byte-identical prefix of the prompt. What layout rule
follows?

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

The course insists cost be reported per successful task rather than per API call. Why
does that framing matter?

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

According to the harness-engineering note on tool design, skill/tool descriptions that
stay resident should be sized at roughly:

A. ~10 tokens
B. ~45 tokens
C. ~100 tokens
D. As long as needed for clarity

### F16

The course keeps skill and tool descriptions to a small token budget. Why does that
budget matter at all?

A. Long descriptions confuse the tokenizer
B. Every description sits in the prefix of every call — it is a fixed tax per request
C. Providers cap tool schema length
D. Shorter descriptions improve tool-selection accuracy monotonically

**Answers F**: F1-B · F2-B · F3-C · F4-B · F5-B · F6-B · F7-B · F8-B · F9-B · F10-B ·
F11-B · F12-B · F13-C · F14-B · F15-A · F16-B

**Rationale notes**

- **F1**: The cache is keyed on the exact tokens from the start of the prompt, so one
  changed character invalidates everything after it. Similar prompts do not count.
- **F2**: Whatever changes ends the cached prefix, so the parts that never change
  (system prompt, tools, documents) go first and the per-request parts last. A timestamp
  at the top defeats the cache.
- **F3**: On Anthropic's API, input tokens read from the cache are billed at about a
  tenth of the normal input price, so the cached part of a prompt costs about 90% less.
  Writing to the cache costs a little more than normal input.
- **F4**: The usage block reports how many input tokens were read from the cache, and
  zero means a miss. Latency is too noisy to tell you.
- **F5**: Prefix caching still runs the model and generates a fresh answer; it only
  skips re-reading the prefix. Semantic caching skips the model and returns an answer
  given earlier to a similar query.
- **F6**: "How do I cancel my order?" and "How do I cancel my subscription?" sit close
  together as embeddings and have different answers.
- **F7**: Anthropic's default is five minutes, refreshed each time the prefix is read,
  with a one-hour option at a higher write price. Caching therefore pays for requests
  that arrive close together, not ones hours apart.
- **F8**: The full order is prefix caching → model routing → streaming → semantic cache
  → compaction/offloading → output-length discipline → batch/offline. Lead with #1
  because it is lossless and large.
- **F9**: Streaming changes neither the tokens nor the total time. It shows the first
  token sooner, so the wait feels shorter. The other three reduce what you actually pay.
- **F10**: A call that fails still costs money, and one task may take several calls.
  Dividing total spend by the tasks that succeeded counts both.
- **F11**: A model at a third of the price that needs four attempts costs a third more
  per finished task than the expensive model that succeeds first time.
- **F12**: As the context grows, the model uses any one part of it less reliably: recall
  drops and early instructions are followed less. It is not about caches or stored
  state.
- **F13**: Decisions and constraints are short, and everything after depends on them.
  Lose one and the agent redoes or contradicts earlier work.
- **F14**: Tool outputs are the bulkiest content and the easiest to get back: the file
  can be read again and the search run again.
- **F15**: A name plus a line on what it does and when to use it is all that has to stay
  in the context; the full procedure loads when the task calls for it. About ten tokens
  is the course's figure for that resident line.
- **F16**: Descriptions are sent with every request whether or not the tool is used, so
  fifty tools cost fifty descriptions on each call. Shorter is not always more accurate:
  the description still has to say when to use the tool.

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

The course starts an eval set with 20–50 real failures. Why real failures rather than
synthetic cases?

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

According to the eval pillar's note on production and the maturity ladder, what share of
production traces should be scored?

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

As an illustrative rule of thumb rather than a measured figure, the split of deployment
effort is:

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

- **G1**: A task is one problem with its success criteria, a trial is one attempt at it
  (several, because outputs vary), and a grader is the logic that scores an attempt.
- **G2**: A code check is fast, cheap and gives the same result every time, so use one
  wherever it can be written. A model judge handles what needs judgement, and people
  cost the most, so they are used to calibrate the judge.
- **G3**: These are deterministic checks on parsing, schemas and how tool arguments are
  built. With no model call they are fast and free, so they can run on every commit.
- **G4**: Mocked tools make a run cheap and repeatable while still checking which tools
  the agent called, in what order and with what arguments.
- **G5**: Real dependencies make these runs slow, costly and flaky. Run them when the
  result decides a release and leave every commit to the cheaper tiers.
- **G6**: Three steps at 75% each gives 42% end-to-end. This is the arithmetic behind
  "agents fail at the seams" — and the argument for per-step reliability targets rather
  than a single end-to-end number.
- **G7**: A capability eval measures what the agent cannot yet do, so a low pass rate is
  room to improve. A regression eval protects what already works, so any drop is a
  signal.
- **G8**: Once a capability passes consistently it is no longer a target to reach but
  behaviour to protect, so it moves into the regression suite.
- **G9**: This is the course's starting size: enough cases to show a pattern and few
  enough to read every one. Starting small beats waiting for a large set.
- **G10**: Cases you invent test what you already thought of. Failures from real use
  show where the system actually breaks.
- **G11**: Files, state or cache left over from one trial can help or break the next.
  The trials would no longer be independent, and the pass rate would mean nothing.
- **G12**: If you tune the agent against a broken eval you optimize toward noise. Fix
  the measurement first, always.
- **G13**: This is the course's range: enough traces to catch drift and rare failures
  without paying to judge every request. A critical flow can be sampled more heavily.
- **G14**: A change can shift behaviour in ways the offline evals do not cover, so the
  course reviews every trace for the first two days and then goes back to sampling.
- **G16**: The number is the point of the section — most of the work is not the agent.
- **G17**: Langfuse can run on your own infrastructure, so traces holding user data
  never leave it. The comparison is as the bank cites it; check what each product offers
  now.
- **G18**: The outcome says whether the task was done. The trajectory says whether it
  was done safely and efficiently. Either one alone misses failures the other catches.

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

The course frames prompt injection as a source-to-sink problem, where you contain it and
do not detect it. Which answer to an interview question on injection is explicitly
called wrong?

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

In the bank's illustrative 9-step defence stack, input guardrails sit at position:

A. 1st
B. 4th
C. 8th
D. 9th

### H7

In the bank's illustrative 9-step defence stack, output validation sits at:

A. 2nd
B. 5th
C. 8th
D. 9th

### H8

In the bank's illustrative 9-step defence stack, continuous trace grading sits at:

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

The course names three boundaries to establish before shipping any agent: who can
trigger it, where it can act, and what it did. Which requirement does "what it did" map
to?

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

Best-of-N jailbreaking (Hughes et al.) reported attack success rates of 89% on GPT-4o
and 78% on Claude 3.5 Sonnet. What does that result imply for guardrail strategy?

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

- **H1**: In a direct injection the user types the attack. In an indirect one it is
  hidden in a web page, email, document or tool result that the agent reads, so the user
  may be the victim.
- **H2**: This is the section's thesis. Injection is not a spam-filtering problem. Trace
  the untrusted *source* to the dangerous *sink* and cut the path — capability
  restriction, dual-LLM, human approval on the sink.
- **H3**: The course's framing is that injection is contained, not detected, so an
  answer that only detects is the one called wrong. Trace the untrusted *source* to the
  dangerous *sink* and cut the path: capability restriction, dual-LLM, human approval on
  the sink.
- **H4**: The privileged model sees only trusted input and is the one that plans and
  calls tools. Untrusted content goes to the quarantined model, and its output is passed
  around as a variable the privileged model never reads.
- **H5**: The quarantined model is assumed to be compromised by whatever it reads, so it
  gets no tools. Injected text then cannot reach anything that can act.
- **H6**: Input guardrails screen a request before anything else spends effort on it or
  is exposed to it, so they come first in the bank's stack.
- **H7**: Output validation checks the response just before it leaves, after the model
  and the tools have run. Only the after-the-fact review follows it.
- **H8**: Grading traces happens after the response has gone. It does not block
  anything; it catches what the earlier layers missed, so it comes last.
- **H9**: A poisoned memory entry is written to a store and loaded again in later
  sessions, so the attack outlives the conversation. Poisoned context lasts only as long
  as that context window.
- **H10**: An attacker triggers a large number of expensive model calls. The service
  stays up and the bill grows. Budgets, rate limits and caps on loop iterations are the
  defences.
- **H11**: Who can trigger it is authentication and authorisation of callers, where it
  can act is scoped permissions and sandboxing, and what it did is the audit record.
- **H12**: You can only investigate or undo what was recorded. Rate limiting, scopes and
  authentication answer the other two questions.
- **H13**: The ladder runs from cheapest and least disruptive to most. A retry handles a
  transient error, a fallback model a provider outage, a simpler baseline gives a
  degraded answer, and a person comes last because that is slowest and costliest.
- **H14**: Cite the numbers. 89%/78% is the argument that no prompt-level filter is a
  boundary; it is a speed bump in front of one.
- **H15**: Best-of-N jailbreaking reached 89% on GPT-4o and 78% on Claude 3.5 Sonnet
  (Hughes et al.) by resampling variations of a prompt. A filter that falls to trying
  again is a speed bump, not a boundary, so containment in the architecture has to carry
  the load.
- **H16**: A model, like a person, can read "ignroe prevoius insturctions", but a filter
  looking for the exact phrase does not match it.
- **H17**: Input guardrails screen what comes in, output guardrails check what goes
  back, and action guardrails check a tool call before it runs.
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

When debugging "the dashboard number is wrong", the lineage walk checks source
freshness, then ingest dedup, then join fan-out, then metric definition drift. What is
the principle behind that ordering?

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

A feature store is justified by online/offline consistency (train/serve skew) and
feature reuse across teams. If neither condition holds, what does the course say?

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

- **I1**: An idempotent job gives the same result whether it runs once or five times,
  which is what makes retries and backfills safe.
- **I2**: An upsert writes by key instead of appending, a partition overwrite replaces a
  whole day's partition, and a dedup key drops a repeated event. Each makes a second run
  harmless.
- **I3**: Each rung adds what the one before lacked: scripts and tracked experiments
  make work reproducible, a pipeline automates it, CI/CD gates what ships, and
  monitoring closes the loop.
- **I4**: The order is by rising exposure. Shadow risks nothing a user sees, a canary
  risks a small share of users, and full rollout follows once both look right.
- **I5**: Shadowing lets you compare the new model's predictions and latency with the
  live model's on real inputs, with no risk to users. Routing a small share of live
  traffic is a canary.
- **I6**: "Evaluate against baseline → register *on pass*" is the load-bearing part. A
  registry that accepts unevaluated models is a filing cabinet, not a gate.
- **I7**: The layers run from outside in: is the service up and fast, have the inputs
  changed, has the relationship changed, and, once labels arrive, was the model right.
  Labels come late, so the first three are the early warnings.
- **I8**: An alert nobody acts on is noise. Tying a threshold to a defined action, such
  as retraining, gives every alert a consequence.
- **I9**: Each check costs more than the one before: freshness is one timestamp, dedup
  is a count, fan-out means comparing row counts across a join, and definition drift
  means reading the logic and asking people.
- **I10**: Cheap checks rule out common causes quickly. Here the cheapest-first order
  happens to match the pipeline's order, but cost is the rule.
- **I11**: A feature store solves two problems: the same feature computed one way in
  training and another in serving, and several teams rebuilding the same features. Data
  volume or streaming alone does not call for one.
- **I12**: A tested mart, a table of features built by the warehouse pipeline, gives one
  definition of each feature without another system to run.
- **I13**: Batch is simpler to build, test and rerun. Streaming adds ordering, late data
  and state, so pay for it only when the product needs data that is seconds old.
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

- **J1**: Five steps at about eight minutes each come to 40 minutes, which leaves the
  rest of the slot for introductions and your own questions.
- **J2**: The prompt is vague on purpose. Designing straight away means guessing the
  users, the scale and the constraints, and the interviewer is scoring whether you ask.
- **J3**: What it has to do, how big it has to be, and what limits it, such as latency,
  budget, compliance and team.
- **J4**: The answer decides what you optimise for in the rest of the round. Throughput
  and cloud provider are details, and RAG against fine-tuning is a solution offered
  before the problem is known.
- **J5**: Every later choice trades one of them against another, such as latency against
  accuracy. Written down, you can point at them when you justify a choice.
- **J6**: It shows you saw the alternatives, lets the interviewer steer, and ties your
  pick to a stated priority.
- **J7**: Every design has weak points. Naming them with a mitigation shows you know
  them; waiting for the interviewer makes it look as though you missed them.
- **J8**: The interviewer is often changing a constraint to see whether you can update.
  Revise the part it affects and say what changed and why; do not restart.
- **J9**: An honest flag costs little, and a bluff falls to one follow-up question. Then
  move to the part you do know.
- **J10**: Precision/recall is a *model* trade-off, not a system non-functional. The six
  axes are latency↔accuracy, cost↔quality, consistency↔availability,
  full-automation↔safety, read↔write throughput, storage↔caching.
- **J11**: The gateway is the front door, so it settles who is calling and how much they
  may use before any model work starts. The other options belong to orchestration,
  retrieval and output validation.
- **J12**: The five are caches, the state store, tracing and observability, the eval
  pipeline and the human-in-the-loop queue. A feature store belongs to the ML spine, not
  this reference architecture.
- **J13**: Cold start is the time taken to load a model before it can serve its first
  request, so the fix is to keep instances loaded. The other options are the mitigations
  for rate limits, queue backlog and index growth.
- **J14**: Numbers close the round. "p95 < 2s, faithfulness > 0.9" plus a
  future-improvements list separates a design from a drawing.
- **J15**: All four distractors are real practices — the question is which one targets
  *cascading* failure. A circuit breaker tracks the failure rate of a dependency and,
  once it crosses a threshold, **opens**: calls fail fast without touching the sick
  service. After a cooldown it goes **half-open**, admits a few probes, and either
  closes (recovered) or re-opens. That containment is the point. Timeouts bound a
  *single* call and are necessary but insufficient — with a dead dependency and a 30s
  timeout, in-flight requests still pile up until threads, connections, or queue depth
  are exhausted, and the caller dies too. Retries make cascades *worse* by multiplying
  load on an already-failing service unless paired with a breaker and jittered backoff.
  Exception handling is local error propagation, not a load-shedding mechanism. In the
  LLM stack this is the pattern behind provider fallback and the degradation ladder:
  trip the breaker on the primary model endpoint, route to the fallback, probe for
  recovery.

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

The intended answer to "Mistral 7B gives 90% of the accuracy, so why still pick it over
GPT-4?" is that the last 10% costs 20× and the use case's error tolerance does not need
it. When should you reverse that answer?

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

- **K1**: Start with who it is for, what problem they have, how you would know it worked
  and what limits you, all before any architecture.
- **K2**: It names an outcome, a target and a guardrail (CSAT), and no solution. The
  others name a technology, or an improvement with no target and nothing protected.
- **K3**: The units work out: tokens per query × dollars per token × queries per day
  gives dollars per day. None of the others is a cost of tokens.
- **K4**: "ROI, not model maximalism" — but the reversal is what shows judgment rather
  than a memorized slogan.
- **K5**: The cheaper model is the right pick while its errors are tolerable. When one
  error is expensive, the last 10% of accuracy is worth more than the price difference.
  "ROI, not model maximalism" still holds; the reversal is what shows judgment rather
  than a memorized slogan.
- **K6**: High volume gives savings and data, and a review step catches errors cheaply.
  Where a mistake cannot be undone, the cost of an error outweighs the saving.
- **K7**: One north star states the goal, driver metrics are what teams can move to
  reach it, and guardrail metrics must not get worse while they push.
- **K8**: Drivers are goal completion, no-touch rate, escalation rate, time-to-trust.
  Guardrails are hallucination rate, complaint rate, cost/interaction. The distinction
  matters: you optimize drivers and *veto* on guardrails.
- **K9**: When confidence is low: decline to answer instead of guessing, show the
  sources so the user can check, and hand over to a person.
- **K10**: Multiplying impact by confidence discounts uncertain bets, and dividing by
  effort gives return per unit of work. The veto stops a high score shipping something
  that harms a protected metric. The option with reach is RICE.
- **K11**: The 92% says nothing until you know how many errors that is at your volume,
  what each one costs, whether the 8% are harmless or catastrophic, and what the product
  does when it is wrong.
- **K12**: The opposite is true — beneficiary PII (immigration status, health, benefits)
  is higher-stakes, and consent/minimization is about trust with vulnerable populations,
  not a compliance checkbox.

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
