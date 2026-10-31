# Data Engineering — Curriculum

Last updated: 2026-10-31

What each note covers, which zoomcamp modules it draws on, and what each module needs to run are in the [README](README.md). This file is the order to work in.

## Prerequisites

- **Python 01–03 and SQL 01–09** from [programming/](../programming/README.md). The zoomcamps assume SQL and teach none.
- **Docker basics** help. DE 01 teaches Docker from scratch, but every later module assumes it.
- **Data analytics basics** ([data-analytics/](../data-analytics/README.md)) are recommended, not required.
- **Cloud accounts:** GCP for the DE warehouse path (BigQuery), AWS for MLOps deployment. Each step below says what's possible without one.

## Sequenced path

The order is linear because each foundation consumes the previous one's output. Steps 5–7 switch from the DE Zoomcamp to the MLOps Zoomcamp.

| Step | Read | Then do | Done when | Without a cloud account |
|---|---|---|---|---|
| 1 | [01 Ingest](notes/01-ingest.md) | DE 01 Docker + Postgres, then Terraform | The taxi CSV is in Postgres via your own container; `terraform apply` creates the bucket and dataset | Skip Terraform; do the dlt → DuckDB example |
| 2 | [04 Warehouse and store](notes/04-warehouse-and-store.md), BigQuery half | DE 03 | You can explain a query's bytes scanned before and after partitioning | Same SQL ideas in DuckDB on the Parquet files |
| 3 | [02 Transform](notes/02-transform.md) | DE 04 | `dbt build` passes; `fact_trips` and one mart exist; you changed one test to `error` | dbt Core + Postgres |
| 4 | [03 Orchestrate](notes/03-orchestrate.md) | DE 02 (videos), then rebuild steps 1–3 as one scheduled pipeline in Mage or Dagster | A backfill of three past months produces identical output when re-run | Fully local |
| 5 | [04 Warehouse and store](notes/04-warehouse-and-store.md), Spark half | DE 05 | The revenue model from step 3 reproduced in Spark SQL, then in DuckDB | Local Spark |
| 6 | [01 Ingest](notes/01-ingest.md), Kafka half | DE 06 | A producer/consumer pair with manual offset commits and an Avro schema | Docker |
| 7 | [06 Feature-serve](notes/06-feature-serve.md) | MLOps 01, 02, 04 | A tracked, registered model served by the Docker web service | Scenarios 1–2 and `web-service/` |
| 8 | [05 Monitor](notes/05-monitor.md) | MLOps 05 | A Grafana panel with an alert rule on drift | Fully local with Docker |
| 9 | [08 MLOps maturity and best practices](notes/08-mlops-maturity-and-best-practices.md) | MLOps 06; MLOps 03 for retraining | `make integration_test` passes against LocalStack | Unit and integration tests are local |
| 10 | [07 Data architectures](notes/07-data-architectures-mesh-fabric-mdw.md) | Work through the scenario prompts | You can answer each prompt with root cause → mechanism → trade-off | Reading only |
| Capstone | — | MLOps 07 project, or the DE project brief | Self-scored against the rubric in note 08 | Use LocalStack for the cloud criterion's middle score |

## Where to go next

The previous and next layers are in the README's [Resource map](README.md#previous-and-next-layer).
