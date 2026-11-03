---
origin: curated
sources:
  - https://www.vldb.org/pvldb/vol11/p1781-schelter.pdf
  - https://mlsys.org/Conferences/2019/doc/2019/167.pdf
  - https://sre.google/sre-book/managing-incidents/
confidence: high
cleaned: 2026-11-02
---
# References: quality and observability

★ marks a reading that changed a claim in the notes. Links were checked on 2026-11-02 unless noted.

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| Kleppmann, [*Designing Data-Intensive Applications*](https://dataintensive.net/) (O'Reilly, 2017) | Ch. 12, auditing and end-to-end checks, pp. 530-532 | [PDF](../sources/kleppmann-designing-data-intensive-applications.pdf) | [01](notes/01-quality-dimensions-and-tests.md) |
| ★ Beyer, Jones, Petoff and Murphy, [*Site Reliability Engineering*](https://sre.google/sre-book/table-of-contents/) (O'Reilly, 2016), free online | [6 Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/), [14 Managing incidents](https://sre.google/sre-book/managing-incidents/), [15 Postmortem culture](https://sre.google/sre-book/postmortem-culture/); for the new notes [3 Embracing risk](https://sre.google/sre-book/embracing-risk/), [4 Service level objectives](https://sre.google/sre-book/service-level-objectives/), [8 Release engineering](https://sre.google/sre-book/release-engineering/), [11 Being on-call](https://sre.google/sre-book/being-on-call/), [26 Data integrity](https://sre.google/sre-book/data-integrity/) | none | [02](notes/02-monitors-and-lineage.md), [03](notes/03-incident-playbooks.md), [05](notes/05-operating-data-stores.md), [06](notes/06-dataops.md) |
| Iusztin and Labonne, *LLM Engineer's Handbook* (Packt, 2024) | Appendix, MLOps principles | none | [02](notes/02-monitors-and-lineage.md) |
| Beyer, Murphy, Rensin, Kawahara and Thorne, [*The Site Reliability Workbook*](https://sre.google/workbook/table-of-contents/) (O'Reilly, 2018), free online | [Data processing pipelines](https://sre.google/workbook/data-processing/), [Implementing SLOs](https://sre.google/workbook/implementing-slos/), [Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) | none | [06](notes/06-dataops.md) |

## Core papers

| Paper | Venue | PDF | Maps to |
|---|---|---|---|
| ★ Schelter et al., [Automating Large-Scale Data Quality Verification](https://www.vldb.org/pvldb/vol11/p1781-schelter.pdf) (dimensions; constraints as aggregation queries) | VLDB 2018 | none | [01](notes/01-quality-dimensions-and-tests.md) |
| ★ Breck et al., [Data Validation for Machine Learning](https://mlsys.org/Conferences/2019/doc/2019/167.pdf) (anomaly rates in production; why chi-squared over-alerts at scale) | MLSys 2019 | none | [01](notes/01-quality-dimensions-and-tests.md), [02](notes/02-monitors-and-lineage.md) |
| ★ Breck et al., [The ML Test Score](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/) (schemas, invariants, dependency notices) | IEEE Big Data 2017 | [PDF](../sources/4156.pdf) | [01](notes/01-quality-dimensions-and-tests.md), [02](notes/02-monitors-and-lineage.md), [03](notes/03-incident-playbooks.md) |
| Sculley et al., [Hidden Technical Debt in Machine Learning Systems](https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html) (data dependencies; data testing debt) | NeurIPS 2015 | [PDF](../sources/hidden-technical-debt-machine-learning-systems.pdf) | [01](notes/01-quality-dimensions-and-tests.md), [02](notes/02-monitors-and-lineage.md) |

## Specifications and docs

| Source | Maps to |
|---|---|
| dbt: [data tests](https://docs.getdbt.com/docs/build/data-tests), [severity](https://docs.getdbt.com/reference/resource-configs/severity), [store_failures](https://docs.getdbt.com/reference/resource-configs/store_failures), [contract](https://docs.getdbt.com/reference/resource-configs/contract), [build](https://docs.getdbt.com/reference/commands/build), [freshness](https://docs.getdbt.com/reference/resource-properties/freshness) | [01](notes/01-quality-dimensions-and-tests.md), [02](notes/02-monitors-and-lineage.md) |
| Great Expectations: [Create an Expectation](https://docs.greatexpectations.io/docs/core/define_expectations/create_an_expectation), [expectation gallery](https://greatexpectations.io/expectations/). Code run on 1.24.1 | [01](notes/01-quality-dimensions-and-tests.md) |
| OpenLineage: [object model](https://openlineage.io/docs/spec/object-model), [run cycle](https://openlineage.io/docs/spec/run-cycle), [Python client](https://openlineage.io/docs/client/python), [column lineage facet](https://openlineage.io/docs/spec/facets/dataset-facets/column_lineage_facet). Code run on 1.55.0. [Marquez](https://marquezproject.ai/) | [02](notes/02-monitors-and-lineage.md) |
| [Evidently docs](https://docs.evidentlyai.com/). The course's legacy API was run on 0.4.36 with `pandas<2.3` | [02](notes/02-monitors-and-lineage.md) |
| [Grafana provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/) | [02](notes/02-monitors-and-lineage.md) |
| [Iceberg, Branching and Tagging](https://iceberg.apache.org/docs/latest/branching/) (audit branches) | [01](notes/01-quality-dimensions-and-tests.md), [03](notes/03-incident-playbooks.md) |
| [Monte Carlo, What is data observability](https://www.montecarlodata.com/blog-what-is-data-observability/) (vendor framing of the five pillars) | [02](notes/02-monitors-and-lineage.md) |
| Postgres migrations: [explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html), [ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html), [CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html), [lock_timeout and client settings](https://www.postgresql.org/docs/current/runtime-config-client.html). Code run on 16.2 | [04](notes/04-schema-and-data-migrations.md) |
| Fowler, [Parallel Change](https://martinfowler.com/bliki/ParallelChange.html) and, with Sadalage, [Evolutionary Database Design](https://martinfowler.com/articles/evodb.html) | [04](notes/04-schema-and-data-migrations.md) |
| [Stripe, Online migrations at scale](https://stripe.com/blog/online-migrations) (engineering post) | [04](notes/04-schema-and-data-migrations.md) |
| GitLab: [migration style guide](https://docs.gitlab.com/development/migration_style_guide/), [batched background migrations](https://docs.gitlab.com/development/database/batched_background_migrations/) | [04](notes/04-schema-and-data-migrations.md) |
| Alembic: [autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html), [offline mode](https://alembic.sqlalchemy.org/en/latest/offline.html), [runtime API](https://alembic.sqlalchemy.org/en/latest/api/runtime.html). Code run | [04](notes/04-schema-and-data-migrations.md) |
| [Flyway migrations](https://documentation.red-gate.com/fd/migrations-271585107.html), [gh-ost](https://github.com/github/gh-ost). Read and not run | [04](notes/04-schema-and-data-migrations.md) |
| [dbt-audit-helper](https://github.com/dbt-labs/dbt-audit-helper), [Snowflake cloning](https://docs.snowflake.com/en/user-guide/object-clone), [Qdrant collections](https://qdrant.tech/documentation/concepts/collections/), [Elasticsearch aliases](https://www.elastic.co/docs/manage-data/data-store/aliases). Read and not run; the warehouse and vector moves in the note are simulated locally | [04](notes/04-schema-and-data-migrations.md) |
| [GitLab postmortem of the 31 January 2017 outage](https://about.gitlab.com/blog/2017/02/10/postmortem-of-database-outage-of-january-31/) | [05](notes/05-operating-data-stores.md) |
| Postgres operations: [backup](https://www.postgresql.org/docs/current/backup.html), [dump](https://www.postgresql.org/docs/current/backup-dump.html), [file system backup](https://www.postgresql.org/docs/current/backup-file.html), [continuous archiving](https://www.postgresql.org/docs/current/continuous-archiving.html), [connections](https://www.postgresql.org/docs/current/runtime-config-connection.html), [process model](https://www.postgresql.org/docs/current/connect-estab.html), [routine vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html), [statistics views](https://www.postgresql.org/docs/current/monitoring-stats.html), [standby](https://www.postgresql.org/docs/current/warm-standby.html), [hot standby](https://www.postgresql.org/docs/current/hot-standby.html), [upgrading](https://www.postgresql.org/docs/current/upgrading.html), [partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html). Code run on 16.2; `pg_upgrade` read and not run | [05](notes/05-operating-data-stores.md) |
| PgBouncer: [features](https://www.pgbouncer.org/features.html), [usage](https://www.pgbouncer.org/usage.html). Read and not run | [05](notes/05-operating-data-stores.md) |
| [The DataOps Manifesto](https://dataopsmanifesto.org/en/) (stewarded by DataKitchen, a vendor) | [06](notes/06-dataops.md) |
| dbt delivery: [environments](https://docs.getdbt.com/docs/environments-in-dbt), [defer](https://docs.getdbt.com/reference/node-selection/defer), [node selection methods](https://docs.getdbt.com/reference/node-selection/methods), [continuous integration](https://docs.getdbt.com/docs/deploy/continuous-integration), [exposures](https://docs.getdbt.com/docs/build/exposures), [Semantic Layer](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl). Code run on dbt Core 1.12.6 with dbt-duckdb; hosted CI and the Semantic Layer read and not run | [06](notes/06-dataops.md) |
| [Airflow best practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html). Read and not run | [06](notes/06-dataops.md) |
| [Twelve-Factor App, config](https://12factor.net/config), [GitHub Actions secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions) | [06](notes/06-dataops.md) |
| Terraform: [intro](https://developer.hashicorp.com/terraform/intro), [plan](https://developer.hashicorp.com/terraform/cli/commands/plan), [state](https://developer.hashicorp.com/terraform/language/state), [lifecycle](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle). Read and not run; the note uses a small model of the loop | [06](notes/06-dataops.md) |
| [OpenMetadata](https://docs.open-metadata.org/latest), [DataHub features](https://docs.datahub.com/docs/features). Overview pages read and not run | [06](notes/06-dataops.md) |
| [Hightouch, What is Reverse ETL?](https://hightouch.com/blog/reverse-etl) (vendor guide) | [06](notes/06-dataops.md) |

## Courses and videos

| Course | Platform | Cost | Notes | Weeks |
|---|---|---|---|---|
| [MLOps Zoomcamp, module 05: monitoring](https://github.com/DataTalksClub/mlops-zoomcamp/tree/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7/05-monitoring) | GitHub, DataTalks.Club | Free | Evidently, Postgres, Grafana; the source of the model half of [02](notes/02-monitors-and-lineage.md) | 1 |
| [Data Engineering Zoomcamp, module 04: analytics engineering](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering) | GitHub, DataTalks.Club | Free | dbt tests and source freshness | 1 |
| [dbt Fundamentals](https://learn.getdbt.com/courses/dbt-fundamentals) | dbt Learn | Free | Tests and sources in a guided project | 1 |
