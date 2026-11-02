# feed-ranker — env2 drill (30 min, AI allowed)

**What is graded is your process, not only the artifact.** One-shot prompting the request
below scores badly even if the output works. The signals are: how you decompose, how
precisely you specify I/O per step, whether you verify each increment, and whether you
catch bad AI output.

Existing code in `src/` — `store.py` is the data layer (do not rewrite it), `ranker.py`
is the stub you implement. Work in `drills/coding/scratch/`.

---

## The request

> Build the ranked home feed. Given a user, return the posts they should see, best first.
> Make it production-ready.

That is the whole ticket, as written. **It is deliberately underspecified** — part of the
exercise is deciding what it means and saying so before you build.

---

## How the drill runs

**Minutes 0–3 — orient.** Read `store.py`. Know the types, the methods available, and the
existing error convention before prompting anything.

**Minutes 3–6 — decompose out loud, in writing.** Post 3–4 named steps *before* your
first prompt. State what each produces. This window is scored on its own.

**Minutes 6–26 — build, one step per prompt.** For each prompt state input types, output
type, failure behavior, and which existing structures to use. Run after every generation.
Write the failing test before the implementation.

**Minutes 26–30 — full run, review, submit.** Nothing half-applied.

Ship a working slice by minute 20. If behind, cut scope out loud rather than silently.

---

## Ambiguities you are expected to surface

Do not ask for all of these to be resolved — decide, state the assumption, move on. The
graded behavior is *noticing* them.

- What does "best first" mean? Recency, engagement, or a blend — and with what weighting?
- Whose posts are eligible? Followed authors only? Does the user see their own?
- What happens to muted follows and deleted posts?
- Is `limit` bounded? What does `limit=0` or a negative do?
- What if the user follows nobody?
- Should engagement be time-decayed, or does a viral month-old post outrank everything?

---

## Definition of done

- `build_feed(user_id, limit)` returns `List[Post]`, ranked, honoring `limit`
- Input validated at the boundary, raising the store's existing `ValidationError` —
  not a new exception type
- Deleted posts and muted authors excluded
- Deterministic ordering — equal scores must not return in arbitrary order
- Tests covering: happy path, empty (no follows), single post, `limit=0`,
  `limit` > available, all-muted, deleted-only
- Type annotations throughout; no `Any` used to silence a real error
- No PII or user content in log lines

---

## After the attempt — the debrief questions

**D1.** Walk through your decomposition. Why that order?

**D2.** Show a prompt where the AI gave you something you rejected. What was wrong with
it and what did you do?

**D3.** What is the time complexity of `build_feed`? What dominates, and what would you
change first if the store held ten million posts?

**D4.** What did you cut for time, and what would you do next?
