---
origin: synthesis  # split from 01-data-architectures-mesh-fabric-mdw.md (2026-11-08) so each part stays under the chapter length cap
sources:
  - James Serra, Deciphering Data Architectures (O'Reilly, 2024), ch. 13
  - "Strengholt, Data Mesh: Topologies and domain granularity, Towards Data Science (saved 2025)"
  # Data mesh scenario prompts handout, origin unknown, no public URL (linked from references.md)
  - https://martinfowler.com/articles/data-mesh-principles.html
confidence: medium
cleaned: 2026-11-02
---
# Data mesh: topologies and scenarios

> Part two of two. [01](01-data-architectures-mesh-fabric-mdw.md) covered the modern data warehouse, the data fabric, the lakehouse and derived data. Here: the four mesh principles, Serra's skepticism and his mesh types, Strengholt's six topologies, the scenario prompts mapped to mechanisms, and the chapter's rules, pitfalls and checklist. The taxi trips and tax rates of part one carry on as the running example.

## Data mesh: the four principles

In the architectures so far a central data team owns ingestion, modelling and serving for the whole company. That team usually doesn't know what the source fields mean, and as the company grows it becomes the queue everyone waits in. Zhamak Dehghani's [data mesh](https://martinfowler.com/articles/data-mesh-principles.html) decentralises that, using four principles. Serra lists four challenges the principles address (p. 172); pairing each with one principle, and the cell wording, is ours:

| Challenge with central ownership | Principle | What it means |
|---|---|---|
| Lack of ownership: the central team doesn't understand the source data | **1. Domain ownership** | The team closest to the data owns its operational and analytical data |
| Low quality: nobody downstream can fix upstream issues | **2. Data as a product** | Domains publish data that is discoverable, trustworthy, accessible, secure and understandable, and treat consumers as customers |
| Technical scaling: every domain rebuilds infrastructure | **3. Self-serve data platform** | A central platform team builds the tooling (storage, compute, pipelines, access control) that domains request through APIs or scripts |
| Organisational scaling: chaos without standards | **4. Federated computational governance** | Global rules (interoperability, quality, security, regulation, modelling) set jointly by domains and a central team, implemented and monitored in domains, automated where possible |

Two of the four are centralised. A mesh is not the absence of central teams: a platform team and a governance group still exist, as Serra's architecture diagram makes clear.

**Data product against data as a product:** Serra separates these. *Data as a product* is the idea: the owner treats the data as a complete product and not as a byproduct. A *data product* is the implementation: "a self-contained, independently deployable unit of data that delivers business value", built by one product team (pp. 173-174). Some exclude code, metadata and infrastructure from it, he notes. A **data contract** is the agreement a consumer reads from: format, schema, metadata, transformation information and access rules. [The contracts chapter](../../02-ingest-and-modelling/notes/04-data-contracts.md) treats producer and consumer in depth; here we care about what happens across many of them.

**Federated governance, run.** Serra's example of an inconsistency is one domain using full state names and another the two-letter abbreviation. This is that bug, built so you can watch it pass quietly.

```python
import duckdb, numpy as np, pyarrow as pa, pyarrow.parquet as pq, os

rng = np.random.default_rng(7)
n = 200_000
states = np.array(["CA", "NY", "WA"])
trip_state = rng.choice(states, n, p=[0.40, 0.45, 0.15])

# The trips domain publishes two-letter codes.
pq.write_table(pa.table({
    "trip_id": np.arange(n),
    "state": trip_state,
    "fare": rng.gamma(3.0, 6.0, n).round(2),
}), "trips.parquet")

# The finance domain keeps tax rates. Its CA row came from a
# different system, which spells the state out.
pq.write_table(pa.table({
    "state": ["California", "NY", "WA"],
    "tax_rate": [0.0725, 0.04, 0.065],
}), "tax_rates.parquet")

con = duckdb.connect()
print(con.sql("""
    SELECT round(sum(fare)) AS revenue, count(*) AS trips
    FROM 'trips.parquet'
""").fetchall()[0])
```

Output:

```text
(3605056.0, 200000)
```

```python
print(con.sql("""
    SELECT count(*) AS trips, round(sum(fare)) AS taxable_revenue,
           round(sum(fare * tax_rate)) AS tax_owed
    FROM 'trips.parquet' JOIN 'tax_rates.parquet' USING (state)
""").fetchall()[0])
print(con.sql("""
    SELECT state, count(*) AS trips
    FROM 'trips.parquet' t
    WHERE NOT EXISTS (SELECT 1 FROM 'tax_rates.parquet' r WHERE r.state = t.state)
    GROUP BY state
""").fetchall())
```

Output:

```text
(120003, 2163607.0, 99957.0)
[('CA', 79997)]
```

The join returned 120,003 rows out of 200,000 and a tax figure of 99,957 where the truth, shown below, is 204,462. There was no exception and no null. Each domain can also pass its own check, because each kept its own promise:

```python
from dataclasses import dataclass, field

@dataclass
class Contract:
    product: str
    domain: str
    owner: str                       # a team that answers, not a person
    path: str
    columns: dict                    # name -> DuckDB type
    freshness_hours: int
    description: str = ""
    reads: list = field(default_factory=list)   # upstream products

trips = Contract("trips", "mobility", "mobility-data@", "trips.parquet",
                 {"trip_id": "BIGINT", "state": "VARCHAR", "fare": "DOUBLE"},
                 freshness_hours=24, description="One row per completed trip.")
tax = Contract("tax_rates", "finance", "finance-data@", "tax_rates.parquet",
               {"state": "VARCHAR", "tax_rate": "DOUBLE"},
               freshness_hours=720, description="Sales tax rate per state.")

def check_schema(c):
    """The domain's own promise: the columns it said it would publish."""
    got = {r[0]: r[1] for r in con.sql(f"DESCRIBE SELECT * FROM '{c.path}'").fetchall()}
    return [f"{k}: want {v}, got {got.get(k)}"
            for k, v in c.columns.items() if got.get(k) != v]

print("trips schema:", check_schema(trips) or "ok")
print("tax schema:  ", check_schema(tax) or "ok")
```

Output:

```text
trips schema: ok
tax schema:   ok
```

A domain test can't catch this, as the fault lies between two products. The rule has to be global, and it has to run where no domain can skip it. Serra's wording is that the central group sets the standard and domains implement it, and that this should be automated whenever possible. Here the federated group has chosen [ISO 3166-2](https://en.wikipedia.org/wiki/ISO_3166-2:US) subdivision codes, in which California is `US-CA`, so both tables are non-conforming. That choice is ours, for this example; Serra names no particular standard.

```python
# Global rules: agreed by the federated group, run by the platform on every product.
GLOBAL_RULES = {
    "state": r"^US-[A-Z]{2}$",        # ISO 3166-2 subdivision code
}

def check_global(c):
    problems = []
    for col in c.columns:
        if col in GLOBAL_RULES:
            bad = con.sql(f"""
                SELECT DISTINCT {col} FROM '{c.path}'
                WHERE NOT regexp_full_match({col}, '{GLOBAL_RULES[col]}')
                ORDER BY 1""").fetchall()
            if bad:
                problems.append(f"{c.product}.{col} breaks ISO 3166-2: "
                                f"{[b[0] for b in bad]} -> {c.owner}")
    return problems

for c in (trips, tax):
    print(check_global(c) or f"{c.product}: ok")
```

Output:

```text
["trips.state breaks ISO 3166-2: ['CA', 'NY', 'WA'] -> mobility-data@"]
["tax_rates.state breaks ISO 3166-2: ['California', 'NY', 'WA'] -> finance-data@"]
```

```python
con.sql("""
    CREATE TABLE ref_state AS SELECT * FROM (VALUES
        ('CA', 'US-CA'), ('California', 'US-CA'),
        ('NY', 'US-NY'), ('New York', 'US-NY'),
        ('WA', 'US-WA'), ('Washington', 'US-WA')) t(raw, iso)
""")
for c in (trips, tax):
    new_path = c.path.replace(".parquet", "_v2.parquet")
    other = [k for k in c.columns if k != "state"]
    con.sql(f"""COPY (SELECT {', '.join(other)}, r.iso AS state
                      FROM '{c.path}' JOIN ref_state r ON state = r.raw)
                TO '{new_path}' (FORMAT parquet)""")
    c.path = new_path
    print(c.product, check_global(c) or "ok")

print(con.sql(f"""
    SELECT count(*) AS trips, round(sum(fare)) AS taxable_revenue,
           round(sum(fare * tax_rate)) AS tax_owed
    FROM '{trips.path}' JOIN '{tax.path}' USING (state)
""").fetchall()[0])
```

Output:

```text
trips ok
tax_rates ok
(200000, 3605056.0, 204462.0)
```

The conformed join covers every trip and the tax figure more than doubles. The fix is small, and a dbt test ([Transform](../../03-transform-and-orchestrate/notes/01-transform.md)) would do the same job within one project. What changes is where it lives: promoted from one project to an organisational rule, with the failure routed to the owner by name.

**The platform makes the right thing the easy thing.** Principles 1 and 2 add work for domain engineers, and Serra's point is that principle 3 exists to pay it back. A single publish call that runs the checks is the smallest version of that:

```python
catalog = {}

def publish(c):
    """Self-serve platform: one call, and the mandatory checks come with it."""
    errors = []
    if not c.owner:
        errors.append("no owner")
    if not c.description:
        errors.append("no description")
    errors += check_schema(c) + check_global(c)
    missing = [u for u in c.reads if u not in catalog]
    if missing:
        errors.append(f"reads unpublished products: {missing}")
    if errors:
        print(f"REJECTED {c.product}: {errors}")
        return False
    catalog[c.product] = c
    print(f"published {c.product} (owner {c.owner})")
    return True

publish(trips)
publish(tax)

# A consumer-aligned product built with no owner and no description.
con.sql(f"""COPY (SELECT state, sum(fare) AS revenue, sum(fare*tax_rate) AS tax_owed
                  FROM '{trips.path}' JOIN '{tax.path}' USING (state) GROUP BY state)
            TO 'pnl.parquet' (FORMAT parquet)""")
pnl = Contract("pnl", "finance", "", "pnl.parquet",
               {"state": "VARCHAR", "revenue": "DOUBLE", "tax_owed": "DOUBLE"},
               freshness_hours=24, reads=["trips", "tax_rates"])
publish(pnl)
pnl.owner, pnl.description = "finance-data@", "Profit and loss by state."
publish(pnl)
```

Output:

```text
published trips (owner mobility-data@)
published tax_rates (owner finance-data@)
REJECTED pnl: ['no owner', 'no description']
published pnl (owner finance-data@)
```

A catalog built from contracts also answers the question that opens most incidents, which is who gets hurt if this changes.

```python
board = Contract("exec_board", "strategy", "strategy-data@", "pnl.parquet",
                 {"state": "VARCHAR", "revenue": "DOUBLE"}, freshness_hours=24,
                 description="Board pack figures.", reads=["pnl"])
publish(board)

def downstream(product):
    """Who has to hear about a change to this product, breadth first."""
    seen, frontier = [], [product]
    while frontier:
        cur = frontier.pop(0)
        for c in catalog.values():
            if cur in c.reads and c.product not in seen:
                seen.append(c.product)
                frontier.append(c.product)
    return [(p, catalog[p].owner) for p in seen]

print(downstream("trips"))
print(downstream("exec_board"))
```

Output:

```text
published exec_board (owner strategy-data@)
[('pnl', 'finance-data@'), ('exec_board', 'strategy-data@')]
[]
```

Notice that `exec_board` was published without its author ever telling the mobility team, and a change to `trips` now knows to reach them. That is the fabric's catalog doing principle 4's work. [Monitors and lineage](../../05-quality-and-observability/notes/02-monitors-and-lineage.md) shows the runtime version with OpenLineage.

**Domain types** (Dehghani's three, with Serra's examples):

| Type | Owns | Example |
|---|---|---|
| Source-aligned | Data close to an operational system, not fitted to a consumer | Manufacturing, sales, supplier |
| Aggregated | Combines several domains, often for query performance | Profit and loss, from manufacturing and sales |
| Consumer-aligned | Shaped for specific users or uses | A simplified supplier model for people outside supplier |

Serra also draws a customer 360 domain that cleans and masters customer data so that other domains pull from it rather than each mastering their own. Designing the domains is the hard part. He calls domain-driven design very difficult and time-consuming, and warns against having to redesign months in.

## Serra's skepticism and his mesh types

Serra (over 35 years in databases) is a mesh skeptic, and the chapter says so:

- **Gartner's 2023 hype cycle** put data mesh near the peak with a "moderate" benefit rating and 5% to 20% market penetration, and predicted it "will be obsolete before the plateau", evolving toward data fabric. This is Gartner as quoted by Serra; the report itself isn't in our sources.
- **His informal poll.** At talks, usually at least 75% of a room have heard of data mesh, one or two in a hundred are building one, and he has yet to see a hand for one in production. He labels this anecdotal.
- **"Pure" data mesh** (all four principles followed completely) he expects no company to build, and a *minimum viable mesh* is undefined. He also rejects the claim that warehouses fail because they can't scale: failures are almost always people, process or the wrong technology choice.

He still says the mesh's ideas can improve any of the other architectures, which is the useful reading.

His three implementation types run from control to agility:

| Type | Technology | Storage | Serra's view |
|---|---|---|---|
| Type 1 | Same tech for all domains | One physical lake, a folder or container per domain | What he sees most, since it avoids cross-lake performance problems and simplifies security, monitoring and backup |
| Type 2 | Same tech | A lake per domain | Truly decentralised, at the cost of linking the lakes and getting acceptable cross-domain performance |
| Type 3 | Any tech, any cloud, per domain | Anything | The pure vision; he thinks it will never be adopted |

**Mesh against fabric:** they aren't rivals. A fabric is a technical architecture. A mesh is an ownership model, so broad that Serra hesitates to call it an architecture. A fabric can be the architecture used *within* the domains of a mesh, and one mesh can hold several fabrics (pp. 182-183). Our addition: a fabric's catalog and policies are often what makes principle 4 enforceable.

**Use cases on a scale:** responsibility runs from fully central IT to fully domain-owned. Data federation (domains own their data, even if IT builds the analytical data) satisfies only principle 1 (p. 183). Serra argues you need principle 2, data as a product, before it's fair to call it a mesh, because that is where the organisational and technical scaling comes from. If most responsibilities sit with IT, he says, what you have is better called an enterprise data fabric or lakehouse (p. 185).

## Is a mesh right for you?

This table is our synthesis of the two sources, not a test either of them gives.

| Signal | Leans central | Leans mesh |
|---|---|---|
| Company size | One or a few teams | Many autonomous business units |
| Bottleneck | Compute, cost | The central data team's backlog |
| Domain data skills | Few | Engineers in each domain |
| Governance maturity | Low | Can agree global standards |
| Culture | Top-down | Teams already own services end to end |

Our advice (Serra defers fit to his chapter 14, not held): start with ownership (principle 1) and contracts (principle 2) on the datasets that hurt most, on a shared platform (Serra's Type 1). Decentralise the technology last, if ever.

## Strengholt's six topologies

Strengholt (Microsoft), in "Data Mesh: Topologies and domain granularity" on Towards Data Science, wrote up the shapes he saw in customer design sessions. He orders them "from full decentralization and fine-grained decoupling to more managed data distribution". The two axes below (domain granularity; peer to peer or a central distribution layer) are our framing, and topologies 3 and 4 don't sit cleanly on them. The article gives no counts.

```text
                    peer to peer              central distribution layer
  fine-grained      1 fully federated         2 fully governed
  by value chain    4 value-chain: autonomy inside a chain, central standards when crossing one
  mixed             3 hybrid federated: central on the source side, mesh on the consumer side
  coarse-grained    5 aligned                 6 governed
```

| # | Topology | Shape | Trade-off | Who picks it |
|---|---|---|---|---|
| 1 | Fine-grained, fully federated | Dehghani's pure form. Many small domains, each data product its own "architectural quantum"; data shared peer to peer; governance metadata logically central | Most flexible, but needs every domain to conform on interoperability and security, duplicates infrastructure, and makes cross-domain lookups problematic ("data gravity and decentralization don't go hand in hand") | Cloud-born, multi-cloud, young firms with many strong engineers |
| 2 | Fine-grained, fully governed | Domains own products in their own workspaces, but distribute them through a central storage layer ("multiple workspaces, shared lake") | Easier conformance, and history processed on shared compute is cheaper; slower time to market and more coupling, and he expects it to be harder on multi-cloud. In his words it "doesn't implement a full data mesh architecture", though it adheres to many mesh principles | Banks, governments, anyone who values compliance over agility |
| 3 | Hybrid federated | A central platform where source-aligned products are built, sometimes by a platform team; consumer side is more autonomous | Works with few engineers and legacy sources; heavier central onboarding and mixed operating models | Firms with legacy systems or limited skills: "some" data mesh |
| 4 | Value-chain-aligned | Domains grouped into value chains (supply chain, product development) with autonomy inside; central standards only across chain boundaries | Fits operational, back-and-forth data flows; boundaries need strong architect guidance | Supply chain, transport, product companies |
| 5 | Coarse-grained, aligned | Large organisational or regional domains, each holding "tens or hundreds of applications" and likely its own platform | Political fights over ownership; duplicated data quality and MDM on every platform; risks bigger silos. His advice: decompose domains first, then settle ownership, then guide product creation | Firms grown by mergers and acquisitions |
| 6 | Coarse-grained, governed | Large domains publish and consume through a central distribution platform or marketplace | Needs a highly mature self-service platform team and a strong governance mandate, or it fails | Large complex organisations taming peer-to-peer sprawl |

Strengholt concludes "there's no right or wrong": data mesh is a framework to pick from, which matches Serra's caution. The article never mentions Serra, so this mapping is ours: topology 2 is close to Serra's Type 1, topology 1 to his Type 3. Serra's warning fits topology 2: with most responsibilities in IT, call it a fabric or lakehouse.

## Scenario prompts, mapped to mechanisms

The handout groups discussion prompts into three themes. For each, here is the mechanism in this course that addresses it. The mapping is ours; the handout only poses the questions.

### Theme 1: misaligned ownership

| Prompt (paraphrased) | Root cause | Mechanism | Chapter |
|---|---|---|---|
| A Looker KPI is wrong; who fixes it? | No owner for the metric definition | Metric defined once in a dbt mart with an owner in `schema.yml` | [Transform](../../03-transform-and-orchestrate/notes/01-transform.md) |
| Snowplow event schema changed upstream and broke models | No contract between producer and consumer | Data contract; schema registry | [Contracts](../../02-ingest-and-modelling/notes/04-data-contracts.md), [Ingest](../../02-ingest-and-modelling/notes/01-ingest.md), principle 2 |
| Who approves a dbt PR that changes a shared model? | Unclear ownership of shared models | CODEOWNERS per model folder; CI runs `dbt build` on the PR | [Transform](../../03-transform-and-orchestrate/notes/01-transform.md), [ML engineering practices](../../06-ml-platform/notes/05-mlops-maturity-and-best-practices.md) |
| A failed test alerts; who is tagged? | Alert routes to a channel, not an owner | `owner` in the contract; the check names it, as `check_global` does above | [Incident playbooks](../../05-quality-and-observability/notes/03-incident-playbooks.md) |
| Who owns feature engineering code? | Features built in notebooks per model | One `prepare_features`, then a feature store | [Feature stores](../../06-ml-platform/notes/01-feature-stores.md) |
| Drift detected; who retrains? | Monitoring with no action owner | Alert to a conditional retraining flow with an owner | [Drift](../../06-ml-platform/notes/04-drift.md), [Orchestrate](../../03-transform-and-orchestrate/notes/02-orchestrate.md) |

### Theme 2: limited governance and QA

| Prompt | Root cause | Mechanism | Chapter |
|---|---|---|---|
| Where does this column come from? | No lineage | dbt docs DAG; fabric metadata catalog | [Transform](../../03-transform-and-orchestrate/notes/01-transform.md), [Data fabric](01-data-architectures-mesh-fabric-mdw.md#data-fabric), [Catalog](03-catalog-semantic-layer-and-contracts.md) |
| A dataset used by models is modified; who is hit? | Dependencies not recorded | `downstream()` over declared `reads`; lineage events | [Monitors and lineage](../../05-quality-and-observability/notes/02-monitors-and-lineage.md) |
| Backend data arrives with no QA | No check at the boundary | Tests at `error` severity at staging; quality dimensions | [Quality dimensions](../../05-quality-and-observability/notes/01-quality-dimensions-and-tests.md) |
| Two dashboards show different numbers | Two definitions of one metric | One definition per metric, in a mart or a semantic layer | [Transform](../../03-transform-and-orchestrate/notes/01-transform.md), [Semantic layer](03-catalog-semantic-layer-and-contracts.md#a-semantic-layer-compiles-the-question-at-its-grain) |
| Can't reproduce last quarter's experiment | Untracked data, params and code | MLflow runs with data path and git SHA tags | [Tracking and registry](../../06-ml-platform/notes/02-experiment-tracking-and-model-registry.md) |
| Is the model fair across groups? | No segment-level evaluation | Reports per segment; fairness checks in CI | [Drift](../../06-ml-platform/notes/04-drift.md) |

### Theme 3: "The pipeline is a monster"

| Prompt | Root cause | Mechanism | Chapter |
|---|---|---|---|
| A new analyst takes weeks to onboard | Undocumented, tangled models | Layers (staging/core/marts), dbt docs, a README per domain | [Transform](../../03-transform-and-orchestrate/notes/01-transform.md) |
| Adding a KPI to Looker takes a sprint | Every change passes through one central team | Domain ownership; self-serve platform | Principles 1 and 3 |
| An upstream change breaks things downstream | No contracts, no tests at boundaries | Contracts plus dbt tests at `error` severity at the staging boundary | [Contracts](../../02-ingest-and-modelling/notes/04-data-contracts.md), [Transform](../../03-transform-and-orchestrate/notes/01-transform.md) |
| No single source of truth | Copies in several stores | MDW with one serving layer; MDM | [Modern data warehouse](01-data-architectures-mesh-fabric-mdw.md#modern-data-warehouse), [Data fabric](01-data-architectures-mesh-fabric-mdw.md#data-fabric) |
| Events dropped silently | At-most-once delivery; no reconciliation | Commit offsets after processing; row-count checks | [Kafka](../../04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics.md), [Monitors](../../05-quality-and-observability/notes/02-monitors-and-lineage.md) |
| Need real-time inference | Batch-only architecture | Online serving, on a stream or an endpoint | [Serving](../../06-ml-platform/notes/03-batch-and-online-serving.md), [Kafka](../../04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics.md) |
| Each model rebuilds the same feature pipeline | No feature reuse | Feature store; features as a data product | [Feature stores](../../06-ml-platform/notes/01-feature-stores.md) |

Use these as interview practice: name the root cause first (usually ownership or a missing contract), then the mechanism, then the trade-off.

## Rules of thumb

| Rule | Why |
|---|---|
| Name the system of record for each fact | Everything else is derived, and can be rebuilt if you know from what |
| Size the architecture to the data | Our synthesis: SMP for modest data (Serra's case study is under 1 TB, projected within 10 TB), MDW up to about 10 TB, fabric or lakehouse beyond |
| A mesh is an ownership model, not a storage choice | Each domain still runs an MDW, fabric or lakehouse |
| Contracts before decentralisation | Ownership without contracts just moves the breakage |
| Start with Serra Type 1 (close to Strengholt's topology 2) | Shared platform, domain ownership of data; decentralise tech last. Our advice: Strengholt makes no starting recommendation |
| Lineage and a catalog pay for themselves first | Most governance prompts start with "where does this come from?" |

## Pitfalls

- **Calling a reorganised folder tree a mesh.** Grouping a lake's data by department applies principle 1 and none of the others; connecting lakes with virtualization software uses none of the four (p. 178).
- **Decentralising without a platform.** Principles 1 and 2 hand domains work; without principle 3 each one rebuilds the same pipelines, and costs and incompatibilities climb.
- **Governance as a document.** A standard nobody can fail is a suggestion. In the run above, the standard only took effect when `publish` called it.
- **Picking a standard and leaving the mapping out.** A regex tells you the code is malformed. It takes a shared reference table, owned by someone, to turn `California` into `US-CA`.
- **Domains drawn around applications.** Serra separates application domains from business domains, and says the challenge in creating domains is ownership: a business domain may own several applications. Strengholt adds that coarse regional boundaries invite political fights over who controls the data.
- **Inner joins across domains with no reconciliation.** Always compare row counts or totals before and after. The 40% loss here was one `count(*)` away from being seen.

## Try it

1. Drop the `WA` row from the conformed tax table and rerun the join. Does `check_global` catch it? What check would?
2. Add a required `freshness_hours` rule to `publish` that rejects any product whose parquet file is older than its promise. Use `os.path.getmtime`.
3. Your company has 3 TB, two data engineers, four business units that all queue on them, and two sources with PII. Write down an architecture and a mesh type from this chapter, and say what would change your mind.
4. A vendor says "buy our virtualization layer and you have a data mesh". Which principles does the product address?

<details><summary>Answers</summary>

1. `check_global` passes, because every value that exists is well formed. The conformed join loses every WA trip silently. You need a referential check (every `state` in `trips` has a row in `tax_rates`) or a reconciliation of row counts before and after the join; this is a contract between two products, and it belongs to the consumer-facing side.
2. `import os, time`, then `age_h = (time.time() - os.path.getmtime(c.path)) / 3600`, and append to `errors` when `age_h > c.freshness_hours`. On a real platform the signal comes from load metadata and not the file's modification time, which a copy can reset.
3. One defensible answer: an MDW or lakehouse on a shared platform, Serra's Type 1 at most, with contracts and owners on the two PII sources first. Two engineers cannot carry a domain team per unit. More engineers in the units, or a backlog that stays long after the platform improves, would move it toward domain ownership.
4. None of them on its own. Serra singles out this claim: connecting stores with virtualization software uses none of the four principles. It can support principle 3 as a tool, but ownership, products and governance are organisational.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| Is a data mesh an architecture? | Mainly an ownership and organisational model. Each domain still runs an MDW, fabric or lakehouse. |
| Name the four principles. | Domain ownership, data as a product, self-serve platform, federated computational governance. |
| Why can't domain tests catch `CA` against `California`? | Each table is valid by its own rules. The failure is between products, so it takes a global rule run by the platform, plus a shared mapping. |
| What's the minimum to call something a mesh? | There is no agreed minimum. Serra argues principle 2 must hold in addition to 1, since federation alone satisfies only 1. |
| Which mesh shape would you start with? | Shared platform, domains owning data: Serra's Type 1, which is close to Strengholt's topology 2 (our mapping; Strengholt says there's no right or wrong). Decentralise technology last. |
| A strong case against mesh? | Serra's: warehouses fail from people and process, not scale, and few meshes reach production. Gartner, as he quotes it, expected it to fold into fabric, though he doesn't. |
| Fabric or mesh? | Not a choice between rivals. A mesh can use a fabric inside each domain, and a fabric's catalog and policies help enforce principle 4. |

## Next

Federated governance named security and regulation as global rules without saying how they work. [Access control, PII and GDPR](02-access-control-pii-gdpr.md) takes the riders behind these trips and asks who may see them, what counts as anonymous, and how to delete one person from an immutable lake. For how automated the ML half of the organisation should be, see [the maturity model](../../06-ml-platform/notes/05-mlops-maturity-and-best-practices.md).
