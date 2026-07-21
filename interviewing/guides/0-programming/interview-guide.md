# Programming Foundations — Study Guide

The coding screen: every interview loop has one. The bar is pattern recognition and clean
implementation under time pressure, not memorized solutions. Know the moves; apply them to
variants.

---

## 1. DSA checklist

### Arrays & Hashing

- Hash map for O(1) lookup: "have I seen this before?" — two-sum, duplicate detection,
  frequency counts.
- Prefix sums for range queries: precompute cumulative sums so any subarray sum is O(1).
- Sorting as a preprocessing step: many O(n²) brute-force solutions drop to O(n log n)
  when you sort first and then use two pointers.
- Edge cases: empty array, single element, all duplicates, negatives.

### Two Pointers

- Same-direction (fast/slow): linked list cycle, middle of list, Nth from end.
- Opposite-direction (left/right): reverse in-place, sorted two-sum, valid palindrome,
  container with most water.
- Squeezed window: fixed or variable window scanning for a target condition — substring
  problems, maximum/minimum subarray.
- When to reach for it: the problem involves a sorted structure or a linear scan where you
  need to track two positions simultaneously.

### Linked Lists

- The pointer manipulation triad: save `next` before overwriting, use a dummy head to
  avoid special-casing empty lists, reverse with three pointers (`prev`, `curr`, `nxt`).
- Cycle detection: Floyd's (fast/slow pointer) — cycle exists if they meet; cycle start
  found by resetting one pointer to head then advancing both at speed 1.
- Merge sorted lists: compare heads, recurse or iterate.

### Trees

- Traversal templates: preorder (root → left → right), inorder (left → root → right, gives
  sorted order for BST), postorder (left → right → root). Iterative with explicit stack.
- BFS with a deque: level-order traversal, shortest path in unweighted graph.
- BST invariant: every left subtree value < root < every right subtree value. Validate by
  passing min/max bounds down.
- Depth/height: recursive base case is `None` returns 0 or -1.

### Graphs

- BFS (deque + visited set): shortest path in unweighted graph, connected components.
- DFS (recursion or explicit stack + visited): cycle detection, topological sort, flood fill.
- Topological sort: Kahn's (in-degree BFS) or DFS post-order. Use for dependency ordering.
- Union-Find: detect cycle in undirected graph, group connected components — O(α(n)) per
  operation with path compression + union by rank.

### Dynamic Programming

- Identify the pattern: "optimal substructure + overlapping subproblems" — every recursive
  solution with repeated calls is a DP candidate.
- Top-down (memoization): write the recursion first, add a cache (`@functools.lru_cache`
  or a dict). Easier to reason about; higher call-stack overhead.
- Bottom-up (tabulation): fill a table from base cases up. Better for large inputs; easier
  to optimize space.
- Classic patterns: 0/1 knapsack, unbounded knapsack, LCS/LIS, coin change, house robber,
  grid paths. Know the state definition and transition before touching code.
- Space optimization: many 2D DP tables can reduce to 1D or two rows if you only need the
  previous row.

---

## 2. Python patterns

### Standard library (reach for these first)

```python
from collections import defaultdict, Counter, deque
from itertools import combinations, permutations, product, groupby, accumulate
from heapq import heappush, heappop, nlargest, nsmallest
import bisect  # bisect_left, bisect_right for binary search on sorted list
```

### Comprehensions and generators

```python
# List comprehension — build filtered/mapped lists
squares = [x**2 for x in range(10) if x % 2 == 0]

# Dict comprehension — invert a mapping, count frequencies
word_count = {word: text.count(word) for word in set(text.split())}

# Generator expression — lazy evaluation; use when you only need one pass
total = sum(x**2 for x in range(10**6))

# Nested — flatten a 2D list
flat = [val for row in matrix for val in row]
```

### Itertools patterns

```python
from itertools import combinations, accumulate
import operator

# All pairs from a list — avoid nested loops
pairs = list(combinations(nums, 2))

# Running prefix sums
prefix = list(accumulate(nums))                     # running total
prefix_prod = list(accumulate(nums, operator.mul))  # running product
```

### Common interview moves in Python

```python
# Swap without temp
a, b = b, a

# Sort by multiple keys
data.sort(key=lambda x: (x[1], -x[0]))

# Counter for frequency map
from collections import Counter
freq = Counter(s)
most_common = freq.most_common(3)

# Defaultdict avoids key-existence checks
graph = defaultdict(list)
graph[node].append(neighbor)

# Deque for O(1) left-append/pop (lists are O(n) for popleft)
from collections import deque
q = deque([start])
q.appendleft(item)  # or q.append(item)
item = q.popleft()
```

---

## 3. SQL patterns

### Joins — know the result count before writing

- `INNER JOIN`: only rows with matches in both tables. Row count ≤ both inputs.
- `LEFT JOIN`: all rows from left, nulls for non-matching right. Row count = left (if join
  key is unique on right) or can exceed left (if right has duplicates).
- Self-join: join a table to itself to compare rows within the same table (hierarchy, pairs).
- "How many rows does this join produce?" — always ask before running.

### Aggregation + filtering

```sql
-- HAVING filters after GROUP BY; WHERE filters before
SELECT department, COUNT(*) AS headcount, AVG(salary) AS avg_sal
FROM employees
WHERE hire_date >= '2022-01-01'   -- filters rows before grouping
GROUP BY department
HAVING COUNT(*) > 5;              -- filters groups after aggregating
```

