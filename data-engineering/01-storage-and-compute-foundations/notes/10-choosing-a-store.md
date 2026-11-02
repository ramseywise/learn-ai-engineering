---
origin: synthesis
sources:
  - https://db.cs.cmu.edu/papers/2024/whatgoesaround-sigmodrec2024.pdf
  - https://www.sqlite.org/whentouse.html
  - https://duckdb.org/why_duckdb
  - https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-general-nosql-design.html
  - https://redis.io/docs/latest/develop/data-types/
  - https://www.mongodb.com/docs/manual/data-modeling/
  - https://www.mongodb.com/docs/manual/core/transactions/
  - https://cassandra.apache.org/doc/latest/cassandra/architecture/overview.html
  - https://www.elastic.co/docs/manage-data/data-store/near-real-time-search
  - https://www.postgresql.org/docs/current/textsearch-intro.html
  - https://www.postgresql.org/docs/current/datatype-json.html
  - https://www.postgresql.org/docs/current/ddl-partitioning.html
  - https://github.com/pgvector/pgvector
  - https://prometheus.io/docs/prometheus/latest/storage/
  - https://docs.timescale.com/use-timescale/latest/hypertables/
  - https://neo4j.com/docs/getting-started/graph-database/
confidence: medium
cleaned: 2026-11-02
---
# 10 — Choosing a store

A team needs to keep some data and someone says "let's use a document database" or "we need a vector store". That sentence has already skipped the question. A store is a set of bets about how data will be read and written, so the right start is to describe the access pattern and only then match it to a store. This chapter gives ten kinds of store a fair summary, then measures how far plain Postgres stretches, because the honest default answer is often the one you already run. Confidence is medium because the choice depends on your workload, and the runs here are one machine's, one trial each, on synthetic data. The code is [`practice/10_choosing_a_store.py`](../practice/10_choosing_a_store.py) and starts its own Postgres 16.2.

## Start with the access pattern

Before naming a product, answer these. Most of the decision is in the answers.

| Question | If the answer is... | It points toward |
|---|---|---|
| How do you find a record? | By one key | Key-value, or any database |
| | By several fields, ad hoc | Relational, document with indexes |
| | By words and relevance | Search engine, or Postgres FTS |
| | By meaning, similar to this | Vector index |
| | By following links many hops | Graph store, or recursive SQL |
| How much of the data does one query touch? | A few rows | Row store, B-tree (OLTP) |
| | Most rows, few columns | Column store (OLAP) |
| How does it change? | Updates in place, transactions | Relational |
| | Append-only by time, old data expires | Time-series, partitioned table |
| | Whole files written once | Object store |
| How big and how fast? | Fits on one machine | Stop here: one node is far simpler |
| | Writes exceed one machine | Partitioned store |
| Who runs it? | Your process, no server | Embedded |
| | A team with an on-call rota | Whatever they already operate |

The last row is not a joke. Every new store brings its own backups, upgrades, monitoring and failure modes, and [Operating data stores](../../05-quality-and-observability/notes/05-operating-data-stores.md) shows what that bill looks like for just one of them.

## Row or column: the first split

The largest performance difference has nothing to do with the data model. Here are the same 2,000,000 rows in two embedded databases, one row-oriented and one columnar, asked two questions.

