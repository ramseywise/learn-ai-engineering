# 04 Warehouse, lakehouse and streaming

**What.** Where data rests and how it moves once it has landed: columnar warehouses, open table formats over a lake, the lakehouse question, Kafka and stream semantics, and the bill for all of it.

**Why.** Every later stage trusts the store. A bad layout charges you on every query, a bucket with no transactions shows half a rewrite as the truth, and a consumer that saves its offset at the wrong moment miscounts money without raising an error.

**The story.** One year of New York taxi trips runs through this pillar. We lay it out in a warehouse and see one question cost 1.6 GB or 106 MB depending on layout. A nightly rewrite dies halfway and corrupts a dashboard, so we build a transaction log over Parquet and find Delta and Iceberg doing the same thing at scale. With that, the lake seems to replace the warehouse, and we test how far the claim holds. Then trips arrive as a stream, where a crash can lose or double a fare and a tunnel makes an event two minutes late, and we find out what exactly-once and watermarks really promise. Finally the dashboard's $36,000 monthly scan bill makes all the layout decisions concrete.

## Reading order

| # | Chapter | Question it answers |
|---|---|---|
| 1 | [Warehouse and store](notes/01-warehouse-and-store.md) | Why does layout decide the bill, and when does Spark earn its shuffle? |
| 2 | [Table formats](notes/02-table-formats.md) | How does a log turn a bucket into a table? Delta, Iceberg and Hudi on disk. |
| 3 | [Lakehouse against warehouse](notes/03-lakehouse-vs-warehouse.md) | What do you gain and give up when the lake is the system of record? |
| 4 | [Kafka and stream semantics](notes/04-kafka-and-stream-semantics.md) | What do at-least-once, exactly-once and watermarks actually guarantee? |
| 5 | [Cost](notes/05-cost.md) | How do bytes, slots and egress turn into a number before the invoice? |

## Rules of thumb

- Select columns, filter on the partition, cluster the next filter, in that order.
- Partition on the date you always filter by; do not partition small tables.
- A table is a list of files, and readers go through the log or catalog, never a glob.
- Compaction and vacuum are production jobs, not cleanup. Vacuum sets how far time travel reaches.
- Choose copy-on-write or merge-on-read by your update distribution.
- Pick a warehouse unless ML, many engines or lock-in give you a reason not to.
- Commit output and offset together, or make the sink idempotent. Ask "exactly once from where to where?"
- Window on event time; count late data; pick allowed lateness from the business cost of waiting.
- Size consumers for catch-up, and alert on growing lag.
- Run the cost arithmetic before you materialise, and put a byte limit in CI.

## Deck and practice

- **Deck:** [slides/warehouse-lakehouse-streaming.pptx](slides/warehouse-lakehouse-streaming.pptx). Build with `make slides PILLAR=data-engineering/04-warehouse-lakehouse-streaming STRICT=1 PREVIEW=1`.
- **Practice:** [practice/datatalks-de](practice/datatalks-de). `03-data-warehouse` needs a GCP account with BigQuery. `05-batch` needs Java and Spark 3.x, and runs offline after its `download_data.sh`. `06-streaming` needs Docker for the broker (`docker compose up`, then the `python/json_example` producer and consumer).
- **Chapter code:** every block without an `# illustrative` label runs locally. Each chapter gives its `uv run --with ...` line. No cloud account is required.

[References](references.md)
