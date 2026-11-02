---
origin: curated
sources:
  - ../references.md
confidence: high
cleaned: 2026-11-01
---
# Transform and orchestrate: references

> The sources behind the five chapters in [notes/](notes/). Books shared across the data-engineering pillars are listed in the [subject references](../references.md). PDFs are in [../sources/](../sources/).

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| ★ Kleppmann, [*Designing Data-Intensive Applications*](https://dataintensive.net/) (O'Reilly, 2017) | ch. 10 (workflow schedulers pp. 402-403; replacing outputs and human fault tolerance pp. 413-414; schema on read pp. 415-416), ch. 11 (idempotence p. 478) | [PDF](../sources/kleppmann-designing-data-intensive-applications.pdf) | [01](notes/01-transform.md), [02](notes/02-orchestrate.md), [04](notes/04-idempotency-and-backfills.md) |

## Core papers

No research paper changes a claim in this pillar. The nearest argument is the Beauchemin essay under Posts.

## Standards and docs

| Source | Used for | Maps to |
|---|---|---|
| [dbt: materializations](https://docs.getdbt.com/docs/build/materializations), [SQL models](https://docs.getdbt.com/docs/build/sql-models), [Jinja and macros](https://docs.getdbt.com/docs/build/jinja-macros), [`dbt build`](https://docs.getdbt.com/reference/commands/build), [project structure](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview) | Layers, the command set | [01](notes/01-transform.md) |
| [dbt: source freshness](https://docs.getdbt.com/docs/deploy/source-freshness) | Freshness checks | [01](notes/01-transform.md) |
| [dbt: data tests](https://docs.getdbt.com/docs/build/data-tests), [severity](https://docs.getdbt.com/reference/resource-configs/severity), [`store_failures`](https://docs.getdbt.com/reference/resource-configs/store_failures), [unit tests](https://docs.getdbt.com/docs/build/unit-tests) | Tests | [01](notes/01-transform.md), [03](notes/03-dbt-tests-snapshots-incremental.md) |
| [dbt: snapshots](https://docs.getdbt.com/docs/build/snapshots) | Strategies, hard deletes | [03](notes/03-dbt-tests-snapshots-incremental.md) |
| [dbt: incremental models](https://docs.getdbt.com/docs/build/incremental-models), [strategies](https://docs.getdbt.com/docs/build/incremental-strategy), [microbatch](https://docs.getdbt.com/docs/build/incremental-microbatch) | Incremental behaviour | [03](notes/03-dbt-tests-snapshots-incremental.md) |
| [Prefect docs](https://docs.prefect.io/), [Mage docs](https://docs.mage.ai/introduction/overview) | The zoomcamps' orchestrators | [02](notes/02-orchestrate.md) |
| [Airflow: backfill](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/backfill.html) | `airflow backfill create` and its options | [04](notes/04-idempotency-and-backfills.md), [05](notes/05-dagster-and-airflow.md) |
| ★ [Airflow 3.0 release notes](https://airflow.apache.org/docs/apache-airflow/3.0.0/release_notes.html), [timetables](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/timetable.html) | Cron default and logical date | [05](notes/05-dagster-and-airflow.md) |
| [Airflow: asset scheduling](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/asset-scheduling.html), [TaskFlow](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html), [best practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html), [Dag runs and catchup](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html), [project history](https://airflow.apache.org/docs/apache-airflow/stable/project.html) | Task model, assets, top-level code | [05](notes/05-dagster-and-airflow.md) |
| [Dagster: partitioning assets](https://docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets), [backfilling](https://docs.dagster.io/guides/build/partitions-and-backfills/backfilling-data), [asset checks](https://docs.dagster.io/guides/test/asset-checks), [IO managers](https://docs.dagster.io/guides/build/io-managers) | Asset model, blocking checks | [05](notes/05-dagster-and-airflow.md) |
| [dagster-dbt](https://docs.dagster.io/integrations/libraries/dbt), [Astronomer Cosmos](https://astronomer.github.io/astronomer-cosmos/) | dbt inside an orchestrator. Cosmos was not run | [05](notes/05-dagster-and-airflow.md) |
| [DuckDB: concurrency](https://duckdb.org/docs/current/connect/concurrency) | The single-writer lock a parallel backfill hit | [05](notes/05-dagster-and-airflow.md) |

## Posts

| Post | Used for | Maps to |
|---|---|---|
| Beauchemin, ["Functional Data Engineering"](https://maximebeauchemin.medium.com/functional-data-engineering-a-modern-paradigm-for-batch-data-processing-2327ec32c42a) (Medium, 2018); [talk](https://aicouncil.com/talks/functional-data-engineering-a-set-of-best-practices). The essay refused automated fetches, so its claims here were checked through search summaries, not the full text | Pure tasks, partition overwrite, immutable inputs | [04](notes/04-idempotency-and-backfills.md) |

## Courses and videos

| Course | Platform | Cost | Supports |
|---|---|---|---|
| [DE Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) (DataTalks.Club), Module 2 Workflow Orchestration (Kestra) and Module 4 Analytics Engineering (dbt) upstream; older snapshot at [practice/datatalks-de/](practice/datatalks-de/) | GitHub, YouTube | Free | [01](notes/01-transform.md), [02](notes/02-orchestrate.md) |
| [MLOps Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp) (DataTalks.Club), modules 03 to 05 | GitHub, YouTube | Free | [02](notes/02-orchestrate.md): Mage and Prefect in practice |
| [dbt Fundamentals](https://learn.getdbt.com/courses/dbt-fundamentals) | dbt Learn | Free | [01](notes/01-transform.md), [03](notes/03-dbt-tests-snapshots-incremental.md) |
| [Dagster University](https://courses.dagster.io/) | Web | Check site | [05](notes/05-dagster-and-airflow.md) |
