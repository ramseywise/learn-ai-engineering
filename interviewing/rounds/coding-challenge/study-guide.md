# Coding Challenge — Study Guide

## The narration method

The #1 differentiator in live coding is not correctness — it's narration. An interviewer watching you code silently cannot tell if you're thinking or stuck. Narrating shows judgment.

**The plan → code → test cycle**:

1. **Before touching the keyboard**: restate the problem in your own words. Ask one clarifying question if scope is ambiguous. Say the approach out loud ("I'll use a sliding window because..."). State the expected complexity.
2. **While coding**: narrate decisions, not keystrokes. "I'm using a deque here because I need O(1) from both ends" beats "now I'm adding a deque." Flag when you're making a tradeoff.
3. **After the first pass**: say "let me trace through a small example before I declare this done." Do it. Then say "let me check the edge cases" — empty input, single element, max values.
4. **When stuck**: say "I'm going to think through this for a moment" or "let me write a simpler version first and optimize." Never go silent for more than 30 seconds without a verbal update.

The goal is that the interviewer always knows where you are.

---

## Debugging methodology

The systematic method — not intuition:

1. **Reproduce first**: write the minimal input that triggers the bug. If you can't reproduce it, you don't understand it yet.
2. **Read the error honestly**: don't interpret, read. What does the traceback actually say? Where is line N?
3. **Bisect, don't read top-to-bottom**: add a print/assertion at the midpoint. Is the state correct there? If yes, the bug is downstream. If no, it's upstream. Repeat.
4. **Fix the root cause, not the symptom**: if the output is wrong, find where it first goes wrong — don't patch the output.
5. **State how you'd prevent regression**: "I'd add an assertion here that checks X invariant" or "this should be a property-based test with random inputs."

**The "quit thinking and look" rule**: when you have a hypothesis, check it immediately. Don't reason further from an unchecked assumption.

---

## Python fluency checklist

Have these cold — interviewers notice when you fumble basics:

**Collections**:
- `collections.OrderedDict` — move_to_end(), popitem(last=True)
- `collections.defaultdict(list)` — skip the key existence check
- `collections.deque(maxlen=N)` — O(1) appendleft/popleft
- `collections.Counter` — most_common(N), arithmetic
- `heapq.nlargest()` / `heapq.nsmallest()` — when to use vs sorted()

**Comprehensions and generators**:
- Dict/set comprehensions — `{k: v for k, v in items if condition}`
- Generator expressions — `(x for x in range(N))` — know when they save memory
- Nested list comprehension vs nested loop — when each is clearer

**Functions**:
- `functools.wraps` — required on every decorator
- `functools.lru_cache` / `functools.cache` — know the difference
- `*args, **kwargs` — forwarding patterns
- Default argument mutation gotcha: `def f(x, seen=set())` — the set is shared across calls

**Error handling**:
- `except SpecificException as e` — never bare `except:`
- `finally` for cleanup vs `contextlib.contextmanager`
- Custom exceptions: subclass `Exception`, not `BaseException`

**Dataclasses**:
- `@dataclass(frozen=True)` for hashable records
- `field(default_factory=list)` — not a mutable default
- `__post_init__` for validation

**Time**:
- `time.monotonic()` for durations (not `time.time()` — wall clock drifts)
- `datetime.timezone.utc` — always timezone-aware; never naive datetimes in production code

---

## Complexity analysis cheat sheet

**When to state it**: after you've named your data structure choice. "I'm using a hash map here, so lookups are O(1) amortized."

**How to narrate optimization**: "The naive approach is O(n²) because we're doing a linear scan inside the loop. We can get to O(n log n) by sorting first, or O(n) with a hash set." State the tradeoff in words before switching approaches.

**Common patterns to know cold**:
- Sliding window → O(n) for subarray problems
- Two pointers → O(n) for sorted array problems
- Binary search → O(log n) when input is sorted or answer is monotonic
- BFS/DFS → O(V+E) for graph problems
- Heap/priority queue → O(n log k) for top-k problems
- Dynamic programming → memoization turns O(2^n) to O(n) or O(n²)

