# Coding Challenge — Sources

## Internal study guides

| Guide | Relevance |
|-------|-----------|
| `ml-foundations` | SQL screens (DS variant), pandas idioms for data manipulation questions |
| `data-engineering-mlops` | Pipeline idioms — ETL transforms, retry/backoff patterns, rate limiting, streaming |
| `programming/Leet-Code/` | Seed material for live coding classics (LRU cache, graph traversal, interval problems) |

Load these before any coding challenge prep session. The `data-engineering-mlops` guide is especially dense with the project-style patterns (rate limiter, retry decorator, ETL) that appear in AIE/MLE loops.

## External resources

### Patterns and practice

| Resource | What it covers |
|----------|---------------|
| [Neetcode.io](https://neetcode.io) | Curated pattern groupings — practice by pattern, not by problem number |
| [Python Cookbook (O'Reilly)](https://www.oreilly.com/library/view/python-cookbook-3rd/9781449357337/) | Idiomatic Python: itertools, collections, context managers, generators — the exact idioms interviewers notice |
| [HackerRank Python domain](https://www.hackerrank.com/domains/python) | Fluency drills in a timed environment |

### Debugging methodology

| Resource | What it covers |
|----------|---------------|
| [How to Debug (Julia Evans / Wizard Zines)](https://wizardzines.com/zines/debugging-adventure/) | Systematic method — reproduce, bisect, trust the data, not assumptions |
| [Rubber Duck Debugging (David Agans — Debugging)](https://debuggingrules.com) | The 9 rules; particularly "quit thinking and look" and "change one thing at a time" |

### AI-assisted coding

| Resource | What it covers |
|----------|---------------|
| [Anthropic prompt engineering docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) | Prompt decomposition patterns — relevant for AI-assisted interview variants |
| [Simon Willison's blog — AI coding patterns](https://simonwillison.net) | Practical verification workflows, when to trust/distrust generated code |

## What to pull first

For a coding challenge loop in the next 2 weeks:

1. `data-engineering-mlops` guide for pipeline patterns (day 1)
2. Neetcode blind 75 — one pattern per day, narrated out loud (ongoing)
3. One debugging kata per day from HackerRank or a broken script you write yourself
4. `programming/Leet-Code/` for the LRU cache and interval problems specifically
