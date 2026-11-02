Look at check_shot(). What are the three possible return values, and under what conditions does each one occur? How does it decide between HIT and SUNK?

These questions test your understanding of the codebase. Take your time and reference the code as needed.

Be specific

Name actual methods, variables, and data structures from the code.

Trace the steps

Walk through execution in order. Say what happens first, second, third.

Explain the why

Don't just describe what the code does — explain why it's built that way.

--

"`check_shot()` returns three different shot results. First, it identifies or defines what a miss is, which is stored as part of the board class itself. We can see where the hits and misses are, and where the occupant actually is. So if it has already been hit, or if it has already been identified as a miss, then obviously it returns a miss—hopefully you’re not asking this again.

But then, if the row and column of the cell indicate that the location is not yet sunk, you can calculate the hit count by looking for cells in that column that have been hit. If the hit count is equal to the number of cells minus one, then we return the shot as sunk. But if the hit count is not equal to that value, then it becomes a hit rather than a sunk ship. Yay."

---

You're on the right track.

What went well

You correctly identified all three return values and got the core conditions right, including that a duplicate shot (already hit or already a miss) returns MISS.

You understood the HIT vs SUNK distinction and correctly described the hit count comparison against the number of cells minus one.

What needs improvement

Your explanation of how the code finds which ship owns the cell was vague, and you missed the key detail that the code iterates through a list of ships to locate the one containing the targeted cell before doing the count.

You described the sunk check as looking at cells 'in that column,' which is imprecise and suggests some confusion about the data structure being iterated, which is actually the ship's own list of cells.

Minor suggestions

It would be worth noting that the hit count loop starts from index 1 rather than index 0, which is a subtle detail that could indicate a potential bug or an intentional design choice worth questioning.

---

`check_shot(row, col)` returns a `ShotResult` enum — `MISS`, `HIT`, or `SUNK` — and it resolves them in that order, as three sequential gates. It reads three of `Board`'s five state structures: `_hits` and `_misses` (both `Set[Tuple[int,int]]`), `_occupied` (`Set[Tuple[int,int]]`), and `_ships` (`Dict[str, List[Tuple[int,int]]]`), plus `_sunk` (`Set[str]`, ship names).

**Gate 1 — duplicate shot → MISS.** `if (row, col) in self._hits or (row, col) in self._misses`. This is a pure early return: it does not mutate anything, because the cell is already recorded in whichever set it came from. Note what this costs — a repeat shot on a cell that was a *hit* is reported as `MISS`. The contract is "this shot yields no new information," not "there is no ship here." A Solver that re-shoots will be actively misled, so this is the thing to clarify with the interviewer rather than assume.

**Gate 2 — empty water → MISS.** `if (row, col) not in self._occupied`, then `self._misses.add((row, col))` and return. `_occupied` is the union of every placed ship's cells, built in `place_ship`. It's a set, so this is the O(1) membership test — the reason `place_ship` maintains `_occupied` separately from `_ships` at all. Testing "is there a ship here?" against `_ships` would mean scanning every ship's cell list.

**Gate 3 — a hit; is it also a sink?** Past both gates, the cell is occupied and unshot, so `self._hits.add((row, col))` records it unconditionally. Now it has to answer the harder question: HIT or SUNK. That requires knowing *which* ship owns this cell and whether that ship's remaining cells are all hit — which is exactly what `_occupied` cannot tell you, and what `_ships` exists for.

So it iterates `for name, cells in self._ships.items()`, looking for the ship whose `cells` list contains `(row, col)` and whose `name` is not already in `_sunk`. This is the step the feedback said I was vague on: the loop is over the **ships dictionary**, and the inner containment check is against **that ship's own list of cells** — not a column, not the board. Having found the owner, it counts how many of that ship's cells are in `_hits`; if the count equals the ship's length, the ship just went down, so `name` is added to `_sunk` and it returns `SUNK`. Otherwise `HIT`.

**Why two structures, again.** This method is the clearest justification for the redundancy in `place_ship`. Gate 2 is a set lookup because it asks a cell-keyed question; gate 3 is a dict scan because it asks a ship-keyed question. `_occupied` makes the common case (most shots are misses) O(1); `_ships` makes the rare case (a hit) answerable at all. Collapsing them would make one of the two paths linear in board size.

**Why `_sunk` is a set of names, not of cells.** Sinking is a property of a ship, and `all_sunk()` / `remaining_ships()` compare `len(self._sunk)` against `len(self._ships)` — both keyed by name. Storing cells would force a re-derivation every time.

### The bug the feedback gestured at

Line 57 is:

```python
hit_count = sum(1 for c in cells[1:] if c in self._hits)
if hit_count == len(cells) - 1:
```

`cells[1:]` skips the ship's **first** cell, and the threshold is correspondingly `len(cells) - 1`. Those two offsets cancel only if the first cell is guaranteed hit — and nothing guarantees that. Concretely, for the Cruiser at `(0,0),(0,1),(0,2)`:

- Shoot `(0,1)` then `(0,2)` then `(0,0)`. On the final shot, `_hits` holds all three. `cells[1:]` is `[(0,1),(0,2)]`, both hit, so `hit_count == 2 == len(cells) - 1` → returns `SUNK`. Correct, by luck.
- But shoot `(0,0)` then `(0,1)`: `cells[1:]` is `[(0,1),(0,2)]`, only one hit, `hit_count == 1 != 2` → `HIT`. Correct.
- The break: shoot `(0,1)` then `(0,2)` **without ever shooting `(0,0)`**. `cells[1:]` is fully hit, `hit_count == 2 == len(cells) - 1` → returns `SUNK` while `(0,0)` is still untouched. The ship is declared sunk with a cell alive, `_sunk` gains the name, `all_sunk()` can return `True` on a board with unhit ship cells.

The fix is to count the whole footprint against the whole length:

```python
hit_count = sum(1 for c in cells if c in self._hits)
if hit_count == len(cells):
```

This matters for the Solver: a hunt/target solver that reports a win off `all_sunk()` will report false wins on any ship it approaches from the non-first end.

### What I'd say to the interviewer

"Three gates in order — duplicate, empty water, occupied. The first two are set lookups against `_hits`/`_misses` and `_occupied`; the third scans `_ships` to find the owning ship and counts its hit cells. Two things I'd flag: a repeat shot on a hit cell returns `MISS`, which is a defensible 'no new information' contract but will mislead a solver, and the sink count uses `cells[1:]` against `len(cells) - 1`, which declares a ship sunk when every cell *except the first* is hit. Should I fix that or work around it?"
