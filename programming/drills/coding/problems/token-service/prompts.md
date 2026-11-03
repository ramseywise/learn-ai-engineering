# token-service — env1 drill (45 min)

Session token issuing and verification, backed by SQLite. **All 6 tests pass.**

```bash
cd src && python3 -m unittest test_tokens -v
```

Work in `programming/drills/coding/scratch/` — copy `src/`, don't edit it in place.

Answer as if an interviewer is reading. Be specific: name actual methods, variables and
data structures. Trace execution in order. Explain *why*, not just *what*.

---

## Phase 1 — comprehension (8 min)

**1a.** Walk through what happens when `issue_token("alice@example.com", "hunter2")` is
called on a registered user. What does the returned token contain, and what is each part
for?

**1b.** `verify_token` runs several checks in sequence. List them in order and say what
each one is defending against. Why is the ordering what it is — would any other order be
wrong?

---

## Phase 2 — security review (15 min)

**2a.** This code has multiple security defects. Find as many as you can. For each one:
name it, cite the line, state a **concrete exploit** (what an attacker sends and what they
get), and give the fix.

**2b.** Which single defect would you fix first if you could only ship one change before
the end of the day? Defend the ordering.

---

## Phase 3 — data handling (8 min)

**3a.** Separate from the exploitable defects, this service mishandles sensitive data in
ways that would fail a privacy review. Identify them and say what a correct version does
instead.

**3b.** `get_profile` takes both a token and a `target_user_id`. What is wrong with that
signature, and what would you change?

---

## Phase 4 — correctness and robustness (10 min)

**4a.** There is at least one non-security bug — logic that is simply wrong regardless of
any attacker. Find it and explain the failing case concretely.

**4b.** The test suite passes on all of the above. What does that tell you about the test
suite, and what tests would you add?

**4c.** Rewrite `delete_user` so it is correct. State every change and why.
