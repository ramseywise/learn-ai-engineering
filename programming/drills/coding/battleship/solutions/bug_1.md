First bug is changing place_ship to pass test_vertical_placement to pass.

```python
def place_ship(self, ship: Ship, row: int, col: int, horizontal: bool) -> None:
        cells: List[Tuple[int, int]] = []
        for i in range(ship.size):
            if horizontal:
                r, c = row, col + i
            else:
                r, c = row + i, col
```

Explain the bug you found in ship placement. Why does the else branch produce the wrong result?

---

"Okay. So the grid is the representation of each point in the ship size. When we place a ship, we take the original row and column. But because it's horizontal, we only adjust each point in the ship size along the column. In other words, it moves along the column axis. Before, the else branch was exactly the same, which meant it was still being placed horizontally—adjusting along the column. We just needed to switch the grid indicator for where we're moving along the row/column axis from the column to the row, so we can see it's actually a vertical placement."

---

## Tightened version

`place_ship` walks `for i in range(ship.size)` and derives one cell per iteration. The anchor is `(row, col)`; `i` is the offset along whichever axis the ship runs. The flag picks the axis:

- `horizontal=True` → hold `row` fixed, advance the column: `r, c = row, col + i`
- `horizontal=False` → hold `col` fixed, advance the row: `r, c = row + i, col`

The `else` branch was a verbatim copy of the `if` branch — both computed `col + i`. So `horizontal=False` still advanced the column, laying the ship horizontally.

Concretely, a Cruiser (size 3) at `row=0, col=0, horizontal=False` should occupy **(0,0), (1,0), (2,0)**. It actually occupied **(0,0), (0,1), (0,2)**:

| `i` | actual `(r,c)` | correct `(r,c)` |
|---|---|---|
| 0 | (0, 0) | (0, 0) |
| 1 | (0, 1) | (1, 0) |
| 2 | (0, 2) | (2, 0) |

The fix is one token — `col + i` → `row + i`, with the increment moved to the row position:

```python
else:
    r, c = row + i, col
```

`test_vertical_placement` shoots `(1,0)` and expects `HIT`. Before the fix, `(1,0)` isn't in `_occupied` — the ship is sitting in row 0 — so it returned `MISS`.

**Why it's dangerous.** It fails silently. No exception, no crash: all three cells pass the bounds check and the overlap check, and the board registers them in both `_occupied` and `_ships`. Every internal invariant holds — three cells, in bounds, non-overlapping, correctly indexed. The board is internally consistent and externally wrong.

**Why it survived.** `main.py` places both test-fleet ships with `horizontal=True`, so the `else` branch never executes in the default run. The code passes its own smoke test.

The second-order damage is placement collisions: two ships meant to be perpendicular both get laid horizontally, so a fleet that should fit raises `ValueError: ... overlaps at (r, c)` — and the error names the *second* ship, which is innocent. Symptom nowhere near cause.

### What I'd say to the interviewer

"The `else` branch is a copy-paste of the `if` branch — both compute `col + i`, so `horizontal=False` still walks the column. A size-3 ship at (0,0) vertical should land on (0,0), (1,0), (2,0) but lands on (0,0), (0,1), (0,2). Fix is `r, c = row + i, col`. It's silent — no exception, the board stays internally consistent — and `main.py` only places horizontally, so the broken branch never runs in the default test. Identical if/else bodies are a shape you can spot before reading the logic."
