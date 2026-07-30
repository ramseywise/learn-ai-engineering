---
origin: video-transcript
confidence: medium
sources:
  - Staff-level system design interview guidance (broadly applicable patterns)
cleaned: 2026-07-30
---
# System Design Interview Patterns

Thirteen more round patterns, staff-level. Companion to
[interview-heuristics.md](interview-heuristics.md); both are behavior in the room rather
than architecture knowledge. For *which option to pick* at a given component, use the
[decision tree](../../guides/9-system-design/04-decision-tree.md).

## 1. Communication is Part of the Evaluation

The interviewer repeatedly praised the **decision-making process**, not just the final architecture.

Use this pattern every time you introduce a design decision:

```
Problem
    ↓
Possible solutions
    ↓
Tradeoffs
    ↓
Chosen solution
    ↓
Why it wins
```

Example:

> "Clients need real-time updates.
>
> We could poll, but polling creates unnecessary load.
>
> WebSockets are another option but require bidirectional communication.
>
> Since updates only flow server→client, I'll use Server-Sent Events."

This style consistently scores highly because it demonstrates engineering judgment.

---

# 2. Build the Simplest Working System First

Don't begin with Kafka, Redis, CQRS, sharding, etc.

Start with:

```
API
↓

Service

↓

Database
```

Only introduce complexity after identifying bottlenecks.

Interviewers prefer:

> "Let's first make the system function."

over

> "We'll use Kafka, Redis, Cassandra, Temporal..."

---

# 3. Think in Evolutions

A common progression:

```
Simple implementation

↓

Scaling issue appears

↓

Targeted optimization

↓

Repeat
```

Example from the auction interview:

```
Cron Job

↓

Need lower latency

↓

Delayed queue message

↓

Need dynamic deadlines

↓

Update scheduled message / Temporal workflow
```

Every optimization should solve a specific problem.

---

# 4. Non-functional Requirements Drive Design

Rather than listing:

* scalability
* latency
* consistency
* durability

Tie each architectural component to one.

| Requirement | Design Choice                 |
| ----------- | ----------------------------- |
| Consistency | ACID transaction              |
| Latency     | SSE                           |
| Durability  | Queue/stream retention        |
| Scalability | Independent streaming service |

This creates a coherent narrative.

---

# 5. High-Level Components Before Details

The interviewer liked introducing abstractions first.

Instead of:

```
APNS
Firebase
SNS
```

say

```
Notification Service
```

Only drill down if asked.

Similarly:

```
Blob Storage
```

before

```
Amazon S3
```

---

# 6. Separate Read and Write Paths

Even if you don't implement CQRS, think this way.

Auction example:

Write path

```
Create Bid

↓

Validate

↓

Persist

↓

Publish Event
```

Read path

```
Client

↓

Streaming Service

↓

Redis Pub/Sub

↓

SSE
```

Interviewers like seeing these modeled independently.

---

# 7. Introduce Services Only for Independent Scaling

Don't split services because "microservices."

Split them because scaling characteristics differ.

Example:

```
Auction Service

- creates auctions
- creates bids

Streaming Service

- maintains thousands of SSE connections
```

Different workloads justify independent scaling.

---

# 8. Think in Events

Modern interview designs often revolve around events.

Examples:

```
Order Created

Bid Submitted

Payment Completed

Photo Uploaded

Ride Requested
```

Pattern:

```
Write DB

↓

Publish Event

↓

Subscribers react
```

Subscribers may include:

* notifications
* analytics
* search indexing
* recommendations
* cache invalidation

---

# 9. Consistency Questions Are Common

If maintaining duplicate state:

```
Auction.highestBid

AND

Bid table
```

expect:

> "How do you keep these consistent?"

Typical answers:

* ACID transaction
* optimistic locking
* compare-and-swap
* serializable isolation
* single-writer pattern

---

# 10. Know When Caching Doesn't Help

A strong answer from the interview:

> "Caching isn't useful because bids change continuously."

Don't force Redis into every design.

Cache only when:

* many reads
* few writes
* repeated access

Avoid caching:

* constantly changing leaderboards
* live bidding
* rapidly mutating state

---

# 11. Scheduled Work Is a Common Pattern

Many interviews include delayed execution:

Examples:

* send reminder tomorrow
* auction ends in one hour
* retry payment later
* expire session
* delete inactive account

Useful solutions:

* delayed queues
* scheduled jobs
* workflow engines (e.g., Temporal)
* scheduler services

Recognize these quickly.

---

# 12. Durability Is Often Forgotten

The interviewer highlighted this as the missing non-functional requirement.

Question:

> What happens if a server crashes after accepting a bid?

Without durable messaging:

```
Client

↓

API

↓

Server crashes

↓

Bid lost
```

With a durable stream:

```
API

↓

Kafka / Queue

↓

Workers

↓

Database
```

Even if workers fail, events remain.

---

# 13. Deep Knowledge > More Boxes

The interviewer emphasized that staff-level interviews don't require dramatically different diagrams.

Instead, they reward deeper explanations.

Example:

Instead of:

> "I'll use Redis."

Explain:

* single-threaded execution
* Lua scripts
* atomic operations
* pub/sub limitations
* persistence options
* eviction policies

Similarly:

Kafka:

* partitions
* ordering guarantees
* consumer groups
* retention
* replication

Postgres:

* MVCC
* isolation levels
* row locking
* indexes
* transactions

Depth demonstrates seniority more than architecture complexity.

---

# 14. Interviewers Want Reasonable Confidence, Not Perfect Recall

You don't need encyclopedic knowledge.

It's acceptable to say:

> "RabbitMQ supports scheduled execution, so I'd choose a messaging system with that capability."

or

> "Kafka may not support this directly, so I'd layer an appropriate scheduler on top."

Demonstrate awareness of the capability rather than perfect product knowledge.

---

# 15. Typical Staff-Level Progression

Aim to move through problems in this order:

```
Clarify requirements

↓

Estimate scale

↓

Simple architecture

↓

Walk request flows

↓

Identify bottlenecks

↓

Optimize each bottleneck

↓

Discuss non-functional requirements

↓

Handle follow-up questions

↓

Dive deep into technologies
```

The interviewer noted that your **diagram likely wouldn't change much** between senior and staff. The difference is that a staff candidate explains *why* each component behaves the way it does and can discuss implementation details (e.g., Kafka partitioning, Postgres isolation levels, Redis internals, Temporal workflows) when prompted.

## Overall Takeaway

Combining these notes with your earlier Spotify and Agentic AI summaries, a consistent interview philosophy emerges:

1. **Start simple.**
2. **Let requirements drive architecture.**
3. **Optimize only when a bottleneck appears.**
4. **Explain trade-offs before choosing.**
5. **Use events to decouple systems.**
6. **Treat consistency, latency, durability, and scalability as explicit design goals.**
7. **Demonstrate depth through implementation knowledge, not by adding unnecessary services.**

Following this pattern will prepare you well not just for auction or Spotify questions, but also for common large-scale design interviews such as Dropbox, Uber, WhatsApp, YouTube, Google Drive, Ticketmaster, Slack, and notification systems.
