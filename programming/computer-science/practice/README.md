# Lab: build the structures you've been trusting

> Six small pieces, each one the core of something you use daily: a dynamic array, a compact hash table, an LRU cache, compensated summation, a decoder for framed messages on a TCP stream, and TCP's retransmission timer. You'll write them from stubs against tests that pin the behaviour the chapters describe.

None of this is code you'd ship, since Python's own versions are faster and better tested. The point is that a structure you've written holds no mystery about what it costs. Each piece goes with a chapter, so do it after reading that one.

## Run it

You need Python 3.14 and [uv](https://docs.astral.sh/uv/). From this folder:

```bash
bash check.sh              # the worked solution, then every code block in the chapters
bash check.sh exercises    # your copy of the lab. It fails until you've written it
bash check.sh network      # as the first, plus the blocks that need the internet
```

```text
ok    solutions/foundations_lab/  (24 passed in 0.10s)
ok    01-cost-models-and-big-o.md  (11 blocks ran, 6 compared exactly, 16 s)
ok    02-data-structures.md  (16 blocks ran, 8 compared exactly, 9 s)
ok    03-algorithm-patterns.md  (11 blocks ran, 6 compared exactly, 10 s)
ok    04-numbers-and-memory.md  (11 blocks ran, 2 compared exactly, 8 s)
ok    05-processes-threads-and-io.md  (13 blocks ran, 1 compared exactly, 16 s)
skip  06-networks.md:361  (needs the network; pass --network)
skip  06-networks.md:639  (needs the network; pass --network)
ok    06-networks.md  (7 blocks ran, 3 compared exactly, 1 s)
69 blocks passed, 0 failed, 2 skipped
```

That's CPython 3.14.7 on an Apple M4 Pro. The two skipped blocks are the ones that need the internet. `check.sh` removes the `.venv` and caches when it finishes. Untouched, `bash check.sh exercises` reports that all 24 tests fail, which is your starting point.

## What's checked in the notes

`run_notes.py` runs each Python block in `notes/` in its own temporary folder, and a block has to exit cleanly. Where a block's output is fixed, as with a parse or an exact sum, the printed output has to match exactly. Where it's a timing, a `<!-- measured -->` line in the note's source sits between code and output, and only the exit status counts, since your machine won't reproduce my numbers. So "compared exactly" in the output above means the printed text is checked, and the other blocks show what happened when I ran them.

Markers in the source say what a block needs: NumPy, the free-threaded build, the `openssl` command or the network. Use `--only 05` to run one chapter, and `--list` to see the blocks.

## What you're given

`exercises/foundations_lab/` holds the stubs and tests. `solutions/foundations_lab/` has the same tests and worked versions.

| File | What you build | After | What the tests pin |
|---|---|---|---|
| `dynamic_array.py` | A list with amortised append | [Chapter 2](../notes/02-data-structures.md) | Growth, and shrinking with hysteresis so that a pop and an append at the boundary don't both resize |
| `hash_table.py` | `CompactDict`, with insertion order kept in a separate entries array | [Chapter 2](../notes/02-data-structures.md) | Later keys still reachable after a delete, and order preserved |
| `lru_cache.py` | An LRU cache | [Chapter 2](../notes/02-data-structures.md) | Eviction order, and that a read counts as a use |
| `summation.py` | `neumaier_sum` | [Chapter 4](../notes/04-numbers-and-memory.md#summing-many-numbers) | An addend bigger than the running total |
| `framing.py` | `encode_frame`, `FrameDecoder` | [Chapter 6](../notes/06-networks.md#tcp-is-a-stream-not-messages) | Frames surviving a cut at any byte, over a real socket too, and an oversized header rejected before buffering |
| `rto.py` | `RtoEstimator` from RFC 6298 | [Chapter 6](../notes/06-networks.md#how-long-to-wait-before-resending) | The update order, the 1 s floor, the 60 s ceiling, backoff, and the clock granularity term |

## The steps

Run one piece's tests with `uv run pytest -k rto`, or another word from the test names, from `exercises/foundations_lab/`, and read each failing test before you start, since they're the specification. Open the solution only after you've tried.

1. **Dynamic array.** The growth factor is a parameter. Count the copies over a million appends for a few factors, and compare them with chapter 1's amortised argument.
2. **Hash table.** Write probing first, then deletion. The delete test fails if you simply clear the slot, and working out why teaches you more than the rest of the table does.
3. **LRU cache.** The stub suggests a `dict` from key to node, plus a doubly linked list for recency, with both operations O(1). Then rewrite it on a plain `dict`, relying on its insertion order, and compare the two.
4. **Summation.** Compare your result with `math.fsum` on values of very different sizes.
5. **Framing.** Keep the decoder's buffer between calls to `feed`, and check the length before you wait for the body.
6. **Retransmission timer.** Follow Section 2 of the RFC literally, in order. Swapping the two update lines is the classic bug.

## What to take from it

After the first three, you should be able to look at a slow piece of Python and say which operation is copying, which is probing, and what happens at a resize. After the last two, you've written the piece of nearly every network protocol that handles `recv`'s missing boundaries, and you've seen how a timeout is estimated, so you can reason about your own retry code.
