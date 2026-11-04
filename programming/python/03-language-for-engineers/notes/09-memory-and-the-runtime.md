---
origin: synthesis
sources:
  - "Python 3.14 docs, gc module — https://docs.python.org/3.14/library/gc.html"
  - "CPython 3.14 InternalDocs, Garbage collector design — https://github.com/python/cpython/blob/3.14/InternalDocs/garbage_collector.md"
  - "Python 3.14 docs, What's New in Python 3.14 — https://docs.python.org/3.14/whatsnew/3.14.html"
  - "Python 3.14 docs, Python support for free threading — https://docs.python.org/3.14/howto/free-threading-python.html"
  - "PEP 779, Criteria for supported status for free-threaded Python — https://peps.python.org/pep-0779/"
  - "Python 3.14 docs, tracemalloc, dis, sys, weakref, Memory Management (C API), Programming FAQ — https://docs.python.org/3.14/library/tracemalloc.html"
  - "Python 3.14 docs, Data model: __slots__ — https://docs.python.org/3.14/reference/datamodel.html#slots"
concepts: [python-reference-counting, python-garbage-collector, python-memory-leaks, python-slots, python-bytecode, python-tracemalloc, python-free-threading]
confidence: high
cleaned: 2026-11-02
---
# 9 — Memory and the runtime

> A retrieval service that holds its embeddings as Python lists will run out of memory long before it runs out of data, and a worker that "leaks" usually hasn't leaked in the C sense at all: something is still holding a reference. To diagnose either, you need a working model of what a Python object costs, what frees it, and how to see what's holding on. This chapter builds that model from measurements. Everything ran on CPython 3.14.7 on macOS arm64, using the default build unless it says free-threaded. This area changes between releases, and the garbage collector changed twice within 3.14 alone, so treat every number and internal detail here as true of that version and recheck on yours.

---

## What an object costs

Every CPython object carries a header, and containers add pointers on top. `sys.getsizeof` reports only the object itself, so for anything nested it undercounts. `tracemalloc` counts what was really allocated.

```python
import sys, tracemalloc
from dataclasses import dataclass
from typing import NamedTuple

class Plain:
    def __init__(self, doc_id, score):
        self.doc_id, self.score = doc_id, score

class Slotted:
    __slots__ = ("doc_id", "score")
    def __init__(self, doc_id, score):
        self.doc_id, self.score = doc_id, score

class Tup(NamedTuple):
    doc_id: int
    score: float

@dataclass
class DC:
    doc_id: int
    score: float

@dataclass(slots=True)
class DCS:
    doc_id: int
    score: float

makers = {
    "dict": lambda i: {"doc_id": i, "score": i * 0.5},
    "tuple": lambda i: (i, i * 0.5),
    "NamedTuple": lambda i: Tup(i, i * 0.5),
    "plain class": lambda i: Plain(i, i * 0.5),
    "plain, __dict__ read": lambda i: (o := Plain(i, i * 0.5), o.__dict__)[0],
    "__slots__ class": lambda i: Slotted(i, i * 0.5),
    "dataclass": lambda i: DC(i, i * 0.5),
    "dataclass(slots)": lambda i: DCS(i, i * 0.5),
}
N = 200_000
for name, make in makers.items():
    tracemalloc.start()
    keep = [make(i + 10_000) for i in range(N)]
    used, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{name:21} {used / N:6.1f} bytes each, getsizeof says {sys.getsizeof(keep[0])}")
```

```text
dict                   248.1 bytes each, getsizeof says 184
tuple                  128.1 bytes each, getsizeof says 64
NamedTuple             136.1 bytes each, getsizeof says 64
plain class            152.1 bytes each, getsizeof says 48
plain, __dict__ read   216.1 bytes each, getsizeof says 48
__slots__ class        112.1 bytes each, getsizeof says 48
dataclass              152.1 bytes each, getsizeof says 48
dataclass(slots)       112.1 bytes each, getsizeof says 48
```

