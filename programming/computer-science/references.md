---
origin: curated
sources:
  - https://github.com/python/cpython/tree/v3.14.7/Objects
  - https://pages.cs.wisc.edu/~remzi/OSTEP/
  - https://jeffe.cs.illinois.edu/teaching/algorithms/
  - https://courses.csail.mit.edu/6.042/spring18/mcs.pdf
  - https://www.rfc-editor.org/rfc/rfc9293
confidence: high
cleaned: 2026-11-02
---
# References: computer science

Every row here was read for this track, and the "Read" column says how much. "Parts" means the sections a chapter relies on, not the whole work, so don't take a row as a claim about anything beyond those parts. For CPython's source files, only the comments and the functions named were read. Links were fetched on 2026-11-02, and none failed. Claims about performance don't rest on these sources: they come from code in the notes, run on the machine each chapter names.

## Books not accessed

These are the standard books on the subject. They weren't read for this track, so no chapter cites them. The free works below were read instead.

| Book | Instead, this track read | Would add |
|---|---|---|
| Cormen, Leiserson, Rivest, Stein, *Introduction to Algorithms* | Erickson's *Algorithms*, and *Mathematics for Computer Science* | Full proofs, including union-find's analysis and the master theorem |
| Steven Skiena, *The Algorithm Design Manual* | Erickson's *Algorithms* | A catalogue of problems and war stories |

These weren't read either, so nothing here rests on them. Where a chapter mentions the idea, it says so and derives or measures it instead:

