---
origin: book-condensed
sources:
  - Negro et al., Knowledge Graphs and LLMs in Action (Manning, 2025), ch. 15
confidence: medium-high
cleaned: 2026-11-01
---
# 11b — A Text-to-Cypher QA Agent as a Graph

> Text-to-Cypher is a Track B technique that only becomes reliable with Track A machinery: named nodes, typed state, a checkpointer and a retry edge with a bound.

A text-to-Cypher prompt alone leaves a user staring at one failed query or at a clean empty result. Reliability comes from what surrounds it: a router, a retry edge that returns the database's error to the generator, a validator ahead of execution, and state you can audit. This chapter wires ch. 15's agent as a LangGraph graph, and fixes the bugs in the book's listings on the way.

---

## Where it sits

[Note 11](11-kg-rag-and-text-to-cypher.md#text-to-cypher) built the expert prompt and named the failure it can't remove. This note wires that prompt into a graph using the primitives of [note 02](02-graph-primitives.md), [note 03](03-state-and-reducers.md) and [note 04](04-durable-execution-and-interrupts.md). The running mistake is L7's: summing `value` on `Company`, when `value` lives on the edge ([note 11](11-kg-rag-and-text-to-cypher.md#the-failure-to-expect)).

---

## The QA agent as a Track A graph

Ch15 implements the expert pipeline in LangGraph (*KG & LLMs in Action*, ch. 15):

![The ch15 LangGraph pipeline: START, intent detection, schema extraction, text to Cypher, query execution; from query execution a dashed Retry edge goes back to text to Cypher, a dashed Summarize edge to generate summary and then END, and a dashed END edge straight to END](../sources/images/negro-kg-and-llms-in-action-fig15-3.png)
*Image Source: Negro et al., Knowledge Graphs and LLMs in Action, Fig. 15.3 (2025)*

### Three supporting pieces

Around the graph sit three components:

- **A configuration provider.** One YAML file holds the prompt templates (Jinja2), the KG notes and the few-shot examples, each example with its question, Cypher and optional reasoning. Prompts and annotations are then tuned and versioned without touching code, and the file is reloaded on every request so edits apply immediately. The KG notes carry domain definitions the schema can't ("a previous offender or known offender is defined by the fact that the node is connected to crimes") and traversal advice ("do not expand ANPRCameraEvent unless you need to connect it to both Vehicle and ANPRCamera"). Check the examples as carefully as code, because the model copies them. Two in the printed config are wrong: the March 14 example's answer, `MATCH (c:Crime) WHERE c.date starts with "2025-03-14"`, has no `RETURN` and won't run, and the "male known offender" example filters `person.sex CONTAINS 'MALE'`, which also matches `'FEMALE'`.
- **A schema provider.** The skip-and-describe transformation [from note 11](11-kg-rag-and-text-to-cypher.md#give-the-model-an-llm-ready-schema).
- **A question-processing interface.** A generator that turns the pipeline run into an event stream for the front end ([below](#streaming-it-to-a-ui)).

### State, node by node

| Node | Reads | Writes |
|---|---|---|
| `intent_detection` | `question` | `output_type`, `output_type_reason` |
| `schema_extraction` | (the database) | `schema`; resets `retries` to 0 |
| `text_to_cypher` | everything above, plus notes, examples, UI selection and `information` | `query`, `query_reasoning`, `query_message` (the raw JSON, kept for debugging) |
| `query_execution` | `query`, `output_type` | `results_error`, `information` (failed query plus error), `retries` + 1 |
| `generate_summary` | `question`, `query`, records, selection | `summary`, `summary_reason`, `summary_analysis` |

Execution keeps records as a list for graph and map output and converts to a DataFrame for tables. It catches the driver's `ClientError` (syntax errors and schema mismatches) instead of raising, so a failure becomes state that the router can act on. Each LLM node parses its reply leniently: strip a stray `` ```json `` fence, then parse with `json5` (ch. 15).

Bugs to fix if you copy the listings:

- The intent node writes `output_reason` while the state declares `output_type_reason`, and the summary node writes `summary_analisys` (misspelt) against `summary_analysis`. `results_error` is declared `list` but holds a string or `None`. A typed state is only an audit trail if node outputs match the declared keys and types.
- `processQuestion` builds the selection as `{"labels": list(node.labels)[0], ...}`, but the ch14 templates render `{{node.label}}`. Jinja2 renders a missing key as an empty string, so the model sees selected nodes with no label and nothing fails. `list(node.labels)[0]` is also an arbitrary pick for a node with several labels.
- The records (`self.results`) and the selection (`self.selection`) live on the `Agent` instance, not in `AgentState`. The checkpointer never sees them, and two concurrent questions on one shared pipeline overwrite each other's records. Put them in state.
- Only `neo4j.exceptions.ClientError` is caught. A query that runs and returns nothing is not an error, so it is never retried; that is the gap the validator below partly fills.

### The retry edge

The retry edge goes back to `text_to_cypher`, not to schema extraction: the schema doesn't change between attempts, only the query does, now with the database's error in the prompt.

```python
def post_query_execution(state):
    if state["results_error"] is not None:
        return "retry" if state["retries"] < 3 else "END"
    return "summarize" if state["output_type"] in ("map", "graph") else "END"
```

`retries` is incremented on every execution, so `< 3` means **three executions in total**, i.e. two retries (the book: "allows up to three attempts to execute the query"). On a retry, `information` reads "We tried: {query} and we got: {error}", and the template sits it next to the restated question. When the budget runs out the route is a bare `END`, so the user gets only the error; a production version should say plainly that it couldn't answer.

Several Track A patterns appear here:

- **Generate-then-verify** ([note 02](02-graph-primitives.md)). The database is the verifier, and its error message goes back into the prompt through the `information` field.
- **A bounded back-edge** ([note 07](07-failure-modes-at-scale.md)). It stops after three attempts.
- **Typed state as the audit trail** ([note 03](03-state-and-reducers.md)). `AgentState` keeps `output_type_reason`, `query_reasoning` and `results_error`, so every intermediate decision can be inspected. The book points out that this also gives you a dataset of failures and few-shot candidates for free.
- **A checkpointer** ([note 04](04-durable-execution-and-interrupts.md)). `graph.compile(checkpointer=self.memory)`, with a fresh `thread_id` per question. Listing 15.12 never defines `self.memory`; use `MemorySaver()`. The checkpointer is what lets the streaming generator call `graph.get_state(config)` for the full state, which needs one. Because every question gets a new thread, nothing carries between questions through LangGraph; continuity across turns comes only from the UI selection.

### Validate before you execute

What the book's version lacks is a validator that runs **before** execution. The database only reports errors it hits; a query that is syntactically fine but semantically wrong (summing `value` on `Company`) runs and returns nothing or nonsense. Put a deterministic node between `text_to_cypher` and `query_execution`:

1. `EXPLAIN <query>` checks that it parses and plans without running it. Neo4j also attaches warnings for label, relationship-type and property names that don't exist anywhere in the database.
2. Check every label and relationship type against the conceptual schema, and every `var.prop` against the properties of the label bound to `var`. This is the check that catches `Company.value`: `value` exists in the database (on `OWNS_STOCK_IN`), so the database-wide warning stays silent.
3. Reject unbounded variable-length paths (`*`, `*2..`).
4. On failure, route back to the generator with the reason in `information`; execute passing queries only, as a read-only database user.

```python
import re

def validate(query: str, schema: dict, session) -> str | None:
    """schema = {"labels": {label: {props}}, "rels": {type: {props}}}. Returns an error or None."""
    try:
        summary = session.run("EXPLAIN " + query).consume()
    except Exception as e:                          # CypherSyntaxError and friends
        return f"does not parse: {e}"
    if summary.notifications:
        return "; ".join(n["description"] for n in summary.notifications)
    bound = dict(re.findall(r"\(\s*(\w+)\s*:\s*`?(\w+)", query))       # var -> label
    for label in set(re.findall(r"\(\s*\w*\s*:\s*`?(\w+)", query)) - schema["labels"].keys():
        return f"unknown label {label}"
    for rel in set(re.findall(r"\[\s*\w*\s*:\s*`?(\w+)", query)) - schema["rels"].keys():
        return f"unknown relationship type {rel}"
    for var, prop in re.findall(r"\b(\w+)\.(\w+)", query):
        if var in bound and prop not in schema["labels"][bound[var]]:
            return f"{bound[var]} has no property {prop}"
    if re.search(r"\*\s*(\d+\s*\.\.\s*|\.\.\s*)?\]", query):    # *, *.., *2.. (not *3 or *1..3)
        return "unbounded variable-length path"
    return None
```

Regexes are a sketch. A Cypher parser does this properly, but even this catches the L7 mistake. To measure the loop, record the first-pass validity rate and the rate after retries.

### Summarise as a complement

Ch15 summarises only graph and map output (tables speak for themselves), and adds analysis only when the question asks for it. The summary node is the only one that sees the actual data, so its prompt rebuilds the whole chain: question, executed query, records, selection. Three instructions do the work (*KG & LLMs in Action*, ch. 14):

- **Complement the view.** The user also sees the graph, so point out what isn't visible there (a detail inside a `description` property, a repeated sighting), rather than repeat it.
- **Filter.** Graph-shaped results return whole paths for drawing; most of that data is irrelevant to the question.
- **Gate analysis.** The output JSON starts with `results_analysis: true|false` ("did the question ask for analysis?"), then `reasoning`, then `summary`. The explicit flag is easy to monitor and shapes the reasoning that follows.

### Streaming it to a UI

`graph.invoke` makes the user wait for the whole run. Ch15 wraps `graph.stream(..., stream_mode="updates")` in a generator that yields `(event_type, payload, state)` triples as each node finishes (ch. 15):

| Event type | Carries | Example |
|---|---|---|
| update | progress text | "generating query..." |
| result | text output | the query reasoning, an error, the summary |
| graph / map / table / chart | structured results | records for the canvas, a DataFrame |
| END | final state | used to persist the turn |

Passing the full state with every event leaves presentation entirely to the front end. The book's front end is Streamlit (chat, a graph canvas, a node-selection column, a history showing reasoning and the query in expanders). It presents Streamlit as a prototyping tool, not a production UI.

### A worked investigation

Ch15's demo chains five questions, each building on the previous selection (ch. 15):

| Step | Question (paraphrased) | What the system did |
|---|---|---|
| 1 | One crime currently under investigation | `MATCH (c:Crime) WHERE c.status = 'investigation' RETURN c LIMIT 1`; the summary pointed out a detail buried in the description: a black car with a plate starting "EB" |
| 2 | ANPR cameras within 1 km of the selected crime | Resolved "selected" from the UI; `point.distance` filter; map and graph shown together |
| 3 | Vehicles that camera saw that day, black, plate starting EB | Combined the selection with explicit constraints; several vehicles |
| 4 | Same, but "compatible with the description … any more likely?" | Took the constraints from the crime node itself; the analysis noticed one plate seen twice around the incident time |
| 5 | "Some may be owned by previous offenders" | Expanded through `OWNS` and `COMMITTED`; the repeat vehicle's owner had a prior conviction for the same offence |

The lesson is the selection mechanism. Refinement works because each turn can point at nodes from the last one instead of restating them.

### Where ch. 15 goes from here

From ch15's closing section:

- **Learn from use.** Cluster complaint-like questions into a pain-point list; keep the reasoning chain of successful queries as new few-shot examples; find question clusters that deserve a narrower schema slice.
- **Enrich the schema the way an expert does.** An agent that runs exploratory queries (value distributions, typical paths) and adds what it finds to the annotations. For large graphs, layered schemas: domain-level views for orientation, the full detail for query generation.
- **Fine-tune.** In-context schemas and examples stop scaling with big graphs. The book cites work finding that in-context learning trails task-specific fine-tuning even with the same examples. Fine-tuned components can replace individual nodes without giving up the observable pipeline.

---

## Working reference

Depth: Negro et al., *Knowledge Graphs and LLMs in Action* (Manning, 2025), ch. 15.

---

## Pitfalls

- **Reading `retries < 3` as three retries.** Symptom: logs show one fewer retry than planned. Fix: `retries` goes up on every execution, so `< 3` means three executions and two retries.
- **Treating empty as success.** Symptom: wrong filters return nothing and never reach the retry edge, because only `ClientError` is caught. Fix: validate before execution, and decide what an empty result should trigger.
- **Executing before validating.** Symptom: semantically wrong queries run, such as one using `Company.value`. Fix: `EXPLAIN`, a schema check on labels and `var.prop`, and rejection of unbounded paths, as a read-only user.
- **Retrying from the top.** Symptom: schema extraction reruns on every attempt. Fix: route back to `text_to_cypher` only, since just the query changes.
- **Keeping results on the agent instance.** Symptom: concurrent users collide, and the checkpointer never sees records held in `self.results`. Fix: move what must survive into `AgentState`.
- **Copying listing 15.12 as it stands.** Symptom: `self.memory` is used and never defined. Fix: define a checkpointer and pass a fresh `thread_id` per question.

## Try it

1. In the validator, what does `MATCH (c:Company) WHERE c.value > 1000 RETURN c` do on the L7 schema, and what goes into `information`?

   <details><summary>Answer</summary>

   Step 2 rejects it, because `value` isn't a property of `Company`; it sits on the `OWNS_STOCK_IN` edge. The reason goes into `information`, and the query goes back to the generator without running. Syntax alone wouldn't catch it, since it would parse and return nothing.

   </details>

2. Add a counter for first-pass validity and the rate after retries, over 20 questions on any graph you have. What would you change first if first-pass validity is 60% and post-retry validity is 95%?

   <details><summary>What to look for</summary>

   The retries are doing real work, at a cost per question. Read the validator's reasons and fix the commonest class in the schema annotations or few-shot examples, since each retry is another model call. If post-retry validity were also low, the prompt is missing information a retry can't supply.

   </details>

3. Draw this graph's five nodes and mark which are generate-then-verify, which edge is bounded, and where a validator node would go.

   <details><summary>Answer</summary>

   `intent_detection` → `schema_extraction` → `text_to_cypher` → `query_execution` → `generate_summary`. `text_to_cypher` generates and the database verifies. The bounded back-edge runs from `query_execution` to `text_to_cypher`. The validator goes between those two, with its failure edge returning to `text_to_cypher`.

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| Why does the retry edge go to `text_to_cypher` and not to schema extraction? | The schema doesn't change between attempts, only the query, which now has the database's error in the prompt's `information` slot. |
| What can't the retry loop catch? | A query that runs and returns nothing, because only `ClientError` is caught. Semantic errors need a validator before execution. |
| What are the steps of a validator? | `EXPLAIN` to parse and plan, check labels, relationship types and `var.prop` against the schema, reject unbounded paths, then route failures back; execute only as a read-only user. |
| Why do you summarise when the user can see the result? | The summary complements the view, pointing out what isn't visible, such as a detail in a `description`. `results_analysis` makes the choice to analyse easy to monitor. |
| Why does the five-step investigation work without restating anything? | Each turn can point at the nodes selected in the last one, so "the selected crime" resolves from the UI selection. |
| What would you measure in production? | First-pass validity and validity after retries, which tell you whether the prompt or the retry edge does the work. |

## Next

[12-kg-as-shared-agent-memory.md](12-kg-as-shared-agent-memory.md): what changes when many agents write to the graph, not just read it.
