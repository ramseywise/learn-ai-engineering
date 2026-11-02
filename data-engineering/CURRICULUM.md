# Data engineering: course curriculum

> Build data systems that stay correct when loads retry, schemas change, data arrives late, infrastructure fails, and people need to trust the answer.

This is the learner-facing syllabus. Pillar READMEs contain the detailed chapter stories, setup, decks, and runnable practice; `references.md` files contain complete source mappings.

## Course outcomes

By the end, you can build repeatable ingestion and well-modelled data; deliver tested, recoverable pipelines; choose storage and streaming systems by correctness, latency, and cost; detect and repair data incidents; build ML-platform foundations; and make defensible architecture and governance decisions.

## Before you begin

**Required:** [Programming](../programming/README.md): Python 01–03 and SQL 01–09. Docker basics help but are introduced in early practice. [Data Analytics](../data-analytics/README.md) is recommended, not required.

**Learning model:** read the unit chapters, use its deck where present, complete drills and practice, then preserve the stated evidence of mastery. Core examples run locally; cloud coursework is optional enrichment with local alternatives described in pillar READMEs.

## Course map

| Unit | Focus | Mastery evidence |
|---|---|---|
| [01 Foundations](01-storage-and-compute-foundations/README.md) | Storage, transactions, distributed systems, compute | Measured system design and failure analysis |
| [02 Ingest and modelling](02-ingest-and-modelling/README.md) | Trusted raw and modelled data | Repeatable load, grain statement, contract |
| [03 Transform and orchestrate](03-transform-and-orchestrate/README.md) | Tested, recoverable pipelines | Green build and idempotent backfill |
| [04 Warehouse, lakehouse, streaming](04-warehouse-lakehouse-streaming/README.md) | Stores, movement semantics, cost | Costed architecture decision |
| [05 Quality and observability](05-quality-and-observability/README.md) | Detection and recovery | Monitor, lineage trace, incident playbook |
| [06 ML platform](06-ml-platform/README.md) | Training, serving, monitoring | Point-in-time dataset and monitored service |
| [07 Architecture and governance](07-architecture-and-governance/README.md) | Teams, access, accountability | Defended architecture scenario |

## Unit syllabus

### 01 — Storage and compute foundations

**Objectives:** define reliability and performance goals; choose data models and encodings; explain row versus column storage; reproduce and prevent transaction anomalies; reason about replication, partitioning, clocks, consensus, and distributed compute.

**Learning:** eight [chapters](01-storage-and-compute-foundations/README.md#reading-order), chapter code, and practice. **Evidence:** measure a representative workload, explain a failure mode, and defend the smallest system that meets the requirement. **Key source:** Kleppmann, [*Designing Data-Intensive Applications*](https://dataintensive.net/), chapters 1–10.

### 02 — Ingest and modelling

**Objectives:** make loads repeatable; choose batch, CDC, or log ingestion; declare table grain; model facts, dimensions, and slowly changing attributes; compare Data Vault and One Big Table; write a data contract.

**Learning:** four [chapters](02-ingest-and-modelling/README.md#reading-order) and DataTalks practice. **Evidence:** a rerunnable load, star-model grain statement, reconciliation check, and contract that rejects a bad batch. **Key sources:** Kimball dimensional modelling; Kleppmann chapters 3, 4, 11, and 12.

### 03 — Transform and orchestrate

**Objectives:** structure transformations; test grain and joins; use dbt tests, snapshots, and incremental models; reason about logical dates, retries, and backfills; compare Dagster and Airflow.

**Learning:** five [chapters](03-transform-and-orchestrate/README.md#reading-order), runnable chapter code, and practice. **Evidence:** a green tested model plus a backfill that produces identical output when rerun. **Key sources:** dbt documentation; Kleppmann chapters 8–10.

### 04 — Warehouse, lakehouse, and streaming

**Objectives:** estimate scan cost; select layout and partitioning; explain table-format transactions; evaluate lakehouse trade-offs; implement safe producer/consumer semantics; reason about event time, watermarks, and lag.

**Learning:** five [chapters](04-warehouse-lakehouse-streaming/README.md#reading-order), [deck](04-warehouse-lakehouse-streaming/slides/warehouse-lakehouse-streaming.pptx), and labelled practice. **Evidence:** a costed store decision plus a stream design that says exactly-once from where to where. **Key sources:** Kleppmann chapters 3, 6, 7, 10–12; Kafka and Iceberg/Delta documentation.

### 05 — Quality and observability

**Objectives:** define quality dimensions; write batch tests and time-aware monitors; use lineage to bound an incident; contain and repair safely; write a blameless playbook and postmortem.

**Learning:** three [chapters](05-quality-and-observability/README.md#reading-order) and [deck](05-quality-and-observability/slides/quality-and-observability.pptx). **Evidence:** catch a planted fault, trace its impact, execute an idempotent repair, and add a preventive check. **Key sources:** Great Expectations, dbt, OpenLineage, and the pillar [references](05-quality-and-observability/references.md).

### 06 — ML platform

**Objectives:** build point-in-time features; track experiments and models; compare batch and online serving; detect drift; select appropriate platform maturity.

**Learning:** [chapters and practice](06-ml-platform/README.md). **Evidence:** a point-in-time-safe training dataset, registered run/model, served prediction, and diagnosis of drift versus pipeline failure. **Key sources:** [pillar references](06-ml-platform/references.md) and DataTalks MLOps coursework.

### 07 — Architecture and governance

**Objectives:** compare centralised, mesh, fabric, and MDW architectures; design ownership and interoperability; control access; protect PII; account for deletion, retention, and audit obligations.

**Learning:** [chapters and scenarios](07-architecture-and-governance/README.md). **Evidence:** defend an architecture with mechanisms and trade-offs, then write an access/retention decision for a dataset. **Key sources:** Kleppmann chapter 12 and [pillar references](07-architecture-and-governance/references.md).

## Completion standard and next steps

Complete a portfolio containing a repeatable ingest/model, tested and orchestrated pipeline, costed storage or streaming decision, quality incident response, ML-platform exercise, and governed architecture decision. Every item should state its grain or contract, failure handling, evidence, and trade-offs.

Continue to [Data Science](../data-science/README.md) for modelling depth, or [Generative AI](../generative-ai/README.md) and [AI Engineering](../ai-engineering/README.md) for LLM systems.
