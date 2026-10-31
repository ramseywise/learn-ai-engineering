---
origin: planning
sources:
  - https://docs.langchain.com/langgraph
  - generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main/
  - https://www.deeplearning.ai/short-courses/knowledge-graphs-rag/
  - sources/kg-and-llms-in-action/
  - https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide
confidence: medium
cleaned: 2026-10-31
---
# Graph Engineering — Exercises

Two tracks, one file. **Part A** (labs A1–A7) grows one agent graph a chapter at a time, following notes 01–08. **Part B** (labs B1–B9) builds, queries and trusts a knowledge graph, following notes 09–13. The code each lab starts from is inline in the notes.

---

## Part A — Agent graph labs

> One graph, grown a chapter at a time. Generate-then-verify gains state, checkpoints, a subgraph, fault guards and tracing.

These labs continue the [loop labs](../../04-loop-engineering/practice/exercises.md). Warm up with the LangGraph course notebooks in [AI-Agents-in-LangGraph-main](../../../generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main/) (Lesson 1 ReAct from scratch, Lesson 2 LangGraph components, Lesson 4 persistence and streaming) if LangGraph is new to you.

---

### Ground rules (Part A)

- **One task, one model** for all labs, so the topology is the only thing that changes. Pick a task with a checkable output: code with tests, JSON against a schema, a summary graded against a rubric.
- **Branch per lab**: `graph-gtv`, `graph-fanout`, `graph-checkpoint`, `graph-subgraph`, `graph-breakeven`, `graph-faults`, `graph-trace`.
- **Measure every run.** The point of each lab is a number, not a working demo.
- Copy the code from the notes into a scratch file and run it with `uv run --with langgraph --with langchain-anthropic python <file>`. The fan-out example in note 03 runs offline with `--with langgraph` alone.

A run log, one row per run:

```markdown
| Lab | Topology | Runs | Pass rate | Tokens / run | Wall-clock / run | Stop reason | Notes |
|---|---|---|---|---|---|---|---|
```

---

### A1 — Generate-then-verify

*Notes [01](../notes/01-graph-vs-loop.md), [02](../notes/02-graph-primitives.md).*

