---
origin: synthesis
sources:
  - notes/
confidence: high
cleaned: 2026-11-01
---
# 01 — Storage and compute foundations

The logic that the rest of data engineering rests on: what a data system promises, how data is encoded and laid out, what happens when two writers meet, how data is split and copied across machines, what goes wrong there, how machines agree anyway, and how work spreads over all of it. Each of the later pillars makes decisions that only look like preferences until you know this layer.

The pillar follows [*Designing Data-Intensive Applications*](https://dataintensive.net/) (Kleppmann, 2017), the [core text of this subject](../README.md#the-core-text), and retells chapters 1 to 10 with code you can run. Every chapter gives page pointers, so you can read the book alongside it. The full [reading map](../CURRICULUM.md#reading-map-designing-data-intensive-applications) says where each of its twelve chapters is used.

**Why it comes first.** Almost every debate in the field reduces to one of these mechanisms. "Why is this query slow?" comes down to layout and pruning. "Why did this count drop?" often comes down to replication lag. "Why is the balance wrong when each job looks right?" comes down to isolation. "Is exactly-once real?" comes down to what a timeout can and cannot tell you. "Do we need Spark?" comes down to how much one query actually reads. Learn the mechanism once and those stop being matters of taste.

**The story.** It starts with one machine and adds trouble a step at a time. A taxi app is a small crowd of storage systems, so we first fix the words for judging one, and measure why the mean hides the tail. We follow one million synthetic trips into a file, where a CSV loses their types and Parquet earns them back, then into a row store and a column store, which each win by about two orders of magnitude on the other's workload. Then a second writer arrives. Running real Postgres, we produce lost updates and write skew, and see the database refuse them only at the right isolation level. The data outgrows one machine, so we split and copy it, and find out what a reader can see. Next the network and the clocks stop cooperating: a timed-out write may have applied, and last-write-wins loses data on a skew of milliseconds. So we ask how machines can agree on anything, and build a small consensus protocol that survives thousands of random failures until we weaken its quorum. Finally we compute across all of it, building MapReduce by hand, following how Spark changed it and seeing how far DuckDB gets on a laptop.

## Reading order

| # | Chapter | Question it answers | Book |
|---|---|---|---|
| 1 | [Data systems and data models](notes/01-data-systems-and-data-models.md) | What are you promising, and how do you measure it? Relational, document, graph | ch. 1, 2 |
| 2 | [Encoding and files](notes/02-encoding-and-files.md) | What does a file promise its reader? CSV, Avro, Parquet, Arrow | ch. 4, 3 |
| 3 | [Row and column stores](notes/03-row-and-column-stores.md) | Why do OLTP and OLAP need different layouts? B-trees and LSM-trees | ch. 3 |
| 4 | [Transactions and isolation](notes/04-transactions-and-isolation.md) | What goes wrong when two writers meet, and which level stops it? | ch. 7 |
| 5 | [Partitioning and replication](notes/05-partitioning-and-replication.md) | Where does each row live, and what can a reader see? | ch. 5, 6 |
| 6 | [When distributed systems fail](notes/06-when-distributed-systems-fail.md) | What can a node know, given timeouts, clocks and pauses? | ch. 8 |
| 7 | [Consistency and consensus](notes/07-consistency-and-consensus.md) | How do machines agree? Linearizability, ordering, 2PC, quorums | ch. 9 |
| 8 | [Distributed compute](notes/08-distributed-compute.md) | What does a cluster cost, and when does one machine suffice? | ch. 10 |

Then go to [02, ingest and modelling](../02-ingest-and-modelling/README.md). The sequenced path across all seven pillars is in the [curriculum](../CURRICULUM.md).

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [Programming](../../programming/README.md) | Python and SQL fluency, which the zoomcamps assume |

**Feeds into**

| Chapter | Why |
|---|---|
| None in other subjects | Nothing outside this subject links here yet |

## Rules of thumb

| Situation | Rule | Why |
|---|---|---|
| Stating a performance goal | Use percentiles, measured from the client, and merge histograms | Means hide the tail, and percentiles cannot be averaged |
| A CSV arrives | State the schema on first read | Inference destroys zip codes and big IDs silently |
| Data at rest | Parquet, sorted by the main filter column | Pruning and pushdown need physical order |
| Data between engines | Arrow | Exchange without copying |
| Records in a stream | Avro or Protobuf, with a registry | Evolution is checked, not hoped for |
| Slow warehouse query | Read the plan before adding anything | Most of the fix is pruning and join strategy |
| Read, decide, then write | Use serializable isolation or lock explicitly, and retry aborts | Snapshot isolation allows write skew |
| A retry that has effects | Reuse one request ID from the client to the store | A timeout does not say whether the write applied |
| Ordering events across machines | Do not use wall clocks, and fence stale lock holders | Skew loses writes, and pauses outlive leases |
| Reading from a replica | Assume it is behind | Async replication lags and can lose writes |
| A quorum store | Do not assume `w + r > n` is linearizable | Reads can still go backwards |
| Needing agreement | Use a coordination service or a database, not your own protocol | Consensus is easy to get wrong in ways tests rarely show |
| Choosing a lake layout | Partition by what you backfill, sort by what you filter | Fine partitions create small files |
| Considering a cluster | Measure what one query reads after pruning | One machine often suffices |

## Deck and practice

- **Deck:** [slides/storage-and-compute-foundations.pptx](slides/storage-and-compute-foundations.pptx), [pdf](slides/storage-and-compute-foundations.pdf), built from [slides/deck.yaml](slides/deck.yaml). Rebuild with `make slides PILLAR=data-engineering/01-storage-and-compute-foundations STRICT=1 PREVIEW=1`.
- **Practice:** [practice/](practice/) has one script per chapter holding that chapter's code. Each prints its output and writes only to a temporary folder. Scripts 04 and 07 install a real PostgreSQL 16 from a Python wheel, with no Docker or system install. Run from `practice/`:

```bash
uv run --with numpy python 01_data_systems_and_data_models.py
uv run --with duckdb --with pyarrow --with numpy --with polars --with fastavro python 02_encoding_and_files.py
uv run --with duckdb --with pyarrow --with numpy python 03_row_and_column_stores.py
uv run --no-project --python 3.12 --with pgserver --with 'psycopg[binary]' python 04_transactions_and_isolation.py
uv run --with duckdb --with numpy python 05_partitioning_and_replication.py
uv run --with numpy python 06_when_distributed_systems_fail.py
uv run --no-project --python 3.12 --with pgserver --with 'psycopg[binary]' python 07_consistency_and_consensus.py
uv run --with duckdb --with pyarrow --with numpy --with polars --with pyspark python 08_distributed_compute.py   # needs Java for the Spark sections
```

## Primary texts

- Kleppmann, *Designing Data-Intensive Applications*: chapters 1 to 10 run through this pillar
- Kimball and Ross, *The Data Warehouse Toolkit*, ch. 1
- Dean and Ghemawat, *MapReduce*

Everything else: [references.md](references.md).
