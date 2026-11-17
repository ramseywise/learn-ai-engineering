# Computer science foundations

The university-level ideas behind the Python you already write, and how to reason about making it faster. Two steps and six chapters: cost models, data structures and algorithm patterns, then numbers and memory, processes and threads, and networks. Math is taught where it's used, and claims about speed are measured in the note that makes them.

**What you should already know.** [Python 03 Language for engineers](../python/README.md), all of it: this track makes its cost and memory arguments on Python's own objects. It leans most on [concurrency](../python/03-language-for-engineers/notes/07-concurrency.md), [objects and the MRO](../python/03-language-for-engineers/notes/08-objects-inheritance-and-mro.md) and [memory and the runtime](../python/03-language-for-engineers/notes/09-memory-and-the-runtime.md).

## Lecture

Start with the overview deck, [Computer science foundations](slides/computer-science.pptx) ([PDF](slides/computer-science.pdf)), on the same examples as the notes. Librarian turns each slide into a flashcard: the title is the question and the takeaway is the rule that answers it.

## The core

Python hides the machine well enough that you can work for years without a model of it, until a job takes all night, a `dict` doubles your memory, a total comes out wrong by a cent, or a service stalls with an idle CPU. This track gives you that model in the order you'd need it. It is one question asked at every layer: **what's being counted, and what does one of them cost?** Big-O counts the operations, the data structure chapter says what an operation really does, the memory chapter prices it in cache misses, and the systems chapters show that the largest cost is often waiting, which doesn't show up in Big-O at all.

There are two steps: reasoning about the code you can see, then the machine underneath it. The track sits beside the [Python track](../python/README.md), which teaches the language, and gives [software design](../software-design/README.md), [backend and system design](../backend-and-system-design/README.md) and the systems in the data and AI subjects their vocabulary.

It inherits a weakness from its method: measured numbers come from one machine (an Apple M4 Pro, on CPython 3.14.7), so the ratios travel better than the absolute values, and microbenchmarks can flatter or hide effects you'd see in a real program. It's also not a substitute for a full algorithms course. Proofs appear only where they change how you'd reason, and [references.md](references.md) lists the books it didn't read.

## Syllabus

