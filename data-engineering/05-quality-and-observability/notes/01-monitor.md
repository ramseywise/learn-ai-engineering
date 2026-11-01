---
origin: course-synthesis
sources:
  - https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/05-monitoring
  - https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering
  - https://docs.evidentlyai.com/
  - https://grafana.com/docs/grafana/latest/administration/provisioning/
  - "Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), appendix (MLOps principles)"
confidence: high
cleaned: 2026-10-31
---
# 5 — Monitor

> Know, before a stakeholder does, that a pipeline or a model has gone wrong: compare each new batch to a reference, store the comparison as a time series, chart it, and alert on it.

---

## Where it sits

Foundation 5 of 6. Everything upstream (ingest, transform, orchestrate, store) can fail silently: a schema changes, a source stops sending, a feature's distribution shifts. Monitoring turns those into numbers with thresholds. The zoomcamp material is MLOps 05 (Evidently + Postgres + Grafana, with Prefect for the batch loop). Pipeline-side checks come from earlier notes: dbt tests and source freshness ([02](../../03-transform-and-orchestrate/notes/01-transform.md)), Mage `@test` blocks ([03](../../03-transform-and-orchestrate/notes/02-orchestrate.md)).

The CURRICULUM.md snapshot listed "Prometheus" for MLOps 05. The 2024 module doesn't use it: metrics go into Postgres and Grafana reads them from there.

---

## What to monitor

MLOps 5.1 sorts monitoring into layers. Each needs a different signal and a different owner:

| Layer | Question | Signal | Course tool |
|---|---|---|---|
| Service health | Is it up and fast? | Latency, error rate, throughput | Out of scope (Grafana/Prometheus in general) |
| Data quality | Is the input well-formed? | Share of missing values, schema, value ranges | `DatasetMissingValuesMetric`, dbt tests |
| Data drift | Does input look like training data? | Per-column distribution distance; number of drifted columns | `DatasetDriftMetric` |
| Prediction drift | Has model output shifted? | Drift score on the prediction column | `ColumnDriftMetric(column_name='prediction')` |
| Model quality | Is it still right? | MAE/RMSE against ground truth | Needs labels; ride duration arrives once the trip ends |
| Pipeline freshness | Did data arrive? | Max `loaded_at` vs now | `dbt source freshness` |

Prediction drift is the first alarm to wire up when labels arrive late. It needs no ground truth, and when the output distribution moves, something upstream moved.

### Three kinds of drift

