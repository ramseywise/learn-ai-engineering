# Env 2 — AI allowed, sandbox, 30 min: production-ready feature end to end

Single agent, in-environment. **What's graded is visible process**, not just the artifact:
how you decompose, how you specify I/O, how you verify each increment. One-shot prompting
scores badly even when the output works.

30 minutes is the hard constraint. Everything below is shaped by it.

---

## The 30-minute budget

| Time | Phase | Output |
|---|---|---|
| 0–3 | Read + orient | Know the codebase vocabulary and where the feature plugs in |
| 3–6 | **Decompose out loud** | 3–4 named tasks, written down where they're visible |
| 6–9 | Task 1: types/models + test | Interfaces exist, one failing test |
| 9–15 | Task 2: core logic | Green on happy path |
| 15–21 | Task 3: edge cases + errors | Green on the boundary set |
| 21–26 | Task 4: hardening | Validation, logging, the one security concern |
| 26–30 | Full run, review, submit | Everything passes, nothing half-applied |

**Ship a working slice by minute 20.** A complete narrow feature beats a broad half-built
one. If you're behind at 20, cut scope explicitly and say you're cutting it.

---

## The decomposition (minutes 3–6) — this is the graded moment

Write the plan somewhere visible before prompting anything. Say what each step produces.

**Right-sized: 3–4 steps for 30 minutes.** Each step is one prompt-and-verify cycle you
could defend on its own.

Canonical ordering:

1. **Data model / types first** — the shapes everything else refers to
2. **Core happy path** — the actual feature, narrow
3. **Edge cases and error handling** — empties, invalid input, failure modes
4. **Hardening** — validation, logging, the security concern, then a review pass

Rules that make a decomposition good:

- **Types before logic that uses them.**
- **Core before edges.**
- **Bug fixes before features that depend on the broken code.**
- Too broad: "build the feature" — nothing to check until the end.
- Too narrow: "write the constructor" — you'd just type that.

State it plainly: *"Four steps — model the Order and OrderItem types, then the validation
rules, then the failure paths, then input hardening and a review pass. I'll run tests
after each."*

---

## Prompting: I/O contract first, every time

The graded skill is **specification**, not phrasing. Before each prompt, know:

- **Input**: exact types, which fields are optional, what's already validated upstream
- **Output**: exact return type, and what happens on failure — exception? `None`?
  a result object? (Match what the codebase already does.)
- **Constraints**: what it must not do; which existing structures it must use
- **Scope**: this step only

### Prompt template

```text
In <file>, add <method> to <existing class>.

Input:  <types, with optionality>
Output: <type>; on <failure case> <exact behavior>
Use:    <existing class/structure from the codebase>
Constraints: <no new deps / match existing error style / no I/O in this layer>

Be concise, minimal comments. Don't modify anything outside <file>.
```

**Use the codebase's real vocabulary.** "Add `search_by_prefix` to the `Dictionary` class
using the existing `TrieNode`" produces code that fits. A generic prompt produces a
parallel structure that clashes — and reveals you didn't read the code.

### Granularity

- **Tricky logic** (state machine, concurrency, tricky invariant) → be precise about
  approach and data structures
- **Boilerplate** (five similar handlers, DTOs) → short prompt, you'll verify anyway
- **Under 30 seconds to type yourself** → just type it. Prompting a one-liner looks worse
  than writing it.

### Temperature / determinism

If the sandbox exposes model settings: **low temperature (0–0.3) for code**. Say why —
you want deterministic, conventional output you can verify, not creative variation. If
it's not exposed, say you'd pin it low for codegen and reserve higher settings for
brainstorming alternatives. Mentioning this unprompted is a differentiator.

---

## Verification: tests first, run every increment

**Write the failing test before the implementation** for each step. It gives the AI a
concrete target and shrinks your review surface from "read every line" to "run it."

```text
"Here's the failing test: <paste>. Implement <method> so it passes.
Don't modify the test."
```

That last clause matters — **deleting or weakening a failing test is the classic AI
correctness shortcut**, and it's a red flag if it lands in your diff.

### After every generation, scan for the four failure patterns

| Pattern | What it looks like |
|---|---|
| **Textbook-but-wrong-fit** | Correct LeetCode answer that ignores the codebase's existing utilities |
| **Verbosity** | 150 lines where 60 would do; comments on every line |
| **Over-abstraction** | `BaseProcessor` for two classes sharing nothing; strategy pattern for an if/else |
| **Correctness shortcuts** | deleted/weakened tests, `any` casts, `except: pass`, hardcoded values to pass a specific case |

Then: **run it.** Never stack two generations without running in between — individually
correct changes conflict, and you get a cascade with no time left.

### The one-reprompt rule

First attempt misses → rephrase once, more specific. Second miss → **write it yourself.**
Never more than 2 minutes on one generation. Watch for the AI spiral: when a model doesn't
know, it starts proposing rewrites and restructures. That's flailing, not momentum —
interrupt it.

---

## "Production-ready" — what they're checking for

This is the phrase that distinguishes env 2 from a LeetCode answer. Cover deliberately:

- **Input validation** at the boundary; reject early with a clear error
- **Error handling that matches the codebase's style** — don't invent exceptions where
  the code returns result objects
- **No swallowed exceptions.** `except: pass` is a finding
- **Logging** at the right level, **with no PII or secrets in the log line**
- **Types** — annotations present, and no `any`/`# type: ignore` used to silence a real error
- **Idempotency / concurrency** if the feature touches shared state
- **Tests** covering happy path + empty + invalid + boundary
- **Security**: parameterized queries, no secrets in code, `hmac.compare_digest` for
  token comparison, authorization checked (not just authentication), no path traversal

Naming **one** concrete security consideration unprompted is worth more than a general
claim of being security-conscious.

---

## Narration — make the process visible

Even if no one is watching live, the transcript is the artifact. State intent *before*
each prompt, and read the output *after*:

- *"Now I'm asking for the validation layer — input is the raw dict, output is a
  validated Order or a ValidationError, matching the existing error style."*
- *"That came back with a base class I didn't ask for. I'm reprompting without it."*
- *"That's green. Moving to the failure paths."*
- *"I'm cutting the retry logic — 8 minutes left and the core needs to be solid. Noting
  it as the next step."*

Pivots get a reason. *"Switching to a heap because the sort is O(n log n) per insert and
we're inserting in a loop."* Silent rewrites read as confusion.

---

## Failure modes to avoid

1. **One-shot prompting the problem statement.** Explicitly graded against. Always
   translate through your own plan first.
2. **Stacking generations without running.** Cascading errors at minute 25.
3. **Accepting a 90%-correct generation and hand-patching the last 10%.** Usually slower
   than one clean reprompt, and produces half-AI/half-hand code you can't explain.
4. **Letting the AI redesign your architecture.** If you can't explain why the new shape
   is better, it's scope creep.
5. **No tests because the clock is running.** Costs more in debugging than it saves.
6. **Building broad, finishing nothing.** Narrow and complete wins.

---

## Pre-submit checklist (minute 26)

- [ ] Full test suite run, not just the last file
- [ ] No deleted or weakened tests in the diff
- [ ] No `any`, `# type: ignore`, or bare `except`
- [ ] No secrets/PII in code or logs
- [ ] Input validated at the boundary
- [ ] Every generated line is one I can explain
- [ ] Scope cuts stated explicitly rather than silently dropped
