---
origin: course-synthesis
sources:
  - https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse
  - https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/05-batch
  - https://cloud.google.com/bigquery/docs/partitioned-tables
  - https://cloud.google.com/bigquery-ml/docs/export-model-tutorial
  - https://spark.apache.org/docs/latest/sql-programming-guide.html
  - https://duckdb.org/docs/
  - https://docs.pola.rs/
  - https://delta.io/
  - https://iceberg.apache.org/docs/latest/
confidence: high
cleaned: 2026-10-31
---
# 4 — Warehouse and Store

> Where data rests and how it's laid out: a columnar warehouse (BigQuery) that bills by bytes scanned, a lake of Parquet files, and a distributed engine (Spark) for the jobs too big for one machine.

---

## Where it sits

Foundation 4 of 6. Ingest ([01](../../02-ingest-and-modelling/notes/01-ingest.md)) lands files in a bucket; transform ([02](../../03-transform-and-orchestrate/notes/01-transform.md)) runs SQL somewhere. This note is the *somewhere*. The zoomcamp material is DE 03 (BigQuery) and DE 05 (Spark batch). Background reading: Kleppmann, *Designing Data-Intensive Applications* (DDIA, [sources/](../../sources/kleppmann-designing-data-intensive-applications.pdf)), ch. 3 (storage engines, column-oriented storage), ch. 6 (partitioning) and ch. 10 (batch processing).

---

## OLTP vs OLAP

| | OLTP (Postgres in DE 01) | OLAP (BigQuery in DE 03) |
|---|---|---|
| Workload | Many small reads and writes by key | Few large scans and aggregations |
| Storage | Row-oriented | Column-oriented (DDIA ch. 3) |
| Schema | Normalised | Denormalised: star schema, wide fact tables |
| Cost driver | Rows touched | Bytes scanned in the columns you select |
| Users | Applications | Analysts, BI, ML training |

The column layout is why `SELECT *` is expensive in BigQuery and why the course's first BigQuery lesson is about scanning less.

---

## BigQuery (DE 03)

### External table → native table

```sql
CREATE OR REPLACE EXTERNAL TABLE `taxi-rides-ny.nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'CSV',
  uris = ['gs://nyc-tl-data/trip data/yellow_tripdata_2019-*.csv',
          'gs://nyc-tl-data/trip data/yellow_tripdata_2020-*.csv']
);

CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_non_partitoned AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;
```

An external table leaves the data in GCS and reads it at query time. Good for exploration and for a lake that other engines also read; slower, and BigQuery can't estimate its cost up front. Materialising to a native table is the "load" in ELT.

### Partitioning: the 15× lesson

```sql
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_partitoned
PARTITION BY DATE(tpep_pickup_datetime) AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;

-- non-partitioned: scans 1.6 GB
-- partitioned:     scans ~106 MB
SELECT DISTINCT(VendorID)
FROM taxi-rides-ny.nytaxi.yellow_tripdata_partitoned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';

SELECT table_name, partition_id, total_rows
FROM `nytaxi.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'yellow_tripdata_partitoned'
ORDER BY total_rows DESC;
```

Same query, same answer, 1.6 GB → ~106 MB, because the `WHERE` on the partition column lets BigQuery skip every other day's storage.

### Clustering: sorting inside partitions

```sql
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_partitoned_clustered
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;

-- partitioned only:        1.1 GB
-- partitioned + clustered: 864.5 MB
SELECT count(*) as trips
FROM taxi-rides-ny.nytaxi.yellow_tripdata_partitoned_clustered
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'
  AND VendorID=1;
```

| | Partitioning | Clustering |
|---|---|---|
| Column type | One date/timestamp, integer range, or ingestion time | Up to four columns, any orderable type |
| Cost known before the query | Yes, the estimate reflects pruning | No, the savings show up only after |
| Granularity limit | Partition count limit per table (thousands); tiny partitions hurt | No count limit |
| Use for | The column every query filters on (almost always event date) | High-cardinality filters and sort keys after that (vendor, zone) |
| Maintenance | None | Automatic re-clustering as data is appended |