1. Re-express your 04-loop agent loop as a `StateGraph` with **one node and a conditional self-edge**. Confirm it behaves the same. A loop is a one-node graph.
2. Copy the generate-then-verify graph from [note 02](../notes/02-graph-primitives.md#the-first-graph-generate-then-verify). Put real deterministic checks in `validate`.
3. **Agency audit.** Find one LLM call that could be code, or one agent that could be a single call. Change it. Record the change in tokens and in run-to-run variance over 10 runs.

**Done when:** you can say which node is the most expensive and whether it needs to be.

### A2 — Fan-out and merge

*Note [03](../notes/03-state-and-reducers.md).*

1. Run the fan-out example in [note 03](../notes/03-state-and-reducers.md#dynamic-fan-out-the-send-api). Remove the reducer on `findings` and run again; read the `InvalidUpdateError`.
2. Replace `operator.add` with a custom dedupe reducer, and give two items the same finding to prove it works.
3. **True-dependency test.** Take a sequential pipeline you own. Mark each edge "reads previous output" or "incidental". Rewrite the incidental ones as a fan-out and measure wall-clock time.

**Done when:** every key in your state has one writer or a reducer, and you can say which.

### A3 — Checkpoint and interrupt

*Note [04](../notes/04-durable-execution-and-interrupts.md).*

1. Swap `InMemorySaver` for a SQLite checkpointer (`langgraph-checkpoint-sqlite`).
2. Add a "publish" node that calls `interrupt()` before its side effect. Run to the interrupt, inspect with `get_state`, **edit** the draft with `update_state`, then resume with `Command(resume=...)`.
3. **Crash and resume.** Kill the process mid-run. Restart with the same `thread_id` and confirm it continues from the last checkpoint.
4. **Time travel.** Use `get_state_history` to find the checkpoint before a bad step. Fork from it with a corrected state.
5. Put a print statement before the `interrupt()` call and watch it run twice. Move the side effect so that doesn't matter.

**Done when:** a run survives a kill, and a human can correct it mid-run.

### A4 — Subgraphs and the parallel review graph

*Note [05](../notes/05-topology-patterns.md).*

1. Build the parallel review graph: security, logic and style reviewers in parallel → synthesiser → pass/fail gate.
2. Compile it and embed it as **one node** in a parent planner → worker → review graph. Use a wrapper node that maps parent state to the subgraph's input.
3. Compare with a sequential version (the three reviewers in a row) over 10 runs: wall-clock time and tokens. Is it ~3× faster, as flowtivity claims?
4. **Same topology in Claude Code.** Re-implement the reviewers as `.claude/agents/` subagents, with a hook as the pass/fail gate. Write down what you lost (typed state, checkpoints) and what you gained.

### A5 — Break-even measurement

*Note [06](../notes/06-when-not-to-build-a-graph.md).*

1. Run the same task as a single loop and as the A4 graph, 20 trials each. Record tokens, wall-clock time and pass rate.
2. Make the task harder (or the model weaker) until the loop's pass rate drops. Find where the graph stops paying for itself.
3. **Split the verifier first.** Take a loop whose verifier judges several criteria. Split it into per-criterion checks *inside the loop* and measure. Only then compare with the graph.

**Done when:** you have your own break-even number, and you no longer need flowtivity's.

### A6 — Fault injection

*Note [07](../notes/07-failure-modes-at-scale.md).*

Break the A4 graph on purpose, one fault at a time:

| Fault | How | Expect | Guard |
|---|---|---|---|
| Oscillation | Two nodes that always route to each other | `GraphRecursionError` | Attempt counter + `recursion_limit` |
| Race | Two parallel branches write one key with no reducer | `InvalidUpdateError` | Reducer or single writer |
| Self-agreement | Give the reviewer the generator's reasoning | Pass rate up, quality down | Isolated reviewer context |
| Unbounded fan-out | `Send` over a 500-item list | Cost spike | Cap N |

For each, write how you detected it and the guard that fixed it.

**Anchor drill.** Add a frozen held-out set the graph can't edit. Let a reviewer prompt be tuned against the training set. Show the training score climbing while the held-out score falls.

### A7 — Trace and attribute

*Note [08](../notes/08-governance-and-production.md).*

1. Instrument the A4 graph so every model call carries `graph_id`, `run_id` and `node_id` (LangSmith, or OpenTelemetry spans).
2. Run it 10 times and produce a per-node cost table. Find the node that dominates spend.
3. Score the graph against the seven-question checklist in note 08. Fix the two weakest answers.

---

## Part B — Knowledge graph labs

> Run the Neo4j course in order, model a domain you know, then build a graph you can measure, query and trust, and finally use it as shared memory for a swarm.

These labs follow notes [09](../notes/09-kg-fundamentals-and-cypher.md)–[13](../notes/13-graph-ml-and-gnns.md). Labs B1, B3 and B5 follow DeepLearning.AI's [*Knowledge Graphs for RAG*](https://www.deeplearning.ai/short-courses/knowledge-graphs-rag/) (Neo4j, 2024). Its hosted notebooks come with a database already loaded, and the key Cypher from each lesson is in notes 09–11. The other labs are new builds.

---

### Ground rules (Part B)

- **Neo4j.** Use the course's hosted notebooks, a local Neo4j (Desktop or Docker, `neo4j:5`) with the APOC and GenAI plugins, or an AuraDB free instance.
- **Credentials.** Keep API and Neo4j credentials in a gitignored `.env`. Never paste them into notes, and rotate them if the file is ever shared.
- **Gold sets first.** Hand-label the evaluation data in Labs B4, B6 and B7 *before* you build. Otherwise you'll label toward what the system already does.
- **Provenance from the first write.** Every node and edge you create records its source, so B8 is possible.

A run log, one row per run:

```markdown
| Lab | Variant | Items | Precision | Recall | False merges | Tokens | Wall-clock | Notes |
|---|---|---|---|---|---|---|---|---|
```

---

### B1 — Cypher on the movies graph

*Note [09](../notes/09-kg-fundamentals-and-cypher.md). Course lessons 1–2 (querying with Cypher).*

1. Load the movies dataset with `:play movies` ([note 09](../notes/09-kg-fundamentals-and-cypher.md#neo4j-and-cypher) has the details).
2. Work through the course lesson, then write these queries without looking: co-actors of an actor; actors within 3 hops of Kevin Bacon (a bounded variable-length path); the shortest path between two actors; the top 5 directors by movie count.
3. Add a uniqueness constraint on `Person.name`, then try to `CREATE` a duplicate. Next, `MERGE` on `{name, born}` with a misspelled `born`, and explain the duplicate it creates.

### B2 — Model this repo as a KG

*Note [09](../notes/09-kg-fundamentals-and-cypher.md).*

1. Write a small script that parses `ai-engineering/*/notes/*.md`. Each note becomes a `(:Note {id, pillar, title})`, each frontmatter source becomes a `(:Source)`, and markdown links between notes become `REFERENCES` edges.
2. Read step 3's questions first: purpose-driven construction (note 09) means the edge types exist to answer them. Then hand-add typed edges: `DEPENDS_ON` (from "Where it sits" and `→ Next`) and `SUPERSEDES` (for example, these notes supersede sections of `sources/graph-engineering-deep-note.md`).
3. Write five queries, including the following: what does note 12 transitively depend on (`*1..5`)? Which notes have no incoming references? Which sources are cited by more than one pillar?
4. Run the same questions with every edge typed `RELATED_TO`. Write down which questions you can no longer answer. That list is the argument for typed edges, and you didn't need a vendor's 18% to make it.

### B3 — Build the 10-K graph

*Note [10](../notes/10-building-kgs-with-llms.md). Course `L3`–`L6`.*

1. **L3–L4.** Chunk the Form 10-K text into `Chunk` nodes, embed them, and create the vector index.
2. **L5.** Link the chunks with `NEXT` and add window retrieval. Compare top-k with and without the ±1 window on three questions.
3. **L6.** Merge Form 13 managers onto the same `Company` nodes. Add the uniqueness constraint *before* the import, and count how many duplicates it prevents compared with running without it.

### B4 — Tiered extraction with a false-merge rate

*Note [10](../notes/10-building-kgs-with-llms.md). Reference: Anthropic's [KG construction cookbook](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide).*

1. Choose 10–20 documents with plenty of people and organisations (archive letters, Wikipedia summaries, your own docs). Hand-label 50 mentions with their gold canonical entity.
2. **Extract** with a Haiku-class model under a JSON schema (Pydantic or tool schema). Output *mentions* with descriptions, not entities.
3. **Resolve** two ways: (a) string similarity followed by WCC, as in ch6; (b) a Sonnet-class model clustering names together with their descriptions, as in the cookbook. Write the result as `RESOLVES_TO` edges with `evidence` and `confidence`. **Never merge destructively.**
4. Report entity precision and recall, false-merge rate and false-split rate for (a) and (b).
5. Undo one resolution by deleting its `RESOLVES_TO` edge, and confirm the graph returns to its earlier state. If that fails, your resolution isn't reversible yet.

### B5 — Chat with the 10-K graph

*Note [11](../notes/11-kg-rag-and-text-to-cypher.md). Course lesson 7 (chatting with the SEC graph).*

1. Use the course's hosted L7 notebook (its database already has the `Address` nodes), or extend your B3 graph with them ([note 10](../notes/10-building-kgs-with-llms.md#stage-5-assembly-with-the-course-as-worked-example)), and run `GraphCypherQAChain` over it ([note 11](../notes/11-kg-rag-and-text-to-cypher.md#the-failure-to-expect) has the setup).
2. Reproduce the course failure: ask for total investment by a manager and check whether the generated query sums a `value` on `Company`, which doesn't exist. Fix it with one few-shot example, then remove the example and fix it instead with a schema annotation (`/* value lives on OWNS_STOCK_IN */`). Record which fix holds up on five paraphrases of the question.

### B6 — Text-to-Cypher as generate-then-verify

*Notes [11](../notes/11-kg-rag-and-text-to-cypher.md), [02](../notes/02-graph-primitives.md). Start from the generate-then-verify graph in [note 02](../notes/02-graph-primitives.md#the-first-graph-generate-then-verify).*

1. **Generate.** An LLM node writes JSON with the fields `relationships`, `reasoning`, `query` and `success`, in that order, from an annotated schema.
2. **Validate deterministically.** Run `EXPLAIN <query>`. Check that every label and relationship type in the query exists in the schema and that variable-length paths are bounded. On failure, route back to the generator with the error in state. Stop after 3 attempts.
3. **Execute** only queries that pass validation, as a read-only user.
4. Write 20 multi-hop questions with gold answers **and gold paths**. Compare vector-only, hybrid (vector entry plus graph expansion) and text-to-Cypher. Score whether the answer is correct, whether the path is valid, and tokens used. Record the first-pass validity rate and the rate after retries.

### B7 — Swarm with and without shared memory

*Note [12](../notes/12-kg-as-shared-agent-memory.md). Start from the fan-out example in [note 03](../notes/03-state-and-reducers.md#dynamic-fan-out-the-send-api) and the `GraphUpdate` schema in [note 12](../notes/12-kg-as-shared-agent-memory.md#the-write-path-graphupdate).*

1. Fan out N = 5–10 research workers over one corpus, giving each a slice or a sub-question.
2. **Run A.** No shared state. Each worker returns prose, and the synthesiser reads everything.
3. **Run B.** Each worker publishes `GraphUpdate`s, validated against the schema with provenance required, into a shared NetworkX `MultiDiGraph` or Neo4j. The synthesiser queries a bounded subgraph and must cite edges.
4. Compare redundant findings (how many workers reported the same fact), synthesiser input tokens, total tokens, and answer quality on 10 questions graded on answer and path.

### B8 — Contamination drill

*Note [12](../notes/12-kg-as-shared-agent-memory.md).*

1. In the B7 run B graph, inject one false merge by adding `RESOLVES_TO` from two distinct people to a single canonical, under a fake `run_id`.
2. Re-run the 10 questions and list every answer that changed. Trace each change back to the bad edge.
3. Roll back **using provenance alone**: delete everything carrying that `run_id`. Re-run and confirm the answers are restored.
4. Write one paragraph on what the validator would have needed in order to reject the merge at write time.

### B9 — Predict missing links

*Note [13](../notes/13-graph-ml-and-gnns.md). Book ch9–12.*

1. **Baseline.** On `nx.karate_club_graph()`, reproduce ch9's three feature sets (degree; Node2Vec; degree plus neighbours in each faction) with the same logistic regression. Run each 10 times and report the mean and spread of F1. Then tune Node2Vec (`walk_length`, `num_walks`) until it matches the homophily features, or explain why it can't.
2. **Link prediction on your own graph.** Take the B2 repo graph, or the B7 run B graph. Hold out 10% of `REFERENCES` or `DEPENDS_ON` edges and sample the same number of non-edges. Score the candidates two ways: (a) manual pair features such as common neighbours, Adamic–Adar and DWPC over typed paths; (b) a GraphSAGE encoder with a dot-product decoder (PyG, `RandomLinkSplit` with `disjoint_train_ratio`). Report precision, recall and false-positive rate at a fixed threshold.
3. **Write back safely.** Publish the top 20 predictions as `GraphUpdate`s with `predicted: true`, the model's confidence and the training `run_id`. Confirm that your B6 queries ignore them by default and pick them up only when asked to.
4. Read the 20 by hand. How many are real missing links, how many are hub artefacts, and did DWPC or the GNN produce fewer artefacts?
