# References — Data Engineering

> Every source the notes cite, mapped to notes. **★** = read first. Local PDFs live in [sources/](sources/). The two zoomcamp snapshots live in [DataTalks Data Engineering/](DataTalks%20Data%20Engineering/) and [DataTalks MLOps/](DataTalks%20MLOps/). Vendor and secondary posts are flagged in [Source quality](#source-quality). The **License** column says what each source allows and how this folder uses it.

---

## Books and courses

| | Source | License | Notes |
|---|---|---|---|
| ★ | DataTalksClub, [*Data Engineering Zoomcamp*](https://github.com/DataTalksClub/data-engineering-zoomcamp) (2024-era snapshot in [DataTalks Data Engineering/](DataTalks%20Data%20Engineering/)). Modules 01–06 and workshops 1 (dlt) and 2 (RisingWave) | Free course; no LICENSE file in the snapshot (upstream licence unchecked). Vendored as-is; notes paraphrase and quote short code | 01, 02, 03, 04 |
| ★ | DataTalksClub, [*MLOps Zoomcamp*](https://github.com/DataTalksClub/mlops-zoomcamp) (2024-era snapshot in [DataTalks MLOps/](DataTalks%20MLOps/)). Modules 01–07 | As above | 03, 05, 06, 08 |
| ★ | Martin Kleppmann, *Designing Data-Intensive Applications* (O'Reilly, 1st ed., 2017; ISBN 978-1-449-37332-0). [sources/kleppmann-designing-data-intensive-applications.pdf](sources/kleppmann-designing-data-intensive-applications.pdf). Ch. 3 (storage, column stores), 6 (partitioning) and 10 (batch) → 04; ch. 4 (encoding, schema evolution) and 11 (streams) → 01 | Proprietary (O'Reilly). Personal reference copy; not quoted beyond chapter pointers | 01, 04 |
| ★ | James Serra, *Deciphering Data Architectures* (O'Reilly, 2024), chapter excerpts: [ch. 10 modern data warehouse](sources/serra-deciphering-data-architectures-ch10-modern-data-warehouse.pdf), [ch. 11 data fabric](sources/serra-deciphering-data-architectures-ch11-data-fabric.pdf), [ch. 13 data mesh foundation](sources/serra-deciphering-data-architectures-ch13-data-mesh-foundation.pdf). **Attribution inferred from content** (the excerpts have no title page; author bio and chapter numbers match) | Proprietary (O'Reilly). Course handouts; paraphrased | 07 |
| | Paul Iusztin & Maxime Labonne, *LLM Engineer's Handbook* (Packt, 2024). Chapter PDFs in [../generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/](../generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/); code at [PacktPublishing/LLM-Engineers-Handbook](https://github.com/PacktPublishing/LLM-Engineers-Handbook). Folded in as: ch. 3 → [01](notes/01-ingest.md#unstructured-ingest-crawling-documents-for-an-llm); ch. 11 → [03](notes/03-orchestrate.md); appendix (MLOps principles) → [05](notes/05-monitor.md#three-kinds-of-drift), [08](notes/08-mlops-maturity-and-best-practices.md). Ch. 1 (FTI) is already in [generative-ai 01-llm-fundamentals 02](../generative-ai/01-llm-fundamentals/notes/02-training-and-adapting.md). Ch. 2 (tool installation) is skipped. Notes cite it as `(*LLM Engineer's Handbook*, ch. N)` | Proprietary (Packt). Personal copy; paraphrased, short code rewritten | 01, 03, 05, 08 |
| | Joe Reis and Matt Housley, [*Fundamentals of Data Engineering*](https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/) (O'Reilly, 2022): the data-engineering lifecycle; a broader frame for the six foundations | Proprietary. Further reading | 01–05 |
| | James Densmore, [*Data Pipelines Pocket Reference*](https://www.oreilly.com/library/view/data-pipelines-pocket/9781492087823/) (O'Reilly, 2021): ingestion and ELT patterns, short | Proprietary. Further reading | 01, 02 |
| | dbt Labs, [*dbt Fundamentals*](https://courses.getdbt.com/courses/fundamentals) (free course) | Free course. Further reading | 02 |
| | Markus Winand, [*Use The Index, Luke*](https://use-the-index-luke.com/): indexing for the OLTP side of [04](notes/04-warehouse-and-store.md)'s OLTP vs OLAP table. Also cited by `programming/` SQL 08 | Read online | 04 |

## First-party docs

| | Source | License | Notes |
|---|---|---|---|
| ★ | [dlt docs](https://dlthub.com/docs/intro) | Apache-2.0 (code) | 01 |
| | [Apache Kafka documentation](https://kafka.apache.org/documentation/) | Apache-2.0 | 01 |
| ★ | dbt docs: [materializations](https://docs.getdbt.com/docs/build/materializations), [data tests](https://docs.getdbt.com/docs/build/data-tests) | Docs; dbt Core Apache-2.0 | 02 |
| | [Mage docs](https://docs.mage.ai/introduction/overview); [mage-zoomcamp](https://github.com/mage-ai/mage-zoomcamp), [mage-ai/mlops](https://github.com/mage-ai/mlops), [Terraform templates](https://github.com/mage-ai/mage-ai-terraform-templates) | Apache-2.0 | 03 |
| | [Prefect docs](https://docs.prefect.io/) | Apache-2.0 | 03 |
| ★ | [Dagster docs](https://docs.dagster.io/); [Airflow docs](https://airflow.apache.org/docs/): the orchestrators the zoomcamps skip | Apache-2.0 | 03 |
| ★ | BigQuery: [partitioned tables](https://cloud.google.com/bigquery/docs/partitioned-tables), [BQML model export](https://cloud.google.com/bigquery-ml/docs/export-model-tutorial) | Docs, CC BY 4.0 (Google) | 04 |
| | [Spark SQL guide](https://spark.apache.org/docs/latest/sql-programming-guide.html) | Apache-2.0 | 04 |
| ★ | [DuckDB](https://duckdb.org/docs/), [Polars](https://docs.pola.rs/), [Delta Lake](https://delta.io/), [Apache Iceberg](https://iceberg.apache.org/docs/latest/): the modern single-node and table-format gaps | MIT / MIT / Apache-2.0 / Apache-2.0 | 04, 07 |
| ★ | [Evidently docs](https://docs.evidentlyai.com/) | Apache-2.0 | 05 |
| | [Grafana provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/) | AGPL-3.0 (Grafana OSS) | 05 |
| ★ | [MLflow model registry](https://mlflow.org/docs/latest/model-registry.html) | Apache-2.0 | 06 |
| | AWS, [Using Lambda with Kinesis](https://docs.aws.amazon.com/lambda/latest/dg/with-kinesis.html) | Docs | 06 |
| ★ | Microsoft, [*MLOps maturity model*](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model) (the MLOps 01 section 1.5 reading; old URL `docs.microsoft.com/.../mlops-maturity-model`) | Docs, CC BY 4.0 (Microsoft Learn) | 08 |
| | [LocalStack docs](https://docs.localstack.cloud/); [pre-commit hooks](https://github.com/pre-commit/pre-commit-hooks), [isort](https://github.com/pycqa/isort), [black](https://github.com/psf/black) | Apache-2.0 / MIT | 08 |

## Papers

None. The folder rests on two courses, two books and vendor docs. The data-mesh source closest to a primary text is Dehghani's article below.

## Secondary and vendor posts

| | Source | License | Notes |
|---|---|---|---|
| ★ | Zhamak Dehghani, [*Data Mesh Principles and Logical Architecture*](https://martinfowler.com/articles/data-mesh-principles.html) (martinfowler.com, 2020): the four principles in the originator's words | Read online | 07 |
| ★ | Piethein Strengholt, *Data Mesh: Topologies and domain granularity* (Towards Data Science). [sources/strengholt-data-mesh-topologies.pdf](sources/strengholt-data-mesh-topologies.pdf) (saved web page, 13 pp.) | Proprietary (author's article). Course handout; paraphrased | 07 |
| | *Data mesh scenario prompts* handout. [sources/data-mesh-scenario-prompts-handout.pdf](sources/data-mesh-scenario-prompts-handout.pdf). Origin unknown (course or workshop material) | Unknown. Prompts paraphrased and mapped to mechanisms | 07 |
| | Max Schultze, [*Data Mesh in Practice*](https://www.youtube.com/watch?v=ekEc8D_D3zY) (talk): Zalando's mesh rollout | Video | 07 |
| | Pedram Navid, [*Airflow, Prefect, and Dagster: An Inside Look*](https://towardsdatascience.com/airflow-prefect-and-dagster-an-inside-look-6074781c9b77) (TDS) | Read online | 03 |
| | Damon Cortesi, [*An Introduction to Modern Data Lake Storage Layers*](https://dacort.dev/posts/modern-data-lake-storage-layers/) (Hudi, Iceberg, Delta Lake) | Read online | 04 |
| | Rivery, [*ETL vs ELT: What's the Difference?*](https://rivery.io/blog/etl-vs-elt/) | Vendor post | 02 |
| | AltexSoft, [*Snowflake, Redshift, BigQuery, and Others: Cloud Data Warehouse Tools Compared*](https://www.altexsoft.com/blog/snowflake-redshift-bigquery-data-warehouse-tools/) | Vendor post | 04 |
| | DataTalks.Club podcast, [*Data Observability* with Barr Moses](https://datatalks.club/podcast/s03e03-data-observability.html) | Podcast | 05 |
| | DataTalks.Club podcast, [*Analytics Engineer* with Victoria Perez Mola](https://datatalks.club/podcast/s03e11-analytics-engineer.html) | Podcast | 02 |
| | DataTalks.Club podcast, [*DataOps 101* with Lars Albertsson](https://datatalks.club/podcast/s02e11-dataops.html) | Podcast | 08 |

The last eight rows and *Fundamentals of Data Engineering*, *Data Pipelines Pocket Reference*, *dbt Fundamentals* and *Use The Index, Luke* come from DataTalksClub's [awesome-data-engineering.md](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/awesome-data-engineering.md), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Only the entries the notes use were kept; the full list (careers, communities, blogs, people to follow) is upstream.

## Source quality

| Source | Caveat | How the notes handle it |
|---|---|---|
| DE Zoomcamp module 02 (Mage) | Videos only; no code in the snapshot | [03](notes/03-orchestrate.md) is `confidence: medium`; Mage code labelled illustrative (mage-zoomcamp shape) |
| Zoomcamp requirements | Mostly unpinned (`mlflow`, `evidently`, `prefect`); Prefect 2 `orion` imports are legacy | Run labels in each note and the README say what to pin |
| Old CURRICULUM.md, MLOps 05 | Said "Prometheus"; the module uses Postgres + Grafana | Corrected in [05](notes/05-monitor.md) |
| Serra excerpts | Opinionated (a declared mesh skeptic); attribution inferred | [07](notes/07-data-architectures-mesh-fabric-mdw.md) is `confidence: medium` and presents the skepticism as his view |
| Gartner hype-cycle placement of data mesh | Second-hand, via Serra | Quoted as Serra's citation, not checked |
| Strengholt, vendor posts, podcasts | Single-author experience, vendor interest (Rivery, AltexSoft) | Used for framing and comparisons, not for numbers |
| BigQuery size figures (1.6 GB → 106 MB; 1.1 GB → 864.5 MB) | From the course videos/README on the 2019–2020 taxi data | Quoted as course figures in [04](notes/04-warehouse-and-store.md) |
