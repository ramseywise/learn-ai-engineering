---
origin: curated
sources:
  - https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf
  - https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf
  - https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf
confidence: high
cleaned: 2026-11-01
---
# References: warehouse, lakehouse and streaming

★ marks a reading that changed a claim in the notes. Links were checked on 2026-11-01 unless noted.

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| ★ Kleppmann, [*Designing Data-Intensive Applications*](https://dataintensive.net/) (O'Reilly, 2017) | 3, 6, 10, 11, 12 | [PDF](../sources/kleppmann-designing-data-intensive-applications.pdf) | [01](notes/01-warehouse-and-store.md), [04](notes/04-kafka-and-stream-semantics.md) |
| Reis and Housley, *Fundamentals of Data Engineering* (O'Reilly, 2022) | Lifecycle chapters; the publisher page blocks automated checks | none | Background for all |

## Core papers

| Paper | Venue | PDF | Maps to |
|---|---|---|---|
| ★ Armbrust et al., [Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores](https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf) | PVLDB 13(12), 2020 | [PDF](../sources/armbrust-2020-delta-lake.pdf) | [02](notes/02-table-formats.md) |
| ★ Armbrust, Ghodsi, Xin, Zaharia, [Lakehouse: A New Generation of Open Platforms](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf) | CIDR 2021 | [PDF](../sources/zaharia-2021-lakehouse.pdf) | [03](notes/03-lakehouse-vs-warehouse.md) |
| ★ Akidau et al., [The Dataflow Model](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf) | PVLDB 8(12), 2015 | none | [04](notes/04-kafka-and-stream-semantics.md) |
| Raasveldt and Mühleisen, [DuckDB: an Embeddable Analytical Database](https://mytherin.github.io/papers/2019-duckdbdemo.pdf) | SIGMOD 2019 demo | [PDF](../sources/raasveldt-2019-duckdb.pdf) | [01](notes/01-warehouse-and-store.md), [03](notes/03-lakehouse-vs-warehouse.md) |

## Specifications and docs

| Source | Maps to |
|---|---|
| [Apache Iceberg table spec](https://iceberg.apache.org/spec/), [partitioning](https://iceberg.apache.org/docs/latest/partitioning/) | [02](notes/02-table-formats.md) |
| [Apache Hudi table types](https://hudi.apache.org/docs/table_types) | [02](notes/02-table-formats.md) |
| [delta-rs](https://delta-io.github.io/delta-rs/), [PyIceberg](https://py.iceberg.apache.org/), [Delta deletion vectors](https://docs.delta.io/latest/delta-deletion-vectors.html) | [02](notes/02-table-formats.md) |
| [Kafka design docs](https://kafka.apache.org/42/design/design), [KIP-98](https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging) | [04](notes/04-kafka-and-stream-semantics.md) |
| [Flink time](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/), [Spark Structured Streaming](https://spark.apache.org/docs/latest/streaming/apis-on-dataframes-and-datasets.html) | [04](notes/04-kafka-and-stream-semantics.md) |
| [BigQuery pricing](https://cloud.google.com/bigquery/pricing), [slots](https://cloud.google.com/bigquery/docs/slots), [cost best practices](https://cloud.google.com/bigquery/docs/best-practices-costs), [VPC network pricing](https://cloud.google.com/vpc/network-pricing), [Cloud Storage pricing](https://cloud.google.com/storage/pricing) | [05](notes/05-cost.md) |

## Courses and videos

| Course | Platform | Cost | Notes | Weeks |
|---|---|---|---|---|
| [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) | DataTalksClub | Free | Modules 03, 05, 06 are the [practice folder](practice/datatalks-de) | About 3 for these modules |
| [Kafka 101](https://developer.confluent.io/courses/apache-kafka/events/) | Confluent | Free | Log concepts with a real broker; pairs with [04](notes/04-kafka-and-stream-semantics.md) | Under 1 |
| [Lakehouse Fundamentals](https://www.databricks.com/learn/training/lakehouse-fundamentals) | Databricks | Free | The vendor's own framing; read beside [03](notes/03-lakehouse-vs-warehouse.md) | Under 1 |
| [Distributed Systems lectures](https://www.youtube.com/playlist?list=PLeKd45zvjcDFUEv_ohr_HdUFe97RItdiB) (Kleppmann) | YouTube | Free | Background on logs, replication and consistency | About 1 |
