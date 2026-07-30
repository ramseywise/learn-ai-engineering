---
origin: article-synthesis
confidence: medium
sources:
  - JamWithAI substack posts + related AI system design articles
cleaned: 2026-07-30
---
# AI System Design Cheat Sheet (2026)

Pillar 9, detailed note 6. Component-by-component reference for the LLM request path:
gateway, rate limiting, caching, orchestrator, RAG pipeline, memory, tools, async work,
reliability, observability, security, cost. The organizing thesis: *AI system design
interviews are software system design interviews with LLM-specific components.*

Use [04-decision-tree.md](04-decision-tree.md) to choose between options; use this to look
up what a component *is*.

## The Interview Mindset

Interviewers aren't testing whether you know LangGraph or Pinecone.

They're testing whether you think like an engineer building a production AI product.

Always think in terms of:

* Reliability
* Scale
* Cost
* Latency
* Security
* Observability
* Tradeoffs

The LLM is only one service in the architecture. ([jamwithai.substack.com][1])

---

# A Standard AI Request Flow

This is the architecture I'd draw for almost every GenAI interview.

```text
Client

↓

API Gateway

↓

Authentication

↓

Rate Limiting

↓

Load Balancer

↓

Orchestrator

↓

Planner

↓

Retrieve Context

↓

Call Tools

↓

LLM

↓

Validation

↓

Response

↓

Logging + Monitoring
```

Then explain each component.

---

# 1. API Gateway

Every request enters through the gateway.

Responsibilities

* Authentication
* Authorization
* Routing
* Request validation
* Rate limiting
* Logging
* Multi-model routing

Never start your architecture at the LLM.

The API Gateway protects expensive GPU resources. ([jamwithai.substack.com][1])

---

# 2. Rate Limiting

AI systems are expensive.

Protect against

* Abuse
* Cost explosions
* Denial-of-wallet attacks

Common limits

* Requests/minute
* Tokens/minute
* Cost/day
* Concurrent sessions

Different users may have different quotas.

---

# 3. Load Balancing

Distribute traffic across inference servers.

Strategies

* Round robin
* Least loaded
* GPU-aware routing
* Model-specific routing

Health checks are especially important because models can fail independently. ([jamwithai.substack.com][1])

---

# 4. Caching

One of the biggest cost savers.

Common caches

### Response Cache

Repeated prompts

↓

Return previous answer

---

### Embedding Cache

Don't regenerate embeddings.

---

### Semantic Cache

If a new question is very similar to a previous one

↓

Reuse previous response

Useful because many users ask nearly identical questions. ([jamwithai.substack.com][1])

---

# 5. Orchestrator

The "brain" of the system.

Responsibilities

* Planning
* State management
* Tool selection
* Retry logic
* Error handling
* Memory retrieval

Frameworks

* LangGraph
* Temporal
* Custom state machine

---

# RAG Architecture

A production RAG system is much more than:

Documents

↓

Embeddings

↓

Vector Search

↓

LLM

Real systems have multiple stages. ([jamwithai.substack.com][2])

---

# Document Ingestion Pipeline

```text
Documents

↓

Parsing

↓

Cleaning

↓

Chunking

↓

Metadata

↓

Embeddings

↓

Vector Database
```

This runs offline.

---

# Query Pipeline

```text
User Question

↓

Rewrite Query

↓

Embedding

↓

Retrieve

↓

Hybrid Search

↓

Rerank

↓

Context Selection

↓

LLM
```

Runs online for every request.

---

# Better Retrieval

Vector search isn't enough.

Production systems combine:

* Semantic search
* Keyword search (BM25)
* Metadata filtering
* Hybrid retrieval
* Rerankers

Reranking often improves answer quality more than changing the embedding model. ([arXiv][3])

---

# Chunking

Poor chunking ruins retrieval.

Strategies

* Fixed-size chunks
* Sentence chunks
* Semantic chunks
* Proposition chunks
* Hierarchical chunks

Tradeoffs

Small chunks

* Better precision

- Lose context

Large chunks

* Better context

- Lower retrieval quality

---

# Metadata Matters

Every chunk should include metadata.

Examples

* Source
* Author
* Timestamp
* Document type
* Access permissions
* Version

Metadata filtering often improves retrieval more than changing embeddings.

---

# Memory ≠ RAG

One of the biggest interview topics.

Retrieval answers:

> "What documents are relevant?"

Memory answers:

> "What should this agent remember?"

Different problems. ([Oracle Blogs][4])

---

# Seven Memory Types

A useful mental model is:

| Memory     | Example                 |
| ---------- | ----------------------- |
| Working    | Current conversation    |
| Episodic   | Previous interactions   |
| Semantic   | Learned user facts      |
| Procedural | How to complete tasks   |
| Tool       | Previous tool outputs   |
| Scratchpad | Intermediate reasoning  |
| Long-term  | Persistent user profile |