The figure in the first column includes the list slot and the int and float inside each record. Two findings go against folklore. `sys.getsizeof` reports 48 bytes for both a plain and a slotted instance even though they differ by 40 in practice, so it can't be used to compare them. And `__slots__` saves about a quarter here, not the factor of several often quoted. The `plain, __dict__ read` row shows why: this interpreter builds an instance's real `__dict__` only when something asks for it, and the cost jumps when you do. So code that reads `vars(obj)` on every record gives up what the plain class gained. A plain dict record stays the heaviest common choice. The same script on the free-threaded build reports 32 bytes more per record in every row.

For numeric data, the cost of boxing dominates everything above. One 1536-dimension embedding:

```python
import array, tracemalloc

DIM = 1536
def measure(make):
    tracemalloc.start()
    keep = make()
    used, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return used

print("list[float]  ", measure(lambda: [i * 0.5 for i in range(DIM)]))
print("array('d')   ", measure(lambda: array.array("d", (i * 0.5 for i in range(DIM)))))
print("array('f')   ", measure(lambda: array.array("f", (i * 0.5 for i in range(DIM)))))
print("per million, list[float]: {:.0f} GiB".format(measure(lambda: [i * 0.5 for i in range(DIM)]) * 1e6 / 2**30))
```

```text
list[float]   49416
array('d')    13176
array('f')    6628
per million, list[float]: 44 GiB
```

The last line measures again, and repeat calls come in about 2 KB lower than the first (47,136 bytes on this run), which is why it says 44 GiB and not the 46 you'd get from the first line. A `list[float]` costs 8 bytes for the pointer plus 24 for each float. Use `array` or, in real systems, NumPy, for anything that is a block of numbers. [Vector databases](../../../../generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann.md) depend on this: index memory only adds up with packed arrays.

## Reference counting frees most things immediately

