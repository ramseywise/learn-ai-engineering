# References: Data Engineering

> The shared library for all seven pillars. Each pillar's own `references.md` maps its chapters to these sources in more detail. PDFs live in [sources/](sources/). **★** = read first. "Pillars" links to where a source is used. Vendor and secondary posts are flagged in [Source quality](#source-quality). The **License** column says what a source allows and how this folder uses it.

Pillar reference lists: [01](01-storage-and-compute-foundations/references.md) · [02](02-ingest-and-modelling/references.md) · [03](03-transform-and-orchestrate/references.md) · [04](04-warehouse-lakehouse-streaming/references.md) · [05](05-quality-and-observability/references.md) · [06](06-ml-platform/references.md) · [07](07-architecture-and-governance/references.md)

## Books

| | Book | PDF | Chapters and pillars | License |
|---|---|---|---|---|
| ★ | **Core text.** Martin Kleppmann, [*Designing Data-Intensive Applications*](https://dataintensive.net/) (O'Reilly, 1st ed., 2017; ISBN 978-1-449-37332-0). Read in full for these notes, reference lists omitted. The [reading map](CURRICULUM.md#reading-map-designing-data-intensive-applications) gives every chapter's notes | [PDF](sources/kleppmann-designing-data-intensive-applications.pdf) | Ch. 1 to 10 → [01](01-storage-and-compute-foundations/references.md); ch. 3, 4, 5, 10, 11 → [02](02-ingest-and-modelling/references.md); ch. 10, 11, 12 → [03](03-transform-and-orchestrate/references.md); ch. 3, 6, 7, 9, 10, 11, 12 → [04](04-warehouse-lakehouse-streaming/references.md); ch. 12 → [05](05-quality-and-observability/references.md); ch. 11 → [06](06-ml-platform/references.md); ch. 11, 12 → [07](07-architecture-and-governance/references.md) | Proprietary. Personal reference copy; not quoted beyond short passages and page pointers, and its figures are redrawn, never extracted |
| ★ | Ralph Kimball and Margy Ross, [*The Data Warehouse Toolkit*](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/) (Wiley, 2nd ed., 2002) | [PDF](sources/data-warehouse-toolkit.pdf) | [01](01-storage-and-compute-foundations/references.md), [02](02-ingest-and-modelling/references.md) | Proprietary. Personal copy; paraphrased |
| ★ | James Serra, *Deciphering Data Architectures* (O'Reilly, 2024), excerpts. **Attribution inferred from content**: the excerpts have no title page, and the author bio and chapter numbers match | [ch. 10](sources/serra-deciphering-data-architectures-ch10-modern-data-warehouse.pdf), [ch. 11](sources/serra-deciphering-data-architectures-ch11-data-fabric.pdf), [ch. 13](sources/serra-deciphering-data-architectures-ch13-data-mesh-foundation.pdf) | [07](07-architecture-and-governance/references.md) | Proprietary. Course handouts; paraphrased |
| ★ | Beyer, Jones, Petoff and Murphy, [*Site Reliability Engineering*](https://sre.google/sre-book/table-of-contents/) (O'Reilly, 2016) | Free online | [05](05-quality-and-observability/references.md) | Free to read online |
| ★ | Ben Wilson, [*Machine Learning Engineering in Action*](https://www.manning.com/books/machine-learning-engineering-in-action) (Manning, 2022) | [PDF](sources/machine-learning-engineering-action.pdf) | [06](06-ml-platform/references.md) | Proprietary. Personal copy; paraphrased |
| | Paul Iusztin and Maxime Labonne, *LLM Engineer's Handbook* (Packt, 2024); [code](https://github.com/PacktPublishing/LLM-Engineers-Handbook) | [Chapter PDFs](../generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/) | Ch. 3 → [Ingest](02-ingest-and-modelling/notes/01-ingest.md); ch. 11 → [Orchestrate](03-transform-and-orchestrate/notes/02-orchestrate.md); appendix → [Monitors](05-quality-and-observability/notes/02-monitors-and-lineage.md), [Maturity](06-ml-platform/notes/05-mlops-maturity-and-best-practices.md) | Proprietary. Personal copy; paraphrased, short code rewritten |
| | Joe Reis and Matt Housley, [*Fundamentals of Data Engineering*](https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/) (O'Reilly, 2022) | None | The data-engineering lifecycle: a broader frame for all seven pillars. Further reading, not cited for a claim | Proprietary |
| | James Densmore, [*Data Pipelines Pocket Reference*](https://www.oreilly.com/library/view/data-pipelines-pocket/9781492087823/) (O'Reilly, 2021) | None | Ingestion and ELT patterns, short. Further reading for [02](02-ingest-and-modelling/references.md), [03](03-transform-and-orchestrate/references.md) | Proprietary |
| | Linstedt and Olschimke, *Building a Scalable Data Warehouse with Data Vault 2.0*; Jones, *Driving Data Quality with Data Contracts*; Sanderson, Freeman and Schmidt, *Data Contracts* | None | Not read in full. Links and further reading in [02](02-ingest-and-modelling/references.md) | Proprietary |
| | Markus Winand, [*Use The Index, Luke*](https://use-the-index-luke.com/) | Free online | Indexing for the OLTP side of [Row and column stores](01-storage-and-compute-foundations/notes/03-row-and-column-stores.md) and [Warehouse and store](04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md). Also cited by `programming/` SQL | Read online |

## Core papers

Each pillar's `references.md` says why to read a paper and which chapter it changed.

| Theme | Papers | Pillar |
|---|---|---|
| Storage and execution | GFS, ★ MapReduce, C-Store, Bigtable, Dynamo, ★ *Column-Stores vs. Row-Stores*, Dremel, RDDs, Spark SQL, ★ *Scalability! But at what COST?*, DuckDB ([PDF](sources/raasveldt-2019-duckdb.pdf)) | [01](01-storage-and-compute-foundations/references.md), [04](04-warehouse-lakehouse-streaming/references.md) |
| Validation and contracts | ★ Breck et al., *Data Validation for Machine Learning* | [02](02-ingest-and-modelling/references.md), [05](05-quality-and-observability/references.md) |
| Tables and streams | ★ Delta Lake ([PDF](sources/armbrust-2020-delta-lake.pdf)), ★ Lakehouse ([PDF](sources/zaharia-2021-lakehouse.pdf)), ★ *The Dataflow Model* | [04](04-warehouse-lakehouse-streaming/references.md) |
| Data quality | ★ Schelter et al., *Automating Large-Scale Data Quality Verification*; ★ Breck et al., *The ML Test Score* ([PDF](sources/4156.pdf)); Sculley et al., *Hidden Technical Debt* ([PDF](sources/hidden-technical-debt-machine-learning-systems.pdf)) | [05](05-quality-and-observability/references.md), [06](06-ml-platform/references.md) |
| ML in production | ★ *Failing Loudly* ([PDF](sources/rabanser-2018-failing-loudly.pdf)), ★ Gama et al. on concept drift ([PDF](sources/gama-2014-survey-concept-drift-adaptation.pdf)), ★ Shankar et al. ([PDF](sources/shankar-2022-operationalizing-machine-learning.pdf)), Paleyes et al. ([PDF](sources/paleyes-2020-challenges-deploying-machine-learning.pdf)), ★ Amershi et al. ([PDF](sources/amershi-icse-2019-software-engineering-machine.pdf)), Ribeiro et al., CheckList | [06](06-ml-platform/references.md) |
| Privacy | ★ Narayanan and Shmatikov on de-anonymisation; Samarati and Sweeney on k-anonymity; Paleyes et al. | [07](07-architecture-and-governance/references.md) |

Filed in [sources/](sources/) and not yet read into a chapter: [Raissi, *Open Problems in Applied Deep Learning*](sources/raissi-2023-open-problems-applied-deep-learning.pdf).

## Courses and videos

Every link was opened on 2 November 2026. These are the courses shared across pillars, and pillar lists add single-module entries.

| Course | Platform | Cost | Pillars | Notes |
|---|---|---|---|---|
| ★ [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) (DataTalks.Club) | GitHub, YouTube | Free | [02](02-ingest-and-modelling/practice/datatalks-de/README.md), [03](03-transform-and-orchestrate/practice/datatalks-de), [04](04-warehouse-lakehouse-streaming/practice/datatalks-de) | The folders hold a 2024-era snapshot. Upstream has since moved to Kestra for orchestration and renumbered its modules (5 Data Platforms, 6 Batch, 7 Streaming), so module numbers differ. Self-paced, or with a cohort; the page lists the next one for January 2027 |
| ★ [MLOps Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp) (DataTalks.Club) | GitHub, YouTube | Free | [06](06-ml-platform/practice/datatalks-mlops/README.md), with [03](03-transform-and-orchestrate/references.md) and [05](05-quality-and-observability/references.md) | Snapshot in pillar 06, modules 01 to 07 |
| ★ Kleppmann, [Distributed Systems lectures](https://www.youtube.com/playlist?list=PLeKd45zvjcDFUEv_ohr_HdUFe97RItdiB) (University of Cambridge), with [notes](https://www.cl.cam.ac.uk/teaching/2122/ConcDisSys/materials.html) | YouTube | Free | [01](01-storage-and-compute-foundations/references.md), [04](04-warehouse-lakehouse-streaming/references.md) | 8 lectures, about 7 hours. Background on replication, logs and consistency |
| [CMU 15-445/645, Intro to Database Systems](https://15445.courses.cs.cmu.edu/) (Pavlo) | Web, YouTube | Free | [01](01-storage-and-compute-foundations/references.md) | Storage, execution and concurrency in depth |
| [dbt Fundamentals](https://learn.getdbt.com/courses/dbt-fundamentals) | dbt Learn | Free | [03](03-transform-and-orchestrate/references.md), [05](05-quality-and-observability/references.md) | A guided project with tests and sources |
| [Dagster University](https://courses.dagster.io/) | Web | Check site | [03](03-transform-and-orchestrate/references.md) | Assets and partitions; the site did not state a price that could be confirmed |
| [Kafka 101](https://developer.confluent.io/courses/apache-kafka/events/) | Confluent | Free | [02](02-ingest-and-modelling/references.md), [04](04-warehouse-lakehouse-streaming/references.md) | Topics, partitions and consumers with a real broker |
| [Lakehouse Fundamentals](https://www.databricks.com/learn/training/lakehouse-fundamentals) | Databricks | Free | [04](04-warehouse-lakehouse-streaming/references.md) | The vendor's own framing, so read it beside [Lakehouse against warehouse](04-warehouse-lakehouse-streaming/notes/03-lakehouse-vs-warehouse.md) |
| [Data Mesh in Practice](https://www.youtube.com/watch?v=ekEc8D_D3zY), Max Schultze | YouTube talk | Free | [07](07-architecture-and-governance/references.md) | Zalando's rollout |

## First-party docs

Each pillar lists the exact pages it cites. These are the entry points.

| | Source | License | Pillars |
|---|---|---|---|
| ★ | [DuckDB](https://duckdb.org/docs/), [Polars](https://docs.pola.rs/) | MIT | 01, 04 |
| ★ | [dlt](https://dlthub.com/docs/intro), [Apache Kafka](https://kafka.apache.org/documentation/) | Apache-2.0 | 02, 04 |
| ★ | dbt: [materializations](https://docs.getdbt.com/docs/build/materializations), [data tests](https://docs.getdbt.com/docs/build/data-tests) | Docs; dbt Core Apache-2.0 | 03, 05 |
| ★ | [Dagster](https://docs.dagster.io/), [Airflow](https://airflow.apache.org/docs/): the orchestrators the zoomcamps skip | Apache-2.0 | 03 |
| | [Prefect](https://docs.prefect.io/), [Mage](https://docs.mage.ai/introduction/overview), with [mage-zoomcamp](https://github.com/mage-ai/mage-zoomcamp), [mage-ai/mlops](https://github.com/mage-ai/mlops) and [Terraform templates](https://github.com/mage-ai/mage-ai-terraform-templates) | Apache-2.0 | 03 |
| ★ | BigQuery: [partitioned tables](https://cloud.google.com/bigquery/docs/partitioned-tables), [BQML model export](https://cloud.google.com/bigquery-ml/docs/export-model-tutorial) | Docs, CC BY 4.0 (Google) | 04 |
| | [Spark SQL guide](https://spark.apache.org/docs/latest/sql-programming-guide.html) | Apache-2.0 | 01, 04 |
| ★ | [Delta Lake](https://delta.io/), [Apache Iceberg](https://iceberg.apache.org/docs/latest/) | Apache-2.0 | 04, 07 |
| ★ | [Evidently](https://docs.evidentlyai.com/) | Apache-2.0 | 05, 06 |
| | [Grafana provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/) | AGPL-3.0 (Grafana OSS) | 05 |
| ★ | [MLflow model registry](https://mlflow.org/docs/latest/model-registry.html) | Apache-2.0 | 06 |
| | AWS, [Using Lambda with Kinesis](https://docs.aws.amazon.com/lambda/latest/dg/with-kinesis.html) | Docs | 06 |
| ★ | Microsoft, [*MLOps maturity model*](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model) | Docs, CC BY 4.0 (Microsoft Learn) | 06 |
| | [LocalStack](https://docs.localstack.cloud/); [pre-commit hooks](https://github.com/pre-commit/pre-commit-hooks), [isort](https://github.com/pycqa/isort), [black](https://github.com/psf/black) | Apache-2.0 / MIT | 06 |

## Secondary and vendor posts

| | Source | License | Pillars |
|---|---|---|---|
| ★ | Zhamak Dehghani, [*Data Mesh Principles and Logical Architecture*](https://martinfowler.com/articles/data-mesh-principles.html) (martinfowler.com, 2020): the four principles in the originator's words | Read online | 07 |
| ★ | Piethein Strengholt, *Data Mesh: Topologies and domain granularity* (Towards Data Science). [PDF](sources/strengholt-data-mesh-topologies.pdf), a saved web page | Proprietary (author's article). Course handout; paraphrased | 07 |
| | *Data mesh scenario prompts* handout. [PDF](sources/data-mesh-scenario-prompts-handout.pdf). Origin unknown (course or workshop material) | Unknown. Prompts paraphrased and mapped to mechanisms | 07 |
| | Rivery, [*ETL vs ELT: What's the Difference?*](https://rivery.io/blog/etl-vs-elt/) | Vendor post | 03 |
| | AltexSoft, [*Snowflake, Redshift, BigQuery, and Others: Cloud Data Warehouse Tools Compared*](https://www.altexsoft.com/blog/snowflake-redshift-bigquery-data-warehouse-tools/) | Vendor post | 04 |
| | DataTalks.Club podcast, [*Data Observability* with Barr Moses](https://datatalks.club/podcast/data-quality-data-observability-data-reliability.html) | Podcast | 05 |
| | DataTalks.Club podcast, [*Analytics Engineer* with Victoria Perez Mola](https://datatalks.club/podcast/analytics-engineer-skills-tools.html) | Podcast | 03 |
| | DataTalks.Club podcast, [*DataOps 101* with Lars Albertsson](https://datatalks.club/podcast/dataops-principles-and-scalable-data-platforms.html) | Podcast | 06 |

The last five rows, Schultze's talk, *Fundamentals of Data Engineering*, *Data Pipelines Pocket Reference*, *dbt Fundamentals* and *Use The Index, Luke* come from DataTalksClub's [awesome-data-engineering.md](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/awesome-data-engineering.md), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Only the entries the notes use were kept; the full list is upstream.

## Source quality

| Source | Caveat | How the notes handle it |
|---|---|---|
| DE Zoomcamp snapshot | 2024-era, with module numbers and an orchestrator that differ from upstream | [Orchestrate](03-transform-and-orchestrate/notes/02-orchestrate.md) labels which is which |
| DE Zoomcamp module 02 (Mage) | Videos only; no code in the snapshot | [Orchestrate](03-transform-and-orchestrate/notes/02-orchestrate.md) labels Mage code as illustrative |
| Zoomcamp requirements | Mostly unpinned (`mlflow`, `evidently`, `prefect`); Prefect 2 `orion` imports are legacy | The run labels in the [README](README.md#coursework-with-run-labels) say what to pin |
| Serra excerpts | Opinionated (a declared mesh skeptic); attribution inferred | [Data architectures](07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md) presents the skepticism as his view |
| Gartner hype-cycle placement of data mesh | Second-hand, via Serra | Quoted as Serra's citation, not checked |
| Strengholt, vendor posts, podcasts | Single-author experience, vendor interest (Rivery, AltexSoft) | Used for framing and comparisons, not for numbers |
| BigQuery size figures (1.6 GB → 106 MB; 1.1 GB → 864.5 MB) | From the course videos and README on the 2019 to 2020 taxi data | Quoted as course figures in [Warehouse and store](04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md) |
| O'Reilly book pages | The publisher blocks automated link checks, so the links rest on the ISBN and title | Listed as further reading |
