---
origin: synthesis
sources:
  - "Google SRE Book, Embracing Risk — https://sre.google/sre-book/embracing-risk/"
  - "Google SRE Book, Service Level Objectives — https://sre.google/sre-book/service-level-objectives/"
concepts: [back-of-envelope-estimation, peak-factor, queueing-utilisation, erlang-c, m-m-c-queue, statistical-multiplexing, availability-nines, error-budget, series-availability, amdahl-law, read-replica-scaling, sharding, hot-key-limit, closed-loop-load-test]
confidence: high
cleaned: 2026-11-02
---
# 5 — Estimation and scaling

> A server at 95% utilisation makes requests wait ten times as long as one at 80%, and adding capacity only looks wasteful until you compute that curve. This chapter turns traffic assumptions into machine counts with code you can rerun, measures what operations cost on this laptop, and works out where each scaling step stops helping.

---

## An estimate is a program

An estimate exists to decide something: whether one database is enough, whether the data fits on one machine, whether a design is off by a factor of a hundred. It doesn't need to be accurate; it needs to show its assumptions, so that someone can argue with them. Writing it as a short program makes both easier, because changing one assumption reruns the rest, and arithmetic slips disappear.

Every input here is an assumption about a made-up photo-sharing service.

```python
import math

DAY = 86_400
GB, TB, PB = 1e9, 1e12, 1e15


def size(bytes_):
    for unit, name in ((PB, "PB"), (TB, "TB"), (GB, "GB"), (1e6, "MB")):
        if bytes_ >= unit:
            return f"{bytes_ / unit:.1f} {name}"
    return f"{bytes_:.0f} B"


# Every input below is an assumption for a made-up photo-sharing service. Change them and rerun.
users = 10_000_000          # daily active users
reads_per_user = 30         # feed or photo reads a day
uploads_per_user = 0.2      # a fifth of users upload one photo a day
peak_factor = 3             # peak hour against the daily average
photo_bytes = 2_000_000     # stored size of one photo
meta_bytes = 500            # database row per photo
years, copies = 5, 3

read_avg = users * reads_per_user / DAY
write_avg = users * uploads_per_user / DAY
print(f"reads    {read_avg:9,.0f}/s average {read_avg * peak_factor:9,.0f}/s peak")
print(f"uploads  {write_avg:9,.1f}/s average {write_avg * peak_factor:9,.1f}/s peak")
print(f"ratio    {read_avg / write_avg:9.0f} reads per upload")

per_day = users * uploads_per_user * photo_bytes
print(f"photos   {size(per_day)}/day, {size(per_day * 365 * years * copies)} over {years} years with {copies} copies")
print(f"rows     {size(users * uploads_per_user * meta_bytes * 365 * years)} of metadata over {years} years")

egress = read_avg * peak_factor * 200_000     # reads fetch a 200 kB thumbnail
print(f"egress   {egress * 8 / 1e9:.0f} Gbit/s at peak with 200 kB per read")

per_core = 500                                # requests/s one core handles at 2 ms of CPU each
peak = read_avg * peak_factor
cores = peak / per_core
print(f"compute  {cores:.0f} cores at 2 ms CPU each, {math.ceil(cores / 0.5)} at a 50% utilisation target")

hot = 0.2 * users * reads_per_user * 1_000    # hold the 20% most-read items at 1 kB each, one day of reads
print(f"cache    {size(hot)} for one day's most-read 20% at 1 kB per read")
```

```text
reads        3,472/s average    10,417/s peak
uploads       23.1/s average      69.4/s peak
ratio          150 reads per upload
photos   4.0 TB/day, 21.9 PB over 5 years with 3 copies
rows     1.8 TB of metadata over 5 years
egress   17 Gbit/s at peak with 200 kB per read
compute  21 cores at 2 ms CPU each, 42 at a 50% utilisation target
cache    60.0 GB for one day's most-read 20% at 1 kB per read
```

Six things to read from that result, none of them about the exact values.

