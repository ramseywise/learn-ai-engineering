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

- Python fluency drills: dict/set idioms, comprehensions, generators, error handling, dataclasses — have these cold
- Narration practice: state the plan first, name complexity as you go, never code silently
- One debugging kata per day pre-loop
- Tests-first reflex for project-style prompts
- Clarify before coding: inputs, edge cases, scale
- AI-assisted: practice prompt decomposition and output verification workflow

## Folder contents

| File | Purpose |
|------|---------|
| `questions.md` | 12–15 questions by format with approach, signals, pitfalls |
| `study-guide.md` | Core methods: narration, debugging methodology, Python fluency, AI-assisted skills |
| `sources.md` | Internal study guides + external resources |
| `examples/` | Three worked walkthroughs with narration annotations |
