Your brute-force `solve()` fires at every cell, averaging ~61 shots on a 10x10 board. Optimize it to average under 50 shots across 20 random games.

---

## Final solution

**43.8 average on the 20-game benchmark, worst case 43.8 across 10 seeds. Need < 50.**

The framing that makes this click: **chasing is cheap, searching is expensive.** On a 100-cell board with a budget of ~50 shots, sinking a found ship costs almost nothing — it's contiguous, you just walk it. Nearly the entire budget goes on *finding* ships in the first place. So the optimization has to attack the search, not the chase.

```python
from typing import List, Set, Tuple

from board import Board, ShotResult


class Solver:
    def __init__(self, board: Board):
        self.board = board
        self.shots: List[Tuple[int, int]] = []
        self._fired: Set[Tuple[int, int]] = set()
        self._targets: List[Tuple[int, int]] = []

    def solve(self) -> None:
        n = self.board.grid_size
        hunt = [(r, c) for r in range(n) for c in range(n) if (r + c) % 2 == 0]

        while not self.board.all_sunk():
            if self._targets:                       # chase a live ship first
                cell = self._targets.pop()
            elif hunt:                              # otherwise search
                cell = hunt.pop()
            else:
                return                              # nothing left — don't spin

            if cell in self._fired:
                continue

            self._fired.add(cell)
            self.shots.append(cell)

            if self.board.check_shot(*cell) == ShotResult.HIT:
                r, c = cell
                for nb in ((r-1, c), (r+1, c), (r, c-1), (r, c+1)):
                    if 0 <= nb[0] < n and 0 <= nb[1] < n and nb not in self._fired:
                        self._targets.append(nb)

    def get_shots(self) -> List[Tuple[int, int]]:
        return self.shots
```

One loop. The hunt list is precomputed once; `_targets` is the chase stack; `_fired` is the dedupe index.

**`from board import Board, ShotResult`** — importing only `Board` gives `NameError: name 'ShotResult' is not defined` on the first HIT, which is what the four test errors were.

### Why there's no `clear()` on SUNK

An earlier version cleared `_targets` when a ship sank, reasoning that leftover leads were stale. It fails when two ships are adjacent:

```text
Cruiser   [(4,2),(4,3),(4,4)]
Submarine [(5,2),(5,3),(5,4)]
```

Sinking the Cruiser discards queued leads — but some pointed at the **Submarine**. `(5,2)` is odd-parity, so hunting never revisits it, and the game ends with a ship alive. A queued neighbour is worth shooting regardless of which ship queued it, so the branch comes out entirely.

---

## The earlier, overcomplicated version

Kept for the comparison — it works, at 37.5 on seed 42, but has four loops where one does.

```python
from typing import List, Set, Tuple
from board import Board, ShotResult


class Solver:
    def __init__(self, board: Board):
        self.board = board
        self.shots: List[Tuple[int, int]] = []
        self._fired: Set[Tuple[int, int]] = set()
        self._targets: List[Tuple[int, int]] = []

    def solve(self) -> None:
        while not self.board.all_sunk():
            cell = self._next_cell()
            if cell is None:
                return                          # board exhausted — no infinite loop
            result = self._fire(cell)
            if result == ShotResult.HIT:
                self._queue_neighbors(cell)     # a ship is here; chase it
            elif result == ShotResult.SUNK:
                self._targets.clear()           # that ship is done; stale leads

    def _next_cell(self):
        while self._targets:                            # target mode wins
            cell = self._targets.pop()
            if cell not in self._fired:
                return cell
        n = self.board.grid_size
        for row in range(n):                            # hunt mode: parity cells
            for col in range(n):
                if (row + col) % 2 == 0 and (row, col) not in self._fired:
                    return (row, col)
        for row in range(n):                            # fallback: anything left
            for col in range(n):
                if (row, col) not in self._fired:
                    return (row, col)
        return None

    def _queue_neighbors(self, cell) -> None:
        row, col = cell
        n = self.board.grid_size
        for r, c in ((row-1, col), (row+1, col), (row, col-1), (row, col+1)):
            if 0 <= r < n and 0 <= c < n and (r, c) not in self._fired:
                self._targets.append((r, c))

    def _fire(self, cell):
        self._fired.add(cell)
        self.shots.append(cell)
        return self.board.check_shot(*cell)

    def get_shots(self) -> List[Tuple[int, int]]:
        return self.shots
```