Each object has a count of the references to it. When that count hits zero, CPython frees it on the spot. That determinism is why closing a file by dropping it often appears to work, but the [data model](https://docs.python.org/3.14/reference/datamodel.html) calls this an implementation detail and warns against relying on it. Use [context managers](04-errors-and-context-managers.md) for anything that must be released at a known time.

```python
import sys, weakref

class Index:
    def __init__(self, name):
        self.name = name

def demo():
    idx = Index("products")
    weakref.finalize(idx, print, "  freed: products")
    print("refcount, one local:", sys.getrefcount(idx))
    alias = idx
    print("refcount, plus alias:", sys.getrefcount(idx))
    del alias
    print("dropping the last reference")
    del idx
    print("after del")

demo()
print("None:", sys.getrefcount(None), "immortal:", sys._is_immortal(None))
```

```text
refcount, one local: 1
refcount, plus alias: 2
dropping the last reference
  freed: products
after del
None: 3221225472 immortal: True
```

`weakref.finalize` registers a callback for when an object is collected, without keeping the object alive. It is a safer tool than `__del__`, and the demo uses it to make freeing visible.

Read `sys.getrefcount` with care. The [docs](https://docs.python.org/3.14/library/sys.html#sys.getrefcount) say the result is generally one higher than you'd expect, because of the temporary argument reference, and then warn against relying on any value other than 0 or 1. On 3.14 the local variable case above shows no extra reference, because the interpreter can borrow a reference to a local instead of counting it. Older tutorials print a different number. `None`'s enormous count is a marker: it's **immortal**, meaning its count never changes. [PEP 683](https://peps.python.org/pep-0683/) introduced this so that objects that look immutable really are, with no refcount writes.

## The cycle collector

Reference counts can't free a cycle: each object keeps the other above zero. A separate collector handles them. Only container objects can form cycles, so only those are tracked.

```python
import gc, weakref

class Node:
    def __init__(self, name):
        self.name, self.peer = name, None

gc.collect()                                  # clear start-up garbage so the count below is ours
gc.disable()                                  # so the collection below is the one that does it
a, b = Node("a"), Node("b")
a.peer, b.peer = b, a                         # a cycle
weakref.finalize(a, print, "  freed a")
weakref.finalize(b, print, "  freed b")
del a, b
print("dropped both names; nothing freed yet")
print("gc.collect() found", gc.collect(), "unreachable objects")
gc.enable()

print("tracked? int:", gc.is_tracked(1), " str:", gc.is_tracked("x"),
      " list:", gc.is_tracked([]), " dict of atoms:", gc.is_tracked({"a": 1}))
print("thresholds:", gc.get_threshold(), "generations:", len(gc.get_count()))
```

```text
dropped both names; nothing freed yet
  freed a
  freed b
gc.collect() found 4 unreachable objects
tracked? int: False  str: False  list: True  dict of atoms: True
thresholds: (2000, 10, 10) generations: 3
```

### Which collector you have depends on the patch version

This is an easy place to pick up wrong facts, so be exact. **CPython 3.14.0 to 3.14.4 shipped an incremental collector, and 3.14.5 reverted it to the generational collector of 3.13.** [What's New in 3.14](https://docs.python.org/3.14/whatsnew/3.14.html) gives the reason as reports of significant memory pressure in production, and the [gc docs](https://docs.python.org/3.14/library/gc.html) record the same change. A blog post from 2025 describing 3.14's incremental collector was right when written and is wrong for 3.14.7. The behaviour described here is the reverted, generational one. The free-threaded build has its own collector.

| | Default build, 3.14.5+ | Free-threaded build, 3.14 |
|---|---|---|
| Design | Three generations | Not generational; scans the whole heap |
| Pauses | Stops the program (it holds the GIL) | Stops the world, twice per collection |
| Trigger | Net container allocations over threshold0 (2000 here) | Same threshold, plus a check that process memory has grown 10%, or that net allocations exceed 40 times the threshold |

The details come from CPython's [internal GC docs](https://github.com/python/cpython/blob/3.14/InternalDocs/garbage_collector.md). In the default build, a full collection also requires that the objects awaiting their first full collection exceed 25% of the long-lived total, which keeps full collections from growing quadratically as the heap does.

### What it costs

A full collection touches every tracked object, so its pause grows with the live heap. In a service holding a large in-memory structure, that pause lands on whichever request was unlucky.

```python
import gc, time

def records(n):
    return [{"id": i, "tags": ["a"]} for i in range(n)]

pauses = []
start = [0.0]
def timer(phase, info):
    if phase == "start":
        start[0] = time.perf_counter()
    else:
        pauses.append(time.perf_counter() - start[0])
gc.callbacks.append(timer)

for n in (100_000, 1_000_000, 4_000_000):
    pauses.clear()
    data = records(n)
    during = len(pauses), sum(pauses), max(pauses)
    t0 = time.perf_counter()
    gc.collect()
    full = time.perf_counter() - t0
    print(f"{n:>9,} records: {during[0]:>3} collections while building, "
          f"{during[1]*1e3:7.0f} ms total, worst {during[2]*1e3:6.0f} ms; full collect {full*1e3:6.0f} ms")
    if n == 4_000_000:
        gc.freeze()                    # move everything to the permanent generation
        t0 = time.perf_counter()
        gc.collect()
        print(f"after gc.freeze(): full collect {(time.perf_counter() - t0)*1e3:.1f} ms")
        gc.unfreeze()
    del data
```

```text
  100,000 records: 100 collections while building,       6 ms total, worst      1 ms; full collect      5 ms
1,000,000 records: 998 collections while building,     237 ms total, worst     55 ms; full collect     64 ms
4,000,000 records: 3995 collections while building,    1179 ms total, worst    217 ms; full collect    265 ms
after gc.freeze(): full collect 0.0 ms
```

Each record here is two tracked containers, so the last row has 8 million. On this machine a full collection grew from about 5 ms to about 260 ms, and building the 4 million records stalled for about 200 ms at worst, and over a second in total across some 4,000 collections. Most of those are cheap young collections. A few aren't, and an interactive request that lands on one of them feels it. These times vary between runs, but the growth with live heap size won't go away.

Two responses are common for a big, long-lived, read-mostly structure. First, avoid creating millions of tracked containers: one `array` is a single tracked object however long it gets, and the [collector untracks tuples](https://github.com/python/cpython/blob/3.14/InternalDocs/garbage_collector.md) whose contents are all untracked. Don't assume the same for dicts: `{"a": 1}` shows as tracked in the output above. Second, `gc.freeze()` moves everything currently tracked to a permanent generation that collections ignore, as above. The [gc docs](https://docs.python.org/3.14/library/gc.html#gc.freeze) describe a recipe for pre-fork servers: `gc.disable()` early in the parent, `gc.freeze()` just before `fork()`, then `gc.enable()` in the children, so that the collector's writes to object headers don't defeat copy-on-write. `gc.disable()` on its own is a hazard, since any cycles you create then stay around forever.

## Leaks: reachable but unwanted

A Python "leak" is almost always an object that something can still reach, so no collector will touch it. The usual suspects in an LLM service:

| Holder | How it grows | Fix |
|---|---|---|
| A module-level dict used as a cache | One entry per unique prompt, forever | Bound it: `lru_cache(maxsize=...)`, or a TTL cache |
| `lru_cache` on a method | The cache holds `self`, so instances live on | Below |
| A registered callback or listener | The registry keeps the bound method, and thus its object | `weakref.WeakMethod`, or an explicit `unsubscribe` |
| Conversation history on a long-lived session object | One list per user, never trimmed | Truncate, summarise or persist; set an eviction policy |
| A stored exception | `err.__traceback__` holds frames, and frames hold their locals, such as a whole batch | Store `str(err)` or a formatted traceback |
| Accumulating metrics or spans | Every label combination stays in memory | Limit cardinality; flush |

The [Programming FAQ](https://docs.python.org/3.14/faq/programming.html#how-do-i-cache-method-calls) lays out the method-cache trade-off, and it's worth seeing run:

```python
import functools, gc, weakref

class WithLru:
    @functools.lru_cache(maxsize=128)
    def embed(self, text):
        return [0.0] * 1536

class WithCachedProperty:
    @functools.cached_property
    def corpus(self):
        return [0.0] * 1536

def lifetime(obj, call):
    ref = weakref.ref(obj)
    call(obj)
    del obj
    gc.collect()
    return "still alive" if ref() is not None else "freed"

print("lru_cache on a method:", lifetime(WithLru(), lambda o: o.embed("hello")))
print("cached_property:      ", lifetime(WithCachedProperty(), lambda o: o.corpus))
print(WithLru.embed.cache_info())
```

```text
lru_cache on a method: still alive
cached_property:       freed
CacheInfo(hits=0, misses=1, maxsize=128, currsize=1)
```

`lru_cache` stores its keys at class level, and `self` is part of the key. The object survives until it ages out, or forever if the cache never fills. `cached_property` stores on the instance, using the [non-data descriptor trick](08-objects-inheritance-and-mro.md#descriptors-how-attribute-access-really-works), so its result dies with the instance.

### Finding it with `tracemalloc`

`tracemalloc` records where each Python allocation came from. Take a snapshot, run the suspect code, take another, and diff them:

```python
import tracemalloc

class SessionStore:
    def __init__(self):
        self.history = {}                         # the leak: nothing ever removes a session

    def handle(self, session_id, prompt):
        self.history.setdefault(session_id, []).append(prompt * 40)

store = SessionStore()
def traffic(start, n):
    for i in range(start, start + n):
        store.handle(f"s-{i}", f"question number {i} ")

tracemalloc.start()
traffic(0, 1_000)
before = tracemalloc.take_snapshot()
traffic(1_000, 50_000)
after = tracemalloc.take_snapshot()
tracemalloc.stop()

for stat in after.compare_to(before, "lineno")[:2]:
    frame = stat.traceback[0]
    print(f"line {frame.lineno:>2}: +{stat.size_diff / 1024:9.0f} KiB, +{stat.count_diff:>7} blocks")
```

```text
line  8: +    50768 KiB, + 150000 blocks
line 13: +     2335 KiB, +  50000 blocks
```

Line 8 is the `setdefault(...).append(...)`, and line 13 builds the session keys, each with the size of the leak attached. In a service, take the two snapshots some time apart, after warm-up, because caches filling up look the same as leaks in the first minutes. Compare by `"lineno"` first, then call `tracemalloc.start(25)` to get the [full traceback](https://docs.python.org/3.14/library/tracemalloc.html) if one line is reached from many places.

It has limits. It only sees allocations made through Python's allocator, so buffers allocated privately by a C extension are invisible. It also slows the program down: an allocation-heavy loop here ran about 4 times slower under `tracemalloc.start()` and about 9 times slower under `start(25)`, so enable it on one replica rather than everywhere. For a memory dump and profiling tools in production, see [debugging and profiling](../../../software-design/notes/06-debugging-and-profiling.md).

### Freed memory doesn't always go back to the OS

Objects of 512 bytes or fewer come from pymalloc, which [manages 1 MiB arenas on 64-bit platforms](https://docs.python.org/3.14/c-api/memory.html). An arena can go back to the operating system only when nothing in it is live, so a few survivors can pin a lot of memory:

```python
import gc, os, subprocess

def rss_mib():
    out = subprocess.run(["ps", "-o", "rss=", "-p", str(os.getpid())], capture_output=True, text=True)
    return int(out.stdout) / 1024

print(f"start                          {rss_mib():7.0f} MiB")
data = [{"id": i} for i in range(3_000_000)]
print(f"3M small dicts                 {rss_mib():7.0f} MiB")
survivors = data[::2000]                  # keep one record in every 2000
del data
gc.collect()
print(f"kept {len(survivors):,} of them              {rss_mib():7.0f} MiB")
del survivors
gc.collect()
print(f"dropped the rest               {rss_mib():7.0f} MiB")
```

```text
start                               16 MiB
3M small dicts                     686 MiB
kept 1,500 of them                  686 MiB
dropped the rest                    44 MiB
```

Dropping all but 1,500 of 3 million records, 0.05% of them, gave back nothing visible, because each one was enough to keep its arena. Dropping those last few gave back about 640 MiB. The free-threaded build uses mimalloc instead, which the [howto](https://docs.python.org/3.14/howto/free-threading-python.html) says also defers returning memory to the OS. This is why a process's RSS can stay high after a spike even though `tracemalloc` shows that Python memory has gone down, and why batch workers often use a process per job, or a `maxtasksperchild`-style restart, instead of fighting the allocator. Don't call RSS growth a leak until the Python-level number agrees.

## `__slots__`: trading flexibility for size

`__slots__` replaces per-instance dictionary storage with fixed positions in the object. Each name becomes a member descriptor on the class, which is the [data-descriptor rule from chapter 8](08-objects-inheritance-and-mro.md#descriptors-how-attribute-access-really-works) at work. The savings measured at the top are real but modest, and the [data model notes](https://docs.python.org/3.14/reference/datamodel.html#notes-on-using-slots) list what you pay:

```python
import functools, weakref

class Chunk:
    __slots__ = ("doc_id", "text")
    def __init__(self, doc_id, text):
        self.doc_id, self.text = doc_id, text

    @functools.cached_property
    def tokens(self):
        return self.text.split()

chunk = Chunk("d1", "refund policy")
print(type(Chunk.__dict__["text"]).__name__)

for label, action in [
    ("new attribute", lambda: setattr(chunk, "score", 0.9)),
    ("weak reference", lambda: weakref.ref(chunk)),
    ("cached_property", lambda: chunk.tokens),
]:
    try:
        action()
        print(f"{label}: ok")
    except Exception as err:
        print(f"{label}: {type(err).__name__}: {err}")

class Base:                                 # no __slots__ here...
    pass

class Leaky(Base):
    __slots__ = ("x",)                      # ...so instances get a __dict__ anyway

print("has __dict__:", hasattr(Leaky(), "__dict__"))

class A: __slots__ = ("a",)
class B: __slots__ = ("b",)
try:
    class AB(A, B): ...
except TypeError as err:
    print("two slotted bases:", err)
```

```text
member_descriptor
new attribute: AttributeError: 'Chunk' object has no attribute 'score' and no __dict__ for setting new attributes
weak reference: TypeError: cannot create weak reference to 'Chunk' object
cached_property: TypeError: No '__dict__' attribute on 'Chunk' instance to cache 'tokens' property.
has __dict__: True
two slotted bases: multiple bases have instance lay-out conflict
```

Use `__slots__` (most easily `@dataclass(slots=True)`) when you hold many instances of one small class, have measured a benefit, and the class is not designed to be extended. Otherwise the plain class is the better default.

## Bytecode and what the interpreter actually runs

CPython compiles a function to bytecode, a list of instructions for a stack machine. `dis` shows it. This is the tool for answering "is this one operation?":

```python
import dis

class Counter:
    def __init__(self):
        self.total = 0

    def add(self, n):
        self.total += n

dis.dis(Counter.add)
```

```text
  7           RESUME                   0

  8           LOAD_FAST_BORROW         0 (self)
              COPY                     1
              LOAD_ATTR                0 (total)
              LOAD_FAST_BORROW         1 (n)
              BINARY_OP               13 (+=)
              SWAP                     2
              STORE_ATTR               0 (total)
              LOAD_CONST               0 (None)
              RETURN_VALUE
```

`self.total += n` is a load, an add and a separate store, so a thread switch can land between them. That's the race behind [a lost update](07-concurrency.md), now visible as instructions. Bytecode isn't a stable interface: the [`dis` docs](https://docs.python.org/3.14/library/dis.html) call it an implementation detail with no guarantees between versions, so read it to learn, and don't write tools that depend on specific opcodes.

Since 3.11 the interpreter also rewrites its own instructions as it runs, replacing general ones with versions specialised for the types it sees. `adaptive=True` shows that:

```python
import dis

def score(values):
    total = 0.0
    for v in values:
        total += v * 2.0
    return total

for _ in range(1000):
    score([1.0, 2.0, 3.0])

general = {i.opname for i in dis.get_instructions(score)}
adaptive = {i.opname for i in dis.get_instructions(score, adaptive=True)}
print("after warm-up, specialised:", sorted(adaptive - general))
print("replaced:", sorted(general - adaptive))
```

```text
after warm-up, specialised: ['BINARY_OP_ADD_FLOAT', 'BINARY_OP_MULTIPLY_FLOAT', 'FOR_ITER_LIST', 'JUMP_BACKWARD_NO_JIT', 'LOAD_CONST_MORTAL', 'RESUME_CHECK']
replaced: ['BINARY_OP', 'FOR_ITER', 'JUMP_BACKWARD', 'LOAD_CONST', 'RESUME']
```

This is why a function that keeps seeing one type runs faster than one that sees a mix, and why micro-benchmarks need a warm-up. It's also why a profile can shift when input types change.

## The `sys` and `gc` toolbox

| Call | What it gives you |
|---|---|
| `sys.getsizeof(x)` | Shallow size in bytes |
| `sys.getrefcount(x)` | A debugging hint; see the warning above |
| `sys._is_gil_enabled()` | Whether the GIL is on right now. Underscore: CPython-specific |
| `sys._is_immortal(x)` | Whether the object's refcount is fixed. Underscore: CPython-specific |
| `sys.getswitchinterval()` | How often the GIL is offered to another thread, 0.005 s by default |
| `sys.getrecursionlimit()` | 1000 by default |
| `sys._current_frames()` | Every thread's current stack, used for [a hand-made sampler](../../../software-design/notes/06-debugging-and-profiling.md) |
| `gc.get_threshold()`, `gc.get_stats()`, `gc.callbacks` | Collector settings, counters and hooks |
| `gc.get_referrers(x)` | What holds `x`, the first thing to try after `tracemalloc`. Debugging only, as the docs warn |
| `gc.garbage` | Objects the collector found unreachable but couldn't free, or everything with `gc.set_debug(gc.DEBUG_SAVEALL)` |

## Free-threading: what's true in 3.14

Treat this as a moving target. These are the facts as of 3.14, from the [free-threading howto](https://docs.python.org/3.14/howto/free-threading-python.html) and [PEP 779](https://peps.python.org/pep-0779/):

- It's **officially supported but optional**: a separate build, usually run as `python3.14t`, and not the default. PEP 779 calls this phase II; it doesn't decide that the default will change.
- A free-threaded build can still run with the GIL on: importing a C extension that hasn't declared support re-enables it, as does `PYTHON_GIL=1` or `-X gil=1`. Check at runtime with `sys._is_gil_enabled()`, not by the name of the binary.
- The howto reports single-threaded overhead on pyperformance from about 1% on macOS aarch64 to 8% on x86-64 Linux.
- Reference counting changes: biased and deferred counting can delay when an object is actually freed, compared with the immediate behaviour shown above, and the howto notes `gc.collect()` merges per-thread counts.
- The built-in types use internal locks, but the howto advises against relying on them for your own code's correctness: use `threading.Lock`. Sharing one iterator across threads isn't safe.

Here is what the build changes on this machine, CPU-bound work in 1 and 4 threads:

```python
import sys, threading, time

def work(n=10_000_000):
    total = 0
    for i in range(n):
        total += i * i
    return total

def run(threads):
    pool = [threading.Thread(target=work) for _ in range(threads)]
    start = time.perf_counter()
    for t in pool: t.start()
    for t in pool: t.join()
    return time.perf_counter() - start

one, four = run(1), run(4)
print(f"GIL enabled: {sys._is_gil_enabled()}")
print(f"1 thread: {one:.2f}s   4 threads, same work each: {four:.2f}s   speedup {4 * one / four:.1f}x")
print(f"None: {sys.getsizeof(None)} bytes, int: {sys.getsizeof(1000)}, float: {sys.getsizeof(1.5)}")
```

```text
GIL enabled: True
1 thread: 0.28s   4 threads, same work each: 1.02s   speedup 1.1x
None: 16 bytes, int: 28, float: 24
```

The same script on `python3.14t`, built by the same release:

```text
GIL enabled: False
1 thread: 0.23s   4 threads, same work each: 0.36s   speedup 2.5x
None: 32 bytes, int: 44, float: 40
```

This one short run shows the shape, not a benchmark: CPU-bound threads scale past 1x only with the GIL off, here to about 2.5x on 4 threads, and each small object carries a bigger header (`None` is 32 bytes against 16). Your overhead and scaling depend on the workload and on reference-count contention, so measure your own code. [Concurrency](07-concurrency.md) still gives the right defaults: threads for I/O, processes for CPU on the default build. Free-threading adds a third option for CPU work with shared memory, if your dependencies support it, and if you've tested with the GIL really off. It does not make your code thread-safe.

## Pitfalls

- **Trusting `sys.getsizeof` for a nested structure.** It's shallow. Symptom: an estimate low by an order of magnitude, followed by an out-of-memory kill.
- **Calling RSS growth a leak.** Fragmentation and caches look the same from outside. Compare `tracemalloc` over time first.
- **Taking a snapshot during warm-up.** Filling caches look like leaks. Wait until the service is steady.
- **`lru_cache` on a method of a short-lived object.** Each instance stays alive until it's evicted. See the [FAQ](https://docs.python.org/3.14/faq/programming.html#how-do-i-cache-method-calls).
- **Keeping exceptions in a list.** Each one holds a traceback, and frames, and every local in them, such as a batch of documents. Symptom: memory tracks error count.
- **Relying on `__del__` to release resources.** It runs at a time you don't control, not at all in some shutdown paths, and later still on a free-threaded build. Use `with`.
- **`gc.disable()` in a long-running process that creates cycles.** Memory grows with no cap. Pair it with `gc.freeze()` and re-enable it.
- **Adding `__slots__` from habit.** You lose `cached_property`, weak references, and flexibility for a saving of around 25% on this interpreter. And a base class without `__slots__` removes most of the benefit.
- **Quoting GC facts without a patch version.** 3.14.0 and 3.14.7 differ. Check `sys.version_info` and the What's New page for your release.
- **Assuming the `t` binary means no GIL.** One extension without declared support turns it back on. Check `sys._is_gil_enabled()`.

## Try it

1. Create a parent `Conversation` and child `Message` objects where each message has a `.conversation` back-reference. Show with `weakref.finalize` that dropping the conversation doesn't free it until the collector runs. Then make the back-reference a `weakref.ref` and show that freeing is immediate.
2. Your job holds 500,000 chunk records, `(doc_id, text, score)`, where the text is about 2 KB. A colleague proposes `__slots__` to save memory. Estimate the saving using the table at the top of this chapter, as a percentage of the total, before you measure.
3. Use `dis` to find out whether `items.append(x)` and `counter[key] += 1` are one instruction each. What does that tell you, and not tell you, about thread safety?
4. A worker's RSS climbs for an hour and then flattens. `tracemalloc` shows no growth after the first ten minutes. Give two explanations, and what you'd check for each.

<details>
<summary>Answers</summary>

1. ```python
   import gc, weakref

   class Conversation:
       def __init__(self):
           self.messages = []

   class Message:
       def __init__(self, conversation, weak):
           self.conversation = weakref.ref(conversation) if weak else conversation

   for weak in (False, True):
       gc.disable()
       conv = Conversation()
       conv.messages.append(Message(conv, weak))
       weakref.finalize(conv, print, f"  freed, weak={weak}")
       del conv
       print(f"after del, weak={weak}")
       gc.collect()
       print("after collect")
       gc.enable()
   ```
   With `weak=False`, "freed" prints after the collect. With `weak=True`, it prints during the `del`.
2. About 40 bytes per record times 500,000 is 20 MB, against about 1 GB of text. So around 2%, not worth it. Size is in the strings.
3. `append` is a load, a call and more, and `counter[key] += 1` is a load, a binary op and a store, so neither is one instruction. That still doesn't settle thread safety in either direction: bytecode count is not the guarantee. A single call into C may hold the GIL throughout on the default build, and that isn't a promise under free-threading. Use a lock, or a queue, when you need the guarantee.
4. Fragmentation or allocator retention: survivors pin arenas. Check by comparing `tracemalloc` current size with RSS, and see whether a process restart clears it. Native allocation outside Python's view, for instance in a tokenizer or model library's buffers. Check by looking at that library's own stats, or at a native heap profiler. A plateau also suggests a cache reaching its bound, which is not a leak at all.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| How does CPython manage memory? | Reference counting frees most objects immediately. A cycle collector handles reference cycles. Small objects come from the pymalloc allocator. |
| Why does Python need a garbage collector if it has refcounts? | A reference cycle keeps all counts above zero even when nothing else can reach it. |
| What's in the generational GC? | On the default build at 3.14.5+: three generations, a young threshold of 2000 net container allocations, and a 25% rule for full collections. The free-threaded build's collector is non-generational. |
| What's a memory leak in Python? | Objects still reachable from a live root that you no longer want: an unbounded cache, a listener, a stored exception. |
| How would you find one? | Compare two `tracemalloc` snapshots taken after warm-up, by line, then with a longer traceback. Use `gc.get_referrers` to see what's holding on. Check RSS against the Python-level number. |
| Why might RSS not fall after freeing? | Allocator arenas return to the OS only when empty, so a few survivors can pin them. |
| What does `__slots__` do and cost? | Fixed slots instead of a per-instance dict. Saves memory, about 25% in the measurement here; loses dynamic attributes, weak references unless declared, and `cached_property`; complicates multiple inheritance. |
| `lru_cache` vs `cached_property` on a method? | `lru_cache` is class-level and bounded but keeps instances alive. `cached_property` is per-instance and has no reference problem, but takes no arguments and can't be bounded. |
| Is `x += 1` atomic? | No. `dis` shows a separate load, operation and store. |
| What is adaptive specialisation? | Since 3.11 the interpreter replaces general instructions with type-specialised ones as it observes running code. |
| Does Python 3.14 still have a GIL? | The default build does. The free-threaded build is officially supported but optional, and can re-enable the GIL. |
| Does removing the GIL make code thread-safe? | No. Compound operations can still interleave; use locks. |

## Next

[Software design: readable code and smells](../../../software-design/notes/01-readable-code-and-smells.md): moving from how the language works to how to arrange code in it.
