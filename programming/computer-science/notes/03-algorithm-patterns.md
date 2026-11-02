---
origin: synthesis
sources:
  - "Jeff Erickson, Algorithms (2019), free online — https://jeffe.cs.illinois.edu/teaching/algorithms/"
  - "Python docs: bisect, functools.lru_cache, heapq — https://docs.python.org/3.14/library/bisect.html"
concepts: [two-pointers, sliding-window, binary-search, backtracking, dynamic-programming, greedy-intervals, graphs, monotonic-stack, memoization, topological-sort, dijkstra, union-find, quickselect]
confidence: high
cleaned: 2026-11-02
---
# 3 — Algorithm patterns

> Algorithm courses cover hundreds of named problems, but most of the code you'll write leans on about ten ideas. Each pattern here exists because a brute-force version does work it doesn't need, and each has a condition that has to hold for the shortcut to be correct. That condition is what's worth remembering, because it's what breaks when you apply the pattern from memory. All the examples are things a Python engineer might actually write: log windows, token budgets, pipeline ordering. The honest results are included too, so you'll see one place where the textbook answer loses to `set` and one where the clever greedy rule is simply wrong.

---

## Which pattern, and how to recognise it

Start by asking what's being thrown away. Brute force looks at every pair, every subset or every path. A pattern is a reason not to.

```text
What you have                                 Try                 It needs
--------------------------------------------  ------------------  ----------------------------
Two sorted sequences, or one scanned inward   Two pointers        Sorted order
Best contiguous stretch of a sequence         Sliding window      Shrinking helps monotonically
"Next greater" or a nesting relation          Monotonic stack     A value can settle its waiters
Smallest x for which a test passes            Binary search       The test flips exactly once
Choose a subset under constraints             Backtracking        A bound, or small input
Same subproblems recurring                    Dynamic programming Finite overlapping states
A rule that never needs undoing               Greedy              An exchange argument
Things connected to things                    Graph search        Marking what you've visited
Merging groups as links arrive                Union-find          Only ever merging
One order statistic                           Quickselect         Random pivots
```

## Two pointers

When inputs are sorted, a comparison tells you which side can't possibly match, so one pointer moves on and never comes back. Two sorted lists of lengths `m` and `n` take at most `m + n` steps and not `m * n`. That's the merge step of merge sort, and of a [sort-merge join](../../../data-engineering/01-storage-and-compute-foundations/notes/08-distributed-compute.md) in a query engine.

```python
import bisect
import random
import time


def intersect(a, b):
    """Both inputs sorted. Returns the shared values and the comparisons used."""
    out, i, j, steps = [], 0, 0, 0
    while i < len(a) and j < len(b):
        steps += 1
        if a[i] == b[j]:
            out.append(a[i])
            i, j = i + 1, j + 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out, steps


print(intersect([2, 5, 9, 14, 30], [5, 6, 14, 15, 31]))

rng = random.Random(2)
a = sorted(rng.sample(range(5_000_000), 1_000_000))
b = sorted(rng.sample(range(5_000_000), 1_000_000))
start = time.perf_counter()
pairwise, steps = intersect(a, b)
t_merge = time.perf_counter() - start
start = time.perf_counter()
sets = sorted(set(a) & set(b))
t_set = time.perf_counter() - start
assert pairwise == sets
print(f"{len(a):,} x {len(b):,}: two pointers {t_merge * 1e3:.0f} ms ({steps:,} steps), set & {t_set * 1e3:.0f} ms")


def intersect_galloping(small, large):
    """For very unequal lists: binary-search each small value in the large list."""
    out, lo = [], 0
    for x in small:
        lo = bisect.bisect_left(large, x, lo)
        if lo < len(large) and large[lo] == x:
            out.append(x)
    return out


tiny = sorted(rng.sample(range(5_000_000), 1_000))
start = time.perf_counter()
one = intersect(tiny, b)[0]
t_two = time.perf_counter() - start
start = time.perf_counter()
two = intersect_galloping(tiny, b)
t_gallop = time.perf_counter() - start
assert one == two
print(f"{len(tiny):,} x {len(b):,}: two pointers {t_two * 1e3:.1f} ms, binary search per item {t_gallop * 1e3:.2f} ms")
```

<!-- measured -->

```text
([5, 14], 7)
1,000,000 x 1,000,000: two pointers 255 ms (1,799,840 steps), set & 135 ms
1,000 x 1,000,000: two pointers 130.6 ms, binary search per item 1.15 ms
```

