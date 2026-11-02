# Drill problems

Cold-attempt material. **Unlike `dsa/`, these ship without solutions**: the answer gets written at
drill time, into `solutions/<phase>.md`.

| Problem | Env | Fills gap | Timebox | Prompts |
|---|---|---|---|---|
| `token-service/` | env1 | security + PII | 45 min | `prompts.md` — 4 phases |
| `rate-limiter/` | env1 | OOD | 45 min | `prompts.md` — 4 phases |
| `feed-ranker/` | env2 | AI-sandbox feature build | 30 min | `prompts.md` — 1 feature request |

## Layout

```text
problems/<name>/
  src/          # given code, runnable, seeded bugs where applicable
  prompts.md    # questions only — safe to read before attempting
```

At drill time, create `problems/<name>/solutions/<phase>.md` with: question → raw attempt → feedback
→ better version → What I'd say. Attempts stay local (gitignored).

## Rules

- **`src/` is copied from, never edited.** Work in `drills/coding/scratch/`.
- **Read `prompts.md` only.** Nothing here contains an answer key by design, but the
  seeded bugs are only findable once.

## Sourcing note

`dsa/` (the "Hello, Interview!" open-source repo) is **reference, not drill material** —
every problem ships with its solution and THINKING doc, so reading one spends it. Use it
to refresh a pattern, not to rehearse cold.
