---
origin: course-synthesis
sources:
  - https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/01-intro
  - https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/06-best-practices
  - https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/07-project
  - https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model
  - https://docs.localstack.cloud/
  - "Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), appendix (MLOps principles)"
  - https://arxiv.org/abs/2005.04118
confidence: high
cleaned: 2026-10-31
---
# 8 — MLOps maturity and engineering best practices

> A maturity model tells you how much of the ML lifecycle runs without a human. Tests, a Makefile, pre-commit hooks, Terraform and CI/CD are what move a team up the levels. MLOps 06 applies all of them to the streaming service from note 06.

---

## Where it sits

Like [07](../../07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md), this is cross-cutting. It isn't one of the six foundations: it's the engineering wrapped around all of them. The material is MLOps 01 section 1.5 (the maturity model), MLOps 06 (best practices) and MLOps 07 (the capstone project rubric).

---

## The Microsoft MLOps maturity model (MLOps 01, section 1.5)

| Level | Name | What's automated | Typical smell |
|---|---|---|---|
| 0 | No MLOps | Nothing. Notebooks, manual deploys | "Which notebook made the production model?" |
| 1 | DevOps but no MLOps | App build, test and deploy. Not training | Releases are automated but models are thrown over the wall |
| 2 | Automated training | Training pipelines, experiment tracking, model registry | Training is reproducible; deploying a new model is still manual |
| 3 | Automated model deployment | CI/CD for models, A/B or shadow tests, model-to-service traceability | Releases are safe, but someone still decides when to retrain |
| 4 | Full MLOps automated operations | Monitoring triggers retraining and redeployment; a closed loop | Few humans in the loop. Needs strong monitoring to be safe |

The module's advice: not every project needs level 4. A proof of concept can stay at 0. A model that matters to the business should reach 2 to 3. Level 4 pays off when there are many models or data drifts quickly.

A coarser cut of the same ladder has three tiers: manual (notebooks), **continuous training** (an orchestrator retrains on a schedule, on new data or on a monitoring alert) and **CI/CD** (code changes are built, tested and deployed automatically). CT automates the pipelines. CI/CD ships new versions of the pipeline code (*LLM Engineer's Handbook*, appendix). The two loops are separate triggers, and Microsoft's level 4 is the point where both are closed.

### Where the zoomcamp takes you

| Level | Course material | Note |
|---|---|---|
| 0 → 1 | MLOps 01 notebook; MLOps 04 Dockerised service | [06](01-feature-serve.md) |
| 2 | MLflow tracking and registry (MLOps 02); orchestrated training (MLOps 03) | [06](01-feature-serve.md), [03](../../03-transform-and-orchestrate/notes/02-orchestrate.md) |
| 3 | Tests, IaC and CI/CD that deploy the Lambda (MLOps 06) | this note |
| 4 | Evidently monitoring + alerts (MLOps 05); conditional retraining is only a capstone criterion | [05](../../05-quality-and-observability/notes/01-monitor.md) |

The course gets you to a solid level 3 with monitoring attached. The closed loop of level 4 is left for the project.

---

## MLOps 06 Part A: testing and code quality

### Refactor so it can be tested

The note 06 Lambda mixed model loading, feature logic, prediction and the Kinesis write in one module-level script. MLOps 06 splits it into `model.py`:

```python
def get_model_location(run_id):
    model_location = os.getenv('MODEL_LOCATION')        # override for tests
    if model_location is not None:
        return model_location
    model_bucket = os.getenv('MODEL_BUCKET', 'mlflow-models-alexey')
    experiment_id = os.getenv('MLFLOW_EXPERIMENT_ID', '1')
    return f's3://{model_bucket}/{experiment_id}/{run_id}/artifacts/model'

class ModelService:
    def __init__(self, model, model_version=None, callbacks=None):
        self.model = model
        self.model_version = model_version
        self.callbacks = callbacks or []                # side effects are injected

    def lambda_handler(self, event):
        ...
        for callback in self.callbacks:
            callback(prediction_event)

def create_kinesis_client():
    endpoint_url = os.getenv('KINESIS_ENDPOINT_URL')    # point at LocalStack in tests
    if endpoint_url is None:
        return boto3.client('kinesis')
    return boto3.client('kinesis', endpoint_url=endpoint_url)
```

`lambda_function.py` shrinks to reading env vars, calling `model.init(...)` once at cold start, and delegating. The three seams (model location, callbacks, endpoint URL) are what make each kind of test possible.

### Unit tests with pytest

```python
def test_prepare_features():
    model_service = model.ModelService(None)            # no model needed
    actual = model_service.prepare_features(
        {"PULocationID": 130, "DOLocationID": 205, "trip_distance": 3.66})
    assert actual == {"PU_DO": "130_205", "trip_distance": 3.66}

class ModelMock:
    def __init__(self, value):
        self.value = value
    def predict(self, X):
        return [self.value] * len(X)

def test_predict():
    model_service = model.ModelService(ModelMock(10.0))
    assert model_service.predict({"PU_DO": "130_205", "trip_distance": 3.66}) == 10.0
```

`test_base64_decode` reads a fixture (`tests/data.b64`) and checks the decoded ride. `test_lambda_handler` runs the whole handler with the mock model and checks the output event. None of these touch AWS or the real model.

### What the module doesn't test: data, model, behaviour

The course's tests cover code. An ML system changes when any of code, data or model changes, so it needs tests on all three (*LLM Engineer's Handbook*, appendix):