## The two ideas

**1. Hunt/target.** The brute-force sweep learns nothing from its own results — it fires at (0,5) whether or not (0,4) just came back HIT. But a hit is information: ships are contiguous, so the neighbouring cells are far likelier than random ones. So run two modes. **Hunt** looks for a ship; the moment one is found, **target** chases it by pushing the four orthogonal neighbours onto a stack and draining that stack until the ship sinks.

**2. Parity.** While hunting, only fire at cells where `(row + col) % 2 == 0` — the black squares of a chessboard. Every ship is at least 2 cells long, so it *must* cover at least one black square. You can ignore half the board and still be mathematically guaranteed to find every ship.

## Measured — and the surprise

I benchmarked each idea alone and together, 20 games, seed 42:

| Version | Average shots | |
|---|---|---|
| Brute sweep | 68.3 | FAIL |
| Parity hunting only | **83.0** | FAIL — *worse than brute force* |
| Hunt/target, no parity | 62.2 | FAIL |
| **Hunt/target + parity** | **37.5** | **PASS** |

**Parity alone makes it worse.** That's the counterintuitive result and it's the most interesting thing to say about this problem. Reason: parity guarantees you *find* every ship, but finding isn't sinking. Skipping half the cells means when you do hit something, you've skipped the very neighbours you now need — so you go on to sweep the remaining white squares anyway, and you've spent shots in a worse order than a plain sweep would have.

**Hunt/target alone barely helps** (62.2 vs 68.3) — it chases ships efficiently but wastes most of its shots looking for them, and a 10×10 with two small ships is mostly water.

**Together they multiply.** Parity halves the search, and hunt/target makes the skipped cells recoverable — once you hit, the target stack fills in the white squares around the hit. Neither idea works alone; both together roughly halve the shot count. *That* is the insight this question is testing, not "use parity."

## Checked across seeds, not just seed 42

The test uses `random.Random(42)`, so tuning to one seed risks a solution that passes by luck:

| seed | 1 | 7 | 42 | 99 | 2024 | worst |
|---|---|---|---|---|---|---|
| hunt/target + parity | 45.8 | 39.0 | 37.5 | 43.1 | 38.3 | **45.8** |

Worst case 45.8, still under 50 — but the margin is thinner than the seed-42 number suggests. Worth saying out loud: the headline is 37.5, the honest number is "under 50 on every seed I tried, worst 45.8."

## Details that matter

**`_fired` is a set, `shots` is a list.** They look redundant but answer different questions: `shots` is the ordered audit trail the test compares against `total_shots()`, `_fired` is the O(1) membership index checked on every iteration. `in` on a list is O(n). Same split as `_occupied` vs `_ships` on the board.

**Deduplication is now mandatory, not cosmetic.** The sweep couldn't repeat a cell by construction; this one can — the target stack may queue a cell twice from two different hits. And a duplicate is silently corrupting here, because of the `bug2` behaviour: `check_shot` returns `MISS` for a repeat, so a re-fire is *told there's no ship* where there is one. It also breaks the `len(get_shots()) == total_shots()` assertion, since the board early-returns without recording. Both the `_next_cell` pop-loop and `_queue_neighbors` filter against `_fired`.

**Clearing `_targets` on SUNK.** Leftover neighbours from a now-dead ship are stale leads. Not clearing them isn't wrong — just wasted shots on cells adjacent to a ship that's already gone.

**The `None` guard.** If `all_sunk()` never goes True, the `while` spins forever. Not hypothetical on this codebase — that's exactly the half-fixed-sink-check scenario. Returning on an exhausted board turns a hang into a visible failure.

