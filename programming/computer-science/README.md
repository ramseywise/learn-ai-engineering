# Computer science foundations

> The university-level ideas behind the Python you already write, and how to reason about making it faster: cost models, data structures, algorithm patterns, numbers and memory, processes and threads, and networks. Math is taught where it's used, and claims about speed are measured in the note that makes them.
> Study deck: [computer-science.pptx](slides/computer-science.pptx), which librarian turns into flashcards (source: [deck.yaml](slides/deck.yaml)).
> Jump to: [Reading order](#reading-order) · [Builds on and feeds into](#builds-on-and-feeds-into) · [Rules of thumb](#rules-of-thumb) · [Layout](#layout) · [Setup](#setup) · [Primary texts](#primary-texts)

---

## What this is

Python hides the machine well enough that you can work for years without a model of it, until a job takes all night, a `dict` doubles your memory, a total comes out wrong by a cent, or a service stalls with an idle CPU. This track gives you that model in the order you'd need it: how to count work, what the built-in structures really do, the handful of patterns most algorithms come from, what a number and a memory access cost, what the OS does while you wait, and where a network request's time goes.

It sits beside the [Python track](../python/README.md), which teaches the language, and comes before [software design](../software-design/README.md) and the systems in the data and AI subjects, which assume this vocabulary. It inherits a weakness from its method: measured numbers come from one machine (an Apple M4 Pro, on CPython 3.14.7), so the ratios travel better than the absolute values, and microbenchmarks can flatter or hide effects you'd see in a real program. It's also not a substitute for a full algorithms course. Proofs appear only where they change how you'd reason, and [references.md](references.md) lists the books it didn't read.

The mental model is one question asked at every layer: what's being counted, and what does one of them cost? Big-O counts the operations, the data structure chapter says what an operation really does, the memory chapter prices it in cache misses, and the systems chapters show that the largest cost is often waiting, which doesn't show up in Big-O at all.

## Reading order

The notes follow the [full chapter standard](../../.claude/skills/pillar/references/pillar-layout.md), not the shorter format of the Python modules.

**Reasoning about code**

| # | Note | You can… |
|---|---|---|
| 01 | [Cost models and Big-O](notes/01-cost-models-and-big-o.md) | Count work with sums and recurrences, state Big-O properly, spot hidden costs, budget a request, and optimise in an order that works |
| 02 | [Data structures](notes/02-data-structures.md) | Explain how CPython's `list` and `dict` work, and choose between arrays, hash tables, heaps, trees and tries by what they cost |
| 03 | [Algorithm patterns](notes/03-algorithm-patterns.md) | Recognise two pointers, binary search, backtracking, dynamic programming, greedy and graph search, and argue that they're correct |

**The machine underneath**

| # | Note | You can… |
|---|---|---|
| 04 | [Numbers and memory](notes/04-numbers-and-memory.md) | Predict float error, sum accurately, read bits, compare fp32/fp16/bf16/fp8 range and precision, write a stable softmax with log-sum-exp, and explain why data layout changes speed by orders of magnitude |
| 05 | [Processes, threads and I/O](notes/05-processes-threads-and-io.md) | Price a process, thread and system call, prevent races and deadlocks, keep an event loop moving, and size a queue |
| 06 | [Networks](notes/06-networks.md) | Frame a TCP stream, count the round trips in a cold request, read a DNS packet, and retry safely |

**Lab:** [build the structures yourself](practice/README.md): a dynamic array, a compact hash table and an LRU cache after chapter 2, compensated summation after chapter 4, and a stream decoder and retransmission timer after chapter 6.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [Python 03: Concurrency](../python/03-language-for-engineers/notes/07-concurrency.md) | The `asyncio` and thread pool APIs, whose underlying model chapter 5 explains |
| [Python 03: Objects, inheritance and the MRO](../python/03-language-for-engineers/notes/08-objects-inheritance-and-mro.md) | How attribute lookup works, which chapter 2's `dict` sits under |
| [Python 03: Memory and the runtime](../python/03-language-for-engineers/notes/09-memory-and-the-runtime.md) | Refcounting and free-threading, which chapters 4 and 5 build on |

**Feeds into**

| Chapter | Why |
|---|---|
| [Debugging and profiling](../software-design/notes/06-debugging-and-profiling.md) | Using a profiler to find the costs chapter 1 teaches you to predict |
| [Row and column stores](../../data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores.md) | Chapter 4's layout results at the scale of a database |
| [Persistence](../../data-engineering/01-storage-and-compute-foundations/notes/09-persistence.md) | What happens after chapter 5's `flush`, including `fsync` |
| [When distributed systems fail](../../data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail.md) | Chapter 6's timeouts and retries across many machines |
| [The hardware](../../ai-engineering/07-inference-engineering/notes/02-the-hardware.md) | Chapter 4's memory hierarchy applied to inference |

## Rules of thumb

- Measure before you optimise, and fix the algorithm before the constant factor.
- Name the variable in a Big-O claim, and ask what the input size really is.
- Amortised cost is the right number for throughput, and the wrong one for a latency budget.
- Use the built-in `dict`, `set`, `sort` and `heapq` before writing your own: they run at C speed, and that often beats a better algorithm in Python.
- Never compare floats with `==`, and never hold money in them if a rounding rule applies.
- When numeric code is slow, change the layout first. Vectorise before you parallelise.
- A shared read-modify-write needs a lock, whatever the GIL seems to promise.
- Take locks in one global order, and give every queue a bound.
- Use threads or `asyncio` for waiting, and processes for pure Python CPU work.
- `recv` returns bytes, not messages. Every connection needs a timeout, and every retried POST an idempotency key.
- Reuse connections. On a slow API, count the round trips before you read the code.

## Layout

```
computer-science/
├── README.md
├── references.md
├── notes/                         01–06
└── practice/
    ├── README.md                  the lab: what to build and how it's checked
    ├── check.sh                   runs the lab's tests and every code block in the notes
    ├── run_notes.py               runs the notes' blocks, and compares output where it's fixed
    ├── exercises/foundations_lab/    stubs and their tests
    └── solutions/foundations_lab/    worked versions and the same tests
```

## Setup

You need Python 3.14 and [uv](https://docs.astral.sh/uv/). The notes' code blocks are standalone: copy one into a file and run it. A few are marked with a comment in the note's source. Those need NumPy, the free-threaded build (`uv run --python 3.14t`), OpenSSL's command line tool or the network, and `check.sh` handles all but the last by default. See [practice/README.md](practice/README.md). Your timings will differ from those printed, as they should: compare the ratios.

## Primary texts

- Arpaci-Dusseau, [*Operating Systems: Three Easy Pieces*](https://pages.cs.wisc.edu/~remzi/OSTEP/), free online: the process, concurrency and I/O chapters
- Jeff Erickson, [*Algorithms*](https://jeffe.cs.illinois.edu/teaching/algorithms/), free online: parts on recursion, dynamic programming, greedy algorithms and graphs
- Lehman, Leighton, Meyer, [*Mathematics for Computer Science*](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf), the MIT 6.042 text: sums, asymptotics and recurrences
- CPython's design notes: [`dictnotes.txt`](https://github.com/python/cpython/blob/v3.14.7/Objects/dictnotes.txt), [`listsort.txt`](https://github.com/python/cpython/blob/v3.14.7/Objects/listsort.txt), and comments in `dictobject.c` and `listobject.c`
- David Goldberg, [What Every Computer Scientist Should Know About Floating-Point Arithmetic](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)
- Ulrich Drepper, [*What Every Programmer Should Know About Memory*](https://www.akkadia.org/drepper/cpumemory.pdf)
- The RFCs for [TCP](https://www.rfc-editor.org/rfc/rfc9293), [DNS](https://www.rfc-editor.org/rfc/rfc1035), [HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112) and [TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)

The well-known textbooks in this field (Cormen et al.'s *Introduction to Algorithms*, Skiena's *The Algorithm Design Manual*) were not accessed for this track, and no claim here rests on their contents. Everything else: [references.md](references.md).
