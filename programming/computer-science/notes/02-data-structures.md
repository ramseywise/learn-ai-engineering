---
origin: synthesis
sources:
  - "CPython 3.14.7, Objects/dictobject.c — https://github.com/python/cpython/blob/v3.14.7/Objects/dictobject.c"
  - "CPython 3.14.7, Objects/dictnotes.txt — https://github.com/python/cpython/blob/v3.14.7/Objects/dictnotes.txt"
  - "CPython 3.14.7, Objects/listobject.c — https://github.com/python/cpython/blob/v3.14.7/Objects/listobject.c"
  - "CPython 3.14.7, Objects/listsort.txt — https://github.com/python/cpython/blob/v3.14.7/Objects/listsort.txt"
  - "Raymond Hettinger, More compact dictionaries with faster iteration, python-dev 2012 — https://mail.python.org/pipermail/python-dev/2012-December/123028.html"
  - "Crosby and Wallach, Denial of Service via Algorithmic Complexity Attacks, USENIX Security 2003 — https://www.usenix.org/legacy/events/sec03/tech/full_papers/crosby/crosby.pdf"
  - "PEP 456, Secure and interchangeable hash algorithm — https://peps.python.org/pep-0456/"
  - "PEP 412, Key-Sharing Dictionary — https://peps.python.org/pep-0412/"
  - "Python docs: Time complexity, collections, heapq, bisect, Sorting techniques — https://docs.python.org/3/builtins/time-complexity.html"
  - https://arxiv.org/abs/1805.04154
concepts: [arrays-hashing, linked-list, stack, heap, trees, tries, design, dynamic-array, hash-table, open-addressing, cpython-list, cpython-dict, hash-flooding, powersort, key-sharing-dict]
confidence: high
cleaned: 2026-11-02
---
# 2 — Data structures

> Every Python program is mostly lists and dicts, and most people who write them can't say why `append` is fast, why a dict doesn't shrink when you empty it, or why a million-key dict iterates ten keys slowly. Those details turn into real outages: a work queue that gets slower the longer it runs, a cache that never gives memory back, an endpoint brought down by a few thousand crafted keys. This chapter reads the CPython source for `list` and `dict`, checks every claim with `sys.getsizeof` and a clock, and then covers the other structures you'll reach for and when each beats the obvious choice. The source is CPython 3.14.7, on 64-bit macOS, and the layout details are implementation choices that could change in another version.

---

## A list is an array of pointers with spare room

