# rate-limiter — env1 drill (45 min, no AI)

Object-oriented design under time. No starter code — you design the interface as well as
the implementation. Work in `drills/coding/scratch/`.

This is the format `dsa/object_oriented_design/` has zero coverage of, and it is a common
45-minute assessment shape.

---

## Phase 1 — clarify before designing (5 min)

Write down the questions you would ask before writing any code. Then answer them yourself
and state your assumptions — you have no interviewer here.

At minimum you should be deciding: what identifies a caller, whether limits are per-caller
or global, what happens on rejection, whether the clock is injectable, and whether this
runs in one process or many.

**A design that does not state its assumptions cannot be evaluated. Write them down.**

---

## Phase 2 — design and implement (20 min)

Build a `RateLimiter` that allows at most **N requests per caller per rolling window of W
seconds**.

```python
limiter = RateLimiter(max_requests=5, window_seconds=60)
limiter.allow("user-123")   # -> True while under the limit, False once over
```

Requirements:

- Rolling window, not fixed buckets — 5/minute must not permit 10 requests across a
  boundary in two seconds
- O(1) amortized per call; do not rescan all history on every request
- Memory must not grow without bound as callers come and go
- Time must be injectable so tests do not sleep
- Type annotations throughout

State your data structure choice and its complexity **before** you write it.

---

## Phase 3 — tests (10 min)

Write them yourself. Cover at minimum: under limit, exactly at limit, over limit,
window expiry allowing again, boundary behavior across the window edge, multiple
independent callers, and `max_requests=0`.

Do not use `time.sleep` — that is what injectable time is for.

---

## Phase 4 — extend and analyze (10 min)

**4a.** Add `remaining(caller_id) -> int` and `retry_after(caller_id) -> float`. What
should each return when the caller has never been seen?

**4b.** State the time and space complexity of `allow`. Define your variables first.

**4c.** Your limiter runs in one process. The service now runs on twelve instances behind
a load balancer. What breaks, and what would you change? Be specific about the failure —
"it doesn't work distributed" is not an answer.

**4d.** A caller sends one request every 61 seconds forever. What happens to memory in
your implementation? If the answer is "it grows," fix it.

---

## Phase 5 — self-review (5 min)

Before declaring done, run this checklist:

- Every test run, not just the last one
- Empty / single / zero / boundary cases covered
- No swallowed exceptions
- Every identifier you would need to name out loud, named
- The fix stated for anything you flagged
