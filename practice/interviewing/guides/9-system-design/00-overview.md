---
units:
  - data-engineering/01-storage-and-compute-foundations
  - ai-engineering/07-inference-engineering/notes/06-serving-at-scale.md
  - generative-ai/02-rag-retrieval/notes/07-rag-in-production.md
---
# Pillar 9 — System Design (putting the pieces together)

The integration pillar: given a vague problem, design the whole system — components,
data flow, trade-offs, failure modes, measurement. Largely the *method* for deploying
pillars 3–8 under time pressure, plus the generic backend substrate the LLM-flavored
round assumes (scaling, storage, APIs). The highest-weight technical round in AIE/MLE
interviews.

## Learn it in the curriculum

The teaching lives in the chapters. Work them in this order, then use the [interview guide](interview-guide.md) as the recall sheet.

| Chapter | What it covers |
|---|---|
| [Storage and compute foundations](../../../../data-engineering/01-storage-and-compute-foundations/README.md) | Data models, replication, partitioning, consistency: the backend substrate |
| [Serving at scale](../../../../ai-engineering/07-inference-engineering/notes/06-serving-at-scale.md) | The model-serving tier of a design |
| [RAG in production](../../../../generative-ai/02-rag-retrieval/notes/07-rag-in-production.md) | The most common design prompt, run for real |

## Decision tree

[04-decision-tree.md](04-decision-tree.md) has **the four spines**: pick one and walk it node by node
under pressure.

## Test yourself

[interview-guide.md](interview-guide.md) · rounds:
[system-design-round](../../rounds/system-design-round/README.md) (logistics + curveballs),
[case-study](../../rounds/case-study/README.md) (the business-flavored variant).