```python
import sqlite3, time, random
import duckdb, numpy as np

N = 2_000_000
rng = np.random.default_rng(10)
ids = np.arange(N)
zones = rng.integers(0, 265, N)
fares = rng.gamma(2.0, 8.0, N).round(2)

lite = sqlite3.connect("trips.sqlite")
lite.execute("CREATE TABLE trips (id INTEGER PRIMARY KEY, zone INT, fare REAL)")
lite.executemany("INSERT INTO trips VALUES (?,?,?)", zip(ids.tolist(), zones.tolist(), fares.tolist()))
lite.commit()

duck = duckdb.connect("trips.duckdb")
duck.execute("CREATE TABLE trips (id BIGINT PRIMARY KEY, zone INT, fare DOUBLE)")
duck.register("src", {"id": ids, "zone": zones, "fare": fares})
duck.execute("INSERT INTO trips SELECT * FROM src")

def timed(run, repeat):
    t = time.perf_counter()
    for _ in range(repeat):
        run()
    return (time.perf_counter() - t) / repeat * 1000

random.seed(1)
POINT = "SELECT fare FROM trips WHERE id = ?"
SCAN = "SELECT zone, avg(fare) FROM trips GROUP BY zone ORDER BY 2 DESC LIMIT 3"
print(f"{N:,} rows                       SQLite ms    DuckDB ms")
print(f"point lookup by primary key {timed(lambda: lite.execute(POINT, (random.randrange(N),)).fetchone(), 2000):11.4f} "
      f"{timed(lambda: duck.execute(POINT, (random.randrange(N),)).fetchone(), 2000):12.4f}")
print(f"group-by over every row     {timed(lambda: lite.execute(SCAN).fetchall(), 3):11.1f} "
      f"{timed(lambda: duck.execute(SCAN).fetchall(), 3):12.1f}")
```

```text
2,000,000 rows                       SQLite ms    DuckDB ms
point lookup by primary key      0.0051       0.2368
group-by over every row           436.2          2.1
```

SQLite wins the point lookup by nearly 50 times; DuckDB wins the group-by by about 200 times. Neither is a better database. [Row and column stores](03-row-and-column-stores.md) explains why, and [The warehouse](../../04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md) covers the large-scale versions of the right-hand column. If a workload has both patterns, the normal answer is two stores with a pipeline between them, rather than one store that does both moderately.

## The ten kinds

