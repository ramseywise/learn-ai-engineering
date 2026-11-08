---
origin: synthesis  # split from 03-catalog-semantic-layer-and-contracts.md (2026-11-08) so each part stays under the chapter length cap
sources:
  - https://raw.githubusercontent.com/datahub-project/datahub/master/docs/managed-datahub/observe/data-contract.md
  - https://docs.open-metadata.org/v2.0.x/how-to-guides/guide-for-data-users/follow-data-asset.md
  - https://docs.open-metadata.org/v2.0.x/how-to-guides/data-quality-observability/alerts-notifications/notify-downstream.md
  - https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/docs/support-communication-channels.md
  - https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/schema/odcs-json-schema-latest.json
  - https://dataproducts.substack.com/p/the-rise-of-data-contracts
  - https://arxiv.org/abs/2304.01062 (Goedegebuure et al., ACM Computing Surveys 2024, arXiv v3 author's version, full; online appendix not read)
confidence: medium
cleaned: 2026-11-03
---
# Data contracts: who a change reaches

> Part two of two. [03](03-catalog-semantic-layer-and-contracts.md) built the catalog and the semantic layer, and its `chapter.py` script. This part continues that same script: it adds the people (who a contract answers to, how consumers are found) and sends the fare change through the whole chain. Run 03 first; the code below uses its `m`, `sh`, `curated`, `tables` and `rebuild`.

## Who a contract answers to

