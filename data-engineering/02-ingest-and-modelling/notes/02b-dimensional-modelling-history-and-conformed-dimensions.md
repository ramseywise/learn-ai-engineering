---
origin: book-condensed  # split from 02-dimensional-modelling.md (2026-11-08) so each part stays under the chapter length cap
sources:
  - "Kimball and Ross, The Data Warehouse Toolkit, 2nd ed. (Wiley, 2002), ch. 2 to 15"
  - https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/
  - "Kleppmann, Designing Data-Intensive Applications (O'Reilly, 2017), ch. 3"
  - https://docs.getdbt.com/docs/build/snapshots
confidence: high
cleaned: 2026-11-01
---
# 2b — Dimensional modelling: history, shapes and conformed dimensions

> Part two of two. [Part one](02-dimensional-modelling.md) covered the grain, the four design decisions and what can be added up. This part continues its `fact_trips` and `dim_zone` script (run it first): slowly changing dimensions, the shapes that keep a dimension manageable, conformed dimensions and drilling across, and when the star is the wrong tool.

## History: slowly changing dimensions

Dimensions do change. In Kimball's example, a product called IntelliKidz 1.0 moves from Education to Strategy on January 15th (ch. 4; the Kimball Group keeps a [summary of the techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) online). The question is what happens to last quarter's Education numbers, and only the business can answer it. The modeller's job is to make the answer a deliberate choice for each attribute. Kimball named the three responses in 1994, and the type numbers have stuck.

Our version: the city redraws a boundary, and zone 6 moves from Queens to Brooklyn on January 15th.

**Type 1, overwrite.** Update the row. It takes one line and keeps no history.

```python
con.execute("CREATE TABLE dim_zone_t1 AS SELECT * FROM dim_zone")
before = con.execute("""SELECT round(sum(fare_usd)) FROM fact_trips f JOIN dim_zone_t1 z USING (zone_key)
    WHERE z.borough = 'Brooklyn'""").fetchall()[0][0]
con.execute("UPDATE dim_zone_t1 SET borough = 'Brooklyn' WHERE zone_id = 6")  # the city redraws a boundary
after = con.execute("""SELECT round(sum(fare_usd)) FROM fact_trips f JOIN dim_zone_t1 z USING (zone_key)
    WHERE z.borough = 'Brooklyn'""").fetchall()[0][0]
print("Brooklyn fares for January, as reported before:", before)
print("Brooklyn fares for January, as reported after: ", after)
```

```text
Brooklyn fares for January, as reported before: 2382840.0
Brooklyn fares for January, as reported after:  2710631.0
```

January's Brooklyn revenue changed by about 328,000 dollars, for days already reported and possibly already invoiced, with no record that anything happened. Type 1 is correct for corrections, such as fixing a misspelled zone name, where the old value was simply wrong. It is wrong for anything people compare over time, and anything built on top, such as an aggregate table, now needs rebuilding.

**Type 2, add a row.** Keep the old row, close it, and open a new one with a new surrogate key. This is the point of surrogate keys, since one natural key now has several rows. Kimball detects a change by comparing a row hash (he calls it a CRC), which spares comparing each column one at a time across, say, 100 attributes and millions of rows (ch. 4). Two cautions from the same chapter: count products on the natural key, not the surrogate, or each version is counted again; and do not constrain on a dimension row's effective date to partition facts, because versions can overlap and give the wrong answer. Type 2 on a dimension that already exceeds about a million rows is the case that leads to the next section (ch. 4).

