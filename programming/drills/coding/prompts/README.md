# Coding-drill starter files

One file per question. Each carries the prompt as a module docstring, the
clarifications the interviewer would give if asked, signatures stubbed with
`NotImplementedError`, and a single happy-path smoke assert.

**Copy, don't edit.** Copy a starter to `programming/drills/coding/scratch/<qid>-<date>.py` (gitignored) so
these stay pristine across attempts.

Every file except `debug-dedup.py` fails at `NotImplementedError` on a fresh run.
`debug-dedup.py` fails on its actual bug — that failure is the exercise.

The smoke test is happy-path only, on purpose. Finding the edge cases is the `T`
in the clarify/plan/narrate/test grade; a starter that tested them for you would
hand you the mark.

| File | QID | Question | Kind | Budget |
|---|---|---|---|---|
| `cache-lru.py` | `cache-lru` | Q4 | live coding | 25–30 min |
| `resilience-retry.py` | `resilience-retry` | Q5 | live coding | 25–30 min |
| `debug-dedup.py` | `debug-dedup` | Q7 | debugging | 20 min |
| `algo-transaction-agg.py` | `algo-transaction-agg` | Q6a | practical | 35 min |
| `db-sqlite-scaling.py` | `db-sqlite-scaling` | Q6d | practical | 40 min |
| `auth-token-endpoint.py` | `auth-token-endpoint` | Q6e | practical | 40 min |
| `agentic-workflow.py` | `agentic-workflow` | Q6c | practical | 40 min |
| `agentic-rag-offline.py` | `agentic-rag-offline` | Q6b | practical | 45 min |

Question numbers refer to `questions.md` in
`practice/interviewing/rounds/coding-challenge/`. That
folder's `examples/` holds full worked solutions — **do not open it before an
attempt finishes.**

Two of these are trap-shaped: the graded mistake is one the prompt does not warn
you about. Their docstrings stay quiet deliberately. Which two is not written
down here for the same reason.
