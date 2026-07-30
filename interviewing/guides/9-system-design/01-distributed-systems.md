---
origin: video-transcript
confidence: medium
sources:
  - System design walkthrough (photo-sharing/Instagram-like running example);
    concepts introduced as the application needs them rather than in isolation
cleaned: 2026-07-30
---
# System Design Fundamentals

Pillar 9, detailed note 1. The generic backend substrate the LLM-flavored design round
assumes you already have: scaling, load balancing, data modeling, replication, sharding,
caching. The [interview guide](interview-guide.md) is the *method*; this is the
*component vocabulary* it operates on.

## What is System Design?

**System Design** is the process of selecting the right components and arranging them to build software that satisfies both functional and scalability requirements.

It is less about writing code and more about answering:

* How should requests flow?
* Where should data live?
* What happens when traffic grows?
* What breaks first?
* How do we fix it?

The core mindset:

> Every scaling solution introduces a new problem.

System design is understanding those tradeoffs.

---

# Engineering Levels

### Junior

Focuses on implementing features.

```
Input
 ↓
Code
 ↓
Output
```

---

### Mid-level

Given a problem.

Responsible for deciding **how to implement** a solution inside an existing system.

---

### Senior

Designs the entire architecture.

Decides

* databases
* caching
* APIs
* scaling
* tradeoffs
* reliability

---

# Build One Server First

Initial architecture:

```
Users
   ↓
Server
 ├── App
 ├── Database
 └── Photos
```

This is actually the correct starting point.

Most startups should begin here.

---

# Common Failures and Their Solutions

## 1. CPU/RAM exhausted

Problem

Too many users.

Solution

Add more application servers.

New problem

Which server receives requests?

Solution

**Load Balancer**

```
Users
    ↓
Load Balancer
   ↙      ↘
Server1  Server2
```

---

## 2. Database overloaded

Problem

Thousands of users repeatedly request the same content.

Example

* trending photos
* popular profiles

Solution

**Cache**

```
Request

↓

Cache

↓

Database
```

Benefits

* faster reads
* reduced DB load

---

## 3. Server dies

Problem

Everything was on one machine.

Single Point of Failure.

Solution

* database replication
* external object storage (e.g. S3)

---

# System Design Principle

Notice:

We never changed application logic.

We only changed **where work happens**.

That is the essence of system design.

---

# High-Level Design vs Low-Level Design

## High-Level Design (HLD)

Architecture.

Focus:

* services
* databases
* cache
* queues
* networking

Interview examples

> Design Instagram

---

## Low-Level Design (LLD)

Implementation.

Focus:

* classes
* objects
* algorithms
* data structures

Interview examples

> Design an LRU Cache

---

Interview tip

Always clarify:

> "I'll answer at the high level first, then dive deeper if you'd like."

---

# Functional vs Non-Functional Requirements

## Functional

Features.

Examples

* upload photo
* follow user
* like photo
* comment
* feed

---

## Non-functional

Quality attributes.

Examples

* latency
* availability
* scalability
* durability
* cost

Interviewers care about these more.

---

# Five Questions Before Designing

Always ask:

### 1. Users?

Current and future scale.

---

### 2. Read-heavy or write-heavy?

Instagram

```
Reads >>> Writes
```

Optimize reads.

---

### 3. What data can never be lost?

Examples

Never lose

* uploaded photos

Can tolerate

* slightly stale like counts

---

### 4. Latency requirements?

Example

Feed

<200 ms

Uploads

2–3 seconds acceptable

---

### 5. Budget?

Architecture is always constrained by cost.

---

# Monolith vs Microservices

## Monolith

One codebase

One deployment

Simpler

Good for:

* startups
* small teams

---

## Microservices

Split by functionality

Example

* Feed Service
* Upload Service
* Likes Service
* Notification Service

Advantages

* independent scaling
* independent deployments

Disadvantages

* network failures
* debugging complexity
* operational overhead

Rule:

> Start with a monolith.
>
> Split only when justified.

---

# Vertical vs Horizontal Scaling

## Vertical

Bigger server.

Pros

* simple
* no code changes

Cons

* expensive
* hard limit
* still one point of failure

---

## Horizontal

More servers.

Pros

* nearly unlimited scaling
* fault tolerant

Requires

* load balancer
* shared state
* distributed data

Interview answer

Start vertically.

Move horizontally when necessary.

---

# How Requests Reach Your Server

Flow

```
Browser

↓

DNS

↓

IP Address

↓

HTTPS

↓

Load Balancer

↓

App Server

↓

Database
```

---

Important concepts

DNS

Maps names to IPs.

HTTPS

Encrypted HTTP.

Latency

Time for one round trip.

Bandwidth

Amount of data transferred.

---

# Load Balancer

Responsibilities

* distribute traffic
* remove dead servers
* health checks

Algorithms

