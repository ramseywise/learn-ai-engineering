# Code Review Round

## What's tested
Reviewing unfamiliar code under observation: do you have a *method*, or just an eye?
Signals: consequence-ranked reading order, catching the innocent-looking dangerous change,
communicating findings without condescension, and knowing what *not* to flag.

## Format & trends
30-60 min: a PR/diff (sometimes a whole small service) to review live, or async with a
written review discussed in the round. Increasingly common for senior/staff loops and
AIE roles (reviewing AI-generated code is now a core job skill — say that out loud if
asked why review matters in 2026).

## The method (contract-first, consequence-ranked)

1. **Orient before judging** — first question is never "is this code good?" but *"what is
   this change supposed to do, and what contracts/invariants does the code it touches
   declare?"* Read the PR description, then the surrounding file conventions.
2. **Read in consequence order**: security & data boundaries (auth, PII, irreversible
   writes) → correctness & interfaces (schema/signature drift, error paths) →
   maintainability (hardcoded tunables, convention breaks) → style last, if at all.
3. **The dangerous class**: changes where every individual line looks innocent — a flag
   wrapped around a safety check, a threshold inlined "temporarily", a `0.42` hardcoded
   in business logic ten lines below an env-driven-constant convention. Line-by-line
   reading approves these; convention/contract-diffing flags them.
4. **Severity from consequence, not taste**: invariant touched → blocker; interface
   drift → warning; tunable made rigid → info; style → nit (or silence).
5. **Confidence is a second, independent axis from severity**: consequence sets severity
   (blocker/warning/nit); the strength of your evidence sets confidence — *verified*
   (reproduced, or traced through the full code path), *supported* (a code path or
   documented behavior strongly indicates it, but you haven't reproduced it), or
   *hypothesis* (a plausible failure mechanism, but key context is still missing). The two
   axes are genuinely independent: a suspected data leak is high-severity/low-confidence
   until you trace the path; a misspelled variable is high-confidence/low-severity. When
   confidence is a hypothesis — especially a high-severity one — frame it as a question or
   a targeted test request, not as an assertion: "this could double-charge if the provider
   retries — worth checking?" beats "this double-charges."
6. **Report news, not history** — don't re-litigate pre-existing debt unless asked; a
   reviewer who flags everything gets muted.
7. **Voice**: questions over verdicts ("what happens if this input is empty?" beats
   "this is wrong"); acknowledge good decisions; propose the mechanical fix when you
   flag something.

## Prep checklist
- [ ] Practice on real PRs: pick merged PRs in OSS repos, review the diff blind, compare
  with the actual review comments.
- [ ] Drill the ordering until automatic: invariants → interfaces → tunables → style.
- [ ] Rehearse one worked example you can narrate (the two-line-diff-that-lints-clean
  story is a strong answer to "how do you review code?").
- [ ] Know your linter boundary: never spend interview time on what a formatter/linter
  catches — say so explicitly, it's a maturity signal.
- [ ] For AIE roles: have a take on reviewing LLM-generated code (verify behavior against
  intent, check hallucinated APIs, test coverage as the safety net).

## Per-role weighting
| AIE | MLE | DS | FDE |
|---|---|---|---|
| ◐ | ◐ | ○ | ◐ |

Mostly senior/staff loops; AIE variants increasingly use AI-generated code as the artifact.

## Folder contents
- [sources.md](sources.md) — curated references and reading list
- [examples/](examples/) — worked code review examples
- [questions.md](questions.md) — sample questions and model answers
- [study-guide.md](study-guide.md) — indexed knowledge areas and what to study