```python
con.execute("CREATE SEQUENCE zone_v_sk START 1")
con.execute("""
CREATE TABLE dim_zone_v (zone_key BIGINT, zone_id INT, zone_name VARCHAR, borough VARCHAR,
                         row_hash UBIGINT, valid_from DATE, valid_to DATE, is_current BOOLEAN)""")

def apply_scd2(source_sql, load_date):
    """Close the current row of any changed zone, then open a new one. Rerunning changes nothing."""
    con.execute(f"""CREATE OR REPLACE TEMP TABLE incoming AS
        SELECT *, hash(zone_name, borough) AS row_hash FROM ({source_sql})""")
    con.execute("""UPDATE dim_zone_v d SET valid_to = ?, is_current = false
        FROM incoming i
        WHERE d.zone_id = i.zone_id AND d.is_current AND d.row_hash <> i.row_hash""", [load_date])
    con.execute("""INSERT INTO dim_zone_v
        SELECT nextval('zone_v_sk'), i.zone_id, i.zone_name, i.borough, i.row_hash,
               ?::DATE, DATE '9999-12-31', true
        FROM incoming i
        LEFT JOIN dim_zone_v d ON d.zone_id = i.zone_id AND d.is_current
        WHERE d.zone_id IS NULL""", [load_date])

apply_scd2("SELECT * FROM src_zones", "2025-01-01")
changed = """SELECT zone_id, zone_name, CASE WHEN zone_id = 6 THEN 'Brooklyn' ELSE borough END AS borough FROM src_zones"""
apply_scd2(changed, "2026-01-15")
apply_scd2(changed, "2026-01-15")     # a retry
print(con.sql("SELECT zone_key, zone_id, borough, valid_from, valid_to, is_current FROM dim_zone_v WHERE zone_id = 6 ORDER BY 1"))
print("rows in dimension:", con.execute("SELECT count(*) FROM dim_zone_v").fetchall()[0][0])
```

```text
┌──────────┬─────────┬──────────┬────────────┬────────────┬────────────┐
│ zone_key │ zone_id │ borough  │ valid_from │  valid_to  │ is_current │
│  int64   │  int32  │ varchar  │    date    │    date    │  boolean   │
├──────────┼─────────┼──────────┼────────────┼────────────┼────────────┤
│        6 │       6 │ Queens   │ 2025-01-01 │ 2026-01-15 │ false      │
│      251 │       6 │ Brooklyn │ 2026-01-15 │ 9999-12-31 │ true       │
└──────────┴─────────┴──────────┴────────────┴────────────┴────────────┘

rows in dimension: 251
```

Three properties of that output matter. The dimension grew by exactly one row, 250 zones became 251 rows, because attributes that did not change do not create history. The retry changed nothing, because a re-run finds a matching hash and no missing row. A pipeline that retries, and all of them do, needs this property; [idempotency and backfills](../../03-transform-and-orchestrate/notes/04-idempotency-and-backfills.md) generalizes it. And the two validity dates form an unbroken chain with no overlap, which is what lets the next step look up the right row.

Facts now take their key from the dimension row that was current when the event happened. Nothing else in the design needs to know.

```python
con.execute("""
CREATE TABLE fact_trips_v AS
SELECT t.trip_id, CAST(strftime(t.pickup_at, '%Y%m%d') AS INT) AS date_key,
       coalesce(z.zone_key, -1) AS zone_key, t.fare_usd
FROM src_trips t
LEFT JOIN dim_zone_v z ON t.zone_id = z.zone_id
     AND t.pickup_at::DATE >= z.valid_from AND t.pickup_at::DATE < z.valid_to""")
print("zone 6, grouped by the borough at the time of the trip")
print(con.sql("""SELECT z.borough, count(*) AS trips, min(f.date_key) AS first_day, max(f.date_key) AS last_day
    FROM fact_trips_v f JOIN dim_zone_v z USING (zone_key) WHERE z.zone_id = 6 GROUP BY 1 ORDER BY 3"""))
print("zone 6, restated to today's borough through the natural key")
print(con.sql("""SELECT cur.borough, count(*) AS trips
    FROM fact_trips_v f JOIN dim_zone_v z USING (zone_key)
    JOIN dim_zone_v cur ON cur.zone_id = z.zone_id AND cur.is_current
    WHERE z.zone_id = 6 GROUP BY 1"""))
```

