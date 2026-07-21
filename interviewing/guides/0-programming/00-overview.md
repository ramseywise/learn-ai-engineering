# Pillar 0 — Programming Foundations (DSA, Python, SQL)

The bedrock under everything else: write clean, efficient code, solve algorithmic problems
under pressure, and translate data questions into working queries. This pillar doesn't
sequence from another — it runs in parallel with or before Pillar 1. Most interview loops
include a coding screen at some stage.

## Learning path

1. **Python fluency by topic** — `programming/HackerRank/python/` works through the
   language systematically: Introduction → Basic Data Types → Strings → Collections →
   Itertools → Functional patterns → Classes → Regex → Error handling. Work in order;
   each topic builds vocabulary for the next.

2. **SQL by topic** — `programming/HackerRank/sql/` covers: Basic Select → Basic Join →
   Aggregation → Advanced Select → Advanced Join. Work all five before moving to window
   functions in the interview guide.

3. **DSA patterns** — `programming/Leet-Code/` is organized by pattern, not difficulty.
   Work in pattern order: Arrays & Hashing → Two Pointers → Sliding Windows → Linked
   Lists. Each pattern teaches a reusable move, not a one-off trick.

4. **Practice mode** — `programming/Leet-Code/NeetCodeExercsises.ipynb` has mixed
   problems. Treat it as timed self-testing after you've worked the patterns.

5. **Reference depth** — *Competitive Programmer's Handbook* (`programming/Leet-Code/`)
   covers trees, graphs, DP, and advanced combinatorics. Read chapter-by-chapter after
   the LeetCode patterns; use it as a reference, not a linear read.

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| HackerRank Python track | code | `programming/HackerRank/python/` | Language idioms by topic: data types, strings, collections, itertools, OOP, regex |
| HackerRank SQL track | code | `programming/HackerRank/sql/` | SQL basics through advanced joins and aggregation |
| LeetCode by pattern | code | `programming/Leet-Code/` | Arrays/hashing, two pointers, sliding windows, linked lists |
| NeetCode exercises | notebook | `programming/Leet-Code/NeetCodeExercsises.ipynb` | Mixed-pattern timed practice |
| Probability Problems | notebook | `programming/Leet-Code/Probability-Problems.ipynb` | Probability math under interview pressure |
| LeetCode cheat sheet | reference | `programming/Leet-Code/LeetCodeCheat/` | Pattern templates and edge-case reminders |
| Competitive Programmer's Handbook | pdf | `programming/Leet-Code/` | Trees, graphs, DP, advanced algorithms — deep reference |

## Progression note

HackerRank → LeetCode is a deliberate ramp: HackerRank trains language fluency topic by
topic (you're not fighting Python syntax when solving an algorithm problem); LeetCode trains
algorithmic pattern recognition. Conflating the two stalls progress on both. Do HackerRank
first, then LeetCode patterns, then timed mixed practice.

## Test yourself

[interview-guide.md](interview-guide.md) — DSA checklist, Python patterns, SQL patterns,
and a question bank with answer sketches. Read it after working through the learning path
above, not before.
