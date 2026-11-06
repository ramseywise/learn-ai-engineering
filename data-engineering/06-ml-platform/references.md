---
origin: curated
sources:
  - https://www.manning.com/books/machine-learning-engineering-in-action
  - https://arxiv.org/abs/1810.11953
  - https://arxiv.org/abs/2209.09125
  - https://arxiv.org/abs/2011.09926
confidence: high
cleaned: 2026-11-02
---
# References: ML platform

★ marks a reading that changed a claim in the notes. Links were checked on 2026-11-02 unless noted.

## Books

| Book | Chapters | PDF | Maps to |
|---|---|---|---|
| Kleppmann, [*Designing Data-Intensive Applications*](https://dataintensive.net/) (O'Reilly, 2017) | Ch. 11, time-dependent joins, pp. 475-476 | [PDF](../sources/kleppmann-designing-data-intensive-applications.pdf) | [01](notes/01-feature-stores.md) |
| ★ Wilson, [*Machine Learning Engineering in Action*](https://www.manning.com/books/machine-learning-engineering-in-action) (Manning, 2022) | Ch. 12 (drift); ch. 16 (registry, feature stores, serving) | [PDF](../sources/machine-learning-engineering-action.pdf) | [01](notes/01-feature-stores.md), [02](notes/02-experiment-tracking-and-model-registry.md), [03](notes/03-batch-and-online-serving.md), [04](notes/04-drift.md) |
| Iusztin and Labonne, *LLM Engineer's Handbook* ([code](https://github.com/PacktPublishing/LLM-Engineers-Handbook); Packt, 2024) | Ch. 2 (artifacts, metadata, trackers and registries) → [02](notes/02-experiment-tracking-and-model-registry.md); appendix, MLOps principles → [05](notes/05-mlops-maturity-and-best-practices.md). Chapter PDFs in [generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/](../../generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/) | none | [02](notes/02-experiment-tracking-and-model-registry.md), [05](notes/05-mlops-maturity-and-best-practices.md) |
| Huyen, *Designing Machine Learning Systems* (O'Reilly, 2022) | Further reading, **not cited**. The book wasn't available to read. Only the author's [public chapter summaries](https://github.com/chiphuyen/dmls-book/blob/main/summary.md) were read, and no claim in the notes rests on them | none | Further reading for [06](notes/06-ml-system-framing-to-monitoring.md) |

## Core papers

| Paper | Venue | PDF | Maps to |
|---|---|---|---|
| ★ Rabanser, Günnemann and Lipton, [*Failing Loudly*](https://arxiv.org/abs/1810.11953) | NeurIPS 2019 | [PDF](../sources/rabanser-2018-failing-loudly.pdf) | [04](notes/04-drift.md) |
| ★ Gama et al., [*A Survey on Concept Drift Adaptation*](http://eprints.bournemouth.ac.uk/22491/) | ACM Computing Surveys, 2014 | [PDF](../sources/gama-2014-survey-concept-drift-adaptation.pdf) | [04](notes/04-drift.md) |
| ★ Shankar et al., [*Operationalizing Machine Learning: An Interview Study*](https://arxiv.org/abs/2209.09125) | arXiv, 2022 | [PDF](../sources/shankar-2022-operationalizing-machine-learning.pdf) | [01](notes/01-feature-stores.md), [02](notes/02-experiment-tracking-and-model-registry.md), [03](notes/03-batch-and-online-serving.md), [04](notes/04-drift.md), [05](notes/05-mlops-maturity-and-best-practices.md) |
| Paleyes, Urma and Lawrence, [*Challenges in Deploying Machine Learning*](https://arxiv.org/abs/2011.09926) | ACM Computing Surveys, 2022 | [PDF](../sources/paleyes-2020-challenges-deploying-machine-learning.pdf) | [02](notes/02-experiment-tracking-and-model-registry.md), [03](notes/03-batch-and-online-serving.md), [05](notes/05-mlops-maturity-and-best-practices.md) |
| ★ Breck et al., [*The ML Test Score*](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/) | IEEE Big Data 2017 | [PDF](../sources/4156.pdf) | [05](notes/05-mlops-maturity-and-best-practices.md), [06](notes/06-ml-system-framing-to-monitoring.md) |
| ★ Amershi et al., [*Software Engineering for Machine Learning*](https://doi.org/10.1109/ICSE-SEIP.2019.00042) | ICSE-SEIP 2019 | [PDF](../sources/amershi-icse-2019-software-engineering-machine.pdf) | [05](notes/05-mlops-maturity-and-best-practices.md) |
| ★ Sculley et al., [*Hidden Technical Debt in Machine Learning Systems*](https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html) | NeurIPS 2015 | [PDF](../sources/hidden-technical-debt-machine-learning-systems.pdf) | [05](notes/05-mlops-maturity-and-best-practices.md), [06](notes/06-ml-system-framing-to-monitoring.md) |
| Ribeiro et al., [*Beyond Accuracy: Behavioral Testing of NLP Models with CheckList*](https://arxiv.org/abs/2005.04118) | ACL 2020 | none | [05](notes/05-mlops-maturity-and-best-practices.md) |

## Specifications and docs

| Source | Maps to |
|---|---|
| [Feast documentation](https://docs.feast.dev/) and its [point-in-time joins](https://docs.feast.dev/getting-started/concepts/point-in-time-joins) page | [01](notes/01-feature-stores.md) |
| [DuckDB ASOF join guide](https://duckdb.org/docs/stable/guides/sql_features/asof_join) | [01](notes/01-feature-stores.md) |
| [MLflow tracking](https://mlflow.org/docs/latest/ml/tracking/) and [model registry](https://mlflow.org/docs/latest/ml/model-registry/) | [02](notes/02-experiment-tracking-and-model-registry.md) |
| [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/) | [03](notes/03-batch-and-online-serving.md) |
| [AWS Lambda with Kinesis](https://docs.aws.amazon.com/lambda/latest/dg/with-kinesis.html) | [03](notes/03-batch-and-online-serving.md) |
| [SciPy `ks_2samp`](https://scipy.github.io/devdocs/reference/generated/scipy.stats.ks_2samp.html) | [04](notes/04-drift.md) |
| [Evidently documentation](https://docs.evidentlyai.com/) | [04](notes/04-drift.md) |
| [Microsoft MLOps maturity model](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model) | [05](notes/05-mlops-maturity-and-best-practices.md) |
| [Google, MLOps: continuous delivery and automation pipelines](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) | [01](notes/01-feature-stores.md), [05](notes/05-mlops-maturity-and-best-practices.md) |
| [LocalStack documentation](https://docs.localstack.cloud/) | [05](notes/05-mlops-maturity-and-best-practices.md) |
| [Amazon SageMaker AI developer guide](https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html), read on 2026-11-02: [Feature Store](https://docs.aws.amazon.com/sagemaker/latest/dg/feature-store.html), [managed MLflow](https://docs.aws.amazon.com/sagemaker/latest/dg/mlflow.html), [Experiments in Studio Classic](https://docs.aws.amazon.com/sagemaker/latest/dg/experiments.html), [Model Registry](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html), [inference options](https://docs.aws.amazon.com/sagemaker/latest/dg/model-deploy-feature-matrix.html), [batch transform](https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform.html), [shadow tests](https://docs.aws.amazon.com/sagemaker/latest/dg/shadow-tests.html), [deployment guardrails](https://docs.aws.amazon.com/sagemaker/latest/dg/deployment-guardrails.html) and [canary traffic shifting](https://docs.aws.amazon.com/sagemaker/latest/dg/deployment-guardrails-blue-green-canary.html), [Pipelines](https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines.html) | [05](notes/05-mlops-maturity-and-best-practices.md) |
| [SageMaker Model Monitor](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html), [model quality](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-model-quality.html) and its [availability change](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-availability-change.html), read on 2026-11-02 | [05](notes/05-mlops-maturity-and-best-practices.md) |

## Courses and videos

| Course | Platform | Cost | Notes | Weeks |
|---|---|---|---|---|
| [MLOps Zoomcamp, module 01: intro](https://github.com/DataTalksClub/mlops-zoomcamp/tree/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7/01-intro) | GitHub, DataTalks.Club | Free | Duration model, environment, maturity model; [05](notes/05-mlops-maturity-and-best-practices.md) | 1 |
| [Module 02: experiment tracking](https://github.com/DataTalksClub/mlops-zoomcamp/tree/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7/02-experiment-tracking) | GitHub, DataTalks.Club | Free | MLflow tracking and registry; [02](notes/02-experiment-tracking-and-model-registry.md) | 1 |
| [Module 03: orchestration](https://github.com/DataTalksClub/mlops-zoomcamp/tree/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7/03-orchestration) | GitHub, DataTalks.Club | Free | Retraining pipelines; treated in [the orchestration chapter](../03-transform-and-orchestrate/notes/02-orchestrate.md) | 1 |
| [Module 04: deployment](https://github.com/DataTalksClub/mlops-zoomcamp/tree/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7/04-deployment) | GitHub, DataTalks.Club | Free | Web service, streaming, batch; [03](notes/03-batch-and-online-serving.md) | 1 |
| [Module 05: monitoring](https://github.com/DataTalksClub/mlops-zoomcamp/tree/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7/05-monitoring) | GitHub, DataTalks.Club | Free | Evidently, Postgres, Grafana; treated in [the monitors chapter](../05-quality-and-observability/notes/02-monitors-and-lineage.md) and used by [04](notes/04-drift.md) | 1 |
| [Module 06: best practices](https://github.com/DataTalksClub/mlops-zoomcamp/tree/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7/06-best-practices) | GitHub, DataTalks.Club | Free | Tests, LocalStack, Terraform, CI/CD; [05](notes/05-mlops-maturity-and-best-practices.md) | 1 |
| [Module 07: project](https://github.com/DataTalksClub/mlops-zoomcamp/tree/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7/07-project) | GitHub, DataTalks.Club | Free | The capstone rubric; [05](notes/05-mlops-maturity-and-best-practices.md) | 2 |
