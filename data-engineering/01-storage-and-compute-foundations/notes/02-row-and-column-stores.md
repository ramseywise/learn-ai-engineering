---
origin: book-condensed
sources:
  - "Kleppmann, Designing Data-Intensive Applications (O'Reilly, 2017), ch. 3"
  - https://doi.org/10.1145/1376616.1376712
  - https://doi.org/10.1145/3226595.3226638
  - https://doi.org/10.1145/3299869.3320212
confidence: high
cleaned: 2026-11-01
---
# 2 — Row and column stores

Ask a database for one customer's record and it wants its rows together on disk. Ask it for average fare by zone over a year and it wants the fares together and everything else out of the way. Those requests pull in opposite directions so strongly that a single storage layout cannot be good at both, and this is why almost every company keeps two kinds of database with a pipeline running between them. This chapter loads the same million trips into SQLite and DuckDB, measures the gap, and follows it down to the compression, sort orders and CPU loops that produce it.

## Two workloads

Kleppmann's distinction ([*Designing Data-Intensive Applications*](https://dataintensive.net/), ch. 3) is between transaction processing and analytics. The names come with history, but the useful part is what the access pattern looks like:

| | OLTP | OLAP |
|---|---|---|
| Reads | A few rows, found by key | Aggregates over many rows |
| Writes | Random, low latency, from user input | Bulk load or event stream |
| Used by | End users, through an application | Analysts and models |
| Data represents | The latest state | History of events |
| Typical size | Gigabytes to terabytes | Terabytes to petabytes |

The practical point is that an analyst's query can hold a production database's disks hostage. So companies copy data into a separate read-only **warehouse** through a pipeline, which is why this subject exists at all. Kimball's image for the split is that operational systems are where users turn the wheels of the organisation and the warehouse is where they watch them turn ([*The Data Warehouse Toolkit*](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/), 2nd ed., ch. 1).

The size of the gap surprises people the first time. Here are both engines on the same rows, using the same `make_trips` as the [previous chapter](01-encoding-and-files.md).

```python
import os, sqlite3, time, numpy as np, pyarrow as pa, duckdb

def make_trips(n=1_000_000, seed=7):
    """One synthetic month of taxi trips, sorted by pickup time like an append-only log."""
    rng = np.random.default_rng(seed)
    start = np.datetime64("2026-01-01T00:00:00", "s")
    seconds = np.sort(rng.integers(0, 31 * 86_400, n))
    # 260 zones with a heavy tail: a few busy zones take most pickups.
    weights = 1 / np.arange(1, 261)
    zones = rng.choice(260, n, p=weights / weights.sum()) + 1
    miles = np.round(rng.gamma(2.0, 1.6, n), 2)
    return pa.table({
        "trip_id": np.arange(n, dtype="int64"),
        "pickup_at": pa.array(start + seconds.astype("timedelta64[s]")),
        "pickup_zone": zones.astype("int32"),
        "payment_type": pa.array(rng.choice(["card", "cash", "app"], n, p=[.7, .2, .1])),
        "passengers": rng.choice([1, 2, 3, 4], n, p=[.7, .18, .07, .05]).astype("int8"),
        "trip_miles": miles,
        "fare_usd": np.round(np.maximum(3.0, 3.0 + 2.5 * miles + rng.normal(0, 1.0, n)), 2),
    })

def best_ms(fn, repeats=5):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter(); fn(); times.append((time.perf_counter() - t0) * 1000)
    return min(times)

trips = make_trips()

# The same rows in a row store (SQLite) and a column store (DuckDB), both on disk.
lite = sqlite3.connect("trips.sqlite")
lite.execute("""CREATE TABLE trips (trip_id INTEGER PRIMARY KEY, pickup_at TEXT, pickup_zone INT,
                payment_type TEXT, passengers INT, trip_miles REAL, fare_usd REAL)""")
lite.executemany("INSERT INTO trips VALUES (?,?,?,?,?,?,?)",
                 ((r[0], str(r[1]), *r[2:]) for r in zip(*[c.to_pylist() for c in trips.columns])))
lite.commit()
duck = duckdb.connect("trips.duckdb")
duck.execute("CREATE TABLE trips AS SELECT * FROM trips")
duck.execute("CHECKPOINT")
print(f"SQLite file {os.path.getsize('trips.sqlite')/1e6:.1f} MB, DuckDB file {os.path.getsize('trips.duckdb')/1e6:.1f} MB")
```

