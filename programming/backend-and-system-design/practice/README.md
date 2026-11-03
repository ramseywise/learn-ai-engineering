# Lab: backend parts you can test without a data centre

> Eleven small modules, each one the core of something from the chapters: a signed cursor, a JWT verifier, single flight, an outbox, rate limiters, a hash ring, Erlang C, a retry budget and breaker, a lease scheduler, a log-structured store, and a token budget. Plus a small service that goes through a real container build and a real SIGTERM.

Each module goes with a chapter, so do it after reading that one. None of it is for production: use a maintained library for JWTs, and a real database for storage. The point is that you can see what each piece must get right.

## Run it

You need Python 3.14 and [uv](https://docs.astral.sh/uv/). `deploy/verify.sh` also needs a running Docker daemon, and `check.sh` skips it with a message if there isn't one. Nothing here uses a cloud account. From this folder:

```bash
bash check.sh              # the worked lab, every code block in the chapters, and the deploy example
bash check.sh exercises    # your copy of the lab. It fails until you've written it
```

```text
ok    solutions/backend_lab/  (99 passed in 13.13s)
ok    01-api-design.md  (5 blocks ran, 4 compared exactly, 2 s)
ok    02-auth-sessions-jwt-oauth.md  (6 blocks ran, 5 compared exactly, 1 s)
ok    03-caching-and-queues.md  (6 blocks ran, 6 compared exactly, 2 s)
ok    04-load-balancing-and-rate-limiting.md  (5 blocks ran, 4 compared exactly, 6 s)
ok    05-estimation-and-scaling.md  (6 blocks ran, 5 compared exactly, 12 s)
ok    06-containers-cicd-and-deployment.md  (5 blocks ran, 5 compared exactly, 1 s)
ok    07-reliability-under-load.md  (10 blocks ran, 10 compared exactly, 1 s)
ok    08-design-walkthroughs-rate-limiter-notifications-scheduler.md  (8 blocks ran, 8 compared exactly, 1 s)
ok    09-design-walkthroughs-kv-store-and-feed.md  (7 blocks ran, 7 compared exactly, 1 s)
ok    10-ai-system-reference-architecture.md  (8 blocks ran, 8 compared exactly, 1 s)
66 blocks passed, 0 failed
== manifests (parsed and checked, never deployed)
  (14 lines, all "ok")
== build (the test stage must pass for the image to exist)
  built; size 44 MB
  user: 65534:65534
  tests are not in the final image
== SIGTERM during a 2 s request, exec form (python is PID 1)
  stop took 2s, exit code 0, running request got HTTP 200
== the same, with a shell as PID 1 (grace period 4 s)
  stop took 5s, exit code 137, running request got HTTP 200
verify OK
```

That's CPython 3.14.7, uv 0.12.8 and Docker 29.7.2 on an Apple M4 Pro. The stop times in the last lines change a little between runs, so read them as "about". The first run downloads pytest, the optional packages below and the base image. `check.sh` removes the `.venv` and caches when it finishes. Untouched, `bash check.sh exercises` reports 98 of the 99 tests failing, which is the starting point. The one that passes checks `stable_hash`, which is given.

## What's checked in the notes

`run_notes.py` runs each Python block in `notes/` in its own temporary folder, and a block has to exit cleanly. Where a block's output is fixed by a seed or by arithmetic, the printed output has to match the chapter exactly. Where it's a timing, marked `<!-- measured -->` above the output, only the exit is checked.

A `<!-- requires: x -->` marker adds a package for that block only: `graphql` (graphql-core), `grpc` (grpcio and grpcio-tools), `otel` (opentelemetry-sdk) or `pyjwt` (PyJWT). Use `--only 05` to run one chapter, and `--list` to see the blocks.

## What you're given

`exercises/backend_lab/` holds the stubs and tests. `solutions/backend_lab/` has the same tests and worked versions.

| File | What you build | After | What the tests pin |
|---|---|---|---|
| `cursor.py` | A signed keyset cursor and `paginate` | [Chapter 1](../notes/01-api-design.md#pagination-that-holds-still) | Every row once across ties, an exact final page, inserts at the top, a tampered cursor rejected |
| `jwt_verify.py` | A strict HS256 verifier | [Chapter 2](../notes/02-auth-sessions-jwt-oauth.md) | The RFC 7515 vector, `alg: none`, a wrong audience, expiry at the exact second, a wrong type |
| `single_flight.py` | One loader per key | [Chapter 3](../notes/03-caching-and-queues.md#the-stampede) | One load for many callers, the leader's exception reaching every waiter |
| `outbox.py` | The outbox and an idempotent consumer | [Chapter 3](../notes/03-caching-and-queues.md#the-outbox-a-write-and-a-message-together) | Both rows or neither, a broker outage, a redelivery applied once |
| `limiters.py` | Five limiters, with the clock passed in | [Chapter 4](../notes/04-load-balancing-and-rate-limiting.md#five-ways-to-count-requests) | The fixed-window boundary burst, window edges, refill caps |
| `hash_ring.py` | A ring with virtual nodes | [Chapter 4](../notes/04-load-balancing-and-rate-limiting.md#hashing-keys-to-nodes) | Only about one share of keys moving, moved keys going only to the new node, distinct replicas |
| `erlang.py` | `erlang_c`, `wait`, `size_for` | [Chapter 5](../notes/05-estimation-and-scaling.md) | Agreement with the direct formula, no overflow at 5,000 workers, overload, the smallest size |
| `retry_budget.py` | `RetryBudget`, `Breaker` | [Chapter 7](../notes/07-reliability-under-load.md#retrying-responsibly) | A 10% ratio under total failure, one half-open trial, a full cool-down after a failed trial |
| `lease_scheduler.py` | `LeaseScheduler` on SQLite | [Chapter 8](../notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md#scheduler-leases-and-fencing) | A double fire, a stale finish, heartbeat renewal, a poison job |
| `mini_kv.py` | `MiniKV`, a log-structured store | [Chapter 9](../notes/09-design-walkthroughs-kv-store-and-feed.md#one-node-a-log-structured-store) | Recovery with a torn log line, tombstones surviving a flush, newest table wins, compaction |
| `token_budget.py` | Reservations per tenant | [Chapter 10](../notes/10-ai-system-reference-architecture.md#why-reserve-first) | No overspending under concurrency, settle and release, a window that resets on your clock |

## The deploy example

[`deploy/`](deploy/) goes with [chapter 6](../notes/06-containers-cicd-and-deployment.md). It holds a small standard-library HTTP service with a drain on SIGTERM, a multi-stage `Dockerfile` whose build fails if the tests fail, a Kubernetes manifest and a CI workflow.

`deploy/verify.sh` builds the image, checks its size and user, confirms that tests aren't in it, and sends SIGTERM during a slow request, once with the service as PID 1 and once behind a shell. It removes its own image and containers when it finishes.

Some of it could only be read, not run:

- **The Kubernetes manifest was never applied.** There's no cluster here, and `kubectl apply --dry-run=client` with `--validate=false` still needs an API server, so it failed offline. `check_manifests.py` parses the YAML and checks 14 structural properties, such as the selector matching the pod labels. That doesn't prove the API server would accept it.
- **The CI workflow never ran.** It would need a GitHub repository and runner. The same script only checks its job order and token permissions.
- **Redis, push providers and hosted models.** The Redis commands in chapters 4 and 8 were read from its docs and modelled with SQLite. No push provider or model was ever called. Chapter 10's gateway uses stubs.
