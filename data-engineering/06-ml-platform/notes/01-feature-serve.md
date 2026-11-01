---
origin: course-synthesis
sources:
  - https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/01-intro
  - https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/02-experiment-tracking
  - https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/04-deployment
  - https://mlflow.org/docs/latest/model-registry.html
  - https://docs.aws.amazon.com/lambda/latest/dg/with-kinesis.html
confidence: high
cleaned: 2026-10-31
---
# 6 — Feature-serve

> Build features the same way at training and serving time, track every training run, register the model you ship, and deploy it in one of three shapes: a web service, a stream consumer, or a batch job.

---

## Where it sits

Foundation 6 of 6, where data engineering hands off to the model. The tables from [04](../../04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md) become training sets. The run that wins becomes a registered model. The model becomes a service whose outputs [05](../../05-quality-and-observability/notes/01-monitor.md) watches. The zoomcamp material is MLOps 01 (the baseline model), MLOps 02 (MLflow tracking and registry) and MLOps 04 (deployment).

---

## The feature, and why it lives in one function

The MLOps 01 baseline predicts NYC green-taxi ride duration:

```python
df['duration'] = (df.lpep_dropoff_datetime - df.lpep_pickup_datetime).dt.total_seconds() / 60
df = df[(df.duration >= 1) & (df.duration <= 60)]           # drop outliers
df[['PULocationID', 'DOLocationID']] = df[['PULocationID', 'DOLocationID']].astype(str)
df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']   # pickup × dropoff pair

dv = DictVectorizer()
X_train = dv.fit_transform(df[['PU_DO', 'trip_distance']].to_dict(orient='records'))
lr = LinearRegression().fit(X_train, df.duration.values)

with open('models/lin_reg.bin', 'wb') as f_out:
    pickle.dump((dv, lr), f_out)                             # vectoriser and model together
```

Every serving path in MLOps 04 then repeats the feature logic in a `prepare_features` function:

```python
def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features
```

| Practice | Why |
|---|---|
| Pickle `(dv, lr)` together, or log an sklearn `Pipeline` | The fitted vocabulary of `PU_DO` values is part of the model; ship it with the model |
| One `prepare_features` used by training, batch, web and stream | Otherwise you get **train/serve skew**: the same ride produces different features in two code paths |
| Test `prepare_features` directly | MLOps 06's first unit test does exactly this ([08](02-mlops-maturity-and-best-practices.md)) |

The zoomcamp has no feature store. When features are shared across models and teams (the "who owns feature engineering code?" scenario in [07](../../07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md)), a feature store such as Feast stores the definitions once and serves them offline for training and online for inference. That's beyond this material.

---

## Experiment tracking with MLflow (MLOps 02)

```python
import mlflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("nyc-taxi-experiment")

with mlflow.start_run():
    mlflow.set_tag("developer", "cristian")
    mlflow.log_param("train-data-path", "./data/green_tripdata_2021-01.csv")
    alpha = 0.1
    mlflow.log_param("alpha", alpha)
    lr = Lasso(alpha).fit(X_train, y_train)
    rmse = mean_squared_error(y_val, lr.predict(X_val), squared=False)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_artifact(local_path="models/lin_reg.bin", artifact_path="models_pickle")
```

| Logged thing | API | Use |
|---|---|---|
| Tag | `set_tag` | Who/what/why: developer, data version, ticket |
| Parameter | `log_param` | Inputs: hyperparameters, data path |
| Metric | `log_metric` | Outputs: RMSE; can be logged per step |
| Artifact | `log_artifact` | Any file: the pickled vectoriser, plots |
| Model | `mlflow.xgboost.log_model(booster, artifact_path="models_mlflow")` | A model in MLflow format with a `pyfunc` loader and an environment spec |
| Everything, automatically | `mlflow.sklearn.autolog()` / `mlflow.xgboost.autolog()` | Params, metrics, model, with no manual calls |

Hyperparameter search with hyperopt logs one nested run per trial:

```python
def objective(params):
    with mlflow.start_run():
        mlflow.set_tag("model", "xgboost")
        mlflow.log_params(params)
        booster = xgb.train(params=params, dtrain=train, num_boost_round=1000,
                            evals=[(valid, 'validation')], early_stopping_rounds=50)
        rmse = mean_squared_error(y_val, booster.predict(valid), squared=False)
        mlflow.log_metric("rmse", rmse)
    return {'loss': rmse, 'status': STATUS_OK}

best_result = fmin(fn=objective, space=search_space, algo=tpe.suggest,
                   max_evals=50, trials=Trials())
```

