---
origin: synthesis
sources:
  - https://github.com/DataTalksClub/mlops-zoomcamp/tree/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7/02-experiment-tracking
  - https://mlflow.org/docs/latest/ml/tracking/
  - https://mlflow.org/docs/latest/ml/model-registry/
  - https://www.manning.com/books/machine-learning-engineering-in-action
  - https://doi.org/10.1109/ICSE-SEIP.2019.00042
  - https://arxiv.org/abs/2209.09125
  - https://arxiv.org/abs/2011.09926
  - https://arxiv.org/abs/2301.11316
  - "Iusztin & Labonne, LLM Engineer's Handbook (Packt, 2024), ch. 2"
  - "Wilson, Machine Learning Engineering in Action (Manning, 2022), ch. 5-8"
confidence: high
cleaned: 2026-11-02
---
# Experiment tracking and the model registry

Six months after a model ships, someone asks why it predicted what it did, and the honest answer is that nobody knows which data it was trained on, which parameters it used, or which of a dozen files in a bucket is the one in production. Wilson tells this story about a model of his own in [*Machine Learning Engineering in Action* (Manning, 2022)](https://www.manning.com/books/machine-learning-engineering-in-action): an unsaved artifact he could not explain three months later. Two tools prevent it. An experiment tracker records every training run as it happens. A model registry names the few runs that matter and says which one is in use. Neither trains a better model. They make it possible to answer questions about the model you have, and to go back to the one you had.

The evidence that this is an engineering need, rather than tidiness, comes from the studies of working teams. [Microsoft's study by Amershi and colleagues (ICSE-SEIP 2019)](https://doi.org/10.1109/ICSE-SEIP.2019.00042), which interviewed 14 people and surveyed 551, reports teams tagging each model with its data and model version, and each dataset with its origin and code version, and it names data as harder to version than code. [Shankar and colleagues' interviews (2022)](https://arxiv.org/abs/2209.09125) put versioning next to velocity and validation as the three things that decide whether an ML effort works in production. Raissi frames the same loop as the expensive part of the workflow: the iteration step, in which experiment tracking, dataset versioning and model management all sit, is "usually the most time and resource consuming step while often being overlooked" ([arXiv:2301.11316](https://arxiv.org/abs/2301.11316) (Raissi, 2023-01, preprint)). That is an assertion in a position paper with no measurement behind it, and its cost figures (32,400 to 43,200 GPU-hours for neural architecture search on image classification) are quoted from Pham et al. and Liu et al. (2018), not measured by Raissi.

## Tracking with MLflow

MLflow is one tracker among several. The *LLM Engineer's Handbook* names W&B, MLflow, Neptune and Comet, says they have "mostly the same features", and uses Comet for training loss, evaluation loss, gradient norm and system metrics such as GPU, CPU and memory use (*LLM Engineer's Handbook*, ch. 2). What carries over is the record, not the vendor.

MLflow's tracker needs only a database, and the first experiment fits in a local SQLite file. We use the same synthetic rides as before, one function per month, and four Ridge models.

```python
import numpy as np, pandas as pd, mlflow, warnings, logging
from mlflow.tracking import MlflowClient
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error as rmse
warnings.filterwarnings("ignore")
logging.getLogger("mlflow").setLevel(logging.ERROR)

def month_of_rides(month, n=6_000, slope=3.2, seed=0):
    """Synthetic taxi rides for one month. `slope` is minutes per mile."""
    rng = np.random.default_rng(seed + month)
    d = rng.gamma(2.0, 1.6, n)
    pu, do = rng.integers(1, 21, n), rng.integers(1, 21, n)
    duration = 3 + slope * d + 0.25 * pu + rng.normal(0, 3, n)
    return pd.DataFrame({"PULocationID": pu, "DOLocationID": do,
                         "trip_distance": d.round(2),
                         "duration": duration.clip(1, 90).round(2)})

def to_dicts(df):
    return [{"PU_DO": f"{p}_{d}", "trip_distance": t} for p, d, t in
            zip(df.PULocationID, df.DOLocationID, df.trip_distance)]

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("taxi-duration")
print("mlflow", mlflow.__version__)
```

Output:

```text
mlflow 3.17.2
```

The tracker's vocabulary is small, and the distinction between its parts is the useful thing to remember:

| Logged thing | API | Use |
|---|---|---|
| Tag | `set_tag` | Who, what, why: developer, data version, ticket |
| Parameter | `log_param` | Inputs: hyperparameters, data path |
| Metric | `log_metric` | Outputs: RMSE; can be logged per step |
| Artifact | `log_artifact` | Any file: the pickled vectoriser, plots |
| Model | `mlflow.sklearn.log_model(model, name="model")` | A model in MLflow format, with a `pyfunc` loader and an environment spec |
| Everything, automatically | `mlflow.sklearn.autolog()` / `mlflow.xgboost.autolog()` | Params, metrics, model, with no manual calls |

Four rules from Wilson's experimentation chapters (experience-based advice from one author's projects, not measured results) say what to put in those calls. First, record every agreed metric on every run, so an old run can be judged again without rerunning it (*ML Engineering in Action*, ch. 5). Second, return metrics as a dictionary and log them rather than printing them, because a printed number leaves no history (*ML Engineering in Action*, ch. 6, 8). Third, when tuning runs in parallel, wrap the whole search in one parent run so each trial logs as a child; where there is no parent-child grouping, such as one model per group, custom run names and tags are the only way to search the runs later (*ML Engineering in Action*, ch. 7, 8). Fourth, lay the evaluation out once before the team splits: a chronological split with an assertion that no rows were dropped, and one function that returns all the errors.

