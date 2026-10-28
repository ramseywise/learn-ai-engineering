---
origin: planning
sources:
  - notebooks/knowledge-graphs-for-rag/
  - sources/kg-and-llms-in-action/
  - https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide
confidence: medium
cleaned: 2026-10-28
---
# P2 — Knowledge Graph Labs

> Run the Neo4j course in order, model a domain you know, then build a graph you can measure, query and trust, and finally use it as shared memory for a swarm.

These labs follow notes [09](../notes/09-kg-fundamentals-and-cypher.md)–[13](../notes/13-graph-ml-and-gnns.md). Labs 1, 3 and 5 are the course notebooks in [notebooks/knowledge-graphs-for-rag/code/](../notebooks/knowledge-graphs-for-rag/code/), with study notes in [notebooks/knowledge-graphs-for-rag/notes/](../notebooks/knowledge-graphs-for-rag/notes/). The other labs are new builds.

---

## Ground rules

- **Neo4j.** Use a local Neo4j (Desktop or Docker, `neo4j:5`) or an AuraDB free instance. The course dumps are `code/data/neo4j_L2.dump` and `neo4j_L7.dump`.
- **Credentials.** `code/.env` holds live API and Neo4j credentials. It is gitignored and has never been committed. Use your own values, never paste them into notes, and rotate them if the folder is ever shared.
- **Gold sets first.** Hand-label the evaluation data in Labs 4, 6 and 7 *before* you build. Otherwise you'll label toward what the system already does.
- **Provenance from the first write.** Every node and edge you create records its source, so Lab 8 is possible.

A run log, one row per run:

```markdown
| Lab | Variant | Items | Precision | Recall | False merges | Tokens | Wall-clock | Notes |
|---|---|---|---|---|---|---|---|---|
```

---

## Lab 1 — Cypher on the movies graph

*Note [09](../notes/09-kg-fundamentals-and-cypher.md). Course `L2-query_with_cypher.ipynb`, Lessons 0–2.*

1. Restore `neo4j_L2.dump`, or load the movies dataset with `:play movies`.
2. Work through the notebook, then write these queries without looking: co-actors of an actor; actors within 3 hops of Kevin Bacon (a bounded variable-length path); the shortest path between two actors; the top 5 directors by movie count.
3. Add a uniqueness constraint on `Person.name`, then try to `CREATE` a duplicate. Next, `MERGE` on `{name, born}` with a misspelled `born`, and explain the duplicate it creates.

## Lab 2 — Model this repo as a KG

*Note [09](../notes/09-kg-fundamentals-and-cypher.md).*

1. Write a small script that parses `ai-engineering/*/notes/*.md`. Each note becomes a `(:Note {id, pillar, title})`, each frontmatter source becomes a `(:Source)`, and markdown links between notes become `REFERENCES` edges.
2. Read step 3's questions first: purpose-driven construction (note 09) means the edge types exist to answer them. Then hand-add typed edges: `DEPENDS_ON` (from "Where it sits" and `→ Next`) and `SUPERSEDES` (for example, these notes supersede sections of `graph-engineering.md`).
3. Write five queries, including the following: what does note 12 transitively depend on (`*1..5`)? Which notes have no incoming references? Which sources are cited by more than one pillar?
4. Run the same questions with every edge typed `RELATED_TO`. Write down which questions you can no longer answer. That list is the argument for typed edges, and you didn't need a vendor's 18% to make it.

## Lab 3 — Build the 10-K graph

*Note [10](../notes/10-building-kgs-with-llms.md). Course `L3`–`L6`.*

1. **L3–L4.** Chunk the Form 10-K text into `Chunk` nodes, embed them, and create the vector index.
2. **L5.** Link the chunks with `NEXT` and add window retrieval. Compare top-k with and without the ±1 window on three questions.
3. **L6.** Merge Form 13 managers onto the same `Company` nodes. Add the uniqueness constraint *before* the import, and count how many duplicates it prevents compared with running without it.

## Lab 4 — Tiered extraction with a false-merge rate

*Note [10](../notes/10-building-kgs-with-llms.md). Reference: Anthropic's [KG construction cookbook](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide).*

1. Choose 10–20 documents with plenty of people and organisations (archive letters, Wikipedia summaries, your own docs). Hand-label 50 mentions with their gold canonical entity.
2. **Extract** with a Haiku-class model under a JSON schema (Pydantic or tool schema). Output *mentions* with descriptions, not entities.
3. **Resolve** two ways: (a) string similarity followed by WCC, as in ch6; (b) a Sonnet-class model clustering names together with their descriptions, as in the cookbook. Write the result as `RESOLVES_TO` edges with `evidence` and `confidence`. **Never merge destructively.**
4. Report entity precision and recall, false-merge rate and false-split rate for (a) and (b).
5. Undo one resolution by deleting its `RESOLVES_TO` edge, and confirm the graph returns to its earlier state. If that fails, your resolution isn't reversible yet.