Then compare runs in the UI (`mlflow ui --backend-store-uri sqlite:///mlflow.db`): parallel coordinates for hyperparameters against RMSE, sorted tables, and per-run artifacts.

### Three ways to run the tracking server

| Scenario | Backend store | Artifact store | Command | Fits |
|---|---|---|---|---|
| 1. Local, no server | `./mlruns` files | `./mlruns` | none, the default | Solo experiments |
| 2. Local server | `sqlite:///backend.db` | Local folder | `mlflow server --backend-store-uri sqlite:///backend.db` | Solo, but with the registry (needs a DB backend) |
| 3. Remote | Postgres on RDS | S3 bucket | `mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://USER:PASS@HOST:5432/DB --default-artifact-root s3://BUCKET` on EC2 | A team; the MLOps 04 services load models from this S3 path |

`running-mlflow-examples/scenario-{1,2,3}.ipynb` walk through each; `mlflow_on_aws.md` is the EC2 + RDS + S3 setup.

---

## The model registry

```python
from mlflow.tracking import MlflowClient
client = MlflowClient(tracking_uri="sqlite:///mlflow.db")

runs = client.search_runs(experiment_ids='1',
                          filter_string="metrics.rmse < 7",
                          run_view_type=ViewType.ACTIVE_ONLY,
                          max_results=5, order_by=["metrics.rmse ASC"])

mlflow.register_model(model_uri=f"runs:/{run_id}/model", name="nyc-taxi-regressor")

# course code (stages, deprecated since MLflow 2.9):
client.transition_model_version_stage(name="nyc-taxi-regressor", version=4,
                                      stage="Staging", archive_existing_versions=False)
# current equivalent (aliases):
client.set_registered_model_alias(name="nyc-taxi-regressor", alias="champion", version=4)

model = mlflow.pyfunc.load_model("models:/nyc-taxi-regressor@champion")
```

| Concept | Meaning |
|---|---|
| Run | One training execution with params, metrics, artifacts |
| Registered model | A named model; versions point at runs |
| Stage (legacy) | `None` / `Staging` / `Production` / `Archived`; one fixed lifecycle |
| Alias (current) | A movable named pointer (`champion`, `challenger`) to a version; as many as you need |

**The registry labels; it doesn't deploy.** Moving the `champion` alias changes nothing in production by itself. A CI/CD pipeline or a service that resolves the alias at startup does the deploying ([08](02-mlops-maturity-and-best-practices.md)). The course services load by `RUN_ID` from S3, which pins an exact artifact and sidesteps the registry entirely. That's simpler and reproducible, but promotion then means a redeploy with a new env var.

Selection rule from the module: filter on the quality metric, then break ties on operational cost (model size, prediction latency), both of which MLflow records.

---

## Deployment: three shapes (MLOps 04)

| Shape | Latency | Trigger | Course code | Output |
|---|---|---|---|---|
| **Web service** | Milliseconds, synchronous | HTTP request | `web-service/`, `web-service-mlflow/` | JSON response |
| **Streaming** | Seconds, asynchronous | Event on a stream | `streaming/` (Kinesis → Lambda → Kinesis) | Event on an output stream |
| **Batch** | Minutes to hours | Schedule | `batch/` (Prefect) | Parquet partition in S3 |

Pick by when the consumer needs the answer. The ride-duration estimate a rider sees is synchronous. A backend that reacts to predictions (dispatch, pricing) can be a stream consumer. Monthly analytics on predicted vs actual is batch.

### Web service: Flask + gunicorn in Docker

```python
app = Flask('duration-prediction')

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()
    features = prepare_features(ride)
    pred = predict(features)                 # dv.transform → model.predict
    return jsonify({'duration': pred})
```

```dockerfile
FROM python:3.11-slim
RUN pip install -U pip && pip install pipenv
WORKDIR /app
COPY [ "Pipfile", "Pipfile.lock", "./" ]
RUN pipenv install --system --deploy
COPY [ "predict.py", "lin_reg.bin", "./" ]
EXPOSE 9696
ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "predict:app" ]
```

`pipenv install --system --deploy` fails the build if `Pipfile.lock` is out of date, so the image has exactly the locked versions. `app.run(debug=True)` is for local only; gunicorn serves in the container.

The MLflow variant loads the model from the tracking server's artifact store and returns which model answered:

```python
RUN_ID = os.getenv('RUN_ID')
logged_model = f's3://mlflow-models-alexey/1/{RUN_ID}/artifacts/model'   # or f'runs:/{RUN_ID}/model'
model = mlflow.pyfunc.load_model(logged_model)
...
return jsonify({'duration': pred, 'model_version': RUN_ID})
```

