Walk through what happens when you call place_ship(Ship('Cruiser', 3), row=0, col=0, horizontal=True). How does the board track which cells are occupied?

These questions test your understanding of the codebase. Take your time and reference the code as needed.

Be specific

Name actual methods, variables, and data structures from the code.

Trace the steps

Walk through execution in order. Say what happens first, second, third.

Explain the why

Don't just describe what the code does — explain why it's built that way.

---

"the function place_ship defines the ship type and size being placed by row and col as well as orientation, as ships can be placed vertically or horizontally on the board. Based on the ship size, the function loops over the board to check whether the coordinates of the ship can be placed. If out of bounds or overlaps with another ship, it returns an error; otherwise, it appends the coordinates of the ship. Occupation is a static term stored with the board as ships are placed and can be returned with self.occupied."

---

What went well

You correctly identified the core purpose of the function, including that it handles both horizontal and vertical placement and validates for out-of-bounds and overlap conditions before placing the ship.

You showed an understanding that occupied cells are tracked as part of the board's state and can be retrieved, which reflects the right mental model.

What needs improvement

You didn't explain the actual data structures involved, specifically that occupied cells are stored in a set of tuples called _occupied for overlap detection, and that the ship's cells are also stored separately in a_ships dictionary keyed by the ship's name.

You missed tracing through the loop concretely, for example explaining that with horizontal=True and size 3, the loop produces cells (0,0), (0,1), and (0,2) by incrementing the column index each iteration.

Minor suggestions

Using precise attribute names like _occupied and_ships when discussing internal state would make your answer sound more grounded in the actual implementation.

Mentioning the horizontal versus vertical branching explicitly, such as noting that vertical placement increments the row instead of the column, would add a nice touch of completeness.

---

place_ship(Ship('Cruiser', 3), row=0, col=0, horizontal=True) runs in two phases: a validate-all-then-commit pass.

Phase 1 — build and validate. It initializes a local cells: List[Tuple[int,int]] and loops for i in range(ship.size) — 3 iterations, since Ship is a NamedTuple with .name and .size. Each iteration derives (r, c): with horizontal=True it should be (row, col + i), giving (0,0), (0,1), (0,2). Each candidate is checked twice — bounds (0 <= r,c < self._grid_size, which is 6 in main.py) and overlap ((r,c) in self._occupied) — and each failure raises ValueError naming the ship.

Phase 2 — commit. Only after all 3 cells validate does it mutate state: each cell is added to self._occupied, and self._ships[ship.name] = cells stores the ship's full footprint keyed by name.

Why two structures for the same cells. _occupied is a Set[Tuple[int,int]] — it answers "is this cell taken?" in O(1), which is what both overlap validation and check_shot's hit/miss test need. _ships is a Dict[str, List[...]] — it answers the inverse question, "which cells belong to this ship?", which is what sink detection needs. A single structure would make one of those a linear scan. They're redundant on purpose.

Why validate-then-commit. If it added cells to _occupied as it went, a placement that fails on cell 3 would leave cells 1 and 2 permanently occupied by a ship that doesn't exist — corrupt board, no rollback. Building the local cells list first makes the failure atomic.

But it doesn't actually do that. Lines 31–34 are:

if horizontal:
    r, c = row, col + i
else:
    r, c = row, col + i   # ← bug: should be row + i, col
Both branches are identical. Vertical placement lays the ship horizontally. It's invisible in main.py because both test-fleet ships are placed horizontal=True; it surfaces the moment you place vertically — silently, as a wrong-shaped ship rather than an exception.
