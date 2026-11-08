---
origin: curated
sources:
  - ../references.md
confidence: high
cleaned: 2026-11-01
---
# Ingest and modelling: references

> The sources behind the four chapters in [notes/](notes/). Books shared across the data-engineering pillars are listed in the [subject references](../references.md). PDFs are in [../sources/](../sources/).

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| ★ Kimball and Ross, [*The Data Warehouse Toolkit*](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/), 2nd ed. (Wiley, 2002) ([3rd ed.](https://www.wiley.com/en-us/The+Data+Warehouse+Toolkit%3A+The+Definitive+Guide+to+Dimensional+Modeling%2C+3rd+Edition-p-9781118530801) is current; the notes follow the 2nd, held in this repo) | Chapter PDFs in [sources/data-warehouse-toolkit/](../sources/data-warehouse-toolkit/). Folded in as: ch. 1 → [02](notes/02-dimensional-modelling.md) (components, staging off-limits, size rules of thumb); ch. 2 → [02](notes/02-dimensional-modelling.md), [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (four-step design, row-width and date-dimension sizes, snowflaking cost, role-playing dates); ch. 3 → [02](notes/02-dimensional-modelling.md), [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (bus matrix, semi-additive and `AVG`, snapshot density, GMROI); ch. 4 → [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (SCD types, CRC change detection, natural-key counts); ch. 5 → [02](notes/02-dimensional-modelling.md), [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (fact-table kinds, accumulating snapshot, junk dimensions, unit-of-measure factors); ch. 6 → [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (minidimensions, outriggers, bridge tables with the levels column, flags and `DISTINCT` against double counting); ch. 7 → [02](notes/02-dimensional-modelling.md), [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (net-change budget facts, to-date totals computed not stored); ch. 8 → [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (Type 2 employee dimension with effective stamps, multivalued skills); ch. 9 → [02](notes/02-dimensional-modelling.md), [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (daily-snapshot size, point-in-time balance from transactions, heterogeneous products); ch. 10 → [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (degenerate bill number, service-line grain, 5 to 15 dimensions); ch. 11 → [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (class-of-service superdimension); ch. 12 → [02](notes/02-dimensional-modelling.md), [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (factless and coverage tables, 15-date applicant snapshot); ch. 13 → [02](notes/02-dimensional-modelling.md), [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (late-arriving rows, weighted diagnosis bridge, seven date roles); ch. 14 → [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (clickstream session and page-event grain and sizes); ch. 15 → [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) (written vs earned premium, per-line snapshots); ch. 16 → [01](notes/01-ingest.md) (CRC change detection, cross-reference table, suspense handling); ch. 17 → [01](notes/01-ingest.md) (warehouse follows application integration; other forecasts dated). Notes cite it as `(*Data Warehouse Toolkit*, ch. N)`. The chapter text is the 2nd edition (2002) | [full PDF](../sources/data-warehouse-toolkit.pdf) | [01](notes/01-ingest.md) · [02](notes/02-dimensional-modelling.md) · [03](notes/03-data-vault-and-obt.md) |
| ★ Kleppmann, [*Designing Data-Intensive Applications*](https://dataintensive.net/) (O'Reilly, 2017) | ch. 3 (star schemas), 4 and 10 (evolution, schema on read), 5 (logical replication), 11 (dual writes pp. 452-454, CDC, log compaction, event sourcing, idempotence, time-dependent joins pp. 475-476) | [PDF](../sources/kleppmann-designing-data-intensive-applications.pdf) | [01](notes/01-ingest.md) · [02](notes/02-dimensional-modelling.md) · [03](notes/03-data-vault-and-obt.md) · [04](notes/04-data-contracts.md) |
| Iusztin and Labonne, *LLM Engineer's Handbook* ([code](https://github.com/PacktPublishing/LLM-Engineers-Handbook); Packt, 2024) | ch. 2 (why a NoSQL store for the raw crawl); ch. 3 (crawling documents). Chapter PDFs in [generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/](../../generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/) | none | [01](notes/01-ingest.md) |
| Linstedt and Olschimke, [*Building a Scalable Data Warehouse with Data Vault 2.0*](https://shop.elsevier.com/books/building-a-scalable-data-warehouse-with-data-vault-20/linstedt/978-0-12-802510-9) (Morgan Kaufmann, 2015) | Not read; the note uses the standard description of the method and says so | none | [03](notes/03-data-vault-and-obt.md) |
| Jones, [*Driving Data Quality with Data Contracts*](https://www.oreilly.com/library/view/-/9781837635009) (Packt, 2023) | Not read in full; further reading | none | [04](notes/04-data-contracts.md) |
| Sanderson, Freeman and Schmidt, [*Data Contracts*](https://www.oreilly.com/library/view/-/9781098157623/) (O'Reilly, 2025) | Not read in full; further reading | none | [04](notes/04-data-contracts.md) |

## Core papers

★ marks a paper whose text changed a claim in the notes.

| Paper | Why read it | PDF | Maps to |
|---|---|---|---|
| ★ Breck et al., [*Data Validation for Machine Learning*](https://proceedings.mlsys.org/paper_files/paper/2019/file/928f1160e52192e3e0017fb63ab65391-Paper.pdf) (MLSys 2019) | Validation at Google scale. "The data comes first": infer a schema and let it co-evolve, in tension with up-front contracts | [public](https://proceedings.mlsys.org/paper_files/paper/2019/file/928f1160e52192e3e0017fb63ab65391-Paper.pdf) | [04](notes/04-data-contracts.md) |

## Standards and docs

| Doc | Use | Maps to |
|---|---|---|
| [Open Data Contract Standard](https://bitol-io.github.io/open-data-contract-standard/latest/) ([repo](https://github.com/bitol-io/open-data-contract-standard)) | The contract format and JSON Schema used in the chapter | [04](notes/04-data-contracts.md) |
| [Kimball dimensional modeling techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) | Free online summary of each technique | [02](notes/02-dimensional-modelling.md) · [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) |
| [Debezium features](https://debezium.io/documentation/reference/stable/features.html) | What log-based CDC gives you | [01](notes/01-ingest.md) |
| [dlt incremental loading](https://dlthub.com/docs/general-usage/incremental-loading) | Merge and state, tested offline against DuckDB | [01](notes/01-ingest.md) |
| [Apache Kafka documentation](https://kafka.apache.org/documentation/) | Producers, consumers, delivery | [01](notes/01-ingest.md) |
| [dbt snapshots](https://docs.getdbt.com/docs/build/snapshots) | Generated Type 2 history | [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md) |
| [Data Vault modeling (Wikipedia)](https://en.wikipedia.org/wiki/Data_vault_modeling) | Overview used in place of the book | [03](notes/03-data-vault-and-obt.md) |

## Posts

| Post | Treat as | Maps to |
|---|---|---|
| Kaminsky, ["Star Schema vs OBT for Data Warehouse Performance"](https://www.fivetran.com/blog/star-schema-vs-obt) (Fivetran, 2022) | A vendor benchmark, with the setup published: ten queries on a TPC-DS subset at scale 100. The best public numbers found, and limited to those queries | [03](notes/03-data-vault-and-obt.md) |

## Courses and videos

| Course | Platform | Cost | Supports |
|---|---|---|---|
| [DE Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) (DataTalks.Club), Module 1 and Workshop 1 upstream; snapshot vendored at [practice/datatalks-de/](practice/datatalks-de/), whose module numbers differ from upstream's current ones | GitHub, YouTube | Free | [01](notes/01-ingest.md): Docker, Terraform, dlt, then Kafka in the streaming module |
| Kimball Group [design tips and techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) | Web | Free | [02](notes/02-dimensional-modelling.md) · [02b](notes/02b-dimensional-modelling-history-and-conformed-dimensions.md): reading, in place of a course |
| [Confluent Kafka 101](https://developer.confluent.io/courses/apache-kafka/events/) | Web, video | Free | [01](notes/01-ingest.md): topics, partitions, consumers |
