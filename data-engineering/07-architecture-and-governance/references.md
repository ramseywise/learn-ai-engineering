---
origin: curated
sources:
  - https://martinfowler.com/articles/data-mesh-principles.html
  - https://eur-lex.europa.eu/eli/reg/2016/679/oj
  - https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf
  - https://www.cs.cornell.edu/~shmat/shmat_oak08netflix.pdf
confidence: medium
cleaned: 2026-11-02
---
# References: Architecture and governance

★ marks a reading that changed a claim in the notes. Links were checked on 2026-11-02 unless noted. The O'Reilly and Towards Data Science sites refuse automated checks, so those works are listed without a checked web link. Attribution of the three Serra excerpts is inferred from their content, as they have no title page.

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| ★ Kleppmann, [*Designing Data-Intensive Applications*](https://dataintensive.net/) (O'Reilly, 2017) | Ch. 11 (deletion on immutable logs, pp. 463-464), ch. 12 (derived data, federation and unbundling, timeliness and integrity, auditing, privacy pp. 490-543) | [PDF](../sources/kleppmann-designing-data-intensive-applications.pdf) | [01](notes/01-data-architectures-mesh-fabric-mdw.md), [02](notes/02-access-control-pii-gdpr.md) |
| ★ James Serra, *Deciphering Data Architectures* (O'Reilly, 2024) | Ch. 10 modern data warehouse | [PDF](../sources/serra-deciphering-data-architectures-ch10-modern-data-warehouse.pdf) | [01](notes/01-data-architectures-mesh-fabric-mdw.md) |
| ★ Same | Ch. 11 data fabric | [PDF](../sources/serra-deciphering-data-architectures-ch11-data-fabric.pdf) | [01](notes/01-data-architectures-mesh-fabric-mdw.md) |
| ★ Same | Ch. 13 data mesh foundation | [PDF](../sources/serra-deciphering-data-architectures-ch13-data-mesh-foundation.pdf) | [01](notes/01-data-architectures-mesh-fabric-mdw.md) |

## Core papers

| Paper | Venue | PDF | Maps to |
|---|---|---|---|
| ★ Narayanan and Shmatikov, *Robust De-anonymization of Large Sparse Datasets* | IEEE S&P 2008 | [Link](https://www.cs.cornell.edu/~shmat/shmat_oak08netflix.pdf) | [02](notes/02-access-control-pii-gdpr.md) |
| Samarati and Sweeney, *Protecting Privacy when Disclosing Information: k-Anonymity and Its Enforcement through Generalization and Suppression* | Technical report, 1998 | [Link](https://dataprivacylab.org/dataprivacy/projects/kanonymity/paper3.pdf) | [02](notes/02-access-control-pii-gdpr.md) |
| Paleyes, Urma and Lawrence, *Challenges in Deploying Machine Learning: a Survey of Case Studies* | ACM Computing Surveys, 2022 | [PDF](../sources/paleyes-2020-challenges-deploying-machine-learning.pdf) | [02](notes/02-access-control-pii-gdpr.md) |
| ★ Piethein Strengholt, *Data Mesh: Topologies and domain granularity* | Towards Data Science (article, not peer reviewed) | [PDF](../sources/strengholt-data-mesh-topologies.pdf) | [01](notes/01-data-architectures-mesh-fabric-mdw.md) |
| ★ Halevy et al., *Goods: Organizing Google's Datasets* | SIGMOD 2016 | [Link](https://doi.org/10.1145/2882903.2903730) ([copy read](https://static.aminer.org/pdf/20170130/pdfs/sigmod/zawvzadb9lb8xexcqvnr41prh5tmk7jc.pdf)) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| Sequeda, Allemang and Jacob, *A Benchmark to Understand the Role of Knowledge Graphs on Large Language Model's Accuracy for Question Answering on Enterprise SQL Databases*, data.world | GRADES-NDA 2024; arXiv v1 read in full | [Link](https://arxiv.org/abs/2311.07509) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| ⚑ Allemang and Sequeda, *Increasing the LLM Accuracy for Question Answering: Ontologies to the Rescue!*, data.world | arXiv preprint, v1 read in full; a chapter with a different title is at ISWC 2024, not read | [Link](https://arxiv.org/abs/2405.11706) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| ⚑ Rumiantsau and Fokeev, *Semantic Layers for Reliable LLM-Powered Data Analytics*, Cube | arXiv preprint, read in full; companion repo not read | [Link](https://arxiv.org/abs/2604.25149) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| Goedegebuure et al., data mesh grey-literature review | ACM Computing Surveys, 2024; arXiv v3 author's version read in full, online appendix not read | [Link](https://arxiv.org/abs/2304.01062) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| *Data mesh scenario prompts* handout, origin unknown | Course or workshop handout | [PDF](../sources/data-mesh-scenario-prompts-handout.pdf) | [01](notes/01-data-architectures-mesh-fabric-mdw.md) |

## Specifications and docs

| Source | Maps to |
|---|---|
| ★ Zhamak Dehghani, [Data Mesh Principles and Logical Architecture](https://martinfowler.com/articles/data-mesh-principles.html) and [How to Move Beyond a Monolithic Data Lake](https://martinfowler.com/articles/data-monolith-to-mesh.html) | [01](notes/01-data-architectures-mesh-fabric-mdw.md), [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| ★ [MetricFlow docs](https://docs.getdbt.com/docs/build/about-metricflow): [join logic](https://docs.getdbt.com/docs/build/join-logic), [entities](https://docs.getdbt.com/docs/build/entities), [ratio metrics](https://docs.getdbt.com/docs/build/ratio), [latest spec](https://docs.getdbt.com/docs/build/latest-metrics-spec), [commands](https://docs.getdbt.com/docs/build/metricflow-commands) (vendor; run locally) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| [dbt Labs, semantic layer vs text-to-SQL, 2026](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026) (vendor benchmark, 11 questions) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| [Cube docs: joins](https://docs.cube.dev/docs/data-modeling/joins.md), [multi-fact views](https://docs.cube.dev/docs/data-modeling/multi-fact-views.md), [Cube Core](https://docs.cube.dev/cube-core/index.md) (vendor; not run in the chapter) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| [DataHub docs: metadata ingestion](https://raw.githubusercontent.com/datahub-project/datahub/master/docs/architecture/metadata-ingestion.md), [glossary](https://raw.githubusercontent.com/datahub-project/datahub/master/docs/glossary/business-glossary.md), [ownership types](https://raw.githubusercontent.com/datahub-project/datahub/master/docs/ownership/ownership-types.md), [data contracts](https://raw.githubusercontent.com/datahub-project/datahub/master/docs/managed-datahub/observe/data-contract.md) (vendor) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| [OpenMetadata docs: tiers](https://docs.open-metadata.org/v2.0.x/how-to-guides/data-governance/classification/tiers.md), [glossary approval](https://docs.open-metadata.org/v2.0.x/how-to-guides/data-governance/glossary/approval.md), [KPIs](https://docs.open-metadata.org/v2.0.x/how-to-guides/data-insights/kpi.md), [downstream alerts](https://docs.open-metadata.org/v2.0.x/how-to-guides/data-quality-observability/alerts-notifications/notify-downstream.md) (vendor) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| [Microsoft Fabric endorsement](https://learn.microsoft.com/en-us/fabric/governance/endorsement-overview), the clearest definition of certification read (vendor) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| [Meta, Nemo](https://engineering.fb.com/data-infrastructure/nemo/) (self-reported, no metric definition) and [Eckerson preliminary catalog survey](https://datalere.com/articles/preliminary-survey-results-on-data-catalog-adoption) (2021, sample size not stated) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| ★ [Open Data Contract Standard v3.2.0 schema](https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/schema/odcs-json-schema-latest.json) and [support channels](https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/docs/support-communication-channels.md): no consumer field, on a search | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| Chad Sanderson, [The Rise of Data Contracts](https://dataproducts.substack.com/p/the-rise-of-data-contracts) (2022, practitioner essay) | [03](notes/03-catalog-semantic-layer-and-contracts.md) |
| [ISO 3166-2:US](https://en.wikipedia.org/wiki/ISO_3166-2:US), the subdivision codes chosen as the example standard (Wikipedia summary; iso.org refuses automated checks) | [01](notes/01-data-architectures-mesh-fabric-mdw.md) |
| ★ [Regulation (EU) 2016/679, GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj), official text. Articles linked through the unofficial mirror [gdpr-info.eu](https://gdpr-info.eu/) | [02](notes/02-access-control-pii-gdpr.md) |
| ★ [EDPB Guidelines 9/2022 on personal data breach notification](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-92022-personal-data-breach-notification-under_en) | [02](notes/02-access-control-pii-gdpr.md) |
| ★ [Article 29 Working Party, Opinion 05/2014 on anonymisation techniques](https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf), under the earlier Directive 95/46 | [02](notes/02-access-control-pii-gdpr.md) |
| [NIST SP 800-162, attribute based access control](https://csrc.nist.gov/pubs/sp/800/162/upd2/final) | [02](notes/02-access-control-pii-gdpr.md) |
| [NIST SP 800-122, protecting PII](https://csrc.nist.gov/pubs/sp/800/122/final) | [02](notes/02-access-control-pii-gdpr.md) |
| ★ [Securing DuckDB](https://duckdb.org/docs/stable/operations_manual/securing_duckdb/overview) | [02](notes/02-access-control-pii-gdpr.md) |
| [Postgres row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html), [BigQuery row-level](https://cloud.google.com/bigquery/docs/row-level-security-intro) and [column-level security](https://cloud.google.com/bigquery/docs/column-level-security-intro), [Snowflake masking](https://docs.snowflake.com/en/user-guide/security-column-ddm-intro) | [02](notes/02-access-control-pii-gdpr.md) |
| ★ [Delta Lake utilities: vacuum](https://docs.delta.io/latest/delta-utility.html), [Iceberg maintenance](https://iceberg.apache.org/docs/latest/maintenance/) | [02](notes/02-access-control-pii-gdpr.md) |

## Courses and videos

| Course | Platform | Cost | Notes | Weeks |
|---|---|---|---|---|
| [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) | GitHub, DataTalks.Club | Free | The MDW stack that [01](notes/01-data-architectures-mesh-fabric-mdw.md) maps its stages to | 9 |
| [Data Mesh Paradigm Shift in Data Platform Architecture](https://www.infoq.com/presentations/data-mesh-paradigm/), Zhamak Dehghani | InfoQ talk | Free | Originator's framing; [01](notes/01-data-architectures-mesh-fabric-mdw.md) | Talk |
| [Data Mesh in Practice](https://www.youtube.com/watch?v=ekEc8D_D3zY), Max Schultze | YouTube talk | Free | Zalando's rollout; a production case to weigh against Serra's poll in [01](notes/01-data-architectures-mesh-fabric-mdw.md) | Talk |
| [Data Privacy Fundamentals](https://www.coursera.org/learn/northeastern-data-privacy), Northeastern | Coursera | Check the course page | Non-engineering view of the legal side of [02](notes/02-access-control-pii-gdpr.md); not worked through for this chapter | Check the course page |
