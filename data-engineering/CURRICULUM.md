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

The order is linear because each pillar consumes the previous one's output: the same question runs through every step, which is what this stage is trusting about the one before it. "Scripts" means the chapter code in that pillar's `practice/` folder, with the run command at the top of each file. Where a pillar has no scripts, the chapter gives its own `uv run --with ...` line. DE and MLOps numbers are zoomcamp modules in the snapshot, placed as in the [README](README.md#coursework-with-run-labels).

| Step | Read | Then do | Done when you can | Without a cloud account |
|---|---|---|---|---|
| 1. Bytes on disk | [01](01-storage-and-compute-foundations/README.md), chapters 1 and 2 | Scripts `01`, `02` | say what a CSV loses, read a Parquet footer, and explain why a query reads only some columns | Fully local |
| 2. Work across machines | [01](01-storage-and-compute-foundations/README.md), chapters 3 and 4 | Scripts `03` (Spark sections need Java), `04` | decide from a measurement whether a job needs a cluster, and say what a replica's reader can see | Fully local |
| 3. Get it in | [02](02-ingest-and-modelling/README.md), chapter 1 | Script `01`; DE 01 Docker and Postgres, then Terraform | rerun a load without doubling it, and show your container loading the taxi CSV | Skip Terraform |
| 4. Say what a row means | [02](02-ingest-and-modelling/README.md), chapters 2 to 4 | Scripts `02` to `04` | declare a grain, choose an SCD type, say when One Big Table wins, and write a contract that fails a bad batch | Fully local |
| 5. Transform it | [03](03-transform-and-orchestrate/README.md), chapters 1 and 3 | Scripts `01`, `03`; DE 04 | run `dbt build` to green, change a test to `error`, and repair a late row with a full refresh | dbt Core with DuckDB or Postgres |
| 6. Run it for the right day | [03](03-transform-and-orchestrate/README.md), chapters 2, 4 and 5 | Scripts `02`, `04`, `05_*`; DE 02 videos, then rebuild steps 3 to 5 as one scheduled pipeline | backfill three past periods and get identical output when you run them again | Fully local |
| 7. Store it at a price | [04](04-warehouse-lakehouse-streaming/README.md), chapters 1 and 5 | Chapter code; DE 03, DE 05 | explain a query's bytes scanned before and after partitioning, price it first, and reproduce a step 5 model in Spark SQL | Same ideas in DuckDB on Parquet; local Spark |
| 8. Make a lake into tables | [04](04-warehouse-lakehouse-streaming/README.md), chapters 2 and 3 | Chapter code | show how a log makes a rewrite atomic, and defend a warehouse or lakehouse choice | Fully local |
| 9. Move it as a stream | [04](04-warehouse-lakehouse-streaming/README.md), chapter 4 | Chapter code; DE 06 | run a producer and consumer with manual offset commits, and say "exactly once" from where to where | Docker |
| 10. Find out it is wrong | [05](05-quality-and-observability/README.md) | Chapter code; MLOps 05 | catch a planted fault with a test or a monitor, trace what it touched, run the playbook, and alert from a Grafana panel | Fully local with Docker |
| 11. Train and track | [06](06-ml-platform/README.md), chapters 1 and 2 | Chapter code; MLOps 01, 02 | build a point-in-time training set, and name the run behind a registered model | Scenarios 1 and 2 |
| 12. Serve and watch | [06](06-ml-platform/README.md), chapters 3 and 4 | Chapter code; MLOps 04, 05 | serve a registered model from the Docker web service, and tell a pipeline fault from drift | `web-service/` |
| 13. Keep it running | [06](06-ml-platform/README.md), chapter 5 | MLOps 06; MLOps 03 for retraining | pass `make integration_test` against LocalStack, and score a team's maturity | Unit and integration tests are local |
| 14. Arrange it across teams | [07](07-architecture-and-governance/README.md) | Chapter code; the [scenario prompts](07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md#scenario-prompts-mapped-to-mechanisms) | answer each prompt with root cause, mechanism and trade-off, and erase one person from an immutable store | Fully local |
| Capstone | All | MLOps `07-project`, or the DE [project brief](02-ingest-and-modelling/practice/datatalks-de/projects) | self-score against the evaluation criteria in the brief | LocalStack for the cloud criterion |

Steps 1 to 6 are the critical path, because every later pillar assumes them. If your goal is ML rather than platform work, you can take step 7 lightly and go from step 6 to steps 10 to 13.

## Where to go next

The previous and next layers are in the README's [Resource map](README.md#previous-and-next-layer).
