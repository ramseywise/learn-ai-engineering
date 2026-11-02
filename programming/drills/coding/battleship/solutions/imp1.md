Implement solve() in solver.py. It should fire shots at the board until all ships are sunk. Track every shot in self.shots. Use self.board.check_shot(row, col) to fire and self.board.all_sunk() to check if you're done.

---

## The solution — linear sweep

Passes all three assertions in `test_solver.py`.

```python
def solve(self) -> None:
    for row in range(self.board.grid_size):
        for col in range(self.board.grid_size):
            if self.board.all_sunk():
                return
            self.board.check_shot(row, col)
            self.shots.append((row, col))
```

Three requirements, three mechanisms:

- **No duplicate shots** — the nested `range` visits each cell exactly once. There's nothing to dedupe, so no set is needed. Correct by construction rather than by guard.
- **Shot tracking** — append after every `check_shot`, which keeps `len(self.shots)` and `board.total_shots()` in lockstep.
- **Sinks all ships** — a full sweep necessarily covers every occupied cell.

The `all_sunk()` check goes **before** the shot, not after, so the loop exits the moment the last ship dies instead of sweeping the remaining water.

Measured on the fixed 6×6 test board: 21 shots, `len(shots) == total_shots()`, zero duplicates, `all_sunk()` True.

## Commentary

**Why this is the right first answer.** The prompt asks for correctness — fire until sunk, track shots, no duplicates. It says nothing about efficiency. A working simple version plus a stated upgrade path beats a half-finished clever one, and this is ten lines that can't be wrong.

**What it doesn't pass.** The commented-out `test_should_be_efficient` wants an average under 50 shots on a 10×10. The sweep averages **68.3**. So this solution is correct and will need replacing at the next stage — worth saying out loud rather than waiting to be told.

**The upgrade is hunt/target with parity.** Every ship is at least 2 cells long, so it must cover at least one cell where `(row + col) % 2 == 0`. That means hunting can skip half the board and still be guaranteed to find every ship; on a hit, switch to draining a stack of orthogonal neighbours until it sinks. Measured: **37.5** average on a 10×10, versus 68.3 for the sweep. Worth naming during the sweep implementation even if it gets built second — the parity insight is the signal the question is fishing for.

**Duplicates would be silently catastrophic on this board.** Because of the bug from `bug2` — `check_shot` returns `MISS` for a repeat shot even on a cell that was a hit. A re-firing solver doesn't just waste a shot, it gets told there's no ship where there is one. And since the duplicate branch early-returns without touching `_hits` or `_misses`, `board.total_shots()` won't count the repeat while `len(self.shots)` will — which is exactly what the `len(get_shots()) == board.total_shots()` assertion catches. The sweep sidesteps this entirely; a hunt/target solver has to track fired cells in a set to stay safe.

---

## Background: what the notation actually means

Forget the symbols for a second. The question big-O answers is:

> **If the board gets bigger, how much more shooting do I have to do?**

That's it. It's about how the work *grows*, not how fast the computer is.

Our board is a square, n cells on a side. Make the side twice as long and you don't get twice as many cells — you get four times as many, because it grew in both directions at once. A 6×6 board is 36 cells; a 12×12 board is 144. Twice the side, four times the squares.

Since we might have to shoot every square, our work grows the same way. **That's all `O(n²)` says: the work follows the area, so doubling the side quadruples the job.** The "n" is the side length, the "²" is what makes it an area, and the O just means "grows like."

The other ones you'll hear, in the same terms:

| Notation | Spoken | If the board doubles… |
|---|---|---|
| O(1) | constant | nothing changes — checking one square takes the same time on any board |
| O(n) | linear | twice the work — walking down a single row |
| O(n²) | quadratic | **four times** the work — covering the whole board |

**A warning about the shortcut.** It's tempting to say "two loops inside each other means n²." That's true here and wrong often — it's counting the code instead of the work. Two loops over *different* things (ships and their cells) isn't n². One loop can be n² if the thing inside it is slow. Two loops one after the other isn't n² at all — you add them, not multiply. Ask what happens as the board grows; don't count `for` statements.

**Space works identically, just about memory instead of time** — how much *storage* grows with the board. And only what we allocate counts; things that already existed aren't ours.

---

## Follow-up: What is the time and space complexity of solve()?

