# Data Engineering

> Interview summary: [interviewing/guides/8-data-eng-mlops](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/8-data-eng-mlops/00-overview.md)
> Position in the learning path: after [programming](../programming/README.md) (Python, SQL) and [data analytics](../data-analytics/README.md); alongside or before [data science](../data-science/README.md). The pipeline layer under [generative AI](../generative-ai/README.md) and [AI engineering](../ai-engineering/README.md). The sequenced path and prerequisites are in [CURRICULUM.md](CURRICULUM.md).

---

## What it is

Data engineering is the pipeline discipline: getting data from where it's born to where it's used, on a schedule, correctly, and in a shape the next stage can trust. This folder treats it as **six foundations**, each preparing data for the next: ingest → transform → orchestrate → warehouse/store → monitor → feature-serve. The last two reach into MLOps, where the "data" is a model's inputs and predictions.

Two notes sit above the pipeline. One covers how an organisation arranges many pipelines (modern data warehouse, data fabric, data mesh). The other covers how automated the ML lifecycle is (the maturity model) and the engineering practices that move it up a level.

The coursework is two complete DataTalksClub zoomcamps, kept as worked material. The notes are the synthesis: each one folds the relevant modules into commands, configs, SQL and Python, says what's legacy, and fills the gaps the zoomcamps leave (DuckDB, Polars, Delta/Iceberg, Dagster, deeper dlt).

> **Every foundation has the same failure mode: a stage silently trusts the one before it. The engineering is in making that trust explicit — keys, contracts, tests, logical dates, monitored metrics.**

---

## Start here

1. Read [01-ingest](02-ingest-and-modelling/notes/01-ingest.md) and run DE 01 `2_docker_sql` (Docker + Postgres). It's the setup every later module reuses.
2. Read [02-transform](03-transform-and-orchestrate/notes/01-transform.md) and [04-warehouse-and-store](04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md) together: dbt models are only as good as the tables underneath them.
3. Read [03-orchestrate](03-transform-and-orchestrate/notes/02-orchestrate.md) for the scheduling ideas (logical dates, idempotent outputs, backfills) and the orchestration-tool inconsistency between the two courses.
4. Switch to MLOps: [06-feature-serve](06-ml-platform/notes/01-feature-serve.md), then [05-monitor](05-quality-and-observability/notes/01-monitor.md). Train, track, deploy, then watch.
5. Finish with [08-mlops-maturity-and-best-practices](06-ml-platform/notes/02-mlops-maturity-and-best-practices.md) (tests, IaC, CI/CD) and [07-data-architectures-mesh-fabric-mdw](07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md) (the interview-level architecture questions).

---

## Layout

```
data-engineering/
├── README.md                     this file
├── CURRICULUM.md                 sequenced path and prerequisites
├── references.md                 every source, mapped to notes, with licences
├── notes/                        01–08, the synthesis (see Syllabus)
├── sources/                      local PDFs: DDIA, three Serra chapters, Strengholt, scenario prompts
├── DataTalks Data Engineering/   DE Zoomcamp snapshot: 01-docker-terraform … 06-streaming, projects/
└── DataTalks MLOps/              MLOps Zoomcamp snapshot: 01-intro … 07-project, generate/
```

**Why the two zoomcamp folders keep their names and places.** Unlike the vendored snapshots elsewhere in this repo, which were condensed into notes and deleted, these hold real worked notebooks and runnable code (`duration-prediction.ipynb`, `model-registry.ipynb`, the Lambda, the Evidently stack, the Terraform). The notes quote them rather than replace them. Their paths are also load-bearing: [`.github/dependabot.yml`](../.github/dependabot.yml) watches six `DataTalks MLOps/...` directories by exact path, the snapshots' own READMEs link between modules with relative paths, and the notes link into them. Renaming would break all of those for no gain.

---

## Syllabus