There are two lessons here beyond the pattern. Two million sorted elements cost 1.8 million steps, as promised, yet `set(a) & set(b)` is about twice as fast. Both are linear, and the set work happens in C, so the constant from [chapter 1](01-cost-models-and-big-o.md#how-to-optimise-the-order-that-works) decides it. In Python, write two pointers when memory forbids building sets, when the inputs are sorted streams too large to hold, or when you need the merged order, and not for speed on in-memory lists.

The third line shows when the sizes differ a lot. With 1,000 items against a million, the two-pointer walk still crosses most of the long list, and binary-searching each small item is 100 times faster, at `m log n`. Search engines intersecting postings lists face the same choice, as does a retriever applying a filter.

The shape to remember is that each step discards at least one candidate, permanently. If you can't argue that, the pattern doesn't apply.

## Sliding window

A window over a sequence moves by adding on one side and removing from the other, so you maintain a running answer and don't recompute it. Each element enters once and leaves once. Here's a rate limiter's question: what's the most tokens spent in any 60 seconds of a log?

```python
import random
import time
from collections import deque


def busiest_window(log, seconds=60):
    """log: (timestamp, tokens), sorted by time. Max tokens in any window of that length."""
    window, total, best = deque(), 0, 0
    for t, tokens in log:
        window.append((t, tokens))
        total += tokens
        while window[0][0] <= t - seconds:
            total -= window.popleft()[1]
        best = max(best, total)
    return best


def busiest_brute(log, seconds=60):
    best = 0
    for i, (t, _) in enumerate(log):
        total = 0
        for s, tokens in log[i::-1]:
            if s <= t - seconds:
                break
            total += tokens
        best = max(best, total)
    return best


print(busiest_window([(0, 100), (10, 50), (59, 25), (60, 200), (130, 10)]))

rng = random.Random(4)
for n in (5_000, 10_000, 20_000):
    t, log = 0.0, []
    for _ in range(n):
        t += rng.expovariate(100)  # about 100 requests a second, so ~6,000 in a window
        log.append((t, rng.randrange(1, 4_000)))
    start = time.perf_counter()
    fast = busiest_window(log)
    t_fast = time.perf_counter() - start
    start = time.perf_counter()
    slow = busiest_brute(log)
    t_slow = time.perf_counter() - start
    assert fast == slow
    print(f"n={n:>7,}  window {t_fast * 1e3:7.1f} ms   rescanning {t_slow * 1e3:9.1f} ms")
```

<!-- measured -->

```text
275
n=  5,000  window     0.4 ms   rescanning     277.5 ms
n= 10,000  window     0.9 ms   rescanning     940.6 ms
n= 20,000  window     1.9 ms   rescanning    2492.0 ms
```

Rescanning costs `n * w`, where `w` is the number of entries in a window, about 6,000 here. It's why 5,000 to 10,000 more than triples and 10,000 to 20,000 less than triples: `w` stops growing once the log is longer than a window. So the cost is really `n * min(n, w)`, and an analysis that just says `O(n²)` would overestimate it at this scale. The window version scales linearly, at about 1,300 times faster for 20,000 rows.

The condition that makes this work is that the window can be repaired by subtraction, and that when you shrink it, you never need the removed items back. A maximum over a window can't be subtracted, so you'd pair it with the stack from the next section. If you're looking for a stretch with a target sum and the values can be negative, shrinking doesn't move the sum in a known direction and the pattern fails. Use prefix sums and a dict there.

## Monotonic stacks

For "how long until something bigger?", you could scan forward from each element, which is quadratic on a falling series. Instead, keep a stack of elements still waiting for an answer. When a new value arrives, it settles everything smaller on the stack. What remains stays in decreasing order, which is where the name comes from:

```python
def next_higher(samples):
    """For each sample, how many steps until a strictly higher one (0 if never)."""
    out, waiting = [0] * len(samples), []  # waiting: indices with decreasing values
    pushes = pops = 0
    for i, value in enumerate(samples):
        while waiting and samples[waiting[-1]] < value:
            j = waiting.pop()
            out[j] = i - j
            pops += 1
        waiting.append(i)
        pushes += 1
    return out, pushes, pops


print(next_higher([80, 75, 70, 90, 60, 65, 120]))
```

```text
([3, 2, 1, 3, 1, 1, 0], 7, 6)
```

The nested loop looks quadratic, but the counts show otherwise: 7 pushes and 6 pops, and an index can only be pushed and popped once. This is the same accounting as the [amortised analysis in chapter 1](01-cost-models-and-big-o.md#amortised-cost-and-when-its-the-wrong-number): you charge each pop to the push that paid for it. Whenever a nested loop looks too fast to be true, count the total work of the inner loop over the whole run, not per iteration.

## Binary search on the answer

Binary search isn't really about sorted lists. It finds the boundary of any test that flips once from false to true, with a fresh look at the middle each time. That makes it a tool for tuning: if you can check whether a value is good enough, you can find the limit in `log` checks. Here's a capacity question, where each check is a whole simulation:

```python
import bisect
import random


def first_true(lo, hi, ok):
    """Smallest x in [lo, hi) with ok(x), assuming ok is False...False True...True.
    Returns hi if there is none."""
    calls = 0
    while lo < hi:
        mid = (lo + hi) // 2
        calls += 1
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo, calls


def p95_wait_ms(rate, service_ms=8, n=4_000, seed=11):
    """One server, Poisson arrivals, fixed service time: simulated 95th percentile wait."""
    rng = random.Random(seed)
    now = free_at = 0.0
    waits = []
    for _ in range(n):
        now += rng.expovariate(rate / 1000)
        start = max(now, free_at)
        waits.append(start - now)
        free_at = start + service_ms
    waits.sort()
    return waits[int(0.95 * n)]


budget = 50
worst, calls = first_true(1, 1_000, lambda r: p95_wait_ms(r) > budget)
print(f"first rate over a {budget} ms p95 wait: {worst}/s after {calls} simulations")
for r in (worst - 10, worst - 1, worst, worst + 1, worst + 10):
    print(f"  rate {r:>4}: p95 wait {p95_wait_ms(r):7.1f} ms")

# bisect does the same search over any sequence, or with key=
print(bisect.bisect_left(range(1, 1_000), True, key=lambda r: p95_wait_ms(r) > budget) + 1)
```

```text
first rate over a 50 ms p95 wait: 99/s after 10 simulations
  rate   89: p95 wait    37.8 ms
  rate   98: p95 wait    49.5 ms
  rate   99: p95 wait    51.9 ms
  rate  100: p95 wait    53.6 ms
  rate  109: p95 wait    82.2 ms
99
```

Ten simulations give the answer from 999 possibilities. If each simulation took a minute, that's ten minutes and not sixteen hours. Note the half-open `[lo, hi)` convention: `hi` is never tested, the loop ends with `lo == hi`, and the result is the first true position or `hi` if none exist. Sticking to one convention removes most off-by-one bugs, and you can check it on empty and one-element ranges.

The last line shows that you rarely have to write it by hand. [`bisect`](https://docs.python.org/3.14/library/bisect.html) takes a `key` function and any sequence, including a `range`, so nothing needs materialising.

The condition is that the test has to be monotonic. A real queue's p95 isn't strictly monotonic in rate, because it's noisy. I fixed the seed above and checked rates 1 to 300 for this one, finding no violations. Under another seed or with fewer requests it may flip more than once, and then binary search returns a boundary and not necessarily the first. Use repeated seeds or a smoothed estimate when checks are noisy.

## Backtracking

Backtracking explores a tree of choices: make a choice, recurse, undo it. Without pruning it's exhaustive, so `2^n` for subsets. [Erickson's chapter](https://jeffe.cs.illinois.edu/teaching/algorithms/) frames it as making one decision at a time from a recursive description of the solution. Pruning is what makes it usable, and it's only correct if you only cut branches that can't beat what you already have:

```python
import random

rng = random.Random(21)
CAPABILITIES = range(16)
TOOLS = {f"tool{i:02}": set(rng.sample(CAPABILITIES, 4)) for i in range(18)}
NEEDED = set(CAPABILITIES)


def fewest(prune):
    names = sorted(TOOLS)
    # what the tools from position i onward could still add
    can_add = [set() for _ in range(len(names) + 1)]
    for i in reversed(range(len(names))):
        can_add[i] = can_add[i + 1] | TOOLS[names[i]]
    best, visited = None, 0

    def go(i, chosen, covered):
        nonlocal best, visited
        visited += 1
        if prune:
            if best is not None and len(chosen) + 1 >= len(best) and not covered >= NEEDED:
                return  # one more tool cannot beat the best so far
            if not covered | can_add[i] >= NEEDED:
                return  # the rest cannot finish the job
        if covered >= NEEDED:
            if best is None or len(chosen) < len(best):
                best = list(chosen)
            return
        if i == len(names):
            return
        chosen.append(names[i])  # choose
        go(i + 1, chosen, covered | TOOLS[names[i]])
        chosen.pop()  # undo
        go(i + 1, chosen, covered)

    go(0, [], set())
    return best, visited


plain, plain_visited = fewest(False)
pruned, pruned_visited = fewest(True)
assert len(plain) == len(pruned)
print(f"fewest tools: {len(plain)} {pruned}")
print(f"calls without pruning {plain_visited:,}, with pruning {pruned_visited:,}")
```

```text
fewest tools: 5 ['tool00', 'tool01', 'tool02', 'tool10', 'tool11']
calls without pruning 426,307, with pruning 875
```

Both find 5 tools, which agrees with the unpruned search. But the two prunes remove 99.8% of the calls. The second one is particularly strong, because a look-ahead table computed once makes the question "can the remaining tools still finish?" a single set operation. Those are the two general kinds of prune: "can't improve on the best so far", and "can't complete at all".

The `chosen.append`/`chosen.pop` pair is the essential mechanic: a single mutable list shared across the search, restored after each call. Mixing that up by storing `chosen` without copying it, in place of `list(chosen)`, is the classic bug, and it leaves a best answer that's empty by the end.

Set cover in general has no known fast exact algorithm, so for large inputs you'd switch to a greedy approximation and accept the difference. Exhaustive search is fine for tens of items if the bounds are strong, and the point of the measurement above is that you can't tell without trying.

## Dynamic programming

Erickson's framing is the useful one: dynamic programming isn't about filling in tables. It's recursion that doesn't repeat itself. You write the recursion first, and if it keeps meeting the same arguments, you store the answers. So work in this order: define what a subproblem means in one sentence, write the recurrence, then decide on memo or table.

Here's picking snippets for a prompt within a token budget. The subproblem is "best relevance from items `i` onward with `room` tokens left":

```python
from functools import lru_cache
import random
import time

# (name, tokens, relevance)
SNIPPETS = [("a", 60, 10), ("b", 100, 20), ("c", 120, 30), ("d", 30, 3), ("e", 200, 42)]


def best_table(items, budget):
    best = [0] * (budget + 1)  # best[room] for the items seen so far
    for _, tokens, value in items:
        for room in range(budget, tokens - 1, -1):  # backwards: each item used once
            best[room] = max(best[room], value + best[room - tokens])
    return best[budget]


print("best relevance within 300 tokens:", best_table(SNIPPETS, 300))
by_ratio, room, got = sorted(SNIPPETS, key=lambda s: s[2] / s[1], reverse=True), 300, []
for name, tokens, value in by_ratio:
    if tokens <= room:
        room -= tokens
        got.append((name, value))
print("greedy by relevance/token:", got, "total", sum(v for _, v in got))

rng = random.Random(6)
items = [("x", rng.randrange(50, 800), rng.randrange(1, 100)) for _ in range(200)]
print(f"\n{'budget':>9} {'table ms':>9}")
for budget in (10_000, 20_000, 40_000):
    start = time.perf_counter()
    best_table(items, budget)
    print(f"{budget:>9,} {(time.perf_counter() - start) * 1e3:>9.1f}")


# The same question with overlap: 22 snippets whose sizes are round numbers.
rng = random.Random(13)
ITEMS = [(rng.randrange(1, 11) * 50, rng.randrange(1, 100)) for _ in range(22)]
calls = 0


def plain(i, room):
    """Best relevance from ITEMS[i:] with `room` tokens left: choose or skip item i."""
    global calls
    calls += 1
    if i == len(ITEMS):
        return 0
    tokens, value = ITEMS[i]
    best = plain(i + 1, room)
    return best if tokens > room else max(best, value + plain(i + 1, room - tokens))


@lru_cache(maxsize=None)
def memo(i, room):
    if i == len(ITEMS):
        return 0
    tokens, value = ITEMS[i]
    best = memo(i + 1, room)
    return best if tokens > room else max(best, value + memo(i + 1, room - tokens))


start = time.perf_counter()
answer = plain(0, 2_000)
t_plain = time.perf_counter() - start
start = time.perf_counter()
assert memo(0, 2_000) == answer
t_memo = time.perf_counter() - start
print(f"\nplain recursion {calls:>10,} calls {t_plain * 1e3:9.1f} ms")
print(f"memoised        {memo.cache_info().misses:>10,} calls {t_memo * 1e3:9.1f} ms")
```

<!-- measured -->

```text
best relevance within 300 tokens: 62
greedy by relevance/token: [('c', 30), ('b', 20), ('a', 10)] total 60

   budget  table ms
   10,000      68.1
   20,000     138.3
   40,000     280.0

plain recursion  1,265,588 calls      72.8 ms
memoised               667 calls       0.3 ms
```

Three things to notice. First, the obvious greedy, best relevance per token, gets 60 and misses the optimum of 62, so that's not a safe shortcut. If a small gap is acceptable, though, it's much cheaper.

Second, the table is linear in the budget, which looks like a bug: time doubles as the number `40,000` doubles, though the input hasn't got any longer. The cost is `items × budget`, 8 million updates here at about 35 ns each. This is called pseudo-polynomial, since it's fast only while the number is small, and it's the reason you can't plug in a budget of a billion.

Third, compare the 1.27 million recursive calls with 667 memoised ones, which works here because the sizes are round numbers, so subproblems recur. Memoisation only saves work when states repeat. With sizes from 1 to 499, the same recursion ran with 20,058 distinct states and got 13,593 cache hits, a much smaller win, in exchange for a dict holding every state. [`functools.lru_cache`](https://docs.python.org/3.14/library/functools.html#functools.lru_cache) requires hashable arguments, and with `maxsize=None` it keeps everything for the life of the function.

The backwards loop in `best_table` is the subtle bit. Going from high `room` to low uses each item at most once, since `best[room - tokens]` still holds the previous row's value. Run it forwards and the item can be used repeatedly, giving a different problem without any error.

Many of these reduce to comparing two sequences. Longest common subsequence is what a diff computes, and here's a diff of two prompt versions:

```python
def lcs(a, b):
    rows = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            rows[i + 1][j + 1] = rows[i][j] + 1 if x == y else max(rows[i][j + 1], rows[i + 1][j])
    out, i, j = [], len(a), len(b)
    while i and j:  # walk the table back to recover the answer, not just its length
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i, j = i - 1, j - 1
        elif rows[i - 1][j] >= rows[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return out[::-1]


old = "You are a helpful assistant . Answer briefly .".split()
new = "You are a careful assistant . Cite sources . Answer briefly .".split()
keep = lcs(old, new)
print(keep)
print("removed:", [w for w in old if w not in keep], " added:", [w for w in new if w not in keep])
```

```text
['You', 'are', 'a', 'assistant', '.', 'Answer', 'briefly', '.']
removed: ['helpful']  added: ['careful', 'Cite', 'sources']
```

Filling in the table costs `len(a) * len(b)`, and that matters: two 100,000-line files need 10 billion cells. That's why real diff tools use more than this. And the answer comes from walking the table backwards, so you can't drop to a two-row table if you want the alignment and not only its length.

## Greedy, and the proof it needs

A greedy algorithm commits to the choice that looks best and never reconsiders. It's the fastest kind of algorithm when it's correct, and it's often not. Scheduling is the textbook case, here as reservations on one GPU. Three rules look plausible:

```python
import random

# GPU reservations: (start, end). Keep as many as possible on one GPU.
BOOKINGS = [(0, 6), (1, 3), (2, 4), (3, 5), (4, 7), (5, 9), (6, 8), (8, 10)]


def by_finish(bookings):
    chosen, free_at = [], float("-inf")
    for start, end in sorted(bookings, key=lambda b: b[1]):
        if start >= free_at:
            chosen.append((start, end))
            free_at = end
    return chosen


def by_rule(bookings, key):
    chosen = []
    for b in sorted(bookings, key=key):
        if all(b[1] <= c[0] or c[1] <= b[0] for c in chosen):
            chosen.append(b)
    return chosen


def brute(bookings):
    best = 0
    for mask in range(1 << len(bookings)):
        s = sorted(b for i, b in enumerate(bookings) if mask >> i & 1)
        if all(s[i][1] <= s[i + 1][0] for i in range(len(s) - 1)):
            best = max(best, len(s))
    return best


print("earliest finish:", by_finish(BOOKINGS))
print("earliest start: ", by_rule(BOOKINGS, lambda b: b[0]))
print("shortest first: ", by_rule([(0, 4), (3, 5), (4, 8)], lambda b: b[1] - b[0]), "from [(0,4), (3,5), (4,8)]")

rng = random.Random(8)
wins = {"finish": 0, "start": 0, "shortest": 0}
trials = 300
for _ in range(trials):
    bs = [(s, s + rng.randrange(1, 8)) for s in (rng.randrange(20) for _ in range(10))]
    best = brute(bs)
    wins["finish"] += len(by_finish(bs)) == best
    wins["start"] += len(by_rule(bs, lambda b: b[0])) == best
    wins["shortest"] += len(by_rule(bs, lambda b: b[1] - b[0])) == best
print(f"optimal in {trials} random cases:", wins)


def peak_concurrency(spans):
    events = sorted([(s, 1) for s, _ in spans] + [(e, -1) for _, e in spans])
    now = peak = 0
    for _, change in events:  # ends sort before starts at the same time: -1 < 1
        now += change
        peak = max(peak, now)
    return peak


print("peak streams:", peak_concurrency(BOOKINGS))
```

```text
earliest finish: [(1, 3), (3, 5), (6, 8), (8, 10)]
earliest start:  [(0, 6), (6, 8), (8, 10)]
shortest first:  [(3, 5)] from [(0,4), (3,5), (4,8)]
optimal in 300 random cases: {'finish': 300, 'start': 175, 'shortest': 285}
peak streams: 3
```

Only "earliest finish" is optimal in all 300 random cases, by comparison with a brute force. "Earliest start" is right in 175 and "shortest first" in 285, and an error rate that low is the dangerous kind, since a few tests would pass. The small example shows how it fails: a short booking straddling two longer ones blocks both.

[Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/) gives the proof, and the argument has a general form called an exchange. Take any optimal schedule. If its first booking isn't the one that finishes earliest, swap that one in. It ends no later, so nothing else clashes, and the schedule is the same size. Repeat for the rest. You've turned any optimal answer into the greedy one without losing anything.

So don't trust a greedy rule until you've either done that exchange or tested it against brute force on small random inputs, as this block does. The test takes minutes to write and caught two of three rules here.

The last line sweeps events in order, adding one per start and subtracting one per end. This gives peak concurrency for any set of spans, which is how you'd size a pool from a trace. Sorting tuples puts ends before starts at the same time, so a booking ending when another starts doesn't count as overlap.

## Graphs are one loop with a different bag

Dependency graphs, agent plans, call graphs and service topologies are all the same kind of thing. Erickson calls the general traversal whatever-first search: keep a bag of nodes to visit, take one out, mark it, and put its neighbours in. What you pick for the bag decides everything else. A stack gives depth-first search, a queue gives breadth-first search, and a priority queue gives Dijkstra's algorithm:

```python
import heapq
from collections import deque

PIPELINE = {
    "fetch": ["parse"],
    "parse": ["chunk", "extract"],
    "chunk": ["embed"],
    "embed": ["index"],
    "extract": ["index"],
    "index": [],
}


def whatever_first(graph, start, take):
    """take pops from the bag: the bag's discipline decides the search order."""
    order, marked, bag = [], set(), deque([start])
    while bag:
        node = take(bag)
        if node not in marked:
            marked.add(node)
            order.append(node)
            bag.extend(graph[node])
    return order


print("stack:", whatever_first(PIPELINE, "fetch", deque.pop))
print("queue:", whatever_first(PIPELINE, "fetch", deque.popleft))


def topological(graph):
    """Reverse postorder of a depth-first search. Raises on a cycle."""
    active, done, post = set(), set(), []

    def visit(node):
        if node in active:
            raise ValueError(f"cycle through {node}")
        if node in done:
            return
        active.add(node)
        for child in graph[node]:
            visit(child)
        active.remove(node)
        done.add(node)
        post.append(node)

    for node in graph:
        visit(node)
    return post[::-1]


print("build order:", topological(PIPELINE))
try:
    topological({**PIPELINE, "index": ["parse"]})
except ValueError as e:
    print("error:", e)

LATENCY_MS = {
    "client": [("edge-a", 12), ("edge-b", 4)],
    "edge-a": [("gateway", 3)],
    "edge-b": [("edge-a", 2), ("gateway", 20)],
    "gateway": [("model", 40), ("cache", 1)],
    "cache": [("model", 35)],
    "model": [],
}


def dijkstra(graph, source):
    dist, parent, heap, pops = {source: 0}, {}, [(0, source)], 0
    while heap:
        d, node = heapq.heappop(heap)
        pops += 1
        if d > dist[node]:
            continue  # a stale entry: we found a shorter way after pushing this one
        for next_node, weight in graph[node]:
            if d + weight < dist.get(next_node, float("inf")):
                dist[next_node] = d + weight
                parent[next_node] = node
                heapq.heappush(heap, (d + weight, next_node))
    return dist, parent, pops


dist, parent, pops = dijkstra(LATENCY_MS, "client")
path, node = ["model"], "model"
while node in parent:
    node = parent[node]
    path.append(node)
print("fastest:", dist["model"], "ms via", " > ".join(reversed(path)), f"({pops} heap pops)")
```

```text
stack: ['fetch', 'parse', 'extract', 'index', 'chunk', 'embed']
queue: ['fetch', 'parse', 'chunk', 'extract', 'embed', 'index']
build order: ['fetch', 'parse', 'extract', 'chunk', 'embed', 'index']
error: cycle through parse
fastest: 45 ms via client > edge-b > edge-a > gateway > cache > model (9 heap pops)
```

The "stack" and "queue" lines differ by one method name. BFS visits by number of hops, so it finds fewest-hop paths. DFS goes deep, and its finishing order is what topological sort needs: a node finishes after everything it depends on has finished, so reversed postorder is a valid build order. A node seen again while it's still active means a cycle, and that's the error you want, naming a node on the cycle, when someone wires an agent graph back on itself. Since each node and edge is handled once, all of these cost `V + E`.

Dijkstra's algorithm is the same loop with costs. A stale entry check does the work of the "decrease-key" operation that textbooks use, since `heapq` can't change a priority. That's why there are 9 pops for 6 nodes. Each edge costs at most one push, at `log` cost, so the total is `E log E`.

The result only holds if weights are non-negative. When a node comes off the heap, every other route to it passes through something on the heap, at least as far away, and non-negative edges can't make it shorter. A negative edge breaks that argument, and you get wrong answers with no error. Latencies are safe. Scores or log-probabilities used as weights may not be, so check.

For deep graphs, recursion hits the [limit from chapter 2](02-data-structures.md#stacks-and-the-one-you-already-use), so convert to an explicit stack.

## Merging groups: union-find

When links between items arrive one at a time and you want connected groups, such as near-duplicate clusters from a similarity join, re-running a graph search after each link is wasteful. Union-find keeps each group as a tree pointing to a root, and two small tricks keep the trees flat: attach the smaller to the larger, and repoint nodes at the root while you walk:

```python
import random
import time


class Clusters:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.parent[b] = a  # smaller tree under larger
        self.size[a] += self.size[b]
        return True


near_duplicates = [(0, 1), (1, 2), (3, 4), (5, 5), (2, 0)]
c = Clusters(6)
print([c.union(a, b) for a, b in near_duplicates])
print("clusters:", len({c.find(i) for i in range(6)}))

rng = random.Random(10)
print(f"{'pairs':>10} {'ms':>8} {'ns/op':>7}")
for n in (250_000, 500_000, 1_000_000):
    pairs = [(rng.randrange(n), rng.randrange(n)) for _ in range(n)]
    c = Clusters(n)
    start = time.perf_counter()
    for a, b in pairs:
        c.union(a, b)
    t = time.perf_counter() - start
    print(f"{n:>10,} {t * 1e3:>8.1f} {t / n * 1e9:>7.0f}")
```

<!-- measured -->

```text
[True, True, True, False, False]
clusters: 3
     pairs       ms   ns/op
   250,000     71.9     288
   500,000    203.9     408
 1,000,000    564.8     565
```

`union` returns `False` when a link adds nothing new, so the same call detects redundancy, and the 3 clusters are `{0, 1, 2}`, `{3, 4}` and `{5}`. The textbook bound is extremely close to constant per operation. I haven't read that proof for this chapter, so treat it as background and not as a claim I've checked. My measurement rises from 288 to 565 ns per operation as `n` quadruples, which is not constant. My guess is that it's cache misses from random access to larger lists, as [chapter 4](04-numbers-and-memory.md#locality-even-from-python) measures, but I didn't separate that out. The structure can only merge. Splitting a group isn't supported, and that's the condition to check.

## Selecting without sorting

Sorting answers every order question at once, which is more than you need if you want one percentile. Quickselect partitions around a random pivot and recurses into only one side. So the work is a shrinking series, `n + n/2 + n/4 + ...`, which is about `2n` on average, the same geometric sum from [chapter 1](01-cost-models-and-big-o.md#the-two-sums-that-pay-for-most-analysis):

```python
import random
import time


def select(values, k, rng=random.Random(1)):
    """The k-th smallest (0-based). Expected linear time: one side discarded per round."""
    items = list(values)
    while True:
        pivot = items[rng.randrange(len(items))]
        low = [x for x in items if x < pivot]
        same = [x for x in items if x == pivot]
        if k < len(low):
            items = low
        elif k < len(low) + len(same):
            return pivot
        else:
            k -= len(low) + len(same)
            items = [x for x in items if x > pivot]


rng = random.Random(12)
print(f"{'n':>10} {'select p99 ms':>14} {'sort p99 ms':>12}")
for n in (500_000, 1_000_000, 2_000_000):
    data = [rng.lognormvariate(4, 1) for _ in range(n)]
    k = int(0.99 * n)
    start = time.perf_counter()
    a = select(data, k)
    t_select = time.perf_counter() - start
    start = time.perf_counter()
    b = sorted(data)[k]
    t_sort = time.perf_counter() - start
    assert a == b
    print(f"{n:>10,} {t_select * 1e3:>14.1f} {t_sort * 1e3:>12.1f}")
```

<!-- measured -->

```text
         n  select p99 ms  sort p99 ms
   500,000           13.3         51.8
 1,000,000           43.6        110.2
 2,000,000           97.6        242.4
```

It wins by only 2.5 to 4 times here, because `sorted` is C and this is Python list comprehensions, and single runs are noisy since a pivot can be unlucky. In production, reach for a sort unless it shows up in a profile.

The randomness matters more than it seems. With a fixed pivot rule, an adversary or plain unlucky data can force one side to hold nearly everything, and that's quadratic. Erickson makes this remark about quicksort, and the same reasoning covers quickselect. With a random pivot, no fixed input is bad.

The other half of divide and conquer is the recurrence, already covered by [recursion trees in chapter 1](01-cost-models-and-big-o.md#recurrences-and-recursion-trees): what matters is the number of branches, how fast the problem shrinks, and how much work each level does.

## Pitfalls

- **Binary search over a test that isn't monotonic.** Symptom: an answer that changes with the seed or the bounds, and looks plausible each time.
- **Two pointers on unsorted input.** Symptom: matches go missing without an error. Assert sortedness in tests.
- **Sliding window with negative values.** Symptom: a sum-based window misses valid stretches.
- **A greedy rule tested only on friendly examples.** Symptom: it passes tests and is about 95% right. Compare against brute force on small random inputs.
- **Memoising on mutable or unbounded arguments.** Symptom: a `TypeError: unhashable type`, or a cache that grows for the process's life.
- **Saving a reference where you needed a copy in backtracking.** Symptom: the stored best is empty at the end, since the shared list was unwound.
- **Marking on removal without allowing for duplicates.** Symptom: a graph search with a much larger bag than expected. It's correct, but the check on pop is what keeps it so.
- **Dijkstra with negative weights.** Symptom: wrong distances, no exception.
- **Recursive DFS on a deep graph.** Symptom: `RecursionError` only on the largest input.

## Try it

1. Given two sorted timestamp lists, find all pairs within 5 ms of each other. Keep the total work close to linear when few pairs match.
2. Show with a small example why "earliest finish" fails if bookings have values and you want the highest total value. Which pattern does that version need?
3. Ten documents have sizes `[120, 400, 75, 300, 90, 250, 60, 500, 110, 95]` and must go in order into 4 batches. Find the smallest batch capacity using `first_true`.
4. Change `topological` so that its error names the whole cycle, rather than one node.

<details>
<summary>Answers</summary>

1. Keep `lo`, the first index in `b` not too early for the current `a` value. It only moves forward. From `lo`, scan forward while `b[j] <= x + 5`. `[10, 20, 31]` against `[6, 12, 15, 40]` gives `(10, 6), (10, 12), (10, 15), (20, 15)`. Work is `m + n + pairs`, so it's linear when few pairs match and larger when many do.
2. `(0, 10)` with value 100, against `(0, 1)` and `(1, 2)` with value 1 each. Earliest finish gets 2, the answer is 100. It needs dynamic programming: sort by finish time, and for each booking take the better of skipping it or adding it to the best answer that ends before it starts.
3. 640. Search `[max(sizes), sum(sizes) + 1)` with a test that packs in order and counts batches. The batches are `[120, 400, 75]`, `[300, 90, 250]`, `[60, 500]` and `[110, 95]`. The test is monotonic, as a larger capacity can't need more batches.
4. Keep the active path as a list as well as a set. On finding `node` in `active`, the cycle is the path from `node`'s position to the end, plus `node` again. With the extra edge in the block, it's `parse > chunk > embed > index > parse`, because `chunk` is visited first.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| When do two pointers work? | When sorted order lets each comparison discard a candidate permanently. `m + n` steps. |
| Two pointers or binary search for unequal lists? | Binary search each small item: `m log n` beats `m + n` when `m` is far smaller. |
| What must a sliding window satisfy? | It can be updated from what enters and leaves, and shrinking moves the answer in a known direction. |
| Why is a monotonic stack linear despite the nested loop? | Each index is pushed and popped at most once. Count total inner-loop work. |
| What's binary search on the answer? | Searching for the boundary of a monotonic yes/no test, in `log` tests. |
| What's the difference between DP and memoised recursion? | The same recurrence, evaluated in a different order. A memo runs only the states you reach; a table has predictable memory use. |
| Why is knapsack pseudo-polynomial? | Time is `items × budget`, and the budget is a number, so it's exponential in its digits. |
| How do you know a greedy rule is correct? | An exchange argument, or at the least agreement with brute force on many small random cases. |
| BFS, DFS, Dijkstra: how do they differ? | The bag: queue, stack, priority queue. All are one traversal loop. |
| When does Dijkstra fail? | With negative edge weights. It finalises a node on the assumption that later paths can't be shorter. |
| How do you detect a cycle in a dependency graph? | In a DFS, an edge to a node still active on the current path. |
| How do you get a percentile from a large list? | Quickselect gives expected linear time; a sort is simple and, in Python, often close enough. |

## Next

[4 — Numbers and memory](04-numbers-and-memory.md): what the values in those structures really are, in bits and in cache lines.
