---
origin: synthesis
sources:
  - notes/
confidence: high
cleaned: 2026-11-01
---
# 01 — Storage and compute foundations

The physical facts that the rest of data engineering rests on: how data is encoded in a file, how a database lays it out on disk, how work spreads across machines, and how data is split and copied among them. Each of the later pillars makes decisions that only look like preferences until you know this layer.

**Why it comes first.** Almost every debate in the field reduces to one of these mechanisms. "Why is this query slow?" comes down to layout and pruning. "Why did this count drop?" often comes down to replication lag. "Do we need Spark?" comes down to how much one query actually reads. Learn the mechanism once and those stop being matters of taste.

**The story.** We take one million synthetic taxi trips and follow them down the stack. In a CSV they lose their types, so we give them a schema and see how Parquet exploits it. We load them into a row store and a column store and watch each win by about two orders of magnitude on the other's workload. When one machine might not be enough, we build MapReduce by hand, follow how Spark changed it, and then see how far DuckDB gets on a laptop. Finally we split and copy the data across machines and find out what a reader can see when something fails.

## Reading order

| # | Chapter | Question it answers |
|---|---|---|
| 1 | [Encoding and files](notes/01-encoding-and-files.md) | What does a file promise its reader? CSV, Avro, Parquet, Arrow |
| 2 | [Row and column stores](notes/02-row-and-column-stores.md) | Why do OLTP and OLAP need different layouts? |
| 3 | [Distributed compute](notes/03-distributed-compute.md) | What does a cluster cost, and when does one machine suffice? |
| 4 | [Partitioning and replication](notes/04-partitioning-and-replication.md) | Where does each row live, and what can a reader see? |

Then go to [02, ingest and modelling](../02-ingest-and-modelling/README.md). The sequenced path across all seven pillars is in the [curriculum](../CURRICULUM.md).

## Rules of thumb

| Situation | Rule | Why |
|---|---|---|
| A CSV arrives | State the schema on first read | Inference destroys zip codes and big IDs silently |
| Data at rest | Parquet, sorted by the main filter column | Pruning and pushdown need physical order |
| Data between engines | Arrow | Exchange without copying |
| Records in a stream | Avro or Protobuf, with a registry | Evolution is checked, not hoped for |
| Slow warehouse query | Read the plan before adding anything | Most of the fix is pruning and join strategy |
| Considering a cluster | Measure what one query reads after pruning | One machine often suffices |
| Choosing a lake layout | Partition by what you backfill, sort by what you filter | Fine partitions create small files |
| Reading from a replica | Assume it is behind | Async replication lags and can lose writes |

## Deck and practice

- **Deck:** [slides/storage-and-compute-foundations.pptx](slides/storage-and-compute-foundations.pptx), built from [slides/deck.yaml](slides/deck.yaml). Rebuild with `make slides PILLAR=data-engineering/01-storage-and-compute-foundations STRICT=1 PREVIEW=1`.
- **Practice:** [practice/](practice/) has one script per chapter holding that chapter's code. Each prints its output and writes only to a temporary folder. Run from `practice/`:

```bash
uv run --with duckdb --with pyarrow --with numpy --with polars --with fastavro python 01_encoding_and_files.py
uv run --with duckdb --with pyarrow --with numpy python 02_row_and_column_stores.py
uv run --with duckdb --with pyarrow --with numpy --with polars --with pyspark python 03_distributed_compute.py   # needs Java for the Spark sections
uv run --with duckdb --with numpy python 04_partitioning_and_replication.py
```

Sources: [references.md](references.md).
