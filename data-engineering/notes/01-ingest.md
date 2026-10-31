---
origin: course-synthesis
sources:
  - https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform
  - https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/06-streaming
  - https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2024/workshops/dlt.md
  - https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2024/workshops/rising-wave.md
  - https://dlthub.com/docs/intro
  - https://kafka.apache.org/documentation/
  - "Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 3"
  - https://github.com/PacktPublishing/LLM-Engineers-Handbook
confidence: high
cleaned: 2026-10-31
---
# 1 — Ingest

> Getting data from where it is born into a place you control, as batch files or as an event stream, without loading it twice or losing it once.

---

## Where it sits

Ingest is foundation 1 of 6: **ingest** → transform → orchestrate → warehouse/store → monitor → feature-serve. Every later stage assumes the raw layer exists, is complete for a known time window, and can be re-pulled. Background reading: Kleppmann, *Designing Data-Intensive Applications* ([sources/](../sources/kleppmann-designing-data-intensive-applications.pdf)), ch. 4 (encoding and schema evolution, which is why the Kafka section uses Avro with a registry) and ch. 11 (stream processing). The zoomcamp material splits the job three ways:

| Mode | Zoomcamp material | What it teaches |
|---|---|---|
| Batch file load | DE 01 `2_docker_sql` | Chunked CSV/Parquet → Postgres in Docker; the ingest script as a container |
| Infrastructure for landing | DE 01 `1_terraform_gcp` | GCS bucket + BigQuery dataset as code; the lake you ingest into |
| API ingest | DE Workshop 1 (dlt) | Paginated APIs, normalisation, incremental loading |
| Event streams | DE 06 | Kafka producers/consumers, Avro + Schema Registry, Kafka Streams, Faust, Spark Structured Streaming, ksqlDB, Redpanda |
| Streaming SQL | DE Workshop 2 (RisingWave) | Incrementally maintained materialised views over a stream |

DE 01 is listed as cross-cutting infrastructure in the module map: Docker and Terraform are used by every later module, but their first job is to stand up the landing zone, so they live here.

---

## Batch ingest: the chunked loader

The DE 01 loader (`ingest_data.py`) is the shape every batch ingester takes: parse arguments, open a connection, stream the file in chunks, create the table from the schema, append the rest.

```python
engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
df = next(df_iter)
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')  # schema only
df.to_sql(name=table_name, con=engine, if_exists='append')
for df in df_iter:                                                     # remaining chunks
    ...
    df.to_sql(name=table_name, con=engine, if_exists='append')
```

For Parquet the same idea uses `pq.ParquetFile(path).iter_batches(batch_size=100000)`.

What the pattern gets right, and what it leaves to you:

| Property | `ingest_data.py` | What production adds |
|---|---|---|
| Bounded memory | Yes, 100k-row chunks | Same |
| Schema from data | `head(n=0).to_sql` | An explicit schema (see the Spark `StructType` in [04](04-warehouse-and-store.md)) so a bad file can't redefine a column |
| Idempotency | `if_exists='replace'` on every run, a full reload | Partition-scoped overwrite or merge on a key, so a rerun of one day replaces only that day |
| Types | Only the two timestamps are cast | Cast every column at the boundary or in staging ([02](02-transform.md)) |
| Partial failure | A crash mid-loop leaves a half-loaded table | Load to a temp table, swap on success |

Source data: `https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz`. The NYC TLC data is now Parquet at the origin; the DataTalks mirror keeps CSV for the course.

### The loader as a container

```dockerfile
FROM python:3.9.1
RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2
WORKDIR /app
COPY ingest_data.py ingest_data.py
ENTRYPOINT [ "python", "ingest_data.py" ]
```

```bash
docker network create pg-network
docker run -it -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root -e POSTGRES_DB=ny_taxi \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data -p 5432:5432 \
  --network=pg-network --name pg-database postgres:13
docker build -t taxi_ingest:v001 .
docker run -it --network=pg-network taxi_ingest:v001 \
  --user=root --password=root --host=pg-database --port=5432 \
  --db=ny_taxi --table_name=yellow_taxi_trips --url=${URL}
pgcli -h localhost -p 5432 -u root -d ny_taxi
```

The `docker-compose.yaml` in the module replaces the network and two `docker run` calls with two services, `postgres:13` and `pgadmin` on port 8080; compose creates the shared network for you. The point of the container is that the *ingest job* becomes a unit an orchestrator can schedule ([03](03-orchestrate.md)), not a script on someone's laptop.