Loading straight from S3 removes the runtime dependency on the tracking server: if MLflow is down, the service still starts. Returning `model_version` is what lets monitoring join predictions to the model that made them.

### Streaming: Kinesis → Lambda → Kinesis

```python
def lambda_handler(event, context):
    predictions_events = []
    for record in event['Records']:
        decoded_data = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        ride_event = json.loads(decoded_data)
        ride, ride_id = ride_event['ride'], ride_event['ride_id']
        prediction = predict(prepare_features(ride))
        prediction_event = {'model': 'ride_duration_prediction_model', 'version': '123',
                            'prediction': {'ride_duration': prediction, 'ride_id': ride_id}}
        if not TEST_RUN:
            kinesis_client.put_record(StreamName=PREDICTIONS_STREAM_NAME,
                                      Data=json.dumps(prediction_event),
                                      PartitionKey=str(ride_id))
        predictions_events.append(prediction_event)
    return {'predictions': predictions_events}
```

| Detail | Why |
|---|---|
| `event['Records']` loop | Lambda receives Kinesis records in batches |
| `base64.b64decode` | Kinesis delivers payloads base64-encoded |
| `PartitionKey=str(ride_id)` | Same role as a Kafka key ([01](../../02-ingest-and-modelling/notes/01-ingest.md)): ordering per ride |
| `TEST_RUN` flag | Run the handler locally without writing to AWS; MLOps 06 replaces this with an injectable callback |
| Container image `public.ecr.aws/lambda/python:3.11` | Lambda's 250 MB zip limit is too small for mlflow + sklearn |

```bash
docker build -t stream-model-duration:v1 .
docker run -it --rm -p 8080:8080 -e PREDICTIONS_STREAM_NAME="ride_predictions" \
  -e RUN_ID="..." -e TEST_RUN="True" -e AWS_DEFAULT_REGION="eu-west-1" stream-model-duration:v1
# local invoke
curl -X POST localhost:8080/2015-03-31/functions/function/invocations -d @event.json

aws kinesis put-record --stream-name ride_events --partition-key 1 --cli-binary-format raw-in-base64-out \
  --data '{"ride": {"PULocationID": 130, "DOLocationID": 205, "trip_distance": 3.66}, "ride_id": 156}'
SHARD_ITERATOR=$(aws kinesis get-shard-iterator --stream-name ride_predictions \
  --shard-id shardId-000000000000 --shard-iterator-type TRIM_HORIZON --query 'ShardIterator' --output text)
aws kinesis get-records --shard-iterator $SHARD_ITERATOR
```

Then push the image to ECR and point a Lambda at it with a Kinesis trigger. MLOps 06 turns this whole setup into Terraform ([08](02-mlops-maturity-and-best-practices.md)).

### Batch scoring

The Prefect flow that reads a month of trips from S3, loads the model by `RUN_ID`, and writes `taxi_type=/year=/month=/{run_id}.parquet` is worked through in [03](../../03-transform-and-orchestrate/notes/02-orchestrate.md), because its lessons (logical dates, deterministic output paths, backfills) are orchestration lessons. Its output rows carry `actual_duration`, `predicted_duration`, `diff` and `model_version`, which makes the batch output a monitoring table for free. The Spark version of batch scoring is `mapPartitions` in [04](../../04-warehouse-lakehouse-streaming/notes/01-warehouse-and-store.md).

---

## Run labels

| Material | Needs |
|---|---|
| MLOps 01 `duration-prediction.ipynb` | Runs offline after downloading the Parquet files |
| MLOps 02 notebooks, scenarios 1–2 | `mlflow`, `hyperopt`, `xgboost`; runs offline |
| MLOps 02 scenario 3, `mlflow_on_aws.md` | AWS account (EC2, RDS, S3) |
| MLOps 04 `web-service/` | Docker; runs offline with the bundled `lin_reg.bin` |
| MLOps 04 `web-service-mlflow/` | MLflow artifacts in S3 + AWS credentials |
| MLOps 04 `streaming/` | Docker for the local Lambda emulator; AWS Kinesis, ECR, Lambda for the real thing |
| MLOps 04 `batch/` | Legacy: Prefect 2 + S3 |

---

→ Next: [07-data-architectures-mesh-fabric-mdw.md](../../07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw.md) — the six foundations describe one pipeline; the next note asks how an organisation arranges many of them and who owns each part.
