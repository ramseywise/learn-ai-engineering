---
origin: synthesis
sources:
  - "Mitzenmacher, The Power of Two Choices in Randomized Load Balancing (IEEE TPDS 2001) — https://www.eecs.harvard.edu/~michaelm/postscripts/tpds2001.pdf"
  - "Karger et al., Consistent Hashing and Random Trees (STOC 1997) — https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf"
  - "Eisenbud et al., Maglev: A Fast and Reliable Software Network Load Balancer (NSDI 2016) — https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/44824.pdf"
  - "DeCandia et al., Dynamo (SOSP 2007) — https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf"
  - "Envoy docs, Supported load balancers — https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers"
  - "NGINX docs, Using nginx as HTTP load balancer — https://nginx.org/en/docs/http/load_balancing.html"
  - "Google SRE Book, Load Balancing in the Datacenter — https://sre.google/sre-book/load-balancing-datacenter/"
  - "Cloudflare blog, How we built rate limiting capable of scaling to millions of domains — https://blog.cloudflare.com/counting-things-a-lot-of-different-things/"
  - "Redis docs, INCR rate limiter patterns — https://redis.io/docs/latest/commands/incr/"
  - "RFC 6585, Additional HTTP Status Codes — https://www.rfc-editor.org/rfc/rfc6585"
  - "gRPC, Load balancing — https://grpc.io/blog/grpc-load-balancing/"
concepts: [load-balancing, power-of-two-choices, least-connections, round-robin, herding, consistent-hashing, virtual-nodes, maglev-hashing, lame-duck, rate-limiting, token-bucket, leaky-bucket, gcra, fixed-window, sliding-window-log, sliding-window-counter, distributed-rate-limit]
confidence: high
cleaned: 2026-11-02
---
# 4 — Load balancing and rate limiting

> A load balancer picking the least busy server can send every request to one machine and melt it, while two random picks do better. This chapter simulates the balancing policies, measures how many keys move when a node joins, and races five rate-limit algorithms against an attacker who knows the window.

---

## Where a balancer sits

A balancer takes one address and spreads requests over many servers, removing dead ones. It works at one of two levels.