Rule from the module's best-practices section: partition on the date you filter by, cluster on what you filter by next, and select only the columns you need. Don't partition a small table: under about 1 GB the per-partition metadata costs more than it saves.

### BigQuery ML

Train and serve a model with SQL, without moving data:

```sql
CREATE OR REPLACE MODEL `taxi-rides-ny.nytaxi.tip_model`
OPTIONS (model_type='linear_reg',
         input_label_cols=['tip_amount'],
         DATA_SPLIT_METHOD='AUTO_SPLIT') AS
SELECT * FROM `taxi-rides-ny.nytaxi.yellow_tripdata_ml`
WHERE tip_amount IS NOT NULL;

SELECT * FROM ML.FEATURE_INFO(MODEL `taxi-rides-ny.nytaxi.tip_model`);
SELECT * FROM ML.EVALUATE(MODEL `taxi-rides-ny.nytaxi.tip_model`, (SELECT ... ));
SELECT * FROM ML.PREDICT(MODEL `taxi-rides-ny.nytaxi.tip_model`, (SELECT ... ));
SELECT * FROM ML.EXPLAIN_PREDICT(MODEL `taxi-rides-ny.nytaxi.tip_model`, (SELECT ... ),
                                 STRUCT(3 as top_k_features));
```

The training table first casts `PULocationID`, `DOLocationID` and `payment_type` to `STRING`. That one-line choice makes BigQuery one-hot encode them as categories instead of treating zone 264 as "bigger than" zone 1. Hyperparameter tuning adds `num_trials=5, max_parallel_trials=2, l1_reg=hparam_range(0, 20), l2_reg=hparam_candidates([0, 0.1, 1, 10])` to `OPTIONS`.

Export and serve outside BigQuery (`extract_model.md`):

```bash
bq --project_id taxi-rides-ny extract -m nytaxi.tip_model gs://taxi_ml_model/tip_model
gsutil cp -r gs://taxi_ml_model/tip_model /tmp/model
mkdir -p serving_dir/tip_model/1 && cp -r /tmp/model/tip_model/* serving_dir/tip_model/1
docker run -p 8501:8501 --mount type=bind,source=`pwd`/serving_dir/tip_model,target=/models/tip_model \
  -e MODEL_NAME=tip_model -t tensorflow/serving &
curl -d '{"instances": [{"passenger_count":1, "trip_distance":12.2, "PULocationID":"193",
  "DOLocationID":"264", "payment_type":"2","fare_amount":20.4,"tolls_amount":0.0}]}' \
  -X POST http://localhost:8501/v1/models/tip_model:predict
```

BQML is the cheapest path from warehouse to a baseline model. The MLflow path in [06](../../06-ml-platform/notes/01-feature-serve.md) is the one that scales to custom models and a registry.

---

## Spark batch (DE 05)

### Session, schema, write

```python
spark = SparkSession.builder.master("local[*]").appName('test').getOrCreate()

schema = types.StructType([
    types.StructField('hvfhs_license_num', types.StringType(), True),
    types.StructField('dispatching_base_num', types.StringType(), True),
    types.StructField('pickup_datetime', types.TimestampType(), True),
    types.StructField('dropoff_datetime', types.TimestampType(), True),
    types.StructField('PULocationID', types.IntegerType(), True),
    types.StructField('DOLocationID', types.IntegerType(), True),
    types.StructField('SR_Flag', types.StringType(), True)])

df = spark.read.option("header", "true").schema(schema).csv('fhvhv_tripdata_2021-01.csv')
df.repartition(24).write.parquet('fhvhv/2021/01/')
```

| Choice | Why |
|---|---|
| Explicit `StructType` instead of `inferSchema` | Inference reads the data twice and guesses; an explicit schema is a contract and fails loudly |
| `repartition(24)` before write | One CSV becomes 24 Parquet files, so 24 executors can read in parallel later |
| Parquet out | Columnar, compressed, typed; the format every later step reads |

