# Coding Challenge

**What's tested**: Engineering judgment in motion — reading unfamiliar code, debugging it, structuring a small solution cleanly, and narrating decisions while typing. The 2026 shift is away from algorithm recall toward observable problem-solving process.

## Formats

| Format | Duration | What's graded |
|--------|----------|---------------|
| Live coding | 45–60 min | Correct solution + clean structure + narration |
| Debugging | 30–45 min | Systematic isolation: reproduce → bisect → root cause → fix → prevent |
| Pair programming | 45–60 min | Collaboration, hint integration, communication quality |
| AI-assisted | 30–45 min | Prompt decomposition, output verification, knowing when not to trust |

Live coding is increasingly project-style ("implement a rate limiter") over pure LeetCode. Debugging rounds hand you broken code and grade your diagnostic method. AI-assisted variants are now present in AIE/MLE loops specifically.

## Per-role weighting

| AIE | MLE | DS | FDE |
|-----|-----|-----|-----|
| ◐ | ◐ | ◐ | ◐ |

Present in every loop but rarely the differentiator round. DS versions skew SQL/pandas. FDE versions skew practical scripting under time pressure.

## Prep checklist

- Python fluency drills: dict/set idioms, comprehensions, generators, error handling, dataclasses — have these cold ([code-from-heart.md](code-from-heart.md) is the pattern set + a 25-min self-test)
- Narration practice: state the plan first, name complexity as you go, never code silently
- One debugging kata per day pre-loop
- Tests-first reflex for project-style prompts
- Clarify before coding: inputs, edge cases, scale
- AI-assisted: practice prompt decomposition and output verification workflow

## Folder contents

| File | Purpose |
|------|---------|
| `questions.md` | 20 questions by format with approach, signals, pitfalls |
| `code-from-heart.md` | The stdlib patterns to write without reference — aggregation, sorting, validation, HTTP/auth minimums, plus a 25-min drill |
| `study-guide.md` | Core methods: narration, debugging methodology, Python fluency, AI-assisted skills |
| `sources.md` | Internal study guides + external resources |
| `examples/` | Eight worked walkthroughs with narration annotations — three general, five offline practicals |

## The AIE practical variant

For AIE/MLE loops, the live-coding round is increasingly an **AI-engineering practical** rather than an algorithm problem: build a retrieval pipeline, orchestrate a multi-step workflow, or validate structured model output. Browser-based assessments (CoderPad/CodeSignal) typically mean no network, no `pip install`, and no AI assistant — so the drill has to run on the standard library alone.

Questions 6a–6e and the five offline examples cover this variant. They deliberately avoid `numpy`, `pandas`, `pydantic`, and any API call, so they are solvable in a bare browser editor within their stated timeboxes.

Two of them are **trap-shaped** — the prompt hands you a tool that is correct for the exercise and wrong for the stated scale, and the grade is in the critique rather than the code. A SQLite pipeline followed by *"this serves millions of requests a day"* wants you to name the single-writer lock and split OLTP from OLAP. An auth prompt wants `hmac.compare_digest` and algorithm pinning, not just a working token.

Before drilling the examples, make sure the syntax underneath them is automatic — [code-from-heart.md](code-from-heart.md) is the pattern set plus a 25-minute self-test.
