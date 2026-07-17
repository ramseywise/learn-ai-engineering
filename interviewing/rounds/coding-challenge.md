# Coding Challenge (live coding · debugging · pair programming)

## What's tested
Working code under observation — but the 2026 emphasis has shifted from algorithm recall
to *engineering judgment in motion*: reading unfamiliar code, debugging it, structuring a
small solution cleanly, and narrating decisions while typing.

## Format & trends
- **Live coding** (45–60 min): increasingly project-style — "implement a rate limiter /
  a retry wrapper / a small ETL transform" — over pure LeetCode (research F4). Big-tech
  loops still run DS&A; startup/AIE loops mostly don't.
- **Debugging round** (2026 trend, research F5): you're handed unfamiliar *broken* code
  and fix it. Tests systematic isolation: reproduce → read the error honestly → bisect
  (prints/debugger) → fix root cause, not symptom → state how you'd prevent regression.
- **Pair programming**: interviewer collaborates; scores collaboration and how you take
  hints — treat every hint as free information, never as an insult.
- **AI-assisted variants**: some loops now *allow or require* an AI assistant; the graded
  skill becomes prompt decomposition, verification of generated code, and knowing when
  not to trust it. Others have moved in-person (~38% in 2025) to prevent exactly that —
  ask the recruiter which regime you're in.

## Prep checklist
- [ ] Fluency drills in your primary language: dict/set idioms, comprehensions,
  generators, error handling, dataclasses (Python) — typing speed on basics matters.
- [ ] Practice narrating while coding: state the plan first ("brute force, then optimize
  if time"), name complexity as you go.
- [ ] One debugging kata per day pre-loop: take any repo, break something, fix it with a
  systematic loop — or fix real issues in your own projects.
- [ ] Tests-first reflex for project-style prompts: even 2 asserts show discipline.
- [ ] Clarify before coding: inputs, edge cases, scale — same clarify-first habit as the
  [system-design round](system-design-round.md).
- Seed material: `programming/Leet-Code/` + HackerRank (coding-patterns study guide is a
  deferred milestone — see [README](../README.md)).

## Question bank
- "Implement an LRU cache." — dict + doubly-linked list (or `OrderedDict`); state O(1)
  invariants before coding.
- "This script should dedupe records but the output is wrong — fix it." — reproduce first,
  print intermediate state, check the equality/key assumption (mutable keys? case? whitespace?).
- "Parse this log file and report the top-5 error codes." — generator + Counter; ask about
  file size (streaming vs load-all — a mini trade-off narration).
- "Write a retry decorator with exponential backoff." — jitter, max attempts, which
  exceptions retry; mention idempotency ([data-eng guide](../guides/8-data-eng-mlops/interview-guide.md) §1).
- "Refactor this function while keeping tests green." — small steps, run tests each step,
  name the smells you're removing.

## Per-role weighting
| AIE | MLE | DS | FDE |
|---|---|---|---|
| ◐ | ◐ | ◐ | ◐ |

Present in every loop but rarely the differentiator round; DS versions skew
SQL/pandas ([ml-foundations](../guides/1-foundations/interview-guide.md) §6), FDE versions skew
practical scripting under time pressure.

## Links
- Study guides: [ml-foundations](../guides/1-foundations/interview-guide.md) (SQL screens), [data-engineering-mlops](../guides/8-data-eng-mlops/interview-guide.md) (pipeline idioms)
- Research: F4/F5 in `.claude/docs/plans/2026-07-17-interview-kb-consolidation.md`