`download_data.sh TAXI_TYPE YEAR` loops over months and lays files out as `data/raw/{taxi_type}/{year}/{month}/`.

### DataFrames, SQL and the union

```python
df_green = df_green.withColumnRenamed('lpep_pickup_datetime', 'pickup_datetime')
df_yellow = df_yellow.withColumnRenamed('tpep_pickup_datetime', 'pickup_datetime')

df_trips_data = (df_green.select(common_colums).withColumn('service_type', F.lit('green'))
    .unionAll(df_yellow.select(common_colums).withColumn('service_type', F.lit('yellow'))))
df_trips_data.registerTempTable('trips_data')      # createOrReplaceTempView in current Spark

df_result = spark.sql("""
SELECT PULocationID AS revenue_zone,
       date_trunc('month', pickup_datetime) AS revenue_month,
       service_type,
       SUM(total_amount) AS revenue_monthly_total_amount,
       AVG(trip_distance) AS avg_montly_trip_distance
FROM trips_data
GROUP BY 1, 2, 3
""")
df_result.coalesce(1).write.parquet(output, mode='overwrite')
```

This is the same monthly-revenue mart as the dbt model in [02](../../03-transform-and-orchestrate/notes/01-transform.md), written in Spark: the logic is portable, the engine is a cost and scale decision. `coalesce(1)` makes one output file without a shuffle; fine for a small result, a bottleneck for a large one.

UDFs exist for logic SQL can't express (`F.udf(crazy_stuff, returnType=types.StringType())`) but run row-at-a-time in Python. Prefer built-in `F.*` functions.

### What happens under a `groupBy` and a `join` (07)

| Operation | Physical plan | Cost |
|---|---|---|
| `groupBy(hour, zone).sum()` | Partial aggregate per partition → **shuffle** by key → final aggregate | Shuffle = network + disk; the expensive step |
| Join two large tables on `['hour', 'zone']` (outer, in the course) | Sort-merge join: shuffle both sides by key | Two shuffles |
| Join large to small (zones lookup) | **Broadcast** the small table to every executor | No shuffle of the large side |

### RDDs and `mapPartitions` (08)

The DataFrame `groupBy` rewritten by hand shows what Spark does underneath:

```python
def prepare_for_grouping(row):
    hour = row.lpep_pickup_datetime.replace(minute=0, second=0, microsecond=0)
    return ((hour, row.PULocationID), (row.total_amount, 1))

def calculate_revenue(left_value, right_value):
    return (left_value[0] + right_value[0], left_value[1] + right_value[1])

df_result = (rdd.filter(filter_outliers)
                .map(prepare_for_grouping)
                .reduceByKey(calculate_revenue)       # the shuffle
                .map(unwrap)
                .toDF(result_schema))
```

`mapPartitions` is the pattern worth keeping. It hands your function an iterator over a whole partition, so you can batch rows into a pandas DataFrame and call a model once per partition instead of once per row:

```python
def apply_model_in_batch(rows):
    df = pd.DataFrame(rows, columns=columns)
    df['predicted_duration'] = model_predict(df)
    for row in df.itertuples():
        yield row

df_predicts = duration_rdd.mapPartitions(apply_model_in_batch).toDF().drop('Index')
```

That is batch scoring at Spark scale, the big-data sibling of the Prefect batch scorer in [03](../../03-transform-and-orchestrate/notes/02-orchestrate.md).

### Where Spark runs

| Mode | Command | Run label |
|---|---|---|
| Local | `master("local[*]")`; set `PYTHONPATH` to include Spark's `python/` and `py4j-*.zip` | needs Java 11/17 + Spark 3.x |
| Standalone cluster | `./sbin/start-master.sh`; `./sbin/start-worker.sh spark://<host>:7077`; `spark-submit --master=spark://<host>:7077 06_spark_sql.py --input_green=... --output=...` | same, on a VM |
| GCS from local Spark | `gcs-connector-hadoop3-2.2.5.jar` on the classpath; `hadoopConf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")` plus a key file | + GCP key |
| Dataproc | `gcloud dataproc jobs submit pyspark --cluster=de-zoomcamp-cluster --region=europe-west6 gs://.../06_spark_sql.py -- --input_green=gs://... --output=gs://...` | needs GCP Dataproc |
| Dataproc → BigQuery | `--jars=gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar`; `spark.conf.set('temporaryGcsBucket', bucket)`; `df.write.format('bigquery').option('table', output).save()` | needs GCP Dataproc + BigQuery |