## Note on running the test

`test_should_be_efficient` calls `random.Random(42)` but `test_solver.py` has no `import random`. Un-commenting it as-is raises `NameError` — add the import first, or you'll debug a solver that's fine.

---

## Follow-up: What is the time complexity of your optimized solution? How does it compare to brute force?

**Both are O(n²). The optimization is a constant factor, not a complexity change.** Say that plainly — the temptation is to claim a better class because the numbers improved a lot, and that's the wrong answer.

### Why it's still quadratic

The hunt list holds every parity cell — that's n²/2 of them. Fire all of those and you've done n²/2 shots. Halving a quadratic leaves a quadratic: **O(n²/2) = O(n²)**, because big-O drops constant multipliers by definition.

The chase adds at most 4 neighbours per hit, and hits are bounded by total ship cells, which is a fixed fleet — not growth. Every step in the loop is constant-time: `pop()` off a list, a set lookup, a set add, an append, and `check_shot` (set lookups plus a bounded loop over the fleet).

**Worst case is exactly n²/2**, measured by placing ships at the end of hunt order:

| board | cells | parity cells | shots fired |
|---|---|---|---|
| 6×6 | 36 | 18 | 21 |
| 10×10 | 100 | 50 | 51 |
| 12×12 | 144 | 72 | 72 |
| 14×14 | 196 | 98 | 97 |

Shots track the parity count, converging to exactly half the board. Brute force in its worst case fires n² — all of it. So the ratio is 2×, and it stays 2× at every size. **A constant factor that doesn't shrink as n grows is the definition of same-complexity-class.**

### How they compare in practice

Averages over 20 random games, both solvers, as the board grows:

| board | cells | optimized | brute force | ratio |
|---|---|---|---|---|
| 6×6 | 36 | 20.3 | 25.6 | 1.26× |
| 8×8 | 64 | 28.1 | 43.0 | 1.53× |
| 10×10 | 100 | 43.8 | 68.3 | 1.56× |
| 12×12 | 144 | 54.8 | 95.8 | 1.75× |

Both curves are quadratic — both roughly quadruple when the side doubles. The optimized one is a lower quadratic. The advantage doesn't grow with n in complexity terms; it's a steady ~1.5–1.75× on these fleet sizes.

### The part worth volunteering

**Big-O is the wrong instrument for this test, and knowing that is the actual signal.** The efficiency test measures *shots fired at a fixed board size*, and big-O measures *how work grows as size changes*. Two solvers can be identical in big-O and one still fails the test — which is precisely what happened here: brute force and the optimized version are both O(n²), and only one passes.

Worth naming: the fleet is fixed at 2 ships. If the fleet grew with board area — say, ships covering a constant fraction of cells — the analysis changes, because hits would scale with n² and the chase would stop being negligible. **The constants only hold still because the fleet does.**

### What I'd say

"They're both O(n²), and I'd want to be upfront about that because the numbers improved enough that it's tempting to claim something better. The hunt list is every parity cell, which is n²/2, so worst case we fire half the board — and halving a quadratic is still a quadratic. I checked that: at 10×10 the worst case is 51 shots against 50 parity cells, at 14×14 it's 97 against 98, so it really does track exactly half. Brute force fires all n² in its worst case, so we're a clean 2× better, and that 2× holds at every board size rather than widening — which is what makes it a constant factor rather than a complexity improvement. The per-shot work is constant either way: popping off a list, a couple of set operations, and `check_shot`, which loops the fleet but the fleet is fixed. What I'd actually flag is that big-O is the wrong instrument for the question the test is asking. That test measures shots fired at a fixed 10×10, and big-O measures how work grows as the board changes — so both solvers are O(n²) and only one of them passes, which tells you the notation can't see the thing being graded. And the constants only stay put because the fleet is fixed at two ships; if the fleet scaled with the board area then hits would scale with n² too, the chase would stop being negligible, and I'd have to redo the analysis."

---

## Appendix — the earlier version's commentary