## Lab 5 — Chat with the 10-K graph

*Note [11](../notes/11-kg-rag-and-text-to-cypher.md). Course `L7-chat_with_kg.ipynb`.*

1. Restore `neo4j_L7.dump` and run `GraphCypherQAChain` over it.
2. Reproduce the course failure: ask for total investment by a manager and check whether the generated query sums a `value` on `Company`, which doesn't exist. Fix it with one few-shot example, then remove the example and fix it instead with a schema annotation (`/* value lives on OWNS_STOCK_IN */`). Record which fix holds up on five paraphrases of the question.

## Lab 6 — Text-to-Cypher as generate-then-verify

*Notes [11](../notes/11-kg-rag-and-text-to-cypher.md), [02](../notes/02-graph-primitives.md). Start from [templates/generate-then-verify.py](../templates/generate-then-verify.py).*

1. **Generate.** An LLM node writes JSON with the fields `relationships`, `reasoning`, `query` and `success`, in that order, from an annotated schema.
2. **Validate deterministically.** Run `EXPLAIN <query>`. Check that every label and relationship type in the query exists in the schema and that variable-length paths are bounded. On failure, route back to the generator with the error in state. Stop after 3 attempts.
3. **Execute** only queries that pass validation, as a read-only user.
4. Write 20 multi-hop questions with gold answers **and gold paths**. Compare vector-only, hybrid (vector entry plus graph expansion) and text-to-Cypher. Score whether the answer is correct, whether the path is valid, and tokens used. Record the first-pass validity rate and the rate after retries.

## Lab 7 — Swarm with and without shared memory

*Note [12](../notes/12-kg-as-shared-agent-memory.md). Use [templates/fan-out-merge.py](../templates/fan-out-merge.py) and [templates/graph-update.schema.json](../templates/graph-update.schema.json).*

1. Fan out N = 5–10 research workers over one corpus, giving each a slice or a sub-question.
2. **Run A.** No shared state. Each worker returns prose, and the synthesiser reads everything.
3. **Run B.** Each worker publishes `GraphUpdate`s, validated against the schema with provenance required, into a shared NetworkX `MultiDiGraph` or Neo4j. The synthesiser queries a bounded subgraph and must cite edges.
4. Compare redundant findings (how many workers reported the same fact), synthesiser input tokens, total tokens, and answer quality on 10 questions graded on answer and path.

## Lab 8 — Contamination drill

*Note [12](../notes/12-kg-as-shared-agent-memory.md).*

1. In the Lab 7 run B graph, inject one false merge by adding `RESOLVES_TO` from two distinct people to a single canonical, under a fake `run_id`.
2. Re-run the 10 questions and list every answer that changed. Trace each change back to the bad edge.
3. Roll back **using provenance alone**: delete everything carrying that `run_id`. Re-run and confirm the answers are restored.
4. Write one paragraph on what the validator would have needed in order to reject the merge at write time.

## Lab 9 — Predict missing links

*Note [13](../notes/13-graph-ml-and-gnns.md). Book ch9–12.*

1. **Baseline.** On `nx.karate_club_graph()`, reproduce ch9's three feature sets (degree; Node2Vec; degree plus neighbours in each faction) with the same logistic regression. Run each 10 times and report the mean and spread of F1. Then tune Node2Vec (`walk_length`, `num_walks`) until it matches the homophily features, or explain why it can't.
2. **Link prediction on your own graph.** Take the Lab 2 repo graph, or the Lab 7 run B graph. Hold out 10% of `REFERENCES` or `DEPENDS_ON` edges and sample the same number of non-edges. Score the candidates two ways: (a) manual pair features such as common neighbours, Adamic–Adar and DWPC over typed paths; (b) a GraphSAGE encoder with a dot-product decoder (PyG, `RandomLinkSplit` with `disjoint_train_ratio`). Report precision, recall and false-positive rate at a fixed threshold.
3. **Write back safely.** Publish the top 20 predictions as `GraphUpdate`s with `predicted: true`, the model's confidence and the training `run_id`. Confirm that your Lab 6 queries ignore them by default and pick them up only when asked to.
4. Read the 20 by hand. How many are real missing links, how many are hub artefacts, and did DWPC or the GNN produce fewer artefacts?

---

← Track A labs: [01-agent-graph-labs.md](01-agent-graph-labs.md)
