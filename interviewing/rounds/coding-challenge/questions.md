# Coding Challenge — Question Bank

## Live Coding (project-style)

### 1. Implement an LRU cache

**Testing**: Data structure selection, API design, edge case handling.

**Approach**:
1. Clarify: capacity, eviction behavior, thread safety needed?
2. Choose `OrderedDict` (Python stdlib) — state why over a raw dict + linked list
3. Define `get(key)` and `put(key, val)` with O(1) contract
4. Handle capacity=0 edge case explicitly

**Key signals**: Knows `OrderedDict.move_to_end()`. States time complexity unprompted. Writes a quick smoke test before declaring done.

**Common pitfalls**: Implementing a linked list from scratch when `collections.OrderedDict` exists. Not handling the `key not found` path in `get`. Forgetting to evict on `put` when at capacity.

**Study refs**: `programming/Leet-Code/` (LRU Cache #146)

---

### 2. Rate limiter (token bucket or sliding window)

**Testing**: System-level thinking, state management, time handling.

**Approach**:
1. Clarify: per-user or global? burst allowed? Redis or in-process?
2. Token bucket: store `(tokens, last_refill_time)` per key; refill on each check
3. Sliding window log: store timestamps in a deque, evict entries older than window
4. State the tradeoff: token bucket = simpler/burstier; sliding window = precise

**Key signals**: Asks about persistence and concurrency. Uses `time.monotonic()` not `time.time()`. Handles the "first request ever" initialization case.

**Common pitfalls**: Using wall clock for rate math without noting the leap-second risk. Forgetting to handle concurrent access if in-process. Not exposing remaining-tokens in the return value.

**Study refs**: `data-engineering-mlops` (rate limiting in pipeline operators)

---

### 3. Retry decorator with exponential backoff

**Testing**: Decorator mechanics, error handling design, production-readiness instinct.

**Approach**:
1. Clarify: which exceptions to retry? max attempts? jitter? reraise on exhaustion?
2. Implement with `functools.wraps` to preserve metadata
3. Add `base_delay * (2**attempt) + random.uniform(0, jitter)` — name jitter's purpose
4. Log each retry with attempt number and exception
5. Write one passing test, one exhaustion test

**Key signals**: Mentions `functools.wraps`. Adds jitter unprompted and can explain it (thundering herd). Handles the "reraise original exception" case on exhaustion, not a generic one.

**Common pitfalls**: Silently swallowing the final exception. Not preserving the wrapped function's `__name__` and `__doc__`. Infinite retry on programmer errors (TypeError, etc.).

**Study refs**: `data-engineering-mlops` (pipeline resilience patterns)

---

### 4. Small ETL transform

**Testing**: Data pipeline instincts, schema validation, error handling at record level.

**Approach**:
1. Clarify: input format (JSON/CSV/parquet)? what constitutes a bad record? write failures or skip?
2. Read → validate schema → transform each record → write output
3. Track good/bad counts; emit a summary at the end
4. Use a dataclass or TypedDict for the record schema — show you're thinking about types

**Key signals**: Validates before transforming. Separates bad records into a rejection file rather than silently dropping. Adds row-level error context to rejections.

**Common pitfalls**: No schema validation at all. Crashing on first bad record instead of continuing. No output summary.

**Study refs**: `data-engineering-mlops` (ETL pipeline idioms)

---

### 5. API client with pagination

**Testing**: Iterator/generator design, HTTP retry integration, state handling.

**Approach**:
1. Clarify: cursor-based or page-number pagination? rate limits? auth?
2. Implement as a generator that yields items, handles `next_cursor` internally
3. Integrate exponential backoff on 429/5xx
4. Show how the caller stays clean: `for item in client.list_all(): ...`

**Key signals**: Uses a generator (caller doesn't need to know about pagination). Handles the "last page has no next cursor" sentinel correctly. Notes that retrying should happen at the page level, not the item level.

**Common pitfalls**: Returning a flat list (forces all pages into memory). Not handling the empty-result-set case. Retrying on 4xx client errors that aren't 429.

---

### 6. Streaming data processor

**Testing**: Memory-efficiency thinking, backpressure, stateful aggregation.

**Approach**:
1. Clarify: ordered stream? what's the aggregation window? what happens on late arrivals?
2. Use a generator pipeline: `source → filter → transform → aggregate → sink`
3. Each stage yields; nothing accumulates the full stream
4. State the tradeoff: simplicity vs. exactly-once semantics

**Key signals**: Does not `list()` the stream at any point. Can discuss what breaks if the source pauses (backpressure). Notes that generator pipelines don't handle fan-out or replay without additional machinery.

**Common pitfalls**: Loading the whole stream into memory before processing. No error handling inside the generator (swallows exceptions silently). Not handling the end-of-stream sentinel.

---

## Debugging

### 7. Broken deduplication script

**Setup**: A script that should dedupe records by ID but the output still has duplicates — or drops records it shouldn't.

**Testing**: Systematic isolation method, willingness to read error output honestly.

**Approach**:
1. Reproduce with a minimal input you control (2 records, same ID)
2. Read the actual output, not what you expect
3. Bisect: is dedup logic wrong, or is the write step wrong?
4. Common root cause: mutable default argument (`def dedup(records, seen=set())`), or hash collision in a custom `__hash__`, or records compared by identity not value
5. Fix root cause, not symptom; add a regression test

**Key signals**: Writes a minimal reproducer before reading the full code. States the hypothesis before checking it. Notes how to prevent this in a code review (mutable default argument is a common Python gotcha).

**Common pitfalls**: Changing code before reproducing. Fixing the symptom (force-sorting output) without finding why dedup failed. Not writing a test that would catch the original bug.

**Study refs**: `programming/Leet-Code/` debugging section

---

### 8. Race condition in shared state

**Setup**: A counter or cache that gives wrong results under concurrent load.

**Testing**: Understanding of concurrency primitives, comfort with non-determinism.

**Approach**:
1. Reproduce: write a tight loop that hammers the shared state from two threads
2. Identify the read-modify-write gap that creates the race
3. Fix with a `threading.Lock` or switch to an atomic operation (`queue.Queue`, `multiprocessing.Value`)
4. State when locks aren't enough (e.g., multiple shared variables that must move together → need a transaction)

**Key signals**: Can reproduce the race reliably. Knows that `+=` on an integer is not atomic in Python. Distinguishes between "this fixes it" and "this makes the race window smaller."

**Common pitfalls**: Adding a sleep to "fix" the race. Using a lock around only one of the two operations in a read-modify-write. Not testing the fix under concurrent load.

---

### 9. Off-by-one in pagination

**Setup**: A paginated fetch that skips the first record of every page or duplicates the last.

**Testing**: Boundary condition reasoning, ability to trace logic without running it.

**Approach**:
1. Trace with a 3-record dataset that fits in 2 pages of size 2
2. Check: is `offset` updated before or after the fetch? is the slice `[offset:offset+limit]` or `[offset+1:...]`?
3. Common root cause: `offset += limit` before appending, or `>` vs `>=` in the loop condition
4. Fix and trace again with the same 3-record dataset before declaring done

**Key signals**: Uses a concrete minimal example to trace. Checks both boundaries (first page, last page, single-record page). Writes an assertion, not just a print.

**Common pitfalls**: Tracing with mental math only (misses the bug). Fixing one boundary and breaking the other. Not checking the empty-final-page case.

---

### 10. Silent data corruption

**Setup**: A transform pipeline that produces numerically wrong outputs with no errors raised.

**Testing**: Instrumentation instinct, distrust of silence, validation discipline.

**Approach**:
1. Add assertions or invariant checks at each stage boundary
2. Bisect: does stage 1 output look right? stage 2?
3. Common root causes: integer division when float expected, timezone-naive datetime math, string → float coercion that rounds silently
4. Fix + add an invariant check that would have caught it

**Key signals**: Does not trust "no exception = correct." Instruments the pipeline before reading the transform code. States what invariant would prevent recurrence.

**Common pitfalls**: Reading the code top-to-bottom hoping to spot it (slow). Not pinning the stage where corruption enters. Fixing the immediate case without adding a guard.

---

## Pair Programming

### 11. Refactoring a tangled function

**Setup**: A 60-line function that does 4 things and has 3 levels of nesting. Tests pass.

**Testing**: Decomposition instinct, keeping tests green, communication with the interviewer.

**Approach**:
1. Read the tests first — they define "correct behavior"
2. Identify seams: name the 4 things the function does
3. Extract one at a time; run tests after each extraction
4. Rename variables once the structure is clear — not before

**Key signals**: Does not refactor and rename in the same step. Runs tests after every extraction. Talks through what they're about to do before doing it — lets the interviewer redirect.

**Common pitfalls**: Big-bang refactor without intermediate test runs. Renaming things that work (breaks tests). Not communicating the plan before starting.

---

### 12. Feature addition to existing code

**Setup**: A working module with tests. Add a new feature without breaking existing behavior.

**Testing**: How you navigate unfamiliar code, whether you ask or guess, how you integrate.

**Approach**:
1. Read the tests before the implementation — understand the contract
2. Identify where the new feature hooks in; ask the interviewer if unclear
3. Write the new test first, make it fail, then implement
4. Preserve existing test behavior — no editing existing tests unless they were wrong

**Key signals**: Reads tests before code. Writes a failing test for the new feature before implementing. Asks one clarifying question rather than guessing at ambiguous requirements.

**Common pitfalls**: Implementing without reading existing tests. Editing existing tests to make them pass. Not asking about edge cases in the new feature's spec.

---

### 13. Code review and inline fix

**Setup**: Interviewer shares a PR diff. Review it, then implement one fix together.

**Testing**: Review quality, constructive communication, collaborative editing.

**Approach**:
1. Scan for correctness issues first (not style)
2. Name two or three concrete issues with line references
3. For the collaborative fix: propose your approach, hear their input, adapt if they have a better angle
4. Leave a note about what a test for this fix would look like

**Key signals**: Prioritizes correctness over style. Does not critique the person, critiques the code. Integrates interviewer suggestions without defensiveness.

**Common pitfalls**: Only catching style issues. Being defensive about initial approach when interviewer offers a better one. Not proposing a test for the fix.

---

## AI-Assisted

### 14. Prompt decomposition task

**Setup**: "Use an AI assistant to implement X. We'll watch how you use it."

**Testing**: Whether you break the problem into verifiable chunks before prompting.

**Approach**:
1. Before prompting: decompose the problem into 3–5 concrete subtasks
2. Prompt one subtask at a time; verify each output before proceeding
3. State your verification method (run it, check types, trace a known input)
4. If output is wrong: diagnose whether the prompt was ambiguous or the model made an error

**Key signals**: Does not paste the full problem into one prompt. Verifies each piece before composing them. Can articulate what they're looking for in the output before they see it.

**Common pitfalls**: One giant prompt. Accepting output that "looks right" without running it. No plan for what to do when the output is wrong.

---

### 15. Verify and fix AI-generated code

**Setup**: You're handed AI-generated code for a function. Find the bugs.

**Testing**: Critical evaluation of generated output, ability to test without bias.

**Approach**:
1. Do not assume it's mostly right — read it as if it came from an untrusted source
2. Check: types, edge cases (empty input, max values), error paths
3. Write a test for each suspicious path before deciding it's a bug
4. Fix root causes; note if the prompt that generated it was underspecified

**Key signals**: Reads it skeptically, not charitably. Writes tests to confirm bugs before fixing. Notes what prompt change would have prevented the issue.

**Common pitfalls**: Trusting the structure because "AI wouldn't make that mistake." Fixing only the obvious bug and missing a second one. Not testing the fixed version.
