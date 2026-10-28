---
origin: web-authored
sources:
  - https://www.aibuilderclub.com/blog/self-improving-agent-loops
confidence: medium
cleaned: 2026-07-30
---
# The Evolve Loop — loops that rewrite themselves

> Topic note. Overview: [loop-engineering.md](loop-engineering.md).
> This is the **practitioner-scale** version of capability level 4
> ([loop-engineering.md §8](loop-engineering.md) covers the frontier/lab version —
> recursive self-improvement where the binding constraint is verification capacity).
> Same shape, different altitude: here the thing being rewritten is a config file, not a model.

---

## The definition

> **An evolve loop is a loop with a second, slower loop pointed at it. The fast loop does
> the work. The slow loop edits the fast loop.**

The critical distinction from RSI as usually discussed: **it does not retrain weights, it
rewrites files.** What improves is the *scaffolding* — the contract, the state, the
triggers, the procedure. The model is fixed. This is why it is available to any
practitioner today and why it belongs in the loop pillar rather than in a frontier-lab
footnote.

---

## Cadence and inputs

The slow loop runs roughly **every 5–10 runs of the fast loop** — often enough to catch
drift, rare enough that there is real evidence to read. A dedicated session reviews three
inputs:

1. **The loop's configuration** — its contract, goals, and boundaries. *What did we say
   success was?*
2. **State and logs** — what the agent believed versus what actually happened. *Where did
   the model of the world diverge from the world?*
3. **Raw conversation history** — where the agent flailed. This is the richest input: the
   thrash itself reveals cheap structural fixes that no metric surfaces.

## The four edit targets

| Target | What gets rewritten | Typical symptom that triggers it |
|---|---|---|
| **Contract** | The definition of success | Loop "succeeds" on runs you'd call failures |
| **State** | Stale or wrong entries | Agent acts on facts that expired |
| **Trigger logic** | When the loop wakes | Wakes constantly, finds nothing to do |
| **SOP steps** | Mechanical procedure | Same manual correction, every run |

**A worked example (Superdesign's support triage loop).** An expensive trigger was waking
the agent repeatedly to find no work. The evolve run wrote a JavaScript trigger script:
fetch SupportPlatform updates from the last 30 minutes, wake the agent only when real work exists.
No human designed that fix — the slow loop read the logs, saw the empty wakeups, and
rewrote its own trigger. Note the shape: the improvement was *structural and deterministic*,
not a better prompt.

---

## The anti-busywork rule

The most important guardrail, and it came out of a production failure:

> **Agents default to doing something even when nothing needs doing.**

An evolve session asked "what should change?" will *always* answer. It will manufacture
plausible edits to justify having run, and those edits degrade a working loop.

**The fix is explicit permission to change nothing** — make `no change needed` a
first-class success outcome, stated in the evolve session's contract, not an implicit
non-event. If "no change" is silent failure, you have built a machine that damages itself
on a schedule.

This generalizes past evolve loops to any reviewer/critic agent: *a reviewer that cannot
return "clean" is a reviewer that invents findings.*

---

## Failure modes

1. **Invented improvements** — changes manufactured to justify the run. (Countered by the
   anti-busywork rule above.)
2. **State rot** — unmaintained state poisons every subsequent evolve run, because state is
   one of the three inputs. Rot compounds: bad state → bad diagnosis → worse state.
3. **Compounding errors** — one bad evolve run degrades all future runs, since the next
   evolve session reads a config that is already wrong and reasons forward from it.
4. **Scope limit** — an evolve loop can improve a loop but **cannot decide whether the loop
   should exist at all.** That judgment stays human. A well-tuned loop doing useless work
   will tune itself further into uselessness.

**Human review of early diffs is essential.** The evolve loop earns autonomy the same way
every other loop does ([autonomy ladder](loop-autonomy-ladder.md)) — start at rung 1 with a
human approving each config rewrite, and climb only once the diffs are boring.

---

## Design checklist

- [ ] Is the evolve cadence tied to *runs* (5–10) rather than wall-clock time?
- [ ] Does the evolve contract explicitly bless "no change needed" as success?
- [ ] Is state pruned/expired as a maintained step, or does it just accumulate?
- [ ] Are evolve diffs reviewed by a human, and are they getting more boring over time?
- [ ] Who decides whether this loop should exist — and when do they revisit it?

---

## Working reference

`~/.claude/refs/agent-context.md` — prompt versioning and progressive disclosure (the
artifacts an evolve loop edits); `~/.claude/refs/agent-observability.md` — the trace
content the slow loop reads.

---

→ Related: [loop-autonomy-ladder.md](loop-autonomy-ladder.md) — earning the handoff.
