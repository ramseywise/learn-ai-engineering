---
origin: synthesis
sources:
  - notes/
confidence: high
cleaned: 2026-11-01
---
# 03 — Transform and orchestrate

How landed tables become tested models, and how those models get built on schedule, in the right order, for the right day. This is where a platform's promises either become executable or remain folklore.

**Why it comes here.** [Pillar 2](../02-ingest-and-modelling/README.md) produced raw data you can re-pull and a model that says what a row means. This pillar is what turns those into something that runs every night. Everything later relies on it: [warehouse layout](../04-warehouse-lakehouse-streaming/README.md) prices these runs, and [monitors](../05-quality-and-observability/README.md) watch what they produce.

**The story.** We build a dbt project and watch an inner join lose 5,680 trips and about $96,000 with every test green, then write a toy orchestrator in fifty lines to see that retries, skips and logical dates hold no magic. A single extra dimension row overstates revenue by 12.5 percent until a grain test catches it, a snapshot misses a state that lasted one day, and a watermark loses a late row for good. Then an append run twice doubles the table, so we learn to replace a period and show that a backfill with one worker or four ends in the same hash. Finally the same pipeline runs in Dagster and Airflow, breaks the same three ways, and shows what each tool can tell you the morning after.

## Reading order

| # | Chapter | Question it answers |
|---|---|---|
| 1 | [Transform](notes/01-transform.md) | How does a wrong number become traceable to one line in one file? |
| 2 | [Orchestrate](notes/02-orchestrate.md) | What does an orchestrator decide that a cron line leaves out? |
| 3 | [dbt tests, snapshots and incremental models](notes/03-dbt-tests-snapshots-incremental.md) | What breaks as the project grows, and in what order? |
| 4 | [Idempotency and backfills](notes/04-idempotency-and-backfills.md) | How do you make running anything twice boring? |
| 5 | [Dagster and Airflow](notes/05-dagster-and-airflow.md) | What does each tool think a pipeline is, and when does that matter? |

The plan listed four chapters. Dagster and Airflow got a chapter of their own, since the comparison needs running code in both.

Then go to [04, warehouse, lakehouse and streaming](../04-warehouse-lakehouse-streaming/README.md). The sequenced path across all seven pillars is in the [curriculum](../CURRICULUM.md).

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [Programming](../../programming/README.md) | Python and SQL fluency, which the zoomcamps assume |

**Feeds into**

| Chapter | Why |
|---|---|
| [DA 06/06 SQL for analytics](../../data-analytics/06-applied-analyses/notes/06-sql-for-analytics.md) | The kind of question an analyst asks of a mart |

## Rules of thumb

| Situation | Rule | Why |
|---|---|---|
| Staging model | Rename, cast, dedupe, nothing else | Logic hidden in staging is logic nobody reviews |
| A fact joins a dimension | Left join to a default row, and test the grain on its key | Inner joins lose revenue; duplicates in a dimension inflate it, and no column test sees either |
| You wrote a `dbt build` test | Remember it protects what is downstream | The tested table has already been rebuilt |
| A task needs a date | Take the logical date as a parameter | `now()` makes a rerun compute another period |
| Before turning on retries | Make the write idempotent | A retry can repeat a write that already happened |
| A batch table | Replace the period in one transaction | Merge leaves rows the source deleted |
| A source overwrites rows you need | Snapshot it, as often as it changes | A snapshot cannot be rebuilt, and the states between runs are gone |
| A nightly rebuild takes too long | Incremental with a `unique_key` and a lookback, plus a periodic full refresh | Watermarks do not see late rows |
| Before a backfill | Decide which dimension version history should use | A rerun against today's labels rewrites the past |
| An Airflow 3 cron schedule | Name the timetable | A bare cron string makes `ds` the day in progress |
| Choosing an orchestrator | The one you already run | A second one costs more than any feature gains |

## Deck and practice

- **Deck:** [slides/transform-and-orchestrate.pptx](slides/transform-and-orchestrate.pptx), built from [slides/deck.yaml](slides/deck.yaml). Rebuild with `make slides PILLAR=data-engineering/03-transform-and-orchestrate STRICT=1 PREVIEW=1`.
- **Practice:** [practice/](practice/) has one script per chapter holding that chapter's code, with three for chapter 5. Each prints its output and writes only to a temporary folder. Run from `practice/`:

```bash
uv run --with dbt-duckdb --with pyarrow --with numpy python 01_transform.py
uv run --with duckdb --with prefect python 02_orchestrate.py
uv run --with dbt-duckdb python 03_dbt_depth.py
uv run --with duckdb python 04_idempotency.py
uv run --with dagster --with duckdb python 05_dagster.py
uv run --with dagster-dbt --with dbt-duckdb python 05_dagster_dbt.py
uv run --python 3.12 --with apache-airflow --with duckdb python 05_airflow.py   # starts airflow standalone for a minute or two
```

- **Zoomcamp:** [practice/datatalks-de/](practice/datatalks-de/) holds the DataTalks.Club [workflow orchestration](practice/datatalks-de/02-workflow-orchestration/) and [analytics engineering](practice/datatalks-de/04-analytics-engineering/) modules. Chapters 1 and 2 say what each needs in their Run labels. It is a snapshot: its orchestration module uses Mage, while the [current course](https://github.com/DataTalksClub/data-engineering-zoomcamp) uses Kestra.

Sources: [references.md](references.md).
