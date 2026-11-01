---
origin: curated
sources:
  - ../references.md
confidence: high
cleaned: 2026-11-01
---
# Storage and compute foundations: references

> The sources behind the four chapters in [notes/](notes/). Books shared across the data-engineering pillars are listed in the [subject references](../references.md). PDFs are in [../sources/](../sources/).

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| ★ Kleppmann, [*Designing Data-Intensive Applications*](https://dataintensive.net/) (O'Reilly, 2017) | ch. 3 (storage, column stores), 4 (encoding), 5 (replication), 6 (partitioning), 10 (batch) | [PDF](../sources/kleppmann-designing-data-intensive-applications.pdf) | [01](notes/01-encoding-and-files.md) · [02](notes/02-row-and-column-stores.md) · [03](notes/03-distributed-compute.md) · [04](notes/04-partitioning-and-replication.md) |
| Kleppmann and Riccomini, [*Designing Data-Intensive Applications*, 2nd ed.](https://martin.kleppmann.com/2026/03/24/designing-data-intensive-applications-2e.html) (O'Reilly, 2026) | Not read for these notes, which follow the 1st edition held in this repo | none | Further reading |
| Kimball and Ross, [*The Data Warehouse Toolkit*](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/), 2nd ed. (Wiley, 2002) | ch. 1 (operational vs warehouse) | [PDF](../sources/data-warehouse-toolkit.pdf) | [02](notes/02-row-and-column-stores.md) |

## Core papers

★ marks a paper whose text changed a claim in the notes. All were read in full or in the sections cited; the PDFs for the older papers are public at the links.

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| Ghemawat, Gobioff and Leung, [*The Google File System*](https://doi.org/10.1145/1165389.945450) (SOSP 2003) | Designs storage around failure as the normal case, which MapReduce builds on | [public](https://research.google.com/archive/gfs-sosp2003.pdf) | [03](notes/03-distributed-compute.md) |
| ★ Dean and Ghemawat, [*MapReduce*](https://research.google.com/archive/mapreduce-osdi04.pdf) (OSDI 2004; [CACM 2008](https://doi.org/10.1145/1327452.1327492)) | The shuffle, atomic output, and backup tasks: a sort took 44% longer without them | [public](https://research.google.com/archive/mapreduce-osdi04.pdf) | [03](notes/03-distributed-compute.md) |
| Stonebraker et al., [*C-Store*](https://doi.org/10.1145/3226595.3226638) (VLDB 2005; 2018 reprint) | Read-optimised relational store with overlapping column projections | [public](https://web.stanford.edu/class/cs345d-01/rl/cstore.pdf) | [02](notes/02-row-and-column-stores.md) |
| Chang et al., [*Bigtable*](https://research.google.com/archive/bigtable-osdi06.pdf) (OSDI 2006) | The source of column families, which are not column stores | [public](https://research.google.com/archive/bigtable-osdi06.pdf) | [02](notes/02-row-and-column-stores.md) |
| DeCandia et al., [*Dynamo*](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) (SOSP 2007) | Always-writeable, leaderless replication with R and W quorums | [public](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) | [04](notes/04-partitioning-and-replication.md) |
| ★ Abadi, Madden and Hachem, [*Column-Stores vs. Row-Stores*](https://doi.org/10.1145/1376616.1376712) (SIGMOD 2008) | Layout alone is not enough: late materialisation about 3x, compression about 2x, invisible joins about 50% | [public](https://www.cs.umd.edu/~abadi/papers/abadi-sigmod08.pdf) | [02](notes/02-row-and-column-stores.md) |
| Melnik et al., [*Dremel*](https://doi.org/10.1145/1953122.1953148) (VLDB 2010; CACM 2011) | Columnar layout for nested data, which Parquet descends from | [public](https://research.google.com/pubs/archive/36632.pdf) | [01](notes/01-encoding-and-files.md) |
| Zaharia et al., [*Resilient Distributed Datasets*](https://www.usenix.org/conference/nsdi12/technical-sessions/presentation/zaharia) (NSDI 2012) | Lineage instead of replicated intermediate data; up to 20x faster than Hadoop on iterative applications | [public](https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final138.pdf) | [03](notes/03-distributed-compute.md) |
| Armbrust et al., [*Spark SQL*](https://doi.org/10.1145/2723372.2742797) (SIGMOD 2015) | DataFrames and the Catalyst optimiser | [public](https://people.csail.mit.edu/matei/papers/2015/sigmod_spark_sql.pdf) | [03](notes/03-distributed-compute.md) |
| ★ McSherry, Isard and Murray, [*Scalability! But at what COST?*](https://www.usenix.org/conference/hotos15/workshop-program/presentation/mcsherry) (HotOS 2015) | The metric that compares a cluster with one good thread. Graph workloads on 2014 systems | [public](https://www.usenix.org/system/files/conference/hotos15/hotos15-paper-mcsherry.pdf) | [03](notes/03-distributed-compute.md) |
| Raasveldt and Mühleisen, [*DuckDB*](https://doi.org/10.1145/3299869.3320212) (SIGMOD 2019) | Embeddable analytics: the row-store gap, vectorised execution, 1,024-value vectors | [PDF](../sources/raasveldt-2019-duckdb.pdf) | [02](notes/02-row-and-column-stores.md) |

## Formats and engine docs

| Doc | Use | Maps to |
|---|---|---|
| [Parquet file format](https://parquet.apache.org/docs/file-format/) | Row groups, column chunks, pages, footer | [01](notes/01-encoding-and-files.md) |
| [Arrow columnar format](https://arrow.apache.org/docs/format/Columnar.html) | Buffers and in-memory layout | [01](notes/01-encoding-and-files.md) |
| [DuckDB docs](https://duckdb.org/docs/stable/) | `read_parquet`, partitioned writes, memory limits | [01](notes/01-encoding-and-files.md) · [03](notes/03-distributed-compute.md) · [04](notes/04-partitioning-and-replication.md) |
| [Polars lazy API](https://docs.pola.rs/user-guide/lazy/) | Lazy plans and pushdown | [03](notes/03-distributed-compute.md) |
| [Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html) | Adaptive execution, shuffle partitions, broadcast joins | [03](notes/03-distributed-compute.md) |

## Posts

| Post | Treat as | Maps to |
|---|---|---|
| Tigani, ["Big Data is Dead"](https://motherduck.com/blog/big-data-is-dead/) | Informed opinion from a vendor founder; figures from memory, as he says | [03](notes/03-distributed-compute.md) |

## Courses and videos

| Course | Platform | Cost | Supports |
|---|---|---|---|
| Kleppmann, [Distributed Systems lecture series](https://www.youtube.com/playlist?list=PLeKd45zvjcDFUEv_ohr_HdUFe97RItdiB) (University of Cambridge, 8 lectures, about 7 hours; [notes](https://www.cl.cam.ac.uk/teaching/2122/ConcDisSys/materials.html)) | YouTube | Free | [04](notes/04-partitioning-and-replication.md): replication, quorums, consistency |
| [CMU 15-445/645, Intro to Database Systems](https://15445.courses.cs.cmu.edu/) (Pavlo; recorded lectures on YouTube from the CMU Database Group, course site lists the current term) | Web, YouTube | Free | [02](notes/02-row-and-column-stores.md): storage, indexes, query execution |
| [DE Zoomcamp, batch module](https://github.com/DataTalksClub/data-engineering-zoomcamp) (DataTalks.Club; vendored here at [05-batch](../04-warehouse-lakehouse-streaming/practice/datatalks-de/05-batch/)) | GitHub, YouTube | Free | [03](notes/03-distributed-compute.md): Spark on real taxi data |
