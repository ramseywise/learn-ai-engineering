place_ship(Ship('Cruiser', 3), row=0, col=0, horizontal=False), which cells should the ship occupy? Trace through the code carefully and note what actually happens.

These questions test your understanding of the codebase. Take your time and reference the code as needed.

Be specific

Name actual methods, variables, and data structures from the code.

Trace the steps

Walk through execution in order. Say what happens first, second, third.

Explain the why

Don't just describe what the code does — explain why it's built that way.

---

"So what I don’t understand is that it has a horizontal flag here. I would expect this to then be placing the ship along the vertical direction, but the code is actually exactly the same. It seems as if it is still treating it as horizontal. But then it would be going up and down the column, not across the row. And if it’s, like, three times,"

---
What went well

You correctly identified the core bug, noticing that the else branch behaves the same as the horizontal branch instead of doing something different.

You showed good instinct by recognizing that the flag being set to False should mean vertical placement but the code doesn't reflect that.

What needs improvement

You got a bit turned around when you said it would be going 'up and down the column' since the bug means it actually places horizontally, incrementing the column index, and you should state the actual cells it lands on like (0,0), (0,1), (0,2).

Try to complete your thought by stating what the fix should be, changing the else branch to increment the row instead of the column, which would have shown full command of the problem.

Minor suggestions

Naming the specific variable that's wrong, col + i in the else branch, would make your explanation much crisper and easier for an interviewer to follow.

---

The question has two answers and the gap between them *is* the question.

**What it should occupy.** `horizontal=False` means vertical placement, so a size-3 Cruiser anchored at `row=0, col=0` should run down the column: **(0,0), (1,0), (2,0)** — row increments, column stays fixed.

**What it actually occupies.** `place_ship` loops `for i in range(ship.size)` and branches on the flag at [board.py:31-34](../src/board.py#L31-L34):

```python
if horizontal:
    r, c = row, col + i
else:
    r, c = row, col + i
```

Both branches are byte-identical. The `else` branch computes `col + i` when it should compute `row + i`. So the trace is:

| `i` | branch taken | `(r, c)` | should be |
|---|---|---|---|
| 0 | `else` | (0, 0) | (0, 0) |
| 1 | `else` | (0, 1) | (1, 0) |
| 2 | `else` | (0, 2) | (2, 0) |

The ship lands on **(0,0), (0,1), (0,2)** — horizontally, straight across row 0. `cells` is built with those three tuples, all three pass the bounds check (`0 <= r,c < 6`) and the overlap check (`_occupied` is empty), so nothing raises. `_occupied` gains the three cells and `_ships['Cruiser']` is set to `[(0,0),(0,1),(0,2)]`.

Verified by running it:

```text
>>> b.place_ship(Ship('Cruiser',3), row=0, col=0, horizontal=False)
>>> b._ships['Cruiser']
[(0, 0), (0, 1), (0, 2)]
```

**The fix.** One token:

```python
else:
    r, c = row + i, col
```

**Why this bug is dangerous — and why it survived.** It fails *silently*. There's no exception, no wrong-count, no crash: the board accepts the placement and reports a perfectly valid ship. Every downstream invariant still holds — three cells, in bounds, non-overlapping, correctly registered in both `_occupied` and `_ships`. The board is internally consistent and externally wrong.

It survives because `main.py` places both test-fleet ships with `horizontal=True` ([main.py:23-24](../src/main.py#L23-L24)), so the `else` branch never executes in the default run. The code passes its own smoke test. That's the general shape worth naming to an interviewer: **a branch that's never exercised by the happy path is where bugs live**, and identical if/else bodies are a copy-paste tell you can spot by shape before you even read the logic.

The second-order damage is placement collisions. Two ships intended to be perpendicular will both be laid horizontally, so a fleet that should fit will spuriously raise `ValueError: ... overlaps at (r, c)` — and the error points at the *second* ship, which is innocent. The symptom surfaces nowhere near the cause.

### What I'd say to the interviewer

"It should occupy (0,0), (1,0), (2,0) — vertical, incrementing the row. It actually occupies (0,0), (0,1), (0,2), because the `else` branch is a copy of the `if` branch: it computes `col + i` when it should compute `row + i`. It fails silently — no exception, the board stays internally consistent — and `main.py` only ever places horizontally, so the broken branch never runs in the default test. Fix is `r, c = row + i, col`. Want me to fix it now, or note it and keep reading?"
