---
origin: video-transcript
confidence: medium
sources:
  - Telegram architecture walkthrough — techniques extracted, design itself not copied
cleaned: 2026-07-30
---
# System Design Interview Heuristics

Fourteen round techniques, extracted from a design walkthrough. These are *how to behave
in the room*, not architecture knowledge — the design content they came from lives in
[pillar 9](../../guides/9-system-design/). Pairs with
[interview-patterns.md](interview-patterns.md) (thirteen more) and the
[study guide](study-guide.md) (the 5-step process they hang on).

# 1. Scope Aggressively

One of the strongest interview habits throughout this interview:

Instead of trying to design "Telegram", reduce it to:

* one-to-one messaging
* text only
* backend only
* ignore groups
* ignore media
* ignore encryption
* ignore presence
* ignore voice/video

Interviewer actually rewards this.

A good phrase:

> "Telegram has many features, but to build a solid MVP within interview time, I'll focus on one-to-one text messaging."

---

# 2. Clarify Functional Requirements First

Notice the order:

Users send messages

↓

Users receive messages

↓

Users read messages

Everything else becomes out-of-scope.

This is much cleaner than brainstorming features.

---

# 3. Treat APIs as Functional Requirements

This is surprisingly useful.

Instead of saying

> Users send messages

translate immediately into APIs.

Example

```
POST /messages

GET /messages

GET /messages/{id}

POST /messages/read
```

For AI systems you can do the same.

```
POST /chat

POST /memory

GET /conversation

POST /feedback
```

Interviewers like seeing APIs because they're concrete.

---

# 4. Capacity Planning Doesn't Need Precision

A very useful pattern.

Start with daily traffic.

Convert to requests/sec.

Estimate peak.

Estimate servers.

Estimate storage.

Done.

Example:

```
10B/day

↓

100k/sec average

↓

500k/sec peak

↓

50 servers
```

Nobody expects exact numbers.

They want reasoning.

---

# 5. Convert Product Metrics Into Infrastructure Metrics

The interview naturally moves:

Business metric

↓

System metric

Example

```
10B messages/day

↓

100k requests/sec

↓

500k peak

↓

autoscaling
```

That's exactly what interviewers want.

---

# 6. Always State Non-functional Requirements Explicitly

Rather than sprinkling them throughout.

Good checklist:

```
Availability

Latency

Consistency

Scalability

Durability

Fault tolerance

Security
```

Then tie every architecture decision back.

---

# 7. Explain Why Every Component Exists

Notice he never says

> We need a load balancer.

He says

```
Traffic grows

↓

Need horizontal scaling

↓

Need multiple API servers

↓

Need load balancer
```

Always explain causality.

---

# 8. Every Architecture Decision Should Include Trade-offs

Excellent example:

SQL

Pros

* joins
* relationships

Cons

* harder to shard

NoSQL

Pros

* horizontal scaling

Cons

* fewer relational queries

Then choose.

Interviewers care much more about reasoning than the "correct" database.

---

# 9. Managed Services Are Good Interview Answers

Interesting point:

Rather than immediately saying

> Cassandra

he says

> DynamoDB because engineers are expensive.

That's a product/business answer.

General principle:

```
Managed service

↓

Faster development

↓

Less operational burden

↓

Can migrate later
```

Shows engineering maturity.

---

# 10. Data Model Before Algorithms

Before architecture he defines entities.

```
Messages

Users
```

Then fields.

```
Message

sender_id

recipient_id

timestamp

status

message_id
```

Simple but very interview-friendly.

---

# 11. Design Around Access Patterns

Probably the biggest architecture lesson.

Instead of designing tables...

Start with

"What queries must be fast?"

Example

```
Unread messages

↓

Must be O(1)

↓

Separate unread index
```

Architecture follows queries.

This is one of the biggest differences between junior and senior candidates.

---

# 12. Think in Terms of State Machines

Notice every message has a status.

```
Undelivered

↓

Delivered

↓

Read
```

Many systems become easier when modeled as state transitions.

Useful for:

* orders
* AI jobs
* agent workflows
* notifications
* payments

---

# 13. Background Workers

A recurring system design component.

```
API

↓

Persist

↓

Background worker

↓

Update state

↓

Notify user
```

Rather than doing everything synchronously.

For AI this becomes

```
Request

↓

Queue

↓

LLM

↓

Evaluation

↓

Store

↓

Notify
```

---

# 14. Find Your Own Bottlenecks

One of the strongest interview habits.

He doesn't wait.

He says

"My design has a bottleneck."

Interviewers love this.

Pattern:

```
Current design

↓

Future scale

↓

Potential bottleneck

↓

Possible mitigation
```

---

# 15. Admit Uncertainty

Another excellent senior behavior.

He says

> I'm hand-waving some locking issues.

instead of pretending.

Much better than bluffing.

---

# 16. Simplicity Wins

Great closing principle.

> Keep it simple.

Interviewers generally prefer

Simple architecture

*

Clear trade-offs

over

Distributed systems everywhere.

---

# 17. Finish With Improvements

Don't stop after drawing.

Spend the last minute discussing

Future improvements

Groups

Caching

Replication

Partitioning

Observability

Locking

Failure recovery

This often separates good from excellent interviews.

---

# 18. Mention Operational Metrics

Beyond business metrics.

Infrastructure metrics worth mentioning include:

* P95/P99 latency
* Error rate
* Throughput (RPS)
* Availability (e.g. 99.99%)
* Queue depth
* CPU/memory utilization
* Database read/write latency
* Replication lag
* Storage growth

This demonstrates production thinking.

---

# General Interview Heuristics

I think these are worth adding as a dedicated section because they apply to nearly every OpenAI, Anthropic, Meta, or Google interview:

| Principle                       | Why it matters                                         |
| ------------------------------- | ------------------------------------------------------ |
| Reduce scope aggressively       | Finish a complete design instead of half of a huge one |
| State assumptions explicitly    | Prevents solving the wrong problem                     |
| Quantify early                  | Lets numbers drive architecture                        |
| Explain every design choice     | Shows engineering judgment                             |
| Design around access patterns   | Data models should follow query patterns               |
| Use managed services first      | Demonstrates pragmatic engineering                     |
| Identify bottlenecks yourself   | Shows senior-level systems thinking                    |
| Discuss trade-offs continuously | There is rarely one "correct" design                   |
| End with future improvements    | Demonstrates iterative design thinking                 |

---

Taken together with your earlier Spotify, RAG, and agentic AI notes, I think you've now accumulated a strong interview playbook. The only major gap I'd still recommend filling is **distributed systems fundamentals**—topics like caching, queues, pub/sub, replication, partitioning/sharding, consistency models (CAP), consensus, idempotency, rate limiting, retries, circuit breakers, and observability. Those concepts are the building blocks that recur across nearly every modern system design interview, whether it's a messaging app, AI agent platform, or retrieval system.