```text
SQLite file 54.6 MB, DuckDB file 6.6 MB
```

SQLite stores rows in a B-tree keyed on `trip_id`, and DuckDB stores compressed columns. The file sizes already show part of the story: the row store is eight times larger, because it cannot exploit similarity within a column.

```python
scan = "SELECT pickup_zone, sum(fare_usd) FROM trips GROUP BY pickup_zone"
point = "SELECT * FROM trips WHERE trip_id = 123456"

print(f"{'':28s}{'SQLite':>11s}{'DuckDB':>11s}")
print(f"{'analytic scan (ms)':28s}{best_ms(lambda: lite.execute(scan).fetchall()):11.2f}"
      f"{best_ms(lambda: duck.execute(scan).fetchall()):11.2f}")
print(f"{'point lookup by key (ms)':28s}{best_ms(lambda: lite.execute(point).fetchall()):11.3f}"
      f"{best_ms(lambda: duck.execute(point).fetchall()):11.3f}")
```

```text
                                 SQLite     DuckDB
analytic scan (ms)               173.84       0.87
point lookup by key (ms)          0.005      0.298
```

The numbers come from one run on a 12-core laptop that was busy with other work, each the best of five, so treat them as an order of magnitude. On the analytic scan DuckDB wins by more than a hundred times. On a key lookup SQLite wins by about sixty. Neither system is badly built: each is doing what its layout makes cheap. DuckDB's authors describe exactly this gap as their motivation, noting that SQLite's row-major B-tree performs poorly on analytic queries while embedded uses still need analytics (Raasveldt and Mühleisen, [*DuckDB*](https://doi.org/10.1145/3299869.3320212), SIGMOD 2019).

## Why the layout decides it

In a row store, a query for `fare_usd` still has to bring every other field of each row through memory, because they sit side by side on the same page. Warehouse fact tables make that much worse. Kleppmann notes that they often pass 100 columns and sometimes reach several hundred, while a typical query reads four or five. A column store writes each column to its own file or segment, with the same row order in each, so that the 23rd entry of every column belongs to row 23.

```text
Row store: pages hold whole rows         Column store: each column is contiguous
+-------------------------------+        trip_id   |0|1|2|3|4|5|6|7|...
|0 |01-01|12|card|1|2.1|8.40    |        zone      |12|12|4|12|4|4|1|1|...
|1 |01-01|12|cash|2|0.9|5.20    |        payment   |card|cash|card|...
|2 |01-01| 4|card|1|5.5|16.10   |        fare_usd  |8.40|5.20|16.10|...
+-------------------------------+
SUM(fare_usd) reads every byte           SUM(fare_usd) reads one column
```

This can be measured without a database at all, by summing the same floats laid out two ways. The row layout below uses a 128-byte record, a modest row width for a fact table.

```python
n = 1_000_000
rows = np.zeros(n, dtype=[("id", "i8"), ("at", "i8"), ("zone", "i4"), ("pay", "i4"),
                          ("pax", "i4"), ("miles", "f8"), ("fare", "f8"), ("pad", "S84")])
rows["fare"] = trips["fare_usd"].to_numpy()
fare_column = trips["fare_usd"].to_numpy().copy()

print("bytes per row in the row layout:", rows.dtype.itemsize)
print(f"sum over row layout:    {best_ms(lambda: rows['fare'].sum()):6.2f} ms")
print(f"sum over column layout: {best_ms(lambda: fare_column.sum()):6.2f} ms")
print(f"python loop, one value at a time: {best_ms(lambda: sum(fare_column[:100_000].tolist()), 3) * 10:6.2f} ms (scaled from 100k)")
```

```text
bytes per row in the row layout: 128
sum over row layout:      2.55 ms
sum over column layout:   0.12 ms
python loop, one value at a time:   9.85 ms (scaled from 100k)
```

The column is about twenty times faster, and no disk is involved. The row layout has to stride through memory, which brings 128 bytes through the cache to use 8. The final line adds the third factor, which is that interpreted Python handling one value at a time is about eighty times slower than the tight loop over the column. DuckDB and other analytic engines close this gap by processing blocks of values at once, a design called vectorised execution. DuckDB processes 1,024 values per vector and chose interpretation over vectors instead of compiling queries, largely for portability. Kleppmann gives the reasoning: tight loops fit in the L1 cache, avoid branch mispredictions, and can use SIMD instructions.

It is tempting to conclude that the layout alone does the work, and that a row store could copy the benefit by creating a narrow table per column or an index on each column. Abadi, Madden and Hachem tested exactly that ([*Column-Stores vs. Row-Stores: How Different Are They Really?*](https://doi.org/10.1145/1376616.1376712), SIGMOD 2008) by comparing a commercial row store against C-Store on the Star Schema Benchmark. Emulating the layout did not give good performance, because of the cost of reconstructing tuples and the per-row overhead in narrow tables. Taking the column store apart, they found late materialisation (stitching rows back together as late as possible) improved performance by a factor of three, compression by about two on average and by an order of magnitude on queries over sorted data, and their invisible join by about 50%. The lesson is that the storage layout makes the benefits possible, and the query executor has to be built to use them. They also caution against reading too much into the absolute difference between the two systems, since they differ in many implementation details.

## Compression exploits the column

A column of similar values compresses far better than a row of unlike ones. The simplest case is run-length encoding, which stores each value once with a count.

```python
def run_length(values):
    """(value, count) pairs: the encoding a sorted column collapses into."""
    change = np.flatnonzero(values[1:] != values[:-1]) + 1
    starts = np.r_[0, change]
    return values[starts], np.diff(np.r_[starts, len(values)])

zone = trips["pickup_zone"].to_numpy()
print("arrival order:", len(run_length(zone)[0]), "runs")
print("sorted:       ", len(run_length(np.sort(zone))[0]), "runs")
```

```text
arrival order: 956362 runs
sorted:        260 runs
```

In arrival order, zone values almost never repeat, and there are nearly as many runs as rows. Sorted, there are exactly 260 runs, one per zone. Kleppmann describes how a sorted first key can shrink to kilobytes even over billions of rows, and how the second sort key helps less because its runs are shorter. The [previous chapter](01-encoding-and-files.md) measured the same effect in a Parquet file, where sorting took `pickup_zone` from about a megabyte to 5 KB and cost `pickup_at` its order.

Bitmap encoding suits columns with few distinct values. Take one bit vector per value, with a 1 for each row that holds it. Then a filter becomes bitwise arithmetic over the vectors, which CPUs do fast. Kleppmann's example has 100,000 distinct products against billions of sales, where the bitmaps are mostly zeros and run-length encode down further.

```python
pay = np.array(trips["payment_type"].to_pylist())
pax = trips["passengers"].to_numpy()
is_cash, is_app = pay == "cash", pay == "app"
is_group = pax >= 3

packed = np.packbits(is_cash)
print("bitmap for payment_type='cash':", packed.nbytes, "bytes,", int(is_cash.sum()), "rows set")
print("(cash OR app) AND passengers>=3:", int(((is_cash | is_app) & is_group).sum()), "rows")
check = duck.execute("SELECT count(*) FROM trips WHERE payment_type IN ('cash','app') AND passengers >= 3").fetchone()[0]
print("same predicate in SQL:          ", check, "rows")
```

```text
bitmap for payment_type='cash': 125000 bytes, 199330 rows set
(cash OR app) AND passengers>=3: 35871 rows
same predicate in SQL:           35871 rows
```

`IN` becomes `OR` over value bitmaps and a conjunction becomes `AND`, and the answer agrees with SQL. Note that the bitmap is 125,000 bytes for a million rows, one bit per row, before any further compression.

## Sort orders and copies

Rows must be sorted as whole rows, or the positional link between columns breaks, so a column store has one physical order per copy of the data. The first sort key is the one that benefits most, so pick it from the common filters. Date is the usual first choice, since most analytic queries restrict a date range.

C-Store carries this a step further: since the system keeps several copies for fault tolerance anyway, each copy can have a different sort order (Stonebraker et al., [*C-Store*](https://doi.org/10.1145/3226595.3226638), VLDB 2005, here in the 2018 reprint collection). The authors describe a collection of overlapping column-oriented projections instead of the usual tables and indexes, along with bitmap indexes that complement B-trees, and the design was commercialised as Vertica. Warehouses that offer clustering keys or multiple materialised projections are making the same trade: more storage and slower loads in exchange for more queries that can skip data.

There is a naming trap worth knowing. The "column families" of Cassandra and HBase, inherited from Bigtable (Chang et al., [*Bigtable*](https://doi.org/10.5555/1298455.1298475), OSDI 2006), are not column-oriented in this sense. They store all of a row's columns in a family together, so the access pattern is still mostly rows.

## Indexes and scans

A B-tree finds a small number of rows faster than any scan, but its value falls as selectivity falls, because each match is another random lookup into the table.

```python
lite.execute("CREATE INDEX idx_zone ON trips(pickup_zone)")
rare, common = "SELECT sum(fare_usd) FROM trips WHERE pickup_zone = 250", "SELECT sum(fare_usd) FROM trips WHERE pickup_zone = 1"
for label, q in [("rare zone", rare), ("busiest zone", common)]:
    print(f"{label:13s} SQLite with index {best_ms(lambda: lite.execute(q).fetchall()):8.2f} ms   "
          f"DuckDB scan {best_ms(lambda: duck.execute(q).fetchall()):6.2f} ms   "
          f"rows {lite.execute(q.replace('sum(fare_usd)', 'count(*)')).fetchone()[0]}")
print(lite.execute("EXPLAIN QUERY PLAN " + rare).fetchall()[0][-1])
```

```text
rare zone     SQLite with index     0.37 ms   DuckDB scan   0.47 ms   rows 623
busiest zone  SQLite with index    24.83 ms   DuckDB scan   0.59 ms   rows 163162
SEARCH trips USING INDEX idx_zone (pickup_zone=?)
```

For the 623 rows of a rare zone, the indexed row store and the scanning column store are comparable. For the busiest zone, with about one trip in six, the index has to chase 163,162 rows and takes around 40 times as long as the scan, which barely changed at all. This is why warehouses tend to do without secondary indexes entirely. Scanning sorted, compressed columns and skipping whole blocks by min and max is enough, an approach DuckDB's storage implements by keeping a minimum and maximum per block. The plan shows it, with the filter pushed into the scan and only two of the seven columns projected.

```python
plan = duck.execute("EXPLAIN SELECT pickup_zone, sum(fare_usd) FROM trips WHERE pickup_zone < 5 GROUP BY pickup_zone").fetchall()[0][1]
print(plan)
```

```text
╭─ Projection ──────────────────────╮
│ Projections: CAST(#0 AS INTEGER), │
│              #1                   │
│ ~289 rows                         │
╰─────────────────┬─────────────────╯
╭─ Perfect Hash Group By ───────────╮
│ Groups: #0                        │
│ Aggregates: sum(#1)               │
│ ~289 rows                         │
╰─────────────────┬─────────────────╯
╭─ Projection ────┴─────────────────╮
│ Projections: pickup_zone,         │
│              fare_usd             │
│ ~200,000 rows                     │
╰─────────────────┬─────────────────╯
╭─ Projection ────┴─────────────────╮
│ Projections: CAST(#0 AS TINYINT), │
│              #1                   │
│ ~200,000 rows                     │
╰─────────────────┬─────────────────╯
╭─ Seq Scan ──────┴─────────────────╮
│ Table: trips.main.trips           │
│ Type: Sequential Scan             │
│ Projections: pickup_zone,         │
│              fare_usd             │
│ Filters: pickup_zone < 5          │
│ ~200,000 rows                     │
╰───────────────────────────────────╯
```

## The write path

Column stores pay for all this on writes. A compressed, sorted column cannot accept an insert in the middle, because doing so would mean rewriting the column files, with every column shifted to keep the row positions aligned. Kleppmann describes the usual answer, borrowed from log-structured storage: keep recent writes in an in-memory store and periodically merge them into the columns in bulk. Queries read both and combine the results, as Vertica does. Bulk loads fit this very well, and most warehouse ingestion is bulk. Here is what happens if you try to use one as a transactional store, one committed row at a time.

```python
def insert_loop(execute, commit, n=2_000, first=2_000_000):
    t0 = time.perf_counter()
    for i in range(first, first + n):
        execute("INSERT INTO trips VALUES (?, '2026-02-01 00:00:00', 1, 'card', 1, 1.0, 5.0)", (i,))
        commit()
    return (time.perf_counter() - t0) / n * 1000

print(f"SQLite one row per transaction: {insert_loop(lite.execute, lite.commit):6.3f} ms per row")
print(f"DuckDB one row per transaction: {insert_loop(duck.execute, lambda: None):6.3f} ms per row")
```

```text
SQLite one row per transaction:  0.250 ms per row
DuckDB one row per transaction:  0.277 ms per row
```

The textbook account would lead you to expect DuckDB to lose by a wide margin, and in this test it does not: both spend about a quarter of a millisecond per commit. My guess at the reason, which this test does not establish, is that both costs are dominated by the commit itself, and appended rows have not reached a compressed block yet. The difference a column store really pays is elsewhere, in concurrent writers and in changes to data that is already compressed, and the DuckDB paper describes a system embedded in one process and not a shared transactional service. A measurement like this one is a good habit anyway. It tells you which cost you actually have, and it stops you repeating a rule of thumb past the point where you have checked it.

## Rollups and cubes

If the same aggregate is computed all day, it can be stored. A materialised view is the result of a query saved as data, and a data cube is the grid of such aggregates across several dimensions with totals along each edge. SQL expresses the cube directly.

```python
print(duck.sql("""
    SELECT date_trunc('week', pickup_at)::DATE AS week, payment_type, sum(fare_usd)::INT AS fares
    FROM trips WHERE pickup_at < DATE '2026-01-12'
    GROUP BY CUBE (week, payment_type)
    ORDER BY week NULLS LAST, payment_type NULLS LAST
"""))
```

```text
┌────────────┬──────────────┬─────────┐
│    week    │ payment_type │  fares  │
│    date    │   varchar    │  int32  │
├────────────┼──────────────┼─────────┤
│ 2025-12-29 │ app          │  140981 │
│ 2025-12-29 │ card         │  994102 │
│ 2025-12-29 │ cash         │  283395 │
│ 2025-12-29 │ NULL         │ 1418477 │
│ 2026-01-05 │ app          │  250451 │
│ 2026-01-05 │ card         │ 1736660 │
│ 2026-01-05 │ cash         │  492873 │
│ 2026-01-05 │ NULL         │ 2479985 │
│ NULL       │ app          │  391432 │
│ NULL       │ card         │ 2730762 │
│ NULL       │ cash         │  776268 │
│ NULL       │ NULL         │ 3898462 │
└────────────┴──────────────┴─────────┘
  12 rows                   3 columns
```

The `NULL` rows are the marginal totals. Scale that to many dimensions and a dashboard can read any slice without touching the fact table.

```python
duck.execute("""CREATE OR REPLACE TABLE daily_zone AS
    SELECT pickup_at::DATE AS day, pickup_zone, count(*) AS trips, sum(fare_usd) AS fares
    FROM trips GROUP BY ALL""")
from_raw = "SELECT sum(fares) FROM (SELECT sum(fare_usd) fares FROM trips WHERE pickup_zone = 1 GROUP BY pickup_at::DATE)"
from_rollup = "SELECT sum(fares) FROM daily_zone WHERE pickup_zone = 1"
print(f"rollup rows: {duck.execute('SELECT count(*) FROM daily_zone').fetchone()[0]}")
print(f"raw {best_ms(lambda: duck.execute(from_raw).fetchall()):.2f} ms, rollup {best_ms(lambda: duck.execute(from_rollup).fetchall()):.2f} ms")
print("but share of fare from trips over 10 miles is not answerable: trip_miles is not a rollup column")
```

```text
rollup rows: 8060
raw 0.92 ms, rollup 0.22 ms
but share of fare from trips over 10 miles is not answerable: trip_miles is not a rollup column
```

Reading the rollup is about four times faster here, and the gap widens as the fact table grows, since the rollup's size depends on the number of zone-days and not on the number of trips. The final line is the catch, and Kleppmann's example makes the same point: a cube of sales cannot answer what share of sales came from items over $100, because price is not one of its dimensions. Rollups trade flexibility for speed. Keep the detailed data too and use rollups as an acceleration layer, the same recommendation Kimball makes when he insists on storing the atomic grain ([dimensional modelling](../../02-ingest-and-modelling/notes/02-dimensional-modelling.md)).

## Pitfalls

- **Running analytics on the production OLTP database.** One long scan fills the buffer pool and slows the application. Replicate to something built for scans, even if it is a single DuckDB file.
- **Assuming "column family" means column store.** Cassandra and HBase store column families row by row. Their access pattern is key-based.
- **Using `SELECT *` in a warehouse.** It discards the entire advantage of the layout, and on systems that bill per byte scanned, it costs money.
- **Adding indexes to fix a slow warehouse.** A low-selectivity index can be slower than the scan it replaces. Sort or cluster on the filter column and let block statistics do the skipping.
- **Treating a rollup as the source of truth.** It cannot answer a question about a dimension it dropped, and it can drift from the facts. Keep the atomic table.
- **Loading a warehouse one row at a time.** Even where it works, it leaves small unmerged segments behind and overwhelms services that expect batches. Load in bulk.
- **Quoting benchmarks across systems as if layout were the only variable.** Abadi and colleagues warn against this in their own study. Implementation differences are often as large as the effect.

## Try it

The code in this chapter is collected in [practice/02_row_and_column_stores.py](../practice/02_row_and_column_stores.py).

1. Widen the `pad` field in `layout` to `S1000`, predict how the gap between row and column sums changes, and measure.

<details><summary>Answer</summary>

The row sum slows further, because each 8-byte value now pulls in about a kilobyte of neighbours, so far fewer useful values fit per cache line and per page. The column sum does not change. That is the fact-table argument in miniature: wider rows only hurt the row layout.

</details>

2. Find the selectivity at which SQLite's indexed query loses to DuckDB's scan, by querying zones of different sizes.

<details><summary>Answer</summary>

Loop `zone` over 1, 2, 5, 10, 50, 250 and record both times with `best_ms`. DuckDB stays nearly flat. SQLite grows roughly linearly with row count, so it loses once the match count passes a few hundred to a few thousand rows on this data. The exact crossover moves with hardware, which is why a measurement beats a rule.

</details>

3. Add a rollup that can answer the share of fares from trips over 10 miles. What did it cost you?

<details><summary>Answer</summary>

Add a derived dimension, `trip_miles > 10 AS long_trip`, to `daily_zone` and regroup. Rows at most double, and the question becomes a `SUM` with a filter. But a threshold of 12 miles still cannot be answered. You paid for one question, so a rollup should be built from questions people have actually asked.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| OLTP vs OLAP? | OLTP does small reads and writes by key for applications. OLAP does large scans and aggregates over history for analysis. Their access patterns need different storage. |
| Why are column stores fast for analytics? | They read only the named columns, compress similar values well, skip blocks by min and max, and use vectorised execution with tight loops over columns. |
| Can a row store emulate one with narrow tables? | Not effectively, as Abadi et al. (SIGMOD 2008) showed. Tuple reconstruction and per-row overhead dominate, and the executor must also be built for columns. |
| What is late materialisation? | Keeping columns separate through the query and building rows only when necessary. Abadi et al. measured about a factor of three. |
| Why do warehouses avoid secondary indexes? | Each match is a random lookup, which loses to a scan as selectivity falls. Sort order and block statistics deliver most of the benefit without slowing writes. |
| How do column stores handle writes? | Recent writes go to an in-memory or row-oriented store and are merged into compressed columns in bulk. Reads combine both. |
| Materialised view vs cube? | A view stores one query's result. A cube precomputes aggregates over combinations of dimensions. Both are fast, and both are limited to the dimensions they kept. |
| What are vectorised and compiled execution? | Vectorised engines run interpreted operators over batches of values. Compiled engines generate code per query. DuckDB chose vectors, citing portability. |

## Next

Both engines here ran on one machine. [Distributed compute](03-distributed-compute.md) asks when one machine stops being enough, and what it costs to use many.