### Round Robin

Equal rotation.

---

### Least Connections

Send to least busy server.

---

### Weighted

Larger servers receive more requests.

---

Load balancers are reverse proxies.

Popular implementations

* NGINX
* HAProxy
* AWS ELB

---

# Stateless vs Stateful

Bad approach

Store login session inside application memory.

```
User

↓

Server A

(session exists)

↓

Later request

↓

Server B

(no session)

↓

Logged out
```

---

Correct approach

Move session into shared storage.

Usually Redis.

```
Server A

↓

Redis

↑

Server B
```

Now every server works.

---

Sticky Sessions

Possible.

Usually discouraged because

* poor load balancing
* server failures lose sessions

Golden rule

Keep application servers stateless.

---

# Data Modeling

Don't start with

> Which database?

Start with

> What questions must the system answer?

Access patterns define schema.

Example queries

* show profile
* show feed
* upload photo
* like photo
* follow user

---

Core entities

Users

Photos

Likes

Comments

Follows

IDs connect everything.

---

# SQL vs NoSQL

Choose based on data shape.

---

SQL

Use when

* structured data
* relationships
* joins
* transactions

Examples

* PostgreSQL
* MySQL

---

NoSQL

Use when

* flexible schema
* huge scale
* document/event data

Examples

* MongoDB
* DynamoDB
* Elasticsearch

---

Instagram example

SQL

* users
* photos
* follows
* comments

NoSQL

* preferences
* analytics
* behavior events

Real systems often use both.

---

# Database Indexes

Without index

Database scans every row.

With index

Database jumps directly to matching rows.

Like the index of a book.

Index columns that are queried frequently.

Example

```
posted_by

upload_time
```

Tradeoff

Indexes speed reads.

Indexes slow writes.

Rule

Measure first.

Index later.

---

# Caching

Purpose

Avoid repeated database work.

Architecture

```
App

↓

Redis

↓

Database
```

Cache hit

Serve from Redis.

Cache miss

Query DB then populate cache.

---

Good cache candidates

* trending posts
* popular profiles
* feed metadata

Also commonly stores

* sessions

---

Cache consistency

Problem

Database changes

↓

Cache still stale

Solutions

### TTL

Expire after fixed time.

Simple.

Eventually consistent.

---

### Active Invalidation

Delete cache immediately after write.

More work.

Always fresh.

---

Cache Stampede

Many cache entries expire simultaneously.

Mitigations

* randomized TTL
* request coalescing
* background refresh

---

# Replication

Architecture

```
Primary

↓

Replica 1

Replica 2
```

Writes

Primary only.

Reads

Primary + replicas.

Benefits

* availability
* read scaling

---

Replication Lag

Replicas slightly behind.

Creates

Eventual Consistency.

For latest user writes

Read from primary.

For normal traffic

Read replicas.

---

Failover

Primary dies.

Promote replica.

---

Replication ≠ Backup

Replication copies mistakes.

Need backups for recovery.

---

# Sharding

Replication solves read scaling.

Sharding solves storage scaling.

Split data across multiple databases.

```
Shard 0

Shard 1

Shard 2

Shard 3
```

Choose a shard key.

Usually

```
user_id
```

---

Problems

### Hot shard

One shard receives most traffic.

Need better key.

---

### Resharding

Modulo-based partitioning moves almost all data when adding shards.

Industry solution

Consistent Hashing.

Moves only small portions of data.

---

# Overall Architecture

Final architecture from the course:

```
                DNS
                 │
          Load Balancer
                 │
     ┌───────────┴───────────┐
     │                       │
 Stateless App Servers (N)
     │
 Redis
 ├── Cache
 └── Sessions
     │
     ├─────────────┐
     │             │
 PostgreSQL     MongoDB
 Structured     Unstructured
     │
 Primary
   │
Replicas
   │
(Optional)
Sharding
```

# Interview Takeaways

The course repeatedly emphasizes these habits:

* Clarify **functional** and **non-functional** requirements before designing.
* Ask about **users, scale, traffic patterns, latency, durability, and cost**.
* Justify every architectural component with a requirement ("We're adding Redis because reads dominate.").
* Start with the simplest architecture (single server → monolith → vertical scaling) and introduce complexity only when required.
* Explain **trade-offs**, not just technologies. Every solution (cache, replicas, microservices, sharding) solves one problem while introducing another.
* Think in terms of **failure modes** ("What happens if this component dies?" or "What happens when this becomes a bottleneck?").

## Key Mental Model

A useful progression for system design interviews is:

1. Gather requirements.
2. Sketch a simple architecture.
3. Identify the first bottleneck.
4. Add the smallest component that solves it.
5. Discuss the new trade-offs that component introduces.
6. Repeat as the system scales.

This iterative reasoning process is what interviewers typically want to see, rather than memorized architecture diagrams.