One row per step. **Core concepts** are the ideas the step turns on, **Study** is what to read, **Labs** is what to do afterwards (the track's own lab first, then the drills on the same topic), and **Sources** is where to read more. How to run the lab: [practice/README.md](practice/README.md).

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. Reasoning about code:** counting work | Name the variable in a Big-O claim, and ask what the input size really is. Amortised cost is right for throughput and wrong for a latency budget. A `list` is a dynamic array and a `dict` is a compact hash table, and the built-ins run at C speed. Most algorithms come from a handful of patterns, and each has an argument for why it is correct. | [1 Cost models and Big-O](notes/01-cost-models-and-big-o.md) · [2 Data structures](notes/02-data-structures.md) · [3 Algorithm patterns](notes/03-algorithm-patterns.md) | [Lab](practice/README.md), after chapter 2: a dynamic array, a compact hash table and an LRU cache · drills: [data structures and algorithms](../drills/coding/dsa/README.md) · [timed algorithm problems](../drills/coding/algorithms/README.md) · [an LRU cache under interview conditions](../drills/coding/prompts/cache-lru.py) | Erickson, [*Algorithms*](https://jeffe.cs.illinois.edu/teaching/algorithms/) · Lehman, Leighton, Meyer, [*Mathematics for Computer Science*](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf) · CPython's [`dictnotes.txt`](https://github.com/python/cpython/blob/v3.14.7/Objects/dictnotes.txt) and [`listsort.txt`](https://github.com/python/cpython/blob/v3.14.7/Objects/listsort.txt) |
| **2. The machine underneath:** what one operation costs | Never compare floats with `==`. When numeric code is slow, change the layout first, and vectorise before you parallelise. A shared read-modify-write needs a lock, and every queue needs a bound. Threads and `asyncio` are for waiting, processes for CPU work. `recv` returns bytes, not messages, and every connection needs a timeout. | [4 Numbers and memory](notes/04-numbers-and-memory.md) · [5 Processes, threads and I/O](notes/05-processes-threads-and-io.md) · [6 Networks](notes/06-networks.md) | [Lab](practice/README.md): compensated summation after chapter 4, a stream decoder and a retransmission timer after chapter 6 · drills, after chapter 4: [softmax and cross-entropy gradient](../drills/coding/ml-coding/softmax-cross-entropy-grad.md) · [gradient check in NumPy](../drills/coding/ml-coding/gradient-check-numpy.md) | Goldberg, [floating-point arithmetic](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) · Drepper, [*What Every Programmer Should Know About Memory*](https://www.akkadia.org/drepper/cpumemory.pdf) · Arpaci-Dusseau, [*Operating Systems: Three Easy Pieces*](https://pages.cs.wisc.edu/~remzi/OSTEP/) · RFCs for [TCP](https://www.rfc-editor.org/rfc/rfc9293), [DNS](https://www.rfc-editor.org/rfc/rfc1035), [HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112) and [TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446) |

The notes follow the [full chapter standard](https://github.com/ramseywise/librarian/blob/main/.claude/skills/pillar/references/pillar-layout.md), not the shorter format of the Python modules. Every source and the chapter it maps to: [references.md](references.md).

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

## Builds on and feeds into

**Builds on**

Read this track after Python 03: the rows below are what it leans on, and Python 03 links back here only as further reading.

| Chapter | Why |
|---|---|
| [Python 03: Concurrency](../python/03-language-for-engineers/notes/07-concurrency.md) | The `asyncio` and thread pool APIs, whose underlying model chapter 5 explains |
| [Python 03: Objects, inheritance and the MRO](../python/03-language-for-engineers/notes/08-objects-inheritance-and-mro.md) | How attribute lookup works, which chapter 2's `dict` sits under |
| [Python 03: Memory and the runtime](../python/03-language-for-engineers/notes/09-memory-and-the-runtime.md) | Refcounting and free-threading, which chapters 4 and 5 build on |

**Feeds into**

| Chapter | Why |
|---|---|
| [Debugging and profiling](../software-design/notes/06-debugging-and-profiling.md) | Using a profiler to find the costs chapter 1 teaches you to predict |
| [Backend and system design](../backend-and-system-design/README.md) | Chapters 5 and 6 are its soft prerequisites: queues, the event loop and what a request costs |
| [Row and column stores](../../data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores.md) | Chapter 4's layout results at the scale of a database |
| [Persistence](../../data-engineering/01-storage-and-compute-foundations/notes/09-persistence.md) | What happens after chapter 5's `flush`, including `fsync` |
| [When distributed systems fail](../../data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail.md) | Chapter 6's timeouts and retries across many machines |
| [The hardware](../../ai-engineering/07-inference-engineering/notes/02-the-hardware.md) | Chapter 4's memory hierarchy applied to inference |

## Primary texts

- Arpaci-Dusseau, [*Operating Systems: Three Easy Pieces*](https://pages.cs.wisc.edu/~remzi/OSTEP/), free online: the process, concurrency and I/O chapters
- Jeff Erickson, [*Algorithms*](https://jeffe.cs.illinois.edu/teaching/algorithms/), free online: parts on recursion, dynamic programming, greedy algorithms and graphs
- Lehman, Leighton, Meyer, [*Mathematics for Computer Science*](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf), the MIT 6.042 text: sums, asymptotics and recurrences
- CPython's design notes: [`dictnotes.txt`](https://github.com/python/cpython/blob/v3.14.7/Objects/dictnotes.txt), [`listsort.txt`](https://github.com/python/cpython/blob/v3.14.7/Objects/listsort.txt), and comments in `dictobject.c` and `listobject.c`
- David Goldberg, [What Every Computer Scientist Should Know About Floating-Point Arithmetic](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)
- Ulrich Drepper, [*What Every Programmer Should Know About Memory*](https://www.akkadia.org/drepper/cpumemory.pdf)
- The RFCs for [TCP](https://www.rfc-editor.org/rfc/rfc9293), [DNS](https://www.rfc-editor.org/rfc/rfc1035), [HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112) and [TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)

The well-known textbooks in this field (Cormen et al.'s *Introduction to Algorithms*, Skiena's *The Algorithm Design Manual*) were not accessed for this track, and no claim here rests on their contents. Everything else: [references.md](references.md). The deck is built from [`slides/deck.yaml`](slides/deck.yaml) with `make slides PILLAR=programming/computer-science`.

## Next

Start with step 1, **Reasoning about code**: read [1 Cost models and Big-O](notes/01-cost-models-and-big-o.md), and build the lab's first three structures once you have read chapter 2.

After step 2 you can say what a piece of code costs and where a request's time goes. Keeping that code cheap to change is [software design](../software-design/README.md), and keeping a service standing under real traffic is [backend and system design](../backend-and-system-design/README.md).
