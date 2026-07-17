# Code Review Round

## What's tested
Reviewing unfamiliar code under observation: do you have a *method*, or just an eye?
Signals: consequence-ranked reading order, catching the innocent-looking dangerous change,
communicating findings without condescension, and knowing what *not* to flag.

## Format & trends
30–60 min: a PR/diff (sometimes a whole small service) to review live, or async with a
written review discussed in the round. Increasingly common for senior/staff loops and
AIE roles (reviewing AI-generated code is now a core job skill — say that out loud if
asked why review matters in 2026).

## The method (contract-first, consequence-ranked)
From the librarian code-review drill (wiki: *Code Review Drill — SANYI*):

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
5. **Report news, not history** — don't re-litigate pre-existing debt unless asked; a
   reviewer who flags everything gets muted.
6. **Voice**: questions over verdicts ("what happens if this input is empty?" beats
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
  intent, check hallucinated APIs, test coverage as the safety net —
  [agents guide](../guides/agents.md) harness sections).

## Question bank
- "Review this PR." — narrate the method: intent first, then consequence-ranked passes;
  end with a summary ranked by severity.
- "The tests pass and it lints clean — approve?" — passing checks verify what's encoded,
  not what's intended; look for contract/convention violations (the §3 dangerous class).
- "How do you review a 2,000-line PR?" — push back first (ask for it split); else review
  by risk: entry points, data writes, interface changes; timebox style to zero.
- "A senior engineer disagrees with your blocker." — restate the consequence, not the
  rule; escalate to data (test, incident precedent) or explicitly downgrade with a
  follow-up ticket — no ego ([behavioral](behavioral.md) overlap).
- "What makes a review comment good?" — specific, actionable, severity-labeled, question-
  phrased where possible.

## Per-role weighting
| AIE | MLE | DS | FDE |
|---|---|---|---|
| ◐ | ◐ | ○ | ◐ |

Mostly senior/staff loops; AIE variants increasingly use AI-generated code as the artifact.

## Links
- Study guides: [agents](../guides/agents.md) (harness/tooling conventions), [security-safety](../guides/security-safety.md) (the invariants you check first)
- librarian wiki: Code Review Drill — SANYI · SANYI Change-Contract System
