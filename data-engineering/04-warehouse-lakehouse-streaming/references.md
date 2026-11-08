---
origin: curated
sources:
  - https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf
  - https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf
  - https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf
confidence: high
cleaned: 2026-11-02
---
# References: warehouse, lakehouse and streaming

★ marks a reading that changed a claim in the notes. Links were checked on 2026-11-01 unless noted; rows for the warehouse rewrite and object storage were read on 2026-11-02.

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| ★ Kleppmann, [*Designing Data-Intensive Applications*](https://dataintensive.net/) (O'Reilly, 2017) | ch. 3, 6, 10 (warehouse and store); ch. 7 (MVCC, optimistic concurrency) and ch. 9 (commit points, total order) behind the table-format log; ch. 11 (log brokers, time, joins, fault tolerance); ch. 12 (system of record, lambda, unbundling, timeliness and integrity) | [PDF](../sources/kleppmann-designing-data-intensive-applications.pdf) | [01](notes/01-warehouse-and-store.md), [02](notes/02-table-formats.md), [03](notes/03-lakehouse-vs-warehouse.md), [04](notes/04-kafka-and-stream-semantics.md) |
| ★ Kimball and Ross, [*The Data Warehouse Toolkit*](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/), 2nd ed. (Wiley, 2002) | Chapter PDFs in [sources/data-warehouse-toolkit/](../sources/data-warehouse-toolkit/). Folded in as: ch. 5 → [01](notes/01-warehouse-and-store.md#a-small-hot-partition-for-todays-rows) (real-time partition sizes by fact grain; the accumulating-snapshot figure does not reproduce). Notes cite it as `(*Data Warehouse Toolkit*, ch. N)`. The chapter text is the 2nd edition (2002) | [ch. 5](../sources/data-warehouse-toolkit/ch05-order-management.pdf) | [01](notes/01-warehouse-and-store.md) |
| Reis and Housley, *Fundamentals of Data Engineering* (O'Reilly, 2022) | Lifecycle chapters; the publisher page blocks automated checks | none | Background for all |

## Core papers

| Paper | Venue | PDF | Maps to |
|---|---|---|---|
| ★ Armbrust et al., [Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores](https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf) | PVLDB 13(12), 2020 | [PDF](../sources/armbrust-2020-delta-lake.pdf) | [02](notes/02-table-formats.md) |
| ★ Armbrust, Ghodsi, Xin, Zaharia, [Lakehouse: A New Generation of Open Platforms](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf) | CIDR 2021 | [PDF](../sources/zaharia-2021-lakehouse.pdf) | [03](notes/03-lakehouse-vs-warehouse.md) |
| ★ Akidau et al., [The Dataflow Model](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf) | PVLDB 8(12), 2015 | none | [04](notes/04-kafka-and-stream-semantics.md) |
| Raasveldt and Mühleisen, [DuckDB: an Embeddable Analytical Database](https://mytherin.github.io/papers/2019-duckdbdemo.pdf) | SIGMOD 2019 demo | [PDF](../sources/raasveldt-2019-duckdb.pdf) | [01](notes/01-warehouse-and-store.md), [03](notes/03-lakehouse-vs-warehouse.md) |
| Dageville et al., [The Snowflake Elastic Data Warehouse](https://15721.courses.cs.cmu.edu/spring2024/papers/19-snowflake/p215-dageville-snowflake.pdf) | SIGMOD 2016 | none | [01](notes/01-warehouse-and-store.md) |
| Armenatzoglou et al., [Amazon Redshift Re-invented](https://www.amazon.science/publications/amazon-redshift-re-invented) | SIGMOD 2022 | none | [01](notes/01-warehouse-and-store.md) |

## Specifications and docs

| Source | Maps to |
|---|---|
| [Apache Iceberg table spec](https://iceberg.apache.org/spec/), [partitioning](https://iceberg.apache.org/docs/latest/partitioning/) | [02](notes/02-table-formats.md) |
| [Apache Hudi table types](https://hudi.apache.org/docs/table_types) | [02](notes/02-table-formats.md) |
| [delta-rs](https://delta-io.github.io/delta-rs/), [PyIceberg](https://py.iceberg.apache.org/), [Delta deletion vectors](https://docs.delta.io/latest/delta-deletion-vectors.html) | [02](notes/02-table-formats.md) |
| [Kafka design docs](https://kafka.apache.org/42/design/design), [KIP-98](https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging) | [04](notes/04-kafka-and-stream-semantics.md) |
| [Flink time](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/), [Spark Structured Streaming](https://spark.apache.org/docs/latest/streaming/apis-on-dataframes-and-datasets.html) | [04](notes/04-kafka-and-stream-semantics.md) |
| [BigQuery pricing](https://cloud.google.com/bigquery/pricing), [slots](https://cloud.google.com/bigquery/docs/slots), [cost best practices](https://cloud.google.com/bigquery/docs/best-practices-costs), [VPC network pricing](https://cloud.google.com/vpc/network-pricing), [Cloud Storage pricing](https://cloud.google.com/storage/pricing) | [05](notes/05-cost.md) |
| Snowflake: [key concepts](https://docs.snowflake.com/en/user-guide/intro-key-concepts), [warehouses](https://docs.snowflake.com/en/user-guide/warehouses-overview), [micro-partitions](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions). Read and not run | [01](notes/01-warehouse-and-store.md) |
| Redshift: [architecture](https://docs.aws.amazon.com/redshift/latest/dg/c_high_level_system_architecture.html), [distribution and sort](https://docs.aws.amazon.com/redshift/latest/dg/c_choosing_dist_sort.html), [sorting](https://docs.aws.amazon.com/redshift/latest/dg/t_Sorting_data.html), [VACUUM](https://docs.aws.amazon.com/redshift/latest/dg/t_Reclaiming_storage_space202.html), [Spectrum](https://docs.aws.amazon.com/redshift/latest/dg/c-using-spectrum.html), [Serverless](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-whatis.html), [clusters](https://docs.aws.amazon.com/redshift/latest/mgmt/working-with-clusters.html). Read and not run | [01](notes/01-warehouse-and-store.md) |
| BigQuery: [storage overview](https://cloud.google.com/bigquery/docs/storage_overview), [pricing](https://cloud.google.com/bigquery/pricing). Read and not run | [01](notes/01-warehouse-and-store.md) |
| [Databricks SQL warehouses](https://docs.databricks.com/aws/en/compute/sql-warehouse/). Read and not run | [01](notes/01-warehouse-and-store.md) |
| ClickHouse: [intro](https://clickhouse.com/docs/intro), [why it is fast](https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast), [MergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree), [mutations](https://clickhouse.com/docs/guides/developer/mutations). Read and not run | [01](notes/01-warehouse-and-store.md) |
| [DuckDB, Why DuckDB](https://duckdb.org/why_duckdb). Code run | [01](notes/01-warehouse-and-store.md) |
| S3 behaviour: [overview and consistency](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html), [object keys](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html), [conditional writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html), [ListObjectsV2](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html), [performance](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html), [multipart upload](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html), [S3 Tables](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html). Code run against moto, a local mock, and not AWS | [01b](notes/01b-object-storage-and-the-data-lake.md) |
| S3 cost: [storage classes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html), [lifecycle transitions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-transition-general-considerations.html), [pricing page](https://aws.amazon.com/s3/pricing/), [AWS Price List file for us-east-1](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json) (the prices quoted come from this file, published 2026-10-15) | [01b](notes/01b-object-storage-and-the-data-lake.md) |

## Courses and videos

| Course | Platform | Cost | Notes | Weeks |
|---|---|---|---|---|
| [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) | DataTalksClub | Free | Modules 03, 05, 06 are the [practice folder](practice/datatalks-de) | About 3 for these modules |
| [Kafka 101](https://developer.confluent.io/courses/apache-kafka/events/) | Confluent | Free | Log concepts with a real broker; pairs with [04](notes/04-kafka-and-stream-semantics.md) | Under 1 |
| [Lakehouse Fundamentals](https://www.databricks.com/learn/training/lakehouse-fundamentals) | Databricks | Free | The vendor's own framing; read beside [03](notes/03-lakehouse-vs-warehouse.md) | Under 1 |
| [Distributed Systems lectures](https://www.youtube.com/playlist?list=PLeKd45zvjcDFUEv_ohr_HdUFe97RItdiB) (Kleppmann) | YouTube | Free | Background on logs, replication and consistency | About 1 |