---

## The landing zone as code: Terraform on GCP

```hcl
provider "google" {
  project = var.project
  region  = var.region
}

resource "google_storage_bucket" "data-lake-bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true
  lifecycle_rule {
    condition { age = 1 }
    action    { type = "AbortIncompleteMultipartUpload" }
  }
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}
```

```bash
gcloud auth application-default login     # or export GOOGLE_APPLICATION_CREDENTIALS=key.json
terraform init && terraform plan && terraform apply
terraform destroy                          # when the homework is done; buckets cost money
```

The provider is pinned at `hashicorp/google 5.6.0`. The service account needs **Storage Admin**, **Storage Object Admin** and **BigQuery Admin**. Those are course-convenient roles; a real pipeline account gets object-level write on one bucket and data-editor on one dataset.

Two settings matter beyond the homework: `force_destroy = true` lets `destroy` delete a non-empty bucket (handy in a course, dangerous in production), and the multipart-abort rule stops half-finished uploads from accumulating as billable storage.

---

## API ingest: dlt (Workshop 1)

Workshop 1 covers reading from APIs, building scalable pipelines, normalising nested JSON and incremental loading, using [dlt](https://dlthub.com/docs/intro). dlt is a Python library, not a service: a pipeline is a function call.

```python
import dlt

@dlt.resource(name="rides", write_disposition="merge", primary_key="record_id")
def rides(updated_at=dlt.sources.incremental("updated_at", initial_value="2024-01-01")):
    for page in paginate(API_URL, since=updated_at.last_value):   # your generator
        yield page

pipeline = dlt.pipeline(pipeline_name="taxi", destination="duckdb", dataset_name="raw")
info = pipeline.run(rides())
print(info)
```

What dlt does that `ingest_data.py` doesn't:

| Concern | dlt mechanism |
|---|---|
| Nested JSON | Normalises nested objects into child tables with generated keys |
| Schema drift | Infers and evolves the destination schema; new columns are added, not dropped |
| Incremental state | `dlt.sources.incremental` stores the high-water mark between runs |
| Idempotent writes | `write_disposition` = `append`, `replace` or `merge` (upsert on `primary_key`) |
| Destinations | DuckDB, BigQuery, Postgres, Snowflake, filesystem/Parquet and others behind one call |

**Modern gap: dlt.** The zoomcamp uses dlt only for one workshop (the course syllabus and module map tag it as ingest), but it is the cleanest Python-native answer to "pull from an API, land it typed, don't reload history". Treat it as the default for API sources and keep the hand-rolled loader for understanding. Source: [dlt docs](https://dlthub.com/docs/intro), [Workshop 1](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2024/workshops/dlt.md).

---

## Streaming ingest: Kafka (DE 06)

### The model

| Term | Meaning | Why it matters for ingest |
|---|---|---|
| Topic | Named, append-only log | The unit you produce to and subscribe to |
| Partition | Ordered shard of a topic | Ordering is per partition only; parallelism = partition count |
| Key | Hashed to choose the partition | Same key → same partition → ordered per key (the course keys rides by `pu_location_id`) |
| Offset | Position in a partition | Consumers commit offsets; replay = reset the offset |
| Consumer group | Consumers sharing a subscription | Each partition goes to one consumer in the group |
| Retention | Time/size the log keeps messages | The window in which a consumer can fall behind and recover |

```bash
kafka-topics.sh --create --topic demo_1 --bootstrap-server localhost:9092 --partitions 2
```

The module's compose file runs Confluent Platform 7.2.0: `broker`, `zookeeper`, `schema-registry` (8081), `control-center` (9021) and `kafka-rest` (8082) on a `kafka-spark-network`. Note the two listeners: `PLAINTEXT://broker:29092` for containers and `PLAINTEXT_HOST://localhost:9092` for your host. Most "can't connect to Kafka" errors in the course are the wrong one of these two.

### JSON producer and consumer

```python
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    key_serializer=lambda key: str(key).encode(),
    value_serializer=lambda x: json.dumps(x.__dict__, default=str).encode('utf-8'))
producer.send('rides_json', key=ride.pu_location_id, value=ride)

consumer = KafkaConsumer(
    'rides_json', bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest', enable_auto_commit=True,
    group_id='consumer.group.id.json-example.1',
    key_deserializer=lambda key: int(key.decode('utf-8')),
    value_deserializer=lambda x: json.loads(x.decode('utf-8'), object_hook=lambda d: Ride.from_dict(d)))
while True:
    records = consumer.poll(1.0)
```

`enable_auto_commit=True` commits offsets on a timer, whether or not your code finished processing. That is at-most-once on a crash. For at-least-once, commit manually after the write succeeds and make the write idempotent.

### Avro and the Schema Registry

JSON carries no contract. The Avro variant registers a schema and serialises against it:

```json
{"type": "record", "name": "RideRecord", "fields": [
  {"name": "vendor_id", "type": "int"},
  {"name": "passenger_count", "type": "int"},
  {"name": "trip_distance", "type": "float"},
  {"name": "payment_type", "type": "int"},
  {"name": "total_amount", "type": "float"}]}
```

```python
schema_registry_client = SchemaRegistryClient({'url': 'http://localhost:8081'})
value_serializer = AvroSerializer(schema_registry_client, value_schema_str, ride_record_to_dict)
producer.produce(topic=topic, key=key_serializer(key, ctx), value=value_serializer(value, ctx),
                 on_delivery=delivery_report)
producer.flush()
```

The registry rejects a producer whose schema breaks the subject's compatibility rule, which turns "an event schema changed and nobody told us" (a scenario in [07](07-data-architectures-mesh-fabric-mdw.md)) from a silent downstream break into a failed deploy upstream.

### Processing the stream: four ways in the module

| Tool | Language | Course example | Run label |
|---|---|---|---|
| Kafka Streams | Java | `groupByKey().windowedBy(TimeWindows.ofSizeAndGrace(10s, 5s)).count()`; stream-stream join after `selectKey` with `JoinWindows.ofTimeDifferenceAndGrace(20m, 5m)` | needs Java/Gradle + a Confluent Cloud key (SASL_SSL config) |
| Faust | Python | `app.Table('vendor_rides_windowed', default=int).tumbling(timedelta(minutes=1), expires=timedelta(hours=1))`; branch with `current_event().forward(high_amount_rides)` when `total_amount >= 40` | needs Docker Kafka; Faust is unmaintained upstream, so legacy |
| Spark Structured Streaming | PySpark | Sliding `F.window(..., "10 minutes", "5 minutes")` counts to console and back to Kafka | needs Spark + `--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1` |
| ksqlDB | SQL | `CREATE STREAM` over a topic, session-windowed `CREATE TABLE ... WINDOW SESSION (60 SECONDS)` | needs Confluent Cloud or a ksqlDB server |

```python
df_kafka_raw = (spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092,broker:29092")
    .option("subscribe", topic).option("startingOffsets", "earliest").load())

counts = df.groupBy(F.window(timeColumn=df.tpep_pickup_datetime,
                             windowDuration="10 minutes", slideDuration="5 minutes"),
                    df.vendor_id).count()

(counts.writeStream.outputMode('complete')
       .trigger(processingTime='5 seconds').format("console").start())
# Kafka sink: .format("kafka").option("topic", ...).option("checkpointLocation", "checkpoint").start()
```

```sql
CREATE STREAM ride_streams (VendorId varchar, trip_distance double, payment_type varchar)
  WITH (KAFKA_TOPIC='rides', VALUE_FORMAT='JSON');

CREATE TABLE payment_type_sessions AS
  SELECT payment_type, count(*)
  FROM RIDE_STREAMS
  WINDOW SESSION (60 SECONDS)
  GROUP BY payment_type
  EMIT CHANGES;
```

Window vocabulary, since every tool above uses it:

| Window | Definition | Course example |
|---|---|---|
| Tumbling | Fixed size, no overlap | Faust 1-minute vendor counts |
| Hopping / sliding | Fixed size, overlapping by a slide | Spark 10 min every 5 min |
| Session | Closed by a gap of inactivity | ksqlDB 60-second sessions |
| Grace | How late an event may arrive and still count | Kafka Streams `ofSizeAndGrace(10s, 5s)` |

The `checkpointLocation` on the Spark Kafka sink is what makes a restarted job resume at the right offsets instead of reprocessing or skipping.

### Redpanda

The Python examples also run against Redpanda (v23.2.26 in the compose file), a Kafka-API-compatible broker without ZooKeeper or a JVM. The module aliases `rpk`:

```bash
rpk cluster info
rpk topic create rides --partitions 2 --replicas 1
rpk topic consume rides
rpk group list && rpk group describe <group>
```

Swap the broker, keep the client code: that is the practical meaning of "Kafka API compatible".

---

## Streaming SQL: RisingWave (Workshop 2)

Workshop 2 ("Stream processing with SQL") uses RisingWave, a Postgres-wire-compatible streaming database. You create a source over a Kafka topic and define `CREATE MATERIALIZED VIEW ... AS SELECT ...`; the engine maintains the view incrementally as events arrive, so a dashboard query reads a precomputed answer. It sits between ksqlDB (stream-native SQL) and a warehouse (batch SQL), and it is the course's only example of serving a continuously updated aggregate with plain SQL. Workshop materials live upstream only: [rising-wave.md](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2024/workshops/rising-wave.md).

---

## Unstructured ingest: crawling documents for an LLM

The zoomcamps ingest tables. An LLM application usually ingests documents: articles, repos and posts scraped from the web. The *LLM Engineer's Handbook* builds this as an ordinary ETL into a document store, and three of its design choices transfer (*LLM Engineer's Handbook*, ch. 3):

- **Normalize by content type, not by source.** Every crawler emits one of three document classes (article, repository, post), with the source URL kept in metadata. Adding a new site means one new crawler. If each source got its own document class, every downstream layer would need code for it.
- **Dispatch on the URL's domain, with a fallback.** A registry maps domain patterns to crawler classes. Anything unmatched goes to a generic HTML crawler.
- **A schemaless store is fine at small scale.** MongoDB as the "warehouse" suits hundreds of heterogeneous text documents. The authors say to move to Snowflake or BigQuery at millions. The feature pipeline reads from this store on its own schedule. The store is the only contract between the two.

```python
import re
from urllib.parse import urlparse

class CrawlerDispatcher:
    def __init__(self):
        self._registry: dict[str, type[BaseCrawler]] = {}

    def register(self, domain: str, crawler: type[BaseCrawler]) -> "CrawlerDispatcher":
        self._registry[rf"https://(www\.)?{re.escape(domain)}/*"] = crawler
        return self

    def get_crawler(self, url: str) -> BaseCrawler:
        for pattern, crawler in self._registry.items():
            if re.match(pattern, url):
                return crawler()
        return CustomArticleCrawler()          # generic fallback: fetch HTML, extract text

dispatcher = (CrawlerDispatcher()
              .register("medium.com", MediumCrawler)
              .register("github.com", GithubCrawler))
```

Count successes and attempts per domain on every run (the book's pipeline writes them into run metadata). A crawler that silently starts returning empty pages is the unstructured version of a source that stops sending. One caution the book skips: its Medium and LinkedIn crawlers log in and drive a browser with Selenium. That is fragile, and it is against those platforms' terms. Prefer official APIs, exports or RSS where they exist.

---

## Choosing batch or stream

| Question | Batch (DE 01, dlt) | Stream (DE 06) |
|---|---|---|
| Freshness the consumer actually needs | Hours or days | Seconds to minutes |
| Replay | Re-download the file or re-run the API window | Reset offsets within retention |
| Ordering | Sort after load | Per-partition, by key |
| Failure unit | One file or one day | One message; needs idempotent sinks |
| Operational cost | A scheduled container | Always-on brokers, schema registry, consumers |

Default to batch. Move a source to streaming when a named consumer needs the freshness. Real-time inference ([06](06-feature-serve.md), Kinesis + Lambda) is the course's example of a consumer that does.

---

## Run labels

| Material | Needs |
|---|---|
| DE 01 `2_docker_sql` | Docker; runs offline after the CSV download |
| DE 01 `1_terraform_gcp` | Terraform + a GCP account and service-account key |
| DE 06 `python/` (JSON, Avro, Faust, Spark streaming, Redpanda) | Docker (Kafka or Redpanda compose) |
| DE 06 `java/` | Java + Gradle + a Confluent Cloud API key |
| DE 06 `ksqldb/` | Confluent Cloud or a self-hosted ksqlDB server |
| Workshops 1–2 | Upstream only; dlt runs offline against DuckDB |

---

→ Next: [02-transform.md](02-transform.md) — the raw tables ingest lands are the `source()` that dbt staging models select from.
