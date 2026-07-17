# Data Engineering & MLOps — Study Guide

Tested directly in MLE loops and as the substrate of every system-design answer. The
DataTalks courses in this repo map 1:1 to the interview checklist — each module below names
its folder.

## 1. Data engineering checklist (DataTalks DE structure)

- **Containers & IaC** (`01-docker-terraform`) — reproducible environments; infra as
  reviewable code; know why Dockerfiles beat "works on my machine" in an interview story.
- **Workflow orchestration** (`02-workflow-orchestration`) — DAGs, idempotency,
  **backfills**, retries with backoff, sensor vs schedule triggers. Idempotency is the word
  interviewers listen for: reruns must not double-write (upserts, partition overwrites,
  dedup keys).
- **Warehouse** (`03-data-warehouse`) — columnar storage, partitioning + clustering,
  star schema vs wide tables, slowly changing dimensions (Kimball — *Data Warehouse Toolkit*
  in readings). OLTP vs OLAP in one breath.
- **Analytics engineering** (`04-analytics-engineering`) — dbt-style: SQL transforms as
  versioned, tested, documented models; staging → marts layering; data tests (unique,
  not-null, referential) in CI.
- **Batch** (`05-batch`) — Spark-style distributed processing: partitions, shuffles (the
  expensive thing), skew handling; when DuckDB/Polars on one box beats a cluster (most
  interview-scale data).
- **Streaming** (`06-streaming`) — Kafka concepts: topics/partitions/consumer groups,
  at-least-once vs exactly-once, watermarks/late data; answer "do we actually need
  streaming?" before designing it.
- Formats & lakes: Parquet (columnar, predicate pushdown) over CSV for anything processed;
  lakehouse table formats give ACID over object storage.
- Data quality & governance: expectations/contracts at ingest, lineage, PII classification
  (ties to [security-safety](../7-security-safety/interview-guide.md) §5). Data mesh handouts in
  `readings/8-data-eng-data-mesh/` for the org-level decentralization story.

## 2. MLOps checklist (DataTalks MLOps structure)

- **Maturity model** (`01-intro`) — notebook → scripted + tracked → automated pipeline →
  CI/CD-gated → monitored/self-healing. Place any system you describe on this ladder.
- **Experiment tracking** (`02-experiment-tracking`) — params/metrics/artifacts logged;
  model registry with stage transitions (staging → prod) and rollback.
- **Training pipelines** (`03-orchestration`) — training as a DAG, not a notebook: validate
  corpus → featurize → train → evaluate against baseline → register on pass.
- **Deployment** (`04-deployment`) — batch scoring vs online REST vs streaming consumer;
  cold-start and model-load latency (warm the model at startup — same pattern as embedder
  warmup in RAG services); shadow → canary → full rollout.
- **Monitoring** (`05-monitoring`) — service metrics (latency/errors) + data drift
  (input distributions) + concept drift (target relationship) + model quality against
  delayed labels; alert thresholds tied to retrain triggers.
- **Best practices** (`06-best-practices`) — tests for data code, pre-commit/lint,
  Makefiles, CI running the eval suite as a merge gate — the same regression-gate pattern
  as agent evals ([evals guide](../6-evals-observability/interview-guide.md) §4).

## 3. LLM-era additions (bridge topics)

Embedding pipelines are ETL (incremental refresh, fingerprint dedup, index rebuild plans);
vector DB operational concerns (snapshotting, reindexing, memory); prompt/config versioning
= model registry thinking applied to prompts; eval suites in CI/CD are the MLOps monitoring
story wearing new clothes — say this mapping out loud, it's the AIE-with-MLOps-roots
advantage.

## 4. Question bank (answer sketches)

- *"Design a daily pipeline for X."* — sources → ingest (idempotent, late-data tolerant) →
  validate (contracts) → transform (layered, tested) → serve (mart/feature store) →
  monitor + backfill story. Name the failure handling at each hop.
- *"Batch or streaming?"* — freshness requirement, cost, correctness complexity
  (exactly-once); usually: batch until a product need forces streaming.
- *"How does a model get to production?"* — registry + stage gates + eval-vs-baseline in
  CI + canary + monitored rollback path. If retraining: trigger = drift signal or schedule.
- *"Your dashboard number is wrong — debug."* — lineage walk: source freshness → ingest
  dedup → join fan-out → metric definition drift; check the cheapest layer first.
- *"Feature store — when?"* — online/offline consistency need (train/serve skew) + feature
  reuse across teams; otherwise a well-tested mart is enough.

## Sources

- repo: `data-engineering/DataTalks Data Engineering/` (modules 01–06 + projects), `data-engineering/DataTalks MLOps/` (modules 01–07)
- readings: `8-data-eng-data-mesh/` handouts, *The Data Warehouse Toolkit* (Kimball), *Machine Learning Engineering in Action*, `general/` (hidden-technical-debt, SE-for-ML)
- librarian wiki: Embedder Warmup · Production Hardening Patterns · PGVector Migration Pattern · Cloud Run + Cloud SQL Pattern · Synthetic Dataset Generation (fingerprinting)
- global rules: `~/.claude/rules/ml.md`, `~/.claude/rules/logging.md`