| # | Note | Covers |
|---|---|---|
| 01 | [Ingest](02-ingest-and-modelling/notes/01-ingest.md) | Batch vs incremental vs stream; chunked loader into Postgres; Docker, compose, Terraform on GCP; dlt (merge, incremental cursors); Kafka (keys, partitions, delivery semantics, Avro + schema registry, windows); RisingWave; DDIA ch. 4 and 11 |
| 02 | [Transform](03-transform-and-orchestrate/notes/01-transform.md) | ETL vs ELT; staging/core/marts layers; dbt project, models, macros, packages, tests, seeds, freshness; dbt Cloud vs Core; BI on top |
| 03 | [Orchestrate](03-transform-and-orchestrate/notes/02-orchestrate.md) | DAGs, retries, logical dates, backfills; Mage (DE 02, MLOps 03); Prefect 2 (MLOps 04/05, legacy); the course-to-course tool inconsistency; Dagster assets and Airflow as the gaps |
| 04 | [Warehouse and store](04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md) | OLTP vs OLAP; BigQuery external tables, partitioning, clustering, cost; BQML and model export; Spark DataFrames, SQL, UDFs, joins, RDDs, Dataproc; DuckDB, Polars, Delta Lake and Iceberg as the gaps |
| 05 | [Monitor](05-quality-and-observability/notes/01-monitor.md) | What to monitor (service, data, model); Evidently reports, test suites, metrics to Postgres; Grafana dashboards and alerts; pipeline-side checks |
| 06 | [Feature-serve](06-ml-platform/notes/01-feature-serve.md) | One `prepare_features` against train/serve skew; MLflow tracking, autolog, hyperopt, three server set-ups; the registry (stages → aliases); web service, Kinesis + Lambda stream, batch scoring |
| 07 | [Data architectures](07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md) | Modern data warehouse, data fabric, lakehouse; data mesh's four principles and domain types; Serra's skepticism and mesh types; Strengholt's six topologies; scenario prompts mapped to mechanisms |
| 08 | [MLOps maturity and best practices](06-ml-platform/notes/02-mlops-maturity-and-best-practices.md) | Microsoft maturity levels 0–4 and where the course reaches; testable refactor; pytest, LocalStack integration tests, pre-commit, Makefile; Terraform modules and remote state; GitHub Actions CI/CD; the capstone rubric |

---

## Rules of thumb

| Rule | Note |
|---|---|
| Every load is keyed and re-runnable: merge on a primary key, write to a path derived from the logical date | [01](02-ingest-and-modelling/notes/01-ingest.md), [03](03-transform-and-orchestrate/notes/02-orchestrate.md) |
| Commit stream offsets after processing, never before | [01](02-ingest-and-modelling/notes/01-ingest.md) |
| Put a schema contract at every producer/consumer boundary (Avro + registry, dbt tests at `error` on staging) | [01](02-ingest-and-modelling/notes/01-ingest.md), [02](03-transform-and-orchestrate/notes/01-transform.md) |
| Define each metric once, in one mart, with an owner | [02](03-transform-and-orchestrate/notes/01-transform.md), [07](07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md) |
| Partition on the filter column; cluster on the next one; don't partition tables under 1 GB | [04](04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md) |
| Reach for DuckDB or Polars before Spark when the data fits on one machine | [04](04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md) |
| Monitor inputs and predictions, not just accuracy; alert only on what someone will act on | [05](05-quality-and-observability/notes/01-monitor.md) |
| One feature function shared by training and every serving path | [06](06-ml-platform/notes/01-feature-serve.md) |
| The registry labels models; CI/CD deploys them | [06](06-ml-platform/notes/01-feature-serve.md), [08](06-ml-platform/notes/02-mlops-maturity-and-best-practices.md) |
| Inject side effects so the service can be unit-tested; integration-test the real container against LocalStack | [08](06-ml-platform/notes/02-mlops-maturity-and-best-practices.md) |
| A data mesh is an ownership model, not a storage choice; contracts before decentralisation | [07](07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md) |

---

## Resource map

### Related notes elsewhere

| Where | Why |
|---|---|
| [programming/](../programming/README.md) SQL 01–10, Python 03 | SQL and Python fluency the zoomcamps assume |
| [data-analytics/](../data-analytics/README.md) | Wrangling and statistics; the consumer of the marts in 02 |
| [data-science/](../data-science/README.md) | The models that 06 serves and 05 monitors; feature engineering and evaluation in depth |
| [generative-ai/06-observability](../generative-ai/06-observability/README.md) | Tracing and scoring for LLM apps: the same monitoring ideas as 05, for a different model type |

### Books and courses

