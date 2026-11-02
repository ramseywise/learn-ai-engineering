# Advanced Python — senior-interview concepts

54 concepts that senior Python screens probe beyond syntax: concurrency, memory, the data
model, metaprogramming. This is the gap `flashcards.md` flags, and the "why is this slow /
why does this leak / why didn't threads help" follow-up that comes after a coding round.

**How to drill it:** pick a theme and answer each recall prompt out loud in under 60
seconds, *then* open the handbook section to check. Concepts you missed get their example
run and rewritten from memory in `drills/coding/scratch/`. Log it in
[`../../coding/drill-log.md`](../../coding/drill-log.md) with QID `py-adv-<theme>`.

| Folder | What |
|---|---|
| [`handbook/`](handbook/) | Explanation per concept: why it matters, trade-offs, when to use |
| [`examples/`](examples/) | One runnable script per concept (`N.<name>.py`); the `.txt` files are inputs for 37/38 |

Source: [gostak-dd/fifty-advanced-python-concepts](https://github.com/gostak-dd/fifty-advanced-python-concepts)
(formerly `GGyll/…`), imported 2026-10-29. The `.pkl`/`.db`/`.bin` files the scripts write
on first run were not copied, so run 27, 28 and 33 to regenerate them.

## Concurrency and parallelism — highest interview yield

| # | Concept | Recall prompt | Handbook |
|---|---|---|---|
| 7 | CPython | What does "CPython" mean, and what does the implementation choice decide for you? | [1–10](handbook/concepts-1-10.md#7-cpython) |
| 8 | GIL | Why don't threads speed up a CPU-bound loop in CPython, and why do they still help I/O? | [1–10](handbook/concepts-1-10.md#8-global-interpreter-lock-gil) |
| 9 | Concurrency vs parallelism | Define both in one sentence each and give a Python tool for each. | [1–10](handbook/concepts-1-10.md#9-concurrency-vs-parallelism) |
| 10 | Multithreading | When is `ThreadPoolExecutor` the right choice? What shared state still needs a lock? | [1–10](handbook/concepts-1-10.md#10-multithreading) |
| 11 | Multiprocessing | What does a new process cost, and what has to be picklable? | [11–25](handbook/concepts-11-25.md#11-multiprocessing) |
| 12 | Race conditions | Show a race on `counter += 1` and two ways to fix it. | [11–25](handbook/concepts-11-25.md#12-race-conditions-multiprocessing--multithreading) |
| 13 | Shared memory | `Value`/`Array`/`shared_memory`: when do you share instead of passing messages? | [11–25](handbook/concepts-11-25.md#13-shared-memory-in-multiprocessing) |
| 50 | asyncio | Event loop, `await`, `gather`. What happens if you call blocking I/O inside a coroutine? | [41–52](handbook/concepts-41-52.md#50-asyncio) |
| 52 | Multiprocessing `Queue` | Sketch a producer/consumer with a sentinel for shutdown. | [41–52](handbook/concepts-41-52.md#52-multiprocessing-with-queue) |

## Memory and performance

| # | Concept | Recall prompt | Handbook |
|---|---|---|---|
| 1 | `array` module | When is `array.array` better than a list, and what does it cost you? | [1–10](handbook/concepts-1-10.md#1-arrays-python-array-module) |
| 2 | GC and cycles | Reference counting vs the cycle collector: what does each one catch? | [1–10](handbook/concepts-1-10.md#2-garbage-collection--circular-references) |
| 3 | Not returning dicts/lists | Why might a function avoid returning a large mutable container? What instead? | [1–10](handbook/concepts-1-10.md#3-not-returning-dicts--lists-from-functions) |
| 33 | `bytes` | `bytes` vs `bytearray` vs `str`: when does encoding happen? | [26–40](handbook/concepts-26-40.md#33-bytes) |
| 34 | Bytecode / `dis` | What does `dis.dis` show you, and when has it settled an argument? | [26–40](handbook/concepts-26-40.md#34-bytecode--dis-module) |
| 35 | `memoryview` | How does `memoryview` avoid copies when slicing a large buffer? | [26–40](handbook/concepts-26-40.md#35-memoryview) |
| 40 | `weakref` | What problem does a weak reference solve in a cache? | [26–40](handbook/concepts-26-40.md#40-weakref) |
| 41 | `WeakKeyDictionary` | When would you key metadata by object without keeping it alive? | [41–52](handbook/concepts-41-52.md#41-weakkeydictionary--weakvaluedictionary) |
| 42 | `__slots__` | What does `__slots__` save, and what does it break? | [41–52](handbook/concepts-41-52.md#42-optimizing-memory-with-__slots__) |
| 43 | `memory_profiler` | How do you find which line allocates the memory? | [41–52](handbook/concepts-41-52.md#43-memory_profiler) |
| 44 | `sys.getsizeof` | Why does `getsizeof` of a list understate its real footprint? | [41–52](handbook/concepts-41-52.md#44-sysgetsizeof) |

## OOP and the data model

| # | Concept | Recall prompt | Handbook |
|---|---|---|---|
| 4 | MRO | Explain C3 linearization on a diamond; what does `super()` actually call? | [1–10](handbook/concepts-1-10.md#4-method-resolution-order-mro) |
| 15 | Encapsulation | `_x` vs `__x`: what does name mangling really do? | [11–25](handbook/concepts-11-25.md#15-encapsulation) |
| 16 | Abstraction | Abstraction vs encapsulation, with one example each. | [11–25](handbook/concepts-11-25.md#16-abstraction) |
| 17 | ABCs | What does `@abstractmethod` enforce, and when? | [11–25](handbook/concepts-11-25.md#17-abstract-base-classes-abc) |
| 18 | Inheritance | When is composition the better answer? | [11–25](handbook/concepts-11-25.md#18-inheritance) |
| 19 | Polymorphism | Duck typing vs subclass polymorphism in Python. | [11–25](handbook/concepts-11-25.md#19-polymorphism) |
| 20 | Dunder methods | Which dunders make a class sortable, hashable, iterable, a context manager? | [11–25](handbook/concepts-11-25.md#20-python-data-model-magic--dunder-methods) |
| 21 | Iterators | `__iter__` vs `__next__`, and why an iterator is exhausted after one pass. | [11–25](handbook/concepts-11-25.md#21-iterators) |
| 22 | Generators | Why is a generator pipeline O(1) memory? What does `yield from` add? | [11–25](handbook/concepts-11-25.md#22-generators) |
| 23 | static/classmethod | When is `@classmethod` the right constructor? | [11–25](handbook/concepts-11-25.md#23-staticmethod-and-classmethod) |
| 24 | Dependency injection | Rewrite a class that builds its own DB client so it's testable. | [11–25](handbook/concepts-11-25.md#24-dependency-injection) |
| 51 | `__call__` | When is a callable object better than a closure? | [41–52](handbook/concepts-41-52.md#51-callable-objects-__call__) |
| 54 | Descriptors | How do `property` and `cached_property` work under the hood? | [53–54](handbook/concepts-53-54.md#54--descriptors-typed--cachedproperty) |

## Metaprogramming, decorators, typing

| # | Concept | Recall prompt | Handbook |
|---|---|---|---|
| 36 | Metaclasses | What runs at class-creation time, and why do you almost never need a metaclass? | [26–40](handbook/concepts-26-40.md#36-metaclasses) |
| 37 | Metaclasses in frameworks | How does a Django model turn class attributes into columns? | [26–40](handbook/concepts-26-40.md#37-metaclasses-in-frameworks-django-example) |
| 45 | Advanced decorators | Write a decorator with arguments that preserves the signature. | [41–52](handbook/concepts-41-52.md#45-advanced-decorators) |
| 47 | Metaprogramming | `__init_subclass__`, `type()`, `setattr`: which is the least magic tool for registration? | [41–52](handbook/concepts-41-52.md#47-metaprogramming) |
| 53 | Protocols and generics | Structural vs nominal typing; write a `Protocol` and a `TypeVar`-bound function. | [53–54](handbook/concepts-53-54.md#53--typing-protocols--generics) |

## Functional and stdlib idioms

| # | Concept | Recall prompt | Handbook |
|---|---|---|---|
| 5 | Walrus `:=` | Show one place it removes a duplicate call, and one place it hurts readability. | [1–10](handbook/concepts-1-10.md#5-walrus-operator-) |
| 6 | `operator.attrgetter` | Sort objects by two attributes without a lambda. | [1–10](handbook/concepts-1-10.md#6-operatorattrgetter) |
| 14 | `collections` | `Counter`, `defaultdict`, `deque`, `namedtuple`, `OrderedDict`: one use each. | [11–25](handbook/concepts-11-25.md#14-collections-module) |
| 29 | `heapq` | Top-k of a stream in O(n log k). Max-heap in a min-heap library? | [26–40](handbook/concepts-26-40.md#29-heapq) |
| 30 | Higher-order functions | Write `compose(f, g)` and say where you'd use it. | [26–40](handbook/concepts-26-40.md#30-higher-order-functions) |
| 31 | `filter` | `filter` vs a comprehension: which is clearer, and when? | [26–40](handbook/concepts-26-40.md#31-filter) |
| 32 | Advanced comprehensions | Nested comprehension order; when to switch to a loop. | [26–40](handbook/concepts-26-40.md#32-advanced-list-comprehensions) |
| 46 | `dataclasses` | What does `@dataclass` generate? `frozen`, `order`, `field(default_factory=…)`. | [41–52](handbook/concepts-41-52.md#46-dataclasses) |
| 48 | `functools` | `lru_cache`, `partial`, `wraps`, `reduce`, `singledispatch`: one use each. | [41–52](handbook/concepts-41-52.md#48-functools) |
| 49 | Advanced dataclasses | `__post_init__`, `slots=True`, `kw_only`: when each earns its place. | [41–52](handbook/concepts-41-52.md#49-advanced-dataclass-features) |

## Resources, testing, serialization

| # | Concept | Recall prompt | Handbook |
|---|---|---|---|
| 25 | Parameterized testing | Turn five copy-pasted tests into one `@pytest.mark.parametrize`. | [11–25](handbook/concepts-11-25.md#25-parameterized-testing) |
| 26 | Fixtures | Fixture scope, `yield` teardown, `tmp_path`. | [26–40](handbook/concepts-26-40.md#26-fixtures-testing-setup--teardown) |
| 27 | Serialization | `pickle` vs `json`: why is unpickling untrusted data a security bug? | [26–40](handbook/concepts-26-40.md#27-serialization--deserialization) |
| 28 | `__getstate__`/`__setstate__` | How do you pickle an object that holds a socket or a lock? | [26–40](handbook/concepts-26-40.md#28-__getstate__-and-__setstate__) |
| 38 | Nested context managers | `ExitStack`: when the number of resources isn't known up front. | [26–40](handbook/concepts-26-40.md#38-nesting--combining-context-managers) |
| 39 | Custom context managers | Write one as a class and as `@contextmanager`; what happens on exception? | [26–40](handbook/concepts-26-40.md#39-custom-context-managers) |
