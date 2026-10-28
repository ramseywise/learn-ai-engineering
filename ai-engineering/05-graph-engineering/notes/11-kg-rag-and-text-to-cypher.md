---
origin: book-and-course-condensed
sources:
  - sources/kg-and-llms-in-action/13-kg-powered-rag.md
  - sources/kg-and-llms-in-action/14-natural-language-kg-questions.md
  - sources/kg-and-llms-in-action/15-qa-agent-with-langgraph.md
  - notebooks/knowledge-graphs-for-rag/notes/Lesson_7.md
  - https://arxiv.org/abs/2404.16130
  - https://neo4j.com/docs/neo4j-graphrag-python/current/
confidence: medium-high
cleaned: 2026-10-28
---
# 11 — KG-Powered RAG and Text-to-Cypher

> Vector search finds text that sounds like the question. A graph finds things connected to the answer. Text-to-Cypher reaches the graph from natural language, and it is reliable only as a generate-then-verify loop.

---

## Where it sits

[Note 10](10-building-kgs-with-llms.md) built the graph. This note reads from it. Retrieval in general is covered in [02-context note 04](../../02-context-engineering/notes/04-retrieval.md) and evaluating it in [06-eval note 07](../../06-eval/notes/07-evaluating-rag-and-grounding.md). This note adds what a graph changes. It ends back in Track A: the book's QA agent is a LangGraph pipeline with a retry edge.

---

## Where vector RAG breaks

Ch13 lists the failure modes of chunk-and-embed retrieval:

| Failure | What happens |
|---|---|
| **Context fragmentation** | Chunks are retrieved independently. A fact split across chunks or documents needs every piece retrieved, in order, near the top. |
| **Embedding compression** | One vector per chunk loses entity-level detail. Rare domain terms embed poorly. |
| **Noise (distraction)** | Loosely related chunks dilute the context and degrade the answer. |
| **Misses** | Similarity optimises for closeness, not coverage, so aggregate questions ("what are the main themes?") get partial answers. |

The ch13 worked example: for "How is Lauritsen related to cyclotron research?", the three top results scored 0.906, 0.903 and 0.902 by cosine similarity, and **only the first mentioned Lauritsen at all**. Embeddings encode overall meaning. They don't guarantee that a named entity is present.

Ch14 shows the consequence. Remove one witness statement from the retrieved context and the model **reverses its conclusion with the same confidence**. RAG output is bounded by retrieval completeness, and the model can't tell that something is missing.

---

## What a graph adds

| Capability | How |
|---|---|
| **Multi-hop** | Traverse typed edges instead of hoping the hops co-occur in one chunk |
| **Entity-exact retrieval** | "Documents that mention *all* of these entities", which vector search can't promise |
| **Aggregation** | `count`, `sum` and `collect` over the whole graph instead of over a top-k sample |
| **Metadata routing** | Filter by date, source or author as graph properties ("the latest version of this regulation") |
| **Traceable answers** | Return the path. A person can check each edge. |
| **Composed retrieval** | Resolve "the head of group X" in the KG, then search a document store for that name |

The book's design advice: make the graph **text-attributed** (nodes and edges carry descriptive text) and **text-paired** (every node and edge links back to its source documents). Then it can serve as a structured store and also as a more precise document retriever.

### The evidence

The primary source is Microsoft Research's GraphRAG paper, Edge et al., *From Local to Global: A Graph RAG Approach to Query-Focused Summarization* ([arXiv 2404.16130](https://arxiv.org/abs/2404.16130)). It builds an entity graph, detects communities and pre-summarises them, then answers **global sensemaking** questions over corpora of about 1M tokens. Against vector RAG it reports:

- **Comprehensiveness** win rates of 72–83% (podcast transcripts) and 72–80% (news).
- **Diversity** win rates of 75–82% and 62–71%.
- Vector RAG **wins on directness** (concise answers).

The judge was an LLM in head-to-head comparisons, not people and not a ground-truth accuracy measure. So the result is "graph community summaries help whole-corpus questions". It does not show that graphs are more accurate than vectors in general.

The 53.4% vs. 42.9% multi-hop figures that graph-engineering.md §9 quoted come from a vendor blog with no stated method. They're dropped here. If you want a number for your own data, [KG Lab 6](../practice/02-knowledge-graph-labs.md#lab-6--text-to-cypher-as-generate-then-verify) measures it.

---

## Retrieval modes