[The contracts chapter](../../02-ingest-and-modelling/notes/04-data-contracts.md) teaches how to write and enforce one. Its organisational job is different: it fixes who may change what, and who has to be told. Sources agree on the first half and divide on who writes it. [DataHub's contracts](https://raw.githubusercontent.com/datahub-project/datahub/master/docs/managed-datahub/observe/data-contract.md) are "owned by the producer", one per asset, and exclude documentation, ownership and tags as things a contract verifies, which is a clean line between contract and catalog. [Sanderson](https://dataproducts.substack.com/p/the-rise-of-data-contracts) has producers own each contract while "data consumers define the schema and properties they NEED". These can coexist: consumers request and producers own. In [Dehghani's mesh](https://martinfowler.com/articles/data-mesh-principles.html), the domain data product owner "must have a deep understanding of who the data users are".

So how does the owner know? Not from the standard. I searched [ODCS](https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/schema/odcs-json-schema-latest.json) v3.2.0's schema and docs for consumer, subscribe and downstream, and found no field that records who consumes a dataset. [Its support section](https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/docs/support-communication-channels.md) lists channels consumers can use, and the closest thing is an optional invitation URL. That is my reading of a search, not a statement in the standard. Three other sources fill the gap, each with a hole:

| Source | How you learn the consumer | What it misses |
|---|---|---|
| Registration | They declare it, as a [dbt exposure](../../05-quality-and-observability/notes/06-dataops.md#one-definition-per-metric) or [a follow](https://docs.open-metadata.org/v2.0.x/how-to-guides/guide-for-data-users/follow-data-asset.md) | Everyone who didn't bother |
| Lineage | Derived from pipelines, as in [OpenLineage](../../05-quality-and-observability/notes/02-monitors-and-lineage.md) or [OpenMetadata's downstream alerts](https://docs.open-metadata.org/v2.0.x/how-to-guides/data-quality-observability/alerts-notifications/notify-downstream.md) | Notebooks and exports outside any pipeline |
| Query log | Observed in the warehouse | Anyone who hasn't read within the log's retention, and a shared service account tells you nothing about who |

Goods notes the lineage route, where provenance lets a producer "quickly notify those affected by the problem". The grey-literature review by [Goedegebuure et al.](https://arxiv.org/abs/2304.01062) (ACM Computing Surveys, 2024; author's version read) reports a central catalog as the common proposal in its sources, and Dehghani as not recommending one run by a separate team, since each data product decides what to publish about itself. I read that as the federated version of [the catalog in the mesh chapter](01b-data-mesh-topologies-and-scenarios.md), a term the review doesn't use, and it still needs one index to search: the review's own runtime architecture keeps a registry and discovery service. Here is the chain, using all three sources.

```python
(m / "exposures.yml").write_text("""
exposures:
  - name: finance_weekly_close
    type: dashboard
    owner: {name: Finance data, email: finance-data@example.com}
    depends_on: ["metric('revenue')"]
  - name: ops_cancellations
    type: dashboard
    owner: {name: Ops analytics, email: ops@example.com}
    depends_on: ["metric('cancel_rate')"]
  - name: pricing_features
    type: ml
    owner: {name: Pricing ML, email: pricing@example.com}
    depends_on: ["ref('fct_trips')"]
""")
assert sh("dbt", "parse", "-q")[0] == 0

v1 = {"fare_usd": {"type": "DOUBLE", "unit": "USD"}, "is_cancelled": {"type": "INT", "unit": None}}
v2 = {"fare_cents": {"type": "BIGINT", "unit": "US cents"}, "is_cancelled": {"type": "INT", "unit": None}}

def breaking(old, new):
    """The structural diff from the contracts chapter, plus the unit."""
    return [c for c, spec in old.items() if new.get(c) != spec]

def manifests():
    return (json.loads((ROOT / "target/semantic_manifest.json").read_text()),
            json.loads((ROOT / "target/manifest.json").read_text()))

def metrics_on(column, sem):
    """Every metric that reads a column, following ratios and derived metrics up."""
    hit = {x["name"] for x in sem["metrics"] if re.search(rf"\b{column}\b", x["type_params"].get("expr") or "")}
    grew = True
    while grew:
        grew = False
        for x in sem["metrics"]:
            tp = x["type_params"]
            inputs = [i["name"] for i in [tp.get("numerator"), tp.get("denominator"), *(tp.get("metrics") or [])] if i]
            if x["name"] not in hit and hit & set(inputs):
                hit.add(x["name"]); grew = True
    return sorted(hit)

def impact(table, column, query_log):
    sem, man = manifests()
    metrics = metrics_on(column, sem)
    named, broad = [], []
    for e in man["exposures"].values():
        deps = e["depends_on"]["nodes"]
        via = [d.split(".")[-1] for d in deps if d.startswith("metric.") and d.split(".")[-1] in metrics]
        if via:
            named.append((e["name"], e["owner"]["email"], "metric " + via[0]))
        elif f"model.rides.{table}" in deps:
            broad.append((e["name"], e["owner"]["email"], "whole table: ask which columns"))
    seen = {e["name"] for e in man["exposures"].values()}
    shadow = sorted({who for who, sql in query_log if re.search(rf"\b{column}\b", sql) and who not in seen})
    return metrics, named, broad, shadow

warehouse_log = [("finance_weekly_close", "select revenue from semantic_layer"),
                 ("nb_fare_audit", "select city, avg(fare_usd) from fct_trips group by 1"),
                 ("nb_fare_audit", "select fare_usd from fct_trips where fare_usd > 50"),
                 ("growth_extract", "select rider_id, trip_date from fct_trips")]

for col in breaking(v1, v2):
    metrics, named, broad, shadow = impact("fct_trips", col, warehouse_log)
    print("breaking column:", col)
    print("  catalog: term", curated[("raw_trips", col)]["term"], "| steward", curated[("raw_trips", col)]["steward"], "| tier", tables["raw_trips"]["tier"])
    print("  metrics:", metrics)
    for row in named + broad:
        print("  must hear:", *row, sep="  ")
    print("  in the query log, registered nowhere:", shadow)
```

```text
breaking column: fare_usd
  catalog: term Net fare | steward finance-data@ | tier 1
  metrics: ['revenue', 'revenue_per_trip']
  must hear:  finance_weekly_close  finance-data@example.com  metric revenue
  must hear:  pricing_features  pricing@example.com  whole table: ask which columns
  in the query log, registered nowhere: ['nb_fare_audit']
```

The chain gives a decision and not just a list. `ops_cancellations` isn't on it, even though it reads the same table, because `cancel_rate` doesn't touch the fare. That precision comes from registering through a metric. `pricing_features` registered against the whole table, so all we know is to ask them. `nb_fare_audit` appears only because we looked at the log, and the code's plain name match would be fooled by a second table with a `fare_usd` column.

It also separates two owners. The **contract owner** (mobility) decides when a column may change. The **metric owner** (finance) decides what `revenue` means, and owns the one line that has to move. A consumer registered with a metric hears from the metric owner, who can absorb the change, so it never hits them at all.

I found no controlled or before-and-after measurement showing that contracts reduce incidents, in the posts, docs and papers I read. The Sanderson and Freeman and the Jones books weren't read, so they may hold case evidence. Figures of that kind that surfaced in search snippets had no named source or method, and they aren't repeated here. The case for contracts in this chapter is mechanical, which the next section shows.

## Sending the change through

Now make the change, two ways, and see what each layer notices.

```python
def rebuild(label, select):
    (m / "fct_trips.sql").write_text(select)
    sh("dbt", "run", "-q", "--select", "fct_trips")
    valid = "pass" if sh("mf", "validate-configs")[0] == 0 else "FAIL"
    code, out = sh("mf", "query", "--metrics", "revenue_per_trip")
    print(f"{label:24} validate {valid}   revenue_per_trip {out.splitlines()[-1].strip() if code == 0 else 'query error'}")
    return out

BASE = "select trip_id, rider_id, trip_date, city, {fare}, is_cancelled from raw_trips"
rebuild("today", BASE.format(fare="fare_usd"))
err = rebuild("renamed to fare_cents", BASE.format(fare="fare_usd * 100 as fare_cents"))
print("  ", next(l.strip() for l in err.splitlines() if "fare_usd" in l)[:90])
rebuild("same name, now in cents", BASE.format(fare="fare_usd * 100 as fare_usd"))
print("rows above the contract's limit of 500:", q("select count(*) from fct_trips where fare_usd > 500")[0][0])

(m / "semantic.yml").write_text(SEMANTIC.replace("expr: fare_usd", "expr: fare_cents / 100.0"))
sh("dbt", "parse", "-q")
rebuild("renamed, metric updated", BASE.format(fare="fare_usd * 100 as fare_cents"))
```

```text
today                    validate pass   revenue_per_trip 30.8594
renamed to fare_cents    validate FAIL   revenue_per_trip query error
   Binder Error: Referenced column "fare_usd" not found in FROM clause!
same name, now in cents  validate pass   revenue_per_trip 3085.94
rows above the contract's limit of 500: 2486
renamed, metric updated  validate pass   revenue_per_trip 30.8594
```

The rename is the good failure: `mf validate-configs` queries the warehouse and fails in CI, naming the column. The same multiplication under the old name is the one to fear. Types match, `mf validate-configs` passes, and revenue per trip is a hundred times too big. Only a value rule catches it. The [contracts chapter's](../../02-ingest-and-modelling/notes/04-data-contracts.md) range rule flags 2,486 rows here, and only because the cheapest fare is $6, which becomes 600 against its limit of 500. A fare of $5 or less would pass, which is why that chapter also checks the median. A unit lives in a contract as text; enforcing it takes a value rule. So a unit change should always get a new column name, which turns the silent failure into a loud one.

The last line is the payoff for defining metrics once. One `expr` changes, in one file, and every consumer of `revenue` and `revenue_per_trip` gets the same number as before with no change of their own. The notebook still breaks, which is why it's on the list. For the sequence that keeps both columns live while readers move, use [expand and contract](../../05-quality-and-observability/notes/04-schema-and-data-migrations.md).


## Pitfalls

- **Registration as the only record of consumers.** Symptom: a "safe" change breaks a notebook nobody listed. Compare the log with the registry regularly, and chase the difference.
- **Treating a green build as a safe change.** Symptom: revenue is a hundred times too big, with every check passing. New unit, new name, plus a range rule.

## Try it

These start from the definitions before the change, so restore them first: `(m / "semantic.yml").write_text(SEMANTIC)`, then `rebuild("restored", BASE.format(fare="fare_usd"))` and `sh("dbt", "parse", "-q")`.

1. Add a derived metric `revenue_k` with `expr: revenue / 1000` and `input_metrics: [{name: revenue}]`, parse, and rerun `impact`. Does it appear for `fare_usd`? What if a metric's `expr` were `fare_usd + tip_usd`?
2. `metrics_on` matches column names only. Add a `fare_usd` column to `fct_wallet_daily`, with a metric on it. What goes wrong, and which field in `target/semantic_manifest.json` fixes it?

<details>
<summary>Answers</summary>

1. Yes for a metric whose inputs include `revenue`, since `metrics_on` walks numerators, denominators and derived inputs until nothing new appears. The `expr` also matches, because the search is a word match within the expression, so `fare_usd + tip_usd` is found for either column. A column renamed inside the model's SQL is missed, because the manifest sees the model's output and not its lineage.
2. `metrics_on("fare_usd")` returns that wallet metric, and the change appears to break finance's wallet numbers too, so people get alerted for nothing. Each simple metric's `metric_aggregation_params.semantic_model` names its model, so filter on that.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| Data contract or dbt model contract? | A data contract is a cross-team promise including meaning and owner. A dbt model contract is a build check on a model's columns and types. |
| How do you know who a contract's consumers are? | Registration, lineage and the query log, compared with each other. ODCS v3.2.0 has no field for it, on my search of it. |
| Who owns what in a fare change? | The contract owner decides when the column changes. The metric owner decides what revenue means and moves the one line. |
| Rename or unit change: which is worse? | The unit change under the same name. Everything passes and the number is wrong. Give a new unit a new name. |
| Do contracts reduce incidents? | I found no controlled measurement in what I read. Don't quote a percentage without a named source and method. |

## Next

That closes the data-engineering subject's path from file to platform: storage, ingest, transform, warehouse, quality, ML platform, and the organisation that owns them. Read [the mesh chapter](01b-data-mesh-topologies-and-scenarios.md) again with these three chapters in mind, since federated governance only works if access rules, erasure and a catalog can be enforced by machine. The [pillar README](../README.md) has the deck and the rules of thumb. From here, the [metric trees chapter](../../../data-analytics/06-applied-analyses/notes/11-metric-trees.md) is the analyst's side of the same definitions, and the [data-analysis agent](../../../generative-ai/07-agentic-applications/notes/05-data-analysis-agent.md) shows what happens when a model has to use them.