```text
zone 6, grouped by the borough at the time of the trip
┌──────────┬───────┬───────────┬──────────┐
│ borough  │ trips │ first_day │ last_day │
│ varchar  │ int64 │   int32   │  int32   │
├──────────┼───────┼───────────┼──────────┤
│ Queens   │ 13251 │  20260101 │ 20260114 │
│ Brooklyn │ 15998 │  20260115 │ 20260131 │
└──────────┴───────┴───────────┴──────────┘

zone 6, restated to today's borough through the natural key
┌──────────┬───────┐
│ borough  │ trips │
│ varchar  │ int64 │
├──────────┼───────┤
│ Brooklyn │ 29249 │
└──────────┴───────┘
```

Both questions are now answerable. Grouped through the fact's own key, you get history as it was: 13,251 trips counted in Queens up to the 14th and 15,998 in Brooklyn from the 15th. Joined back through the natural key to the current row, you get history restated to today's map, all 29,249 in Brooklyn. Kimball's warning here matters for query writers: facts already carry the right key, so do not constrain them with the effective dates in ordinary queries. The dates exist for load logic and as-of lookups of the dimension itself.

That range join is also the answer to **late-arriving facts**. A trip dated January 10th that lands on January 20th looks up by its event date, finds zone key 6, and reports under Queens as it should. The only remaining work is inserting it into the right partition (ch. 13). If it would change a period finance already closed, you need a policy, and Kimball describes keeping two date keys, the event date and the booking date, so that both views tie out. **Late-arriving dimension rows** are the harder case. You learn on the 20th that the change took effect on the 10th, so you insert a row with a new key, fix the dates, and repoint the fact rows in that interval. It is messy and Kimball says so. Surrogate keys in a fact are not ordered by time, so do not rely on their order.

**Type 3, add a column.** Store `prior_borough` beside `borough`. It supports one "before and after" view and is rarely used (ch. 4). Use it for one planned reorganization, when the business wants to compare old and new side by side for a while.

| Type | Mechanism | History | Fact table impact | Use for |
|---|---|---|---|---|
| 1 | Overwrite | Gone | None, but past reports change | Corrections |
| 2 | New row and new key | Full | New facts get new keys; old facts untouched | Anything compared over time |
| 3 | New column | One step | None | A single planned before and after |

