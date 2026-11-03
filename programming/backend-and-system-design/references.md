---
origin: curated
sources:
  - https://www.rfc-editor.org/rfc/rfc9110
  - https://sre.google/sre-book/handling-overload/
  - https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf
confidence: high
cleaned: 2026-11-02
---
# References: backend and system design

Every row here was read for this track, and the "Read" column says how much. "Parts" means the sections a chapter relies on, not the whole work. "Page" means one web page was fetched in full and the parts the chapter uses were read closely. Don't take a row as a claim about anything beyond that. "Whole" means the full text was read, including in the audit of this track's citations; figures and some tables and equations didn't survive text extraction, so no chapter relies on them. Links were checked on 2026-11-03.

## Books not accessed

These are the standard books on the subject. They weren't available to read, so no chapter cites their contents.

| Book | Instead, this track read | Would add |
|---|---|---|
| Kleppmann, *Designing Data-Intensive Applications* | Dynamo, Bigtable, the LSM paper, and the [data engineering notes on replication and consistency](../../data-engineering/01-storage-and-compute-foundations/README.md) | A single connected account of storage, replication and streams |
| Xu, *System Design Interview* | The primary sources behind each walkthrough, listed below | More walkthroughs, in an interview's format |
| Newman, *Building Microservices* | SRE book chapters and Kubernetes docs | How to divide services and teams, which this track doesn't cover |

## Core papers

