---
origin: synthesis
sources:
  - "Lehman, Leighton, Meyer, Mathematics for Computer Science, MIT 6.042 spring 2018, sections 14.1, 14.7, 22.4 — https://courses.csail.mit.edu/6.042/spring18/mcs.pdf"
  - "Jeff Erickson, Algorithms, recursion trees — https://jeffe.cs.illinois.edu/teaching/algorithms/"
  - "Python docs, Time complexity of built-in operations — https://docs.python.org/3/builtins/time-complexity.html"
  - "CPython 3.14.7, Objects/listobject.c — https://github.com/python/cpython/blob/v3.14.7/Objects/listobject.c"
  - "Gene Amdahl, Validity of the single processor approach, AFIPS 1967 — https://www3.cs.stonybrook.edu/~rezaul/Spring-2012/CSE613/reading/Amdahl-1967.pdf"
concepts: [cost-model, big-o, asymptotic-analysis, recurrences, recursion-tree, amortised-analysis, amdahls-law, performance-budget]
confidence: high
cleaned: 2026-11-02
---
# 1 — Cost models and Big-O

> A deduplication step that took 10 ms on your test file takes eleven minutes on the real one, and nothing in the code looks wrong. Without a way to predict that, you find out in production; with Big-O alone, you might spend a week on a change that saves nothing. This chapter teaches both halves: how to count work and read growth rates properly, including the small amount of math behind them, and how to turn a count into a time you can believe. Everything here ran on CPython 3.14.7 on an Apple M4 Pro with 24 GB of RAM, and your constants will differ.

---

## Count something before you time it

A cost model is a decision about what counts as one step. Choose it well and you can reason about a program without running it. The usual choice is that reading a variable, comparing two small values, or doing arithmetic on them costs one unit, and everything else is built from those. That's a fiction, as [chapter 4](04-numbers-and-memory.md) will show, but it's a useful one because the size of the input usually matters more than which step is slowest.

Here are two ways to ask whether a list of ids has a repeat. The first compares every pair. The second remembers what it has seen. Count the comparisons rather than the seconds, and the counts are exact and identical on every machine:

```python
def has_duplicate_scan(ids):
    checks = 0
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            checks += 1
            if ids[i] == ids[j]:
                return True, checks
    return False, checks


def has_duplicate_set(ids):
    checks, seen = 0, set()
    for x in ids:
        checks += 1
        if x in seen:
            return True, checks
        seen.add(x)
    return False, checks


print(f"{'n':>6} {'scan checks':>12} {'n(n-1)/2':>10} {'set checks':>11}")
for n in (1_000, 2_000, 4_000):
    ids = list(range(n))  # all distinct: the worst case for both
    print(f"{n:>6} {has_duplicate_scan(ids)[1]:>12} {n * (n - 1) // 2:>10} {has_duplicate_set(ids)[1]:>11}")
```

```text
     n  scan checks   n(n-1)/2  set checks
  1000       499500     499500        1000
  2000      1999000    1999000        2000
  4000      7998000    7998000        4000
```

The scan's count is a sum you can do by hand. The first element is compared with `n-1` others, the second with `n-2`, and so on, for `n(n-1)/2` in total. The set version does `n` checks, each of which we're treating as one step. [Chapter 2](02-data-structures.md) earns that assumption.

## The doubling test

Counting tells you the shape. To see whether the shape survives contact with a real machine, double the input and look at the ratio of the times. If `T(n)` is roughly `c * n^k`, then `T(2n)/T(n) = 2^k`, so `log2` of the ratio estimates the exponent `k` without you needing to know `c`. I reach for this before anything else, because it needs no theory about the code.

```python
import math
import platform
import random
import time


def best_of(f, *args, repeat=5):
    best = math.inf
    for _ in range(repeat):
        start = time.perf_counter()
        f(*args)
        best = min(best, time.perf_counter() - start)
    return best


def doubling(label, make, f, sizes):
    print(label)
    previous = None
    for n in sizes:
        t = best_of(f, make(n))
        slope = f"{math.log2(t / previous):5.2f}" if previous else "    -"
        print(f"  n={n:>9,}  {t * 1e3:9.2f} ms  log2(ratio)={slope}")
        previous = t


def quadratic(ids):
    seen = []
    for x in ids:
        if x not in seen:
            seen.append(x)


def linear(ids):
    seen = set()
    for x in ids:
        if x not in seen:
            seen.add(x)


def shuffled(n):
    return random.Random(1).sample(range(n * 10), n)


print(platform.python_implementation(), platform.python_version())
doubling("dedupe with a list", shuffled, quadratic, [2_000, 4_000, 8_000, 16_000])
doubling("dedupe with a set", shuffled, linear, [125_000, 250_000, 500_000, 1_000_000])
doubling("sorted()", shuffled, sorted, [125_000, 250_000, 500_000, 1_000_000])
```