"So the brute-force version has one real weakness, which is that it doesn't learn anything from its own results — it fires at the next cell whether or not the previous one came back as a hit. And a hit is genuinely informative, because ships are contiguous, so the neighbours are much likelier than anywhere else on the board. So I've split it into two modes: hunting, where we're looking for a ship, and targeting, where we've found one and we chase it by pushing the four neighbours onto a stack and draining that until it sinks. Then the second idea is parity — while hunting we only fire where row plus column is even, so the black squares. Every ship is at least two cells long, which means it has to cover at least one black square, so we can ignore half the board and still be guaranteed to find everything. Now the thing I'd actually want to flag is that neither of those works on its own. I benchmarked them separately and parity alone is *worse* than brute force — 83 shots against 68 — because it guarantees you find a ship but not that you sink it, so you skip the very neighbours you need and end up sweeping the white squares anyway. And hunt/target on its own only gets you from 68 to 62, because it's still spending most of its shots looking. Together they're 37.5, which passes. So the interesting part isn't parity, it's that parity only pays off once something else can recover the cells you skipped. I also ran it across five different seeds rather than just the 42 the test uses, and the worst case was 45.8 — still under, but a thinner margin than the headline number suggests, so I'd rather quote that one."

---

The brute-force approach is a solvable solution, but it can be taxing depending on what you're trying to do. A more optimized solution would use more intelligence or logic rather than just covering all of the cells. In the brute-force approach, the results from firing a shot don't actually teach you anything. However, when you're actually playing the game, a hit is genuinely informative because the ships will have neighbors. We can also be able to rule out areas where ships are not applicable. For example, if there are only two dots left and we're looking for a three-cell ship, then you can cancel out those cells. That means we're reducing shots fired on unlikely cells and increasing shots fired where hits are occurring, so we can sink the ship more quickly with fewer shots actually fired. It is a more optimized solution because there is some intelligent learning occurring during the loop.

---

What went well

You correctly identified the core intuition behind your optimization, namely that a HIT result is informative and should direct subsequent shots toward neighboring cells rather than continuing to scan blindly.

You recognized that the checkerboard hunt pattern reduces the number of cells visited in the hunt phase, which is a real improvement over exhaustive scanning.

What needs improvement

You never gave any actual Big-O expressions, so your answer lacks the quantitative precision expected in a complexity analysis, for example the hunt phase visits roughly N²/2 cells on a grid of size N, giving O(N²) worst-case time, the same asymptotic class as brute force, and you need to explicitly state that the worst case does not improve.

You did not distinguish between worst-case and expected-case complexity, which is the critical insight here since your checkerboard pattern halves expected hunt shots and target mode adds at most O(S) overhead per ship of size S, but an adversarial placement can still force O(N²) shots in the worst case.

Minor suggestions

It is worth noting that your _targets list is used as a stack while hunt is also a stack, so in the worst case both can hold O(N²) entries simultaneously, meaning your space complexity is also O(N²), which is worth mentioning alongside time complexity.

---

## Better version — short

The intuition was all there. What was missing is the notation, and they told you exactly which four things to say. Lead with the expressions, then explain.

**1. Say the letters.** Worst case O(n²), same as brute force. Space O(n²).

**2. Split worst case from typical case.** This is the one they called critical, and it's the only place the two solvers differ:

| | Brute force | Optimized |
|---|---|---|
| Worst case | n² | n²/2 → still **O(n²)** |
| Typical (10×10) | 68.3 | 43.8 |

Parity halves the *search*, so the typical case improves. It cannot help the worst case, because a ship can always hide in the last parity cell you check. **The asymptotic class doesn't move.**

**3. Say the worst case explicitly doesn't improve.** Halving a quadratic leaves a quadratic — O(n²/2) = O(n²). Measured: 51 shots against 50 parity cells at 10×10, 97 against 98 at 14×14. It tracks exactly half, and half of quadratic is quadratic.

**4. Mention space.** `hunt` and `_targets` are both lists, `_fired` and `shots` both grow per shot — all O(n²). Space is O(n²) too.