Two zoomcamps, *Designing Data-Intensive Applications*, and three chapters of *Deciphering Data Architectures*. Full list, licences and chapter-to-note mapping in [references.md](references.md#books-and-courses).

### Coursework, with run labels

Labels: **offline** = runs on a laptop with no account once data is downloaded · **Docker** · **GCP** / **AWS** = needs a cloud account (and billing) · **pin** = unpinned dependencies; pin as stated · **legacy** = API or tool superseded · **reading** = videos or text, no code. No notebook was executed for this pass.

**[DataTalks Data Engineering/](02-ingest-and-modelling/practice/datatalks-de/README.md)**

| Module | Note | Needs |
|---|---|---|
| `01-docker-terraform` | 01 | Docker (Postgres, pgAdmin, ingest container): offline. Terraform part: GCP (service-account key) |
| `02-workflow-orchestration` | 03 | Reading (videos only in the snapshot); to follow along, Docker (Mage) + GCP |
| `03-data-warehouse` | 04 | GCP (BigQuery, billing). BQML export: Docker (`tensorflow/serving`) |
| `04-analytics-engineering` | 02 | GCP (BigQuery + dbt Cloud), or offline with dbt Core + Postgres |
| `05-batch` | 04 | Java 11 + Spark 3.3.2 (pin); offline locally. Dataproc and the GCS connector: GCP |
| `06-streaming` | 01 | Docker (Kafka / Confluent compose, Redpanda); Java for the Kafka Streams examples; ksqlDB folder is SQL only |
| `projects/` | 01–05 | Reading: project brief and dataset list |
| Workshop 1 (dlt), Workshop 2 (RisingWave) | 01 | Upstream only (cohort links in the README). dlt runs offline with DuckDB; RisingWave needs Docker |

**[DataTalks MLOps/](06-ml-platform/practice/datatalks-mlops/README.md)**

| Module | Note | Needs |
|---|---|---|
| `01-intro` | 06, 08 | Offline after downloading the taxi Parquet files (Codespaces or an EC2 VM optional) |
| `02-experiment-tracking` | 06 | `mlflow`, `hyperopt`, `xgboost` (pin; requirements unpinned): offline. Scenario 3 and `mlflow_on_aws.md`: AWS (EC2, RDS, S3) |
| `03-orchestration` | 03 | Docker (Mage; pinned requirements in the module) |
| `04-deployment` | 06, 03 | `web-service/`: Docker, offline. `web-service-mlflow/`: AWS (S3). `streaming/`: Docker locally; AWS (Kinesis, Lambda, ECR) for real. `batch/`: legacy (Prefect 2 `orion`) + AWS S3 |
| `05-monitoring` | 05 | Docker compose (Postgres, Adminer, Grafana): offline. `evidently` unpinned: pin `evidently<0.7` (legacy API). Prefect: legacy |
| `06-best-practices` | 08 | Unit tests: offline. Integration test: Docker + LocalStack, offline. Terraform and CI/CD: AWS + GitHub |
| `07-project` | 08 | Reading: capstone brief and rubric |
| `generate/` | — | Course-site tooling (`generate_pages.ipynb`), not coursework |

### Readings

[sources/](sources/) holds the cited PDFs; see [references.md](references.md). The `/readings` router also files `ml-systems` papers and books here. These are queued and not yet cited by any note: *Hidden Technical Debt in ML Systems*, Amershi et al. *Software Engineering for ML*, *Failing Loudly*, the KDD metric-interpretation pitfalls paper, *The Data Warehouse Toolkit*, *Machine Learning Engineering in Action*. Fold them in with `/papers` or `/chapter`.

### Interviewing guide

[8-data-eng-mlops/00-overview.md](https://github.com/ramseywise/sisyphus/blob/main/interviewing/guides/8-data-eng-mlops/00-overview.md). Note 07's scenario-prompt tables are written as interview practice.

### Previous and next layer

| | Where |
|---|---|
| Previous | [data-analytics/](../data-analytics/README.md), on top of [programming/](../programming/README.md) |
| Next | [data-science/](../data-science/README.md) for the modelling side; [generative-ai/](../generative-ai/README.md) and [ai-engineering/](../ai-engineering/README.md), which use these pipelines as their data layer |
