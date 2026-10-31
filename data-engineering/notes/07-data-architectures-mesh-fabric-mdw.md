---
origin: handout-synthesis
sources:
  - ../sources/serra-deciphering-data-architectures-ch10-modern-data-warehouse.pdf
  - ../sources/serra-deciphering-data-architectures-ch11-data-fabric.pdf
  - ../sources/serra-deciphering-data-architectures-ch13-data-mesh-foundation.pdf
  - ../sources/strengholt-data-mesh-topologies.pdf
  - ../sources/data-mesh-scenario-prompts-handout.pdf
  - https://martinfowler.com/articles/data-mesh-principles.html
confidence: medium
cleaned: 2026-10-31
---
# 7 — Data architectures: modern data warehouse, data fabric, data mesh

> Notes 01–06 build one pipeline. This note is about arranging many: where the data physically sits (modern data warehouse, data fabric, lakehouse) and who owns each part (data mesh). Most "the pipeline is a monster" problems are ownership problems.

---

## Where it sits

This note isn't one of the six foundations. It sits above them. The material is five PDFs in [sources/](../sources/): three chapter excerpts (10, 11 and 13), which from their content are James Serra's *Deciphering Data Architectures* (O'Reilly, 2024); Piethein Strengholt's data-mesh topologies article; and a scenario-prompts handout for discussion. The excerpts have no title page, so the attribution is inferred (see [references.md](../references.md)). Confidence is `medium` because these are opinionated secondary sources rather than course code.

| Question | Architecture | Section |
|---|---|---|
| Where does the data live, and how is it served? | Modern data warehouse, data fabric, lakehouse | 1–3 |
| Who owns each dataset and pipeline? | Centralised vs data mesh | 4–6 |
| What does it look like in practice? | Strengholt's topologies; scenario prompts | 7–8 |

---

## 1. Modern data warehouse (Serra ch. 10)

A **modern data warehouse (MDW)** is a relational data warehouse (RDW) plus a data lake. At least some data is copied from the lake into the RDW. If none is, and everything is queried in the lake, you have a lakehouse instead.

| Stage | What happens | Zoomcamp equivalent |
|---|---|---|
| Ingestion | Pull from sources into the lake | [01](01-ingest.md): dlt, Kafka, `wget` into GCS |
| Storage | Raw files in the lake | GCS bucket from Terraform ([01](01-ingest.md)) |
| Transformation | Clean, join, conform | dbt ([02](02-transform.md)), Spark ([04](04-warehouse-and-store.md)) |
| Data modeling | Star schema in the RDW | dbt `core` facts and dims ([02](02-transform.md)) |
| Visualization | Reports, dashboards | Looker Studio / Metabase ([02](02-transform.md)) |

The data-engineering zoomcamp *is* an MDW: GCS lake → BigQuery warehouse → dbt models → Looker Studio.

**Lake vs RDW roles:**

| | Data lake | Relational data warehouse |
|---|---|---|
| Schema | On read | On write |
| Users | Data scientists, power users | Business users, BI |
| Job | Staging, preparation, exploration, cheap storage of everything | Serving: fast queries, a stable model |
| Security | Folder/file level | Row- and column-level |
| Strength | Flexibility, any format | Compliance, performance, familiarity |

| Pros | Cons |
|---|---|
| Integrates many sources | Complexity: two systems to run |
| Scales storage and compute separately | Cost: data is stored twice |
| Can add real-time | Needs both lake and SQL skills |
| Performance where it matters (RDW) | Lake and RDW can drift into silos |
| Flexible: raw data is kept | Compliance across two stores |
| Fine-grained security in the RDW | Vendor lock-in on a cloud stack |

Serra says MDWs are most popular under about 10 TB. Above that, the cost of copying data into the RDW pushes teams towards a lakehouse.

**Stepping stones** for a team with an on-prem enterprise data warehouse (EDW):

| Path | What you do |
|---|---|
| EDW augmentation | Keep the EDW; add a lake for new sources and data science |
| Temporary lake + EDW | Land data in a lake, load the EDW from it, retire the old ETL over time |
| All-in-one | Lake only, query it directly. Close to a lakehouse |

**Case study (Wilson & Gunkerk):** under 1 TB, so the firm chose a symmetric multiprocessing (SMP) database (a single node, e.g. Azure SQL Database) rather than a massively parallel processing (MPP) warehouse. Lesson: don't buy MPP for data that fits on one machine. That's the same point as the "don't partition tables under 1 GB" rule in [04](04-warehouse-and-store.md), at a larger scale.

### The lakehouse

A lakehouse drops the RDW copy and adds warehouse features (ACID transactions, schema enforcement, time travel) to the lake through an open table format: Delta Lake, Apache Iceberg or Hudi. The zoomcamp doesn't teach table formats. The gap and a comparison table are in [04](04-warehouse-and-store.md#modern-gaps-duckdb-polars-delta-lake-and-iceberg).

---

## 2. Data fabric (Serra ch. 11)

A **data fabric** is an MDW plus features that make the data findable, governed and accessible without moving it all. Serra counts eight:

| Feature | What it adds |
|---|---|
| Data access policies | Central rules for who sees what, enforced everywhere |
| Metadata catalog | Search across all datasets, with **lineage** (where a column came from) |
| Master data management (MDM) | One golden record per customer, product, supplier |
| Data virtualization | Query data where it sits, without copying |
| Real-time processing | Streams alongside batch ([01](01-ingest.md)) |
| APIs | Programmatic access for apps |
| Services | Reusable shared functions such as data quality and masking |
| Products | Packaged, documented datasets for consumers |

Serra's rule of thumb: an MDW with three or more of these is a data fabric. The line is fuzzy on purpose. A fabric is an evolution of an MDW, not a replacement. The cost is a lot more technology to buy and integrate.

---

## 3. Choosing the physical architecture

| You have | Consider |
|---|---|
| Under about 1 TB, one team | A single SMP database. Or DuckDB ([04](04-warehouse-and-store.md)) |
| Up to about 10 TB, BI-heavy | MDW |
| Many sources, governance pain, lineage questions | Data fabric (MDW plus catalog, MDM, policies) |
| Large data, data science heavy, cost-sensitive | Lakehouse |
| Many autonomous business units | Data mesh on top of any of the above |

The last row matters: a data mesh is *not* a fourth storage option. It's an organisational model, and each domain still picks an MDW, a fabric or a lakehouse for its own data.

---

## 4. Data mesh: the four principles (Serra ch. 13)

Centralised architectures have a central data team own ingestion, modelling and serving for the whole company. Zhamak Dehghani's data mesh decentralises that, using four principles that answer four challenges:

| Challenge with central ownership | Principle | What it means |
|---|---|---|
| Lack of ownership: the central team doesn't understand the source data | **1. Domain ownership** | The team that produces the data owns its pipeline and its analytical data |
| Low quality: nobody downstream can fix upstream issues | **2. Data as a product** | Domains publish datasets with owners, SLAs, docs, schemas and quality checks |
| Technical scaling: every domain rebuilds infrastructure | **3. Self-serve data platform** | A central platform team builds the shared tooling (storage, pipelines, catalog) that domains use |
| Organisational scaling: chaos without standards | **4. Federated computational governance** | Global standards (IDs, formats, security) set jointly and enforced by the platform, in code |

**Data product vs data as a product:** a *data product* is any useful dataset or model. *Data as a product* is the discipline of treating it like a product: discoverable, addressable, trustworthy, self-describing, interoperable, secure. A **data contract** is the written, enforced interface: schema, semantics, SLA and owner.

**Federated governance example:** one domain stores US states as `CA`, another as `California`. Joining them silently fails. A global standard ("ISO 3166-2 codes") set by the federated group and enforced in the platform fixes it. That is a dbt test ([02](02-transform.md)) promoted from one project to an organisational rule.

**Domain types:**

| Type | Owns | Example |
|---|---|---|
| Source-aligned | Data close to an operational system | Manufacturing, sales, supplier |
| Aggregated | Combines several source domains | Profit and loss |
| Consumer-aligned | Shaped for one use | Customer 360 for marketing |

---

## 5. Serra's skepticism and his mesh types

Serra (35 years in databases) is a mesh skeptic, and the chapter says so:

- **Gartner's 2023 hype cycle** put data mesh near the peak, labelled "obsolete before plateau", with 5–20% penetration.
- **"Pure" data mesh** (all four principles, fully decentralised) is rare, and a *minimum viable mesh* is undefined.
- Most companies lack the domain-level data skills that principle 1 assumes.

His three implementation types:

| Type | Technology | Storage | Serra's view |
|---|---|---|---|
| Type 1 | Same tech for all domains | One physical lake, a folder per domain | Most practical; governance is easy |
| Type 2 | Same tech | A lake per domain | Real isolation; costs more |
| Type 3 | Any tech, any cloud, per domain | Anything | The pure vision; he thinks it will never be widely adopted |

**Mesh vs fabric:** they aren't rivals. A fabric is a technical architecture. A mesh is an ownership model. A fabric can be the architecture used *within* the domains of a mesh, and a fabric's catalog and policies are often what makes principle 4 enforceable.

**Use cases on a scale:** responsibility runs from fully central IT to fully domain-owned. Data federation (domains own their data, IT owns everything else) satisfies only principle 1. You need at least principle 2, data as a product, before it's fair to call it a mesh.

---

## 6. Is a mesh right for you?

| Signal | Leans central | Leans mesh |
|---|---|---|
| Company size | One or a few teams | Many autonomous business units |
| Bottleneck | Compute, cost | The central data team's backlog |
| Domain data skills | Few | Engineers in each domain |
| Governance maturity | Low | Can agree global standards |
| Culture | Top-down | Teams already own services end to end |

Start with ownership (principle 1) and contracts (principle 2) on the datasets that hurt most. Do this on a shared platform (Serra's Type 1). Decentralise the technology last, if ever.

---

## 7. Strengholt's six topologies

Strengholt (Microsoft) wrote up the shapes he saw in customer design sessions. Two axes separate them: how fine-grained the domains are, and whether data moves peer to peer or through a central distribution layer.

| # | Topology | Shape | Trade-off | Who picks it |
|---|---|---|---|---|
| 1 | Fine-grained, fully federated | Dehghani's pure form. Many small domains, each data product its own "architectural quantum"; data shared peer to peer; governance metadata logically central | Most flexible, but needs every domain to conform on interoperability and security, duplicates infrastructure, and makes cross-domain lookups costly ("data gravity and decentralization don't go hand in hand") | Cloud-born, multi-cloud, young firms with many strong engineers |
| 2 | Fine-grained, fully governed | Domains own products in their own workspaces, but distribute them through a central storage layer ("multiple workspaces, shared lake") | Easier conformance and cheaper history; slower time to market, more coupling, hard on multi-cloud | Banks, governments, anyone who values compliance over agility |
| 3 | Hybrid federated | A central platform where source-aligned products are built, sometimes by a platform team; consumer side is more autonomous | Works with few engineers and legacy sources; heavier central onboarding and mixed operating models | Firms with legacy systems or limited skills: "some" data mesh |
| 4 | Value-chain-aligned | Domains grouped into value chains (supply chain, product development) with autonomy inside; central standards only across chain boundaries | Fits operational, back-and-forth data flows; boundaries need strong architect guidance | Supply chain, transport, product companies |
| 5 | Coarse-grained, aligned | A few large domains (regions, acquired units), each with tens or hundreds of apps and its own platform | Political fights over ownership; duplicated data quality and MDM on every platform; risks bigger silos | Firms grown by mergers and acquisitions |
| 6 | Coarse-grained, governed | Large domains publish and consume through a central distribution platform or marketplace | Needs a highly mature self-service platform team and a strong governance mandate, or it fails | Large complex organisations taming peer-to-peer sprawl |

Strengholt's conclusion matches Serra's caution: treat data mesh as a framework of principles to pick from, not an all-or-nothing target. His topology 2 ("multiple workspaces, shared lake") is close to Serra's Type 1, and his topology 1 is Serra's Type 3.

---

## 8. Scenario prompts, mapped to mechanisms

The handout groups discussion prompts into three themes. For each, here is the mechanism from this folder that addresses it.

### Theme 1: misaligned ownership

| Prompt (paraphrased) | Root cause | Mechanism | Note |
|---|---|---|---|
| A Looker KPI is wrong; who fixes it? | No owner for the metric definition | Metric defined once in a dbt mart with an owner in `schema.yml` | [02](02-transform.md) |
| Snowplow event schema changed upstream and broke models | No contract between producer and consumer | Data contract; schema registry | [01](01-ingest.md) (Avro + registry), principle 2 |
| Who approves a dbt PR that changes a shared model? | Unclear ownership of shared models | CODEOWNERS per model folder; CI runs `dbt build` on the PR | [02](02-transform.md), [08](08-mlops-maturity-and-best-practices.md) |
| Who owns feature engineering code? | Features built in notebooks per model | One `prepare_features`, then a feature store | [06](06-feature-serve.md) |
| Drift detected; who retrains? | Monitoring with no action owner | Alert → conditional retraining flow with an owner | [05](05-monitor.md), [03](03-orchestrate.md) |

### Theme 2: limited governance and QA

| Prompt | Root cause | Mechanism | Note |
|---|---|---|---|
| Where does this column come from? | No lineage | dbt docs DAG; fabric metadata catalog | [02](02-transform.md), section 2 |
| Two dashboards show different numbers | Two definitions of one metric | One mart per metric; a semantic layer | [02](02-transform.md) |
| Can't reproduce last quarter's experiment | Untracked data, params and code | MLflow runs with data path and git SHA tags | [06](06-feature-serve.md) |
| Is the model fair across groups? | No segment-level evaluation | Evidently reports per segment; fairness checks in CI | [05](05-monitor.md) |

### Theme 3: "The pipeline is a monster"

| Prompt | Root cause | Mechanism | Note |
|---|---|---|---|
| A new analyst takes weeks to onboard | Undocumented, tangled models | Layers (staging/core/marts), dbt docs, a README per domain | [02](02-transform.md) |
| Adding a KPI to Looker takes a sprint | Every change passes through one central team | Domain ownership; self-serve platform | principles 1 and 3 |
| An upstream change breaks things downstream | No contracts, no tests at boundaries | Contracts plus dbt tests at `error` severity at the staging boundary | [02](02-transform.md), [01](01-ingest.md) |
| No single source of truth | Copies in several stores | MDW with one serving layer; MDM | section 1–2 |
| Events dropped silently | At-most-once delivery; no reconciliation | Commit offsets after processing; row-count checks | [01](01-ingest.md), [05](05-monitor.md) |
| Need real-time inference | Batch-only architecture | Stream deployment (Kinesis/Lambda or Kafka) | [06](06-feature-serve.md), [01](01-ingest.md) |
| Each model rebuilds the same feature pipeline | No feature reuse | Feature store; features as a data product | [06](06-feature-serve.md) |

Use these as interview practice: name the root cause first (usually ownership or a missing contract), then the mechanism, then the trade-off.

---

## Rules of thumb

| Rule | Why |
|---|---|
| Size the architecture to the data | SMP under 1 TB, MDW up to about 10 TB, lakehouse beyond |
| A mesh is an ownership model, not a storage choice | Each domain still runs an MDW, fabric or lakehouse |
| Contracts before decentralisation | Ownership without contracts just moves the breakage |
| Start with Serra Type 1 / Strengholt topology 2 | Shared platform, domain ownership of data; decentralise tech last |
| Lineage and a catalog pay for themselves first | Most governance prompts start with "where does this come from?" |

---

→ Next: [08-mlops-maturity-and-best-practices.md](08-mlops-maturity-and-best-practices.md) — this note covered how the organisation arranges its data; the next measures how automated the ML half of it is, and the engineering practices (tests, IaC, CI/CD) that move a team up the levels.