### On terminology — "hunt" vs "search"

Standard naming is confusing: **hunt** = firing blind, looking for any ship; **target** = chasing a ship you've already hit. So "hunting" is the *un*targeted mode. "Search and chase" says the same thing more clearly, and is fine to use out loud as long as you name the standard terms once.

### The ruling-out idea is a real technique

Eliminating cells where no live ship could *fit* — two blanks in a gap when the smallest remaining ship is 3 — is **probability density targeting**, and it's the strongest known Battleship strategy. Parity is a crude approximation of it: parity says "a 2-cell ship must touch a black square," while density says "score every cell by how many placements of live ships cover it, then fire at the maximum."

It also strictly dominates parity, because it adapts as ships sink — once the 2-cell ship is gone the minimum length rises and you can skip more. Not needed to pass this test, but naming it as the next step is a strong close.

### What I'd say

"So it's O(n²) worst case, which is the same class as brute force, and O(n²) space as well. The distinction I'd want to draw is between worst case and typical case, because that's where these two actually differ. In the hunt phase — the searching phase, before we've hit anything — parity means we only visit about n²/2 cells, so a 10×10 is 50 rather than 100, and that halving is what takes us from roughly 68 shots down to 44 in practice. But it doesn't touch the worst case: a ship can always be sitting in the last parity cell we look at, so we still fire n²/2, and halving a quadratic leaves a quadratic. I measured it — 51 shots against 50 parity cells at 10×10, 97 against 98 at 14×14 — so it really does track exactly half. Then targeting adds at most four neighbours per hit, and hits are bounded by total ship cells, which is a fixed fleet, so that's a constant. Space is also O(n²): the hunt list, the target stack and the fired set can all hold on the order of n² entries. And the thing I'd actually want to add — parity is really a rough version of a better idea, which is ruling out cells where no remaining ship could physically fit. If the smallest live ship is three cells and there's only a two-cell gap, nothing can be there and we shouldn't spend a shot on it. That's probability density targeting, and it adapts as ships sink where parity doesn't. We don't need it to get under 50, but it's where I'd go next."

---

## What algorithm family is this actually?

Worth knowing, because it doesn't sit neatly in the usual taxonomy — and that mismatch is why big-O kept being the wrong instrument.

**It is not "search" in the CS sense.** Searching normally means finding a value in a structure you can inspect — binary search, BFS, DFS. Here nothing is inspectable: the board answers one question at a time, and every question costs a shot.

The real family is **adaptive querying under uncertainty** — also called sequential decision-making or active learning. Formally it's a **group testing / noiseless search** problem: identify a hidden configuration in as few queries as possible, where each query returns partial information you use to pick the next one. Its relatives are Mastermind, twenty questions, and sequential experiment design.

The defining property: **the metric is queries issued, not operations executed.** Complexity theory counts work; this problem counts questions. Different currencies — which is exactly why two O(n²) solvers can differ by 24 shots.

Nearest textbook neighbours:

| Family | Applies here? |
|---|---|
| Graph search (BFS/DFS) | Partly — target mode is a frontier expansion from a seed cell |
| Constraint satisfaction | Yes — "which placements are still consistent with what I've seen?" |
| Bayesian inference | Yes — density targeting is a posterior over ship placements |
| Greedy | Yes — fire at the current best cell, no lookahead |
| Searching a data structure | No — there's nothing to traverse |

### Is "hunt/target" real terminology?

**Yes, but it's domain jargon, not CS vocabulary.** "Hunt mode / target mode" is standard in Battleship-solver literature (Nick Berry's DataGenetics analysis is the usual reference). An interviewer who knows the problem will recognize it; one who doesn't needs a gloss.

So use it *and* define it: *"the standard framing is hunt and target — firing blind to find a ship, then chasing it once you've hit."* Knowing the domain term and being able to explain it beats either alone.

Note the terminology is genuinely confusing: **"hunting" is the blind phase**, not the targeted one. Search-and-chase is clearer if you say the standard names once.

