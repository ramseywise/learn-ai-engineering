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
| ★ Beyer, Jones, Petoff and Murphy, [*Site Reliability Engineering*](https://sre.google/sre-book/table-of-contents/) (O'Reilly, 2016), free online | [6 Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/), [14 Managing incidents](https://sre.google/sre-book/managing-incidents/), [15 Postmortem culture](https://sre.google/sre-book/postmortem-culture/) | none | [02](notes/02-monitors-and-lineage.md), [03](notes/03-incident-playbooks.md) |
| Iusztin and Labonne, *LLM Engineer's Handbook* (Packt, 2024) | Appendix, MLOps principles | none | [02](notes/02-monitors-and-lineage.md) |

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

## Courses and videos

| Course | Platform | Cost | Notes | Weeks |
|---|---|---|---|---|
| [MLOps Zoomcamp, module 05: monitoring](https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/05-monitoring) | GitHub, DataTalks.Club | Free | Evidently, Postgres, Grafana; the source of the model half of [02](notes/02-monitors-and-lineage.md) | 1 |
| [Data Engineering Zoomcamp, module 04: analytics engineering](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering) | GitHub, DataTalks.Club | Free | dbt tests and source freshness | 1 |
| [dbt Fundamentals](https://learn.getdbt.com/courses/dbt-fundamentals) | dbt Learn | Free | Tests and sources in a guided project | 1 |
