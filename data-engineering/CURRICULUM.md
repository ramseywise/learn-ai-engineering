# Data Engineering: curriculum

Last updated: 2026-11-02

> The sequenced path across the seven pillars, with the practice for each step and how you know you are done. What each chapter covers is in the [README](README.md#syllabus). Sources are in [references.md](references.md).

## Prerequisites

| Need | Where |
|---|---|
| Python and SQL | [programming/](../programming/README.md): Python 01 to 03 and SQL 01 to 09. The zoomcamps assume SQL and teach none |
| Docker basics | Helpful from the start. DE 01 teaches Docker from scratch, and every later module assumes it |
| Data analytics basics | [data-analytics/](../data-analytics/README.md), recommended and not required |
| Cloud accounts | Optional. GCP for BigQuery, AWS for the deployment modules. The last column says what to do without one |

## Path

The order is linear because each pillar consumes the previous one's output: the same question runs through every step, which is what this stage is trusting about the one before it. "Book" points to the chapters of [the core text](README.md#the-core-text) to read beside that step. "Scripts" means the chapter code in that pillar's `practice/` folder, with the run command at the top of each file. Where a pillar has no scripts, the chapter gives its own `uv run --with ...` line. DE and MLOps numbers are zoomcamp modules in the snapshot, placed as in the [README](README.md#coursework-with-run-labels).

| Step | Read | Book | Then do | Done when you can | Without a cloud account |
|---|---|---|---|---|---|
| 1. One machine | [01](01-storage-and-compute-foundations/README.md), chapters 1 to 4 | ch. 1, 2, 3, 4, 7 | Scripts `01` to `04` | state a load and a latency goal in percentiles, say what a CSV loses, read a Parquet footer, explain why a query reads only some columns, and reproduce and then fix a lost update and write skew on Postgres | Fully local |
| 2. Many machines | [01](01-storage-and-compute-foundations/README.md), chapters 5 to 8 | ch. 5, 6, 8, 9, 10 | Scripts `05` to `07`, `08` (Spark sections need Java) | say what a replica's reader can see, explain why a timed-out write may have applied, show what breaks if a consensus quorum is weakened, and decide from a measurement whether a job needs a cluster | Fully local |
| 3. Get it in | [02](02-ingest-and-modelling/README.md), chapter 1 | ch. 11, 12 | Script `01`; DE 01 Docker and Postgres, then Terraform | rerun a load without doubling it, and show your container loading the taxi CSV | Skip Terraform |
| 4. Say what a row means | [02](02-ingest-and-modelling/README.md), chapters 2 to 4 | ch. 3, 4, 11 | Scripts `02` to `04` | declare a grain, choose an SCD type, say when One Big Table wins, and write a contract that fails a bad batch | Fully local |
| 5. Transform it | [03](03-transform-and-orchestrate/README.md), chapters 1 and 3 | ch. 10 | Scripts `01`, `03`; DE 04 | run `dbt build` to green, change a test to `error`, and repair a late row with a full refresh | dbt Core with DuckDB or Postgres |
| 6. Run it for the right day | [03](03-transform-and-orchestrate/README.md), chapters 2, 4 and 5 | ch. 10, 8 | Scripts `02`, `04`, `05_*`; DE 02 videos, then rebuild steps 3 to 5 as one scheduled pipeline | backfill three past periods and get identical output when you run them again | Fully local |
| 7. Store it at a price | [04](04-warehouse-lakehouse-streaming/README.md), chapters 1 and 5 | ch. 3, 6, 10 | Chapter code; DE 03, DE 05 | explain a query's bytes scanned before and after partitioning, price it first, and reproduce a step 5 model in Spark SQL | Same ideas in DuckDB on Parquet; local Spark |
| 8. Make a lake into tables | [04](04-warehouse-lakehouse-streaming/README.md), chapters 2 and 3 | ch. 7, 9, 12 | Chapter code | show how a log makes a rewrite atomic, and defend a warehouse or lakehouse choice | Fully local |
| 9. Move it as a stream | [04](04-warehouse-lakehouse-streaming/README.md), chapter 4 | ch. 11, 12 | Chapter code; DE 06 | run a producer and consumer with manual offset commits, and say "exactly once" from where to where | Docker |
| 10. Find out it is wrong | [05](05-quality-and-observability/README.md) | ch. 12, pp. 530-532 | Chapter code; MLOps 05 | catch a planted fault with a test or a monitor, trace what it touched, run the playbook, and alert from a Grafana panel | Fully local with Docker |
| 11. Train and track | [06](06-ml-platform/README.md), chapters 1 and 2 | ch. 11, pp. 475-476 | Chapter code; MLOps 01, 02 | build a point-in-time training set, and name the run behind a registered model | Scenarios 1 and 2 |
| 12. Serve and watch | [06](06-ml-platform/README.md), chapters 3 and 4 | none | Chapter code; MLOps 04, 05 | serve a registered model from the Docker web service, and tell a pipeline fault from drift | `web-service/` |
| 13. Keep it running | [06](06-ml-platform/README.md), chapter 5 | none | MLOps 06; MLOps 03 for retraining | pass `make integration_test` against LocalStack, and score a team's maturity | Unit and integration tests are local |
| 14. Arrange it across teams | [07](07-architecture-and-governance/README.md) | ch. 12 | Chapter code; the [scenario prompts](07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md#scenario-prompts-mapped-to-mechanisms) | answer each prompt with root cause, mechanism and trade-off, and erase one person from an immutable store | Fully local |
| Capstone | All | none | MLOps `07-project`, or the DE [project brief](02-ingest-and-modelling/practice/datatalks-de/projects) | self-score against the evaluation criteria in the brief | LocalStack for the cloud criterion |

Steps 1 to 6 are the critical path, because every later pillar assumes them. If your goal is ML rather than platform work, you can take step 7 lightly and go from step 6 to steps 10 to 13.

## Reading map: Designing Data-Intensive Applications

[Kleppmann's book](https://dataintensive.net/) (O'Reilly, 1st ed., 2017) in its own order, with where this course develops each chapter. The first note listed is the main treatment, and the others apply the idea to a decision. Page pointers are in the notes themselves.

| Book chapter | The idea to take from it | Main note | Applied in |
|---|---|---|---|
| 1. Reliable, Scalable, and Maintainable Applications | Faults against failures, load parameters, percentiles and the tail | [01/01](01-storage-and-compute-foundations/notes/01-data-systems-and-data-models.md) | [01/06](01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail.md) |
| 2. Data Models and Query Languages | Relational, document and graph, judged by which relationships they make easy | [01/01](01-storage-and-compute-foundations/notes/01-data-systems-and-data-models.md) | [02/04](02-ingest-and-modelling/notes/04-data-contracts.md), [01/05](01-storage-and-compute-foundations/notes/05-partitioning-and-replication.md) |
| 3. Storage and Retrieval | B-trees against LSM-trees, OLTP against OLAP, column storage | [01/03](01-storage-and-compute-foundations/notes/03-row-and-column-stores.md) | [01/02](01-storage-and-compute-foundations/notes/02-encoding-and-files.md), [02/02](02-ingest-and-modelling/notes/02-dimensional-modelling.md), [04/01](04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md), [04/02](04-warehouse-lakehouse-streaming/notes/02-table-formats.md) |
| 4. Encoding and Evolution | Data outlives code, so compatibility runs both ways | [01/02](01-storage-and-compute-foundations/notes/02-encoding-and-files.md) | [02/01](02-ingest-and-modelling/notes/01-ingest.md), [02/04](02-ingest-and-modelling/notes/04-data-contracts.md) |
| 5. Replication | Leaders and followers, lag anomalies, quorums, concurrent writes | [01/05](01-storage-and-compute-foundations/notes/05-partitioning-and-replication.md) | [02/01](02-ingest-and-modelling/notes/01-ingest.md) |
| 6. Partitioning | Key range against hash, skew, secondary indexes, routing | [01/05](01-storage-and-compute-foundations/notes/05-partitioning-and-replication.md) | [01/08](01-storage-and-compute-foundations/notes/08-distributed-compute.md), [04/01](04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md) |
| 7. Transactions | Isolation levels by the anomalies they allow: lost updates, write skew, phantoms | [01/04](01-storage-and-compute-foundations/notes/04-transactions-and-isolation.md) | [04/02](04-warehouse-lakehouse-streaming/notes/02-table-formats.md), [03/02](03-transform-and-orchestrate/notes/02-orchestrate.md), [03/04](03-transform-and-orchestrate/notes/04-idempotency-and-backfills.md) |
| 8. The Trouble with Distributed Systems | Timeouts, unreliable clocks, process pauses, fencing | [01/06](01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail.md) | [03/02](03-transform-and-orchestrate/notes/02-orchestrate.md), [03/04](03-transform-and-orchestrate/notes/04-idempotency-and-backfills.md), [04/04](04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics.md) |
| 9. Consistency and Consensus | Linearizability, ordering, two-phase commit, majority agreement | [01/07](01-storage-and-compute-foundations/notes/07-consistency-and-consensus.md) | [04/02](04-warehouse-lakehouse-streaming/notes/02-table-formats.md), [04/04](04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics.md), [03/02](03-transform-and-orchestrate/notes/02-orchestrate.md), [03/05](03-transform-and-orchestrate/notes/05-dagster-and-airflow.md) |
| 10. Batch Processing | Immutable inputs, derived outputs, MapReduce to dataflow engines, schema on read | [01/08](01-storage-and-compute-foundations/notes/08-distributed-compute.md) | [03/01](03-transform-and-orchestrate/notes/01-transform.md), [03/02](03-transform-and-orchestrate/notes/02-orchestrate.md), [03/04](03-transform-and-orchestrate/notes/04-idempotency-and-backfills.md), [02/04](02-ingest-and-modelling/notes/04-data-contracts.md), [04/01](04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md) |
| 11. Stream Processing | Logs against queues, CDC, event time, stream joins, fault tolerance | [04/04](04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics.md) | [02/01](02-ingest-and-modelling/notes/01-ingest.md), [02/02](02-ingest-and-modelling/notes/02-dimensional-modelling.md), [02/03](02-ingest-and-modelling/notes/03-data-vault-and-obt.md), [03/04](03-transform-and-orchestrate/notes/04-idempotency-and-backfills.md), [06/01](06-ml-platform/notes/01-feature-stores.md), [07/02](07-architecture-and-governance/notes/02-access-control-pii-gdpr.md) |
| 12. The Future of Data Systems | System of record and derived data, federation and unbundling, timeliness and integrity, auditing, responsibility | [07/01](07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md) | [04/03](04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse.md), [04/04](04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics.md), [03/04](03-transform-and-orchestrate/notes/04-idempotency-and-backfills.md), [05/01](05-quality-and-observability/notes/01-quality-dimensions-and-tests.md), [07/02](07-architecture-and-governance/notes/02-access-control-pii-gdpr.md) |

The course changes the book's order in two places. Encoding comes before storage, since a file is easier to hold than a storage engine, and transactions come before replication, so that the second writer on one machine appears before the second machine. Otherwise the order holds, so the book and pillar 01 can be read side by side.

## Where to go next

The previous and next layers are in the README's [Resource map](README.md#previous-and-next-layer).