| Paper | Read | Why | Maps to |
|---|---|---|---|
| Dean and Barroso, [The Tail at Scale](https://www.barroso.org/publications/TheTailAtScale.pdf), CACM 2013 | Whole | Fan-out makes the tail common; hedged requests | [07](notes/07-reliability-under-load.md), [10](notes/10-ai-system-reference-architecture.md) |
| DeCandia et al., [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), SOSP 2007 | Whole | Virtual nodes, quorums, vector clocks, the shopping cart merge | [04](notes/04-load-balancing-and-rate-limiting.md), [09](notes/09-design-walkthroughs-kv-store-and-feed.md) |
| Chang et al., [Bigtable](https://static.googleusercontent.com/media/research.google.com/en//archive/bigtable-osdi06.pdf), OSDI 2006 | Whole | Memtable, sorted tables, major compaction | [09](notes/09-design-walkthroughs-kv-store-and-feed.md) |
| O'Neil et al., [The LSM-Tree](https://www.cs.umb.edu/~poneil/lsmtree.pdf), Acta Informatica 1996 | Whole | The original trade of writes against reads | [09](notes/09-design-walkthroughs-kv-store-and-feed.md) |
| Nishtala et al., [Scaling Memcache at Facebook](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf), NSDI 2013 | Whole | Leases against stale fills | [03](notes/03-caching-and-queues.md) |
| Bronson et al., [Metastable Failures](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf), HotOS 2021 | Whole | Why retries can keep a recovered system down | [03](notes/03-caching-and-queues.md), [07](notes/07-reliability-under-load.md) |
| Mitzenmacher, [The Power of Two Choices](https://www.eecs.harvard.edu/~michaelm/postscripts/tpds2001.pdf), IEEE TPDS 2001 | Whole, without the cells of its tables | Why two random choices do so well | [04](notes/04-load-balancing-and-rate-limiting.md) |
| Karger et al., [Consistent Hashing and Random Trees](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf), STOC 1997 | Whole, with its mathematics garbled in extraction | Few keys move when nodes change | [04](notes/04-load-balancing-and-rate-limiting.md), [09](notes/09-design-walkthroughs-kv-store-and-feed.md) |
| Eisenbud et al., [Maglev](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/44824.pdf), NSDI 2016 | Whole | Layer 4 balancing with a lookup table | [04](notes/04-load-balancing-and-rate-limiting.md) |
| Verma et al., [Borg](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43438.pdf), EuroSys 2015 | Whole | SIGTERM before SIGKILL, and how often it arrives | [06](notes/06-containers-cicd-and-deployment.md), [08](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md) |

## HTTP and API design

| Source | Read | Maps to |
|---|---|---|
| [RFC 9110, HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110) | Parts: methods, safety, idempotency, validators, conditional requests, status codes, Retry-After | [01](notes/01-api-design.md), [02](notes/02-auth-sessions-jwt-oauth.md), [08](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md) |
| [RFC 6585, Additional HTTP Status Codes](https://www.rfc-editor.org/rfc/rfc6585) | Parts: 428 and 429 | [01](notes/01-api-design.md), [04](notes/04-load-balancing-and-rate-limiting.md), [08](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md), [10](notes/10-ai-system-reference-architecture.md) |
| [RFC 9457, Problem Details](https://www.rfc-editor.org/rfc/rfc9457) | Parts: the members and an example | [01](notes/01-api-design.md) |
| [RFC 8288, Web Linking](https://www.rfc-editor.org/rfc/rfc8288) | Parts: the Link header | [01](notes/01-api-design.md) |
| [Stripe API docs, Idempotent requests](https://docs.stripe.com/api/idempotent_requests) | Page | [01](notes/01-api-design.md) |
| [GraphQL docs, Pagination](https://graphql.org/learn/pagination/) | Page | [01](notes/01-api-design.md) |
| [GraphQL docs, Performance](https://graphql.org/learn/performance/) | Page | [01](notes/01-api-design.md) |
| [GraphQL docs, Security](https://graphql.org/learn/security/) | Page | [01](notes/01-api-design.md) |
| [GraphQL docs, Schema design](https://graphql.org/learn/schema-design/) | Page | [01](notes/01-api-design.md) |
| [gRPC docs, Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/) | Page | [01](notes/01-api-design.md) |
| [gRPC docs, Deadlines](https://grpc.io/docs/guides/deadlines/) | Page | [01](notes/01-api-design.md), [07](notes/07-reliability-under-load.md) |
| [gRPC docs, Status codes](https://grpc.io/docs/guides/status-codes/) | Page | [01](notes/01-api-design.md), [07](notes/07-reliability-under-load.md) |
| [gRPC docs, Retry](https://grpc.io/docs/guides/retry/) | Page | [01](notes/01-api-design.md) |
| [Protocol Buffers docs, Encoding](https://protobuf.dev/programming-guides/encoding/) | Parts: varints and field tags | [01](notes/01-api-design.md) |
| [OWASP API Security Top 10 2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) | Page | [01](notes/01-api-design.md) |
| [OWASP API Security 2023, API4 Unrestricted Resource Consumption](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/) | Page | [01](notes/01-api-design.md) |

## Authentication and authorization

| Source | Read | Maps to |
|---|---|---|
| [RFC 6265, HTTP State Management Mechanism](https://www.rfc-editor.org/rfc/rfc6265) | Parts: cookie attributes | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [RFC 7515, JSON Web Signature](https://www.rfc-editor.org/rfc/rfc7515) | Parts: Appendix A.1 and validation | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [RFC 7519, JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519) | Parts: claims and validation | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [RFC 8725, JWT Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725) | Whole | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [RFC 9068, JWT Profile for OAuth 2.0 Access Tokens](https://www.rfc-editor.org/rfc/rfc9068) | Parts: type and validation | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [RFC 6749, OAuth 2.0](https://www.rfc-editor.org/rfc/rfc6749) | Parts: authorization code grant, roles, tokens | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [RFC 7636, PKCE](https://www.rfc-editor.org/rfc/rfc7636) | Parts: the protocol | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [RFC 9700, Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700) | Parts: the main recommendations and §4.14 refresh tokens | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html) | Parts: ID token and its validation | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html) | Parts: passwords and sessions | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) | Page | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) | Page | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) | Page | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html) | Page | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | Page | [02](notes/02-auth-sessions-jwt-oauth.md) |
| [OWASP API Security 2023, API1 Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/) | Page | [02](notes/02-auth-sessions-jwt-oauth.md) |

## Caching and queues

| Source | Read | Maps to |
|---|---|---|
| [RFC 9111, HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111) | Parts: Cache-Control directives (§5.2.2) | [03](notes/03-caching-and-queues.md) |
| [Redis docs, Key eviction](https://redis.io/docs/latest/develop/reference/eviction/) | Page | [03](notes/03-caching-and-queues.md) |
| [Redis docs, Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) | Page | [03](notes/03-caching-and-queues.md) |
| [Amazon SQS guide, Standard queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html) | Page | [03](notes/03-caching-and-queues.md) |
| [Amazon SQS guide, At-least-once delivery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html) | Page | [03](notes/03-caching-and-queues.md) |
| [Amazon SQS guide, Visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html) | Page | [03](notes/03-caching-and-queues.md) |
| [Apache Kafka docs, Design](https://kafka.apache.org/42/design/design/) | Parts: consumer position and delivery semantics | [03](notes/03-caching-and-queues.md) |
| [RabbitMQ docs, Reliability Guide](https://www.rabbitmq.com/docs/reliability) | Page | [03](notes/03-caching-and-queues.md) |
| [RabbitMQ docs, Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms) | Parts: acknowledgements and confirms | [03](notes/03-caching-and-queues.md) |
| [Richardson, Transactional outbox pattern](https://microservices.io/patterns/data/transactional-outbox.html) | Page | [03](notes/03-caching-and-queues.md), [08](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md) |

## Load balancing and rate limiting

| Source | Read | Maps to |
|---|---|---|
| [Envoy docs, Supported load balancers](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers) | Page | [04](notes/04-load-balancing-and-rate-limiting.md) |
| [NGINX docs, Using nginx as HTTP load balancer](https://nginx.org/en/docs/http/load_balancing.html) | Page | [04](notes/04-load-balancing-and-rate-limiting.md) |
| [Google SRE Book, Load Balancing in the Datacenter](https://sre.google/sre-book/load-balancing-datacenter/) | Page | [04](notes/04-load-balancing-and-rate-limiting.md) |
| [gRPC blog, gRPC Load Balancing](https://grpc.io/blog/grpc-load-balancing/) | Page | [04](notes/04-load-balancing-and-rate-limiting.md) |
| [Cloudflare blog, How we built rate limiting capable of scaling to millions of domains](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/) | Page | [04](notes/04-load-balancing-and-rate-limiting.md), [08](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md) |
| [Redis docs, INCR](https://redis.io/docs/latest/commands/incr/) | Page. The patterns were read, not run, since Redis wasn't installed | [04](notes/04-load-balancing-and-rate-limiting.md), [08](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md) |

## Reliability, SLOs and observability

| Source | Read | Maps to |
|---|---|---|
| [Google SRE Book, Handling Overload](https://sre.google/sre-book/handling-overload/) | Page | [07](notes/07-reliability-under-load.md), [10](notes/10-ai-system-reference-architecture.md) |
| [Google SRE Book, Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) | Page | [01](notes/01-api-design.md), [07](notes/07-reliability-under-load.md) |
| [Google SRE Book, Embracing Risk](https://sre.google/sre-book/embracing-risk/) | Page | [05](notes/05-estimation-and-scaling.md), [07](notes/07-reliability-under-load.md) |
| [Google SRE Book, Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) | Page | [05](notes/05-estimation-and-scaling.md), [07](notes/07-reliability-under-load.md) |
| [Google SRE Book, Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) | Page | [07](notes/07-reliability-under-load.md) |
| [Google SRE Book, Effective Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/) | Page | [07](notes/07-reliability-under-load.md) |
| [Google SRE Book, Managing Incidents](https://sre.google/sre-book/managing-incidents/) | Page | [07](notes/07-reliability-under-load.md) |
| [AWS Builders' Library, Timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) | Page | [07](notes/07-reliability-under-load.md) |
| [AWS Builders' Library, Using load shedding to avoid overload](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/) | Page | [07](notes/07-reliability-under-load.md) |
| [AWS, Disaster recovery options in the cloud](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html) | Page | [07](notes/07-reliability-under-load.md) |
| [AWS, Business continuity plan](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/business-continuity-plan-bcp.html) | Page | [07](notes/07-reliability-under-load.md) |
| [Prometheus, Histograms and summaries](https://prometheus.io/docs/practices/histograms/) | Page | [07](notes/07-reliability-under-load.md) |
| [OpenTelemetry, Traces](https://opentelemetry.io/docs/concepts/signals/traces/) | Page | [07](notes/07-reliability-under-load.md) |
| [OpenTelemetry, Sampling](https://opentelemetry.io/docs/concepts/sampling/) | Page | [07](notes/07-reliability-under-load.md) |
| [OpenTelemetry, Semantic conventions for HTTP metrics](https://opentelemetry.io/docs/specs/semconv/http/http-metrics/) | Page | [07](notes/07-reliability-under-load.md) |
| [W3C, Trace Context](https://www.w3.org/TR/trace-context/) | Parts: the traceparent header | [07](notes/07-reliability-under-load.md) |

## Containers, delivery and deployment

| Source | Read | Maps to |
|---|---|---|
| [Docker, Docker overview](https://docs.docker.com/get-started/docker-overview/) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [Docker, Building best practices](https://docs.docker.com/build/building/best-practices/) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [Docker, Multi-stage builds](https://docs.docker.com/build/building/multi-stage/) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [Kubernetes, Liveness, readiness and startup probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [Kubernetes, Resource management for pods and containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) | Parts: requests and limits | [06](notes/06-containers-cicd-and-deployment.md) |
| [Kubernetes, Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) | Parts: rolling updates, rollback | [06](notes/06-containers-cicd-and-deployment.md) |
| [Kubernetes, Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [Kubernetes, Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) | Parts: termination | [06](notes/06-containers-cicd-and-deployment.md) |
| [Kubernetes, Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [The Twelve-Factor App, Config](https://12factor.net/config) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [The Twelve-Factor App, Disposability](https://12factor.net/disposability) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [Google SRE Book, Release Engineering](https://sre.google/sre-book/release-engineering/) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [Google SRE Workbook, Canarying Releases](https://sre.google/workbook/canarying-releases/) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [DORA, Continuous delivery](https://dora.dev/capabilities/continuous-delivery/) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [Martin Fowler, Continuous Delivery](https://martinfowler.com/bliki/ContinuousDelivery.html) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [Martin Fowler, Blue Green Deployment](https://martinfowler.com/bliki/BlueGreenDeployment.html) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [Martin Fowler, Canary Release](https://martinfowler.com/bliki/CanaryRelease.html) | Page | [06](notes/06-containers-cicd-and-deployment.md) |
| [GitHub Actions, Understanding GitHub Actions](https://docs.github.com/en/actions/get-started/understand-github-actions) | Page | [06](notes/06-containers-cicd-and-deployment.md) |

## Notifications and scheduling

| Source | Read | Maps to |
|---|---|---|
| [RFC 8030, Generic Event Delivery Using HTTP Push](https://www.rfc-editor.org/rfc/rfc8030) | Parts: TTL, urgency and topic | [08](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md) |
| [Firebase Cloud Messaging, Set the lifespan of a message](https://firebase.google.com/docs/cloud-messaging/customize-messages/setting-message-lifespan) | Page. Read only; no message was sent | [08](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md) |
| [Firebase Cloud Messaging, Set the priority of a message](https://firebase.google.com/docs/cloud-messaging/customize-messages/setting-message-priority) | Page. Read only | [08](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md) |
| [Google SRE Book, Distributed Periodic Scheduling with Cron](https://sre.google/sre-book/distributed-periodic-scheduling/) | Page | [08](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md) |
| [Kubernetes, CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) | Page | [08](notes/08-design-walkthroughs-rate-limiter-notifications-scheduler.md) |

## Streaming and AI systems

| Source | Read | Maps to |
|---|---|---|
| [WHATWG, HTML Living Standard, Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html) | Parts: the format, the EventSource interface, reconnection, authoring notes | [10](notes/10-ai-system-reference-architecture.md) |
| [OpenTelemetry, Semantic conventions for generative AI metrics, v1.38.0](https://raw.githubusercontent.com/open-telemetry/semantic-conventions/v1.38.0/docs/gen-ai/gen-ai-metrics.md) | Parts: metric names and status | [10](notes/10-ai-system-reference-architecture.md) |

## Inside this course

The AI chapter points to other notes in this course and doesn't restate them. Its links are in [chapter 10's table](notes/10-ai-system-reference-architecture.md#the-whole-system). The sections chapter 10 describes were read for this track; the course's own sources for those notes are in their references files.