### Window functions — the interview staple

```sql
-- ROW_NUMBER: unique rank (no ties). RANK: ties get same rank, next skips.
-- DENSE_RANK: ties get same rank, next does NOT skip.
SELECT name, salary,
       ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn,
       RANK()       OVER (PARTITION BY department ORDER BY salary DESC) AS rnk,
       DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rnk
FROM employees;

-- Running total and moving average
SELECT date, revenue,
       SUM(revenue)  OVER (ORDER BY date) AS running_total,
       AVG(revenue)  OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_7d_avg
FROM daily_sales;

-- LAG/LEAD: access adjacent rows without a self-join
SELECT date, revenue,
       LAG(revenue) OVER (ORDER BY date) AS prev_day_revenue,
       revenue - LAG(revenue) OVER (ORDER BY date) AS day_over_day_change
FROM daily_sales;
```

### CTEs and dedup idiom

```sql
-- CTE: name an intermediate result — cleaner than nested subqueries
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM events
)
SELECT * FROM ranked WHERE rn = 1;   -- dedup: keep latest row per user

-- Recursive CTE: hierarchy traversal (org chart, category tree)
WITH RECURSIVE org AS (
    SELECT id, name, manager_id, 0 AS depth FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, org.depth + 1
    FROM employees e JOIN org ON e.manager_id = org.id
)
SELECT * FROM org ORDER BY depth;
```

### Funnel / retention / cohort (one-per-interview)

```sql
-- Funnel: count users completing each step
SELECT
    COUNT(DISTINCT CASE WHEN step >= 1 THEN user_id END) AS step1,
    COUNT(DISTINCT CASE WHEN step >= 2 THEN user_id END) AS step2,
    COUNT(DISTINCT CASE WHEN step >= 3 THEN user_id END) AS step3
FROM user_events;

-- Monthly retention: users active in month N who were also active in month 0
WITH cohort AS (
    SELECT user_id, DATE_TRUNC('month', MIN(event_date)) AS cohort_month
    FROM events GROUP BY user_id
)
SELECT cohort_month,
       DATE_DIFF('month', cohort_month, DATE_TRUNC('month', e.event_date)) AS months_since_start,
       COUNT(DISTINCT e.user_id) AS retained
FROM events e JOIN cohort USING (user_id)
GROUP BY 1, 2;
```

---

## 4. Question bank (answer sketches)

**"Two Sum"** (arrays + hashing)
Iterate; store `target - num` in a hash map as you go. O(n) time, O(n) space. One pass.
Variant: sorted array → two pointers, O(1) space.

**"Valid parentheses"** (stack)
Push open brackets; on close, check stack top matches. Empty stack at end = valid.

**"Longest substring without repeating characters"** (sliding window)
Expand right; when duplicate found, shrink left until duplicate is gone. Track max window
with a set + two pointers. O(n).

**"Reverse a linked list"** (linked list)
`prev = None; curr = head`. Loop: `nxt = curr.next; curr.next = prev; prev = curr; curr = nxt`.
Return `prev`.

**"Binary tree level-order traversal"** (BFS)
Deque seeded with root. Each iteration: snapshot the current queue length (that's the
level), pop that many nodes, append their children.

**"Coin change"** (DP)
`dp[i]` = min coins to make amount `i`. Base: `dp[0] = 0`. For each amount, try every
coin: `dp[i] = min(dp[i], dp[i - coin] + 1)`. O(amount × coins).

**"Number of islands"** (graph DFS/BFS)
Iterate cells; on `'1'`, do DFS/BFS to mark the whole island visited (flip to `'0'` or
use a visited set), increment count. O(rows × cols).

**"Top-K frequent elements"** (heap)
`Counter` for frequencies → `heapq.nlargest(k, freq, key=freq.get)`. O(n log k).
Alternative: bucket sort by frequency for O(n).

**"Merge intervals"** (sorting)
Sort by start. Iterate: if current start ≤ last merged end, extend end; else append new
interval. O(n log n).

**"Find duplicate in array"** (Floyd's)
Treat array values as next-pointers. Phase 1: find intersection (fast/slow). Phase 2:
reset one to start, advance both at speed 1 — they meet at the duplicate.

**SQL: "Second highest salary"**
`SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees)`.
Or: `SELECT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1`. Discuss ties →
`DENSE_RANK() OVER (ORDER BY salary DESC) = 2`.

**SQL: "Users active in Jan and Feb but not March"**
```sql
SELECT user_id
FROM events
WHERE DATE_TRUNC('month', event_date) IN ('2024-01-01', '2024-02-01')
GROUP BY user_id
HAVING COUNT(DISTINCT DATE_TRUNC('month', event_date)) = 2
   AND SUM(CASE WHEN DATE_TRUNC('month', event_date) = '2024-03-01' THEN 1 ELSE 0 END) = 0;
```

---

## Sources

- code: `programming/HackerRank/python/` (language topics), `programming/HackerRank/sql/` (SQL tracks), `programming/Leet-Code/` (DSA patterns + NeetCode exercises)
- reference: `programming/Leet-Code/Competitive Programmer's Handbook - 296p.pdf`
- overview: [00-overview.md](00-overview.md) (learning path + resource map)