| Mode | How it retrieves | Use when | Fails when |
|---|---|---|---|
| **Vector** | Embed the question, top-k chunks | Local lookups: "find the passage about X" | Multi-hop, aggregates, exact entity constraints |
| **Graph traversal (canned)** | Fixed Cypher templates keyed by entities from the question (shortest paths, k-hop neighbourhood) | Known question shapes; production paths | A question shape you didn't template |
| **Text-to-Cypher** | LLM writes Cypher from the schema | Open-ended structured questions over a well-described schema | Schema is large or badly named; no validator |
| **Hybrid** | Vector to find entry chunks or entities, then expand through the graph (L5's `NEXT` window, entity neighbourhoods) | Text-heavy corpora where the graph adds context to found passages | Entry points are wrong, so expansion makes things worse |
| **Global (GraphRAG communities)** | Pre-summarised communities, then map-reduce | "What are the themes across everything?" | Specific factual lookups; high indexing cost |

**Default order:** start with vector. Add canned traversals for the multi-hop question shapes you can name. Add text-to-Cypher only for the long tail, and only with a validator. Ch13 takes the same position: its ReAct agent's tools use **precanned Cypher queries** because free-form generation fails too often, with a vector-search tool as a fallback. This is the agency rule from [note 02](02-graph-primitives.md) again.

---

## Text-to-Cypher

### Think like the expert: schema first

Ch14's method is to ask what a domain expert would do. An expert doesn't read paragraphs. They know the **schema** and build a **constrained traversal**:

1. **Parse** the question into entities (`Car {color, model}`), relationships (owns, captured by) and constraints (red, Camaro, this area, this time window).
2. **Map** those onto schema labels and relationship types.
3. **Construct** the Cypher.

```cypher
MATCH path = (v:Vehicle)<-[:PLATE_READ]-(e:CameraEvent)-[:HAS_EVENT]-(c:ANPRCamera)
WHERE v.model = "Camaro" AND v.color = "Red"
  AND e.timestamp >= $startTime AND e.timestamp <= $endTime
  AND point.distance(c.position, $areaCenter) < $areaRadius
RETURN path
```

### Give the model an LLM-ready schema

Raw `apoc.meta.schema` output is the wrong input. Ch14 transforms it:

- **Filter** with a skip list: drop internal labels, embeddings and housekeeping properties.
- **Annotate** with `/* comments */` on labels, relationship types and properties: value encodings ("`status`: 1 = open"), direction semantics, units.
- **Name things well in the first place.** A model can't use a relationship called `REL_7`.

### Prompt shape

The book's prompt has nine parts: task and `<QUESTION>`; `<SCHEMA>` with annotations; requirements that depend on the intent (a map needs coordinates, a graph view needs named relationships); few-shot examples; the user's current selection; KG-specific notes; the question restated; the requirements restated; and the output format.

**Order the output fields so reasoning comes first:**

```json
{
  "relationships": ["..."],   // the edges it intends to traverse, before the query
  "reasoning": "...",         // the plan
  "query": "<Cypher>",        // written last, consistent with the two fields above
  "success": true
}
```

Listing `relationships` first reduces invented relationship types, because the model commits to the schema before writing the query. This is chain-of-thought ordering ([01-prompt note 03](../../01-prompt-engineering/notes/03-core-techniques.md)): an answer written before its reasoning is a guess, and the reasoning that follows only rationalises it. Few-shot examples have to follow the same format.

### Intent detection

Ch14 classifies at two levels before generating anything:

1. **Request type:** a data question, a question about the system, or feedback or a complaint. Only data questions go on to Cypher.
2. **Output form:** graph, table, chart or map. This changes what the query must `RETURN`.

### The failure to expect

In course L7, LangChain's `GraphCypherQAChain` was told to follow the schema and still summed a `value` property on `Company`, which doesn't exist. The property is on the `OWNS_STOCK_IN` relationship. **One few-shot example with the right pattern fixed it.** Text-to-Cypher fails on plausible-looking schema mistakes, and those are exactly what a schema check catches.

---

## The QA agent as a Track A graph

Ch15 implements the expert pipeline in LangGraph:

```
START → intent_detection → schema_extraction → text_to_cypher → query_execution
                                  ▲                                   │
                                  └────────── "retry" (≤3) ───────────┤
                                                                      ├── "summarize" → generate_summary → END
                                                                      └── "END" → END
```

```python
def post_query_execution(state):
    if state["results_error"] is not None:
        return "retry" if state["retries"] < 3 else "END"
    return "summarize" if state["output_type"] in ("map", "graph") else "END"
```

Several Track A patterns appear here:

- **Generate-then-verify** ([note 02](02-graph-primitives.md)). The database is the verifier, and its error message goes back into the prompt through the `information` field.
- **A bounded back-edge** ([note 07](07-failure-modes-at-scale.md)). It stops after three retries.
- **Typed state as the audit trail** ([note 03](03-state-and-reducers.md)). `AgentState` keeps `output_type_reason`, `query_reasoning` and `results_error`, so every intermediate decision can be inspected. The book points out that this also gives you a dataset of failures and few-shot candidates for free.
- **A checkpointer** ([note 04](04-durable-execution-and-interrupts.md)). `graph.compile(checkpointer=self.memory)`.

What the book's version lacks is a validator that runs **before** execution. Use `EXPLAIN` to check that the query parses and plans without running it, and compare the labels and relationship types it uses against the schema. A wrong query is then caught before it reaches a live database, and the repair is cheaper. That is the lab exercise.

### Summarise as a complement

Ch15 summarises only when the output is a graph or a map, and only when the question asked for analysis. A summary should point out what isn't obvious in the visualisation, not repeat it.

---

## Working reference

`~/.claude/refs/agent-context.md`: retrieval and context assembly. `~/.claude/refs/agent-reliability.md`: bounded retries.

Depth: [ch13](../sources/kg-and-llms-in-action/13-kg-powered-rag.md), [ch14](../sources/kg-and-llms-in-action/14-natural-language-kg-questions.md), [ch15](../sources/kg-and-llms-in-action/15-qa-agent-with-langgraph.md). Practice: [KG Lab 5](../practice/02-knowledge-graph-labs.md#lab-5--chat-with-the-10-k-graph) and [KG Lab 6](../practice/02-knowledge-graph-labs.md#lab-6--text-to-cypher-as-generate-then-verify).

---

→ Next: [12-kg-as-shared-agent-memory.md](12-kg-as-shared-agent-memory.md): where the two kinds of graph meet.
