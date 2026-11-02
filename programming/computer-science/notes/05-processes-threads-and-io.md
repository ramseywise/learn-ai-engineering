---
origin: synthesis
sources:
  - "Arpaci-Dusseau, Operating Systems: Three Easy Pieces, chapters cpu-api, cpu-mechanisms, threads-intro, threads-locks, threads-bugs, threads-events, file-devices — https://pages.cs.wisc.edu/~remzi/OSTEP/"
  - "Gene Amdahl, Validity of the single processor approach, AFIPS 1967 — https://www3.cs.stonybrook.edu/~rezaul/Spring-2012/CSE613/reading/Amdahl-1967.pdf"
  - "Python docs: multiprocessing start methods, threading, selectors, os, glossary (free-threaded) — https://docs.python.org/3.14/library/multiprocessing.html"
concepts: [process, thread, system-call, context-switch, race-condition, critical-section, lock, deadlock, blocking-io, event-loop, buffering, littles-law, backpressure, amdahls-law]
confidence: high
cleaned: 2026-11-02
---
# 5 — Processes, threads and I/O

> Most Python performance mysteries are about waiting, and they're not about computing. A request sits in a queue, a thread sits on a lock, and an event loop stops dead because one handler called something that blocks. To reason about those, you need the operating system's model: what a process is, what happens when your code asks the kernel for something, what a thread shares, and why an interleaving nobody planned can lose an update. This chapter builds that model and prices each operation on one machine, from a 10 ns function call to a 32 ms process start. [Concurrency in Python](../../python/03-language-for-engineers/notes/07-concurrency.md) already covers `asyncio`, thread pools and how to choose between them. This is the layer beneath it, so read that for the API and this for the reason. Measurements are from an Apple M4 Pro on macOS with CPython 3.14.7.

---

## A process is a running program with its own memory

A process is what the OS gives a program to run in: an address space, some open files, and at least one thread of execution. Unix creates one in a strange but useful way. `fork` copies the running process, and `exec` replaces the copy's program with a new one. [OSTEP's process API chapter](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-api.pdf) explains why they're separate: the shell runs code between the two, and that's how it sets up redirection.

```python
import os
import sys

tokens_seen = 100
pid = os.fork()
if pid == 0:  # the child: a copy of the parent's memory
    tokens_seen += 1
    print(f"child sees {tokens_seen}", flush=True)
    os.execv("/bin/echo", ["echo", "the child is now /bin/echo"])  # replaces the program
else:
    _, status = os.waitpid(pid, 0)
    print(f"parent sees {tokens_seen}; child exit code {os.waitstatus_to_exitcode(status)}")
```

```text
child sees 101
the child is now /bin/echo
parent sees 100; child exit code 0
```

The child changes its copy of `tokens_seen` and the parent doesn't see the change. That isolation is the reason a process exists: a crash or a stray write in one can't touch another. The price is that sharing data means copying it through a pipe or socket, or setting up shared memory on purpose.

In Python, you'd rarely call `fork` directly. The [multiprocessing docs](https://docs.python.org/3.14/library/multiprocessing.html#contexts-and-start-methods) say that `spawn` is the default on macOS and Windows, and that as of 3.14 `fork` isn't the default on any platform, since forking a multithreaded process is problematic. A forked child has a copy of every lock, in whatever state it was in, but only the thread that called `fork`. So a lock held by another thread stays locked forever in the child.

## What the kernel does for you, and what it costs

Your code runs with limited privileges. It can't touch a device or another process's memory directly. To do either, it makes a system call: a special instruction traps into the kernel, which runs the request with full privileges and returns. OSTEP calls this design limited direct execution: the program runs directly on the CPU for speed, and the OS regains control through traps and a timer interrupt. [That chapter](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf) also describes a context switch: the kernel saves one process's registers and restores another's. Without the timer, a program stuck in a loop would never give the machine back.

Here's the price of each boundary on this machine:

```python
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import threading
import time


def per_call(f, n):
    start = time.perf_counter()
    for _ in range(n):
        f()
    return (time.perf_counter() - start) / n


def noop():
    pass


def thread_cycle():
    t = threading.Thread(target=noop)
    t.start()
    t.join()


def fork_cycle():
    pid = os.fork()
    if pid == 0:
        os._exit(0)
    os.waitpid(pid, 0)


def spawn_cycle():
    p = mp.get_context("spawn").Process(target=noop)
    p.start()
    p.join()


def pipe_round_trip(n=20_000):
    a_r, a_w, b_r, b_w = *os.pipe(), *os.pipe()
    pid = os.fork()
    if pid == 0:
        for _ in range(n):
            os.read(a_r, 1)
            os.write(b_w, b"x")
        os._exit(0)
    start = time.perf_counter()
    for _ in range(n):
        os.write(a_w, b"x")
        os.read(b_r, 1)
    elapsed = time.perf_counter() - start
    os.waitpid(pid, 0)
    return elapsed / n


if __name__ == "__main__":
    print(sys.version.split()[0], mp.get_start_method())
    rows = [
        ("Python function call", per_call(noop, 2_000_000)),
        ("os.getppid() (a system call)", per_call(os.getppid, 2_000_000)),
        ("pipe round trip, two processes", pipe_round_trip()),
        ("thread start + join", per_call(thread_cycle, 3_000)),
        ("os.fork + waitpid", per_call(fork_cycle, 300)),
        ("subprocess: run `true`", per_call(lambda: subprocess.run([shutil.which("true")]), 100)),
        ("new python -c pass", per_call(lambda: subprocess.run([sys.executable, "-c", "pass"]), 10)),
        ("multiprocessing spawn + join", per_call(spawn_cycle, 10)),
    ]
    for label, seconds in rows:
        print(f"{label:<32} {seconds * 1e6:>12,.2f} us")
```

<!-- measured -->

```text
3.14.7 spawn
Python function call                     0.01 us
os.getppid() (a system call)             0.09 us
pipe round trip, two processes           4.92 us
thread start + join                     27.85 us
os.fork + waitpid                      718.92 us
subprocess: run `true`               1,556.39 us
new python -c pass                  16,304.21 us
multiprocessing spawn + join        32,481.50 us
```

Each row is a useful comparison. A system call that does nothing is about 9 times a Python function call. A round trip through a pipe, where the kernel has to wake the other process and then wake this one, costs 5 µs. A thread costs 28 µs to start. A forked process costs 26 times that, and a spawned process with a fresh interpreter costs 32 ms, over 1,000 times what a thread does. So you can start a thread per task if there's a reason to, but a process per request is a mistake, and that's why worker pools exist. The `python -c pass` row suggests that most of `spawn`'s cost is the interpreter starting up.

```text
           process A                          process B
  +-------------------------+          +-------------------------+
  | memory: heap, globals   |          | memory: its own copy    |
  | open files, sockets     |          | open files, sockets     |
  |  thread 1    thread 2   |          |  thread 1               |
  |  own stack   own stack  |          |  own stack              |
  +-----------+-------------+          +-----------+-------------+
              |  system call: trap into the kernel |
  ------------+------------------------------------+-------------
       kernel: scheduler, page tables, files, network, devices
```

## Threads share memory, so updates can be lost

