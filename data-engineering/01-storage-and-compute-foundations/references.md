---
origin: curated
sources:
  - ../references.md
confidence: high
cleaned: 2026-11-02
---
# Storage and compute foundations: references

> The sources behind the ten chapters in [notes/](notes/). Books shared across the data-engineering pillars are listed in the [subject references](../references.md). PDFs are in [../sources/](../sources/).

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| ★ **Core text.** Kleppmann, [*Designing Data-Intensive Applications*](https://dataintensive.net/) (O'Reilly, 2017) | Read in full, reference lists omitted. ch. 1 (reliability, load, percentiles), 2 (data models), 3 (storage, B-trees, LSM, column stores), 4 (encoding), 5 (replication), 6 (partitioning), 7 (transactions), 8 (faults, clocks, truth), 9 (consistency, consensus), 10 (batch). See the [reading map](../references.md#reading-map-designing-data-intensive-applications) | [PDF](../sources/kleppmann-designing-data-intensive-applications.pdf) | [01](notes/01-data-systems-and-data-models.md) · [02](notes/02-encoding-and-files.md) · [03](notes/03-row-and-column-stores.md) · [04](notes/04-transactions-and-isolation.md) · [05](notes/05-partitioning-and-replication.md) · [06](notes/06-when-distributed-systems-fail.md) · [07](notes/07-consistency-and-consensus.md) · [08](notes/08-distributed-compute.md), [09](notes/09-persistence.md) (the sidebar "Replication and Durability" in ch. 7, and the introduction to Part III) |
| Kleppmann and Riccomini, [*Designing Data-Intensive Applications*, 2nd ed.](https://martin.kleppmann.com/2026/03/24/designing-data-intensive-applications-2e.html) (O'Reilly, 2026) | Not read for these notes, which follow the 1st edition held in this repo | none | Further reading |
| Kimball and Ross, [*The Data Warehouse Toolkit*](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/), 2nd ed. (Wiley, 2002) | ch. 1 (operational vs warehouse) | [PDF](../sources/data-warehouse-toolkit.pdf) | [03](notes/03-row-and-column-stores.md) |

## Core papers

★ marks a paper whose text changed a claim in the notes. All were read in full or in the sections cited, except Codd, Lamport, Ports and Grittner, and Ongaro and Ousterhout. Those four are cited for one idea each as the book presents it, with the links checked, and were not read in full for these notes. The PDFs for the older papers are public at the links.

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| Codd, [*A Relational Model of Data for Large Shared Data Banks*](https://doi.org/10.1145/362384.362685) (CACM 1970) | Where the relational model comes from | [DOI](https://doi.org/10.1145/362384.362685) | [01](notes/01-data-systems-and-data-models.md) |
| Lamport, [*Time, Clocks, and the Ordering of Events in a Distributed System*](https://doi.org/10.1145/359545.359563) (CACM 1978) | Happened-before and logical clocks | [DOI](https://doi.org/10.1145/359545.359563) | [07](notes/07-consistency-and-consensus.md) |
| Ghemawat, Gobioff and Leung, [*The Google File System*](https://doi.org/10.1145/1165389.945450) (SOSP 2003) | Designs storage around failure as the normal case, which MapReduce builds on | [public](https://research.google.com/archive/gfs-sosp2003.pdf) | [08](notes/08-distributed-compute.md) |
| ★ Dean and Ghemawat, [*MapReduce*](https://research.google.com/archive/mapreduce-osdi04.pdf) (OSDI 2004; [CACM 2008](https://doi.org/10.1145/1327452.1327492)) | The shuffle, atomic output, and backup tasks: a sort took 44% longer without them | [public](https://research.google.com/archive/mapreduce-osdi04.pdf) | [08](notes/08-distributed-compute.md) |
| Stonebraker et al., [*C-Store*](https://doi.org/10.1145/3226595.3226638) (VLDB 2005; 2018 reprint) | Read-optimised relational store with overlapping column projections | [public](https://web.stanford.edu/class/cs345d-01/rl/cstore.pdf) | [03](notes/03-row-and-column-stores.md) |
| Chang et al., [*Bigtable*](https://research.google.com/archive/bigtable-osdi06.pdf) (OSDI 2006) | The source of column families, which are not column stores | [public](https://research.google.com/archive/bigtable-osdi06.pdf) | [03](notes/03-row-and-column-stores.md) |
| DeCandia et al., [*Dynamo*](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) (SOSP 2007) | Always-writeable, leaderless replication with R and W quorums | [public](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) | [05](notes/05-partitioning-and-replication.md) |
| ★ Abadi, Madden and Hachem, [*Column-Stores vs. Row-Stores*](https://doi.org/10.1145/1376616.1376712) (SIGMOD 2008) | Layout alone is not enough: late materialisation about 3x, compression about 2x, invisible joins about 50% | [public](https://www.cs.umd.edu/~abadi/papers/abadi-sigmod08.pdf) | [03](notes/03-row-and-column-stores.md) |
| Melnik et al., [*Dremel*](https://doi.org/10.1145/1953122.1953148) (VLDB 2010; CACM 2011) | Columnar layout for nested data, which Parquet descends from | [public](https://research.google.com/pubs/archive/36632.pdf) | [02](notes/02-encoding-and-files.md) |
| Zaharia et al., [*Resilient Distributed Datasets*](https://www.usenix.org/conference/nsdi12/technical-sessions/presentation/zaharia) (NSDI 2012) | Lineage instead of replicated intermediate data; up to 20x faster than Hadoop on iterative applications | [public](https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final138.pdf) | [08](notes/08-distributed-compute.md) |
| Armbrust et al., [*Spark SQL*](https://doi.org/10.1145/2723372.2742797) (SIGMOD 2015) | DataFrames and the Catalyst optimiser | [public](https://people.csail.mit.edu/matei/papers/2015/sigmod_spark_sql.pdf) | [08](notes/08-distributed-compute.md) |
| Ports and Grittner, [*Serializable Snapshot Isolation in PostgreSQL*](https://arxiv.org/abs/1208.4179) (VLDB 2012) | How Postgres implements the serializable level measured in the chapter | [public](https://arxiv.org/abs/1208.4179) | [04](notes/04-transactions-and-isolation.md) |
| Ongaro and Ousterhout, [*In Search of an Understandable Consensus Algorithm*](https://raft.github.io/raft.pdf) (USENIX ATC 2014) | The design the toy consensus simulation is shaped after: terms, votes, log comparison | [public](https://raft.github.io/raft.pdf) | [07](notes/07-consistency-and-consensus.md) |
| ★ McSherry, Isard and Murray, [*Scalability! But at what COST?*](https://www.usenix.org/conference/hotos15/workshop-program/presentation/mcsherry) (HotOS 2015) | The metric that compares a cluster with one good thread. Graph workloads on 2014 systems | [public](https://www.usenix.org/system/files/conference/hotos15/hotos15-paper-mcsherry.pdf) | [08](notes/08-distributed-compute.md) |
| Raasveldt and Mühleisen, [*DuckDB*](https://doi.org/10.1145/3299869.3320212) (SIGMOD 2019) | Embeddable analytics: the row-store gap, vectorised execution, 1,024-value vectors | [PDF](../sources/raasveldt-2019-duckdb.pdf) | [03](notes/03-row-and-column-stores.md) |
| Rebello et al., [*Can Applications Recover from fsync Failures?*](https://www.usenix.org/conference/atc20/presentation/rebello) (USENIX ATC 2020) | Abstract and introduction read. What file systems and databases do after a failed fsync | none | [09](notes/09-persistence.md) |
| Pillai et al., [*All File Systems Are Not Created Equal*](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai) (OSDI 2014) | Abstract read. Crash consistency in applications depends on file system behaviour | none | [09](notes/09-persistence.md) |
| Stonebraker and Pavlo, [*What Goes Around Comes Around... And Around...*](https://db.cs.cmu.edu/papers/2024/whatgoesaround-sigmodrec2024.pdf) (SIGMOD Record 2024) | Sections read. New data models keep being absorbed by relational systems; the frame for choosing a store | none | [10](notes/10-choosing-a-store.md) |

## Formats and engine docs

| Doc | Use | Maps to |
|---|---|---|
| [Parquet file format](https://parquet.apache.org/docs/file-format/) | Row groups, column chunks, pages, footer | [02](notes/02-encoding-and-files.md) |
| [Arrow columnar format](https://arrow.apache.org/docs/format/Columnar.html) | Buffers and in-memory layout | [02](notes/02-encoding-and-files.md) |
| [DuckDB docs](https://duckdb.org/docs/stable/) | `read_parquet`, partitioned writes, memory limits | [02](notes/02-encoding-and-files.md) · [08](notes/08-distributed-compute.md) · [05](notes/05-partitioning-and-replication.md) |
| [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [serialization caveats](https://www.postgresql.org/docs/current/mvcc-caveats.html) | What each level actually does in Postgres, and the errors to retry | [04](notes/04-transactions-and-isolation.md) |
| [PostgreSQL `PREPARE TRANSACTION`](https://www.postgresql.org/docs/current/sql-prepare-transaction.html) | Two-phase commit you can leave in doubt | [07](notes/07-consistency-and-consensus.md) |
| [SQLite isolation](https://www.sqlite.org/isolation.html) | One writer at a time, and what that rules out | [04](notes/04-transactions-and-isolation.md) |
| [Airflow tasks](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html), [scheduler](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/scheduler.html) | Heartbeat timeouts, and why schedulers rely on database row locks | [06](notes/06-when-distributed-systems-fail.md) · [07](notes/07-consistency-and-consensus.md) |
| [Spark configuration](https://spark.apache.org/docs/latest/configuration.html) | Network timeouts as a tuning trade-off | [06](notes/06-when-distributed-systems-fail.md) |
| [Iceberg spec](https://iceberg.apache.org/spec/), [Delta concurrency control](https://docs.delta.io/latest/concurrency-control.html) | Compare-and-swap commits, which the isolation and consensus chapters preview | [04](notes/04-transactions-and-isolation.md) · [07](notes/07-consistency-and-consensus.md) |
| [KIP-595, a Raft protocol for the Kafka metadata quorum](https://cwiki.apache.org/confluence/display/KAFKA/KIP-595%3A+A+Raft+Protocol+for+the+Metadata+Quorum) | Consensus in a system you are likely to run | [07](notes/07-consistency-and-consensus.md) |
| [Polars lazy API](https://docs.pola.rs/user-guide/lazy/) | Lazy plans and pushdown | [08](notes/08-distributed-compute.md) |
| [Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html) | Adaptive execution, shuffle partitions, broadcast joins | [08](notes/08-distributed-compute.md) |
| Postgres: [WAL intro](https://www.postgresql.org/docs/current/wal-intro.html), [reliability](https://www.postgresql.org/docs/current/wal-reliability.html), [async commit](https://www.postgresql.org/docs/current/wal-async-commit.html), [WAL settings](https://www.postgresql.org/docs/current/runtime-config-wal.html), [standby](https://www.postgresql.org/docs/current/warm-standby.html), [continuous archiving](https://www.postgresql.org/docs/current/continuous-archiving.html), [fsync errors (wiki)](https://wiki.postgresql.org/wiki/Fsync_Errors) | What a commit promises and the settings that change it. Code run on 16.2 | [09](notes/09-persistence.md) |
| [fsync(2), Linux](https://man7.org/linux/man-pages/man2/fsync.2.html), plus `man 2 fsync` on macOS | What the call does and does not promise | [09](notes/09-persistence.md) |
| [SQLite, How To Corrupt](https://www.sqlite.org/howtocorrupt.html), [Appropriate Uses](https://www.sqlite.org/whentouse.html) | Ways durability breaks; when an embedded database fits | [09](notes/09-persistence.md), [10](notes/10-choosing-a-store.md) |
| [S3 data durability](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DataDurability.html), [AWS RTO and RPO](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/business-continuity-plan-bcp.html) | Durability numbers and recovery objectives | [09](notes/09-persistence.md) |
| [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [Redis data types](https://redis.io/docs/latest/develop/data-types/) | RDB and AOF trade-offs; the key-value access pattern | [09](notes/09-persistence.md), [10](notes/10-choosing-a-store.md) |
| Postgres as a general store: [text search](https://www.postgresql.org/docs/current/textsearch-intro.html), [JSON types](https://www.postgresql.org/docs/current/datatype-json.html), [partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html), [pgvector](https://github.com/pgvector/pgvector) | How far one server goes. Code run on 16.2; pgvector read and not run | [10](notes/10-choosing-a-store.md) |
| [DuckDB, Why DuckDB](https://duckdb.org/why_duckdb) | Embedded analytics | [10](notes/10-choosing-a-store.md) |
| [DynamoDB NoSQL design](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-general-nosql-design.html), [Cassandra architecture](https://cassandra.apache.org/doc/latest/cassandra/architecture/overview.html) | Designing from access patterns; read and not run | [10](notes/10-choosing-a-store.md) |
| MongoDB: [data modeling](https://www.mongodb.com/docs/manual/data-modeling/), [transactions](https://www.mongodb.com/docs/manual/core/transactions/) | Document stores; read and not run | [10](notes/10-choosing-a-store.md) |
| [Elasticsearch near real-time search](https://www.elastic.co/docs/manage-data/data-store/near-real-time-search) | Search stores and refresh delay; read and not run | [10](notes/10-choosing-a-store.md) |
| [Prometheus storage](https://prometheus.io/docs/prometheus/latest/storage/), [Timescale hypertables](https://docs.timescale.com/use-timescale/latest/hypertables/) | Time-series stores; read and not run | [10](notes/10-choosing-a-store.md) |
| [Neo4j, graph databases](https://neo4j.com/docs/getting-started/graph-database/) | Graph stores; read and not run | [10](notes/10-choosing-a-store.md) |

## Posts

| Post | Treat as | Maps to |
|---|---|---|
| Tigani, ["Big Data is Dead"](https://motherduck.com/blog/big-data-is-dead/) | Informed opinion from a vendor founder; figures from memory, as he says | [08](notes/08-distributed-compute.md) |

## Courses and videos

| Course | Platform | Cost | Supports |
|---|---|---|---|
| Kleppmann, [Distributed Systems lecture series](https://www.youtube.com/playlist?list=PLeKd45zvjcDFUEv_ohr_HdUFe97RItdiB) (University of Cambridge, 8 lectures, about 7 hours; [notes](https://www.cl.cam.ac.uk/teaching/2122/ConcDisSys/materials.html)) | YouTube | Free | [05](notes/05-partitioning-and-replication.md): replication, quorums, consistency, and background for [06](notes/06-when-distributed-systems-fail.md) and [07](notes/07-consistency-and-consensus.md) |
| [CMU 15-445/645, Intro to Database Systems](https://15445.courses.cs.cmu.edu/) (Pavlo; recorded lectures on YouTube from the CMU Database Group, course site lists the current term) | Web, YouTube | Free | [03](notes/03-row-and-column-stores.md): storage, indexes, query execution |
| [DE Zoomcamp, batch module](https://github.com/DataTalksClub/data-engineering-zoomcamp) (DataTalks.Club; vendored here at [05-batch](../04-warehouse-lakehouse-streaming/practice/datatalks-de/05-batch/)) | GitHub, YouTube | Free | [08](notes/08-distributed-compute.md): Spark on real taxi data |
