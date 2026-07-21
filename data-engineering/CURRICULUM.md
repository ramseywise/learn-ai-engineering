# Data Engineering — Curriculum

Last updated: 2026-07-21

## Prerequisites

Python basics from `programming/Python Basics/`. Docker and SQL fundamentals help (the
DataTalks DE Zoomcamp covers Docker from scratch; SQL is assumed).

## The 6 Foundations

Data engineering is a pipeline discipline — each stage prepares data for the next.

| # | Foundation | What you learn | Primary material |
|---|---|---|---|
| 1 | **Ingest** | Pull data from APIs and streams; incremental loading; dlt pipelines | DE Zoomcamp Workshop 1 (dlt), Module 6 (Kafka/streaming) |
| 2 | **Transform** | Layered modeling (raw → staging → mart); dbt; SQL transformation patterns | DE Zoomcamp Module 4 (analytics engineering, dbt, BigQuery) |
| 3 | **Orchestrate** | DAG authoring; scheduling; backfill; retry logic | DE Zoomcamp Module 2 (Mage); MLOps Module 3 (Mage) |
| 4 | **Warehouse / Store** | BigQuery internals; partitioning and clustering; Spark batch; columnar storage | DE Zoomcamp Module 3 (data warehouse) + Module 5 (Spark batch) |
| 5 | **Monitor** | Pipeline observability; data quality checks; model drift monitoring | MLOps Module 5 (Prometheus, Evidently, Grafana) |
| 6 | **Feature-serve** | Feature engineering for ML; experiment tracking; model registry; deployment | MLOps Module 2 (MLflow) + Module 4 (deployment) |

## Module Map

### DataTalks Data Engineering Zoomcamp (`DataTalks Data Engineering/`)

| Module | Topic | Foundation |
|---|---|---|
| 01-docker-terraform | Containerization + IaC | Cross-cutting infrastructure |
| 02-workflow-orchestration | Mage orchestration | 3 — Orchestrate |
| 03-data-warehouse | BigQuery | 4 — Warehouse/Store |
| 04-analytics-engineering | dbt + transformation | 2 — Transform |
| 05-batch | Spark | 4 — Warehouse/Store |
| 06-streaming | Kafka | 1 — Ingest |
| Workshop 1 (dlt) | API ingestion + incremental loading | 1 — Ingest |
| Workshop 2 (RisingWave) | Stream processing with SQL | 1 — Ingest |

### DataTalks MLOps Zoomcamp (`DataTalks MLOps/`)

| Module | Topic | Foundation |
|---|---|---|
| 01-intro | MLOps maturity model | Cross-cutting |
| 02-experiment-tracking | MLflow | 6 — Feature-serve |
| 03-orchestration | Mage pipelines for ML | 3 — Orchestrate |
| 04-deployment | Flask, Kinesis, batch scoring | 6 — Feature-serve |
| 05-monitoring | Prefect + Evidently + Grafana | 5 — Monitor |
| 06-best-practices | Testing, CI/CD, Terraform | Cross-cutting |

## Orchestration Inconsistency

Both zoomcamps use **Mage** for orchestration (DE Module 2, MLOps Module 3). The MLOps
monitoring module (05) uses **Prefect** for batch job scheduling alongside Evidently.
These tools are equivalent in capability; the inconsistency is a zoomcamp version artifact,
not a curriculum design choice. Modern production stacks (2024+) also use **Dagster**
and **Airflow 2.x** — neither appears in these materials.

## Modern Gaps

The following tools are not covered in the existing material but are standard in modern DE stacks. These are named as future additions, not currently implemented:

- **DuckDB** — in-process OLAP engine; largely replaces Spark for single-node analytics workloads
- **Polars** — DataFrame library with Rust performance; preferred over pandas for large-scale local processing
- **Delta Lake / Apache Iceberg** — open table formats for data lakehouse architecture; critical for production lake stacks
- **dlt (data load tool)** — Python-native ingestion library; appears in DE Zoomcamp Workshop 1 but deserves deeper coverage
- **Dagster** — modern orchestrator with asset-first model; not in either zoomcamp

## Reference Links

- **Interview guide**: [`../interviewing/guides/8-data-eng-mlops/`](../interviewing/guides/8-data-eng-mlops/00-overview.md)
- **Readings**: [`8-data-eng-data-mesh/`](8-data-eng-data-mesh/)
- **Curated resource list**: [`awesome-data-engineering.md`](awesome-data-engineering.md)
- **Reference book**: *Designing Data-Intensive Applications* (O'Reilly, in repo root of this dir)

## What Comes Next

After completing DE foundations, typical progressions:

- **ML in production** → continue with MLOps depth (experiment tracking, monitoring, deployment)
- **Data science** → `data-science/CURRICULUM.md` (statistical foundations + supervised learning)
- **AI engineering** → `ai-engineering/` pillars (uses DE pipelines as the data layer)