Write the job with `argparse` inputs and outputs (as `06_spark_sql.py` does) and the same file runs locally, on a standalone cluster and on Dataproc.

---

## Modern gaps: DuckDB, Polars, Delta Lake and Iceberg

Not covered by either zoomcamp; standard in current stacks.

**DuckDB**: an in-process OLAP engine, SQLite for analytics. It queries Parquet, CSV and S3/GCS directly with vectorised columnar execution. For single-node workloads up to hundreds of GB it largely replaces both the local Spark setup above and a warehouse round-trip.

```python
import duckdb
duckdb.sql("""
  SELECT PULocationID, date_trunc('month', lpep_pickup_datetime) AS m, sum(total_amount)
  FROM 'data/pq/green/2021/*/*.parquet'
  GROUP BY 1, 2
""").df()
```

It is also a dbt target (`dbt-duckdb`) and a dlt destination ([01](../../02-ingest-and-modelling/notes/01-ingest.md)), which makes a laptop-only version of this whole course possible.

**Polars**: a Rust DataFrame library with a lazy query optimiser and multi-threaded execution. It's the default over pandas for large local processing; `scan_parquet(...).filter(...).group_by(...).agg(...).collect()` pushes filters into the scan the way Spark does.

**Delta Lake / Apache Iceberg**: open table formats that add a transaction log on top of Parquet in object storage. They give ACID writes, schema evolution, time travel (`VERSION AS OF`), `MERGE` upserts and hidden partitioning. They turn the course's "bucket of Parquet files" into tables that Spark, Trino, DuckDB, Snowflake and BigQuery can all read and write safely. This is the *lakehouse* in Serra's taxonomy ([07](../../07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md)): the lake behaves like a warehouse, so the modern data warehouse's copy into a relational warehouse becomes optional.

| Need | Course tool | Modern default |
|---|---|---|
| Single-node analytics over Parquet | Spark `local[*]` | DuckDB or Polars |
| Distributed batch beyond one machine | Spark on Dataproc | Spark (unchanged), often on Delta/Iceberg tables |
| Updatable lake tables | Overwrite partitions | Delta or Iceberg `MERGE` |
| Serverless warehouse | BigQuery | BigQuery, Snowflake, or Iceberg tables BigQuery reads |

Sources: [DuckDB docs](https://duckdb.org/docs/), [Polars docs](https://docs.pola.rs/), [Delta Lake](https://delta.io/), [Apache Iceberg](https://iceberg.apache.org/docs/latest/); the awesome-list entry [*An Introduction to Modern Data Lake Storage Layers*](https://dacort.dev/posts/modern-data-lake-storage-layers/) compares Hudi, Iceberg and Delta.

---

## Run labels

| Material | Needs |
|---|---|
| DE 03 `big_query.sql`, `big_query_ml.sql` | A GCP account with BigQuery + the taxi CSVs in GCS (`extras/web_to_gcs.py` uploads them) |
| DE 03 `extract_model.md` | GCP + Docker (`tensorflow/serving`) |
| DE 05 notebooks 03–08 | Java + Spark 3.x locally; runs offline after `download_data.sh` |
| DE 05 `09_spark_gcs.ipynb`, `cloud.md` | GCS connector jar + GCP key; Dataproc for the cluster jobs |

---

→ Next: [05-monitor.md](../../05-quality-and-observability/notes/01-monitor.md) — once data and models sit in tables and serve predictions, you need to know when they go wrong: drift, missing values, freshness.