**Space complexity**: always mention it. "This is O(n) time and O(1) space because I'm modifying in place" is a complete answer.

---

## Tests-first discipline for project-style problems

When the prompt is "implement X" (not "solve this algorithm"), tests-first is expected at the AIE/MLE level.

**The sequence**:
1. Define the interface (function signature or class API) — don't implement yet
2. Write the happy-path test
3. Write the edge case tests (empty, single, max, error path)
4. Implement to make them pass
5. Refactor if needed — tests protect you

**Why this signals seniority**: it shows you think about contracts, not just logic. It also gives you a way to check your implementation as you go, which is faster than running it and hoping.

**Minimum test coverage for interview problems**:
- Happy path (nominal inputs)
- Empty/zero/null input
- Single-element input
- Max-scale input (even if just described, not run)
- Error path (what should raise vs what should return a sentinel)

---

## AI-assisted coding skills

For loops that allow or require an AI assistant:

**Prompt decomposition**: break the problem into 3–5 subtasks before prompting. Each prompt should ask for exactly one thing. "Write a retry decorator that catches ConnectionError and retries up to 3 times with exponential backoff and jitter" is one subtask.

**Output verification workflow**:
1. Read the output before running it — check types and control flow
2. Trace it mentally with a known input
3. Run it with a minimal test case you wrote before seeing the output
4. Only then integrate it into the larger solution

**When not to trust it**:
- Off-by-one boundary conditions (especially in pagination, sliding windows)
- Concurrency — generated code almost never handles thread safety
- Error handling paths — the happy path is usually correct, error paths often aren't
- Anything that requires domain knowledge (e.g., timezone handling, numeric precision)

**What the grader is watching**: not whether you used AI effectively, but whether you caught what it got wrong and whether your prompts showed that you understood the problem before you prompted.

---

## Per-role variant preparation

**AIE (AI Engineering)**: expect system-level code — clients, wrappers, retry/rate-limit infrastructure. AI-assisted variants likely. Project-style over algorithm.

**MLE (Machine Learning Engineering)**: scikit-learn pipeline idioms, numpy/pandas manipulation, metric computation. May include debugging a training loop or a data preprocessing bug.

**DS (Data Science)**: SQL and pandas heavy. "Parse this log file and report top-5 error codes" type problems. Expect GROUP BY logic in pandas, window functions in SQL.

**FDE (Full-Stack/Data Engineering)**: practical scripting under time pressure. File I/O, CLI tools, JSON parsing, subprocess calls. Speed and correctness over elegance.

---

## Practice plan

**Daily (2 weeks pre-loop)**:
- One debugging kata: write a function with a deliberate bug, fix it using the systematic method
- One Python fluency drill: pick one item from the checklist above and use it in a small program

**Weekly**:
- One project-style problem (rate limiter, retry decorator, ETL transform) — timed, narrated out loud, tests-first
- One pair-programming simulation: code with someone watching and giving hints

**Week before the loop**:
- Reread the per-role variant section — know which format you're likely to see
- One full mock session with a timer: 45 minutes, narrated, with tests

---

## Anti-patterns (what sinks candidates)

- **Coding silently**: the most common failure. If you haven't spoken in 60 seconds, say something.
- **Jumping to optimization**: solve it correctly first, then optimize. Saying "I know this is O(n²), let me get it working then we can optimize" is professional.
- **Not testing**: declaring "done" without tracing an example or running a test.
- **Ignoring edge cases**: empty input and single-element input break most first-draft solutions.
- **Fixing the symptom**: changing output formatting instead of finding where the data went wrong.
- **Defensive about the interviewer's hints**: when they say "what if the input is empty?", they're helping you. Incorporate it.
- **One giant AI prompt**: shows you don't know how to decompose problems, which is the actual skill being tested.