```python
def calculate_errors(y_true, y_pred):
    """Every metric on every run; the caller logs the dict (after Wilson, ch. 6)."""
    e = np.asarray(y_true) - np.asarray(y_pred)
    return {"mae": np.abs(e).mean(), "mse": (e**2).mean(), "rmse": np.sqrt((e**2).mean()),
            "mape": 100 * np.mean(np.abs(e / np.asarray(y_true)))}
```

Tuning is where the run count explodes, which is why the logging has to be automatic. Wilson's example grid over 11 Holt-Winters hyperparameters has 2 x 2 x 4 x 2 x 4 x 4 x 4 x 2 x 2 x 2 x 2 = 32,768 combinations, about 1.9 days at 5 seconds a model (a worked example in *ML Engineering in Action*, ch. 7). He prefers Hyperopt's TPE search to a grid, and reports four airports at 400 serial iterations taking 3 hours 34 minutes on a single-core VM, and SparkTrials (600 iterations, parallelism 8, four-node cluster) taking tuning from just over 3.5 hours to just under 30 minutes (his own example, with no loss values printed to show the quality matched). Both tools have since been joined by Optuna, which he names as a successor.

```python
train, valid = month_of_rides(1), month_of_rides(2)
for alpha in [0.1, 1.0, 10.0, 100.0]:
    with mlflow.start_run(run_name=f"ridge-{alpha}"):
        mlflow.set_tag("train_data", "rides-2024-01")
        mlflow.log_param("alpha", alpha)
        model = make_pipeline(DictVectorizer(), Ridge(alpha=alpha))
        model.fit(to_dicts(train), train.duration)
        mlflow.log_metric("rmse", rmse(valid.duration, model.predict(to_dicts(valid))))
        mlflow.sklearn.log_model(model, name="model")

runs = mlflow.search_runs(order_by=["metrics.rmse ASC"])
print(runs[["params.alpha", "metrics.rmse", "tags.train_data"]].round(4).to_string(index=False))
```

Output:

```text
params.alpha  metrics.rmse tags.train_data
        10.0        3.0717   rides-2024-01
         1.0        3.0823   rides-2024-01
         0.1        3.0959   rides-2024-01
       100.0        3.2278   rides-2024-01
```

The `train_data` tag is the line most often left out and most often wanted later. A run with a metric and no record of its data cannot be compared to anything, since a better RMSE on different data is not better. Amershi's provenance tags are this idea made into a rule.

Hyperparameter search logs one run per trial, nested under a parent. This is the course's hyperopt objective, cut to eight trials. One update for anyone following the course code: its `mean_squared_error(..., squared=False)` no longer exists in current scikit-learn, and `root_mean_squared_error` replaces it.