The transferable CS terms — the ones that travel to other problems:

- **Parity / lattice argument** — the "every ship covers a black square" reasoning
- **Frontier** or **worklist** — `_targets` is the same pattern as BFS's queue
- **Greedy** — best cell now, no lookahead
- **Constraint propagation** — the ruling-out idea
- **Adaptive / sequential algorithm** — the umbrella term

---

## Follow-up: Explain your optimization strategy. How does it reduce shots vs brute force?

Brute force has one flaw: **it ignores its own results.** It fires at (0,5) whether or not (0,4) just came back HIT. Every shot is wasted information.

Two changes, each attacking a different half of the problem.

### 1. Chase after a hit — makes sinking cheap

Ships are contiguous. So a HIT tells you the rest of that ship is orthogonally adjacent. On every hit, push the four neighbours onto `_targets` and drain that stack before resuming the search.

Brute force walks the whole board between hitting a ship's first cell and its last. Chasing finds the remaining cells immediately.

### 2. Parity while searching — makes finding cheap

Every ship is at least 2 cells, so it must cover at least one cell where `(row + col)` is even — the black squares. Search only those and you cover half the board while still being guaranteed to find every ship.

### Why both are needed — the measured surprise

| Version | Avg shots (10×10) | |
|---|---|---|
| Brute force | 68.3 | |
| Parity only | **83.0** | *worse than brute force* |
| Chase only | 62.2 | barely helps |
| **Both** | **43.8** | **passes** |

**Parity alone is worse than doing nothing.** It guarantees you *find* a ship but not that you *sink* one — you skipped exactly the neighbours you now need, so you sweep the white squares afterwards anyway, in a worse order than a plain sweep.

**Chasing alone barely helps**, because on a mostly-empty board almost every shot is spent searching, not chasing.

**Together they compound**: parity halves the search, and chasing recovers the skipped cells whenever it matters. The real insight isn't "use parity" — it's that **parity only pays off once something else can fill in the cells it skips.**

### Where the savings come from

Brute force spends ~n² shots, nearly all on water. The optimized version spends about half that searching, plus a small bounded amount chasing. Since chase cost is tied to fleet size and search cost is tied to board size, **the search is where all the savings are** — which is why halving it moves the number so much.

### What I'd say

"So the problem with brute force is that it doesn't use its own results at all — it fires at the next cell in order whether or not the previous shot was a hit, and a hit is genuinely informative because ships are contiguous. So the first change is that whenever we hit something, we push the four neighbouring cells onto a stack and work through those before going back to searching. That makes actually sinking a ship cheap, because we're walking along it instead of stumbling back across it later. The second change is parity — while we're searching we only fire where row plus column is even, so half the board. And that's safe because every ship is at least two cells long, which means it has to cover at least one of those cells; we can skip half the board and still be guaranteed to find everything. Now the part I found genuinely surprising is that neither of those works on its own. I benchmarked them separately, and parity by itself is actually *worse* than brute force — 83 shots against 68 — because it guarantees you find a ship but not that you sink it, so you've skipped the very neighbours you need and end up sweeping the other half anyway. And chasing on its own only gets you from 68 to 62, because on a mostly-empty board you're spending nearly all your shots looking rather than chasing. Together they're 44, which passes. So the way I'd put it is that the savings are all in the search half — chasing is bounded by the fleet, which is fixed, but searching scales with the board — and parity only pays off once you've got something that can recover the cells it skipped."

---

What went well

You articulated the core insight behind both optimizations clearly and correctly, explaining that the checkerboard pattern works because every ship must span at least two cells, and that the target stack exploits the contiguity of ships to sink them efficiently once found.

Your empirical benchmarking observation that parity alone performs worse than brute force is a genuinely sharp insight, and your explanation of why this happens (you skip the neighbors you need to sink the ship) shows you understand the interaction between the two strategies, not just each in isolation.

Minor suggestions

When you mention the smallest ship being 'at least two cells long,' note that your actual test fleet uses ships of size 3, which means you could use an even sparser checkerboard pattern like every third cell if you wanted to push the hunt phase further.

