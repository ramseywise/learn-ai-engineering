---
origin: course-synthesis
sources:
  - https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering
  - https://docs.getdbt.com/docs/build/materializations
  - https://docs.getdbt.com/docs/build/data-tests
confidence: high
cleaned: 2026-10-31
---
# 2 — Transform

> Turn raw landed tables into typed, deduplicated, tested models in layers (source → staging → core → mart), written as SQL in version control with dbt.

---

## Where it sits

Foundation 2 of 6. Ingest ([01](01-ingest.md)) lands raw data that is untyped, duplicated and named by the source system. Transform makes it usable. Orchestrate ([03](03-orchestrate.md)) schedules it, and the warehouse ([04](04-warehouse-and-store.md)) executes it. The zoomcamp material is DE 04, *Analytics engineering*, and its worked project `taxi_rides_ny/`.

DE 04 assumes week 3 is done: a running warehouse (BigQuery or Postgres) with yellow and green trip data for 2019–2020 and FHV for 2019 loaded.

---

## ETL vs ELT, and why dbt is ELT

| | ETL | ELT |
|---|---|---|
| Transform runs | Before load, in a separate engine | After load, inside the warehouse |
| Raw data kept | Often not | Yes, the raw layer is the replay point |
| Compute | Pipeline servers | Warehouse (BigQuery slots, Postgres) |
| Who writes it | Data engineers in Python/Java | Analytics engineers in SQL |

dbt does not move data. It compiles Jinja-templated `SELECT` statements into DDL/DML and runs them in your warehouse, in dependency order. That is why the DE 04 project runs unchanged on BigQuery and Postgres: the adapter changes, the SQL mostly doesn't.

---

## The layers in `taxi_rides_ny`

```
models/
  staging/   stg_green_tripdata.sql, stg_yellow_tripdata.sql, schema.yml   → views
  core/      dim_zones.sql, fact_trips.sql, dm_monthly_zone_revenue.sql, schema.yml → tables
seeds/       taxi_zone_lookup.csv
macros/      get_payment_type_description.sql
```

| Layer | Grain and job | Materialisation | Course model |
|---|---|---|---|
| Source | Declared, not built: points at raw tables | n/a | `sources: staging.green_tripdata`, `yellow_tripdata` |
| Staging | One model per source table; rename, cast, dedupe, nothing else | `view` | `stg_green_tripdata` |
| Core | Facts and dimensions; joins across sources | `table` | `fact_trips`, `dim_zones` |
| Mart / data mart | Aggregates for one consumer | `table` | `dm_monthly_zone_revenue` |

The materialisations are set per folder in `dbt_project.yml`, not per file:

```yaml
models:
  taxi_rides_ny:
    staging:
      materialized: view
    core:
      materialized: table
vars:
  payment_type_values: [1, 2, 3, 4, 5, 6]
seeds:
  taxi_rides_ny:
    taxi_zone_lookup:
      +column_types:
        locationid: numeric
```

dbt's four materialisations: `view` (cheap to build, query cost paid on read), `table` (rebuilt each run), `incremental` (insert/merge only new rows, needs a filter on `is_incremental()`), `ephemeral` (inlined as a CTE). The course uses only the first two; incremental is the one you'll need first in production, once a full rebuild of `fact_trips` gets slow.

---

## A staging model, line by line

```sql
with tripdata as (
  select *,
    row_number() over(partition by vendorid, lpep_pickup_datetime) as rn
  from {{ source('staging','green_tripdata') }}
  where vendorid is not null
)
select
    {{ dbt_utils.generate_surrogate_key(['vendorid', 'lpep_pickup_datetime']) }} as tripid,
    {{ dbt.safe_cast("vendorid", api.Column.translate_type("integer")) }} as vendorid,
    {{ dbt.safe_cast("pulocationid", api.Column.translate_type("integer")) }} as pickup_locationid,
    cast(lpep_pickup_datetime as timestamp) as pickup_datetime,
    cast(trip_distance as numeric) as trip_distance,
    cast(total_amount as numeric) as total_amount,
    coalesce({{ dbt.safe_cast("payment_type", api.Column.translate_type("integer")) }},0) as payment_type,
    {{ get_payment_type_description("payment_type") }} as payment_type_description
from tripdata
where rn = 1

{% if var('is_test_run', default=true) %}
  limit 100
{% endif %}
```

| Line | Pattern | Why |
|---|---|---|
| `source('staging', ...)` | Declared source | Lineage starts here; `dbt docs` draws the graph from it |
| `row_number() ... where rn = 1` | Dedupe on the natural key | The raw data has duplicate (vendor, pickup time) rows |
| `generate_surrogate_key` | Hash of the natural key | A stable `tripid` to test for uniqueness and join on |
| `dbt.safe_cast` + `translate_type` | Adapter-neutral cast | Same model on BigQuery and Postgres; a bad value becomes null, not a failed run |
| `coalesce(..., 0)` | Explicit unknown | Null payment types fall into a bucket the macro labels |
| `var('is_test_run', default=true)` | Dev limit | Development builds touch 100 rows; prod overrides it |

The full build overrides the variable:

```bash
dbt build --select stg_green_tripdata --vars '{is_test_run: false}'
```

---

## Macros and packages

```sql
{% macro get_payment_type_description(payment_type) -%}
    case {{ dbt.safe_cast("payment_type", api.Column.translate_type("integer")) }}
        when 1 then 'Credit card'
        when 2 then 'Cash'
        when 3 then 'No charge'
        when 4 then 'Dispute'
        when 5 then 'Unknown'
        when 6 then 'Voided trip'
        else 'EMPTY'
    end
{%- endmacro %}
```

A macro is a Jinja function that returns SQL. Use one when the same CASE or expression appears in two models; the yellow and green staging models both call this one.