```python
import xgboost as xgb
from hyperopt import fmin, hp, tpe, Trials, STATUS_OK
from hyperopt.pyll import scope

dv = DictVectorizer()
X_tr, X_val = dv.fit_transform(to_dicts(train)), dv.transform(to_dicts(valid))
y_val = valid.duration
dtrain, dvalid = xgb.DMatrix(X_tr, label=train.duration), xgb.DMatrix(X_val, label=y_val)

def objective(params):
    with mlflow.start_run(nested=True):
        mlflow.set_tag("model", "xgboost")
        mlflow.log_params(params)
        booster = xgb.train(params=params, dtrain=dtrain, num_boost_round=100,
                            evals=[(dvalid, 'validation')], early_stopping_rounds=10,
                            verbose_eval=False)
        score = rmse(y_val, booster.predict(dvalid))
        mlflow.log_metric("rmse", score)
    return {'loss': score, 'status': STATUS_OK}

search_space = {"max_depth": scope.int(hp.quniform("max_depth", 2, 6, 1)),
                "learning_rate": hp.loguniform("learning_rate", -3, 0),
                "objective": "reg:squarederror"}
with mlflow.start_run(run_name="xgboost-search"):
    best_params = fmin(fn=objective, space=search_space, algo=tpe.suggest,
                       max_evals=8, trials=Trials(), show_progressbar=False,
                       rstate=np.random.default_rng(1))
print({k: round(float(v), 3) for k, v in best_params.items()})
```

Output:

```text
{'learning_rate': 0.362, 'max_depth': 3.0}
```