**Time: O(n²). Space: O(n²).** Where n is the length of one side of the board — say that first, because n could mean the side or the number of cells and the answer changes.

### Time — why quadratic

Worst case we shoot every square, and a board n on a side has n² squares. Everything we do at each square is fixed-cost — checking whether the game is over, recording the shot, firing — so the total is just "one unit of work per square," and there are n² squares.

One honest wrinkle: `check_shot` does contain a loop over the ships. So strictly we're at n² × (number of ships). But the fleet is 2 ships here and 5 in a standard game — it's the same fleet whatever the board size — so it's a fixed multiplier, not growth. **Naming that and then explaining why you're setting it aside is the part that scores**; silently ignoring it looks like you missed it.

**And this really is the worst case, not a pessimistic guess.** Put a ship in the last row and we genuinely fire every shot:

| board | squares | shots fired |
|---|---|---|
| 6×6 | 36 | 36 |
| 10×10 | 100 | 100 |
| 12×12 | 144 | 144 |

### Space — why also quadratic

Because we keep a list of every shot, and there can be n² of them. The problem asked us to track them, so that's a requirement, not a leak.

The board's own bookkeeping (`_hits`, `_occupied`, `_ships`) doesn't count — it exists whether or not a solver ever runs. Interviewers do listen for whether you charge yourself for someone else's memory.

### "Can you do it in less?" — No, and that's the real answer

Ships can be hidden anywhere. So there's always an arrangement where the last square you check is the one with a ship on it, which means any correct solver has to be *willing* to check all of them. **That's a limit of the problem, not a flaw in the code** — no algorithm beats it in the worst case.

What can improve is how often you hit the worst case. Hunt/target with parity averages 37.5 shots on a 10×10 where the plain sweep averages 68.3 — clearly better, and still O(n²), because halving a quadratic leaves a quadratic.

Which is the genuinely interesting bit: **big-O can't tell these two solvers apart, but the efficiency test can.** That test measures shots fired; big-O measures growth. Knowing when the notation *isn't* the right instrument is worth more than reciting it.

### What I'd say

"So it's O(n²) for both time and space, with n as the length of one side of the board — I'll say that up front because n could just as easily mean the number of cells. The reasoning is that worst case we shoot every square, and a board that's n on a side has n² squares on it; everything we do at each square is fixed-cost, so it's one unit of work per square. There is one wrinkle I'd flag — `check_shot` loops over the ships internally, so strictly we're at n² times the fleet size. But the fleet is the same two or five ships whatever the board size, so that's a fixed multiplier rather than growth, and I'm setting it aside. And this is genuinely the worst case, not a pessimistic guess: if a ship sits in the last row we really do fire every shot, which I checked at 6, 10 and 12 and it comes out exactly n² each time. Space is the same, and it's all the shots list — the problem asked us to track every shot, so that's a requirement rather than something to optimise away; the board's own bookkeeping isn't ours to count. Now if you're asking whether we can do better than quadratic, I don't actually think we can, and I'd say that's a limit of the problem rather than the code — ships can be hidden anywhere, so there's always an arrangement where the last square we check is the one with a ship on it, and we have to be willing to look everywhere. What we *can* improve is how often we hit that worst case: hunt/target with parity gets us to about 37 shots on a 10×10 where the sweep averages 68, but it's still O(n²), because halving a quadratic is still a quadratic. Which I think is the interesting part — big-O can't tell those two solvers apart at all, so it's the wrong instrument for the efficiency test. That test is measuring shots fired, and big-O measures growth."

---
Okay. If we think of n as the grid size of the matrix itself, then we have n squared cells, which is the dominant term. With that inside a loop that checks the grid size, and inside of that we have another loop as well—so it’s technically O(n squared) times k for the loop inside the loop. But because the board is kind of small, that’s really okay. And so the space complexity is also O(n squared), for the shots."

---

What went well

You correctly identified that iterating over all cells in the grid produces an O(n²) dominant term, which is the core insight for this problem.

You recognized there is an additional factor from the inner work per shot, which shows you were thinking beyond just the nested loops in solve().

What needs improvement

You should be more precise about what that inner factor k represents, since in your actual code check_shot iterates over all ships and their cells, making the per-shot cost O(S *L) where S is the number of ships and L is the maximum ship length, giving a total time complexity of O(n²* S * L).

