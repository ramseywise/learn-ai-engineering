---
origin: course-synthesis
sources:
  - https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/02-workflow-orchestration
  - https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/03-orchestration
  - https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/04-deployment/batch
  - https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/05-monitoring
  - https://docs.mage.ai/introduction/overview
  - https://docs.prefect.io/
  - https://docs.dagster.io/
  - https://airflow.apache.org/docs/
confidence: medium
cleaned: 2026-10-31
---
# 3 — Orchestrate

> Turn scripts into scheduled, parameterised, retryable, observable runs with explicit dependencies, so that "re-run March" is one command and a failure stops what depends on it.

---

## Where it sits

Foundation 3 of 6. Ingest ([01](01-ingest.md)) and transform ([02](02-transform.md)) are tasks. Orchestration decides when they run, in what order, with which parameters, and what happens on failure. Confidence is `medium` because DE 02 in this snapshot is a README of video links with no code; the worked code comes from MLOps 03 (Mage, upstream repo), MLOps 04 (Prefect batch scoring) and MLOps 05 (Prefect monitoring backfill).

---

## What an orchestrator gives you

DE 02.2.1 ("What is orchestration?") frames the job; this table is the checklist to hold any tool against:

| Capability | Without an orchestrator | With one |
|---|---|---|
| Dependencies | A shell script in the right order | A DAG; downstream waits on upstream success |
| Scheduling | cron on one machine | Schedules stored with the pipeline, visible in a UI |
| Parameters | `sys.argv` | Typed run parameters (date, taxi type, model run ID) |
| Retries | Manual rerun | Per-task retry with backoff |
| Backfill | A for-loop someone writes once | Run the same pipeline over a date range, each run isolated |
| Observability | Log files | Run history, task state, logs per run, alerts |
| Triggers | None | Schedule, sensor (new data arrived), API call, upstream success |

---

## The orchestration inconsistency

The two zoomcamps don't agree on a tool, and the history explains why:

| Where | Tool | Note |
|---|---|---|
| DE 02 (2024 cohort, this snapshot) | **Mage** | Video module 2.2.1–2.2.9 |
| DE 2022 cohort | **Airflow** | [cohorts/2022/week_2_data_ingestion](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/cohorts/2022/week_2_data_ingestion) |
| DE 2023 cohort | **Prefect** | [cohorts/2023/week_2_workflow_orchestration](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/cohorts/2023/week_2_workflow_orchestration) |
| MLOps 03 (2024) | **Mage** | Units 3.0–3.5, code in [mage-ai/mlops](https://github.com/mage-ai/mlops) |
| MLOps 03 (2022/2023 cohorts) | **Prefect** | Superseded by Mage |
| MLOps 04 batch scoring | **Prefect 2** | `prefect.orion` import, a pre-2.10 API |
| MLOps 05 monitoring | **Prefect** | `@flow batch_monitoring_backfill`; the README says Prefect is "not officially supported in 2024" |
| Neither zoomcamp | **Dagster**, **Airflow 2.x** | Common in 2024+ production stacks |

These tools are equivalent in capability for the course's pipelines. The inconsistency is a zoomcamp version artifact, not a curriculum design choice: each cohort re-recorded the orchestration module with a different sponsor tool and left the other modules alone. Learn the concepts in the table above once; the API is a week's work in any of them.

---

## Mage (DE 02, MLOps 03)

Mage is an open-source pipeline tool with a notebook-style UI. A pipeline is a sequence of **blocks**, each a Python (or SQL) file with a decorator that says what kind of block it is. DE 02 ships no code in this snapshot, so the blocks below are illustrative, written in the shape of the API → Postgres pipeline in the [mage-zoomcamp](https://github.com/mage-ai/mage-zoomcamp) starter:

```python
@data_loader
def load_data(*args, **kwargs):
    url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz'
    return pd.read_csv(url, compression='gzip', dtype=taxi_dtypes, parse_dates=parse_dates)

@transformer
def transform(data, *args, **kwargs):
    return data[data['passenger_count'] > 0]

@test
def test_output(output, *args) -> None:
    assert output['passenger_count'].isin([0]).sum() == 0, 'There are rides with zero passengers'

@data_exporter
def export_data(data, *args, **kwargs):
    ...  # Postgres / GCS / BigQuery via io_config.yaml profiles
```

The `@test` block runs against the block's output after every run, a data quality check built into the pipeline rather than bolted on.

### DE 02 sequence

| Section | Pipeline | Concept |
|---|---|---|
| 2.2.2 | Spin up Mage with Docker ([mage-zoomcamp](https://github.com/mage-ai/mage-zoomcamp)) | Projects, blocks, `io_config.yaml` |
| 2.2.3 | API → Postgres | Loader → transformer → exporter |
| 2.2.4 | API → GCS, partitioned vs unpartitioned | Write Parquet partitioned by date so downstream reads one day, not the whole file |
| 2.2.5 | GCS → BigQuery | Lake to warehouse, the standard ELT hop |
| 2.2.6 | Parameterised execution + backfills | Runtime variables such as `execution_date`; a backfill creates one run per date in a range |
| 2.2.7 | Deploy to GCP with Terraform ([mage-ai-terraform-templates](https://github.com/mage-ai/mage-ai-terraform-templates)) | Orchestrator as infrastructure |

### MLOps 03 sequence

```bash
git clone https://github.com/mage-ai/mlops.git
cd mlops && ./scripts/start.sh        # UI on http://localhost:6789
```

| Unit | Pipeline | Concept |
|---|---|---|
| 3.0 | Why operationalise | Productivity, reliability, reproducibility, time-to-value |
| 3.1 | Data preparation | Ingest, prepare, build the training set; data validations as blocks |
| 3.2 | Training | sklearn and XGBoost with hyperopt; experiments to MLflow ([06](06-feature-serve.md)) |
| 3.3 | Observability | SHAP dashboards and alerting |
| 3.4 | Triggers | `sensors/detect_new_data.py` fires the retraining pipeline; an inference pipeline served via API |
| 3.5 | Deployment | AWS permissions, Terraform deploy, CI/CD with GitHub Actions |

Unit 3.4 is the bridge to monitoring: a **sensor** polls for new data and triggers retraining, which is the "conditional retraining" the MLOps project rubric rewards ([08](08-mlops-maturity-and-best-practices.md)).

`03-orchestration/requirements.txt` pins `mlflow==3.17.2`, `prefect==3.9.0`, `pandas==3.1.0`, `scikit_learn==1.9.1`, `xgboost==3.4.1`, `hyperopt==0.3.0`.

---

## Prefect (MLOps 04, 05)

Prefect turns decorated Python functions into tracked runs. The MLOps 04 batch scorer is the clearest worked example of a parameterised, scheduled, backfillable job in either course.

```python
@task
def apply_model(input_file, run_id, output_file):
    logger = get_run_logger()
    df = read_dataframe(input_file)
    dicts = prepare_dictionaries(df)
    model = load_model(run_id)
    y_pred = model.predict(dicts)
    save_results(df, y_pred, run_id, output_file)
    return output_file

def get_paths(run_date, taxi_type, run_id):
    prev_month = run_date - relativedelta(months=1)
    year, month = prev_month.year, prev_month.month
    input_file = f's3://nyc-tlc/trip data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'
    output_file = (f's3://nyc-duration-prediction-alexey/taxi_type={taxi_type}'
                   f'/year={year:04d}/month={month:02d}/{run_id}.parquet')
    return input_file, output_file

@flow
def ride_duration_prediction(taxi_type: str, run_id: str, run_date: datetime = None):
    if run_date is None:
        ctx = get_run_context()
        run_date = ctx.flow_run.expected_start_time
    input_file, output_file = get_paths(run_date, taxi_type, run_id)
    apply_model(input_file=input_file, run_id=run_id, output_file=output_file)
```

Four orchestration ideas in thirty lines:

| Idea | Where |
|---|---|
| **Logical date, not wall-clock date** | `run_date` defaults to the run's `expected_start_time`, so a late or re-run job scores the month it was *scheduled* for |
| **Partitioned, deterministic output** | `taxi_type=/year=/month=/{run_id}.parquet`: a rerun overwrites the same file; Hive-style keys let Spark or BigQuery prune by month |
| **Model version in the path and rows** | `run_id` names the file and fills a `model_version` column, so every prediction traces to an MLflow run |
| **Tasks as the retry unit** | `apply_model` is a `@task`; retries and logs attach to it |

Scheduling (Prefect 2 API, as in the course):

```python
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule

deployment = Deployment.build_from_flow(
    flow=ride_duration_prediction,
    name="ride_duration_prediction",
    parameters={"taxi_type": "green", "run_id": "e1efc53e9bd149078b0c12aeaa6365df"},
    schedule=CronSchedule(cron="0 3 2 * *"),     # 03:00 on the 2nd of each month
    work_queue_name="ml",
)
deployment.apply()
```

Backfill is just the flow called over a range:

```python
@flow
def ride_duration_prediction_backfill():
    d, end = datetime(2021, 3, 1), datetime(2022, 4, 1)
    while d <= end:
        score.ride_duration_prediction(taxi_type='green',
                                       run_id='e1efc53e9bd149078b0c12aeaa6365df', run_date=d)
        d = d + relativedelta(months=1)
```

It works only because the flow takes `run_date` as a parameter and writes to a path derived from it. **A pipeline that reads "today" from the clock can't be backfilled.**

MLOps 05 reuses the pattern: `@flow batch_monitoring_backfill` loops over days, computes Evidently metrics per day and inserts them into Postgres ([05](05-monitor.md)).

**Legacy label.** `prefect.orion` was renamed in Prefect 2.10 and `Deployment.build_from_flow` is gone in Prefect 3, which uses `flow.serve(cron=...)` or `flow.deploy(...)`. The flow and task decorators carry over unchanged. Run the course code with a pinned Prefect 2 or port the deploy script. Source: [Prefect docs](https://docs.prefect.io/).

---

## Modern gaps: Dagster and Airflow

Neither appears in the 2024 materials. Both are standard in production stacks.

| Tool | Model | Why it matters here |
|---|---|---|
| **Dagster** | **Asset-first**: you declare the tables/files/models that should exist (`@asset`) and their dependencies; runs materialise assets | Lineage is the primary object, not a side effect. dbt models import as assets (`dagster-dbt`), so ingest → dbt → ML training is one graph. Partitions and backfills are first-class per asset |
| **Airflow 2.x** | **Task-first** DAGs; TaskFlow API (`@dag`, `@task`) since 2.0; data-aware scheduling via Datasets since 2.4 | The incumbent; most job descriptions list it. The DE 2022 cohort taught it |

```python
from dagster import asset, MonthlyPartitionsDefinition
import pandas as pd

@asset(partitions_def=MonthlyPartitionsDefinition(start_date="2021-01-01"))
def green_trips(context) -> pd.DataFrame:
    month = context.partition_key           # the logical date, as in run_date above
    return pd.read_parquet(f"s3://.../green_tripdata_{month[:7]}.parquet")

@asset
def monthly_revenue(green_trips: pd.DataFrame) -> pd.DataFrame:
    return green_trips.groupby("PULocationID").total_amount.sum().reset_index()
```

The dependency is the function argument. Sources: [Dagster docs](https://docs.dagster.io/), [Airflow docs](https://airflow.apache.org/docs/).

---

## Choosing

| If | Use |
|---|---|
| You are doing the zoomcamp homework | Whatever the cohort uses (Mage in 2024) |
| The pipeline is mostly dbt plus a few Python steps and lineage matters | Dagster |
| The org already runs Airflow | Airflow; don't introduce a second orchestrator |
| A Python team wants the least ceremony for scheduled functions | Prefect |

---

## Run labels

| Material | Needs |
|---|---|
| DE 02 | Videos only in this snapshot; following along needs Docker (Mage) + Postgres; 2.2.4–2.2.7 need a GCP account |
| MLOps 03 | Docker; code lives upstream in [mage-ai/mlops](https://github.com/mage-ai/mlops); 3.5 needs AWS |
| MLOps 04 `batch/` | Legacy: Prefect 2 (`prefect.orion`) + S3 credentials |
| MLOps 05 backfill | Docker (Postgres, Grafana) + Prefect |

---

→ Next: [04-warehouse-and-store.md](04-warehouse-and-store.md) — the tasks orchestration schedules run against storage; how that storage is laid out (partitions, clusters, file formats) decides what each run costs.