Then compare runs in the UI (`mlflow ui --backend-store-uri sqlite:///mlflow.db`): parallel coordinates for hyperparameters against RMSE, sorted tables, and per-run artifacts. The value is mostly in the first weeks of a project. In the interview study, tracking is described as a virtue of velocity: it makes it quick to see what has been tried ([Shankar et al., 2022](https://arxiv.org/abs/2209.09125)).

### Three ways to run the tracking server

| Scenario | Backend store | Artifact store | Command | Fits |
|---|---|---|---|---|
| 1. Local, no server | Local files | Local folder | None, the default | Solo experiments |
| 2. Local server | `sqlite:///backend.db` | Local folder | `mlflow server --backend-store-uri sqlite:///backend.db` | Solo, but with the registry, which needs a database backend |
| 3. Remote | Postgres on RDS | S3 bucket | `mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://USER:PASS@HOST:5432/DB --default-artifact-root s3://BUCKET` on EC2 | A team; the course's services load models from this S3 path |

The course folder [`02-experiment-tracking/running-mlflow-examples/`](https://github.com/DataTalksClub/mlops-zoomcamp/tree/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7/02-experiment-tracking/running-mlflow-examples) has a notebook for each scenario; [`mlflow_on_aws.md`](https://github.com/DataTalksClub/mlops-zoomcamp/blob/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7/02-experiment-tracking/mlflow_on_aws.md) covers the EC2, RDS and S3 setup. The second scenario is the code in this chapter and needs no server, because MLflow can open the SQLite file directly. The third needs an AWS account and was not run here.

## From a run to a model

A run is a record of something that happened. A registered model is a decision that one of those runs matters. The registry keeps a name, numbered versions that point at runs, and movable labels on them ([MLflow's docs](https://mlflow.org/docs/latest/ml/model-registry/)).

```mermaid
flowchart LR
  R1[Run: alpha 10] -->|register| V1[taxi-duration v1]
  R2[Run: retrain March] -->|register| V2[taxi-duration v2]
  R3[Run: retrain May] -->|register| V3[taxi-duration v3]
  A["@champion alias"] -.-> V3
  S[Service loads models:/taxi-duration@champion] --> A
```

| Concept | Meaning |
|---|---|
| Run | One training execution with params, metrics, artifacts |
| Registered model | A named model; versions point at runs |
| Stage (legacy) | `None` / `Staging` / `Production` / `Archived`; one fixed lifecycle, deprecated since MLflow 2.9 |
| Alias (current) | A movable named pointer (`champion`, `challenger`) to a version; as many as you need |

The registry is one case of a wider idea. The Handbook defines an artifact as any file the ML lifecycle produces, such as a dataset, model, checkpoint or log, and names three properties: artifacts are versioned, shareable and carry metadata. A model registry is "a particular use case for an artifact" (*LLM Engineer's Handbook*, ch. 2). The metadata exists so you can tell what an artifact holds without downloading it. On a dataset that means its size, train-test split and label types (ch. 2). That is the same reason this chapter tags every run with its training data. The authors keep their models on the Hugging Face Hub, although ZenML, Comet and SageMaker each offer a registry too, and their rule is to pick the one that integrates best with the rest of your tooling (ch. 2).

```python
client = MlflowClient()
best = runs.iloc[0]
uri = f"runs:/{best.run_id}/model"
v1 = mlflow.register_model(uri, "taxi-duration")
client.set_registered_model_alias("taxi-duration", "champion", v1.version)
client.set_model_version_tag("taxi-duration", v1.version, "train_data", "rides-2024-01")
loaded = mlflow.pyfunc.load_model("models:/taxi-duration@champion")
mv = client.get_model_version_by_alias("taxi-duration", "champion")
print("version", mv.version, "from run", mv.run_id == best.run_id)
print("prediction", loaded.predict(to_dicts(valid.head(1))).round(2))
```

Output:

```text
version 1 from run True
prediction [13.59]
```

If you follow the course's code you will see `client.transition_model_version_stage(name=..., version=4, stage="Staging")`. That is the stages API. It still appears in older material; the alias is the current equivalent, and it is what this chapter uses.

Now look at what a logged model actually contains, because this is what lets a model be loaded a year from now on a different machine:

```python
import mlflow.artifacts as ma
for f in ma.list_artifacts(f"models:/taxi-duration/1"):
    print(f.path)
reqs = open(ma.download_artifacts("models:/taxi-duration/1/requirements.txt")).read().split()
print(reqs[:3])
```

Output:

```text
MLmodel
conda.yaml
model.skops
python_env.yaml
registered_model_meta
requirements.txt
['mlflow==3.17.2', 'numpy==2.5.4', 'pandas==3.1.0']
```

`MLmodel` describes how to load it, `model.skops` is the serialised model in this MLflow version, and the three environment files pin what it needs. Log an sklearn `Pipeline` and the fitted vectoriser travels with it, which removes one common form of [skew](01-feature-stores.md).

## The gate: passive retraining

The registry's real use appears with the second model. Wilson calls the simple approach passive retraining (*ML Engineering in Action*, ch. 16): on a schedule, train a new model, compare it against production on a holdout, and promote it only if it wins. He prefers it over anything more elaborate until it fails. The comparison needs to use data newer than either model's training set, so neither gets credit for having seen it:

```python
def train_and_log(month, alpha=float(best["params.alpha"]), slope=3.2):
    df = month_of_rides(month, slope=slope)
    with mlflow.start_run(run_name=f"retrain-{month:02d}") as run:
        mlflow.set_tag("train_data", f"rides-2024-{month:02d}")
        mlflow.log_param("alpha", alpha)
        m = make_pipeline(DictVectorizer(), Ridge(alpha=alpha))
        m.fit(to_dicts(df), df.duration)
        mlflow.sklearn.log_model(m, name="model")
    return run.info.run_id

def champion_version():
    return client.get_model_version_by_alias("taxi-duration", "champion").version

def promote_if_better(run_id, holdout, min_gain=0.0):
    """Passive retraining gate: register always, move the alias only on a win."""
    champion = mlflow.pyfunc.load_model("models:/taxi-duration@champion")
    challenger = mlflow.pyfunc.load_model(f"runs:/{run_id}/model")
    x = to_dicts(holdout)
    c = rmse(holdout.duration, champion.predict(x))
    n = rmse(holdout.duration, challenger.predict(x))
    v = mlflow.register_model(f"runs:/{run_id}/model", "taxi-duration").version
    verdict = "kept champion"
    if n < c - min_gain:
        client.set_registered_model_alias("taxi-duration", "champion", v)
        verdict = "promoted"
    print(f"v{v}: champion {c:.3f} vs challenger {n:.3f} -> {verdict}")

# March: nothing has changed, so a retrain wins nothing.
promote_if_better(train_and_log(3), month_of_rides(4))
# May onwards: traffic slows and a mile costs more.
promote_if_better(train_and_log(5, slope=4.0), month_of_rides(6, slope=4.0))
print(f"champion is now v{champion_version()}")
```

Output:

```text
v2: champion 3.044 vs challenger 3.054 -> kept champion
v3: champion 4.456 vs challenger 3.060 -> promoted
champion is now v3
```

The March retrain was trained on an unchanged world and gets 3.054 against the champion's 3.044, so it is not promoted, even though it was trained on newer data. Without a gate, you would have shipped a model that was slightly worse and learned nothing. By May a mile costs more, the champion falls to 4.456, and the challenger wins clearly. Both versions stay registered, including the loser, since it is evidence about what was tried.

Note the limits of this gate. A single metric on a single holdout does not catch a model that wins on average and fails badly on one slice, and the offline metric may not move the thing you care about: [Paleyes, Urma and Lawrence's survey (ACM Computing Surveys, 2022)](https://arxiv.org/abs/2011.09926) reports Booking.com's experience across 150 models that offline gains did not translate directly to business value. So the gate decides what is allowed to proceed to a [staged rollout](03-batch-and-online-serving.md#rolling-out-a-new-model), not what users get.

A classifier's gate needs the same discipline as an LLM's: score both models on the same rows, set a floor for the never-events, and treat a small win as noise until a paired test says otherwise. [Evals in CI](../../../generative-ai/08-eval/notes/10-evals-in-ci.md#the-regression-gate) builds that gate, so reuse it and change only the metric.

Paleyes also cites work on update compatibility that deserves a thought here: a more accurate update can still hurt when people have learned how the old model behaves, as Bansal and colleagues showed for human and AI teams. A new champion is not automatically a better colleague.

## Rollback, and why the registry labels but does not deploy

```python
client.set_registered_model_alias("taxi-duration", "champion", 1)
print(f"champion back to v{champion_version()}")
for v in client.search_model_versions("name='taxi-duration'",
                                      order_by=["version_number ASC"]):
    print(f"v{v.version} trained on", client.get_run(v.run_id).data.tags["train_data"])
```

Output:

```text
champion back to v1
v1 trained on rides-2024-01
v2 trained on rides-2024-03
v3 trained on rides-2024-05
```

Moving the alias takes one line and needs no retraining, and the listing tells you what each version was trained on. This is Wilson's point: months later you can recover the artifact from week 25, and know what it was. In ch. 16 he says that with a registry a historic problem takes "no more than an hour" to trace, against hunting for an old model or retraining on data that may have changed. The hour is an illustration in his Fig. 16.3, not a measurement. His Listing 16.3 moves versions between `Production` and `Archived` stages and logs each change to an append-only status table (model name, production version, update time, training time), where this note uses aliases. The idea carries over: the registry keeps what ran, and the log keeps when it changed.

![Six weekly model versions, then a week-25 issue traced with a registry in an hour or without one by painful reconstruction](../../sources/images/ml-engineering-in-action-fig16-3.png)
*Image Source: Ben Wilson, *Machine Learning Engineering in Action* (Manning, 2022), Fig. 16.3*

But **the registry labels; it doesn't deploy.** Moving the `champion` alias changes nothing in production by itself. A CI/CD pipeline, or a service that resolves the alias at startup, does the deploying ([the maturity chapter](05-mlops-maturity-and-best-practices.md)). That gap matters in an incident: a service that loaded at startup keeps running the old model until something restarts it. Your rollback runbook has to include that step.

The course's services load by `RUN_ID` from S3, which pins an exact artifact and sidesteps the registry altogether. That is a real choice with a real trade-off:

| Load by | URI | Promotion means | Good | Bad |
|---|---|---|---|---|
| Run ID | `runs:/<id>/model`, or the S3 path | A redeploy with a new env var | Exact and reproducible; no runtime dependency on the tracking server if you load straight from S3 | The deploy pipeline carries the decision |
| Version | `models:/taxi-duration/3` | A redeploy with a new version number | Exact, and named | Same |
| Alias | `models:/taxi-duration@champion` | Moving the alias, then a restart or reload | Promotion is a deliberate registry action | What is running depends on when it started, so log the resolved version |

Whichever you use, return the version with each prediction, as the [serving chapter](03-batch-and-online-serving.md) does. Without it, nobody can tie a bad prediction back to a model.

One service can also serve many customers with one model and [a different offset or threshold for each](../../../data-science/01-classical-ml/notes/13-automate-review-or-reject.md#when-customers-differ). Then the version alone doesn't say what decided a case. Version those per-customer values too, and log them with each prediction, since rolling back the model without them changes what they mean.

## Choosing the run

The selection rule from the course is two steps: filter on the quality metric, then break ties on operational cost, such as model size and prediction latency. MLflow writes `model_size_bytes` into each model's `MLmodel` file in the version tested here; latency it records only if you measure it and log it as a metric.

```python
candidates = mlflow.search_runs(filter_string="metrics.rmse < 3.1 and params.alpha != ''",
                                order_by=["metrics.rmse ASC"])
print(len(candidates), "runs pass the quality bar of 3.1")
print(candidates[["params.alpha", "metrics.rmse"]].round(4).to_string(index=False))
```

Output:

```text
3 runs pass the quality bar of 3.1
params.alpha  metrics.rmse
        10.0        3.0717
         1.0        3.0823
         0.1        3.0959
```

These three are within 0.025 minutes of each other, about a second and a half on a typical ride. In practice that is a tie, and the simplest or cheapest one should win. Treating the top of a sorted table as the answer is how a team ends up running a complicated model for no measured gain. Paleyes's survey has the extreme case: Airbnb's search team found that a complex deep model failed, and got moving by simplifying to a network with one hidden layer of 32 units, largely so they could build the pipeline around it.

## Run labels

Course paths are as they stood at [upstream commit `e34bf8f`](https://github.com/DataTalksClub/mlops-zoomcamp/tree/e34bf8f540b75dfd712ffcc97d3c000ae1c2e3e7), the version these chapters read.

| Material | Needs |
|---|---|
| Course `01-intro/duration-prediction.ipynb` | Runs offline after downloading the Parquet files |
| Course `02-experiment-tracking` notebooks, scenarios 1 and 2 | `mlflow`, `hyperopt`, `xgboost`; runs offline |
| Course scenario 3, `mlflow_on_aws.md` | AWS account (EC2, RDS, S3) |
| The code in this chapter | `uv run --with mlflow --with pandas --with scikit-learn --with xgboost --with hyperopt --with setuptools python file.py`; tested on MLflow 3.17 |

## Pitfalls

- **No data version on the run.** A metric without its data cannot be compared. Log the data path or hash as a tag every time.
- **Comparing on different holdouts.** Two RMSE values from two runs are comparable only if they were computed on the same rows. The gate above scores both models on the same holdout at decision time, rather than trusting logged numbers.
- **Holdout older than the training data.** The challenger has seen it and the champion has not, or the reverse. Use a window newer than both.
- **Promoting on a tie.** A difference of 0.01 minutes is noise. Set `min_gain` to something you would defend.
- **Assuming the alias moved production.** It moved a pointer. Know how your service picks up a change.
- **Deleting the losers.** Failed candidates record what was tried, and the versions behind today's champion are your rollback.
- **Copying stage-based tutorials.** Stages are deprecated in MLflow. Use aliases on new work.
- **Pickle across versions.** Unpickling under a different library version can fail or misbehave. The environment files exist to prevent this, so load in the logged environment.

## Try it

1. Set `min_gain=0.5` in `promote_if_better` and rerun. Does the May challenger still win? What does `min_gain` protect against, and what does it cost?
2. Add a `challenger` alias and have `promote_if_better` set it on every run, moving `champion` only on a win. What can a service do with both aliases?
3. Read `model_size_bytes` from `MLmodel`, log it as a metric, and change the selection to choose the smallest model within 0.05 of the best RMSE. Which alpha do you get?

<details><summary>Answers</summary>

1. It does, since the gain is about 1.4 minutes. A `min_gain` protects against churn from noise; the cost is that a run of small true gains is never promoted, so it may need checking against the champion's age too.
2. It can shadow: send every request to both, return the champion's answer, and log the challenger's. That is the rollout pattern in the next chapter.
3. Ridge models on the same vocabulary are very nearly the same size, so the size test is not decisive here, and the selection falls to whichever rule you use next. The exercise is really about noticing that a tie-break needs a metric that differs between candidates.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What is the difference between a run and a registered model version? | A run records one training execution. A version is a named, numbered pointer to a run that someone decided matters |
| What must you log so that a run can be reproduced? | Code version, data version, parameters, metrics, the model artifact and its environment |
| Stage or alias? | Alias. Stages are one fixed lifecycle, deprecated since MLflow 2.9. Aliases are as many movable pointers as you need |
| Does moving `@champion` change production? | Only if something resolves it again. The registry labels; a pipeline or a restart deploys |
| Run ID or alias in the service? | Run ID pins exactly and promotion is a redeploy. Alias makes promotion a registry action, but you must log which version was resolved |
| What is passive retraining? | Retrain on a schedule, compare against production on a newer holdout, and promote only on a win |
| Why keep the versions that lost? | Rollback, audit, and a record of what was tried |

## Next

[Batch and online serving](03-batch-and-online-serving.md): the registry says which model. Next, how it reaches the people and systems that need its answers.
