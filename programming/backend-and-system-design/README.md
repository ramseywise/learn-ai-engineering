# Backend and system design

> How a service holds up once it has real users: API contracts, identity, caches and queues, balancing and limits, capacity sums, deployment, and behaviour under load, followed by five full design walkthroughs and a reference architecture for an AI system.
>
> Study deck: [backend-and-system-design.pptx](slides/backend-and-system-design.pptx), which librarian turns into flashcards (source: [deck.yaml](slides/deck.yaml)).
> Jump to: [What this is](#what-this-is) · [Reading order](#reading-order) · [Builds on and feeds into](#builds-on-and-feeds-into) · [Rules of thumb](#rules-of-thumb) · [Layout](#layout) · [Setup](#setup) · [Primary texts](#primary-texts)

---

## What this is

Ten chapters on the part of backend work that tutorials leave out: what happens when a request is retried, when a token is forged, when a cache key expires under load, when a deploy meets a long request, or when a region goes away. Each chapter's numbers come from code you can run, or from an estimate written as a program.

It sits in the programming subject, after [computer science foundations](../computer-science/README.md), and it borrows from [data engineering](../../data-engineering/01-storage-and-compute-foundations/README.md) for what's underneath a store. It links to those notes for replication, consistency and persistence, and doesn't restate them. The last chapter does the same for inference, retrieval, harnesses and observability.

The usual weakness of system design material is that it's a list of components with arrows, and every design looks fine. This track attacks that by making you compute. If a design needs 22 nodes for traffic and 6 for disk, it's a traffic problem, and the design follows from that. Everything that could be run was run, and [what could only be read](practice/README.md#the-deploy-example) is named.

The mental model is a question to ask of every box on a diagram: **what happens to this request if the box is slow, down, or running twice?**

## Reading order

Each chapter takes about an hour, with its exercises. The format of a chapter follows [the course's chapter standard](https://github.com/ramseywise/librarian/blob/main/.claude/skills/pillar/references/pillar-layout.md). Lab: [`practice/`](practice/README.md).

**The contract and who may use it**

| # | Note | You can… |
|---|---|---|
| 1 | [API design](notes/01-api-design.md) | Say what each method promises, make a write survive a retry, paginate with a cursor, and choose among REST, GraphQL and gRPC |
| 2 | [Auth: sessions, JWT, OAuth](notes/02-auth-sessions-jwt-oauth.md) | Choose a session or a token, verify a JWT strictly, run an authorization code flow, and check access per object |

**The building blocks**

| # | Note | You can… |
|---|---|---|
| 3 | [Caching and queues](notes/03-caching-and-queues.md) | Predict a hit rate, stop a stampede and a stale fill, handle at-least-once delivery, and use an outbox |
| 4 | [Load balancing and rate limiting](notes/04-load-balancing-and-rate-limiting.md) | Pick a balancing policy, use consistent hashing, and compare five rate limiters on their accuracy |

**Sums and shipping**

| # | Note | You can… |
|---|---|---|
| 5 | [Estimation and scaling](notes/05-estimation-and-scaling.md) | Write an estimate as a program, size a pool with queueing theory, and combine availability figures |
| 6 | [Containers, CI/CD and deployment](notes/06-containers-cicd-and-deployment.md) | Build a small image, drain on SIGTERM, set three probes correctly, and pick a rollout strategy |
| 7 | [Reliability under load](notes/07-reliability-under-load.md) | Explain the tail, stop a retry storm, shed load, read percentiles and traces, and plan for losing a region |

**Whole designs**

| # | Note | You can… |
|---|---|---|
| 8 | [Walkthroughs: rate limiter, notifications, scheduler](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md) | Run a design from requirements to failure modes, close a race with one atomic step, and fence a stale worker |
| 9 | [Walkthroughs: KV store and feed](notes/09-design-walkthroughs-kv-store-and-feed.md) | Build a log-structured store, reason about quorums and concurrent writes, and pick a feed's fan-out |
| 10 | [An AI system reference architecture](notes/10-ai-system-reference-architecture.md) | Place each part of an AI system, build a gateway with a token budget, fallback and streaming, and find the note that goes deeper on each part |

## Builds on and feeds into

**Hard prerequisites** (chapters 1 and 3 use them from the first page)

| Chapter | Why |
|---|---|
| [SQL 07: modeling and DDL](../sql/notes/07-modeling-and-ddl.md) and [SQL 08: indexes and query plans](../sql/notes/08-indexes-and-query-plans.md) | Chapters 1 and 3 run SQLite: unique constraints, keyset pagination over a covering index, and the outbox table |
| [DE 01: transactions and isolation](../../data-engineering/01-storage-and-compute-foundations/notes/04-transactions-and-isolation.md) | "Same transaction" carries the idempotency check in chapter 1 and the outbox in chapter 3 |

**Builds on** (soft prerequisites: skim when a chapter points at them)

| Chapter | Why |
|---|---|
| [CS 05: processes, threads and I/O](../computer-science/notes/05-processes-threads-and-io.md) | Little's law, backpressure and the event loop are used throughout |
| [CS 06: networks](../computer-science/notes/06-networks.md) | What a request costs, and what HTTP sits on |
| [DE 01: partitioning and replication](../../data-engineering/01-storage-and-compute-foundations/notes/05-partitioning-and-replication.md) | Chapter 9 uses replication without re-teaching it |
| [DE 01: consistency and consensus](../../data-engineering/01-storage-and-compute-foundations/notes/07-consistency-and-consensus.md) | What quorums and leases do and don't give you |
| [DE 01: persistence](../../data-engineering/01-storage-and-compute-foundations/notes/09-persistence.md) and [choosing a store](../../data-engineering/01-storage-and-compute-foundations/notes/10-choosing-a-store.md) | Why a write is durable, and which store fits |
| [DE 01: row and column stores](../../data-engineering/01-storage-and-compute-foundations/notes/03-row-and-column-stores.md) | The LSM tree in chapter 9 is the write-optimised side of this |
| [DE 04: Kafka and stream semantics](../../data-engineering/04-warehouse-lakehouse-streaming/notes/04-kafka-and-stream-semantics.md) | Delivery guarantees, which chapter 3's at-least-once section applies to a queue |
| [DE 05: schema and data migrations](../../data-engineering/05-quality-and-observability/notes/04-schema-and-data-migrations.md) | Expand, migrate, contract, as chapter 6 uses it for a deploy |
| [DE 05: operating data stores](../../data-engineering/05-quality-and-observability/notes/05-operating-data-stores.md) | Running what these designs depend on |
| [Software design 05: testing strategy](../software-design/notes/05-testing-strategy.md) and [06: debugging and profiling](../software-design/notes/06-debugging-and-profiling.md) | Tests for the lab, and the profiling habits behind chapter 7's debugging section |

**Feeds into**

| Chapter | Why |
|---|---|
| [Serving at scale](../../ai-engineering/07-inference-engineering/notes/06-serving-at-scale.md) | Balancing and autoscaling, with a GPU and tokens as the unit |
| [RAG in production](../../generative-ai/02-rag-retrieval/notes/07-rag-in-production.md) | Caching, latency and tenancy applied to retrieval |
| [Execution boundaries](../../ai-engineering/03-harness-engineering/notes/04-execution-boundaries.md) | Sandboxes, budgets and permission for code an agent runs |
| [Cost and latency dashboards](../../generative-ai/06-observability/notes/06-cost-and-latency-dashboards.md) | Percentiles and alerts, in dollars as well |

## Rules of thumb

- A retry is a write. Ask what happens if every request arrives twice.
- Use a cursor, not an offset, on anything that changes while you page through it.
- A JWT's header doesn't choose its own algorithm: your configuration does.
- Check access on every object, not only every route.
- A cache's expiry time doesn't protect you when a popular key expires. Limit its fills to one at a time.
- A queue gives you at-least-once delivery, so make the consumer idempotent.
- Balance on live load. Hash only when a key has to land in one place.
- Write the estimate as a program, so that when a number is questioned you can change it.
- Run servers well below saturation: wait grows sharply near the limit.
- Readiness and liveness answer different questions. A failed dependency should fail readiness only.
- Retries need a budget, deadlines need to travel, and overload needs a queue with a limit.
- Report percentiles from histograms and never average them across hosts.
- In a design interview, name the requirement that drives the design before you draw anything.
- For an AI system, limit tokens rather than requests, and fall back only before the first token.

## Layout

```
backend-and-system-design/
├── README.md
├── references.md
├── notes/                         01–10
└── practice/
    ├── README.md                  the lab: what to build and how it's checked
    ├── check.sh                   runs the lab's tests, every code block, and deploy/verify.sh
    ├── run_notes.py               runs the notes' blocks, and compares output where it's fixed
    ├── deploy/                    service, Dockerfile, Kubernetes manifest, CI workflow, verify.sh
    ├── exercises/backend_lab/     stubs and their tests
    └── solutions/backend_lab/     worked versions and the same tests
```

## Setup

You need Python 3.14 and [uv](https://docs.astral.sh/uv/). Docker is optional, for chapter 6's example. The notes' code blocks are standalone apart from a few marked with a package they need, so you can copy one into a file and run it. `bash practice/check.sh` runs everything. Nothing needs a cloud account, and no block calls a model.

## Primary texts

- *Site Reliability Engineering* and *The Site Reliability Workbook*, free online. These chapters above all: [handling overload](https://sre.google/sre-book/handling-overload/), [cascading failures](https://sre.google/sre-book/addressing-cascading-failures/), [SLOs](https://sre.google/sre-book/service-level-objectives/), [monitoring](https://sre.google/sre-book/monitoring-distributed-systems/) and [canarying](https://sre.google/workbook/canarying-releases/)
- Papers: [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), [Bigtable](https://static.googleusercontent.com/media/research.google.com/en//archive/bigtable-osdi06.pdf), [The Tail at Scale](https://www.barroso.org/publications/TheTailAtScale.pdf), [Scaling Memcache at Facebook](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf), [Metastable Failures](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf)
- The RFCs for [HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110), [OAuth 2.0](https://www.rfc-editor.org/rfc/rfc6749), [JWT](https://www.rfc-editor.org/rfc/rfc7519) and [JWT best practices](https://www.rfc-editor.org/rfc/rfc8725)
- OWASP cheat sheets for [sessions](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), [passwords](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) and [Docker](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- Project docs: [gRPC core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/), [GraphQL security](https://graphql.org/learn/security/), [Docker build best practices](https://docs.docker.com/build/building/best-practices/), [Kubernetes probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/) and [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/)

The well-known books in this field (Kleppmann's *Designing Data-Intensive Applications*, Xu's *System Design Interview*) were not accessed for this track, and no claim here rests on their contents. Everything else: [references.md](references.md).