A Python `list` holds a C array of pointers plus two numbers: the length, and how many slots are allocated. Indexing is one multiplication and one memory read, so it's constant time regardless of length, and that's the property that every other cost here is traded against. The values themselves live elsewhere: a list of a million floats is a million pointers to a million objects. See [what an object costs](../../python/03-language-for-engineers/notes/09-memory-and-the-runtime.md#what-an-object-costs) for what those cost, and [chapter 4](04-numbers-and-memory.md#the-layout-decides-the-constant) for what that indirection does to speed.

The growth rule sits in `list_resize` in [`listobject.c`](https://github.com/python/cpython/blob/v3.14.7/Objects/listobject.c): the new allocation is `(newsize + (newsize >> 3) + 6) & ~3`. So it adds about 12.5%, plus a little to help small lists, rounded to a multiple of 4. You can watch that happen from Python, because `sys.getsizeof` reports the allocation:

```python
import sys

items = []
header = sys.getsizeof(items)
capacities = [0]
for i in range(1_000):
    items.append(i)
    capacity = (sys.getsizeof(items) - header) // 8
    if capacity != capacities[-1]:
        capacities.append(capacity)
print("header bytes:", header)
print("capacities:", capacities[:18])


def rule(size):
    return (size + (size >> 3) + 6) & ~3


predicted, capacity = [0], 0
for size in range(1, 1_001):
    if size > capacity:
        capacity = rule(size)
        predicted.append(capacity)
print("matches the rule in listobject.c:", capacities == predicted)
```

```text
header bytes: 56
capacities: [0, 4, 8, 16, 24, 32, 40, 52, 64, 76, 92, 108, 128, 148, 172, 200, 232, 268]
matches the rule in listobject.c: True
```

[Chapter 1](01-cost-models-and-big-o.md#the-two-sums-that-pay-for-most-analysis) showed why any fixed factor gives amortised constant-time appends. The factor sets the waste. A list that has just grown holds up to about 12.5% unused slots, and the allocation depends on how it was built:

```python
import sys


def capacity(xs):
    return (sys.getsizeof(xs) - sys.getsizeof([])) // 8


grown = []
for i in range(1_000):
    grown.append(i)
print("append 1000 times:      ", capacity(grown))
print("list(range(1000)):      ", capacity(list(range(1_000))))
print("[0] * 1000:             ", capacity([0] * 1_000))
print("copy of the grown list: ", capacity(grown.copy()))

seen = [capacity(grown)]
while grown:
    grown.pop()
    if capacity(grown) != seen[-1]:
        seen.append(capacity(grown))
print("capacity while popping: ", seen[:8], "...", seen[-3:])
```

```text
append 1000 times:       1100
list(range(1000)):       1000
[0] * 1000:              1000
copy of the grown list:  1000
capacity while popping:  [1100, 620, 352, 200, 116, 68, 40, 24] ... [8, 4, 0]
```

A list built by `append` carries 100 spare slots. One made with `[0] * n` or a copy carries none, so preallocating when you know the size saves that memory as well as the resizes.

The last line shows shrinking. The source keeps the allocation as long as `allocated >= newsize >= allocated >> 1`, so it only reallocates when the list falls below half full, and the new allocation has the same 12.5% slack computed from the smaller size. That's why capacities drop from 1100 to 620 and not to 550. The gap between shrink and grow points matters: if they were the same point, alternating `append` and `pop` at the boundary would resize every time. You'll build the failing version in the [lab](../practice/README.md).

## The expensive end of a list

Everything after an index has to shift when you insert or delete there. The [docs' table](https://docs.python.org/3/builtins/time-complexity.html) lists `pop(0)` and `insert` as `O(n)`. Used as a queue, a list turns into an arithmetic series of shifts. `collections.deque` is built for this, and [its docs](https://docs.python.org/3/library/collections.html#collections.deque) promise appends and pops from both ends in about constant time:

```python
import time
from collections import deque


def drain_list(n):
    q = list(range(n))
    while q:
        q.pop(0)


def drain_deque(n):
    q = deque(range(n))
    while q:
        q.popleft()


def timed(f, n):
    start = time.perf_counter()
    f(n)
    return (time.perf_counter() - start) * 1e3


print(f"{'n':>8} {'list.pop(0) ms':>15} {'deque.popleft ms':>17}")
for n in (25_000, 50_000, 100_000, 200_000):
    print(f"{n:>8,} {timed(drain_list, n):>15.1f} {timed(drain_deque, n):>17.1f}")
```

<!-- measured -->

```text
       n  list.pop(0) ms  deque.popleft ms
  25,000            30.4               0.4
  50,000           138.4               0.9
 100,000           572.1               1.9
 200,000          2305.7               4.0
```

Each doubling multiplies the list's time by about four, as you'd expect. In exchange, a deque gives up fast access to the middle, which the docs list as `O(n)` there. If you have a list named `queue` anywhere in a long-running service, check this first.

## A dict is a table of positions and an array of entries

A hash table turns a key into an array position, in three steps: compute `hash(key)`, reduce it to a slot number, and handle the case where the slot is taken. CPython resolves collisions by open addressing, meaning there are no chains. If a slot is taken, it probes another slot in the same table.

Since Python 3.6, the table has been split in two, following [Raymond Hettinger's 2012 proposal](https://mail.python.org/pipermail/python-dev/2012-December/123028.html). The hash table proper holds only small integers, positions into a second, dense array of entries. Each entry holds the hash, key and value, in insertion order:

```text
d = {"model": "m", "tokens": 512, "ms": 81}

dk_indices: 8 slots, one byte each
  slot    0    1    2    3    4    5    6    7
        [ . ][ 2 ][ . ][ 0 ][ . ][ . ][ 1 ][ . ]        . = EMPTY

dk_entries: dense, in insertion order (room for 5)
  0: hash("model")   "model"   "m"
  1: hash("tokens")  "tokens"  512
  2: hash("ms")      "ms"      81
  3: free
  4: free

The slot positions are illustrative: string hashes change per process.
```

Two good things come from this layout. Iterating walks the dense entries and so needs no scan of empty slots, and insertion order comes free, a property the language now guarantees. And the sparse part is small: a table of up to 128 slots needs 1 byte per slot and not a full 24-byte entry, because positions are small numbers, and the width only steps up to 2, 4 and then 8 bytes as the table grows. The comment at the top of [`dictobject.c`](https://github.com/python/cpython/blob/v3.14.7/Objects/dictobject.c) lays out the same design.

The size in bytes fits a simple model. The table is kept at most two-thirds full, by the `USABLE_FRACTION` macro. With `s` slots, the entries array has room for `2s/3` entries at 24 bytes each, and the index width depends on `s`:

```python
import sys

d = {}
print(f"empty dict: {sys.getsizeof(d)} bytes")
last = sys.getsizeof(d)
print(f"{'keys':>8} {'bytes':>9} {'bytes/key':>10}")
for i in range(1, 100_000):
    d[i] = None
    size = sys.getsizeof(d)
    if size != last:
        print(f"{i:>8,} {size:>9,} {size / i:>10.1f}")
        last = size


def model(log2_size):
    table = 2**log2_size
    usable = (table << 1) // 3
    index_width = 1 if table <= 0xff else 2 if table <= 0xffff else 4
    return table, usable, table * index_width, usable * 24


print(f"\n{'slots':>8} {'usable':>8} {'indices B':>10} {'entries B':>10}")
for k in (3, 4, 8, 16):
    print("{:>8,} {:>8,} {:>10,} {:>10,}".format(*model(k)))

print("\none int key:", sys.getsizeof({1: None}), "bytes; one str key:", sys.getsizeof({"a": None}), "bytes")
```

```text
empty dict: 64 bytes
    keys     bytes  bytes/key
       1       224      224.0
       6       352       58.7
      11       632       57.5
      22     1,168       53.1
      43     2,264       52.7
      86     4,688       54.5
     171     9,304       54.4
     342    18,512       54.1
     683    36,952       54.1
   1,366    73,808       54.0
   2,731   147,544       54.0
   5,462   294,992       54.0
  10,923   589,912       54.0
  21,846 1,310,800       60.0
  43,691 2,621,528       60.0
  87,382 5,242,960       60.0

   slots   usable  indices B  entries B
       8        5          8        120
      16       10         16        240
     256      170        512      4,080
  65,536   43,690    262,144  1,048,560

one int key: 224 bytes; one str key: 184 bytes
```

The numbers match. A one-key dict's 224 bytes are the 64-byte dict object, a 32-byte keys header, 8 index bytes and 5 entries at 24 bytes. Bytes per key peak just after a resize at 54 to 60, and halve before the next, and that's before you pay for the key and value objects. Resizes come at 6, 11, 22, 43 keys and on: the source asks for `used * 3` slots (`GROWTH_RATE`) rounded up to a power of two, so the table approximately doubles.

A dict with one string key is 184 bytes and not 224, because 5 entries each shrink by 8 bytes. An all-string table has a separate entry type with no hash field, since a string object already keeps its own.

## How probing avoids clusters

The first slot is `hash & (size - 1)`, the low bits of the hash, which is why table sizes are powers of two. Small integers hash to themselves, so consecutive ints go to consecutive slots with no collisions at all. The comment in `dictobject.c` calls this a good thing, in that the common case is fast, and then has to deal with the bad case: keys that differ only in their high bits all land in the same slot. Linear probing would then walk one long cluster.

CPython's probe sequence brings in the high bits gradually. It uses the recurrence `i = (5*i + perturb + 1) & mask`, shifting `perturb` right by 5 bits each step. With `perturb` at 0, the recurrence alone visits every slot in a power-of-two table, as the first line below shows. While `perturb` is non-zero, keys with the same low bits follow different paths:

```python
PERTURB_SHIFT = 5


def probes(h, size):
    """Slots CPython's recurrence visits for hash h in a table of `size` (a power of 2)."""
    mask = size - 1
    perturb = h
    i = h & mask
    while True:
        yield i
        perturb >>= PERTURB_SHIFT
        i = (i * 5 + perturb + 1) & mask


from itertools import islice

print("hash 0, size 8:      ", list(islice(probes(0, 8), 9)))
print("hash 1<<16, size 8:  ", list(islice(probes(1 << 16, 8), 9)))
print("hash 3<<16, size 8:  ", list(islice(probes(3 << 16, 8), 9)))


def insert_all(hashes, size, step):
    table = [False] * size
    total = 0
    for h in hashes:
        for slot in step(h, size):
            total += 1
            if not table[slot]:
                table[slot] = True
                break
    return total / len(hashes)


def linear(h, size):
    i = h & (size - 1)
    while True:
        yield i
        i = (i + 1) & (size - 1)


n = 6_000
size = 2**15
keys = [i << 16 for i in range(n)]
print(f"\nmean probes per insert, {n:,} keys i<<16 in {size:,} slots")
print(f"  CPython recurrence: {insert_all(keys, size, probes):8.2f}")
print(f"  linear probing:     {insert_all(keys, size, linear):8.2f}")
print(f"  sequential ints:    {insert_all(list(range(n)), size, probes):8.2f}")
```

```text
hash 0, size 8:       [0, 1, 6, 7, 4, 5, 2, 3, 0]
hash 1<<16, size 8:   [0, 1, 6, 1, 6, 7, 4, 5, 2]
hash 3<<16, size 8:   [0, 1, 6, 5, 2, 3, 0, 1, 6]

mean probes per insert, 6,000 keys i<<16 in 32,768 slots
  CPython recurrence:     3.91
  linear probing:      3000.50
  sequential ints:        1.00
```

Six thousand keys that all collide on their low bits cost about 4 probes each here, against 3,000 for linear probing. Sequential ints cost exactly 1. The same table holds both kinds of key without knowing in advance which it'll get.

## Deleting doesn't give anything back

You can't simply mark a deleted slot as empty, because other keys' probe sequences may run through it, and a lookup stops at the first empty slot. So deletion leaves a `DUMMY` in the index and a hole in the entries array. [`dictnotes.txt`](https://github.com/python/cpython/blob/v3.14.7/Objects/dictnotes.txt) says that resizing only happens on insertion, when the usable space runs out. That has real consequences:

```python
import sys
import time

d = {i: None for i in range(1_000_000)}
full = sys.getsizeof(d)
for i in range(999_990):
    del d[i]
print(f"full {full:,} bytes; after deleting all but {len(d)} keys {sys.getsizeof(d):,} bytes")

start = time.perf_counter()
for _ in range(100):
    for k in d:
        pass
hollow = (time.perf_counter() - start) / 100

fresh = dict(d)
print(f"after dict(d), a copy: {sys.getsizeof(fresh):,} bytes")
start = time.perf_counter()
for _ in range(100):
    for k in fresh:
        pass
compact = (time.perf_counter() - start) / 100
print(f"iterate 10 keys: hollow {hollow * 1e6:,.1f} us, fresh {compact * 1e6:,.2f} us")

next_key, before = 2_000_000, sys.getsizeof(d)
while sys.getsizeof(d) == before:
    d[next_key] = None
    next_key += 1
print(f"inserting {next_key - 2_000_000:,} new keys triggers a resize: {before:,} -> {sys.getsizeof(d):,} bytes")
```

<!-- measured -->

```text
full 41,943,128 bytes; after deleting all but 10 keys 41,943,128 bytes
after dict(d), a copy: 352 bytes
iterate 10 keys: hollow 241.6 us, fresh 0.13 us
inserting 1,398,092 new keys triggers a resize: 41,943,128 -> 83,886,160 bytes
```

Delete all but 10 of a million keys and the dict still holds 41.9 MB. Iterating it costs about 240 µs for 10 keys, because it walks the dense array past all the holes, while a fresh copy takes 0.13 µs. `dict(d)` is the fix, and it's a one-liner once you know you need it. The last line needs some arithmetic, and it comes out exact. A table of 2^21 slots has room for 1,398,101 entries, and the deleted million still occupy theirs, so 398,101 free entries remain. When they run out, the dict rebuilds from its 398,111 live keys. `used * 3` rounds up to 2^21 again, so it compacts in place at the same size, which `sys.getsizeof` can't show. The rebuilt table then takes another 999,991 inserts to fill, and that second resize is the one the block sees, at 1,398,092 inserts. By then all those keys are live, so the table doubles.

The hole-walking also makes a tempting pattern quadratic. A dict is ordered, so `next(iter(d))` looks like a way to get the oldest key:

```python
import time
from collections import OrderedDict


def drain_dict(n):
    d = dict.fromkeys(range(n))
    while d:
        del d[next(iter(d))]


def drain_ordered(n):
    d = OrderedDict.fromkeys(range(n))
    while d:
        d.popitem(last=False)


def timed(f, n):
    start = time.perf_counter()
    f(n)
    return (time.perf_counter() - start) * 1e3


print(f"{'n':>8} {'dict, oldest first':>19} {'OrderedDict':>12}   (ms)")
for n in (5_000, 10_000, 20_000, 40_000):
    print(f"{n:>8,} {timed(drain_dict, n):>19.1f} {timed(drain_ordered, n):>12.1f}")
```

<!-- measured -->

```text
       n  dict, oldest first  OrderedDict   (ms)
   5,000                 3.6          0.4
  10,000                13.6          0.8
  20,000                53.3          1.5
  40,000               205.7          2.9
```

Each `next(iter(d))` walks past all the holes left by earlier deletions, and that's an arithmetic series again. [`OrderedDict`](https://docs.python.org/3/library/collections.html#collections.OrderedDict) keeps a linked list and stays linear, and its docs say it handles frequent reordering better than a plain dict. I've seen this pattern in hand-rolled caches. It looks fine in a test, since the test doesn't run long enough for the holes to accumulate.

## Hash flooding, and why strings are randomised

All of the above assumes hashes spread out. [Crosby and Wallach (USENIX Security 2003)](https://www.usenix.org/legacy/events/sec03/tech/full_papers/crosby/crosby.pdf) showed that an attacker who can predict a hash function can force the worst case: send keys that all collide, and each insert scans all the previous ones. That makes a small amount of traffic do quadratic work on the server.

Python ints are a live demonstration, because their hash is public and documented. The docs [define it as a reduction modulo a prime](https://docs.python.org/3/library/stdtypes.html#hashing-of-numeric-types), 2^61 - 1 on this build, so every multiple of that prime hashes to 0:

```python
import subprocess
import sys
import time

P = 2**61 - 1
print("sys.hash_info.modulus == 2**61 - 1:", sys.hash_info.modulus == P)
print("hash of 0, P, 2P, 3P:", [hash(i * P) for i in range(4)])
print("hash(-1):", hash(-1), " hash(-2):", hash(-2))


def build(keys):
    start = time.perf_counter()
    d = {}
    for k in keys:
        d[k] = True
    return (time.perf_counter() - start) * 1e3


print(f"\n{'n':>7} {'ordinary ints ms':>17} {'multiples of P ms':>18}")
for n in (2_000, 4_000, 8_000, 16_000):
    print(f"{n:>7,} {build(range(n)):>17.2f} {build([i * P for i in range(n)]):>18.2f}")

cmd = [sys.executable, "-c", "print(hash('alice'))"]
runs = {subprocess.run(cmd, capture_output=True, text=True).stdout.strip() for _ in range(3)}
print("\nhash('alice') in three fresh processes: distinct values =", len(runs))
print("hash algorithm:", sys.hash_info.algorithm)
```

<!-- measured -->

```text
sys.hash_info.modulus == 2**61 - 1: True
hash of 0, P, 2P, 3P: [0, 0, 0, 0]
hash(-1): -2  hash(-2): -2

      n  ordinary ints ms  multiples of P ms
  2,000              0.04              17.22
  4,000              0.07              69.12
  8,000              0.17             273.49
 16,000              0.30            1091.42

hash('alice') in three fresh processes: distinct values = 3
hash algorithm: siphash13
```

Sixteen thousand ordinary ints take 0.3 ms to insert, and 16,000 colliding ones take over a second. That's a factor of 3,600, and the slope of 2 confirms that it's quadratic. Multiple values hash identically but compare unequal, so each insert walks everything.

Strings are the common case for keys from the outside world, and they're protected: [PEP 456](https://peps.python.org/pep-0456/) made SipHash the default, keyed with a random value per process, so an attacker can't compute collisions offline. You see the two consequences above: `hash('alice')` differs between runs, and the algorithm reports as `siphash13`. Never persist `hash()` of a string, and never use it to partition data across processes. Use `hashlib` for that. Ints, however, are still predictable. If a service takes integer ids from a client and uses them as dict keys, this block is what a hostile client can do, so bound the input's size or validate it.

The small oddity on the third line, `hash(-1) == -2`, is in the same [documented algorithm](https://docs.python.org/3/library/stdtypes.html#hashing-of-numeric-types): a final step turns -1 into -2.

## Instances share their keys

Objects of one class tend to have the same attributes, so storing those keys per instance is wasteful. [PEP 412](https://peps.python.org/pep-0412/) added key-sharing dictionaries: instances of a class share one keys table and each holds only its values. `dictnotes.txt` says memory savings can reach 60% for object-oriented programs. Here's what that comes to:

```python
import tracemalloc


class Request:
    def __init__(self, model, tokens, ms):
        self.model = model
        self.tokens = tokens
        self.ms = ms


def footprint(build, n=100_000):
    tracemalloc.start()
    keep = [build(i) for i in range(n)]
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del keep
    return current / n


print(f"plain dict per record:      {footprint(lambda i: {'model': 'm', 'tokens': i, 'ms': 1.5}):7.1f} bytes")
print(f"instance per record:        {footprint(lambda i: Request('m', i, 1.5)):7.1f} bytes")


def with_dict(i):
    r = Request("m", i, 1.5)
    r.__dict__  # asking for it materialises a dict object
    return r


print(f"instance, __dict__ touched: {footprint(with_dict):7.1f} bytes")
```

<!-- measured -->

```text
plain dict per record:        223.9 bytes
instance per record:          135.9 bytes
instance, __dict__ touched:   199.8 bytes
```

Compare 224 bytes for a dict with 136 for an instance holding the same three fields. Note the third line: merely reading `r.__dict__` creates a dict object for each instance, and costs another 64 bytes. Code that touches `__dict__` on every record, for logging or serialisation, gives some of the savings back. For more on `__slots__` and object sizes, see [memory and the runtime](../../python/03-language-for-engineers/notes/09-memory-and-the-runtime.md#what-an-object-costs).

## Sorting exploits what is already ordered

CPython's sort is a stable, adaptive merge sort, described by its author at length in [`listsort.txt`](https://github.com/python/cpython/blob/v3.14.7/Objects/listsort.txt). It looks for runs that are already sorted, reverses descending ones, and merges them, choosing the merge order with the powersort strategy of [Munro and Wild](https://arxiv.org/abs/1805.04154). I read their abstract and the description in `listsort.txt`, not the proofs. Count its comparisons on inputs with different amounts of existing order:

```python
import math
import random


class Counted:
    __slots__ = ("v",)
    count = 0

    def __init__(self, v):
        self.v = v

    def __lt__(self, other):
        Counted.count += 1
        return self.v < other.v


def comparisons(values):
    Counted.count = 0
    sorted(Counted(v) for v in values)
    return Counted.count


n = 100_000
rng = random.Random(3)
shuffled = rng.sample(range(n), n)
ten_runs = [v for run in range(10) for v in sorted(rng.sample(range(n), n // 10))]
nearly = list(range(n))
for _ in range(100):
    i, j = rng.randrange(n), rng.randrange(n)
    nearly[i], nearly[j] = nearly[j], nearly[i]

print(f"n = {n:,}   lg(n!) = {sum(math.log2(i) for i in range(2, n + 1)):,.0f}")
for name, values in [
    ("random", shuffled),
    ("already sorted", list(range(n))),
    ("reversed", list(range(n, 0, -1))),
    ("10 sorted runs joined", ten_runs),
    ("sorted, 100 random swaps", nearly),
]:
    print(f"{name:<26} {comparisons(values):>10,}")

logs = [("gpt", 3), ("claude", 1), ("gpt", 1), ("claude", 3)]
print(sorted(logs, key=lambda r: r[1]))
```

```text
n = 100,000   lg(n!) = 1,516,704
random                      1,532,037
already sorted                 99,999
reversed                       99,999
10 sorted runs joined         439,975
sorted, 100 random swaps      112,156
[('claude', 1), ('gpt', 1), ('gpt', 3), ('claude', 3)]
```

Random input needs 1,532,037 comparisons, 1% above the theoretical minimum from [chapter 1](01-cost-models-and-big-o.md#logarithms-are-what-halving-looks-like), so the sort isn't wasting anything. Sorted and reversed inputs cost `n - 1`. Ten sorted runs joined together cost less than a third of random, and that case is common in practice: merged log files, or results from shards. The lower bound only covers arbitrary input, and real data has structure.

The last line shows stability: items with equal keys keep their relative order. The [sorting how-to](https://docs.python.org/3/howto/sorting.html) notes that this lets you sort by several keys in successive passes, from least to most significant.

When you need sorted output and comparisons are costly, a `key=` function is called once per element. When you have a custom comparison, the counts above are the number of calls you're paying for.

## Heaps: the top of something large

A binary heap is an array where each element is no greater than its two children, at positions `2k+1` and `2k+2`. That's the whole [invariant `heapq` documents](https://docs.python.org/3/library/heapq.html). It gives you the smallest item at index 0, and pushing and popping cost `log n`. It doesn't give you sorted order, so `heap[1]` isn't the second smallest in general.

The classic use is keeping the `k` largest of a stream without sorting it. Replace the smallest of your `k` whenever something bigger arrives, and each item costs at most `log k`:

```python
import heapq
import random
import time

rng = random.Random(5)
latencies = [rng.lognormvariate(4, 1) for _ in range(2_000_000)]


def timed(f):
    start = time.perf_counter()
    result = f()
    return result, (time.perf_counter() - start) * 1e3


def bounded_heap(stream, k):
    heap = []
    for x in stream:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    return sorted(heap, reverse=True)


full, t_sort = timed(lambda: sorted(latencies, reverse=True)[:100])
mine, t_heap = timed(lambda: bounded_heap(latencies, 100))
lib, t_lib = timed(lambda: heapq.nlargest(100, latencies))
assert full == mine == lib
print(f"top 100 of {len(latencies):,}")
print(f"sorted then slice: {t_sort:8.1f} ms")
print(f"bounded heap:      {t_heap:8.1f} ms")
print(f"heapq.nlargest:    {t_lib:8.1f} ms")

h = [3, 8, 5, 9, 12, 7]
print("heap invariant:", all(h[k] <= h[c] for k in range(len(h)) for c in (2 * k + 1, 2 * k + 2) if c < len(h)))
```

<!-- measured -->

```text
top 100 of 2,000,000
sorted then slice:    259.7 ms
bounded heap:          24.5 ms
heapq.nlargest:         9.2 ms
heap invariant: True
```

On 2 million latencies, the library version is 28 times faster than sorting and holds only 100 items. It also works on a stream you can't hold in memory. Dijkstra's algorithm in [chapter 3](03-algorithm-patterns.md#graphs-are-one-loop-with-a-different-bag) uses the same structure as a priority queue. When `k` is close to `n`, a full sort is simpler and competitive, so use a heap when `k` is small.

## Sorted lists and bisect

`bisect` does binary search over a sorted list, in `log n` comparisons. Its `insort` also has to insert, which is `O(n)`, as [the docs warn](https://docs.python.org/3/library/bisect.html). So maintaining a sorted list one item at a time is quadratic overall, and in practice the shift dominates long before the search does:

```python
import bisect
import random
import time

rng = random.Random(9)


def run(n):
    xs = [rng.random() for _ in range(n)]
    start = time.perf_counter()
    out = []
    for x in xs:
        bisect.insort(out, x)
    insort_ms = (time.perf_counter() - start) * 1e3
    start = time.perf_counter()
    sorted(xs)
    return insort_ms, (time.perf_counter() - start) * 1e3


print(f"{'n':>9} {'insort each ms':>15} {'sort once ms':>13}")
for n in (25_000, 50_000, 100_000):
    insort_ms, sort_ms = run(n)
    print(f"{n:>9,} {insort_ms:>15.1f} {sort_ms:>13.1f}")
```

<!-- measured -->

```text
        n  insort each ms  sort once ms
   25,000            44.8           1.8
   50,000           172.9           3.7
  100,000           677.3           8.4
```

At 100,000 items, sorting once is 80 times faster. If you have all the data up front, sort it once and then bisect. Keep a list sorted incrementally only if you really do need order between inserts, and it stays small. For the search itself, including how to use it on things that aren't lists, see [binary search on the answer](03-algorithm-patterns.md#binary-search-on-the-answer).

## Linked lists, honestly

A linked list node holds a value and a pointer to the next node. Inserting at a known node is constant time with no shifting, and that's the whole of its advantage. Everything else it trades away:

```python
import time
import tracemalloc


class Node:
    __slots__ = ("value", "next")

    def __init__(self, value, next=None):
        self.value, self.next = value, next


def footprint(build):
    tracemalloc.start()
    keep = build()
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return keep, current


n = 1_000_000
values = list(range(n))


def build_linked():
    head = None
    for v in reversed(values):
        head = Node(v, head)
    return head


array, array_bytes = footprint(lambda: list(values))
head, linked_bytes = footprint(build_linked)


def timed(f):
    start = time.perf_counter()
    f()
    return (time.perf_counter() - start) * 1e3


def walk():
    total, node = 0, head
    while node:
        total += node.value
        node = node.next


def loop():
    total = 0
    for v in array:
        total += v


print(f"list:   {array_bytes / n:5.1f} bytes/element extra, walk {timed(loop):6.1f} ms")
print(f"linked: {linked_bytes / n:5.1f} bytes/element extra, walk {timed(walk):6.1f} ms")
print(f"insert at front: list ", end="")
start = time.perf_counter()
array.insert(0, -1)
print(f"{(time.perf_counter() - start) * 1e6:.0f} us, linked ", end="")
start = time.perf_counter()
head = Node(-1, head)
print(f"{(time.perf_counter() - start) * 1e6:.1f} us")
del head  # a long chain frees one node at a time
```

<!-- measured -->

```text
list:     8.0 bytes/element extra, walk   12.9 ms
linked:  48.0 bytes/element extra, walk   17.4 ms
insert at front: list 339 us, linked 3.1 us
```

In this measurement a linked list costs 48 extra bytes per element, against 8 for a list's pointer. Walking it took about 35% longer here, and that gap is flattered by the nodes having been allocated in order. Scatter them and each hop can miss the cache, which [chapter 4](04-numbers-and-memory.md#locality-even-from-python) measures. An insert at the front takes 339 µs for the list against 3 µs for the node. So use one when you hold references to nodes and need to splice at them, as in the LRU below. Otherwise, use a list or a `deque`.

The operations you'll be asked about are worth writing once: reversing in place with three pointers, and finding a cycle with a slow and a fast pointer, where the fast one gains one step per iteration so it must meet the slow one if there's a loop. The [lab](../practice/README.md) has you write a doubly linked one with sentinel nodes, which remove every edge case at the ends. The `del head` at the end of the block isn't decoration: dropping a long chain frees nodes through a cascade of deallocations, a cost you pay all at once.

## Trees and tries

A binary search tree keeps smaller keys on the left and larger on the right, so a lookup follows one path from the root. Its speed depends entirely on that path's length, which isn't guaranteed:

```python
import random


class Node:
    __slots__ = ("key", "left", "right")

    def __init__(self, key):
        self.key, self.left, self.right = key, None, None


def insert(root, key):
    if root is None:
        return Node(key)
    node = root
    while True:
        side = "left" if key < node.key else "right"
        child = getattr(node, side)
        if child is None:
            setattr(node, side, Node(key))
            return root
        node = child


def height(root):
    best, stack = 0, [(root, 1)] if root else []
    while stack:
        node, depth = stack.pop()
        best = max(best, depth)
        stack.extend((c, depth + 1) for c in (node.left, node.right) if c)
    return best


def build(keys):
    root = None
    for k in keys:
        root = insert(root, k)
    return root


n = 2_000
rng = random.Random(1)
print("height, random inserts:", height(build(rng.sample(range(n), n))))
print("height, sorted inserts:", height(build(range(n))))


class Trie:
    def __init__(self):
        self.children, self.end = {}, False

    def add(self, word):
        node = self
        for ch in word:
            node = node.children.setdefault(ch, Trie())
        node.end = True

    def with_prefix(self, prefix):
        node = self
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        out, stack = [], [(node, prefix)]
        while stack:
            node, word = stack.pop()
            if node.end:
                out.append(word)
            stack.extend((child, word + c) for c, child in node.children.items())
        return sorted(out)


tools = Trie()
for name in ["search_docs", "search_web", "send_email", "sql_query", "search_code"]:
    tools.add(name)
print(tools.with_prefix("search_"))
print(tools.with_prefix("s"))
print(tools.with_prefix("x"))
```

```text
height, random inserts: 23
height, sorted inserts: 2000
['search_code', 'search_docs', 'search_web']
['search_code', 'search_docs', 'search_web', 'send_email', 'sql_query']
[]
```

Randomly ordered inserts give height 23 for 2,000 keys. Sorted inserts give height 2,000, which is a linked list with extra steps, and sorted input is exactly what real data tends to be. Balanced variants fix this with rotations. Python's standard library has none, since a sorted list with `bisect` covers small cases and databases cover large ones: on disk, a [SQLite B-tree](../../../data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores.md) is the same idea with very wide nodes, because reading a whole disk page costs about the same as reading one key.

A trie stores strings by shared prefix, one edge per character, so prefix lookup costs the length of the prefix and not the number of strings. It's natural for autocomplete and for routing tools by name, as above. For a small, fixed set, a sorted list and `bisect` on the prefix does the job with less memory. Choose a trie when prefixes are the main query and the set changes.

## Stacks, and the one you already use

A stack is `list.append` and `list.pop`, both constant at the end. Python's own call stack is one too, and when a tree is deep you sometimes need to manage your own. Checking nested structure is the typical use, and so is walking data with no depth limit:

```python
def first_unbalanced(text, pairs={")": "(", "]": "[", "}": "{"}):
    """Index of the first bad bracket, or None. Strings are ignored for brevity."""
    stack = []
    for i, ch in enumerate(text):
        if ch in "([{":
            stack.append((ch, i))
        elif ch in pairs:
            if not stack or stack.pop()[0] != pairs[ch]:
                return i
    return stack[0][1] if stack else None


print(first_unbalanced('{"a": [1, 2]}'))
print(first_unbalanced('{"a": [1, 2}'))
print(first_unbalanced('{"a": [1, 2]'))


def depth(tree):
    return 1 + max((depth(child) for child in tree), default=0)


nested = []
for _ in range(100_000):
    nested = [nested]


def depth_iterative(tree):
    best, stack = 0, [(tree, 1)]
    while stack:
        node, d = stack.pop()
        best = max(best, d)
        stack.extend((child, d + 1) for child in node)
    return best


try:
    depth(nested)
except RecursionError as e:
    print("recursive:", type(e).__name__)
print("explicit stack:", depth_iterative(nested))
```

```text
None
11
0
recursive: RecursionError
explicit stack: 100001
```

Recursion hits a limit on 100,000-level nested data, and that data can come from a user's JSON. The same walk with an explicit stack is limited only by memory. Converting recursion to a loop with a stack is a skill you'll use in [chapter 3](03-algorithm-patterns.md#graphs-are-one-loop-with-a-different-bag).

## Building a structure from two others

Interesting requirements often need two structures at once. A bounded cache needs a lookup by key and an ordering by recency, each in constant time. A dict gives the first and a doubly linked list gives the second, and a dict that maps keys to list nodes joins them. [`OrderedDict`](https://docs.python.org/3/library/collections.html#collections.OrderedDict) has done this for you, with `move_to_end` and `popitem(last=False)`:

```python
from collections import OrderedDict


class EmbeddingCache:
    """At most `capacity` entries; the entry unused for longest goes first."""

    def __init__(self, capacity):
        self.capacity = capacity
        self.entries = OrderedDict()

    def get(self, text):
        if text not in self.entries:
            return None
        self.entries.move_to_end(text)
        return self.entries[text]

    def put(self, text, vector):
        self.entries[text] = vector
        self.entries.move_to_end(text)
        if len(self.entries) > self.capacity:
            self.entries.popitem(last=False)


cache = EmbeddingCache(2)
cache.put("refund policy", [0.1])
cache.put("shipping times", [0.2])
cache.get("refund policy")
cache.put("store hours", [0.3])
print(list(cache.entries))
```

```text
['refund policy', 'store hours']
```

The general approach is to write down the operations and how often each happens, then pick the structure for each and link them. Use [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache) when the thing you're caching is a function call, and when a process-wide cache that never expires is acceptable. Build the linked version yourself in the [lab](../practice/README.md), once, to see what `OrderedDict` takes care of.

| You need | Use | Watch for |
|---|---|---|
| Index by position, append at the end | `list` | `insert`, `pop(0)`, `in` are linear |
| Queue | `collections.deque` | Middle access is linear |
| Lookup or membership | `dict`, `set` | Keys must be hashable; memory; hostile ints |
| Oldest or recently used key | `OrderedDict` | Larger per key than a dict |
| Top k, or next smallest | `heapq` | Not sorted order; a min-heap |
| Search in data that rarely changes | `sorted` + `bisect` | `insort` is linear |
| Prefix queries that change | A trie | Python objects per character |
| Numbers, in bulk | `array`, `numpy` | [Chapter 4](04-numbers-and-memory.md#the-layout-decides-the-constant) |

## Pitfalls

- **A list used as a queue.** Symptom: a worker gets slower as its backlog grows, which then makes the backlog grow.
- **A dict you delete from and expect to shrink.** Symptom: memory stays at the peak after a purge, and iteration over few keys is oddly slow. Rebuild it with `dict(d)`.
- **`next(iter(d))` as a pop-oldest.** Symptom: an LRU that takes far longer the longer it runs. Use `OrderedDict`.
- **Persisting `hash()`.** Symptom: a partition assignment that changes on restart. String hashes vary per process. Use `hashlib`.
- **Mutable or unhashable keys, or an inconsistent `__hash__`.** Symptom: a `TypeError`, or an object you put in a set that you can no longer find, because its hash changed.
- **A `__hash__` that returns a constant.** Symptom: a dict that's quadratic with no error. Test with a counter, as in the collision block.
- **`sys.getsizeof` on a container.** Symptom: "only 8 MB" for a million floats, when the float objects hold another 24 MB. It counts the array, not the contents. Use `tracemalloc`.
- **Assuming you need a balanced tree.** Symptom: a custom structure where `sorted` once and `bisect` would have done.

## Try it

1. Add `sys.getsizeof` output to a `set` being grown, and compare bytes per key with the dict table. Is a set smaller than a dict with `None` values?
2. Modify the probing block to count probes for string keys with the real `hash()` in a table of 32,768 slots. What's the mean, and how does it compare with `i << 16`?
3. Implement `CompactDict` in [the lab](../practice/README.md), including deletion. Which test fails if deletion marks the slot `FREE`?
4. Write `dedupe_keep_last(items, key)` that keeps the last record for each key, in order of those last appearances, in linear time.

<details>
<summary>Answers</summary>

1. It depends on the count, because they resize at different points. On this build: 10 keys 728 bytes for the set against 352 for the dict, 1,000 keys 32,984 against 36,952, 10,000 keys 524,504 against 294,992. Don't assume the set is the cheap one.
2. With 6,000 string keys in 32,768 slots, the load reaches about 18%, and I measured a mean of 1.10 probes, against 3.91 for `i << 16`.
3. `test_delete_keeps_later_keys_reachable`: all keys collide, so `c` and `d` sit further along `b`'s probe path, and a `FREE` slot ends the search early.
4. `latest = {}`, then for each item do `latest.pop(key(item), None); latest[key(item)] = item`, and return `list(latest.values())`. Removing before re-inserting moves the key to the end. A plain assignment wouldn't, since overwriting keeps the original position.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| How does a Python list grow? | It reallocates to about 1.125 × the new size, rounded to a multiple of 4. Amortised constant-time appends follow from the geometric series. |
| Why is `pop(0)` slow? | Everything after it shifts down one slot. Use a `deque`. |
| How is a Python dict laid out? | A sparse table of small integers pointing into a dense, insertion-ordered array of hash, key and value entries. Load is at most 2/3. |
| How does it resolve collisions? | Open addressing with `i = 5i + perturb + 1`, where `perturb` shifts in the hash's high bits. |
| Why can't a deleted slot just be emptied? | A lookup stops at the first empty slot, so later keys on that path would vanish. It's marked `DUMMY`. |
| Does a dict shrink when you delete? | Not on deletion. It resizes on insertion, when usable space runs out, based on the number of live keys. |
| What's hash flooding? | Crafted colliding keys force quadratic insertion. Strings are protected by per-process keyed SipHash; ints aren't randomised. |
| Why does a key-sharing dict help? | Instances of a class share a keys table and store only values. |
| How does Python's sort work? | A stable adaptive merge sort: it finds natural runs and merges them by the powersort strategy. Sorted input costs `n - 1` comparisons. |
| Top k of a stream? | A min-heap of size k: `O(n log k)` time and `O(k)` memory. |
| When is a linked list worth it? | When you hold node references and splice at them, as in an LRU. Otherwise the memory and pointer-chasing cost more. |
| How do you build an LRU cache? | A dict from key to node in a doubly linked list. Both operations are constant time, and `OrderedDict` packages that. |

## See also

- [Python 03 · 08 Objects, inheritance and the MRO](../../python/03-language-for-engineers/notes/08-objects-inheritance-and-mro.md): how attribute lookup uses the `dict` described here.
- [Python 03 · 09 Memory and the runtime](../../python/03-language-for-engineers/notes/09-memory-and-the-runtime.md): `__slots__` and object size in CPython.

## Next

[3 — Algorithm patterns](03-algorithm-patterns.md): the handful of ideas behind most algorithms you'll write, on these structures.
