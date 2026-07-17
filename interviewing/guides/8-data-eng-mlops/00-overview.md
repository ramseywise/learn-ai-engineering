# Pillar 8 — Data Engineering & MLOps

How data and models get to production and stay healthy: pipelines, orchestration,
warehouses, deployment, monitoring. The DataTalks courses in this repo are a complete
guided path — this pillar is the most "just do the course" of the ten.

## Learning path

1. **Data engineering end to end** — `data-engineering/DataTalks Data Engineering/`
   modules 01–06 in order: Docker/Terraform → orchestration → warehouse → analytics
   engineering (dbt) → batch (Spark) → streaming (Kafka). Each module has runnable
   homework; do it, don't read it.
2. **Dimensional modeling** — *The Data Warehouse Toolkit* (Kimball, `readings/`) after
   module 03, when star schemas stop being abstract.
3. **MLOps** — `data-engineering/DataTalks MLOps/` modules 01–07: tracking → training
   pipelines → deployment → monitoring → best practices.
4. **The cautionary tales** — *Hidden Technical Debt in ML Systems* + *Software
   Engineering for ML* (Amershi, ICSE 2019) — short papers that name what the courses
   guard against.
5. **Book-depth engineering** — *Machine Learning Engineering in Action* (Ben Wilson,
   `readings/`) as the narrative companion.
6. **Org-scale data** — data mesh handouts (`readings/8-data-eng-data-mesh/`) for the
   decentralization story; LLM-era bridges (embedding pipelines as ETL, prompt/config
   versioning) in the [interview guide](interview-guide.md) §3.

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| DataTalks Data Engineering (01–06 + projects) | code | `data-engineering/DataTalks Data Engineering/` | the full DE stack, hands-on |
| DataTalks MLOps (01–07) | code | `data-engineering/DataTalks MLOps/` | experiment tracking → monitored deployment |
| *The Data Warehouse Toolkit* (Kimball) | pdf | `readings/` | dimensional modeling canon |
| *ML Engineering in Action* (Wilson) | pdf | `readings/` | production ML war stories |
| Hidden Technical Debt (NIPS 2015) · SE for ML (Amershi) | pdf | `readings/general/`, `readings/2-llm-rlhf/` | why ML systems rot |
| Data mesh handouts | pdf | `readings/8-data-eng-data-mesh/` | domain-oriented data architecture |
| Embedder Warmup · Production Hardening Patterns · PGVector Migration · Cloud Run + Cloud SQL | wiki | librarian | deployment patterns from real systems |
| ML practice rules | note | `~/.claude/rules/ml.md`, `logging.md` | personal engineering checklist |

## Test yourself
[interview-guide.md](interview-guide.md) · rounds:
[technical-questions](../../rounds/technical-questions.md),
[system-design-round](../../rounds/system-design-round.md) (pipelines are the substrate),
[coding-challenge](../../rounds/coding-challenge.md) (idempotency idioms).