Threads in a process share the heap and have separate stacks. That makes sharing data free and makes it unsafe. [OSTEP's introduction to concurrency](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf) gives the vocabulary: a *race condition* is when the result depends on the timing of execution, and a *critical section* is code touching shared data that mustn't run concurrently. You'd think `box["n"] += 1` was one operation. The disassembly shows otherwise:

```python
import dis
import sys
import threading
import time


def bump(box):
    box["n"] += 1


dis.dis(bump)


def run(worker, threads=4):
    box = {"n": 0}
    pool = [threading.Thread(target=worker, args=(box,)) for _ in range(threads)]
    for t in pool:
        t.start()
    for t in pool:
        t.join()
    return box["n"]


def racy(box):
    for _ in range(50):
        value = box["n"]  # read
        time.sleep(0)  # give the scheduler a chance to switch, as a timer interrupt might
        box["n"] = value + 1  # write back


lock = threading.Lock()


def safe(box):
    for _ in range(50):
        with lock:
            value = box["n"]
            time.sleep(0)
            box["n"] = value + 1


print("expected:", 4 * 50)
print("racy:    ", [run(racy) for _ in range(3)])
print("locked:  ", [run(safe) for _ in range(3)])
```

<!-- measured -->

```text
  7           RESUME                   0

  8           LOAD_FAST_BORROW         0 (box)
              LOAD_CONST               0 ('n')
              COPY                     2
              COPY                     2
              BINARY_OP               26 ([])
              LOAD_SMALL_INT           1
              BINARY_OP               13 (+=)
              SWAP                     3
              SWAP                     2
              STORE_SUBSCR
              LOAD_CONST               1 (None)
              RETURN_VALUE
expected: 200
racy:     [50, 62, 96]
locked:   [200, 200, 200]
```

The `+=` is a load, an add and a store, with a gap between them. If two threads load the same value, both store the same result and one update is gone. To make that visible I've widened the gap with `time.sleep(0)`, which lets another thread in, standing in for an ill-timed interrupt. Three runs lose most of the updates, with different totals each time, and that's what makes these bugs so hard to debug. The lock makes the three steps a critical section.

## The GIL hides this, and it's not a guarantee

Without the artificial gap, the standard build gets the right answer:

```python
import sys
import threading


def run(worker, threads=4):
    box = {"n": 0}
    pool = [threading.Thread(target=worker, args=(box,)) for _ in range(threads)]
    for t in pool:
        t.start()
    for t in pool:
        t.join()
    return box["n"]


def plain(box, n=500_000):
    for _ in range(n):
        box["n"] += 1


print("GIL enabled:", sys._is_gil_enabled())
print("got:", [run(plain) for _ in range(3)])
```

<!-- measured -->

```text
GIL enabled: True
got: [2000000, 2000000, 2000000]
```

That's exactly 2,000,000 in all three runs. The GIL only lets one thread run Python bytecode at a time, and in this build it wasn't switched in that small window. It's tempting to conclude that `+=` is safe. On the free-threaded build, it plainly isn't:

<!-- requires: free-threaded -->
```python
import sys
import threading


def run(worker, threads=4):
    box = {"n": 0}
    pool = [threading.Thread(target=worker, args=(box,)) for _ in range(threads)]
    for t in pool:
        t.start()
    for t in pool:
        t.join()
    return box["n"]


def plain(box, n=500_000):
    for _ in range(n):
        box["n"] += 1


print("GIL enabled:", sys._is_gil_enabled())
print("expected:", 4 * 500_000)
print("got:     ", [run(plain) for _ in range(3)])
```

<!-- measured -->

```text
GIL enabled: False
expected: 2000000
got:      [567019, 572334, 593672]
```

This is the same code on `python3.14t`, and about 70% of the updates are lost. It's the best demonstration I know that the earlier result was luck and not a promise. Code that "works because of the GIL" is a bug that hasn't been triggered yet, so add the lock. The state of free-threading in 3.14 is covered in [memory and the runtime](../../python/03-language-for-engineers/notes/09-memory-and-the-runtime.md#free-threading-whats-true-in-314).

## What a lock costs

Locks cost much less than people fear, as long as nobody's waiting:

```python
import threading
import time

lock = threading.Lock()
n = 2_000_000
counter = 0


def timed(f):
    start = time.perf_counter()
    f()
    return (time.perf_counter() - start) / n * 1e9


def bare():
    global counter
    for _ in range(n):
        counter += 1


def with_lock():
    global counter
    for _ in range(n):
        with lock:
            counter += 1


print(f"increment: {timed(bare):6.1f} ns;  with uncontended lock: {timed(with_lock):6.1f} ns")
```

<!-- measured -->

```text
increment:   17.2 ns;  with uncontended lock:   56.4 ns
```

An uncontended lock adds about 40 ns to each increment. [OSTEP's chapter on locks](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks.pdf) explains why: a lock is an atomic instruction on a word in memory, and it only enters the kernel if it has to wait. So the expensive thing isn't the lock but the contention: threads queueing to take turns. If you find a lock in a profile, shrink the critical section or split the data, and don't try to avoid locking.

The classic failure with several locks is deadlock:

```python
import threading
import time

cache = threading.Lock()
index = threading.Lock()
outcome = {}


def worker(name, first, second):
    with first:
        time.sleep(0.05)  # hold one, want the other: the window where both threads get stuck
        got = second.acquire(timeout=0.3)
        outcome[name] = "finished" if got else "timed out holding a lock"
        if got:
            second.release()


def run(pairs):
    threads = [threading.Thread(target=worker, args=(f"t{i}", a, b)) for i, (a, b) in enumerate(pairs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return dict(sorted(outcome.items()))


print("opposite orders:", run([(cache, index), (index, cache)]))
print("same order:     ", run([(cache, index), (cache, index)]))
```

<!-- measured -->

```text
opposite orders: {'t0': 'timed out holding a lock', 't1': 'timed out holding a lock'}
same order:      {'t0': 'finished', 't1': 'finished'}
```

`t0` holds `cache` and wants `index`, and `t1` holds `index` and wants `cache`. A plain `acquire` would hang forever, and I've added a timeout only so that the block finishes. [OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf) lists the four conditions that are all needed: mutual exclusion, hold-and-wait, no preemption and circular wait. Breaking any one prevents it, and in practice the one to break is circular wait: always take locks in one global order. The second line shows that this is enough. Timeouts on `acquire` are also worthwhile, as a hang becomes an error you can log.

## I/O: waiting without burning a core

Devices are slow, so a CPU shouldn't sit and watch them. [OSTEP's I/O chapter](https://pages.cs.wisc.edu/~remzi/OSTEP/file-devices.pdf) goes through the options: polling repeatedly asks if the device is ready, while an interrupt lets the CPU do other work until the device signals. Blocking system calls give you the same behaviour: the kernel puts your thread to sleep until the data arrives. Here's the difference from a Python thread:

```python
import select
import os
import threading
import time


def waiter(kind, r):
    start_cpu = time.process_time()
    if kind == "poll":
        os.set_blocking(r, False)
        while True:
            try:
                os.read(r, 1)
                break
            except BlockingIOError:
                pass
    else:
        select.select([r], [], [])
        os.read(r, 1)
    return time.process_time() - start_cpu


for kind in ("poll", "block"):
    r, w = os.pipe()
    threading.Timer(0.5, os.write, (w, b"x")).start()
    start = time.perf_counter()
    cpu = waiter(kind, r)
    print(f"{kind:<6} wall {time.perf_counter() - start:5.2f} s   cpu {cpu:6.3f} s")
```

<!-- measured -->

```text
poll   wall  0.51 s   cpu  0.505 s
block  wall  0.50 s   cpu  0.000 s
```

Both waited 0.5 s, and polling used 0.5 s of a CPU to do it, while blocking used none. Anything of the form `while not ready: pass` is a bug of this kind. Even with a short sleep inside, you're trading between CPU use and reaction time, while a blocking call gives you both.

Crossing into the kernel is what makes writes expensive, and buffering is how you avoid it:

```python
import os
import tempfile
import time

n = 200_000
line = b'{"tokens": 512, "ms": 81.5}\n'


def unbuffered(path):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    for _ in range(n):
        os.write(fd, line)
    os.close(fd)


def buffered(path):
    with open(path, "wb") as f:
        for _ in range(n):
            f.write(line)


def flushed_each(path):
    with open(path, "wb") as f:
        for _ in range(n):
            f.write(line)
            f.flush()


def joined(path):
    with open(path, "wb") as f:
        f.write(b"".join(line for _ in range(n)))


with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "log.jsonl")
    for f in (unbuffered, buffered, flushed_each, joined):
        start = time.perf_counter()
        f(path)
        print(f"{f.__name__:<14} {(time.perf_counter() - start) / n * 1e9:>8.0f} ns per line")
    assert os.path.getsize(path) == n * len(line)
```

<!-- measured -->

```text
unbuffered         1011 ns per line
buffered             32 ns per line
flushed_each       1108 ns per line
joined               30 ns per line
```

An `os.write` for each line costs about 1 µs, while a buffered `open` costs 32 ns, 30 times less, since it only makes a system call when the buffer fills. Flushing every line gives all of that back. That's a real tradeoff: buffered log lines are lost if the process crashes before a flush. And a `flush` only hands the data to the kernel, which is a different promise from the data being on disk, so see [persistence](../../../data-engineering/01-storage-and-compute-foundations/notes/09-persistence.md) for `fsync`. For a log you'll read after a crash, flush per line and accept the cost. For a batch job, don't.

## The event loop: many waits, one thread

A thread per connection costs a stack and a context switch per wakeup. An event loop instead asks the kernel in one call which of many sockets are ready, handles those, and asks again. [OSTEP's chapter on event-based concurrency](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-events.pdf) describes this design, built on `select`. In Python, the [`selectors`](https://docs.python.org/3.14/library/selectors.html) module is the layer that `asyncio` builds on, and this is a working server with it, about 20 lines long:

```python
import selectors
import socket
import threading
import time


def serve(listener, delay, stop):
    """A single-threaded echo server: one loop, one call that waits, many clients."""
    sel = selectors.DefaultSelector()
    listener.setblocking(False)
    sel.register(listener, selectors.EVENT_READ)
    while not stop.is_set():
        for key, _ in sel.select(timeout=0.05):
            if key.fileobj is listener:
                conn, _ = listener.accept()
                conn.setblocking(False)
                sel.register(conn, selectors.EVENT_READ)
            else:
                data = key.fileobj.recv(1024)
                if not data:
                    sel.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                if data.startswith(b"slow"):
                    time.sleep(delay)  # a blocking call: everything else now waits
                key.fileobj.sendall(data)
    sel.close()


def client(port, body, results, gap=0.0):
    time.sleep(gap)
    with socket.create_connection(("127.0.0.1", port)) as s:
        start = time.perf_counter()
        s.sendall(body)
        s.recv(1024)
        results.append((body.decode(), (time.perf_counter() - start) * 1e3))


def trial(delay):
    listener = socket.create_server(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    stop = threading.Event()
    server = threading.Thread(target=serve, args=(listener, delay, stop))
    server.start()
    results = []
    threads = [threading.Thread(target=client, args=(port, b"slow", results))]
    threads += [threading.Thread(target=client, args=(port, f"fast{i}".encode(), results, 0.02)) for i in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    stop.set()
    server.join()
    listener.close()
    fast = sorted(ms for name, ms in results if name.startswith("fast"))
    return len(fast), fast[len(fast) // 2], fast[-1]


for delay in (0.0, 0.2):
    n, median, worst = trial(delay)
    print(f"slow handler blocks {delay * 1e3:>3.0f} ms: {n} other clients, median {median:7.2f} ms, worst {worst:7.2f} ms")
```

<!-- measured -->

```text
slow handler blocks   0 ms: 50 other clients, median    0.68 ms, worst    1.13 ms
slow handler blocks 200 ms: 50 other clients, median  186.30 ms, worst  187.26 ms
```

With no blocking calls, 50 clients get a median of 0.68 ms, all on one thread. Now let one handler call `time.sleep(0.2)`, and all 50 other clients wait 186 ms, which is the rest of that 200 ms after they arrive at 20 ms. There's the fundamental rule: an event loop's concurrency only exists at the points where it waits, and one blocking call stops every client on the loop. OSTEP makes the same point, adding that this style trades locks for manual management of state across waits, which `async`/`await` now does for you.

A blocking call is anything that doesn't yield: a synchronous database driver, `requests`, a big JSON parse, or a long CPU loop. [Concurrency in Python](../../python/03-language-for-engineers/notes/07-concurrency.md) covers how to move those off the loop.

## Queues: Little's law

Once there's a queue, there's one relationship you can always use. The average number of items in a system `L` equals the arrival rate `λ` times the average time each spends there `W`, so `L = λW`. It's known as Little's law. I didn't read Little's paper, so I'll check it by measurement here, using a real queue and workers. `L` comes from a thread that samples the count independently of the timestamps:

```python
import queue
import random
import threading
import time


def run(rate, service_s, workers, seconds=1.5, seed=1):
    """Random arrivals into a queue. Measures L by sampling, W from timestamps, lambda by counting."""
    q, stop, rng = queue.Queue(), object(), random.Random(seed)
    latencies, samples = [], []
    in_system = [0]
    guard = threading.Lock()
    finished = threading.Event()

    def worker():
        while (arrived := q.get()) is not stop:
            time.sleep(service_s)
            latencies.append(time.perf_counter() - arrived)
            with guard:
                in_system[0] -= 1

    def sampler():
        while not finished.wait(0.002):
            samples.append(in_system[0])

    pool = [threading.Thread(target=worker) for _ in range(workers)]
    pool.append(threading.Thread(target=sampler))
    for t in pool:
        t.start()
    begin = next_at = time.perf_counter()
    while next_at - begin < seconds:
        next_at += rng.expovariate(rate)
        time.sleep(max(0, next_at - time.perf_counter()))
        with guard:
            in_system[0] += 1
        q.put(time.perf_counter())
    elapsed = time.perf_counter() - begin
    for _ in range(workers):
        q.put(stop)
    for t in pool[:-1]:
        t.join()
    finished.set()
    pool[-1].join()
    lam = len(latencies) / elapsed
    w = sum(latencies) / len(latencies)
    return lam, w, sum(samples) / len(samples)


print(f"{'offered/s':>9} {'workers':>8} {'lambda/s':>9} {'W ms':>7} {'L sampled':>10} {'lambda x W':>11}")
for rate, workers in [(50, 2), (120, 2), (120, 4), (150, 2), (165, 2)]:
    lam, w, l = run(rate, 0.01, workers)
    print(f"{rate:>9} {workers:>8} {lam:>9.0f} {w * 1e3:>7.1f} {l:>10.2f} {lam * w:>11.2f}")
```

<!-- measured -->

```text
offered/s  workers  lambda/s    W ms  L sampled  lambda x W
       50        2        52    12.5       0.64        0.65
      120        2       126    22.9       2.86        2.88
      120        4       126    11.9       1.51        1.49
      150        2       154    34.3       5.27        5.30
      165        2       169    52.4       8.67        8.86
```

`λW` matches the sampled `L` to within about 2%, even with random arrivals. It's a very practical law. If a service handles 20 requests a second that take 3 seconds each, you have 60 in flight on average, and a pool of 10 connections will queue. If you can see `L` and `λ` but not `W`, you can compute it. Comparing the rows shows something else. Rows two and three have the same arrival rate, and doubling the workers halves the time in the system, because queueing goes away and `W` is left at about 12 ms, what a nominal 10 ms sleep really takes here. So two workers can do about 165 a second. On those two workers, going from 52 to 169 a second, roughly a third of capacity to nearly all of it, multiplies `W` by four with no change in the work. Latency doesn't rise evenly with load: most of the rise comes in the last stretch.

## Backpressure: bounding what's in flight

If producers outrun consumers and the queue has no bound, the difference goes to memory:

```python
import queue
import threading
import time


def pipeline(capacity, items=2_000, consume_every=0.0002):
    q = queue.Queue(maxsize=capacity)
    peak = 0
    done = threading.Event()

    def consumer():
        while (x := q.get()) is not None:
            time.sleep(consume_every)
        done.set()

    threading.Thread(target=consumer).start()
    start = time.perf_counter()
    for _ in range(items):
        q.put(bytes(100_000))
        peak = max(peak, q.qsize())
    produce_time = time.perf_counter() - start
    q.put(None)
    done.wait()
    return peak, produce_time, time.perf_counter() - start


for capacity in (0, 16):
    peak, produced, total = pipeline(capacity)
    label = "unbounded" if capacity == 0 else f"bound {capacity}"
    print(f"{label:<10} peak queue {peak:>5} items = {peak * 100_000 / 1e6:6.1f} MB   producer done {produced:5.2f} s   all done {total:5.2f} s")
```

<!-- measured -->

```text
unbounded  peak queue  2000 items =  200.0 MB   producer done  0.00 s   all done  0.52 s
bound 16   peak queue    16 items =    1.6 MB   producer done  0.51 s   all done  0.52 s
```

Both finish in 0.52 s, since the consumer's rate decides the total. But the unbounded pipeline holds 200 MB while the bounded one holds 1.6 MB. A bound does its work by making the producer wait, as the 0.51 s "producer done" shows. So the wait moves to the producer, where it can spread back to whatever is feeding it. That's called backpressure. Without it, the only signal of overload is running out of memory. If you can't afford for the producer to wait, then you need to drop or reject work, using `put_nowait` and handling `queue.Full`. The choice between waiting and rejecting has to be made on purpose. A default `queue.Queue()` has quietly made that choice by having no bound at all.

## What parallelism buys

More cores help only with work that can run in parallel, and only if your runtime lets it. Here's a pure Python CPU task on the GIL build:

```python
import multiprocessing as mp
import os
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def pure(n):
    total = 0
    for i in range(n):
        total += i * i
    return total


def timed(pool_type, workers, f, n):
    start = time.perf_counter()
    if pool_type is None:
        [f(n) for _ in range(8)]
    else:
        with pool_type(workers) as pool:
            list(pool.map(f, [n] * 8))
    return time.perf_counter() - start


if __name__ == "__main__":
    print("cpus:", os.cpu_count(), " start method:", mp.get_start_method())
    base = timed(None, 1, pure, 6_000_000)
    print(f"serial, pure Python          {base:6.2f} s")
    for label, pool, f, n in [
        ("threads, pure Python", ThreadPoolExecutor, pure, 6_000_000),
        ("processes, pure Python", ProcessPoolExecutor, pure, 6_000_000),
    ]:
        t = timed(pool, 8, f, n)
        print(f"{label:<28} {t:6.2f} s   {base / t:5.2f}x")
```

<!-- measured -->

```text
cpus: 12  start method: spawn
serial, pure Python            1.12 s
threads, pure Python           1.16 s    0.97x
processes, pure Python         0.24 s    4.65x
```

Threads give 0.97 times the speed, so nothing, because the GIL lets only one run at a time. Processes give 4.65x on 8 workers. That shortfall from 8 is Amdahl's point. [His 1967 paper](https://www3.cs.stonybrook.edu/~rezaul/Spring-2012/CSE613/reading/Amdahl-1967.pdf) argues in prose that the housekeeping parts of a program put a ceiling on what parallel hardware can do. The paper doesn't include the formula that now carries his name, which is just algebra on that argument. If a fraction `s` must run serially, the speedup with `n` workers is `1 / (s + (1 - s) / n)`, and it can't pass `1 / s`, however many workers you add.

Ideally this work takes 1.12 / 8 = 0.14 s, and measured it's 0.24 s, so roughly 0.10 s went on starting 8 interpreters and passing work to them. That's consistent with the 32 ms spawn cost above if they overlap, though I didn't break it down further. It also means that the speedup would look much better for long tasks and much worse for short ones. Don't send a 1 ms task to a process pool one at a time: it'll spend most of its time on overhead.

So the rule is this. For waiting on network or disk, use threads or `asyncio`, since the GIL is released while waiting, and they cost little. For pure Python CPU work, use processes, with big enough tasks. For numeric work, use a library that releases the GIL or vectorise, as [chapter 4](04-numbers-and-memory.md#the-layout-decides-the-constant) shows. The [Python chapter](../../python/03-language-for-engineers/notes/07-concurrency.md) has more on that choice.

## Pitfalls

- **A blocking call in an event loop.** Symptom: all requests' latency spikes together, and the CPU looks idle.
- **Assuming the GIL makes `+=` atomic.** Symptom: it's fine for years, then miscounts after moving to free-threaded Python.
- **Locks taken in different orders.** Symptom: a hang under load with no CPU use and no error. Dump thread stacks with `faulthandler`.
- **Forking with threads running.** Symptom: an occasional deadlock in a child process, since a lock was copied while held.
- **Unbounded queues.** Symptom: memory climbs under load, then the process is killed, with latency worsening the whole time.
- **Tiny tasks in a process pool.** Symptom: slower than serial, and all cores busy.
- **Busy-waiting.** Symptom: one core pinned, doing nothing visible in a profile but a loop.
- **Flushing logs per line in a hot path.** Symptom: a syscall per record, and a slow job. Or, not flushing: no log lines from the last seconds before a crash.

## Try it

1. A worker pool handles 40 requests a second, and the p50 is 250 ms with little variance. Roughly how many requests are in flight, and how many workers do you need?
2. Using the Amdahl formula and the measured 4.65x on 8 workers, what serial fraction does this imply? What's the ceiling?
3. Make the producer in the backpressure block reject work rather than wait, and count the rejections.
4. In the event loop block, change the slow handler so that it doesn't stop the others, without adding a thread. What does the handler have to do in place of sleeping?

<details>
<summary>Answers</summary>

1. `L = λW = 40 × 0.25 = 10` in flight on average, so more than 10 workers, since at exactly 10 they'd be 100% busy and the queue would grow. Allow headroom for bursts, and rerun the block with your numbers to see how `W` responds.
2. `1 / 4.65 = 0.215 = s + (1 - s) / 8`, so `s` is about 0.10, and the ceiling is about 10x. Here that "serial" part is mostly startup, so it's not a property of the task. Longer tasks would imply a smaller `s`.
3. Replace `q.put(item)` with `try: q.put_nowait(item)`, and `except queue.Full: rejected += 1`. I ran this: 1,984 of the 2,000 items were rejected, because the producer finishes before the consumer has taken more than a few. So the queue length is the wrong knob if you meant to serve them. You need more consumers.
4. It records when it's due, such as `ready_at = now + 0.2`, and returns to the loop. The loop computes its `select` timeout from the soonest due time and then sends the reply. That's the state management OSTEP describes, and it's what `await asyncio.sleep` does for you.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| Process or thread: what's the difference? | A process has its own address space. Threads in a process share memory and have separate stacks. |
| What's a system call? | A trap into the kernel to do something privileged. Costlier than a function call and much cheaper than a context switch to another process. |
| What does `fork` do, and why is `spawn` the default now? | `fork` copies the process, including held locks but only the calling thread, which is unsafe with threads. `spawn` starts a new interpreter. |
| What's a race condition? | A result that depends on timing, usually from an unprotected read-modify-write. |
| Does the GIL make `+=` safe? | No. It's not atomic. It often happens to work, and fails outright on the free-threaded build. |
| How do you prevent deadlock? | Take locks in one global order, which breaks circular wait. Add timeouts so a hang becomes an error. |
| Polling or blocking? | Blocking gets the same response with no CPU. Polling is only worth it for very short waits. |
| How does an event loop work, and what breaks it? | One thread asks the kernel which sockets are ready and handles those. Any blocking call stops every client. |
| What's Little's law? | `L = λW`: in flight = arrival rate × time in system. |
| What's backpressure? | A bound that makes producers wait or reject, so overload doesn't turn into unbounded memory. |
| What's Amdahl's law? | Serial fraction `s` caps speedup at `1/s`. |
| Threads or processes for CPU work in Python? | Processes on the GIL build. Threads for I/O. |

## Next

[6 — Networks](06-networks.md): what's on the other end of those sockets, and where the time goes on a real request.
