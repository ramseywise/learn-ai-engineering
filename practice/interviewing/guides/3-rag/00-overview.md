---
units:
  - generative-ai/02-rag-retrieval
  - ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher.md
---
# Pillar 3 — RAG (retrieval-augmented generation)

The default pattern for giving an LLM knowledge it wasn't trained on: chunk documents,
embed them, retrieve the relevant pieces, ground the answer in them. Most enterprise LLM
systems are RAG systems — and most interview design questions have a RAG core.

## Learn it in the curriculum

The teaching lives in the chapters. Work them in this order, then use the [interview guide](interview-guide.md) as the recall sheet.

| Chapter | What it covers |
|---|---|
| [RAG and retrieval](../../../../generative-ai/02-rag-retrieval/README.md) | The pipeline, search, chunking, reranking, production |
| [Evaluating RAG and grounding](../../../../generative-ai/08-eval/notes/07-evaluating-rag-and-grounding.md) | Measuring retrieval and faithfulness; pairs with pillar 6 |
| [KG-RAG and text-to-Cypher](../../../../ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher.md) | Knowledge graphs as the next step |

## Test yourself

[interview-guide.md](interview-guide.md) · rounds:
[system-design-round](../../rounds/system-design-round/README.md),
[technical-questions](../../rounds/technical-questions/README.md).