| Kind | Bet it makes | Read this | Reach for it when | It hurts when |
|---|---|---|---|---|
| **Relational** (Postgres, MySQL) | You don't know all your queries yet | [DE 01/01](01-data-systems-and-data-models.md), [01/04](04-transactions-and-isolation.md) | Default for application state | Writes outgrow one primary |
| **Key-value** (Redis, DynamoDB) | You read by key, and that is all | [Redis types](https://redis.io/docs/latest/develop/data-types/), [DynamoDB design](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-general-nosql-design.html) | Sessions, caches, predictable high scale | A new query arrives that isn't by key |
| **Document** (MongoDB) | Data read together is stored together | [MongoDB modelling](https://www.mongodb.com/docs/manual/data-modeling/) | Varying shapes, whole-object reads | Many-to-many joins; transactions across documents |
| **Wide-column** (Cassandra, Bigtable) | Huge writes, known partition key | [Cassandra overview](https://cassandra.apache.org/doc/latest/cassandra/architecture/overview.html) | Multi-region, always-on writes | Ad hoc queries; strong consistency |
| **Search** (Elasticsearch) | Relevance over text, slight staleness | [Near real-time search](https://www.elastic.co/docs/manage-data/data-store/near-real-time-search) | Ranking, facets, fuzzy text | As the only copy of your data |
| **Time-series** (Prometheus, Timescale) | Append by time, expire old | [Prometheus storage](https://prometheus.io/docs/prometheus/latest/storage/) | Metrics, sensors | Frequent updates to old points |
| **Graph** (Neo4j) | Long chains of links dominate | [AIE 05/09](../../../ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher.md) | Deep variable-length traversal | Mostly tabular reporting |
| **Vector** (Qdrant, pgvector) | Nearest neighbours by embedding | [GA 02/04](../../../generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann.md), [GA 02/09](../../../generative-ai/02-rag-retrieval/notes/09-vector-database-comparison.md) | Semantic retrieval at scale | Small corpora, where exact search is fine |
| **Object** (S3, GCS) | Cheap durable whole files | [DE 04/01b](../../04-warehouse-lakehouse-streaming/notes/01b-object-storage-and-the-data-lake.md) | Lakes, backups, media | Small mutable records; latency |
| **Embedded** (SQLite, DuckDB) | No server, one process | [SQLite: when to use](https://www.sqlite.org/whentouse.html), [Why DuckDB](https://duckdb.org/why_duckdb) | Local apps, tools, analysis, tests | Many concurrent writers |

A few details from the sources are worth having precisely.

**DynamoDB inverts the design order.** Its [own guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-general-nosql-design.html) says that in a relational database you can model first and query flexibly later, whereas in DynamoDB you design the schema around your most important queries and should know your access patterns before you begin. So the price of its predictable scale is paid up front, in knowing what you will ask.

**MongoDB now has transactions, and advises you not to lean on them.** A single-document operation is atomic and multi-document ACID transactions exist, but [its docs](https://www.mongodb.com/docs/manual/core/transactions/) say distributed transactions usually cost more than single-document writes and should not replace effective schema design. That follows from its [modelling rule](https://www.mongodb.com/docs/manual/data-modeling/): data accessed together should be stored together.

**"Wide-column" does not mean columnar.** Stonebraker and Pavlo are blunt about this in [*What Goes Around Comes Around... And Around...* (SIGMOD Record, 2024)](https://db.cs.cmu.edu/papers/2024/whatgoesaround-sigmodrec2024.pdf): column-family is a reduction of the document model with one level of nesting, and it is not a columnar store. Cassandra describes itself as [partitioned wide-column storage with eventually consistent semantics](https://cassandra.apache.org/doc/latest/cassandra/architecture/overview.html), and it is not the choice for scanning one column across all rows. Do not let the name put it on the wrong side of the row and column split.

**Search is near real time, on purpose.** Elasticsearch [makes new documents searchable by periodically refreshing](https://www.elastic.co/docs/manage-data/data-store/near-real-time-search), every second by default, because opening a new segment is cheaper than a full commit. A document you just wrote may not appear for a moment. That's fine for search and wrong for a system of record, so keep the source of truth elsewhere and treat the index as [derived data](09-persistence.md#cache-versus-source-of-truth).

**Prometheus keeps recent data in memory.** [Its storage docs](https://prometheus.io/docs/prometheus/latest/storage/) describe two-hour blocks with the current block in memory, protected by a write-ahead log. Timescale takes the other route, with [hypertables](https://docs.timescale.com/use-timescale/latest/hypertables/) that remain Postgres tables automatically split into time-based chunks. The trade between them is the usual one: a purpose-built system or an extension of what you run.

## When Postgres is enough

Stonebraker and Pavlo review 20 years of attempts to replace the relational model and conclude, as their abstract says, that "SQL has been extended to capture the good ideas from others". Their arguments are specific. Relational systems "easily emulate" key-value stores without changes, and vector databases are "essentially document-oriented DBMSs with specialized ANN indexes", where those indexes are "a feature, not the foundation of a new system architecture". They saw JSON support take years to reach relational systems and vector indexes take under one. Keep in mind one of the authors founded database companies and neither is neutral on this; still, these are checkable claims.

So check them. Each block below tries one specialised pattern on a single private Postgres. These aren't benchmarks against the specialised stores, which I did not run. The question is only whether the plain option clears the bar your workload sets.

### As a key-value store

```python
pg.execute("CREATE TABLE kv (k text PRIMARY KEY, v jsonb)")
pg.execute("""INSERT INTO kv SELECT 'session:' || g, jsonb_build_object('user', g, 'cart', g % 7)
              FROM generate_series(1, 1000000) g""")
def rate(run, seconds=2):
    n, end = 0, time.perf_counter() + seconds
    while time.perf_counter() < end:
        run(); n += 1
    return n / seconds
print(f"reads per second, one client, over a Unix socket: "
      f"{rate(lambda: pg.execute('SELECT v FROM kv WHERE k = %s', (f'session:{random.randrange(1, 10**6)}',)).fetchone()):,.0f}")
print(f"upserts per second, one client, durable commit:   "
      f"{rate(lambda: pg.execute('INSERT INTO kv VALUES (%s, %s) ON CONFLICT (k) DO UPDATE SET v = excluded.v', (f'session:{random.randrange(1, 10**6)}', '{}'))):,.0f}")
```

```text
reads per second, one client, over a Unix socket: 33,181
upserts per second, one client, durable commit:   20,741
```

Tens of thousands of operations a second from one client, against a million keys, on a laptop. Note the durable commit here uses macOS's `fsync`, which [does not flush the drive](09-persistence.md#fsync-what-a-power-cut-takes-and-what-it-costs), so a server with honest flushes will show lower upsert numbers. Most applications don't need more than this, and those that do tend to know it. Redis earns its place when you want sub-millisecond reads as a cache in front of the database, or its [data structures](https://redis.io/docs/latest/develop/data-types/): sorted sets, HyperLogLog, streams.

### As a document store

The [JSON docs](https://www.postgresql.org/docs/current/datatype-json.html) recommend `jsonb` for most applications, since `json` keeps the text and reparses it on each use.

```python
pg.execute("CREATE TABLE product (id serial PRIMARY KEY, doc jsonb)")
pg.execute("""INSERT INTO product (doc)
    SELECT CASE WHEN g % 2 = 0
        THEN jsonb_build_object('kind', 'shoe', 'size', g % 15, 'color', (ARRAY['red','blue','green'])[g % 3 + 1])
        ELSE jsonb_build_object('kind', 'book', 'pages', g % 900, 'author', 'author' || g % 5000) END
    FROM generate_series(1, 1000000) g""")
Q = "SELECT count(*) FROM product WHERE doc @> %s"
print("no index  ", explain_top(Q, '{"author": "author42"}'))
pg.execute("CREATE INDEX ON product USING gin (doc jsonb_path_ops)")
pg.execute("ANALYZE product")
print("GIN index ", explain_top(Q, '{"author": "author42"}'))
```

```text
no index   Parallel Seq Scan on product               31.387 ms
GIN index  Bitmap Heap Scan on product                0.017 ms
```

Two document shapes in one column, and a GIN index turns a containment query from a 31 ms scan of a million documents to 0.017 ms. You can also mix columns and documents in one table, which a document store can't do as well: keep what you filter and join on in real columns and put the variable part in `jsonb`.

### As a search engine

```python
WORDS = ("trip fare driver taxi route satisfy satisfies satisfied refund airport tip late meter zone "
         "payment rider complaint cancelled surge receipt").split()
docs = [" ".join(random.choices(WORDS, k=12)) for _ in range(300_000)]
pg.execute("CREATE TABLE ticket (id serial PRIMARY KEY, body text, tsv tsvector)")
with pg.cursor() as cur, cur.copy("COPY ticket (body) FROM STDIN") as copy:
    for d in docs:
        copy.write_row((d,))
pg.execute("UPDATE ticket SET tsv = to_tsvector('english', body)")
pg.execute("CREATE INDEX ON ticket USING gin (tsv)")
pg.execute("ANALYZE ticket")
print("LIKE 'satisfied'     matches", pg.execute("SELECT count(*) FROM ticket WHERE body LIKE '%satisfied%'").fetchone()[0])
print("tsquery 'satisfied'  matches", pg.execute(
    "SELECT count(*) FROM ticket WHERE tsv @@ to_tsquery('english', 'satisfied')").fetchone()[0], "(stems to 'satisfi')")
print("top result:", pg.execute("""SELECT body FROM ticket, to_tsquery('english', 'refund & surge') q
    WHERE tsv @@ q ORDER BY ts_rank(tsv, q) DESC LIMIT 1""").fetchone()[0][:60])
```

```text
LIKE 'satisfied'     matches 138026
tsquery 'satisfied'  matches 257679 (stems to 'satisfi')
top result: trip refund driver refund surge surge late surge late surge
```

The [text search introduction](https://www.postgresql.org/docs/current/textsearch-intro.html) gives the reasons not to use `LIKE`: no language support, no ranking, no index. The counts show the first. `LIKE '%satisfied%'` finds 138,026 rows, and the stemmed query finds 257,679, including "satisfy" and "satisfies". For one language and simple ranking on one table, this is often enough. Move to a search engine when you need facets, typo tolerance, custom analysers and relevance tuning as a product feature.

### As a time-series store

```python
pg.execute("CREATE TABLE metric (ts timestamptz NOT NULL, value float8) PARTITION BY RANGE (ts)")
for m in range(1, 13):
    pg.execute(f"""CREATE TABLE metric_{m:02d} PARTITION OF metric
        FOR VALUES FROM ('2026-{m:02d}-01') TO ('{"2027-01-01" if m == 12 else f"2026-{m + 1:02d}-01"}')""")
pg.execute("""INSERT INTO metric SELECT '2026-01-01'::timestamptz + (g * interval '10 seconds'), random()
              FROM generate_series(0, 3100000) g""")
pg.execute("ANALYZE metric")
rows = pg.execute("EXPLAIN SELECT avg(value) FROM metric WHERE ts >= '2026-03-01' AND ts < '2026-03-08'").fetchall()
print("partitions the plan reads for one week:", sum("Scan on metric_" in r[0] for r in rows))
t = time.perf_counter()
print("DELETE one month:", pg.execute("DELETE FROM metric WHERE ts < '2026-02-01'").rowcount, "rows", end=" ")
print(f"in {(time.perf_counter() - t) * 1000:,.0f} ms")
t = time.perf_counter()
pg.execute("DROP TABLE metric_02")
print(f"DROP one partition (a month of similar size) in {(time.perf_counter() - t) * 1000:,.1f} ms")
```

```text
partitions the plan reads for one week: 1
DELETE one month: 267840 rows in 64 ms
DROP one partition (a month of similar size) in 5.4 ms
```

[Range partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html) gives the two things time-series stores are built around. A one-week query reads one partition out of twelve, and expiry is a `DROP`, here about 12 times faster than a `DELETE` of similar size and leaving no dead rows behind for [VACUUM](../../05-quality-and-observability/notes/05-operating-data-stores.md). What it doesn't give you is automatic chunk creation, retention policies or time-series compression, which is the case for an extension such as Timescale.

### As a graph store

```python
pg.execute("CREATE TABLE edge (src int, dst int)")
edges = rng.integers(0, 100_000, (500_000, 2))
with pg.cursor() as cur, cur.copy("COPY edge FROM STDIN") as copy:
    for s, d in edges.tolist():
        copy.write_row((s, d))
pg.execute("CREATE INDEX ON edge (src)")
pg.execute("ANALYZE edge")
HOPS = """WITH RECURSIVE walk(node, depth) AS (
    SELECT %s::int, 0
  UNION
    SELECT e.dst, w.depth + 1 FROM walk w JOIN edge e ON e.src = w.node WHERE w.depth < %s
) SELECT count(DISTINCT node) FROM walk"""
print("hops  nodes reached     ms    (100,000 nodes, 500,000 edges)")
for hops in [1, 2, 3, 4, 5, 6]:
    t = time.perf_counter()
    reached = pg.execute(HOPS, (7, hops)).fetchone()[0]
    print(f"{hops:4d} {reached:14,d} {(time.perf_counter() - t) * 1000:6,.0f}")
```

```text
hops  nodes reached     ms    (100,000 nodes, 500,000 edges)
   1              6      1
   2             31      0
   3            154      0
   4            754      1
   5          3,786      4
   6         17,297     15
```

Six hops across 500,000 edges takes milliseconds. Stonebraker and Pavlo make the case for this directly: a graph can be simulated as node and edge tables, so "RDBMSs are always an option", while [Neo4j](https://neo4j.com/docs/getting-started/graph-database/) uses pointer chasing, which helps on long edge chains. Their question is whether there are enough long-chain scenarios to justify leaving a relational database. This graph is sparse and random, so a hub-heavy social graph with higher fan-out will grow much faster. When you need path patterns as a first-class query language, [AIE 05/09](../../../ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher.md) shows Cypher.

### As a vector store

The bundled Postgres in this practice file does not include [pgvector](https://github.com/pgvector/pgvector), so nothing here runs on it. By its documentation, it does exact search by default with perfect recall and adds approximate indexes (HNSW, IVFFlat) that trade recall for speed, alongside ACID, point-in-time recovery and joins. Before reaching for any index, though, know what exact search costs.

```python
dim = 384
print(f"exact nearest neighbours by brute force, {dim} dimensions, numpy")
for count in [10_000, 100_000, 1_000_000]:
    corpus = rng.standard_normal((count, dim), dtype=np.float32)
    corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)
    query = corpus[3]
    t = time.perf_counter()
    for _ in range(5):
        np.argpartition(corpus @ query, -10)[-10:]
    print(f"{count:10,d} vectors {corpus.nbytes / 1e9:5.2f} GB  {(time.perf_counter() - t) / 5 * 1000:7.1f} ms per query")
```

```text
exact nearest neighbours by brute force, 384 dimensions, numpy
    10,000 vectors  0.02 GB      0.1 ms per query
   100,000 vectors  0.15 GB      1.5 ms per query
 1,000,000 vectors  1.54 GB     16.7 ms per query
```

About 17 ms for an exact search over a million 384-dimensional vectors with numpy, in memory, one query at a time. Plenty of retrieval corpora are far smaller than that, and they don't need an approximate index at all. How indexes behave at scale is in [GA 02/04](../../../generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann.md), and choosing among vector stores is in [GA 02/09](../../../generative-ai/02-rag-retrieval/notes/09-vector-database-comparison.md). Neither is repeated here. Changing embedding models means rebuilding the store, which is covered in [Schema and data migrations](../../05-quality-and-observability/notes/04-schema-and-data-migrations.md).

### So when is it not enough?

Be just as honest in the other direction. Postgres stops being enough when:

- **Writes exceed one primary.** You can add replicas for reads, but one node takes every write. See [partitioning and replication](05-partitioning-and-replication.md).
- **You scan most of a large table.** The 200x gap above is architecture, and an index won't close it. Use a warehouse.
- **You need multi-region writes with no single primary.** That's the design goal Cassandra and Dynamo-style stores trade consistency for.
- **Search or retrieval is the product.** A team tuning relevance every week deserves a tool built for it.
- **Blobs.** Large files belong in an object store, with their paths in the database.

And the trap in the other direction: adopting a specialised store for a scale you do not have. SQLite's own guidance is a good corrective. It [says any site with fewer than 100K hits a day should work fine](https://www.sqlite.org/whentouse.html), and notes it has one writer at a time, which is the real limit to check.

## Stores, and what is not a store

Comparisons often go wrong because the two things aren't in the same category. **"Snowflake or Airflow?" is not a real choice.** Snowflake stores data and computes over it. Airflow stores no business data: it schedules and retries work that runs elsewhere, often *in* Snowflake. Teams routinely run both. The useful comparisons are within a layer: warehouses against each other in [The warehouse](../../04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md), and orchestrators against each other in [Dagster and Airflow](../../03-transform-and-orchestrate/notes/05-dagster-and-airflow.md).

The same check catches a few others. Kafka against Postgres is usually a log against a store, covered in [Kafka and stream semantics](../../04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics.md). Parquet against Snowflake compares a file format with an engine. Before weighing two tools, ask whether they'd ever sit in the same box on a diagram.

## A worked decision

An app needs: user accounts and orders, a product catalogue with varying attributes, search over product descriptions, a session cache, recommendation by embedding over 200,000 products, and monthly revenue dashboards over 500 million order lines.

| Need | Pattern | Choice | Why not a dedicated store |
|---|---|---|---|
| Accounts, orders | Transactions, joins | Postgres | This is the system of record |
| Catalogue | Varying shape, read by id | `jsonb` columns in Postgres | Joins orders, and GIN handles filters |
| Product search | Words and ranking | Postgres FTS first | Move when relevance becomes a project |
| Sessions | Key lookup, can be lost | Redis, or a Postgres table | Redis is justified if already run; this is derived data |
| Recommendations | Nearest neighbour, 200,000 items | pgvector, or exact search | Flat search is about 3 ms at this size by our table |
| Revenue dashboards | Scan and aggregate | A warehouse, fed by a pipeline | This one does need a different store |

Two stores, perhaps three, where the first instinct might name six. If search relevance later becomes a product of its own, you add Elasticsearch fed from Postgres, and nothing else has to change. It is also an easier migration to make once you know you need it than a premature one is to undo.

## Pitfalls

- **Choosing by data shape instead of access.** JSON-shaped data doesn't require a document store. How you read it decides.
- **Adopting for future scale.** You pay the operating cost now, for a load that might never arrive.
- **Using a search index or cache as the only copy.** They are built as derived data. Check how each [survives a crash](09-persistence.md) before you trust it.
- **Reading "wide-column" as "columnar".** Cassandra isn't a scan engine.
- **Assuming NoSQL means no modelling.** DynamoDB needs more up-front design than a relational schema, not less.
- **Trusting one laptop benchmark, including ours.** These numbers show orders of magnitude on synthetic data. Test your own queries on your own data before you commit.
- **Comparing across layers.** Warehouses compete with warehouses, and orchestrators with orchestrators.
- **Counting only licence and hardware.** Backups, upgrades, on-call and hiring are the real cost of each extra store.

## Try it

1. In `pg_graph`, change the edge count from 500,000 to 3,000,000. How does the time per hop change, and at what hop do most nodes get reached?
2. In `embedded`, add `SELECT * FROM trips WHERE zone = 7` to both databases, with and without an index in SQLite. Which side is faster, and why is the answer less one-sided than the group-by?
3. A team wants MongoDB because "our events are JSON". The events are appended, and read in bulk for daily reports. What would you ask, and what would you likely suggest?
4. In `vectors_flat`, at what corpus size would exact search take longer than a 100 ms budget, and what would you try before installing a new store?

<details><summary>Answers</summary>

1. Fan-out rises from about 5 to about 30 per node, so the reachable set explodes in two or three fewer hops and the query does far more work, with most of it deduplicating nodes already seen. That is where hub-heavy graphs start to hurt in SQL.
2. It selects whole rows, so a column store has to reassemble every column, and a row store reads them directly. An index on `zone` helps SQLite, but at about 1 in 265 it still touches many rows. The gap narrows sharply compared with a group-by over one column.
3. Ask how the data is read. Whole-object lookups by key and varying shape favour a document store; bulk daily reports favour files in an object store, such as Parquet, queried by DuckDB or a warehouse. JSON at ingest says nothing about either. Likely suggestion: append to object storage and leave MongoDB out.
4. Exact search scales linearly, so at this rate about 6 million vectors reach 100 ms. Before a new store, try reducing dimensions, filtering first, or pgvector with an HNSW index if Postgres is already there.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| How do you choose a database? | Start with access patterns: how records are found, how much one query touches, how data changes, size and who operates it. Then match a store. |
| When is Postgres enough? | Usually, until writes outgrow one primary, or you need scans over most of a huge table, multi-region writes, or search as a product. |
| Key-value versus document? | Key-value stores an opaque value read by key. A document store understands the value's fields, so it can index and query them. |
| Is Cassandra a column store? | No. Wide-column means rows with flexible columns under a partition key. It's built for writes by key, not scans. |
| Do you need a vector database? | Not for small corpora: exact search over a million vectors took about 17 ms here. Above that, an index in your existing database is the next step, then a dedicated store. |
| Why not use Elasticsearch as the primary store? | It is refreshed periodically and is built as a derived index. Keep the record elsewhere and rebuild from it. |
| Snowflake versus Airflow? | They don't compete. Snowflake stores and computes; Airflow schedules. Compare warehouses with warehouses and orchestrators with orchestrators. |
| What does a new store really cost? | Backups, upgrades, monitoring, on-call and hiring, and a new set of failure modes on top of the licence. |

## Next

The large-scale right-hand side of the row and column split is in [DE 04: The warehouse](../../04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md). The next pillar in reading order starts with [ingest](../../02-ingest-and-modelling/notes/01-ingest.md).
