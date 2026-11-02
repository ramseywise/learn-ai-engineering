# Env 1 — No AI, 45 min: comprehension, critical bugs, optimization

Solo, proctored, one attempt. This is the battleship format widened: read code you didn't
write, find what's wrong with it (including security and data-handling), and improve it.

Graded on: technical fundamentals, correctness of diagnosis, and **clear logic stated
plainly**. Not on volume of code written.

---

## The first 5 minutes — orient before touching anything

Do this in order. It's the difference between finding bugs and guessing at them.

1. **Read the data structures first.** What state exists? Keyed by what? Which structure
   answers which question? Two structures holding the same data is normal when they
   answer different questions (`_occupied`: "is this cell taken?" O(1); `_ships`: "which
   cells belong to this ship?").
2. **Read the tests.** They are the real spec. Commented-out or skipped assertions tell
   you the contract before it's enforced.
3. **Run everything.** Note what fails and what passes. A passing suite on buggy code
   tells you the tests only exercise the happy path.
4. **Map the entry point.** What does `main` actually call, with what arguments? Anything
   it never exercises is where bugs hide.

Say the shape out loud to yourself: *"N classes, state lives in X, tests cover Y, main
only ever does Z."*

---

## Where bugs actually hide — the patterns that recur

From battleship, and general:

| Pattern | Tell | Example |
|---|---|---|
| **Identical if/else branches** | Copy-paste shape, visible before reading logic | `if horizontal: r,c = row, col+i` / `else: r,c = row, col+i` |
| **Offsets that appear to cancel** | Two `-1`s, or a slice + adjusted threshold | `cells[1:]` counted against `len(cells)-1` |
| **Slice that skips an element** | `[1:]`, `[:-1]`, `range(1, n)` | first/last element silently excluded |
| **Off-by-one in bounds** | `<=` vs `<`, `n` vs `n-1` | reading one past the end |
| **Unexercised branch** | main/tests only hit one side | `horizontal=False` never run |
| **Mutation before validation** | state changed, then a raise | partial write, corrupt state, no rollback |
| **Early return that skips bookkeeping** | `return` before a counter increments | duplicate shot not recorded in `total_shots()` |
| **Order-dependent logic** | works if inputs arrive in index order | tests all shoot first-cell-first |

**The meta-rule: a branch or input order never exercised by the default run is where the
bug is.** Both battleship bugs hid there.

---

## Security and data-sensitivity review

No coverage of this in the DSA bank — read this section twice. Scan for these in any
codebase you're handed:

### Injection and untrusted input

- **SQL built by string concatenation / f-strings** → parameterized queries instead
- **`eval`, `exec`, `pickle.loads`, `yaml.load`** on anything user-supplied
- **`subprocess` with `shell=True`** and interpolated input
- **Path traversal** — user input reaching `open()` without normalizing `../`
- **Unvalidated deserialization** of request bodies

### Secrets and credentials

- Hardcoded API keys, tokens, passwords, connection strings
- Secrets in log lines, error messages, or exception text
- Credentials in default arguments or committed config

### Comparison and crypto

- **`==` on secrets/tokens/signatures** → `hmac.compare_digest` (timing attack)
- Plaintext password storage, or MD5/SHA1 for passwords → bcrypt/argon2
- Predictable tokens from `random` → `secrets` module

### PII and data handling

- Personal data written to logs (emails, names, addresses, card numbers)
- PII in exception messages that propagate to the client
- Full records returned where an ID would do — overexposure in responses
- Missing redaction on debug output
- Retaining data past its purpose

### Authz vs authn

- Authenticated but not **authorized** — "is this user logged in" ≠ "may this user
  read *this* record"
- IDs from the request trusted without an ownership check (IDOR)

### Error handling that hides problems

- `except: pass` / bare `except` swallowing failures
- Returning success on a failed write
- Catching and logging without re-raising where the caller must know

**How to phrase a finding:** name it, show the line, state the concrete exploit, give the
fix. *"Line 42 compares the signature with `==`, which short-circuits on the first
differing byte — that's a timing oracle for forging tokens. `hmac.compare_digest` fixes
it."*

---

## Optimization — the shape of the argument

From the battleship work, the moves that scored:

1. **Get correct first, then improve.** The linear sweep passed before the smart solver
   existed. Say out loud: *"this is correct but wasteful; here's what I'd change."*
2. **Name what dominates.** Where does the cost actually live? In battleship: searching
   scales with the board, chasing is bounded by the fleet — so all savings are in search.
3. **Distinguish complexity class from constant factor.** Halving a quadratic leaves a
   quadratic. If the fix is a constant factor, say so rather than claiming a better class.
4. **State when big-O is the wrong instrument.** If the metric is queries/shots/API calls
   rather than operations, say that — two O(n²) solutions can differ 2× and only one passes.
5. **Say when the bound is inherent.** "No algorithm does better in the worst case,
   because the target can always be in the last place you look" is a strong answer, not
   a failure.
6. **Measure, don't assume.** Parity *alone* was worse than brute force (83 vs 68). I'd
   have asserted the opposite.

### Complexity checklist

- Define your variable first — "n is the side length, so n² cells."
- Name any inner loop and say why you're dropping it ("k is fleet size, fixed").
- Give worst case *and* typical case separately when they differ.
- Space as well as time.
- Is the worst case actually reachable? Say so if you checked.

---

## Communication (no interviewer, but the write-up is graded)

If there's a text box for explanation, this is where fundamentals show. Rules from the
drill feedback:

- **Name the identifiers.** `_occupied`, a `Set[Tuple[int,int]]` — not "it's stored on
  the board."
- **Trace with real numbers, not variables.** "The slice gives 2 cells, compared against
  3, so it's never true." Not "n minus one can't resolve."
- **Finish with the fix.** Diagnosis is half; the one-line correction is the deliverable.
- **Coordinates over axis words.** "(0,0), (0,1), (0,2)" is self-correcting; "up and down
  the column" is not.
- **Cut vague caveats.** If you can't make a concern specific, delete it.
- **Structure a finding as:** what's wrong → concrete failing case → why it survived →
  the fix.

---

## Time plan (45 min)

| Time | Do |
|---|---|
| 0–5 | Orient: structures, tests, run, entry point |
| 5–15 | Find bugs. Trace failing tests with real values. Fix one at a time, re-run. |
| 15–25 | Security/data pass — run the checklist above explicitly |
| 25–35 | Implement whatever's asked; simplest correct version first |
| 35–42 | Edge cases, optimization if demanded, full re-run |
| 42–45 | Write-up / final submit |

**Never stack two untested fixes.** Run between each.

---

## Pre-flight checklist

- [ ] Imports complete? (`NameError: ShotResult is not defined` = 4 test errors from one
      missing name)
- [ ] All tests run, not just the one I was working on
- [ ] Edge cases: empty, single, duplicate, zero, boundary, negative
- [ ] Did I actually re-run after the last edit?
- [ ] Is there a security finding I noticed and didn't write down?
