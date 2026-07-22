# Programming

Practice problems and cloud/infra reference — doesn't map onto the data-domain categories above, so
it gets its own bucket.

## Contents

- **`HackerRank/`** — Python and SQL practice problems (Introduction, Strings, Collections,
  Itertools, Classes; Basic/Advanced Select, Join, Aggregation).
  TypeScript: `HackerRank/typescript/` — one solved example (`example-plus-minus.ts`) with
  `tsconfig.json` and `package.json`. Infrastructure only; problem coverage is minimal.
- **`Leet-Code/`** — arrays/hashing, two pointers, sliding windows, linked lists, plus NeetCode
  exercises and a probability-problems notebook. Includes *A Competitive Programmer's Handbook* as a
  reference PDF, and its own `LeetCodeCheat/` quick-reference repo.

## TypeScript Examples

**What exists:** `HackerRank/typescript/` — one solved problem (`example-plus-minus.ts`) with
build config. Essentially a scaffold with no meaningful problem coverage.

**Gaps:**

| Area | Python coverage | TypeScript gap |
|---|---|---|
| HackerRank problems | ~30 solved across 5 categories | 1 example only — all major categories (strings, collections, classes, SQL) missing |
| LeetCode / DS&A | 4 pattern notebooks (arrays, two-pointers, sliding window, linked lists) | No TypeScript DS&A solutions at all |
| Reference material | *A Competitive Programmer's Handbook* (PDF) | Applies to any language; no TS-specific algorithms reference |

**Recommendation:** HackerRank TypeScript coverage is the easiest win — the problem set is fixed
and the scaffold is already there. LeetCode TS solutions are lower priority; the Python notebooks
are already the canonical form for algorithm study here.