Each has different retention and retrieval policies. ([Oracle Blogs][4])

---

# Memory Storage

Don't store everything in one database.

Typical architecture

Working memory

→ Redis

Semantic memory

→ Vector DB

Structured facts

→ PostgreSQL

Documents

→ Object Storage

Conversation logs

→ S3/Data Lake

Choose storage based on access patterns, not convenience. ([Oracle Blogs][4])

---

# Tool Calling

The LLM shouldn't perform actions directly.

Instead:

Model

↓

Generate Tool Call

↓

Application validates

↓

Execute Tool

↓

Return Result

↓

Model continues

Never trust raw model outputs to invoke external systems.

---

# Asynchronous Work

Some tasks shouldn't block the user.

Examples

* Document ingestion
* Embedding generation
* Batch evaluation
* Large summarization jobs
* Retraining

Pattern

```text
API

↓

Queue

↓

Workers

↓

Database
```

Use queues to improve resilience and throughput. ([jamwithai.substack.com][1])

---

# Reliability Patterns

Every production AI system should include:

Retry

↓

Fallback Model

↓

Circuit Breaker

↓

Graceful Degradation

Examples

Primary model unavailable

↓

Switch to backup model

Vector DB unavailable

↓

Keyword search

Retriever timeout

↓

Answer with partial context

---

# Observability

You need traces—not just logs.

Track

* Model version
* Prompt version
* Retrieved chunks
* Tool calls
* Token usage
* Latency
* Cost
* Failures
* User feedback

You should be able to replay any request end-to-end.

---

# Evaluation

Evaluate every stage.

Retrieval

* Recall@k
* MRR
* nDCG

Generation

* Faithfulness
* Groundedness
* Hallucination rate

Agents

* Task completion
* Tool accuracy
* Planning success

System

* Latency
* Cost
* User satisfaction

Evaluation should be continuous, not a one-time benchmark. ([arXiv][5])

---

# Security

Treat everything as untrusted.

Includes

* User prompts
* Retrieved documents
* Tool outputs
* LLM responses

Defend against

* Prompt injection
* Data leakage
* Unauthorized tool use
* Jailbreaks
* Memory poisoning

Always validate tool arguments before execution. ([arXiv][5])

---

# Cost Optimization

Large production systems optimize aggressively.

Strategies

* Route simple tasks to smaller models
* Cache embeddings and responses
* Retrieve fewer but higher-quality chunks
* Compress context before prompting
* Batch embedding jobs
* Stream responses
* Auto-scale GPU workers

Track **cost per successful task**, not just cost per request. ([jamwithai.substack.com][1])

---

# Interview Questions to Expect

Be ready to discuss:

* Design a production RAG system.
* Design an AI coding assistant.
* Design an enterprise knowledge assistant.
* Design a customer support agent.
* How would you scale an LLM API to 100k users?
* How would you reduce latency and token costs?
* When would you choose RAG vs. fine-tuning?
* How would you monitor hallucinations?
* How would you prevent prompt injection?
* How would you evaluate an AI agent?

---

# The Mental Model

Think of an AI system as **three interacting layers**:

```text
Application Layer
-----------------
API Gateway
Authentication
Rate Limiting
Orchestrator
Business Logic

↓

AI Layer
---------
Models
RAG
Memory
Tools
Planning
Evaluation

↓

Infrastructure Layer
--------------------
GPU Inference
Queues
Caches
Databases
Vector DB
Storage
Monitoring
Autoscaling
```

Most interview questions can be answered by walking through these layers, discussing the components involved and the tradeoffs between reliability, latency, cost, and complexity. That structured approach is what interviewers for senior AI/ML engineering roles are typically looking for. ([jamwithai.substack.com][1])

[1]: https://jamwithai.substack.com/p/system-design-for-ai-engineers-7?utm_source=chatgpt.com "System Design for AI Engineers: 7 patterns you should know in your interviews"
[2]: https://jamwithai.substack.com/p/the-infrastructure-that-powers-rag?utm_source=chatgpt.com "The Infrastructure That Powers RAG Systems"
[3]: https://arxiv.org/abs/2601.05264?utm_source=chatgpt.com "Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval-Augmented Generation Systems"
[4]: https://blogs.oracle.com/developers/from-rag-to-memory-systems-building-stateful-ai-architecture?utm_source=chatgpt.com "From RAG to Memory Systems: Building Stateful AI Architecture | developers"
[5]: https://arxiv.org/abs/2603.07379?utm_source=chatgpt.com "SoK: Agentic Retrieval-Augmented Generation (RAG): Taxonomy, Architectures, Evaluation, and Research Directions"