<!-- measured -->

```text
CPython 3.14.7
dedupe with a list
  n=    2,000      10.78 ms  log2(ratio)=    -
  n=    4,000      43.48 ms  log2(ratio)= 2.01
  n=    8,000     172.68 ms  log2(ratio)= 1.99
  n=   16,000     690.83 ms  log2(ratio)= 2.00
dedupe with a set
  n=  125,000       4.68 ms  log2(ratio)=    -
  n=  250,000      10.24 ms  log2(ratio)= 1.13
  n=  500,000      24.80 ms  log2(ratio)= 1.28
  n=1,000,000      61.02 ms  log2(ratio)= 1.30
sorted()
  n=  125,000      11.64 ms  log2(ratio)=    -
  n=  250,000      25.79 ms  log2(ratio)= 1.15
  n=  500,000      58.50 ms  log2(ratio)= 1.18
  n=1,000,000     130.47 ms  log2(ratio)= 1.16
```

The list version's slope is 2.0 to two decimal places, so quadratic behaviour is about as clean as measurements get. That's also where the opening's eleven minutes comes from: 690 ms at 16,000 items, times 1,000 for 500,000 items if you extrapolate with `k = 2`, is about 11.5 minutes.

The other two rows are more instructive. `sorted` costs `n log n`, and that has a slope a bit above 1, which fits: `log2(2n)/log2(n)` is about 1.05 at this size, and the measured value is a little more. The set is the odd one. Theory says slope 1, and I measured 1.13 to 1.30. The analysis isn't wrong, but the cost model is. Those lookups stop being one unit once the table outgrows the CPU's caches, and at a million items each one is likelier to miss. [Chapter 4](04-numbers-and-memory.md#the-staircase) measures that staircase directly. A slope that doesn't match your prediction is telling you something about the machine or the code, so don't explain it away.

## The two sums that pay for most analysis

Two closed forms cover much of what you'll need. An arithmetic series, `1 + 2 + ... + n`, is `n(n+1)/2`: write it forwards and backwards, and each of the `n` columns adds to `n+1`. Any loop whose inner work grows by a fixed amount per step lands here, and it's quadratic.

A geometric series is more surprising. [Lehman, Leighton and Meyer](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf) derive it in section 14.1 by a perturbation trick. Let `S = 1 + x + ... + x^(n-1)`. Multiply by `x`, subtract, and all the middle terms cancel, leaving `S - xS = 1 - x^n`, so `S = (1 - x^n)/(1 - x)`. The result that matters for programmers is that with `x = 2`, the sum is `2^n - 1`, which is about twice its largest term. **In a series that grows geometrically, the last term dominates.**

This one fact explains why a growable array has to multiply its capacity and not add to it. Every resize copies what's there. Add a fixed number of slots and the copies form an arithmetic series. Multiply, and they form a geometric one:

```python
def copies_when_growing(n, grow):
    """Total elements copied to reach n appends, if every resize copies."""
    capacity, copied = 1, 0
    for size in range(1, n + 1):
        if size > capacity:
            copied += capacity
            capacity = grow(capacity)
    return copied


n = 1_000_000
print(f"arithmetic: sum(1..n) = {sum(range(1, n + 1)):,} = n(n+1)/2 = {n * (n + 1) // 2:,}")
print(f"geometric:  sum(2**i, i=0..19) = {sum(2**i for i in range(20)):,} = 2**20 - 1 = {2**20 - 1:,}")
print(f"\ncopies per append, to reach n = {n:,}:")
for label, grow in [
    ("add 1000 slots", lambda c: c + 1000),
    ("multiply by 2", lambda c: c * 2),
    ("multiply by 1.5", lambda c: max(c + 1, c * 3 // 2)),
    ("multiply by 1.125", lambda c: max(c + 1, c * 9 // 8)),
]:
    print(f"  {label:<18} {copies_when_growing(n, grow) / n:8.2f}")
```

```text
arithmetic: sum(1..n) = 500,000,500,000 = n(n+1)/2 = 500,000,500,000
geometric:  sum(2**i, i=0..19) = 1,048,575 = 2**20 - 1 = 1,048,575

copies per append, to reach n = 1,000,000:
  add 1000 slots       499.50
  multiply by 2          1.05
  multiply by 1.5        2.10
  multiply by 1.125      8.68
```

Adding a thousand slots at a time costs 500 copies per append, and that number keeps growing with `n`. Any factor above 1 gives a constant, and the constant is a trade against wasted space. CPython's list grows by about 1.125. This model counts every resize as a full copy, which is an upper bound for the real list: `listobject.c` calls `PyMem_Realloc`, which can sometimes extend a block where it sits.

## Big-O, stated properly

"`f` is `O(g)`" has a precise meaning, and most misuses come from forgetting it. It says there's a constant `c` and a threshold `n0` such that `f(n) <= c * g(n)` for every `n >= n0`. So Big-O is an upper bound on growth, ignoring constant factors and small inputs. `Ω` is the matching lower bound, and `Θ` means both. Saying a function is `Θ(n²)` is a stronger claim than `O(n²)`, because a linear function is also `O(n²)`. In conversation people say O when they mean Θ, and you should know which one you mean.

To show a claim like this, you only have to produce a witness:

```python
def f(n):
    return 3 * n**2 + 20 * n


# A witness for f = O(n^2): c = 4 and n0 = 20.
assert all(f(n) <= 4 * n**2 for n in range(20, 100_000))
print("first n where f(n) <= 4 n^2:", next(n for n in range(1, 1000) if f(n) <= 4 * n**2))
print("f(n)/n^2 as n grows:", [round(f(n) / n**2, 3) for n in (10, 100, 1000, 10_000)])

# 4^x is not O(2^x): the ratio is 2^x, and no constant bounds it.
print("4^x / 2^x:", [4**x // 2**x for x in (1, 10, 20, 30)])

# log bases differ by a constant factor; exponents do not.
from math import log

print("log2(n)/log10(n):", [round(log(n, 2) / log(n, 10), 4) for n in (10, 10**6, 10**12)])
```

```text
first n where f(n) <= 4 n^2: 20
f(n)/n^2 as n grows: [5.0, 3.2, 3.02, 3.002]
4^x / 2^x: [2, 1024, 1048576, 1073741824]
log2(n)/log10(n): [3.3219, 3.3219, 3.3219]
```

The last two prints come from pitfalls that section 14.7 of the [MIT text](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf) spells out. Constants can be ignored as multipliers but not in exponents: `2^x` and `4^x` differ by a ratio that grows without bound, so `4^x` isn't `O(2^x)`. On the other hand, the base of a logarithm is only a constant multiplier, which is why `O(log n)` never names one. The same section warns that an asymptotically faster algorithm isn't necessarily better on the inputs you have, which is the job of the rest of this chapter.

Big-O also says nothing about what `n` is. A text search that's `O(n + m)` has two sizes in it, and a "linear" scan over rows each holding a 10 KB string is linear in rows only if comparing strings costs nothing. Name the variable, and name all of them.

## Logarithms are what halving looks like

If you repeatedly halve something, the number of steps is the base-2 logarithm of its size, rounded up. That's where the `log n` in binary search and balanced trees comes from, and it's why these algorithms keep working at sizes where nothing else does.

```python
from math import ceil, factorial, log2


def halvings(n):
    steps = 0
    while n > 1:
        n = (n + 1) // 2
        steps += 1
    return steps


print(f"{'n':>15} {'halvings':>9} {'n log2 n':>16}")
for n in (1_000, 1_000_000, 1_000_000_000):
    print(f"{n:>15,} {halvings(n):>9} {n * log2(n):>16,.0f}")

# Why comparison sorting costs n log n: n! orderings, each comparison at most halves them.
for n in (10, 1_000, 100_000):
    lower = sum(log2(i) for i in range(2, n + 1))
    print(f"n={n:>7,}: lg(n!) = {lower:>12,.0f}   n lg n = {n * log2(n):>12,.0f}   ratio {lower / (n * log2(n)):.2f}")
```

```text
              n  halvings         n log2 n
          1,000        10            9,966
      1,000,000        20       19,931,569
  1,000,000,000        30   29,897,352,854
n=     10: lg(n!) =           22   n lg n =           33   ratio 0.66
n=  1,000: lg(n!) =        8,529   n lg n =        9,966   ratio 0.86
n=100,000: lg(n!) =    1,516,704   n lg n =    1,660,964   ratio 0.91
```

Going from a thousand items to a billion adds 20 steps. Multiplying `n` by a million adds 20 to the log, which you can check in your head from `2^10 ≈ 1000`.

The second table is the reason sorting by comparison can't beat `n log n`. There are `n!` possible orderings of `n` distinct items. Each comparison has two outcomes, so it can rule out at most about half of those remaining. Finding the right ordering therefore needs at least `log2(n!)` comparisons in the worst case, and the table shows that quantity closing in on `n log2 n`. This is a statement about every possible comparison sort, including ones that nobody has written. It's why [chapter 2](02-data-structures.md#sorting-exploits-what-is-already-ordered) can only beat it on inputs that aren't in random order, and why a sort that avoids comparisons entirely, such as radix sort on small integers, isn't bound by it.

## Recurrences and recursion trees

A recursive function's cost is defined in terms of itself: merge sort splits in two, sorts both halves and merges in linear time, so `T(n) = 2T(n/2) + n`. The method I find most useful for solving these comes from [Erickson's *Algorithms*](https://jeffe.cs.illinois.edu/teaching/algorithms/): draw the recursion as a tree and add up each level.

```text
T(n) = 2 T(n/2) + n

level 0                 n                       n
                     /     \
level 1           n/2       n/2                 2 * n/2  = n
                 /   \     /   \
level 2        n/4  n/4  n/4  n/4               4 * n/4  = n
               ...                              ...
level log2 n   1 1 1 1 1 1 1 ... 1              n * 1    = n

                                  total: n per level, log2 n + 1 levels
```

For the general form `T(n) = r T(n/c) + f(n)`, the level sums form a series, usually geometric, and the two-sums section tells you what happens: if they shrink, the root dominates; if they grow, the leaves do; if they're equal, you multiply by the number of levels. Compute all three cases and you can see each one:

```python
def levels(n, r, c, f):
    """Work per level of T(n) = r T(n/c) + f(n), for n a power of c."""
    out, nodes, size = [], 1, n
    while size >= 1:
        out.append(nodes * f(size))
        if size == 1:
            break
        nodes *= r
        size //= c
    return out


n = 2**10
for name, r, c, f in [
    ("T(n) = T(n/2) + n       ", 1, 2, lambda m: m),
    ("T(n) = 2T(n/2) + n      ", 2, 2, lambda m: m),
    ("T(n) = 3T(n/2) + n      ", 3, 2, lambda m: m),
]:
    work = levels(n, r, c, f)
    print(f"{name} first levels {work[:4]} last {work[-1]:>6,}  total {sum(work):>6,}")
```

```text
T(n) = T(n/2) + n        first levels [1024, 512, 256, 128] last      1  total  2,047
T(n) = 2T(n/2) + n       first levels [1024, 1024, 1024, 1024] last  1,024  total 11,264
T(n) = 3T(n/2) + n       first levels [1024, 1536, 2304, 3456] last 59,049  total 175,099
```

The first line is what you get when you throw away half the work each round, as selection does in [chapter 3](03-algorithm-patterns.md#selecting-without-sorting), and it's linear overall even though the first step alone already costs `n`. The second is merge sort. In the third, the leaves dominate: their count is `n^(log2 3) = n^1.585`, and that's the exact exponent of Karatsuba multiplication, which [Python's big integers use](04-numbers-and-memory.md#integers-that-dont-overflow). You'll measure it there.

This is the whole of the "master theorem" you need for everyday reasoning. The [MIT text](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf) (section 22.4) gives the fully general Akra-Bazzi result if you ever have unequal splits, but I've not needed to apply it to working code.

## Amortised cost, and when it's the wrong number

The Python docs [list `list.append` as amortised constant time](https://docs.python.org/3/builtins/time-complexity.html). Amortised means the average over a sequence of operations in the worst case, with no probability involved. By the geometric sum, `n` appends cost `O(n)` copies in total, so each one pays a constant share. An individual append can still cost `O(n)`, and you only see that if you measure each one:

```python
import statistics
import time


def next_capacity(size):
    """The growth rule from Objects/listobject.c, for an append reaching `size`."""
    return (size + (size >> 3) + 6) & ~3


clock = time.perf_counter_ns
n = 2_000_000
samples = [0] * n
items = []
for i in range(n):
    start = clock()
    items.append(i)
    samples[i] = clock() - start

# Replay the rule to find which appends had to resize.
resizes, capacity = [], 0
for size in range(1, n + 1):
    if size > capacity:
        capacity = next_capacity(size)
        resizes.append(size - 1)
at_resize = [samples[i] for i in resizes]

print(f"{n:,} appends, {len(resizes)} resizes")
print(f"mean over all     {statistics.fmean(samples):9.1f} ns")
print(f"median over all   {statistics.median(samples):9.1f} ns")
print(f"median at resize  {statistics.median(at_resize):9.1f} ns")
print(f"worst at resize   {max(at_resize):9.1f} ns")
print(f"worst overall     {max(samples):9.1f} ns")
worst = sorted(range(n), key=samples.__getitem__, reverse=True)[:100]
print("of the 100 slowest appends,", len(set(worst) & set(resizes)), "were resizes")
```

<!-- measured -->

```text
2,000,000 appends, 92 resizes
mean over all          55.8 ns
median over all        42.0 ns
median at resize      333.5 ns
worst at resize    136208.0 ns
worst overall      136208.0 ns
of the 100 slowest appends, 19 were resizes
```

The resizes do what the theory says: 92 of them across 2 million appends, and the mean of 56 ns hardly notices them. The worst one took 136 microseconds, thousands of times the median. If you're filling a list, that's irrelevant. If you hold a lock in a latency-sensitive loop, an amortised cost hides the number you care about.

The last line stopped me. Only 19 of the 100 slowest appends were resizes. The other 81 were ordinary appends that happened to be running when something else took the core: a timer tick, the garbage collector, another process. They aren't the list's fault, and an experiment that only counted operations would never reveal them. Reasoning about the algorithm gets you the shape, and measuring gets you what actually happens. You need both.

Keep these kinds of bound apart:

| Claim | Meaning | Example |
|---|---|---|
| Worst case | The slowest possible input of size `n` | `in` on a list: `n` comparisons |
| Average case | Averaged over assumed inputs. The assumption can be false | `dict` lookup, assuming hashes spread out |
| Expected | Averaged over the algorithm's own random choices, on any input | Quicksort with a random pivot |
| Amortised | Worst-case total over a sequence, shared out | `list.append` |
| Adversarial | Someone picks the inputs to hurt you | [Hash flooding](02-data-structures.md#hash-flooding-and-why-strings-are-randomised) turns the average case into the worst |

The docs' table lists `dict` get as `O(1)` on average and `O(n)` in the worst case. Chapter 2 builds a real input that reaches the second number.

## A budget for one request

Growth rates tell you which way things go, but you also need to know the size of the units. Here's what common operations cost on this machine. Each number includes about 14 ns of calling the lambda that wraps it, so read the first few as upper bounds:

```python
import hashlib
import json
import math
import platform
import re
import time


def per_second(f, budget=0.15):
    n, elapsed = 1, 0.0
    while elapsed < budget:
        n *= 2
        start = time.perf_counter()
        for _ in range(n):
            f()
        elapsed = time.perf_counter() - start
    return n / elapsed


a, b, c = 1.5, 2.5, 1.0  # names, so the compiler cannot fold the arithmetic
small = list(range(1_000))
as_set = set(small)
as_dict = {i: i for i in small}
record = {"model": "m", "tokens": 512, "latency_ms": 81.5, "ok": True}
encoded = json.dumps(record)
pattern = re.compile(r"(\d+) tokens")
line = "request 7781 used 512 tokens in 81 ms"
sixty_four = b"x" * 64
million = list(range(1_000_000))
rows = [
    ("empty function call", lambda: None),
    ("list index", lambda: small[500]),
    ("dict lookup (int key)", lambda: as_dict[500]),
    ("set membership", lambda: 500 in as_set),
    ("float multiply and add", lambda: a * b + c),
    ("`in` on a 1,000-item list", lambda: 999 in small),
    ("regex search on a log line", lambda: pattern.search(line)),
    ("sha256 of 64 bytes", lambda: hashlib.sha256(sixty_four).digest()),
    ("json.dumps a small dict", lambda: json.dumps(record)),
    ("json.loads the same", lambda: json.loads(encoded)),
    ("sum() a 1M-int list", lambda: sum(million)),
    ("sorted() a 1,000-int list", lambda: sorted(small)),
]
print(platform.python_version(), platform.machine())
for label, f in rows:
    rate = per_second(f)
    print(f"{label:<28} {rate:>14,.0f} /s  {1e9 / rate:>12,.0f} ns")
```

<!-- measured -->

```text
3.14.7 arm64
empty function call              70,978,768 /s            14 ns
list index                       59,448,824 /s            17 ns
dict lookup (int key)            36,242,365 /s            28 ns
set membership                   40,107,567 /s            25 ns
float multiply and add           40,075,569 /s            25 ns
`in` on a 1,000-item list           186,906 /s         5,350 ns
regex search on a log line        2,965,728 /s           337 ns
sha256 of 64 bytes                3,832,184 /s           261 ns
json.dumps a small dict           1,034,579 /s           967 ns
json.loads the same               1,470,228 /s           680 ns
sum() a 1M-int list                     422 /s     2,367,264 ns
sorted() a 1,000-int list           432,519 /s         2,312 ns
```

With this table you can do useful arithmetic in your head. A service with a 10 ms budget can do roughly 300,000 dict lookups, or 10,000 `json.dumps`, or 2,000 scans of a 1,000-item list per request, before any network call. A cold network round trip across a region costs what millions of dict lookups cost, which [chapter 6](06-networks.md#a-budget-for-a-cold-request) puts numbers on. So:

- Multiply the unit cost by the count, and write the answer down before you run anything.
- The most expensive operations in any request usually dwarf the rest. Find those first.
- `sum` over a million ints took 2.4 ms, which is 2.4 ns per item. A Python loop doing the same work takes several times longer per item, because of the interpreter around it. Crossing into C changes the constant, not the Big-O. [Chapter 4](04-numbers-and-memory.md#the-layout-decides-the-constant) measures that.

## Costs hidden in ordinary Python

Python's syntax doesn't show what things cost. `x in items`, `s += t`, `items[1:]`, `items.pop(0)` and `key in mapping` are all short, and they range from constant to linear. The [time complexity table](https://docs.python.org/3/builtins/time-complexity.html) has most of them. Two cases are worth running yourself, because they catch people out:

```python
import time


def timed(f, *args):
    start = time.perf_counter()
    f(*args)
    return (time.perf_counter() - start) * 1e3


def concat_local(n):
    s = ""
    for _ in range(n):
        s += "token "
    return s


def concat_shared(n):
    s = ""
    for _ in range(n):
        keep = s  # a second reference, so CPython cannot extend in place
        s += "token "
    return s


def concat_join(n):
    return "".join("token " for _ in range(n))


def slice_recursion(items):
    return 0 if not items else items[0] + slice_recursion(items[1:])


def index_recursion(items, i=0):
    return 0 if i == len(items) else items[i] + index_recursion(items, i + 1)


print(f"{'n':>8} {'s += x':>10} {'s += x, shared':>15} {'join':>8}   (ms)")
for n in (20_000, 40_000, 80_000):
    print(f"{n:>8,} {timed(concat_local, n):>10.2f} {timed(concat_shared, n):>15.2f} {timed(concat_join, n):>8.2f}")

import sys

sys.setrecursionlimit(20_000)
print(f"\n{'n':>8} {'items[1:]':>10} {'index':>8}   (ms)")
for n in (2_000, 4_000, 8_000):
    items = list(range(n))
    print(f"{n:>8,} {timed(slice_recursion, items):>10.2f} {timed(index_recursion, items):>8.2f}")
```

<!-- measured -->

```text
       n     s += x  s += x, shared     join   (ms)
  20,000       0.60           25.21     0.40
  40,000       1.30           81.54     0.76
  80,000       2.33          290.40     1.52

       n  items[1:]    index   (ms)
   2,000       6.35     0.11
   4,000      24.32     0.23
   8,000     119.50     0.43
```

String `+=` in a loop looks quadratic, since strings are immutable and each result is new. The first column shows it's nearly linear on CPython. The middle column shows why you can't rely on that: the moment something else holds a reference to the string, the time grows much faster than `n`. So the near-linear behaviour depends on no one else holding the string, which is an implementation detail you've now seen by experiment and that an unrelated change can remove. `"".join` is the one that's safe to reason about.

The slice recursion is a pattern I've seen in hand-written parsers. `items[1:]` copies the rest of the list, so a linear-looking recursion becomes an arithmetic series of copies. Its slope is about 2 and the index version's is 1. Slices, `list(x)`, `dict(x)`, `sorted(x)` and `x + y` are all loops, and it pays to read them as loops.

## How to optimise: the order that works

Here's a small job, summing tokens for users on a block list, written four ways. The second version applies the micro-optimisations people reach for first, and the third changes the data structure:

```python
import random
import time

rng = random.Random(7)
n = 20_000
# request logs: (user id, tokens). Find tokens for users on a block list.
log = [(rng.randrange(100_000), rng.randrange(1, 4_000)) for _ in range(n)]
blocked = [rng.randrange(100_000) for _ in range(2_000)]


def baseline():
    total = 0
    for row in log:
        if row[0] in blocked:
            total = total + row[1]
    return total


def constant_factor():
    total = 0
    local = blocked
    for user, tokens in log:  # unpack instead of index; local name
        if user in local:
            total += tokens
    return total


def better_algorithm():
    total = 0
    wanted = set(blocked)
    for row in log:
        if row[0] in wanted:
            total = total + row[1]
    return total


def builtin_boundary():
    wanted = set(blocked)
    return sum(tokens for user, tokens in log if user in wanted)


results = {}
for f in (baseline, constant_factor, better_algorithm, builtin_boundary):
    best = min(
        (lambda s: (f(), time.perf_counter() - s)[1])(time.perf_counter()) for _ in range(3)
    )
    results[f.__name__] = best
    print(f"{f.__name__:<18} {best * 1e3:9.2f} ms   {results['baseline'] / best:7.1f}x")
assert len({f() for f in (baseline, better_algorithm, builtin_boundary)}) == 1
```

<!-- measured -->

```text
baseline              210.72 ms       1.0x
constant_factor       210.67 ms       1.0x
better_algorithm        0.33 ms     637.6x
builtin_boundary        0.33 ms     630.3x
```

Local variables and tuple unpacking gained nothing measurable here, since nearly all the time is inside `in` on a 2,000-item list. Changing `blocked` to a set gained a factor of over 600. The order I use follows from that:

1. **Measure, and find where the time goes.** Use a profiler, as in [debugging and profiling](../../software-design/notes/06-debugging-and-profiling.md). The block above would show `in` straight away. Check whether the time is even on-CPU, because waiting on a network or lock needs a different fix.
2. **Stop doing the work.** Cache it, batch it, skip it, or move it out of the loop. A removed call is infinitely faster.
3. **Change the algorithm or data structure.** This is where the factors of hundreds come from, and it's chapters 2 and 3.
4. **Change the layout or cross into C.** Use `numpy`, `sum`, `join`, `sorted` or a columnar format. These give factors of 2 to 100, as in chapter 4.
5. **Use parallelism, if the work allows it.** See [chapter 5](05-processes-threads-and-io.md#what-parallelism-buys).
6. **Tune constants last,** on the part that's still hot, with a benchmark that you trust.

Before you start on step 3, work out what you can win at all. [Amdahl's 1967 paper](https://www3.cs.stonybrook.edu/~rezaul/Spring-2012/CSE613/reading/Amdahl-1967.pdf) argued in prose, about parallel hardware, that the part of the work you can't speed up sets the limit on the whole. The version in today's textbooks is a formula that I didn't find in the paper itself: if a share `p` of the time gets `s` times faster, the program as a whole speeds up by `1 / ((1 - p) + p / s)`.

```python
def speedup(p, s):
    """Whole-program gain when a fraction p of the time gets s times faster."""
    return 1 / ((1 - p) + p / s)


print(f"{'share p':>8} {'s=2':>6} {'s=10':>6} {'s=100':>7} {'limit':>7}")
for p in (0.05, 0.25, 0.5, 0.9, 0.99):
    print(f"{p:>8.0%} {speedup(p, 2):>6.2f} {speedup(p, 10):>6.2f} {speedup(p, 100):>7.2f} {1 / (1 - p):>7.1f}")
```

```text
 share p    s=2   s=10   s=100   limit
      5%   1.03   1.05    1.05     1.1
     25%   1.14   1.29    1.33     1.3
     50%   1.33   1.82    1.98     2.0
     90%   1.82   5.26    9.17    10.0
     99%   1.98   9.17   50.25   100.0
```

Read the 5% row as a warning: a hundredfold speedup of something that takes 5% of the time gains you 5%. If an LLM call is 95% of a request, then every optimisation of the code around it combined can only reach that same 5%. The right column is the ceiling, and it's often low enough to end the conversation.

## Pitfalls

- **Dropping the variable.** "It's linear" in what? Symptom: a job that's fine on many small documents falls over on one big one, since `n` was the document count and the cost was in characters.
- **Treating O(1) as cheap.** Symptom: replacing a 20-element list scan with a dict makes no measurable difference. On small `n`, constants win, and `n` is often small.
- **Trusting the doubling slope at one size.** Symptom: a slope of 1 on small inputs, then a jump. You've crossed a cache level or started swapping. Test at the size you run in production.
- **Quoting average-case bounds where inputs are hostile.** Symptom: a service using a user-controlled key format gets slow under a small amount of traffic.
- **Timing once, or timing a mean.** Symptom: results vary by 30% between runs. Take the best of several for algorithm comparisons, and report percentiles for latency, since the mean of the appends hid a 136 µs outlier.
- **Timing something the compiler folded.** Symptom: an impossibly fast benchmark. My first run of the budget table reported a float expression at the cost of an empty call, because `1.5 * 2.5 + 1.0` was computed at compile time. That's why it uses names now.
- **Optimising before counting.** Symptom: a week of tuning for a change that Amdahl's formula would have ruled out in a minute.

## Try it

1. Without running it, predict how many times `print` is called for `n = 100`: `for i in range(n): for j in range(i, n, 2): print(i, j)`. Then run it.
2. Work out the cost of `T(n) = 2T(n/2) + n²` from a recursion tree. Which level dominates? Check it by adding a row to the recursion-tree block.
3. Use the doubling test on `" ".join(words).split()` and on your own slowest helper function. Do the slopes match what you expected?
4. Build the growth experiment by hand in [the lab's `DynamicArray`](../practice/README.md), then see what happens if `pop` shrinks at half full rather than a quarter.

<details>
<summary>Answers</summary>

1. For each `i`, the inner loop runs `ceil((n - i) / 2)` times. That's `50 + 50 + 49 + 49 + ... + 1 + 1`, so `2 * (1 + ... + 50) = 2,550`. It's arithmetic, so quadratic.
2. Level `k` has `2^k` nodes of cost `(n/2^k)²`, which comes to `n²/2^k`. The levels shrink geometrically, so the root dominates and the total is about `2n²`, which is `Θ(n²)`. In the block, use `("...", 2, 2, lambda m: m * m)`, and the total comes to `2n² - n`.
3. Both should be close to 1, and your helper's slope is your own result. If it's near 2, look for a slice, `in` on a list, or a repeated copy.
4. Pop to just below half, then alternate append and pop. Every pair then resizes, since the shrink and the grow boundaries coincide, and a sequence of `n` operations costs `O(n²)` copies. The lab's test `test_pop_returns_last_and_shrinks_with_hysteresis` catches this.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What does `f = O(g)` actually say? | There's a constant `c` and a threshold `n0` with `f(n) <= c g(n)` for all `n >= n0`. It's an upper bound on growth, not a claim about speed. |
| O vs Θ? | O is an upper bound, Θ is tight. A linear function is `O(n²)` but not `Θ(n²)`. |
| Why doesn't the log base matter in Big-O? | Bases differ by a constant factor. Exponent bases don't: `4^x` isn't `O(2^x)`. |
| Why does a growable array multiply its capacity? | Total copies form a geometric series, so they're `O(n)` overall. Adding a fixed amount gives an arithmetic series, `O(n²)`. |
| What does amortised mean? | Worst-case total over a sequence, divided by its length. There's no probability involved, and a single operation can still be slow. |
| Why can't comparison sorting beat `n log n`? | There are `n!` orderings and each comparison splits them at most in half, so you need at least `log2(n!)`, which is `Θ(n log n)`, comparisons. |
| How do you solve `T(n) = 2T(n/2) + n`? | Recursion tree: `log2 n` levels, each costing `n`, so `Θ(n log n)`. |
| How do you estimate complexity empirically? | Double `n`, and take `log2` of the time ratio. It estimates the exponent. |
| Where do you start with slow code? | Measure. Check if it's on-CPU. Then remove work, change the algorithm, change the layout, parallelise, and tune constants last. |
| What's Amdahl's law? | If a share `p` gets `s` times faster, the gain is `1 / ((1-p) + p/s)`. The part you don't touch sets a ceiling of `1/(1-p)`. |
| Is O(1) always faster than O(n)? | No. Constants and caches decide it on small inputs. Measure at the real size. |

## Next

[2 — Data structures](02-data-structures.md): what's behind the `O(1)` claims, down to how CPython's `list` and `dict` are laid out in memory.
