# 45-Minute Coding Challenge — Prep Brief

One attempt, no retake, timer starts on click. Auto-saves every 30s.

---

## First: what format is this?

**Unknown until you open it.** The reminders say paste is disabled and typing patterns are
tracked — that's proctoring language, and it suggests **no AI assistant and no interviewer**.
The four notes files (`comms.md`, `ai.md`, `approach.md`, `testing.md`) describe an
*AI-enabled, interviewer-present* format. Those may not apply here.

Spend the **first 60 seconds** determining which world you're in:

| Signal | Means |
|---|---|
| Chat panel / AI sidebar present | AI-enabled — the notes apply |
| Just an editor + problem statement | Solo timed assessment — narration is irrelevant, tests matter more |
| Existing codebase with files | Comprehension/debug format — like battleship |
| Empty function stubs | Build-from-scratch |
| "Run tests" button | Tests are the grader — make them pass, nothing else scores |

**No interviewer = no credit for narration.** Do not spend time writing explanatory comments
for an audience that isn't there. Put that time into tests and correctness.

---

## The three likely problem types

### 1. Codebase comprehension + debug (what battleship was)

Given working-ish code with seeded bugs. Read, find, fix.

**Method that worked on battleship:**

1. Read the data structures first — what state exists, keyed by what
2. Run the tests, note which fail
3. For each failure, trace the specific values, don't skim the logic
4. Look for **identical if/else branches**, **off-by-one pairs that appear to cancel**
   (`cells[1:]` with `len - 1`), and **slices that skip an element**
5. Fix one bug, re-run everything — never stack fixes

**Bugs hide behind the happy path.** A branch never exercised by the default run
(`horizontal=False` when main.py only places horizontally) is where they live.

### 2. DSA / algorithms (classic LeetCode shape)

Most likely if it's a solo timed assessment. Cover these — they're 80% of what appears:

| Pattern | Signal in the problem | Data structure |
|---|---|---|
| Hash map counting | "how many times", "duplicate", "anagram" | `dict` / `Counter` |
| Two pointers | sorted array, "pair that sums to" | two indices |
| Sliding window | "longest/shortest substring/subarray" | window + `dict` |
| BFS | "shortest path", "fewest steps", grid | `deque` |
| DFS / backtracking | "all combinations", "does a path exist" | recursion + `set` visited |
| Heap | "top K", "k largest/smallest" | `heapq` |
| Sorting first | "intervals", "merge", "schedule" | `sorted(key=...)` |
| Prefix sum | "range sum", "subarray sums to K" | running total + `dict` |

**Syntax you must not fumble** (this is what burns the clock):

```python
from collections import defaultdict, Counter, deque
import heapq

counts = Counter(items)                    # {item: count}
graph = defaultdict(list)                  # graph[k].append(v), no KeyError
q = deque([start]); q.popleft()            # BFS queue
heapq.heappush(h, (priority, item))        # min-heap; negate for max
heapq.nlargest(k, items, key=lambda x: x[1])
sorted(items, key=lambda x: (-x[1], x[0])) # desc by count, asc by name
seen = set(); seen.add(x)
for i, val in enumerate(items): ...
for a, b in zip(xs, ys): ...
{k: v for k, v in d.items() if v > 1}
```

### 3. Build a small system (classes + methods)

"Implement a `RateLimiter` / `Cache` / `Scheduler` / `Inventory`."

Model the data first, then the logic. Ask: what's the O(1) lookup I need, and what
structure gives it? Usually a `dict` plus one auxiliary structure — exactly the
`_occupied` (set, "is this taken?") + `_ships` (dict, "what belongs to this?") split
in battleship. **Two structures for the same data is normal when they answer
different questions.**

---

## The 45-minute plan

| Time | Do |
|---|---|
| 0–3 min | Read the whole problem. Identify format. Find the tests. Note the output signature exactly. |
| 3–6 min | Write down 3–5 steps. Note edge cases as you read: empty, single, duplicate, zero, max. |
| 6–30 min | Implement the simplest correct version. Run after each step. |
| 30–38 min | Edge cases + your own tests. Optimize only if a test demands it. |
| 38–45 min | Final full run. Clean up. Submit with time to spare. |

**Submit something working by minute 35.** A correct simple solution beats a half-finished
optimal one, every time. Optimize only after the simple version is green.

---

## Rules that carry over from the battleship drill

1. **Simplest correct thing first.** The linear sweep passed before the parity solver
   existed. Get green, then improve.
2. **Run after every meaningful change.** Never stack two untested edits.
3. **Read the test file** — it's the actual spec. Battleship's commented-out asserts
   told us the real contract (`len(shots) == total_shots()`, `< 36 shots`) before
   any of it was live.
4. **Check imports.** `NameError: ShotResult is not defined` cost four test errors
   from one missing name in an import line.
5. **Trace with real numbers, not variables.** "cells[1:] gives 2 cells, compared
   against 3" found the bug; "n minus one" didn't.
6. **A guard that seems dead may be load-bearing.** Remove it and test hard before
   concluding it's noise.
7. **Name the structures.** If asked to explain, say `_occupied`, `Set[Tuple[int,int]]`
   — not "it's stored on the board."

---

## Edge case checklist (30 seconds, run it every time)

- Empty input — `[]`, `""`, `{}`, `0`
- Single element
- All identical / all duplicates
- Boundaries — first index, last index, off both ends
- Negative numbers, zero
- Already-sorted and reverse-sorted
- Capacity/limit of exactly 0 and exactly 1

---

## If there IS an AI assistant

Then the notes files apply. Compressed:

- **One reprompt rule.** First attempt misses → rephrase once with specifics. Second
  miss → write it yourself. Never more than 2 minutes fighting one generation.
- **Prompt with your plan, not the problem statement.** "Implement BFS from the start
  position in the Grid class, return the path as a list of coords" — not "solve this."
- **Use codebase vocabulary** — real class and method names from what you read.
- **Ask for concise output**, minimal comments. Every extra line is one you must defend.
- **Scan generated code for the four failure patterns**: textbook-but-wrong-fit,
  verbosity, over-abstraction (base classes for two unrelated things), and correctness
  shortcuts (deleted tests, `any` casts, swallowed exceptions, hardcoded values).
- **Write it yourself if it's under 30 seconds.** Prompting a one-liner looks worse
  than typing it.

---

## If there IS an interviewer

- State the plan out loud before touching code: "three steps — model, then core, then edges."
- Narrate at inflection points only, ~1 statement per 30–60s. Decisions, surprises,
  corrections. Not keystrokes.
- "Let me think for a second" beats silence.
- Pivots get a reason: "brute force won't scale for phase three, switching to a heap."
- Ask for help rather than burning five minutes silently.

---

## The mental reset

You did well on battleship — you found both seeded bugs unaided, including one the
feedback model itself missed. Your gap was never diagnosis, it was **closing**: stating
the fix, naming the structure, finishing the sentence.

In a solo timed assessment that gap costs nothing. Just solve it, test it, submit early.