Drift metrics are proxies: they flag trouble without labels by comparing a **reference window** (data the model is known to handle) with a **test window** (recent production data) (*LLM Engineer's Handbook*, appendix):

| Drift | What moved | Typical response |
|---|---|---|
| Data (covariate) drift | P(inputs): new segment, pipeline bug, schema change | Fix upstream if it's a bug; otherwise consider retraining before quality drops |
| Target drift | P(outputs): shape changes, classes appear or vanish | Often a schema change for the model head (add a class, an "unknown" bucket) rather than a retrain |
| Concept drift | P(output \| input): the same inputs now mean something else | Retrain on recent data; arrives gradually, suddenly (an external event) or periodically (seasonality) |

The test depends on the column: Kolmogorov–Smirnov for one numeric feature, chi-squared for a categorical one, one test per feature. Text and other embedded inputs are multivariate. The usual approach there is to reduce the embeddings of both windows and compare them with maximum mean discrepancy (MMD), a kernel distance between the two distributions. `alibi-detect` ships `KSDrift` and `MMDDrift`, and Evidently has embedding-drift methods too. Several kinds of drift can happen at once, which is why the per-column test suite below matters for finding the source.

---

## Batch vs online monitoring

| | Batch (the course) | Online |
|---|---|---|
| When | A scheduled job over the last window (a day here) | Per request or per micro-window |
| Mechanism | Orchestrated job computes metrics, writes to a DB | Service emits metrics; collector aggregates |
| Fits | Batch scoring ([03](../../03-transform-and-orchestrate/notes/02-orchestrate.md)), daily pipelines | Web/stream serving ([06](../../06-ml-platform/notes/01-feature-serve.md)) |
| Drift tests | Full distribution tests on the window | Approximate or windowed |

The course simulates online monitoring with batch: one day of February 2022 every 10 seconds.

---

## The stack

```yaml
services:
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: example
    ports: ["5432:5432"]
  adminer:
    image: adminer
    ports: ["8080:8080"]
  grafana:
    image: grafana/grafana-enterprise
    user: "472"
    ports: ["3000:3000"]
    volumes:
      - ./config/grafana_datasources.yaml:/etc/grafana/provisioning/datasources/datasource.yaml:ro
      - ./config/grafana_dashboards.yaml:/etc/grafana/provisioning/dashboards/dashboards.yaml:ro
      - ./dashboards:/opt/grafana/dashboards
```

| Service | Role |
|---|---|
| `db` | Postgres; stores one row of metrics per batch |
| `adminer` | Web DB browser on 8080, for checking the rows landed |
| `grafana` | Dashboards on 3000 (login `admin`/`admin`), **provisioned from files** |

Provisioning is the part to copy. The datasource file points Grafana at `db:5432`, database `test`. The dashboards provider loads `dashboards/data_drift.json` from disk. A `docker-compose up` on a fresh machine therefore comes up with the dashboard already there, so dashboards live in version control rather than only in Grafana's internal DB (5.8 "Save Grafana dashboard" exports the JSON for this).

```yaml
datasources:
  - name: PostgreSQL
    type: postgres
    access: proxy
    url: db:5432
    database: test
    user: postgres
    secureJsonData: {password: 'example'}
    jsonData: {sslmode: 'disable'}
```

---

## Reference data

`baseline_model_nyc_taxi_data.ipynb` downloads green taxi January and February 2022 and filters trips to 0–60 minutes. It trains a linear regression on `passenger_count, trip_distance, fare_amount, total_amount, PULocationID, DOLocationID` and writes:

- `models/lin_reg.bin`, the model
- `data/reference.parquet`, **the validation set with predictions**

The reference set is the most consequential choice in monitoring. It should be data the model is known to perform acceptably on, from the same pipeline, with predictions attached. Comparing against raw training data flags differences your model already handles.

---

## Computing metrics with Evidently

```python
from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric

column_mapping = ColumnMapping(
    prediction='prediction',
    numerical_features=['passenger_count', 'trip_distance', 'fare_amount', 'total_amount'],
    categorical_features=['PULocationID', 'DOLocationID'],
    target=None)

report = Report(metrics=[
    ColumnDriftMetric(column_name='prediction'),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()])

report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)
result = report.as_dict()

prediction_drift     = result['metrics'][0]['result']['drift_score']
num_drifted_columns  = result['metrics'][1]['result']['number_of_drifted_columns']
share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']
```

| Metric | Output used | Meaning |
|---|---|---|
| `ColumnDriftMetric('prediction')` | `drift_score` | Distance between reference and current prediction distributions (Evidently picks the test by type and size: K-S, chi-squared, Wasserstein, Jensen-Shannon) |
| `DatasetDriftMetric()` | `number_of_drifted_columns` | How many features crossed their drift threshold; dataset drift = share above a cutoff |
| `DatasetMissingValuesMetric()` | `current.share_of_missing_values` | Data quality on the current batch |

`ColumnMapping` declares types. Without it Evidently guesses, and treats location IDs as numeric.

---

## The batch loop

```python
create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
    timestamp timestamp,
    prediction_drift float,
    num_drifted_columns integer,
    share_missing_values float)
"""

@task
def calculate_metrics_postgresql(curr, i):
    current_data = raw_data[(raw_data.lpep_pickup_datetime >= (begin + datetime.timedelta(i))) &
                            (raw_data.lpep_pickup_datetime <  (begin + datetime.timedelta(i + 1)))]
    current_data['prediction'] = model.predict(current_data[num_features + cat_features].fillna(0))
    report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)
    result = report.as_dict()
    curr.execute(
        "insert into dummy_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values) "
        "values (%s, %s, %s, %s)",
        (begin + datetime.timedelta(i), prediction_drift, num_drifted_columns, share_missing_values))

@flow
def batch_monitoring_backfill():
    prep_db()
    with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example",
                         autocommit=True) as conn:
        for i in range(0, 27):                  # 27 days of Feb 2022
            with conn.cursor() as curr:
                calculate_metrics_postgresql(curr, i)
            # sleep so one "day" lands every SEND_TIMEOUT = 10 seconds
```

The design in one sentence: **monitoring is a pipeline**, with a scheduled job, an idempotent write keyed by the batch's logical timestamp (not `now()`), and a backfill. Everything in [03](../../03-transform-and-orchestrate/notes/02-orchestrate.md) applies to it.

Two things to change before production. Metrics are keyed by `begin + timedelta(i)`, which is right, but the table is dropped on every run, so history is lost. And `fillna(0)` before predict hides the missing values the third metric is meant to catch: impute in the model's preprocessing, not in the monitor.

---

## Dashboard and alerts

`dashboards/data_drift.json` charts the three columns over `timestamp`: **Prediction drift**, **Number of drifted columns**, **Share of missing values**. Grafana alert rules on the same queries (for example `num_drifted_columns > 2` for two consecutive batches) close the loop. The MLOps project rubric gives full monitoring marks only when a threshold triggers an alert or a retraining run ([08](../../06-ml-platform/notes/02-mlops-maturity-and-best-practices.md)); the Mage sensor in MLOps 3.4 is the retraining half.

Give every alert an owner and an action (page, open a ticket, trigger retraining). An alert nobody acts on trains the team to ignore the channel, and requiring two consecutive breaches is the cheapest guard against one noisy batch. For statistical drift tests the p-value is the threshold, and the same trade-off applies: set it too loose and false positives drown the real ones.

Before a drift alert triggers retraining, rule out the cheap explanations: is the data valid, did a schema change, is it one outlier? Retraining is the expensive response and fixes none of those (*LLM Engineer's Handbook*, appendix).

---

## Debugging with test suites (5.9)

When the dashboard shows drift, `debugging_nyc_taxi_data.ipynb` drills in:

```python
from evidently.test_suite import TestSuite
from evidently.test_preset import DataDriftTestPreset
from evidently.metric_preset import DataDriftPreset

suite = TestSuite(tests=[DataDriftTestPreset()])
suite.run(reference_data=reference_data, current_data=problematic_day, column_mapping=column_mapping)
suite.show(mode='inline')        # pass/fail per column

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=reference_data, current_data=problematic_day, column_mapping=column_mapping)
report.show(mode='inline')       # distributions side by side
```

A **Report** describes (distributions, scores). A **TestSuite** asserts (pass/fail against conditions), so it's the object to gate a pipeline on. The notebooks also build an Evidently `Workspace` project with `DashboardPanelCounter` and `DashboardPanelPlot`, Evidently's own UI as an alternative to Grafana.

---

## Pipeline-side monitoring, from earlier notes

| Check | Where | Note |
|---|---|---|
| `unique`, `not_null`, `relationships`, `accepted_values` | dbt `schema.yml` | [02](../../03-transform-and-orchestrate/notes/01-transform.md) |
| Source freshness `error_after: {count: 6, period: hour}` | dbt `sources:` | [02](../../03-transform-and-orchestrate/notes/01-transform.md) |
| Assertion on block output | Mage `@test` | [03](../../03-transform-and-orchestrate/notes/02-orchestrate.md) |
| Schema compatibility on produce | Kafka Schema Registry | [01](../../02-ingest-and-modelling/notes/01-ingest.md) |
| Bytes scanned per query | BigQuery job metadata | [04](../../04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md) |

Data observability as a discipline is covered in the awesome-list podcast with Barr Moses ([references](../../references.md)).

---

## Legacy label

The code uses Evidently's pre-0.7 API (`evidently.report.Report`, `evidently.metrics.*`, `ColumnMapping`, `TestSuite`). `requirements.txt` leaves `evidently` unpinned, so a fresh install gets 0.7+, where these imports moved under `evidently.legacy` and the new API uses `Report` + `DataDefinition`. Pin `evidently<0.7` to run the module as written. Prefect here is optional; the README says it's "not officially supported in the 2024 edition", and the loop runs as plain Python if you remove the decorators.

---

## Run labels

| Material | Needs |
|---|---|
| `baseline_model_nyc_taxi_data.ipynb` | Python + `evidently<0.7`; downloads two Parquet files, then runs offline |
| `docker-compose.yml` + `evidently_metrics_calculation.py` | Docker (Postgres, Adminer, Grafana) + `evidently<0.7` + `psycopg`; Prefect optional |
| `debugging_nyc_taxi_data.ipynb` | Python + `evidently<0.7` |

---

→ Next: [06-feature-serve.md](../../06-ml-platform/notes/01-feature-serve.md) — the model being monitored came from somewhere: tracked experiments, a registry entry, and a deployment as a web service, a stream consumer or a batch job.