| Work | How the chapter handles it |
|---|---|
| Little, the proof of `L = λW` | [Chapter 5](notes/05-processes-threads-and-io.md#queues-littles-law) checks the law by measurement |
| Chiu and Jain, on additive increase and multiplicative decrease | [Chapter 6](notes/06-networks.md#sharing-a-link-aimd) shows a small simulation, labelled as such |
| Neumaier's paper on compensated summation | [Chapter 4](notes/04-numbers-and-memory.md#summing-many-numbers) uses the name only, and tests the code |

## Books and long works read online

| Source | Read | Maps to |
|---|---|---|
| Arpaci-Dusseau and Arpaci-Dusseau, [*Operating Systems: Three Easy Pieces*](https://pages.cs.wisc.edu/~remzi/OSTEP/) | [Process API](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-api.pdf), [limited direct execution](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf), [concurrency introduction](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf), [locks](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks.pdf), [concurrency bugs](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf), [event-based concurrency](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-events.pdf), [I/O devices](https://pages.cs.wisc.edu/~remzi/OSTEP/file-devices.pdf), [TLBs](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-tlbs.pdf), [swapping mechanisms](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys.pdf) | 04, 05 |
| Jeff Erickson, [*Algorithms*](https://jeffe.cs.illinois.edu/teaching/algorithms/) | Parts: recursion trees, divide and conquer, the remark on randomised quicksort, backtracking, dynamic programming as smart recursion, the greedy scheduling exchange argument, whatever-first search, topological sort, Dijkstra | 01, 03 |
| Lehman, Leighton, Meyer, [*Mathematics for Computer Science*](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf), the MIT 6.042 text | §14.1 on sums, §14.7 on asymptotic notation, §22.4 on recurrences | 01 |
| Ulrich Drepper, [*What Every Programmer Should Know About Memory*](https://www.akkadia.org/drepper/cpumemory.pdf), 2007 | Parts: the cache sections and their measurement method | 04 |
| ★ Jake VanderPlas, *Python Data Science Handbook* (O'Reilly, 2016, first edition, inferred from the library versions in its output), ch. 2. Chapter PDF in [data-analytics/sources/python-data-science-handbook/](../../data-analytics/sources/python-data-science-handbook/) | Broadcasting rules and Fig. 2-4, and all-pairs distance by broadcasting plus `argpartition`. Folded in as: ch. 2 → [04](notes/04-numbers-and-memory.md#broadcasting-stretching-without-copying). Notes cite it as `(*Python Data Science Handbook*, ch. 2)` | 04 |

## Core papers

| Paper | Read | Why | Maps to |
|---|---|---|---|
| David Goldberg, [What Every Computer Scientist Should Know About Floating-Point Arithmetic](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html), 1991 | Parts: rounding error, guard digits, cancellation, and summation | Why subtraction loses precision, and how to reason about it | 04 |
| Gene Amdahl, [Validity of the single processor approach](https://www3.cs.stonybrook.edu/~rezaul/Spring-2012/CSE613/reading/Amdahl-1967.pdf), 1967 | All of it | The source of the limit, argued in prose. The formula is later algebra | 05 |
| Crosby and Wallach, [Denial of Service via Algorithmic Complexity Attacks](https://www.usenix.org/legacy/events/sec03/tech/full_papers/crosby/crosby.pdf), 2003 | Abstract and introduction | Why hash tables get attacked | 02 |
| Munro and Wild, [Nearly-Optimal Mergesorts](https://arxiv.org/abs/1805.04154), 2018 | Abstract only | Where Python's current merge policy comes from | 02 |

## CPython source and design notes

All at tag v3.14.7, the version the notes ran on.

| Source | Read | Maps to |
|---|---|---|
| [`Objects/dictobject.c`](https://github.com/python/cpython/blob/v3.14.7/Objects/dictobject.c) | Layout and probing comments, resize and growth | 02 |
| [`Objects/dictnotes.txt`](https://github.com/python/cpython/blob/v3.14.7/Objects/dictnotes.txt) | All of it | 02 |
| [`Objects/listobject.c`](https://github.com/python/cpython/blob/v3.14.7/Objects/listobject.c) | `list_resize` and its comments | 02 |
| [`Objects/listsort.txt`](https://github.com/python/cpython/blob/v3.14.7/Objects/listsort.txt) | Parts on runs, merging and galloping | 02 |
| [`Include/cpython/longintrepr.h`](https://github.com/python/cpython/blob/v3.14.7/Include/cpython/longintrepr.h), [`Objects/longobject.c`](https://github.com/python/cpython/blob/v3.14.7/Objects/longobject.c) | Comments on digit layout and on Karatsuba | 04 |
| Raymond Hettinger, [compact dictionaries proposal](https://mail.python.org/pipermail/python-dev/2012-December/123028.html), python-dev, 2012 | All of it | 02 |
| [PEP 412](https://peps.python.org/pep-0412/), key-sharing dictionaries; [PEP 456](https://peps.python.org/pep-0456/), secure hash | Abstract and rationale | 02 |

## RFCs

| RFC | Read | Maps to |
|---|---|---|
| [9293](https://www.rfc-editor.org/rfc/rfc9293), TCP | §3.4 on sequence numbers and MSL, §3.5 handshake, §3.6 close and half-close, §3.7.4 Nagle | 06 |
| [6298](https://www.rfc-editor.org/rfc/rfc6298), retransmission timer | All of it | 06 |
| [5681](https://www.rfc-editor.org/rfc/rfc5681), congestion control | §3.1 | 06 |
| [6928](https://www.rfc-editor.org/rfc/rfc6928), initial window | Introduction and the change itself | 06 |
| [1034](https://www.rfc-editor.org/rfc/rfc1034), [1035](https://www.rfc-editor.org/rfc/rfc1035), DNS | 1034 §3.7, §4.3.1. 1035 §4.1 on format and compression, §4.2.1 on UDP | 06 |
| [8305](https://www.rfc-editor.org/rfc/rfc8305), Happy Eyeballs | §3, §5 | 06 |
| [9110](https://www.rfc-editor.org/rfc/rfc9110), HTTP semantics | §9.2.1, §9.2.2 | 06 |
| [9112](https://www.rfc-editor.org/rfc/rfc9112), HTTP/1.1 | §6.3, §7.1, §9.3, §9.3.2 | 06 |
| [9113](https://www.rfc-editor.org/rfc/rfc9113), HTTP/2 | §1 | 06 |
| [9114](https://www.rfc-editor.org/rfc/rfc9114), HTTP/3; [9000](https://www.rfc-editor.org/rfc/rfc9000), QUIC | 9114 §1.1, §1.2. 9000 introduction | 06 |
| [8446](https://www.rfc-editor.org/rfc/rfc8446), TLS 1.3 | §2, §2.3, §4.6.1, Appendix E.5 | 06 |
| [6066](https://www.rfc-editor.org/rfc/rfc6066), TLS extensions | §3 on SNI | 06 |
| [2606](https://www.rfc-editor.org/rfc/rfc2606), reserved names | All of it, for why the examples use `example.com` | 06 |

## Reference documentation

All from the [Python 3.14 documentation](https://docs.python.org/3.14/), except the first row and NumPy.

| Source | Read | Maps to |
|---|---|---|
| [Python's time complexity page](https://docs.python.org/3/builtins/time-complexity.html) | All of it | 01, 02 |
| [`collections`](https://docs.python.org/3.14/library/collections.html), [`heapq`](https://docs.python.org/3.14/library/heapq.html), [`bisect`](https://docs.python.org/3.14/library/bisect.html), [`functools`](https://docs.python.org/3.14/library/functools.html), [sorting how-to](https://docs.python.org/3.14/howto/sorting.html) | The types and functions used | 02, 03 |
| [Floating-point tutorial](https://docs.python.org/3.14/tutorial/floatingpoint.html), [`math`](https://docs.python.org/3.14/library/math.html), [`sys`](https://docs.python.org/3.14/library/sys.html), [`decimal`](https://docs.python.org/3.14/library/decimal.html), [`fractions`](https://docs.python.org/3.14/library/fractions.html), [`struct`](https://docs.python.org/3.14/library/struct.html), [`array`](https://docs.python.org/3.14/library/array.html), [`mmap`](https://docs.python.org/3.14/library/mmap.html), [built-in `sum`](https://docs.python.org/3.14/library/functions.html#sum), [`int` limits](https://docs.python.org/3.14/library/stdtypes.html#int-max-str-digits) | The parts used | 04 |
| [NumPy `sum`](https://numpy.org/doc/stable/reference/generated/numpy.sum.html) | The note on pairwise summation | 04 |
| [`multiprocessing`](https://docs.python.org/3.14/library/multiprocessing.html), [`threading`](https://docs.python.org/3.14/library/threading.html), [`os`](https://docs.python.org/3.14/library/os.html), [`subprocess`](https://docs.python.org/3.14/library/subprocess.html), [`selectors`](https://docs.python.org/3.14/library/selectors.html), [`concurrent.futures`](https://docs.python.org/3.14/library/concurrent.futures.html), [event loop](https://docs.python.org/3.14/library/asyncio-eventloop.html), [`time`](https://docs.python.org/3.14/library/time.html), [glossary](https://docs.python.org/3.14/glossary.html) | The parts used, including start methods and the GIL entries | 05 |
| [`socket`](https://docs.python.org/3.14/library/socket.html), [`ssl`](https://docs.python.org/3.14/library/ssl.html), [`http.client`](https://docs.python.org/3.14/library/http.client.html), [`hashlib`](https://docs.python.org/3.14/library/hashlib.html) | The parts used | 02, 06 |