- **Reads dominate by 150 to 1.** That points to caching and replicas for reads, and suggests writes aren't the first problem.
- **Peak, not average.** Machines must handle 10,417 reads per second, and 3,472 would be the wrong number to size for. The factor of 3 is an assumption here; replace it with your own traffic's peak-to-mean ratio as soon as you have one.
- **The photos decide the storage design.** 21.9 PB can't live in the database, while the 1.8 TB of metadata can fit on [one good Postgres box](../../../data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store.md#when-postgres-is-enough). This one split, objects in an object store and metadata in a database, comes straight out of the arithmetic.
- **Egress at 17 Gbit/s** means a CDN. It is also the line that tends to dominate the bill.
- **Compute is modest.** 42 cores at 50% target utilisation is a handful of machines. Teams often reach for many more on instinct.
- **Cache size follows from what you want cached.** 60 GB holds the most-read 20% for a day, which is one machine. [Chapter 3's Zipf curve](03-caching-and-queues.md#what-a-cache-buys-measured) shows why a small fraction goes a long way, if your traffic is similarly skewed.

The 2 ms of CPU per request is another assumption, and it's the weakest. Measuring it is better than assuming it.

## What things cost, on this machine

Published latency tables go out of date and were measured on somebody else's hardware. It's more useful to get figures you can reproduce. These were measured on an Apple M4 Pro with CPython 3.14. The tables report p50 and p99, the latency that 50% and 99% of requests beat; [chapter 7](07-reliability-under-load.md#measuring-percentiles-and-histograms) says why the p99 is the number to watch.

```python
import fcntl, json, os, sqlite3, tempfile, time
import http.server, threading, http.client, socket


def timed(label, fn, n):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    per = (time.perf_counter() - start) / n
    print(f"{label:44}{per * 1e6:12,.1f} us")


obj = {"id": 12345, "user": "alice", "items": list(range(20)), "ok": True}
text = json.dumps(obj)
timed("json.loads, 100-byte object", lambda: json.loads(text), 100_000)

db = sqlite3.connect(":memory:")
db.execute("create table t(id integer primary key, v text)")
db.executemany("insert into t values (?, ?)", ((i, "x" * 100) for i in range(100_000)))
timed("SQLite point read, in memory", lambda: db.execute("select v from t where id = 5000").fetchone(), 100_000)

with tempfile.TemporaryDirectory() as tmp:
    fd = os.open(os.path.join(tmp, "f"), os.O_WRONLY | os.O_CREAT)

    def durable_write():
        os.write(fd, b"x" * 4096)
        os.fsync(fd)

    def full_flush_write():
        os.write(fd, b"x" * 4096)
        fcntl.fcntl(fd, fcntl.F_FULLFSYNC)   # macOS: fsync alone leaves data in the drive's cache

    timed("4 kB write + fsync, local SSD", durable_write, 2_000)
    if hasattr(fcntl, "F_FULLFSYNC"):
        timed("4 kB write + F_FULLFSYNC, local SSD", full_flush_write, 500)
    os.close(fd)


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        body = b'{"ok": true}'
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
port = server.server_address[1]

a, b = socket.socketpair()


def ping():
    a.send(b"x")
    b.recv(1)


timed("one byte through a local socket pair", ping, 100_000)


def fresh():
    c = http.client.HTTPConnection("127.0.0.1", port)
    c.request("GET", "/")
    c.getresponse().read()
    c.close()


timed("HTTP GET on loopback, new connection", fresh, 2_000)
keep = http.client.HTTPConnection("127.0.0.1", port)
keep.connect()
keep.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


def reused():
    keep.request("GET", "/")
    keep.getresponse().read()


timed("HTTP GET on loopback, reused connection", reused, 5_000)


def load(workers, seconds=2.0):
    latencies, lock = [], threading.Lock()
    stop = time.perf_counter() + seconds

    def client():
        c = http.client.HTTPConnection("127.0.0.1", port)
        c.connect()
        c.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        mine = []
        while time.perf_counter() < stop:
            t = time.perf_counter()
            c.request("GET", "/")
            c.getresponse().read()
            mine.append(time.perf_counter() - t)
        with lock:
            latencies.extend(mine)

    pool = [threading.Thread(target=client) for _ in range(workers)]
    [t.start() for t in pool]
    [t.join() for t in pool]
    latencies.sort()
    return len(latencies) / seconds, latencies[len(latencies) // 2], latencies[int(len(latencies) * 0.99)]


print("\nThreadingHTTPServer, one Python process for client and server")
print(f"{'clients':>8}{'req/s':>10}{'p50 ms':>9}{'p99 ms':>9}")
for workers in (1, 4, 16, 64):
    rate, p50, p99 = load(workers)
    print(f"{workers:8}{rate:10,.0f}{p50 * 1000:9.2f}{p99 * 1000:9.2f}")
```

<!-- measured -->

```text
json.loads, 100-byte object                          1.3 us
SQLite point read, in memory                         0.6 us
4 kB write + fsync, local SSD                       35.9 us
4 kB write + F_FULLFSYNC, local SSD              3,505.3 us
one byte through a local socket pair                 0.6 us
HTTP GET on loopback, new connection               162.0 us
HTTP GET on loopback, reused connection             58.2 us

ThreadingHTTPServer, one Python process for client and server
 clients     req/s   p50 ms   p99 ms
       1    16,620     0.06     0.10
       4    15,394     0.24     0.59
      16    14,870     0.93     3.07
      64    14,465     3.64    13.25
```

Note the orders of magnitude, since those carry over to other machines, while the exact values don't:

- A parse or an in-memory lookup is about a microsecond.
- A loopback HTTP request costs about 50 times that. Real networks add [a round trip per hop and more for a cold connection](../../computer-science/notes/06-networks.md#a-budget-for-a-cold-request). A reused connection is about three times cheaper here even with no TLS, which is [why you pool](../../../data-engineering/05-quality-and-observability/notes/05-operating-data-stores.md#connections-why-you-pool).
- A durable write depends entirely on what "durable" means. Here `fsync` takes 36 µs, and a flush that really reaches the drive takes about 3.5 ms. [Persistence](../../../data-engineering/01-storage-and-compute-foundations/notes/09-persistence.md#fsync-what-a-power-cut-takes-and-what-it-costs) explains that macOS-specific gap. At 3.5 ms, one disk commits about 285 separate transactions a second, which is why databases batch commits.

The load test is a useful warning about method. Client and server share one Python process and one interpreter lock, so 15,000 requests a second describes this script, not a production server. The shape is what generalises. This is a *closed-loop* test, where each client waits for its reply before sending again. Past saturation, throughput stays flat and only latency grows, and the numbers satisfy [Little's law](../../computer-science/notes/05-processes-threads-and-io.md#queues-littles-law): 64 clients divided by 14,465 requests per second is 4.4 ms, a little above the 3.64 ms median, as you'd expect with a long tail. A closed-loop test also understates overload, since slow servers slow the clients down. Real users arriving independently keep arriving, and that is what the next section models.

## Why utilisation has a knee

How busy can you run a server? The answer comes from queueing theory, and the standard model is M/M/c: random arrivals, random service times, *c* workers sharing one queue. The Erlang C formula gives the chance an arrival must wait. I check the formula against a seeded simulation, so that you needn't take it on trust.

```text
 total
 latency (ms)
   70 |                                        *
   60 |
   50 |
   40 |                                    *
   30 |
   20 |                               *
   10 | *      *       *        *
      +--------------------------------------------
        50%   70%     80%      90%   95%  98%  99%   utilisation
```

```python
import heapq, math, random


def erlang_c(servers, offered):
    """Probability an arrival has to wait in M/M/c, where offered = arrival rate x service time."""
    if offered >= servers:
        return 1.0
    b = 1.0
    for k in range(1, servers + 1):           # the Erlang B recurrence, stable for large c
        b = offered * b / (k + offered * b)
    rho = offered / servers
    return b / (1 - rho + rho * b)


def wait(servers, arrival, service):
    offered = arrival * service
    return erlang_c(servers, offered) * service / (servers - offered)


def simulate(servers, arrival, service, n=400_000, seed=2):
    rng = random.Random(seed)
    free, now, total = [0.0] * servers, 0.0, 0.0
    heapq.heapify(free)
    for _ in range(n):
        now += rng.expovariate(arrival)
        start = max(now, heapq.heappop(free))
        total += start - now
        heapq.heappush(free, start + rng.expovariate(1 / service))
    return total / n


SERVICE, C = 0.010, 16                        # 10 ms per request on 16 workers
print(f"{C} workers, 10 ms mean service. Formula against simulation:")
print(f"{'load':>6}{'req/s':>8}{'P(wait)':>9}{'wait ms':>9}{'sim ms':>8}{'total ms':>10}")
for rho in (0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99):
    rate = rho * C / SERVICE
    w = wait(C, rate, SERVICE)
    print(f"{rho:6.0%}{rate:8.0f}{erlang_c(C, rate * SERVICE):9.3f}{w * 1000:9.2f}"
          f"{simulate(C, rate, SERVICE) * 1000:8.2f}{(w + SERVICE) * 1000:10.2f}")


def size_for(arrival, service, target_wait):
    c = math.ceil(arrival * service) + 1
    while wait(c, arrival, service) > target_wait:
        c += 1
    return c


print("\nworkers needed for mean wait under 1 ms, 10 ms service:")
for rate in (100, 1_000, 10_000, 100_000):
    c = size_for(rate, SERVICE, 0.001)
    print(f"  {rate:7,} req/s -> {c:6,} workers, load {rate * SERVICE / c:.1%}")
```

```text
16 workers, 10 ms mean service. Formula against simulation:
  load   req/s  P(wait)  wait ms  sim ms  total ms
   50%     800    0.009     0.01    0.01     10.01
   70%    1120    0.130     0.27    0.26     10.27
   80%    1280    0.305     0.95    0.91     10.95
   90%    1440    0.591     3.70    3.53     13.70
   95%    1520    0.780     9.75    8.91     19.75
   98%    1568    0.908    28.39   23.16     38.39
   99%    1584    0.954    59.60   43.02     69.60

workers needed for mean wait under 1 ms, 10 ms service:
      100 req/s ->      3 workers, load 33.3%
    1,000 req/s ->     13 workers, load 76.9%
   10,000 req/s ->    106 workers, load 94.3%
  100,000 req/s ->  1,008 workers, load 99.2%
```

Formula and simulation agree closely up to 95%. They drift apart at 98–99% because the queue's swings last a very long time near saturation, so even 400,000 arrivals don't fully converge, and the formula is the better guide. Three things to carry away.

- **The knee is real and brutal.** At 80% load the wait is 0.95 ms; at 95% it is 9.75 ms, about ten times as much for 19% more traffic. A traffic spike doesn't degrade service gently.
- **The model is optimistic.** It assumes smooth random arrivals and no retries. Real services have bursts, garbage collection and correlated load. That's why people target 50–70% and not 95%, and why the target goes down as latency matters more.
- **Bigger pools run hotter.** At 100 requests a second you need 3 workers at 33% load, and at 100,000 you need 1,008 workers at 99% load for the same 1 ms mean wait. This is *statistical multiplexing*: one shared queue feeding many workers absorbs bursts better than many small queues. So don't split a pool into per-tenant fragments without a reason, because each fragment has to run colder.

The [capacity section of Operating data stores](../../../data-engineering/05-quality-and-observability/notes/05-operating-data-stores.md#capacity) applies the same logic to a database, and [Chapter 7](07-reliability-under-load.md) shows what happens past the knee when clients retry.

## Availability is arithmetic too

A target converts directly into time and into a count of failed requests, and the [SRE book's Embracing Risk chapter](https://sre.google/sre-book/embracing-risk/) uses both forms: 99.99% is 52.56 minutes a year, and in a system serving 2.5 million requests a day, a 99.99% target allows 250 errors. The gap between the target and 100% is the *error budget*, the amount of failure you've agreed to accept. Outages use it up too, and what's left decides whether releases continue. [SLOs](https://sre.google/sre-book/service-level-objectives/) are covered in [chapter 7](07-reliability-under-load.md).

```python
MINUTES_A_YEAR = 365 * 24 * 60

print("target     downtime/year   downtime/30 days   errors per 10M requests")
for nines in (0.99, 0.999, 0.9995, 0.9999, 0.99999):
    budget = 1 - nines
    print(f"{nines:<8.3%}  {budget * MINUTES_A_YEAR:9.2f} min   {budget * 30 * 1440:11.2f} min   {budget * 10_000_000:12,.0f}")


def series(*parts):
    product = 1.0
    for p in parts:
        product *= p
    return product


def parallel(p, copies):
    return 1 - (1 - p) ** copies


print("\nfive 99.9% dependencies all required :", f"{series(*[0.999] * 5):.3%}")
print("twenty 99.9% dependencies all required:", f"{series(*[0.999] * 20):.3%}")
print("two independent 99% copies            :", f"{parallel(0.99, 2):.3%}")
print("three independent 99% copies          :", f"{parallel(0.99, 3):.4%}")
# Copies share failures. If 10% of a copy's failures hit every copy (bad deploy, shared config):
fail, shared = 0.01, 0.10
print("two copies, 10% of failures are shared:", f"{1 - (fail * shared + (fail * (1 - shared)) ** 2):.3%}")
```

```text
target     downtime/year   downtime/30 days   errors per 10M requests
99.000%     5256.00 min        432.00 min        100,000
99.900%      525.60 min         43.20 min         10,000
99.950%      262.80 min         21.60 min          5,000
99.990%       52.56 min          4.32 min          1,000
99.999%        5.26 min          0.43 min            100

five 99.9% dependencies all required : 99.501%
twenty 99.9% dependencies all required: 98.019%
two independent 99% copies            : 99.990%
three independent 99% copies          : 99.9999%
two copies, 10% of failures are shared: 99.892%
```

Two of these are worth remembering. Dependencies you require multiply, so twenty at 99.9% give 98%, which is about 170 hours a year. Your own service cannot be more available than the product of what it hard-depends on. So decide per dependency whether you can degrade when it's gone. Copies multiply the *unavailability*, which looks spectacular until you add reality. Two 99% copies should give 99.99%, but if just 10% of failures hit both (the same bad deploy, the same config push, the same DNS) you get 99.89%. The shared failures dominate. Spending on independence of failure usually beats spending on more copies.

## The ladder of scaling steps

Most services should climb these one at a time, since each step adds failure modes you then have to run.

| Step | Fixes | Stops helping when | Costs you |
|---|---|---|---|
| Bigger machine | Everything, for a while | The biggest machine isn't enough | A restart, and a single point of failure |
| Stateless app tier behind a [balancer](04-load-balancing-and-rate-limiting.md) | CPU in the app | The database saturates | Sessions and files have to move out |
| [Connection pool](../../../data-engineering/05-quality-and-observability/notes/05-operating-data-stores.md#connections-why-you-pool) | Connection exhaustion | Queries themselves are too slow | One more component |
| Indexes and query fixes | Slow queries | The working set outgrows memory | Slower writes |
| [Cache](03-caching-and-queues.md) | Repeated reads | Traffic stops being skewed | Staleness, and the cold-start risk |
| Read replicas | Read volume | Writes saturate the primary | [Replica lag](../../../data-engineering/05-quality-and-observability/notes/05-operating-data-stores.md#replica-lag) reaches users |
| [Queue](03-caching-and-queues.md#queues-give-you-at-least-once) | Spikes, slow work | Average arrivals exceed consumers | Duplicates, eventual results |
| [Sharding](../../../data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication.md#range-and-hash-partitioning) | Write volume, data size | Hot keys and cross-shard work | Everything gets harder |

The limits on these steps can be computed. A serial fraction caps any parallel speedup, a replica still applies every write, and one hot key caps a whole sharded cluster.

```python
def amdahl(serial, workers):
    return 1 / (serial + (1 - serial) / workers)


print("Amdahl: speedup on N workers given the fraction of work that is serial")
print(f"{'serial':>8}" + "".join(f"{n:>8}" for n in (2, 8, 32, 128, 1024)))
for serial in (0.0, 0.01, 0.05, 0.20):
    print(f"{serial:8.0%}" + "".join(f"{amdahl(serial, n):8.1f}" for n in (2, 8, 32, 128, 1024)))

# Hypothetical database: a node can do 10,000 operations a second.
NODE = 10_000
print("\nread replicas, one primary, 10,000 ops/s per node")
print(f"{'read share':>11}{'replicas':>10}{'total ops/s':>13}{'writes/s':>10}")
for reads in (0.5, 0.9, 0.99):
    for replicas in (0, 2, 8):
        writes = 1 - reads
        # Every node must apply every write; reads spread over all nodes.
        # Solve total*writes + total*reads/(1+replicas) = NODE on the busiest node.
        total = NODE / (writes + reads / (1 + replicas))
        print(f"{reads:11.0%}{replicas:10}{total:13,.0f}{total * writes:10,.0f}")

print("\nsharding: one key gets 5% of traffic, limit 10,000 ops/s per shard")
for shards in (1, 4, 16, 64, 256):
    # The hot key's shard takes the hot share plus an even slice of the rest.
    busiest_share = 0.05 + 0.95 / shards
    print(f"  {shards:4} shards  max total {NODE / busiest_share:9,.0f} ops/s, even-spread would allow {NODE * shards:9,}")
```

```text
Amdahl: speedup on N workers given the fraction of work that is serial
  serial       2       8      32     128    1024
      0%     2.0     8.0    32.0   128.0  1024.0
      1%     2.0     7.5    24.4    56.4    91.2
      5%     1.9     5.9    12.5    17.4    19.6
     20%     1.7     3.3     4.4     4.8     5.0

read replicas, one primary, 10,000 ops/s per node
 read share  replicas  total ops/s  writes/s
        50%         0       10,000     5,000
        50%         2       15,000     7,500
        50%         8       18,000     9,000
        90%         0       10,000     1,000
        90%         2       25,000     2,500
        90%         8       50,000     5,000
        99%         0       10,000       100
        99%         2       29,412       294
        99%         8       83,333       833

sharding: one key gets 5% of traffic, limit 10,000 ops/s per shard
     1 shards  max total    10,000 ops/s, even-spread would allow    10,000
     4 shards  max total    34,783 ops/s, even-spread would allow    40,000
    16 shards  max total    91,429 ops/s, even-spread would allow   160,000
    64 shards  max total   154,217 ops/s, even-spread would allow   640,000
   256 shards  max total   186,182 ops/s, even-spread would allow 2,560,000
```

- **Amdahl's law.** With 5% of the work serial, such as a lock or one shared row, no number of workers gets you past 20×, and 128 workers yield only 17. When adding servers stops helping, look for [the shared thing](../../computer-science/notes/05-processes-threads-and-io.md#what-a-lock-costs).
- **Replicas.** At 99% reads, 8 replicas multiply capacity by more than eight, and the writes rise only because the mix does. At 50% reads the gain is under 2×, because every replica spends its capacity applying writes. Replicas are for read-heavy workloads, and they'd also return [stale data](../../../data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication.md#what-lag-looks-like).
- **Sharding.** One key with 5% of traffic caps the cluster, whatever the shard count: past some point, more shards do nothing, and 256 shards give 186,182 operations a second against an even-spread 2.56 million. The limit is 200,000, which is 10,000 divided by 0.05. Handling [hot keys](../../../data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication.md#hot-keys) takes a cache or a split of that key.

The replica and shard numbers are for an invented 10,000 ops/s node with a simplified cost model (a write costs the same as a read everywhere), so use the formula and not the figures.

## Pitfalls

- **Sizing to the average.** Traffic has peaks. Size for the peak plus failure of the largest unit.
- **False precision.** Three significant figures on a guess mislead. State the assumption, and round the answer.
- **Forgetting replication and overhead in storage.** Copies, indexes and backups are often several times the raw size.
- **Planning at 100% utilisation.** The queueing curve says you'll be in trouble long before that.
- **Averages in a capacity plan.** Latency at the knee is about the tail. See [chapter 7](07-reliability-under-load.md).
- **Trusting a closed-loop benchmark.** It slows down its own clients, so it can hide overload. Note the setup when quoting numbers.
- **Assuming independent failure.** Copies in the same deploy share many failures. Multiplying probabilities overstates reliability.
- **Sharding too early.** It's very hard to undo, and bigger machines and replicas carry many services a long way. See [when Postgres is enough](../../../data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store.md#when-postgres-is-enough).
- **Ignoring the failure case in N.** If you need 10 machines, losing one must still leave 10. [Region loss](07-reliability-under-load.md#losing-a-region) raises this further.

## Try it

**1. Size a worker pool.** Do `erlang.py` in the [lab](../practice/README.md): the Erlang C probability, the mean wait and the smallest worker count for a target. Run `cd practice/exercises/backend_lab && uv run pytest test_erlang.py`.

<details>
<summary>Answer</summary>

Worked code is in [`solutions/backend_lab/erlang.py`](../practice/solutions/backend_lab/erlang.py). Use the Erlang B recurrence: computing `c!` and `a^c` directly overflows for large pools, while the recurrence stays between 0 and 1. Handle `offered >= servers` explicitly, since the queue then has no steady state.

</details>

**2. Compute it.** Hypothetical chat service: 5 million daily users, each sending 40 messages a day at 300 bytes, with a peak factor of 4. Each message is stored for a year and fans out to an average of 3 recipients. Give peak writes per second, peak deliveries per second, and yearly storage before replication.

<details>
<summary>Answer</summary>

```python
users, msgs, size, peak, fanout = 5_000_000, 40, 300, 4, 3
per_day = users * msgs
peak_writes = per_day / 86_400 * peak
print(round(peak_writes), round(peak_writes * fanout), per_day * size * 365 / 1e12)
```

```text
9259 27778 21.9
```

About 9,300 writes per second, 28,000 deliveries per second, and 22 TB a year. That storage fits on one big machine, and the fan-out is what deserves the design attention.

</details>

**3. A service runs 8 workers at 75% utilisation, 20 ms per request. Traffic grows 25%. Using the code above, what happens to the mean wait, and how many workers bring it back?**

<details>
<summary>Answer</summary>

Offered load goes from 6 to 7.5 erlangs, so utilisation becomes 93.75%. The formula gives a mean wait of about 3.6 ms before and about 32 ms after (`wait(8, 300, 0.02)` and `wait(8, 375, 0.02)` from the code above). A 25% traffic rise makes the wait nine times as long. `size_for(375, 0.02, wait(8, 300, 0.02))` returns 10 workers, with a wait of about 2.5 ms; 9 workers would still wait 6.8 ms.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| How do you start an estimate? | State the assumptions, then users to average rate, a peak factor, sizes, retention, copies. Use it to make a decision. |
| Peak or average? | Peak, plus the failure of your largest unit. |
| Why not run at 95% utilisation? | Waiting grows like 1/(1 − ρ). In the 16-worker example, the wait at 95% is about ten times that at 80%. |
| How do you turn QPS into machines? | QPS × CPU per request, divided by a target utilisation, then rounded up for failure. |
| Little's law? | In-flight = arrival rate × latency. |
| Why do bigger pools tolerate higher utilisation? | One shared queue absorbs bursts: statistical multiplexing. |
| What is 99.99% in minutes? | 52.56 per year, 4.32 per 30 days. |
| What do twenty 99.9% dependencies give? | About 98%, since required dependencies multiply. |
| Replica or shard? | Replica for read volume, shard for write volume or data size. Shard last. |
| What limits sharding? | Hot keys and cross-shard work. A key with fraction *f* caps the cluster at node capacity / *f*. |
| What does Amdahl's law say? | Speedup is capped at 1 / (serial fraction). |

## Next

You know how much capacity you need. [Chapter 6 — Containers, CI/CD and deployment](06-containers-cicd-and-deployment.md) packages the code and changes it safely while traffic runs.