You use a list as a stack with `_targets.pop()` which is fine in Python, but naming it `_targets` and describing it as a stack in your explanation would be slightly clearer if you also mentioned that LIFO ordering means you tend to explore in one direction before backtracking, which helps when ships are long.

---

## Acting on the feedback

Both suggestions are real. The first is a genuine speedup **and** a trap, which makes it the more interesting one.

### 1. Sparser lattice — tie the spacing to the smallest *live* ship

The general rule isn't "parity." It's: **if the smallest remaining ship is length L, you only need to search every L-th cell** along the diagonal, because a ship of length L must cover one of them. Parity is just this rule with L=2.

The test fleet is `Cruiser(3)` + `Submarine(3)`, so L=3 and `(r + c) % 3 == 0` is legal — a third of the board instead of half. Measured over 10 seeds:

| Search pattern | avg (seed 42) | worst of 10 seeds | mean of 10 |
|---|---|---|---|
| Brute force | 68.3 | 83.2 | 72.1 |
| `% 2` parity | 43.8 | 43.8 | 40.2 |
| `% 3` lattice | **35.4** | **35.4** | **32.8** |

~19% fewer shots, all games still valid.

**But it is only safe for this fleet.** Run the same solver against `get_standard_fleet()`, which includes a 2-cell Destroyer:

| Search pattern | avg shots | games where a ship survived |
|---|---|---|
| `% 2` parity | 60.3 | **0 / 50** |
| `% 3` lattice | 53.5 | **13 / 50** |

A 2-cell ship can sit entirely between the `%3` lines, so it's never found — the solver terminates with a ship alive. **Faster on the test fleet, silently broken on the real one.**

So the honest version is to derive the spacing rather than hardcode it:

```python
spacing = min(ship.size for ship in fleet_still_afloat)   # 2 for standard, 3 for test
hunt = [(r, c) for r in range(n) for c in range(n) if (r + c) % spacing == 0]
```

`Board` doesn't expose the live fleet, so with the current interface `%2` is the correct choice — it's safe for any fleet with a 2-cell ship, which is every standard game. Worth saying: *"I'd tie the spacing to the smallest surviving ship if the board exposed it; hardcoding 3 passes this fixture and breaks on a standard fleet."*

This is also the same idea as the ruling-out instinct from the last answer — spacing-by-minimum-length is constraint propagation with one constraint. Recomputing it as ships sink is what makes density targeting strictly stronger.

### 2. Name the LIFO behaviour

`_targets.pop()` takes from the end, so the stack is **LIFO** — depth-first. After a hit, that means the solver commits to one direction and walks it until it fails, then backtracks to the other neighbours.

That's the right choice here: ships are straight lines, so continuing in the direction that just worked is more likely to hit than switching. A FIFO queue (`pop(0)`) would expand evenly in all four directions — breadth-first — and waste shots probing sideways off a ship it's already walking along.

Worth naming out loud as *"a stack, so depth-first — we commit to a direction and walk it, which suits ships being straight."*

### What I'd add to the answer

"...and one thing worth flagging on the search spacing — the general rule isn't really parity, it's that if the smallest ship still afloat is L cells long, we only need to check every L-th cell, because a ship that long has to cover one of them. Parity is just that with L equals two. Our test fleet is two three-cell ships, so I could go to every third cell and it drops from about 44 shots to 35. But I'd want to be careful there, because that's only safe for this fleet — I ran it against the standard fleet, which has a two-cell destroyer, and it fails to sink everything in about a quarter of games, since a two-cell ship can hide between the lines. So I'd rather derive the spacing from the smallest surviving ship than hardcode it, and since `Board` doesn't expose that, parity is the safe choice with the current interface. And on the target stack — it's LIFO, so we're depth-first: after a hit we commit to one direction and walk it before backtracking. That suits ships being straight lines; a queue would expand evenly in all four directions and waste shots probing sideways off a ship we're already walking."
