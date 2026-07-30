---
origin: video-transcript
confidence: medium
sources:
  - ML system design interview walkthrough (course promotion omitted)
cleaned: 2026-07-30
---
# ML System Design Interview Notes

Pillar 9, detailed note 3. The ML-flavored variant of the design round: business problem
→ ML problem → data → approach, with the model as one component rather than the answer.
Base-vs-fine-tune-vs-RAG is covered deeper in the
[LLM fundamentals guide](../2-llm-fundamentals/interview-guide.md) §3.

## The Biggest Mistake

Don't start by talking about models.

❌ Wrong

> "I'd use XGBoost..."
> "I'd fine-tune GPT-4..."

Instead start with:

* Business problem
* User problem
* Success metrics
* Constraints

The model is just one component of the solution.

---

# ML System Design Framework

A good answer follows roughly this order:

```text
Business Problem

↓

Requirements Gathering

↓

Scope the ML Problem

↓

Data

↓

Model Selection

↓

Evaluation

↓

Deployment

↓

Monitoring

↓

Operations
```

Think like an **ML Engineer building a product**, not a researcher optimizing a model.

---

# Step 1: Understand the Business Problem

Ask questions first.

Examples:

* Who are the users?
* What problem are we solving?
* What does success look like?
* What are the business metrics?
* What are the engineering constraints?

Examples of constraints:

* Latency
* Budget
* Accuracy
* Throughput
* Privacy
* Compliance

Never assume requirements.

---

# Step 2: Define the ML Problem

Translate the product problem into an ML problem.

Business goal

> Recommend personalized wellness articles

Possible ML tasks

* Recommendation
* Classification
* Ranking
* Retrieval
* Summarization
* Text generation

Always identify:

* Inputs
* Outputs
* Objective function

ML is simply a tool for achieving the business goal.

---

# Step 3: Understand the Data

Questions to ask

* Where does data come from?
* Is it labeled?
* How much data exists?
* How fresh is it?
* Any privacy concerns?
* Any missing data?
* Any bias?

Without understanding the data, don't discuss models.

---

# Step 4: Choose the Right Approach

For GenAI systems there are three common choices:

## Option 1: Use the Base Model

Pros

* Fast
* Cheap
* Easy

Cons

* Doesn't know your domain

---

## Option 2: Fine-tune

Pros

* Learns specialized knowledge
* Better on repeated tasks

Cons

* Expensive
* Requires ML expertise
* Risk of catastrophic forgetting
* Must retrain for new tasks

Use when the model's behavior itself must change.

---

## Option 3: RAG (Usually Preferred)

Keep the model unchanged.

Instead:

* Retrieve relevant information
* Add it to the prompt at inference time
* Generate the answer

Advantages

* Cheaper
* Easier
* More scalable
* Knowledge stays up to date

RAG modifies the **context**, not the model.

---

# Inference Time vs Training Time

Training/Fine-tuning

Knowledge is baked into the model.

Inference

Retrieve information dynamically when the user asks a question.

```text
User Question

↓

Retrieve Context

↓

LLM

↓

Answer
```

This is why RAG can stay current without retraining.

---

# Tool Calling

Sometimes retrieving text isn't enough.

The model needs to perform actions.

Examples

* Search a database
* Call an API
* Look up inventory
* Execute code
* Book an appointment

Instead of answering from memory, the LLM delegates work to tools.

---

# Designing an End-to-End ML System

Think beyond the model.

Typical components:

```text
Product Requirements

↓

Data Pipeline

↓

Feature Engineering

↓

Model

↓

Serving Layer

↓

API

↓

Monitoring

↓

Retraining
```

Production systems are much larger than the model itself.

---

# Production Considerations

Don't stop after training.

Consider:

* Monitoring
* Logging
* Drift detection
* Retraining
* Privacy
* Compliance
* Maintenance

Especially for systems using user-generated content.

---

# Thinking Like an ML Engineer

Interviewers are looking for structured thinking.

A good answer sounds like:

> "First I'd clarify the business objective. Then I'd identify the users and success metrics. Next I'd examine the available data and determine the ML task. Only after understanding the requirements would I discuss candidate models and deployment."

This demonstrates product thinking rather than jumping straight into algorithms.

---

# Common Interview Questions

### Why not fine-tune?

Good answer:

* Expensive
* Slow
* Compute intensive
* Risk of catastrophic forgetting
* Must repeat for each new task

Often RAG or tool calling is sufficient.

---

### When should you use RAG?

When:

* Knowledge changes frequently
* Need company-specific information
* Need citations
* Don't want to retrain models

---

### What should you ask before designing a system?

* Who are the users?
* What problem are we solving?
* How is success measured?
* What are latency requirements?
* What data is available?
* What are privacy/compliance constraints?
* What is the expected scale?

---

# Interview Checklist

A strong ML system design answer should include:

* ✅ Business problem first
* ✅ Requirements gathering
* ✅ Success metrics
* ✅ User personas
* ✅ Data sources and quality
* ✅ ML task definition
* ✅ Model choice (with tradeoffs)
* ✅ RAG vs fine-tuning vs base model
* ✅ Evaluation metrics
* ✅ Deployment architecture
* ✅ Monitoring and maintenance
* ✅ Privacy and compliance

---

# Key Takeaways

* **Start with the problem, not the model.**
* **Frame everything around business objectives and user value.**
* **Treat ML as one component of a larger production system.**
* **Know when to use a base model, RAG, fine-tuning, or tool calling, and explain the tradeoffs.**
* **Demonstrate end-to-end thinking—from requirements through deployment and monitoring—as that's what interviewers for ML Engineer and Applied AI roles are typically evaluating.