`packages.yml` pulls community macros; `dbt deps` installs them:

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1
  - package: dbt-labs/codegen
    version: 0.12.1
```

`dbt_utils` supplies `generate_surrogate_key` and many generic tests. `codegen` writes the boilerplate `schema.yml` and base models from an existing table.

---

## The fact model

```sql
with green_tripdata as (
    select *, 'Green' as service_type from {{ ref('stg_green_tripdata') }}
),
yellow_tripdata as (
    select *, 'Yellow' as service_type from {{ ref('stg_yellow_tripdata') }}
),
trips_unioned as (
    select * from green_tripdata
    union all
    select * from yellow_tripdata
),
dim_zones as (
    select * from {{ ref('dim_zones') }} where borough != 'Unknown'
)
select trips_unioned.tripid, trips_unioned.service_type,
       pickup_zone.borough as pickup_borough, pickup_zone.zone as pickup_zone,
       dropoff_zone.borough as dropoff_borough, dropoff_zone.zone as dropoff_zone,
       trips_unioned.pickup_datetime, trips_unioned.total_amount -- ...
from trips_unioned
inner join dim_zones as pickup_zone  on trips_unioned.pickup_locationid  = pickup_zone.locationid
inner join dim_zones as dropoff_zone on trips_unioned.dropoff_locationid = dropoff_zone.locationid
```

Three things to see:

1. **`ref()` builds the DAG.** dbt parses every `ref` to order the run: staging before core, `dim_zones` (built from the `taxi_zone_lookup` seed) before `fact_trips`. You never write the order by hand.
2. **Union needs identical column lists.** The two staging models are written to the same column order so `select *` unions safely. The Spark version of this union in [04](04-warehouse-and-store.md) has to compute the common columns explicitly.
3. **The inner joins drop rows.** Trips with an unknown zone vanish from the fact table. That is a business decision hiding in a join type; a test or a comment should say so.

The mart aggregates the fact for one question, monthly revenue by zone:

```sql
select
    pickup_zone as revenue_zone,
    {{ dbt.date_trunc("month", "pickup_datetime") }} as revenue_month,
    service_type,
    sum(total_amount) as revenue_monthly_total_amount,
    count(tripid) as total_monthly_trips,
    avg(trip_distance) as avg_monthly_trip_distance
from {{ ref('fact_trips') }}
group by 1, 2, 3
```

---

## Tests and documentation

Tests live beside the docs in `schema.yml`:

```yaml
models:
  - name: stg_green_tripdata
    columns:
      - name: tripid
        tests:
          - unique:   {severity: warn}
          - not_null: {severity: warn}
      - name: pickup_locationid
        tests:
          - relationships:
              to: ref('taxi_zone_lookup')
              field: locationid
              severity: warn
      - name: payment_type
        tests:
          - accepted_values:
              values: "{{ var('payment_type_values') }}"
              severity: warn
              quote: false
```

| Test | Catches |
|---|---|
| `unique` | Dedupe failed; the surrogate key collides |
| `not_null` | A required field arrived empty |
| `relationships` | A foreign key with no parent (unknown zone ID) |
| `accepted_values` | A new code the business logic doesn't know |

Every test in the course is `severity: warn`, so a failure never stops the build. That's fine for a homework dataset with known dirt. In production, decide per test: keys `error`, descriptive columns `warn`. A test that only warns is a test nobody reads.

The `sources:` block also has a commented-out `freshness:` with `error_after: {count: 6, period: hour}` and `loaded_at_field`. Uncomment it and `dbt source freshness` becomes your first ingest monitor ([05](05-monitor.md)).

---

## The command set

| Command | Does |
|---|---|
| `dbt deps` | Install packages |
| `dbt seed` | Load CSVs in `seeds/` as tables (`taxi_zone_lookup`) |
| `dbt run` | Build models |
| `dbt test` | Run tests |
| `dbt build` | Seed + run + test + snapshot, in DAG order; a failing test stops its downstream models |
| `dbt build --select +fact_trips` | `fact_trips` and everything upstream of it |
| `dbt docs generate && dbt docs serve` | Catalogue and lineage graph site |

`dbt build` is the one to schedule: it won't build `fact_trips` on top of a staging model whose `error`-severity tests failed.

---

## Deployment

DE 04 shows two paths:

| Path | Setup | Scheduling |
|---|---|---|
| dbt Cloud | `dbt_cloud_setup.md`: connect BigQuery with a service-account key, link the repo | dbt Cloud jobs, `dbt build` on a cron, with a production environment and target dataset |
| dbt Core locally (Postgres in the course) | `docker_setup/` (Dockerfile + compose) or `pip install dbt-bigquery` / `dbt-postgres`, plus `~/.dbt/profiles.yml` | Your orchestrator runs `dbt build` as a task ([03](03-orchestrate.md)) |

The module ends by charting `dm_monthly_zone_revenue` in Google Data Studio (now Looker Studio) or Metabase. A dashboard on a mart, never on a staging view, is the rule that keeps metric logic in one place, which is the "two dashboards show different numbers" scenario in [07](07-data-architectures-mesh-fabric-mdw.md).

---

## Run labels

| Material | Needs |
|---|---|
| `taxi_rides_ny/` on BigQuery | `dbt-bigquery` + a GCP account with the week-3 tables loaded |
| `taxi_rides_ny/` on Postgres | `dbt-postgres` + the DE 01 Postgres container with green/yellow data |
| `docker_setup/` | Docker |
| dbt Cloud path | A dbt Cloud account (free developer tier) + GCP |

---

→ Next: [03-orchestrate.md](03-orchestrate.md) — `dbt build` is one task; orchestration decides when it runs, what runs before it, and what happens when it fails.