- **Data validity**, run in the feature pipeline. For tabular data: no nulls where none are allowed, categoricals only take expected values, floats stay in range. For text: length, encoding, language, special characters. These belong next to the dbt and Mage checks in [05](../../05-quality-and-observability/notes/01-monitor.md#pipeline-side-monitoring-from-earlier-notes).
- **Model sanity**, the cheap catches for a training run that finishes without error and is still wrong. Check input and output tensor shapes. Check that loss falls after one batch. Check that the model can overfit a tiny batch to near-zero loss. Run the pipeline on every supported device (CPU and GPU) and check that early-stopping and checkpoint logic fires. These are slow, so gate them in CI on changes to model code.
- **Behaviour**, treating the model as a black box ([CheckList](https://arxiv.org/abs/2005.04118), Ribeiro et al., 2020). *Minimum functionality*: simple cases it must always get right. *Invariance*: a perturbation that shouldn't change the output (synonym swap) doesn't. *Directional*: a perturbation that should change the output does.

```python
def test_overfits_one_batch():
    model, batch = make_model(), next(iter(train_loader))
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
    for _ in range(200):
        loss = loss_fn(model(batch.x), batch.y)
        opt.zero_grad(); loss.backward(); opt.step()
    assert loss.item() < 0.05       # can't memorise 32 rows → wiring bug, not a tuning problem
```

### Integration test with docker-compose and LocalStack

```yaml
services:
  backend:
    image: ${LOCAL_IMAGE_NAME}
    ports: ["8080:8080"]
    environment:
      - PREDICTIONS_STREAM_NAME=${PREDICTIONS_STREAM_NAME}
      - RUN_ID=Test123
      - MODEL_LOCATION=/app/model                   # model from a local folder, not S3
      - KINESIS_ENDPOINT_URL=http://kinesis:4566/   # fake Kinesis
      - AWS_ACCESS_KEY_ID=abc
      - AWS_SECRET_ACCESS_KEY=xyz
    volumes: ["./model:/app/model"]
  kinesis:
    image: localstack/localstack
    ports: ["4566:4566"]
    environment: [SERVICES=kinesis]
```

`integraton-test/run.sh` (the folder name is misspelt upstream) builds the image if needed, runs `docker-compose up -d`, creates the stream with `aws --endpoint-url=http://localhost:4566 kinesis create-stream`, then runs two checks:

| Script | Checks |
|---|---|
| `test_docker.py` | POSTs `event.json` to the Lambda emulator and compares the response with `DeepDiff` |
| `test_kinesis.py` | Reads the output stream from LocalStack and asserts one record with `version: Test123`, `ride_duration: 21.3` |

On failure it prints `docker-compose logs`, tears down, and exits with the error code, so CI fails. Testing the real container against fake cloud services catches packaging, env-var and wiring bugs that unit tests miss.

### Linting, formatting and pre-commit

| Tool | Job | Config |
|---|---|---|
| `isort` | Sort imports | `pyproject.toml` |
| `black` | Format | `pyproject.toml` (line length, skip string normalisation) |
| `pylint --recursive=y` | Lint | `pyproject.toml` `[tool.pylint]`, disabling noisy checks |
| `pre-commit` | Run all of the above, plus `pytest tests/`, on every commit | `.pre-commit-config.yaml` |

```yaml
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v3.2.0
  hooks: [{id: trailing-whitespace}, {id: end-of-file-fixer}, {id: check-yaml}, {id: check-added-large-files}]
- repo: https://github.com/pycqa/isort
  rev: 5.10.1
  hooks: [{id: isort}]
- repo: https://github.com/psf/black
  rev: 22.6.0
  hooks: [{id: black, language_version: python3.11}]
- repo: local
  hooks:
    - {id: pylint, entry: pylint, language: system, types: [python], args: ["-rn", "-sn", "--recursive=y"]}
    - {id: pytest-check, entry: pytest, language: system, pass_filenames: false, always_run: true, args: ["tests/"]}
```

The pinned hook versions are from 2022. Run `pre-commit autoupdate` before reusing this, or replace isort, black and pylint with `ruff` (`ruff check` + `ruff format`), which does all three jobs faster.

### The Makefile chains it all

```makefile
LOCAL_TAG:=$(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME:=stream-model-duration:${LOCAL_TAG}

test:
	pytest tests/
quality_checks:
	isort .
	black .
	pylint --recursive=y .
build: quality_checks test
	docker build -t ${LOCAL_IMAGE_NAME} .
integration_test: build
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash integraton-test/run.sh
publish: build integration_test
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash scripts/publish.sh
setup:
	pipenv install --dev
	pre-commit install
```

The dependency chain is the point: `make publish` can't push an image that failed linting, unit tests or the integration test. The timestamp tag means each build gets a unique image.

---

## MLOps 06 Part B: infrastructure as code and CI/CD

### Terraform for the stream pipeline

```hcl
terraform {
  required_version = ">= 1.0"
  backend "s3" {                                  # remote state; create the bucket first
    bucket  = "tf-state-mlops-zoomcamp"
    key     = "mlops-zoomcamp-stg.tfstate"
    region  = "eu-west-1"
    encrypt = true
  }
}

module "source_kinesis_stream" {                  # ride_events
  source           = "./modules/kinesis"
  retention_period = 48
  shard_count      = 2
  stream_name      = "${var.source_stream_name}-${var.project_id}"
}
module "output_kinesis_stream" { ... }            # ride_predictions
module "s3_bucket"             { ... }            # model artifacts
module "ecr_image"             { ... }            # builds and pushes the image
module "lambda_function" {
  source            = "./modules/lambda"
  image_uri         = module.ecr_image.image_uri  # wiring through module outputs
  source_stream_arn = module.source_kinesis_stream.stream_arn
  output_stream_arn = module.output_kinesis_stream.stream_arn
  ...
}
output "lambda_function" { value = "${var.lambda_function_name}_${var.project_id}" }   # read by CI/CD
```

| Idea | Where it shows |
|---|---|
| Remote state in S3 | `backend "s3"`; the whole team and CI share one state |
| Modules | `modules/{kinesis,s3,ecr,lambda}`; one Kinesis module used twice |
| Environments via var files | `vars/stg.tfvars`, `vars/prod.tfvars`: `terraform apply -var-file=vars/stg.tfvars` |
| Outputs as an interface | CD reads `lambda_function`, `model_bucket`, `ecr_repo` to know what to update |

Compare the GCP Terraform in [01](../../02-ingest-and-modelling/notes/01-ingest.md): same tool, different provider. The concepts carry over.

`scripts/deploy_manual.sh` then sets the Lambda's `RUN_ID` with `aws lambda update-function-configuration --environment "Variables={...}"`. It picks the latest run by S3 `LastModified` and is marked "NOT FOR PRODUCTION!". In practice the run comes from the registry alias ([06](01-feature-serve.md)).

### CI/CD with GitHub Actions

| Workflow | Trigger | Steps |
|---|---|---|
| `ci-tests.yml` | `pull_request` to `develop` | Set up Python and pipenv; unit tests; integration test; `terraform plan` |
| `cd-deploy.yml` | `push` to `develop` | `terraform plan` + `apply`; Docker build and ECR push; update the Lambda config |

The workflow files live in the upstream repo's `.github/workflows/`, not in this snapshot. Caveats if you copy them:

| Caveat | Fix |
|---|---|
| Older Actions examples write outputs with `echo "::set-output name=x::y"`, which GitHub deprecated | `echo "x=y" >> "$GITHUB_OUTPUT"` |
| Long-lived AWS keys in repository secrets | OIDC federation (`aws-actions/configure-aws-credentials` with `role-to-assume`) |
| `develop` deploys straight to the one environment | Stage on `develop`, promote to `prod` with `vars/prod.tfvars` on `main` behind an approval |
| CD sets `RUN_ID` from "latest" | Resolve a registry alias, so promotion is a deliberate registry action |

---

## MLOps 07: the capstone rubric as a checklist

The project rubric is a good definition of "production-shaped" for a portfolio ML system:

| Criterion | Max points | Full marks means |
|---|---|---|
| Problem description | 2 | Clear problem and why ML helps |
| Cloud | 4 | Developed on the cloud and IaC used to provision it |
| Experiment tracking and model registry | 4 | Both used |
| Workflow orchestration | 4 | Fully deployed workflow |
| Model deployment | 4 | Containerised and deployable to the cloud |
| Model monitoring | 4 | Metrics calculated, with alerts or conditional retraining |
| Reproducibility | 4 | Clear instructions, pinned dependency versions, data available |
| Best practices | 7 | Unit tests 1, integration test 1, linter/formatter 1, Makefile 1, pre-commit 1, CI/CD 2 |

The "best practices" row is MLOps 06, one for one. The monitoring row is the only place the course asks for level-4 behaviour.

---

## Run labels

| Material | Needs |
|---|---|
| MLOps 01 environment setup | GitHub Codespaces or an AWS EC2 VM (Anaconda, Docker); the notebook then runs offline after the data download |
| MLOps 06 unit tests | Runs offline: `pipenv install --dev && pytest tests/` |
| MLOps 06 integration test | Docker + docker-compose; LocalStack image; no AWS account |
| MLOps 06 Terraform, `deploy_manual.sh`, `test_cloud_e2e.sh` | AWS account; S3 state bucket created beforehand |
| MLOps 06 CI/CD | GitHub repo + AWS secrets; workflows upstream only |
| MLOps 07 project | Your choice of cloud; peer-reviewed against the rubric |

---

## Rules of thumb

| Rule | Why |
|---|---|
| Inject side effects (callbacks, endpoint URLs, model location) | It's the only way to unit-test a service that writes to the cloud |
| Integration-test the real container against fake services | Catches packaging and wiring bugs; LocalStack makes it free |
| Make the Makefile the single entry point, and have CI call it | Local and CI runs can't drift |
| Pin hook and tool versions, and update them on purpose | 2022 pins rot; `pre-commit autoupdate` |
| Aim for level 2–3 before level 4 | A closed retraining loop without good monitoring automates mistakes |

---

→ Next: this is the last note in the folder. The path continues in [data science](../../../data-science/README.md), where the models these pipelines serve are built and evaluated, and in [AI engineering](../../../ai-engineering/README.md), where the same tracking, serving and monitoring patterns apply to LLM systems.