| Level | Sees | Can do | Example |
|---|---|---|---|
| Layer 4 | IP, port, TCP packets | Very fast forwarding; keeps a connection on one server | [Maglev](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/44824.pdf) |
| Layer 7 | HTTP method, path, headers | Route by path, retry, terminate TLS, split traffic for a canary | [Envoy](https://grpc.io/blog/grpc-load-balancing/), [nginx](https://nginx.org/en/docs/http/load_balancing.html) |

Layer 7 needs a [parsed request and usually a TLS handshake](../../computer-science/notes/06-networks.md#tls-13-one-more-round-trip), so it costs more per request, and a common setup puts layer 4 machines in front of a layer 7 fleet. One thing to watch: if a layer 4 balancer holds a long-lived HTTP/2 or gRPC connection on one backend, every request on it goes to that backend. Balance per request at layer 7 or in the client, and the [gRPC load-balancing post](https://grpc.io/blog/grpc-load-balancing/) describes both options.

## Picking a server

[nginx](https://nginx.org/en/docs/http/load_balancing.html) offers round robin by default, `least_conn`, and `ip_hash` for stickiness. [Envoy](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers) adds *power of two choices* (P2C) when host weights are equal: pick two hosts at random and send to the one with fewer active requests. A simulation lets us compare them under the conditions they are really chosen for. The setup is invented: 50 servers, Poisson arrivals, exponential service times with mean 1, each server with its own queue.

```python
import heapq, random, statistics


def simulate(policy, servers=50, load=0.9, n=200_000, seed=11, slow=(), stale=0.0):
    """Poisson arrivals, exponential service. `slow` servers run at a quarter of the speed.
    `stale` > 0 means the balancer only learns the in-flight counts every `stale` time units."""
    rng = random.Random(seed)
    rate = load * servers
    t = 0.0
    busy_until = [0.0] * servers
    in_flight = [[] for _ in range(servers)]              # completion times per server
    latencies = []
    next_rr, known, refreshed = 0, [0] * servers, -1.0
    for _ in range(n):
        t += rng.expovariate(rate)
        for q in in_flight:
            while q and q[0] <= t:
                heapq.heappop(q)
        if t - refreshed >= stale:
            known, refreshed = [len(q) for q in in_flight], t
        if policy == "round robin":
            s = next_rr = (next_rr + 1) % servers
        elif policy == "random":
            s = rng.randrange(servers)
        elif policy == "two choices":
            a, b = rng.randrange(servers), rng.randrange(servers)
            s = a if known[a] <= known[b] else b
        else:                                              # least loaded, a scan of every server
            s = min(range(servers), key=known.__getitem__)
        service = rng.expovariate(1.0) * (4 if s in slow else 1)
        finish = max(t, busy_until[s]) + service
        busy_until[s] = finish
        heapq.heappush(in_flight[s], finish)
        latencies.append(finish - t)
    latencies.sort()
    return statistics.fmean(latencies), latencies[int(0.99 * n)]


POLICIES = ("round robin", "random", "two choices", "least loaded")
print("50 servers at 90% load, mean service time 1, single queue per server")
print(f"{'policy':14}{'mean':>8}{'p99':>8}")
for policy in POLICIES:
    mean, p99 = simulate(policy)
    print(f"{policy:14}{mean:8.2f}{p99:8.2f}")
print("the same at 60% load, with two of the 50 running at a quarter speed")
for policy in POLICIES:
    mean, p99 = simulate(policy, load=0.6, slow={0, 1})
    print(f"{policy:14}{mean:8.2f}{p99:8.2f}")
print("the same at 60% load, all servers equal, counts refreshed only once per time unit")
for policy in POLICIES:
    mean, p99 = simulate(policy, load=0.6, stale=1.0)
    print(f"{policy:14}{mean:8.2f}{p99:8.2f}")
```

```text
50 servers at 90% load, mean service time 1, single queue per server
policy            mean     p99
round robin       5.14   24.61
random            9.78   43.91
two choices       2.71    9.21
least loaded      1.17    5.21
the same at 60% load, with two of the 50 running at a quarter speed
round robin     188.18 6942.83
random          177.24 6437.94
two choices       1.59    7.79
least loaded      1.05    5.15
the same at 60% load, all servers equal, counts refreshed only once per time unit
round robin       1.50    6.98
random            2.50   11.72
two choices       1.62    6.82
least loaded     15.93   41.93
```

Three results, and each one is worth stating:

1. **At high load on identical servers, two choices is far better than one.** Random's p99 is 43.9, while P2C's is 9.2. [Mitzenmacher's analysis](https://www.eecs.harvard.edu/~michaelm/postscripts/tpds2001.pdf) explains why with the "supermarket" model: moving from one random choice to two is an exponential improvement in expected time in the system, and going from two to three only gains a constant factor. Full knowledge of every queue beats P2C, but it needs a scan of every server.
2. **A static policy has no idea a server is slow.** With two servers at a quarter speed, round robin keeps giving them 1/50 of the traffic each, which is more than they can serve, so their queues grow without limit for as long as the run lasts. The 6,900 p99 is a measure of how long the simulation ran. P2C sees the queue and steers around it. Load feedback fixes this; the cost is that a failing server that errors quickly can look idle and attract traffic, so count errors as well.
3. **Stale information breaks "least loaded".** With counts refreshed once per time unit, the policy sends every arrival in that interval to the same apparently idle server. Mean latency goes from 1.05 to 15.9, worse than a coin flip, while P2C stays close to round robin. [Envoy's docs](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers) mention this directly as P2C's resistance to herding. A real fleet has many balancers working from partial views, so this is the normal case.

LLM traffic makes this more extreme, since requests differ in cost by orders of magnitude and queue counts say little. [Serving at scale](../../../ai-engineering/07-inference-engineering/notes/06-serving-at-scale.md) covers that case.

## Taking a server out

Passive removal after failures means some requests fail first. A planned shutdown should do better. The SRE book's [datacenter load balancing chapter](https://sre.google/sre-book/load-balancing-datacenter/) describes a *lame duck* state: the task is still serving and tells its clients to stop sending new requests. It finishes what it has, then exits. That is the same sequence as a [graceful SIGTERM in chapter 6](06-containers-cicd-and-deployment.md#shutting-down-without-dropping-requests).

## Hashing keys to nodes

Sometimes the same key has to reach the same place, such as with cache shards or a partitioned store. The obvious scheme is `hash(key) % N`, and adding a node remaps nearly everything. For a cache that means a miss on nearly every key at once, which is [the stampede from chapter 3](03-caching-and-queues.md#the-stampede) at full fleet scale. [Consistent hashing](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf), from Karger and colleagues, places nodes and keys in the same range, so each key goes to a nearby node. The usual form, as in [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), is a circle where each key belongs to the next node clockwise, so only keys next to the new node move.

```text
         key k1
            \            node C
   node A ---o----------o
         |               \
         |    hash circle o  key k2 goes clockwise to node B
         |               /
         o--------------o
      key k3 -> A        node B
```

```python
import bisect, hashlib


def h(text):
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big")


class Modulo:
    def __init__(self, nodes):
        self.nodes = sorted(nodes)

    def owner(self, key):
        return self.nodes[h(key) % len(self.nodes)]


class Ring:
    def __init__(self, nodes, vnodes=1):
        self.points = sorted((h(f"{n}#{i}"), n) for n in nodes for i in range(vnodes))
        self.hashes = [p for p, _ in self.points]

    def owner(self, key):
        i = bisect.bisect(self.hashes, h(key)) % len(self.points)
        return self.points[i][1]


KEYS = [f"key-{i}" for i in range(100_000)]
TEN = [f"node-{i}" for i in range(10)]
ELEVEN = TEN + ["node-10"]


def moved(a, b):
    return sum(a.owner(k) != b.owner(k) for k in KEYS) / len(KEYS)


def spread(table):
    counts = {}
    for k in KEYS:
        counts[table.owner(k)] = counts.get(table.owner(k), 0) + 1
    return max(counts.values()) / (len(KEYS) / len(counts))


print(f"add an 11th node; the ideal is {1 / 11:.1%} of keys moving")
print(f"  hash mod N          {moved(Modulo(TEN), Modulo(ELEVEN)):6.1%} moved   busiest node {spread(Modulo(TEN)):.2f}x the average")
for v in (1, 10, 100, 1000):
    print(f"  ring, {v:4} vnodes    {moved(Ring(TEN, v), Ring(ELEVEN, v)):6.1%} moved   busiest node {spread(Ring(TEN, v)):.2f}x the average")
```

```text
add an 11th node; the ideal is 9.1% of keys moving
  hash mod N           91.0% moved   busiest node 1.03x the average
  ring,    1 vnodes      8.8% moved   busiest node 3.09x the average
  ring,   10 vnodes     10.7% moved   busiest node 1.38x the average
  ring,  100 vnodes      8.4% moved   busiest node 1.18x the average
  ring, 1000 vnodes      9.2% moved   busiest node 1.05x the average
```

The ring moves about the ideal 1/11 of keys, where modulo moves 91%. But look at the last column: a single point per node is badly uneven, with the busiest node holding three times the average. Virtual nodes fix that by giving each physical node many points on the circle. Karger's construction already replicates each node; [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) calls these virtual nodes and also lets a larger machine take more of them. A thousand points gets within 5% here, at the cost of a bigger table.

[Maglev](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/44824.pdf) makes a different trade for layer 4 forwarding. It precomputes a large lookup table, prioritising very even load over minimal disruption, so slightly more keys move when backends change, and fills it from per-backend permutations. The lab's [`hash_ring.py`](../practice/solutions/backend_lab/hash_ring.py) has the ring. How partitioned data is assigned, and rebalanced, is in [partitioning and replication](../../../data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication.md#rebalancing), and the same rings return in the [KV store walkthrough](09-design-walkthroughs-kv-store-and-feed.md).

## Five ways to count requests

A rate limit protects capacity and enforces fairness: no single caller gets to spend everyone's budget. The limiters below share one interface, and the clock is passed in so a test can run ten minutes in microseconds. They're tested against the worst case for each, an attacker who knows when the window rolls over.

```python
from collections import deque


class FixedWindow:
    def __init__(self, limit, window):
        self.limit, self.window, self.current, self.count = limit, window, None, 0

    def allow(self, now):
        slot = int(now // self.window)
        if slot != self.current:
            self.current, self.count = slot, 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False


class SlidingLog:
    def __init__(self, limit, window):
        self.limit, self.window, self.log = limit, window, deque()

    def allow(self, now):
        while self.log and self.log[0] <= now - self.window:
            self.log.popleft()
        if len(self.log) < self.limit:
            self.log.append(now)
            return True
        return False


class SlidingCounter:
    """Two counters: previous window weighted by how much of it still overlaps."""

    def __init__(self, limit, window):
        self.limit, self.window, self.slot, self.previous, self.count = limit, window, None, 0, 0

    def estimate(self, now):
        into = (now % self.window) / self.window
        return self.previous * (1 - into) + self.count

    def allow(self, now):
        slot = int(now // self.window)
        if slot != self.slot:
            self.previous = self.count if self.slot == slot - 1 else 0
            self.slot, self.count = slot, 0
        if self.estimate(now) < self.limit:
            self.count += 1
            return True
        return False


class TokenBucket:
    """Holds up to `burst` tokens and refills at `rate` per second."""

    def __init__(self, rate, burst):
        self.rate, self.burst, self.tokens, self.last = rate, burst, burst, 0.0

    def allow(self, now):
        self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class Gcra:
    """A leaky bucket as a meter. Stores one number: the theoretical arrival time."""

    def __init__(self, rate, burst):
        self.interval, self.tolerance, self.tat = 1 / rate, (burst - 1) / rate, 0.0

    def allow(self, now):
        tat = max(self.tat, now)
        if tat - now <= self.tolerance:
            self.tat = tat + self.interval
            return True
        return False


LIMIT, WINDOW = 100, 60.0
make = {
    "fixed window": lambda: FixedWindow(LIMIT, WINDOW),
    "sliding log": lambda: SlidingLog(LIMIT, WINDOW),
    "sliding counter": lambda: SlidingCounter(LIMIT, WINDOW),
    "token bucket": lambda: TokenBucket(LIMIT / WINDOW, LIMIT),
    "gcra": lambda: Gcra(LIMIT / WINDOW, LIMIT),
}


def worst_60s(accepted):
    start, best = 0, 0
    for end, t in enumerate(accepted):
        while accepted[start] <= t - WINDOW:
            start += 1
        best = max(best, end - start + 1)
    return best


# An attacker who knows the window: wait until just before the boundary, then keep sending.
burst = [59.0 + i * 0.01 for i in range(400)]
# Steady traffic at three times the limit for ten minutes.
steady = [i * 0.2 for i in range(3000)]
print(f"limit: {LIMIT} per {WINDOW:.0f} s")
print(f"{'algorithm':17}{'boundary burst':>15}{'worst 60 s':>12}{'steady 300/min':>16}")
for name, factory in make.items():
    limiter = factory()
    accepted = [t for t in burst if limiter.allow(t)]
    limiter = factory()
    kept = [t for t in steady if limiter.allow(t)]
    print(f"{name:17}{len(accepted):15}{worst_60s(accepted):12}{len(kept) / 10:13.0f}/min")

# Cloudflare's worked example: 42 last minute, 18 so far, 15 seconds into this one.
estimate = 42 * ((60 - 15) / 60) + 18
print("sliding estimate, 42 then 18 at 15 s in:", estimate)
```

```text
limit: 100 per 60 s
algorithm         boundary burst  worst 60 s  steady 300/min
fixed window                 200         200          100/min
sliding log                  100         100          100/min
sliding counter              105         105          100/min
token bucket                 106         106          110/min
gcra                         106         106          110/min
sliding estimate, 42 then 18 at 15 s in: 49.5
```

Reading across each row:

| Algorithm | State per key | Boundary burst | Note |
|---|---|---|---|
| Fixed window | 1 counter | Twice the limit | Simple, but it let through 200 in about two seconds |
| Sliding log | One timestamp per request | None | Exact, and [expensive at scale](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/) |
| Sliding counter | 2 counters | Slight | A good default for "N per minute" |
| Token bucket | Tokens + time | A chosen burst | Separates the sustained rate from the allowed burst |
| GCRA (leaky bucket as a meter) | 1 timestamp | A chosen burst | The same behaviour as the bucket, with one number to store |

The token bucket shows 110 per minute in the steady column for a reason. It started full, so ten minutes of traffic got the initial 100 plus the refill of 100 per minute. If you offer a burst, it's real capacity that you need to have.

The bucket's two numbers are its strength: you can allow 100 per minute sustained and independently decide how large a burst is acceptable. Use a window counter when the contract is a plain quota. Use a bucket when traffic is legitimately bursty.

The sliding counter is an approximation, weighting the previous window by how much of it still overlaps. The last line of output reproduces [Cloudflare's worked example](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/): 42 requests last minute and 18 so far, 15 seconds in, gives 42 × 45/60 + 18 = 49.5. Cloudflare reports that on 400 million requests from 270,000 sources, 0.003% were wrongly allowed or limited, with an average 6% difference from the real rate. That approximation assumes traffic is evenly spread within the previous window, so here it is on two workloads I invented, both chosen to sit near the limit:

```python
import random

LIMIT, WINDOW = 100, 60.0


def exact(times, now):
    return sum(now - WINDOW < t <= now for t in times)


def estimated(times, now):
    slot = int(now // WINDOW)
    current = sum(int(t // WINDOW) == slot and t <= now for t in times)
    previous = sum(int(t // WINDOW) == slot - 1 for t in times)
    return previous * (1 - (now % WINDOW) / WINDOW) + current


rng = random.Random(5)
for label, generate in {
    "steady, around the limit": lambda: sorted(rng.uniform(0, 300) for _ in range(rng.randint(300, 600))),
    "bursty, on and off": lambda: sorted(t + rng.uniform(0, 8) for t in range(0, 300, 40) for _ in range(rng.randint(5, 60))),
}.items():
    wrong, checks, gap = 0, 0, 0.0
    for _ in range(2000):
        times, now = generate(), rng.uniform(120, 300)
        e, x = estimated(times, now), exact(times, now)
        checks += 1
        wrong += (e >= LIMIT) != (x >= LIMIT)
        gap += abs(e - x) / max(x, 1)
    print(f"{label:26} wrong decision {wrong / checks:6.2%}   mean count error {gap / checks:6.1%}")
```

```text
steady, around the limit   wrong decision  5.10%   mean count error   3.5%
bursty, on and off         wrong decision  2.40%   mean count error  30.0%
```

The wrong-decision rate is far higher than Cloudflare's, and that's expected, not a contradiction. Most sources in real traffic are nowhere near their limit, so the approximate and exact counts agree on the decision. These workloads are built to sit on the line. The error grows on bursty traffic, because that assumption of even spread fails. For a safety limit this is fine; don't use it for anything that bills customers.

## Sharing the count

With 20 API servers, 20 private counters allow 20 times the limit. So the count moves to a shared store, and then the danger is read, decide, write as three separate steps. SQLite stands in for the shared store here, using one file and eight threads with separate connections:

```python
import sqlite3, tempfile, threading
from pathlib import Path

LIMIT = 100


def naive(db_path, key, window):
    """Read, decide, write: three steps, with a gap that other processes can use."""
    db = sqlite3.connect(db_path, timeout=30, isolation_level=None)
    row = db.execute("select n from counter where k = ? and w = ?", (key, window)).fetchone()
    n = row[0] if row else 0
    if n >= LIMIT:
        return False
    db.execute("insert into counter values (?, ?, 1) on conflict (k, w) do update set n = ?", (key, window, n + 1))
    return True


def atomic(db_path, key, window):
    """One statement: the database decides and increments together."""
    db = sqlite3.connect(db_path, timeout=30, isolation_level=None)
    row = db.execute("""
        insert into counter values (?, ?, 1)
        on conflict (k, w) do update set n = n + 1 where n < ?
        returning n
    """, (key, window, LIMIT)).fetchone()
    return row is not None


def hammer(check, threads=8, each=100):
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "limit.db")
        db = sqlite3.connect(path, isolation_level=None)
        db.execute("pragma journal_mode=wal")
        db.execute("create table counter(k text, w int, n int, primary key (k, w))")
        accepted, lock = [0], threading.Lock()

        def worker():
            for _ in range(each):
                if check(path, "alice", 0):
                    with lock:
                        accepted[0] += 1

        pool = [threading.Thread(target=worker) for _ in range(threads)]
        [t.start() for t in pool]
        [t.join() for t in pool]
        return accepted[0]


print(f"limit {LIMIT}, 8 threads send 100 each, one shared SQLite file")
print("atomic statement accepted:", hammer(atomic))
print("read-then-write accepted, five runs:", [hammer(naive) for _ in range(5)])
```

<!-- measured -->

```text
limit 100, 8 threads send 100 each, one shared SQLite file
atomic statement accepted: 100
read-then-write accepted, five runs: [748, 722, 749, 693, 734]
```

The read-then-write version let through seven times the limit. The single statement can't, because the check and the increment happen as one step. On a real system that step belongs in the store: the [Redis `INCR` docs](https://redis.io/docs/latest/commands/incr/) give a per-second counter pattern that wraps `INCR` and `EXPIRE` in `MULTI`/`EXEC`, and note that a single-counter variant is a bit more complex to get right without race conditions. Redis isn't installed on this machine, so that pattern was read and not run. [Chapter 8](08-design-walkthroughs-rate-limiter-notifications-scheduler.md) designs the whole service around this.

A round trip per request has a cost, though. Cloudflare's design counts asynchronously and caches only the decision to block a client, which keeps the request path fast. Decide what happens when the limiter's store is down. Failing open keeps your service up while removing the protection; failing closed turns a limiter outage into a full outage. For most APIs, fail open and fall back to a coarse local limit.

Tell the client what happened. [RFC 6585 §4](https://www.rfc-editor.org/rfc/rfc6585#section-4) defines 429 with an optional `Retry-After`, and a good client waits at least that long. Rate limits are per client and protect fairness. They don't protect the server from total overload, since many clients each under their limit can still overwhelm it, which is why [load shedding](07-reliability-under-load.md) is a separate mechanism.

## Pitfalls

- **Round robin with uneven requests or servers.** It keeps feeding the slow one. Use P2C or least requests.
- **"Least connections" on stale data from many balancers.** All of them pick the same server. P2C is the fix.
- **Layer 4 balancing for HTTP/2 or gRPC.** One connection carries many streams, so one server gets everything.
- **Hash mod N for a cache tier.** Adding a node empties the cache. Use a consistent ring, with virtual nodes.
- **Using the client IP as the rate-limit key.** Many users share one address behind NAT, and an attacker can rotate addresses. Prefer the authenticated identity.
- **Trusting `X-Forwarded-For` blindly.** Clients can set it themselves. Read only the entry added by your own proxy.
- **Read-then-write counters.** They overrun under concurrency. Use one atomic operation.
- **Rate limiting by request count when costs vary.** One GraphQL query or LLM call can cost a thousand times another. Limit on cost.
- **Forgetting health checks can lie.** A shallow check passes while the dependency is down, and a deep one can take out the whole fleet at once when a shared dependency blips.

## Try it

**1. Build the limiters and a ring.** Do `limiters.py` and `hash_ring.py` in the [lab](../practice/README.md). Run `cd practice/exercises/backend_lab && uv run pytest test_limiters.py test_hash_ring.py`.

<details>
<summary>Answer</summary>

Worked code is in [`solutions/backend_lab/limiters.py`](../practice/solutions/backend_lab/limiters.py) and [`hash_ring.py`](../practice/solutions/backend_lab/hash_ring.py). The tests pass the clock in, so no test sleeps. Use a stable hash such as SHA-256: Python's `hash()` for strings changes between processes, which would make every node compute a different ring.

</details>

**2. Compute it.** With limit 100 per minute and a token bucket at rate 100/60 per second with burst 100, what is the most a client can get through in any one minute? And what would a burst of 20 change?

<details>
<summary>Answer</summary>

Starting full, it can take 100 tokens immediately plus 60 × 100/60 = 100 more refilled during that minute, so 200 at the theoretical maximum. A burst of 20 limits it to 20 + 100 = 120. So a token bucket's burst is added on top of the rate, and if your contract says "at most 100 in any minute", you have to choose the rate and burst to sum to it, or use a sliding log.

</details>

**3. Why does P2C need only a small amount of randomness to beat a full scan on stale data?**

<details>
<summary>Answer</summary>

On stale data, the full scan makes the same deterministic choice for everyone until the data refreshes, so it concentrates load. Random picks spread across different pairs and never agree on one target. The comparison still avoids clearly overloaded servers. It keeps most of the benefit of the information and throws away the coordination. Run the simulation above with `stale=1.0` and compare.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| Layer 4 or layer 7? | Layer 4 forwards fast with no view of HTTP. Layer 7 routes by content, retries and terminates TLS, at more cost. |
| Which balancing policy by default? | P2C or least requests. Round robin only for uniform requests and servers. |
| Why two random choices? | Exponential improvement over one choice, a constant factor from three, and it resists herding on stale data. |
| What is a lame duck? | A task that keeps serving and tells clients to stop sending, before a clean exit. |
| What does consistent hashing buy? | About 1/N of keys move when a node joins, against nearly all with mod N. |
| Why virtual nodes? | One point per node gives uneven arcs; many points even out load and allow weighting. |
| Token bucket or sliding window? | Bucket when you want a chosen burst; sliding counter for a plain per-minute quota. |
| What's wrong with fixed windows? | Twice the limit can pass in a moment across the boundary. |
| How do you rate limit across servers? | A shared counter with an atomic operation, or async counters with cached decisions if the round trip costs too much. |
| Limiter store down: open or closed? | Usually open with a coarse local limit; closed for high-risk paths such as login. |
| What status do you return? | 429 with `Retry-After`. |

## Next

You can now spread and bound traffic. [Chapter 5 — Estimation and scaling](05-estimation-and-scaling.md) works out how much traffic a design has to handle and how many machines that takes.