The trade-offs in row growth are real. Kimball warns about Type 2 on a rapidly changing attribute, since a dimension of millions of customers with one volatile column can grow past the point where it is a dimension. Split the volatile columns into their own dimension. In dbt you do not write `apply_scd2` by hand: a [snapshot](https://docs.getdbt.com/docs/build/snapshots) generates it, with `dbt_valid_from` and `dbt_valid_to` in place of our two columns. It is still worth writing once, so that when a snapshot does something surprising you know what it is doing.

Streaming has the same problem under another name. Kleppmann's example is applying a tax rate to a past sale: if you join to the rate as it is now, a rerun gives a different answer, so the join is not deterministic (pp. 475-476). His fix is the Type 2 idea, giving each version of the rate an identifier and referring to it from the sale. He also names the cost that a warehouse rarely feels and a log does, which is that with every version needed forever, log compaction cannot throw any of them away (p. 476). That is the same row growth as above, and the reason streaming pipelines tend to prefer a versioned dimension table to an endless changelog.

Two Kimball cases show where Type 2 is the right default. Employee profile changes (promotions, transfers) are kept as Type 2 rows in the employee dimension, each with an effective and an expiration date-time and a most-recent flag, and the current row's expiration is a far-future date, not null. At 100,000 employees, 10 changes a year, 2,000-byte rows and 5 years, that is only 10 GB of raw data, so the dimension is not a factless fact table in disguise (ch. 8). Budgets are better stored as changes than as monthly status: an original $200,000 line, a $40,000 increase in June and a $25,000 cut in October are three rows, and summing every row to date gives the current $215,000 without duplicating unchanged lines. A snapshot grain would be semi-additive (ch. 7).

## Shapes that keep a dimension manageable

Three devices answer "the dimension is too big, too fast-changing or too awkward".

**Minidimension.** Move a customer's volatile attributes (banded income, age band, credit score band) into a small separate dimension and put its key in the fact table beside the customer key. The fact row records the profile in force at event time, so the customer row stays unversioned. Banding is required, because raw values would make the minidimension as large as the customer dimension, and it is the compromise Kimball calls the most significant. Five attributes of ten values each give 100,000 rows, which he treats as a reasonable upper limit. If the demographics key instead sits in the customer row it is an outrigger, and that key must be Type 1 or the monster dimension returns (ch. 6). Type 2 stays the default for customer dimensions under about 100,000 rows (ch. 6).

**Junk dimension.** Ten two-value flags on a fact become one dimension of at most 1,024 rows (2^10) and one key. Five three-valued flags give 243, so combine them. Five 100-valued flags give 100 million combinations, so keep those apart (ch. 5).

**Role-playing dates and bridges.** An order has an order date, a requested ship date and more. Keep one date table and expose it through one view per role (`order_date`, `req_ship_date`), each with its own key in the fact (ch. 2, ch. 5). A ragged customer hierarchy cannot be followed by `GROUP BY` through a parent pointer, so Kimball adds a bridge table of every parent and descendant pair; his eight-customer, four-level example needs 22 rows (1+4+9+8). It stays standard SQL, at the price of a table several times the dimension's size (ch. 6). An employee's skills are either a skills-group outrigger, which needs `UNION` or `INTERSECT` for Unix and Linux together, or a delimited string such as `\Unix\C++\` searched with `LIKE`, which answers AND and OR in one `SELECT` but cannot use an ordinary index (ch. 8). A multivalued dimension such as a bill's diagnoses gets a group key and a bridge with a weighting factor per member, and the weights in a group sum to exactly 1.00; without them each fact is counted once per member, an "impact report" (ch. 13).

Each bridge row holds a parent key, a subsidiary key, the levels between them, and bottom and top flags, plus a zero-length row from each parent to itself. Filter `levels = 1` for direct subsidiaries. Constrain the dimension to one parent before joining the bridge to the fact, or revenue is counted once per path (ch. 6):

```sql
SELECT c.customer_name, SUM(f.revenue)
FROM customer c
JOIN bridge b ON c.customer_key = b.parent_key
JOIN fact f   ON b.subsidiary_key = f.customer_key
WHERE c.customer_name = 'ABC General International' AND f.month = '2002-01'
GROUP BY c.customer_name;

-- many parents: take subsidiary keys DISTINCT, or shared ones double count
SELECT SUM(f.revenue) FROM fact f
WHERE f.month = '2002-01' AND f.customer_key IN (
  SELECT DISTINCT b.subsidiary_key FROM customer c
  JOIN bridge b ON c.customer_key = b.parent_key WHERE c.customer_city = 'San Francisco');
```


**Factless facts.** An event with nothing to measure is still a fact row. A registration table at grain one row per registered course, student and term holds only keys, and counting any key gives the same answer, so add an always-1 count column to keep the SQL readable (ch. 12). What did not happen needs a **coverage table** with a row for every possible combination, such as every promoted product in a store and week. Subtract the sales fact and the set difference is promoted-but-unsold, far smaller than padding the sales fact with zero rows (ch. 12).

**Superdimension and degenerate key.** Small dimensions that always travel together merge into one. An airline's class purchased, class flown and upgrade flag are three rows each, so their cross product is a nine-row table and one key, not three (ch. 11). The opposite error is a bill-number dimension with nearly as many rows as the fact: make it a degenerate dimension on the fact row, and set the grain at one row per service line per bill, since each line has its own metrics (ch. 10). Kimball also gives the sanity check that a model usually has 5 to 15 dimensions, with fewer suggesting omissions and 25 to 30 needing junk or centipede fixes (ch. 9, ch. 10).

**Clickstream grain.** Start with one row per web session, 13 four-byte fields (52 bytes), and in Kimball's hypothetical site 5 million sessions a day add about 260 MB. Keep a page-event table beneath it for the 20 million meaningful events (60 bytes, about 1.2 GB a day) and join it by a degenerate session ID (ch. 14).

**Written against earned.** A $600 annual policy earns $50 a month, but is written as $600 in January and 0 in February, so a pay-in-advance insurer needs a transaction fact and a monthly snapshot together; earned premium comes from the revenue-recognition system, not from summing transactions (ch. 15).

**Heterogeneous products.** A bank sells checking, mortgages and cards with different attributes. Keep a core fact and product dimension with only the shared measures and attributes, and add a custom fact and a custom product dimension per line of business. The custom dimensions are row subsets of the core one and reuse its surrogate keys, so core reports never lose a product (ch. 9). Insurance repeats it per line of business, with separate snapshot tables so one is not full of nulls (ch. 15).

Two further rules of thumb. Put unit-of-measure conversion factors on the fact row, not in the product dimension: in his order pipeline, 10 quantities and 4 factors make 14 facts per row, against 50 if each quantity were stored in all five units (ch. 5). And normalising facts into one amount column plus a fact-type dimension turns a 10-million-row order fact into 40 million, which he accepts only for sparse facts with no arithmetic between them (ch. 5).

## Conformed dimensions and drilling across

One star is a report, while an enterprise warehouse is many stars that can be compared. Kimball's answer is the **bus architecture** (ch. 3): dimensions are built once and shared, so `dim_zone` means the same in trips, in driver shifts and in vehicle inspections. Planning happens on a **bus matrix**, business processes down the side and dimensions across the top, with a tick where a process uses a dimension. His retail example has rows such as Retail Sales, Retail Inventory and Purchase Orders against columns such as Date, Product, Store and Vendor. A single page makes the integration plan visible before anyone writes a pipeline. Kimball calls the matrix part design tool, part project-management tool and part communication tool, with rows that follow source systems and not departments. Build single-source marts first and consolidated ones (profitability is his example) later, since ETL effort grows with every source. He puts conformed dimensions at about 90 percent of the up-front data-architecture effort. Where a fact cannot be conformed exactly, name the variants differently, and where units differ carry the fact in both units (ch. 3).

| Process | Date | Zone | Payment | Vehicle | Driver |
|---|---|---|---|---|---|
| Trips | x | x | x | x | x |
| Driver shifts | x | x | | | x |
| Vehicle inspections | x | | | x | |

Conformed dimensions give you a safe way to combine facts, and a tempting wrong way sits right next to it. Add a shifts fact at one row per zone, day and shift, then ask for fares and drivers by zone.

```python
con.execute("""
CREATE TABLE fact_shifts AS
SELECT d.date_key, z.zone_key, (1 + (hash(d.date_key, z.zone_key) % 40))::INT AS drivers_on_shift, s.shift
FROM dim_date d CROSS JOIN dim_zone z CROSS JOIN (VALUES ('day'), ('night')) s(shift)
WHERE d.year = 2026 AND d.month = 1 AND z.zone_key > 0""")

wrong = con.execute("""SELECT round(sum(f.fare_usd)), sum(s.drivers_on_shift)
    FROM fact_trips f JOIN fact_shifts s USING (date_key, zone_key)""").fetchall()[0]
right = con.execute("""
WITH t AS (SELECT zone_key, sum(fare_usd) AS fares FROM fact_trips WHERE zone_key > 0 GROUP BY 1),
     s AS (SELECT zone_key, sum(drivers_on_shift) AS drivers FROM fact_shifts GROUP BY 1)
SELECT round(sum(t.fares)), sum(s.drivers) FROM t JOIN s USING (zone_key)""").fetchall()[0]
print("fact joined to fact:", wrong)
print("drill across:       ", right)
print("true:               ", con.execute("SELECT round(sum(fare_usd)) FROM fact_trips WHERE zone_key > 0").fetchall()[0][0],
      con.execute("SELECT sum(drivers_on_shift) FROM fact_shifts").fetchall()[0][0])
```

```text
fact joined to fact: (22466405.0, 42499888)
drill across:        (11233203.0, 314322)
true:                11233203.0 314322
```

Joining fact to fact doubled the fares, because each day and zone has two shifts, and it inflated drivers by more than a hundred times, because each shift row repeated once per trip. Both errors are the fan-out from earlier, this time in both directions at once. **Drilling across** means aggregating each fact to the shared dimension first and then joining the results, and that returns the true totals exactly. A BI tool's semantic layer does the same for you, if the model tells it which facts and dimensions conform ([one running, with the fan-out it refuses](../../07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts.md#a-semantic-layer-compiles-the-question-at-its-grain)).

## When the star is the wrong tool

Stars are built for analytical questions, and some other uses do not fit them. They are slower to change than a raw layer, they take design effort before value, and they assume someone owns the conformed dimensions. When many source systems need to be integrated and audited, the next chapter's Data Vault separates integration from presentation. When a team has one consumer and a modern column store, the same chapter's One Big Table is often cheaper. Neither removes the need to know what a row means, so the grain sentence survives every alternative.

Two remarks from Kleppmann put the star in a wider frame. An event log and a fact table resemble each other, since both record immutable facts at a fine grain and derive everything else (p. 458). And once a read shape can be derived from a log, the question of whether to normalise or denormalise loses most of its force, because you can have both: normalised at the system of record, denormalised wherever it is read (p. 462). The [first chapter of this subject](../../01-storage-and-compute-foundations/notes/01-data-systems-and-data-models.md) sets out why normalisation exists at all. Dimensional modelling is the discipline of deciding what the derived shape should be.

## Pitfalls

- **Natural keys in the fact.** They look simpler until the first Type 2 change, when one id maps to several rows and each join fans out.
- **Type 1 by default.** An `UPDATE` on a dimension rewrites published history. Choose per attribute, and ask the people who read the reports.
- **Fact-to-fact joins.** Always drill across through conformed dimensions.
- **Modelling the org chart.** A "marketing mart" with copies of everything breeds exactly the two-numbers meeting this whole design exists to prevent.

## Try it

1. Run the trip of January 10th through the range join, as a late-arriving fact in zone 6. Which `zone_key` does it get, and which borough does it report under?
2. Add a Type 3 `prior_borough` column to a copy of `dim_zone` and write the query comparing January fares by old and new borough. Why is this cheaper than Type 2 for this question, and what can it not answer?

The full code for this chapter is in [`practice/02_dimensional_modelling.py`](../practice/02_dimensional_modelling.py).

<details>
<summary>Answers</summary>

1. It gets `zone_key` 6, the row valid from 2025-01-01 to 2026-01-15, and reports under Queens. The join compares the event date with the validity range and never looks at the load date. That is why the late fact needs no special case.
2. `ALTER TABLE` plus one `UPDATE`: `prior_borough` takes the old value on the changed row. The dimension does not grow, and each fact can be grouped by either column with no new keys. It cannot say which borough a given trip belonged to on its date, and it holds one prior value only, so a second move loses the first.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| SCD Types 1, 2, 3? | Overwrite and lose history; new row with new key and full history; new column with one prior value. Chosen per attribute. |
| Why does Type 2 need no change to fact queries? | The fact row holds the surrogate key of the version in force at event time, so a plain key join gives history as it was. |
| How do you restate Type 2 history to current values? | Join through the natural key to the row with `is_current`. |
| How do you load a late-arriving fact? | Look up the dimension by event date within the validity range, use that key, write into the correct partition. |
| What is a conformed dimension? | One dimension shared across facts with identical meaning, the basis for comparing processes. |
| How do you combine two facts? | Drill across: aggregate each to the shared dimensions separately, then join the results. |

## Next

[Data Vault and One Big Table](03-data-vault-and-obt.md) looks at the two alternatives to the star: one that puts more structure in the middle, and one that takes nearly all of it out.