Your space complexity reasoning needs tightening because the shots list stores at most n² entries but you should also account for the board's internal sets like hits, misses, and occupied, which are all O(n²) as well, so the conclusion is correct but the justification was incomplete.

Minor suggestions

Since the grid is fixed and small in your implementation, noting that S and L are bounded constants is a reasonable practical simplification, but in an interview you should still state those variables explicitly before collapsing them.

---
Walk me through your implementation of solve(). How does it guarantee all ships are sunk?

---

Well, the implementation is sort of brute force, really. It loops over the entire grid and searches all the possibilities of where shots could be fired. During each check shot, it records whether it was a hit or a miss. Then, at the top of the loop, we ask whether everything gets sunk—when there are no more shots that can be made.

---

What went well

You correctly identified the brute-force nature of your approach, showing you understand the core strategy of exhaustively covering the grid.

You mentioned the early-exit condition using all_sunk(), which shows you understand the optimization built into your loop.

What needs improvement

Your explanation of why the approach guarantees all ships are sunk was vague. The guarantee comes specifically from iterating over every (row, col) pair in range(self.board.grid_size) for both dimensions, so no cell is ever skipped.

You described the early-exit condition slightly inaccurately by saying 'when there are no more shots that can be made' rather than 'when all ships are confirmed sunk via board.all_sunk()'.

Minor suggestions

When explaining a nested loop approach, naming the two variables explicitly, like row and col, makes it much clearer to an interviewer exactly what your iteration covers.

---

## Better version

The word "guarantee" is asking for a **proof**, not a description. You gave the description — brute force, loops the grid, records hits, checks `all_sunk()` at the top — which is all accurate, but it never actually closes the argument. The guarantee is three sentences and it has to be said as a chain:

1. **Every ship sits on cells of the board.** `place_ship` validates that every cell is within bounds, so no ship can be anywhere the loops don't reach.
2. **The loops reach every cell.** `for row in range(grid_size)` crossed with `for col in range(grid_size)` produces every `(row, col)` pair on the board. Nothing is skipped, nothing is conditional.
3. **Therefore every ship cell gets shot** — and a ship whose every cell is hit is sunk, by definition of `check_shot`.

That's the whole proof: *ships live on cells → we visit every cell → so we hit every ship.* Say those three steps and the question is answered.

### The two corrections

**Name the loop variables.** "It loops over the entire grid" is a claim; "`for row in range(grid_size)`, and inside that `for col in range(grid_size)`" is the evidence for it. The specific pairing is what makes "no cell is skipped" checkable rather than asserted.

**The exit is not "no more shots that can be made."** It's `board.all_sunk()` returning True — every ship confirmed sunk. Those are genuinely different conditions: running out of cells means the loop ended, while `all_sunk()` means the job finished. Conflating them matters here, because if the exit condition were "out of shots," the method would have no guarantee at all — it would just be stopping.

Worth being precise about what the early return buys, too: it's an **optimization, not the mechanism**. Delete the `all_sunk()` check entirely and every ship still sinks — you'd just keep firing at water afterwards. The guarantee comes from the exhaustive sweep; the check only saves the leftover shots.

### The honest caveat

This guarantees all ships sink *given the board behaves correctly*. On the unfixed board it doesn't hold — the `cells[1:]` bug means a ship can be fully hit and never marked sunk, so `all_sunk()` stays False, the sweep runs out of cells, and `solve()` returns with ships still standing. Naming that dependency shows you know where your correctness argument is resting.

### What I'd say

"So it's deliberately brute force — we walk `for row in range(grid_size)`, and inside that `for col in range(grid_size)`, which gives us every row-column pair on the board. And the guarantee actually comes out of that directly: ships can only be placed on cells, since `place_ship` bounds-checks them, and we visit every cell, so we necessarily shoot every cell any ship is sitting on — and a ship with all its cells hit is sunk. So it's really just: ships live on cells, we cover all the cells, therefore we sink all the ships. The `all_sunk()` check at the top of the loop is an early exit rather than the mechanism — if I deleted it we'd still sink everything, we'd just carry on shooting water afterwards, so it saves us the leftover shots and nothing more. One thing I'd flag is that the whole argument rests on the board reporting sinks correctly, and with the `cells[1:]` bug still in there it doesn't — a ship can be fully hit and never marked sunk, so we'd run out of cells with ships still standing. So I'd say this guarantees coverage; it guarantees sinking as long as `check_shot` is honest about it."
