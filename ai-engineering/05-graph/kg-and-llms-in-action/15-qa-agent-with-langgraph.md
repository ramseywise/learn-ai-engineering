---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 15: Building a QA agent with LangGraph"
confidence: high
cleaned: 2026-07-29
---

# Ch 15 — Building a QA Agent with LangGraph

This chapter builds a practical, end-to-end application for querying knowledge graphs
(KGs) with LLMs, combining chapter 14's expert-emulating architecture into one integrated
system. **LangGraph** orchestrates the core pipeline; **Streamlit** provides the frontend
for user input (questions, node selection) and output (visualization, summaries).

The overall system architecture (figure 15.1) is a loop: Input (user request + user
selection) → **Intent detection** → **Query generation** → **Query execution** → Output
(visualization) → **Generate summary**, with schema extraction feeding query generation
and an execution-error path looping back for retry.

## 15.1 Building the LangGraph Pipeline

**LangGraph** is "an innovative library designed for building stateful, multi-actor
applications powered by LLMs," suited for orchestrating workflows with complex reasoning
and decision-making.

### Core LangGraph concepts

A basic two-node RAG example (figure 15.2 — "retrieve relevant documents" then "generate
answer") introduces the key idea: **state-based communication**. Rather than passing data
directly between components, each node reads from and writes to a shared **state**
object — "similar to a whiteboard where each agent can read previous work and add their
results." The retrieval node reads the question and adds documents to the state; the
generation node reads both and adds the answer.

- LangGraph implements workflows as **directed graphs**. Each **node** is a distinct
  **agent function** reading from and writing to the global state.
- **Edges** determine execution flow — which node runs next.
- LangGraph supports **dynamic edge resolution**: branching based on arbitrarily complex
  logic (the next node can depend on a preceding node's output), enabling everything from
  simple routers to fully autonomous LLM-driven flow control.

### 15.1.1 System architecture overview

The KG querying pipeline (figure 15.3) maps each expert-emulating step to a LangGraph
node:

```
START → Intent detection → Schema extraction → Text to Cypher → Query execution
                                                                        │
                              ┌── (retry) ──────────────────────────────┘
                              │
        Generate summary ←── (summarize) ── [conditional edge on query execution outcome]
              │                                        │
              └──────────────→ END ←────────────── (END, direct)
```

Solid arrows are the main flow (intent detection → schema extraction → query execution);
dashed arrows are conditional paths based on query execution outcomes (retry, summarize,
or end directly).

The broader backend architecture (figure 15.4) places LangGraph at the center, integrated
with:

- **Configuration provider** — manages `config.yaml` and prompt templates.
- **Schema provider** — connects to the graph database, extracts schema, and transforms
  it into an LLM-friendly format.
- **Question processing interface** — bridges the core pipeline and frontend
  applications, exposing the LangGraph workflow as an **event stream** so frontends can
  track pipeline progress in real time.

### 15.1.2 Configuring pipeline components

The **configuration provider** is a centralized repository for prompt templates and KG
annotations, keeping lengthy text out of the implementation. Templates use the **Jinja2**
templating language for dynamic content generation at runtime. This simplifies tuning KG
descriptions/prompts in one place and eases versioning of prompt/annotation changes.

**Listing 15.1 — Configuration file example (YAML)**

```yaml
notes: >
    - all POINTS properties are Neo4j Points (`point.distance()`)
      and similar functions work for them)
    - do not expand ANPRCameraEvent unless you need
      to connect it to both Vehicle and ANPRCamera
    - a previous offender or known offender is defined by the fact that
      the node is connected to crimes
examples:
    - question: Crimes that occurred on March 14th, 2025
      answer: MATCH (c:Crime) WHERE c.date starts with "2025-03-14"
      reasoning: >-
          To find the crimes that occurred on that date, we leverage
          the <b>date</b> property of the crime node.
          Since it is formatted as an ISO string, we can use the
          prefix "2025-03-14" to get all crimes that occurred on that date
          Since there is no traversal, no paths are returned
    [...]
    - question: Return one male known offender aged 20 to 22
      answer: >-
          MATCH path = (person:Person)
                        -[committed:COMMITTED]->(crime:Crime)
          WHERE (person.sex CONTAINS 'MALE' AND
                 person.age >= 20 AND person.age <= 22)
          RETURN path LIMIT 1
prompts:
    text_to_cypher:
        system: >-
            Your task is to generate a Cypher query for a Neo4j graph
            database, based on the schema definition provided,
            that answers the user question.
        template: templates/text_to_cypher.template
    intent_detection:
        template: templates/intent_detection.template
    generate_summary:
        template: templates/summary.template
```

The configuration combines three elements: **notes** (operational/domain knowledge and
best practices for the graph database), **examples** (question–answer pairs with detailed
reasoning demonstrating expected query patterns), and **prompts** (references to external
templates for intent detection, query generation, and summary generation) — giving the
LLM rich context for accurate query generation while keeping template content separately
versionable.

**Listing 15.2 — Configuration component**

```python
class ChainConfiguration:
    def __init__(self):
        self.base = Path(__file__).parent
        self.config = self.load()

    def load(self):
        config_file = self.base / "chain_config.yaml"
        return yaml.load(config_file.open(), Loader=yaml.FullLoader)

    def get_prompt(self, name, **kwargs):
        system = self.config["prompts"][name].get("system")
        template_file = (
            self.base / self.config["prompts"][name]["template"])

        template = template_file.read_text()
        prompt = jinja2_formatter(template, **kwargs)

        return system, prompt

    def getAnnotations(self, reload=True):
        if reload:
            self.config = self.load()
        return {
            "notes": self.config["notes"],
            "examples": self.config["examples"]}
```

`ChainConfiguration` exposes two main methods: `get_prompt` (retrieves and renders prompt
templates via Jinja2) and `getAnnotations` (accesses notes/examples).

### 15.1.3 Schema translation service

The **schema provider** (`Neo4jSchema`) solves the fundamental challenge from chapter 14:
the system needs the **conceptual schema**, but can only programmatically access the
**technical schema**. The solution is a **configuration-based transformation approach**
with two YAML-stored parts:

- A **skip list** identifying technical nodes/relationships/properties to exclude from
  the conceptual model (internal IDs, timestamps, implementation-specific properties).
- A **description section** enriching the filtered schema with business-level
  descriptions for nodes, relationships, and properties, plus domain terminology.

The schema provider follows a **three-step process**: extract the technical schema via
Neo4j's `apoc.meta.schema`, filter out technical elements via the skip list, and enrich
remaining elements with business descriptions.

**Listing 15.3 — Schema provider: data model**

```python
@dataclass
class Property:  #1
    """Represents a node or relationship property with an optional
       description"""
    name: str
    type: str
    description: str = None

    def __str__(self):
        """Represents the property as string in the format:
           property_name:TYPE /* optional description */ """
        ret = f"{self.name}: {self.type}"
        if self.description is not None:
            ret += f" /* {self.description} */"
        return ret


@dataclass
class Node:  #2
    """Represents a node type."""
    items = {}  #3
    name: str
    properties: list[Property]
    description: str = None

    @classmethod
    def mk_node(cls, name, value):  #4
        """Creates a new node with the given name and properties
           from a dictionary.

           Args:
               name (str): The name of the node.
               value (dict): the node description as
                             returned by `apoc.meta.schema`
        """
        properties = [Property(name=k, type=v["type"])
                      for k, v in value["properties"].items()]
        properties = sorted(properties, key=lambda x: x.name)

        node = Node(name=name,
                     properties=properties)

        for rel_name, rel_value in value["relationships"].items():
            Relationship.mk_rels(source=name, name=rel_name,
                                  value=rel_value)

        cls.items[node.name] = node  #5

    def drop_properties(self, skipProperties):
        """Drops specified properties from the node.

           Args:
               skipProperties (list): A list of property names
                                       to be dropped.
        """
        self.properties = [prop for prop in self.properties
                            if prop.name not in skipProperties]  #6

    def __str__(self):  #7
        """Represents the node as string in the format:
           (:NodeType /* node class description */ {
               property_one:TYPE /* property one description */,
               property_two:TYPE /* property two description */,
               ...
           })
        """
        descr = ("" if self.description is None
                  else f"/* {self.description} */ ")

        return (
            f"(:{self.name} {descr}{{\n    " +
            ",\n    ".join(str(prop) for prop in self.properties) +
            "\n})\n"
        )
```

Annotations:
1. Dataclass representing a node or relationship property
2. Dataclass representing a node type
3. Keeps track of all nodes at a global level
4. Instantiates nodes using the node description from `apoc.meta.schema`
5. Stores the newly created node instance in the `Node.items` dictionary
6. Recomputes node properties by filtering out properties in the skip list
7. Assembles node components to form the desired node description format

`Property` handles individual attributes; `Node` manages overall structure and filtering.
A parallel `Relationship` class (referenced but not fully shown) handles relationship
types, sources, destinations, and their own skip/description logic.

**Listing 15.4 — Schema provider main class**

```python
class Neo4jSchema:
    [...]

    def get_schema(self):  #1
        with self.driver.session() as session:
            result = list(session.run(
                "CALL apoc.meta.schema({sample:-1})"  #2
            ))[0]["value"]

        [Node.mk_node(k, v) for k, v in result.items()
         if v["type"] == "node"]  #3

    @staticmethod
    def apply_configuration(config: dict = None):  #4
        if config is None:  #5
            config_file = Path(__file__).parent / "schema_config.yaml"
            config = yaml.load(config_file.open(),
                                Loader=yaml.FullLoader)["schema"]

        items = {node.name: node for node in Node.items.values()
                 if node.name not in config["skip"]["classes"]}
        Node.items = items  #6

        for node in Node.items.values():
            node.drop_properties(config["skip"]["properties"])  #7

        for node in Node.items.values():
            node.description = (config["descriptions"]["classes"]
                                 .get(node.name))  #8
            for prop in node.properties:
                property_description = (config["descriptions"]["properties"]
                                         .get(node.name, {})
                                         .get(prop.name))  #9
                prop.description = property_description

        skip = config["skip"]
        relationships = {rel_name: rel
                          for rel_name, rel in Relationship.items.items()
                          if rel.source not in skip["classes"]  #10
                          if rel.dest not in skip["classes"]  #11
                          if rel.name not in skip["relationships"]  #12
                          }
        for rel in Relationship.items.values():
            rel.drop_properties(config["skip"]["properties"])  #13

        Relationship.items = relationships

    def __str__(self):  #14
        ret = ["### Graph Schema Overview\n",
               "#### Node Types"]
        ret += [str(node) for node in Node.items.values()]
        ret.append("#### Relationships\n")
        ret += [str(rel) for rel in Relationship.items.values()]
        return "\n".join(ret)
```

Annotations:
1-3. `get_schema` calls `apoc.meta.schema` on the full DB without sampling, then parses
     results via list comprehension into `Node` instances.
4-5. `apply_configuration` converts technical → conceptual schema, defaulting to
     `schema_config.yaml` from the package directory if no config is passed.
6-9. Recomputes node types (dropping skip-list classes/properties) and applies
     descriptions from `descriptions.classes.<name>` and
     `descriptions.properties.<class>.<property>` where present.
10-13. Filters relationships whose source, destination, or name is in the skip list, and
       drops their skip-listed properties, mirroring the node-side logic.
14. `__str__` renders a Markdown representation with node types and relationships.

`get_schema` retrieves the technical schema; `apply_configuration` handles the
transformation, giving LLMs a clean, conceptual view of the data model while preserving
everything needed for query generation, proper entity/relationship naming, and applying
business rules/constraints during query construction.

### 15.1.4 State management design

The cornerstone of agent communication in LangGraph is the `state` object — a shared
memory space agents read from and write to, creating a clear chain of responsibility.

**Listing 15.5 — Pipeline agent's state**

```python
class AgentState(TypedDict):
    question: str
    output_type: str
    output_type_reason: str
    schema: str
    query: str
    query_reasoning: str
    query_message: str
    results_error: list
    summary: str
    summary_reason: str
    summary_analysis: bool
    information: str
    retries: int
```

| Section | Fields | Purpose |
|---|---|---|
| Question input | `question` | Original user request |
| Intent detection | `output_type`, `output_type_reason` | Detected visualization intent + reasoning |
| Schema info | `schema` | Graph schema in LLM-friendly format |
| Query generation | `query`, `query_reasoning`, `query_message` | Generated Cypher query + metadata |
| Error handling | `results_error` | Errors from query execution |
| Summary generation | `summary`, `summary_reason`, `summary_analysis` | Generated summary + analysis flag |
| Retry mechanism | `information`, `retries` | Drives retry logic for failed queries |

The state carries data between agents *and* maintains context for routing decisions and
graceful error handling.

### 15.1.5 Pipeline agent implementation

Figure 15.7 shows the same pipeline topology as figure 15.3. Each step below is a
specialized agent function operating on `AgentState`.

#### Intent detection agent

Entry point of the pipeline. Operates solely on the user's question, using the
intent-detection prompt from chapter 14. Updates `output_type` (determined visualization
format: table, graph, or map) and `output_reason` (reasoning for that choice).

**Listing 15.6 — Intent detection agent implementation**

```python
def run_prompt(self, prompt, system=""):  #1
    messages = [HumanMessage(content=prompt)]
    if self.system or system:
        system = self.system if not system else system
        messages = [SystemMessage(content=system)] + messages  #2

    message = self.model.invoke(messages)

    logger.debug(f" got {message.content}")
    payload = message.content
    payload = re.sub(r'^\s*```json\s*|\s*```\s*$', '',
                      payload, flags=re.DOTALL)  #3
    return json5.loads(payload)  #4

def intent_detection(self, state: AgentState):
    system, prompt = self.config.get_prompt(  #5
        "intent_detection", question=state["question"])
    results = self.run_prompt(prompt, system)
    return {  #6
        "output_type": results["type"],
        "output_reason": results["reason"]}
```

Annotations:
1. Handles prompt execution and response processing
2. Prepends a system message to the prompt if provided
3. Removes JSON code block markers from the response if present
4. Parses the response as JSON using the more lenient JSON5 format
5. Retrieves and renders the intent detection prompt template from configuration
6. Maps the response fields to their corresponding state properties

#### Schema extraction agent

Bridges the KG and LLM using the `Neo4jSchema` object (section 15.1.3), converting the KG
schema into an LLM-friendly format for downstream agents.

**Listing 15.7 — Schema extraction agent**

```python
def schema_extraction(self, state: AgentState):
    assert self.neo4j_schema is not None, \
        "you need to provide a neo4j schema"

    self.neo4j_schema.get_schema()  #1
    self.neo4j_schema.apply_configuration()  #2
    return {"schema": str(self.neo4j_schema),
            "retries": 0}  #3
```

Annotations:
1. Retrieves the full technical schema
2. Filters unnecessary schema components and adds descriptions as per the configuration
3. Updates the state properties with the LLM-friendly version of the schema and resets
   the retries counter

The heavy lifting is done by `Neo4jSchema`: retrieve schema, apply configuration, convert
to string, and reset the retry counter to zero.

#### Text-to-Cypher agent

Transforms the user's natural-language question into a Cypher query, considering both
the graph's schema and any currently selected elements in the visualization. This
**contextual awareness** lets users reference selected nodes/relationships without
explicitly describing them (section 14.7.2), making queries more natural and concise. The
agent adds annotations (notes/examples from the configuration provider) and the current
selection to the state before executing the prompt.

**Listing 15.8 — Text-to-Cypher agent**

```python
def text_to_cypher(self, state: AgentState):
    extra = {
        "annotations": self.config.getAnnotations(),
        "selection": self.selection
    }
    params = dict(state) | extra
    system, prompt = self.config.get_prompt("text_to_cypher", **params)
    logger.debug(f"prompt: {prompt}")

    results = self.run_prompt(prompt, system)

    return {"query": results["query"],
            "query_reasoning": results["reasoning"],
            "query_message": json.dumps(results)}
```

Results (generated Cypher query, reasoning, and the full LLM response for debugging) are
stored in `query`, `query_reasoning`, and `query_message` respectively.

#### Query execution agent

Provides robust error handling and dynamic result formatting based on visualization
needs.

**Listing 15.9 — Query execution agent**

```python
def query_execution(self, state: AgentState):
    try:
        results = self.neo4j_schema.run(state["query"])
        if state["output_type"] in {"graph", "map"}:
            self.results = list(results)
        else:
            self.results = results.to_df()
        results_error = None
        information = ""
    except neo4j.exceptions.ClientError as e:
        self.results = None
        results_error = str(e)
        logger.info(f"got error: {e}")
        information = f"""We tried:
                        {state['query']}
                        and we got:
                        ```
                        {str(e)}
                        ```"""

    retries = state.get("retries", 0) + 1
    return {"results_error": results_error,
            "retries": retries,
            "information": information}
```

Logic: attempt to execute the query, process results based on detected intent. For
graph/map visualizations, results are kept as a list of records (native format); for
tabular output, results are converted to a pandas `DataFrame` via Neo4j's built-in
conversion.

**Error handling**: if execution fails (typically syntax errors or schema mismatches),
the agent captures error details, logs the failure, and constructs an error message
including both the attempted query and the error description. State is updated with
`results_error` (error message or `None`), `retries` (attempt count), and `information`
(detailed error context for a potential retry) — feeding the post-execution routing
logic.

#### Post-query execution (dynamic conditional edge)

Unlike the other components, **post-query execution is not an agent** — it implements
routing logic as a **dynamic edge** in the LangGraph pipeline (figure 15.8).

**Listing 15.10 — Post-query execution dynamic edge**

```python
def post_query_execution(self, state: AgentState):

    if state["results_error"] is not None:  #1
        if state["retries"] < 3:
            logger.info(f"{state['retries']} runs, we retry")
            return "retry"
        else:
            logger.info(f"{state['retries']} runs are enough")
            return "END"

    if state["output_type"] in ("map", "graph"):  #2
        logger.info("summarizing..")
        return "summarize"
    else:
        logger.info("no summarization is needed")
        return "END"
```

Annotations:
1. Handles query execution failures with retry logic up to three attempts
2. Routes to summarization for map/graph outputs; otherwise, completes

Two decision paths:

1. **Failure handling** — checks `results_error`. If an error occurred, allows up to
   **three retry attempts**, giving resilience against temporary failures or cases where
   the LLM needs multiple tries to generate a correct query.
2. **Success routing** — depends on `output_type`. Map/graph visualizations route to
   summarization (they "benefit from additional context and explanation"); tabular
   results (self-explanatory) route directly to `END`.

This dynamic routing is called out as "a key feature of LangGraph," enabling complex flow
control based on both execution results and user intent.

#### Generate-summary agent

The final agent, generating summaries for graph and map visualizations. Combines query
results and schema selection into the summary prompt context.

**Listing 15.11 — Generate-summary agent**

```python
def generate_summary(self, state: AgentState):
    extra = {
        "records": self.results,
        "selection": self.selection
    }
    params = dict(state) | extra
    system, prompt = self.config.get_prompt(
        "generate_summary", **params)
    logger.debug(prompt)

    results = self.run_prompt(prompt, system)
    return {"summary": results["summary"],
            "summary_reason": results["reasoning"],
            "summary_analisys": results["results_analysis"]}
```

Output enriches state with the summary text, the reasoning behind it, and a flag
indicating whether additional analysis was performed — completing the pipeline.

### Pipeline assembly

**Listing 15.12 — Building the LangGraph pipeline graph**

```python
class Agent:
    def __init__(self, model):
        self.neo4j_schema: Neo4jSchema = None
        self.selection = []
        self.results = None
        self.config = ChainConfiguration()
        graph = StateGraph(AgentState)
        graph.add_node("intent_detection", self.intent_detection)
        graph.add_edge("intent_detection", "schema_extraction")
        graph.add_node("schema_extraction", self.schema_extraction)
        graph.add_edge("schema_extraction", "text_to_cypher")
        graph.add_node("text_to_cypher", self.text_to_cypher)
        graph.add_edge("text_to_cypher", "query_execution")
        graph.add_node("query_execution", self.query_execution)
        graph.add_conditional_edges("query_execution",
                                     self.post_query_execution,
                                     {"retry": "text_to_cypher",
                                      "summarize": "generate_summary",
                                      "END": END})
        graph.add_node("generate_summary", self.generate_summary)
        graph.add_edge("generate_summary", END)
        graph.set_entry_point("intent_detection")
        self.graph = graph.compile(checkpointer=self.memory)
        self.model = model
```

`StateGraph` (from LangGraph) is initialized with the `AgentState` type for type safety.
Each agent is added as a node, with edges defining the standard flow between them;
`add_conditional_edges` wires the dynamic routing logic (`post_query_execution`) to its
three destinations (`retry`, `summarize`, `END`). The graph is compiled with a
`checkpointer` (`self.memory`), and `set_entry_point` designates `intent_detection` as
the starting node. This implements the expert-emulating approach in a single unified
pipeline, handling errors and different visualization requirements together.

### 15.1.6 Pipeline integration layer

A naive integration would use LangGraph's **invoke** mode: provide an initial state,
receive the final result once the pipeline completes — poor UX, since users wait without
feedback.

Instead, LangGraph's **stream execution mode** provides visibility into intermediate
steps. The chapter builds an **interface layer** (figure 15.9) — a **generator function**
that processes questions and **yields** a sequence of events, keeping a simple linear
code flow while producing intermediate results with strong event typing.

**Listing 15.13 — Question-processing interface function**

```python
def processQuestion(question, selection=None):
    config = {"configurable": {"thread_id": uuid.uuid4().hex}}  #1
    if selection is not None:  #2
        pipeline.selection = [{"labels": list(node.labels)[0],
                                "properties": dict(node)}
                               for node in selection]
    else:
        pipeline.selection = []
    input = {"question": question}
    results = pipeline.graph.stream(input,
                                     config=config,
                                     stream_mode="updates")  #3

    yield "update", "*detecting intent...*", input  #4
    for result in results:  #5
        node, value = list(result.items())[0]  #6
        logger.info(f"got results: {node}, keys: {list(value.keys())}")
        current_state = pipeline.graph.get_state(config).values  #7
        match node:
            case "intent_detection":
                yield "update", "*extracting schema...*", current_state
            case "schema_extraction":  #8
                yield "update", "*generating query...*", current_state
            case "text_to_cypher":  #9
                yield "update", "*executing the query...*", current_state
                yield "result", ("Reasoning", value["query_reasoning"]), \
                    current_state
            case "query_execution":
                if value["results_error"]:  #10
                    yield "result", ("ERROR", value["results_error"]), \
                        current_state
                else:  #11
                    output_type = current_state["output_type"]
                    yield output_type, pipeline.results, current_state
                    if output_type in {"graph", "map"}:
                        yield "update", "*summary generation...*", \
                            current_state

            case "generate_summary":  #12
                yield "result", ("Summary", value["summary"]), \
                    current_state
    logger.info("no more results  sendin END")
    current_state = pipeline.graph.get_state(config).values  #13
    yield "END", current_state, current_state  #14
```

Annotations:
1-2. Configures execution with a unique thread ID; builds the internal selection list of
     dictionaries when a non-empty selection is provided.
3-4. Invokes the pipeline in stream mode (each update = only the changed state portion);
     first yields an update telling the user intent detection is running.
5-7. Loops over pipeline events until completion, extracting the agent name + state
     updates (LangGraph result format) and the current full state each iteration.
8-9. On intent detection/schema extraction, notifies the user of the next step; on
     text-to-Cypher, surfaces the reasoning as an intermediate result.
10-11. On query execution: surfaces the error message if one occurred, otherwise emits a
       graph/table/map event with the results as payload.
12. Surfaces the summary as an intermediate result on `generate_summary`.
13-14. On completion, fetches the final state and emits an `END` event containing it.

Each event yielded is a **triplet**: response type, response payload, and the current
pipeline state. Response types fall into three categories:

| Event category | Purpose | Examples |
|---|---|---|
| **Update events** | Inform users about pipeline progress | "detecting intent", "generating query" |
| **Result events** | Deliver textual outputs | reasoning steps, errors, summaries |
| **Visualization events** | Represent structured outputs | graphs, maps, charts, tables |

Including the current pipeline state with each event gives frontends complete context
without assuming how they'll use it — the interface layer transforms execution into an
event stream, leaving presentation decisions to the frontend.

## 15.2 Streamlit Application

The interface must support: interactive graph visualization (explore/select nodes),
real-time feedback as the pipeline progresses, a chat-like interface, and complex state
for selected graph elements and processing context.

**Streamlit** fits well: native chat interface support, built-in data visualization
extensible via custom components, and a Python-first approach with no separate API or
cross-language serialization (frontend and backend share the same Python process).
Streamlit's **session state** plus automatic UI updating reflects pipeline progress in
real time. This makes Streamlit well suited for **prototyping and testing** — though a
production deployment "may warrant a more specialized interface."

### 15.2.1 Application overview

The interface layout (figure 15.10) has four regions:

- **Selection column** — displays selected nodes in the current query context, making
  questions more natural/context-aware (e.g., "What are the companies related to these
  assets?" instead of naming each asset).
- **Graph Canvas area** — visualizes KG nodes/relationships as results accumulate.
- **Question input area** — natural-language question entry at the bottom.
- **History area** — displays previous questions/answers (table or map format) with
  reasoning and summaries, updating in real time as the pipeline processes each question —
  building user trust by making the pipeline's reasoning process visible.

### 15.2.2 LangGraph integration

The integration follows an **event-driven pattern**: on Send click, the question travels
through the question-processing interface to the LangGraph pipeline, providing immediate
feedback as each agent processes it. Two complementary mechanisms manage state:

- **Temporary placeholders** — show real-time updates as the pipeline runs (transient).
- **`MessageHistory`** — accumulates the permanent conversation state, collecting the
  complete state for each message until an `END` event arrives, then re-rendering with
  the final, persistent version.

**Listing 15.14 — Message history implementation**

```python
class MessageHistory:
    def __init__(self):
        self.messages = [{}]  #1

    def update(self, message, finalize=False):
        self.messages[-1].update(message)  #2
        if finalize:  #3
            self.messages.append({})

    @staticmethod
    def display_message(msg):  #4
        with st.chat_message("user"):
            st.markdown(msg["question"])
        with st.chat_message("assistant"):  #5
            if "query_reasoning" in msg:
                st.markdown(f"##### Reasoning\n\n**output type**:\
                              `{msg['output_type']}`\n\n\
                              {msg['query_reasoning']}")
            if "table" in msg:
                st.table(msg["table"])
            if "map" in msg:
                map_ = folium.Map()
                nodes_to_map(msg["map"], map_)  #6
                st_folium(map_)
            if "query" in msg:  #7
                with st.expander("Query...", expanded=False):
                    st.markdown(f"```cypher\n\n{msg['query']}\n```")
                    st.json(msg["query_message"])
            if "summary" in msg:
                st.markdown(f"##### Summary\n\n{msg['summary']}")
                with st.expander("extra...", expanded=False):
                    st.json({  #8
                        "summary_reason": msg["summary_reason"],
                        "summary_analisys": msg["summary_analisys"]
                    })
                    st.json(msg, expanded=False)  #9

    def display_messages(self):  #10
        for message in self.messages:
            if not message:
                continue
            self.display_message(message)
```

Annotations:
1-3. Messages are a list of dicts; the last always represents the current message,
     updated in place until `finalize=True` appends a new empty dict for the next one.
4-5. `display_message` renders a single message, adapting to which keys are present.
6. Converts "map"-key graph data into a format compatible with the map library.
7. Shows the generated Cypher query in a collapsible section with process details.
8-9. Adds summary-generation details and the full message state in collapsible sections
     for debugging.
10. `display_messages` renders all messages sequentially.

`MessageHistory` maintains a list of message dictionaries. `update` allows progressive
building of messages, reflecting step-by-step pipeline processing. `display_message`
renders content using Streamlit components: Markdown for text, tables for structured
data, and Python's **folium** library for maps, with queries/summary reasoning in
expandable sections.

**Listing 15.15 — User input handler**

```python
[...]
if question := st.chat_input("What is up?"):
    with chat:
        with st.chat_message("user"):  #1
            st.markdown(question)
        with st.chat_message("assistant"):  #2
            placeholder = st.empty()

        selection = [state.canvas["byId"][int(item)]
                     for item in state.selection]  #3

        for response_type, response, current_state in \
                chain.processQuestion(question=str(question),
                                       selection=selection):  #4
            state.messages.update(current_state)  #5
            match response_type:  #6

                case "update":  #7
                    placeholder.markdown(response)

                case "graph" | "map":
                    placeholder.markdown("*updating canvas...*")
                    store_to_canvas(response)  #8
                    if response_type == "map":
                        state.messages.update(
                            {"map": state.canvas["nodes"]})  #9

                case "table" | "chart":
                    state.messages.update({"table": response})  #10
                    placeholder.table(response)  #11
                    with st.chat_message("assistant"):  #12
                        placeholder = st.empty()

                case "result":  #13
                    title, content = response
                    response = f"##### {title}\n\n{content}"
                    placeholder.write(response)
                    with st.chat_message("assistant"):  #14
                        placeholder = st.empty()

                case "END":
                    state.messages.update(current_state, finalize=True)  #15
                    st.rerun()  #16
```

Annotations:
1-3. Displays the question under the "user" role; creates an "assistant" placeholder for
     real-time updates; extracts selected nodes from canvas state via their IDs.
4-6. Sends question + selection into `processQuestion`; updates `MessageHistory` with
     current state each iteration; routes handling by response type via `match`.
7-9. "update" events render Markdown in the placeholder; "graph"/"map" events update the
     canvas, storing node data for map-type responses.
10-12. "table"/"chart" events store tabular data in `MessageHistory`, render it as a
       Streamlit table, then open a fresh placeholder to preserve that display.
13-14. "result" events format title + content and write them, then open a fresh
       placeholder to preserve the display.
15-16. "END" finalizes the message in `MessageHistory` and triggers `st.rerun()`.

The `match` statement handles response types: text updates, graph/map canvas
visualizations, tabular data (Streamlit table component), formatted results with
title/content, and an `END` event that triggers a rerun so all UI elements refresh.

## 15.3 Expert-Emulating Investigation (Worked Example)

A realistic investigation workflow demonstrates the system end-to-end. The KG subset
(figure 15.11) connects:

```
Vehicle --OWNS--> Person --COMMITTED--> Crime
   ▲                                (location, description, date-time)
   │ PLATE_READ
   │
ANPRCamera --HAS_EVENT--> CameraEvent
(location, uniqueID)      (location, timestamp)
```

`Vehicle` properties: `model`, `color`, `plate_number`. `Crime` properties: `location`,
`description`, `date-time`.

### 15.3.1 Identifying the initial case

Query: *"Return one crime node currently under investigation"*. The system detects a
graph visualization is appropriate and the generator adds a `status = 'investigation'`
constraint. Generated Cypher (figure 15.12):

```cypher
MATCH (c:Crime) WHERE c.status = 'investigation' RETURN c LIMIT 1
```

Result: a `CRIMINAL TRESPASS` crime node. Its description mentions a black vehicle with
partial plate "EB" — the summary surfaces this detail buried in the description field,
demonstrating **intelligent summarization**.

### 15.3.2 Spatial analysis of surveillance coverage

Crime node added to selection. Query: *"Return any ANPR camera node located within 1 km
from the selected crime."* The system resolves "the selected crime" from selection
context and uses `point.distance()` to filter `ANPRCamera` nodes within 1 km. Result: a
**map visualization** alongside the graph view, markers colored to match graph nodes —
demonstrating **spatial query processing**, **selection-aware NL understanding**, and
**intelligent visualization selection** (map + graph together).

### 15.3.3 Vehicle pattern detection

Camera node added to selection. Query: *"Return the vehicles detected by the selected
camera on June 15, 2023. The vehicle is black and its license plate must start with
EB."* Combines selection reference with explicit constraints (date, color, partial
plate). Result: multiple vehicle nodes connected to the camera through detection events.

### 15.3.4 Context-aware request refinement

Refined query, relying on the system to pull description/date constraints from the
selected crime node rather than restating them: *"I'm an investigator working on the
selected crime. I need all vehicle nodes compatible with the description, detected by the
selected camera the day of the incident. Are there any significantly more likely to be
involved?"*

Same vehicles returned, but the **summarization now includes deeper analysis**: one
vehicle (plate `EB16946`) was detected **twice** around the incident time, suggesting "a
potential circuit of the area." This shows the system **autonomously extracting
constraints from node properties** and **analyzing temporal patterns** for suspicious
behavior, not just matching criteria.

### 15.3.5 Historical record analysis

Final refinement adds: *"Some of these vehicles may be owned by previous offenders. What
vehicles are most likely to be involved?"* The system expands analysis to **ownership
relationships and criminal records**, discovering the repeatedly-detected vehicle is
owned by someone with a **prior conviction for criminal trespass** — the same offense
type under investigation. The summary agent highlights this connection in both the
general summary and analysis section.

This demonstrates: contextual awareness across multiple refinements, integration of
spatial/temporal/historical evidence, pattern identification, and findings presented to
support investigative decisions.

## 15.4 Future Directions and Enhancements

The implementation is framed as **"a foundation rather than a turkey solution"** — its
value lies as much in how it's built (observability, expert emulation) as in what it
does. Transparency isn't just for debugging; it creates natural points for collecting
feedback, showing both *what* the system does and *why*. The **expert-emulation
pattern**: when facing new challenges, ask "What would an expert do in this situation?"

### 15.4.1 Learning from use

- Collect and categorize **"complaint-like" questions** (responses that didn't meet
  user needs) via LLM-based analysis into a dashboard of pain points guiding priorities.
- Collect **successful interactions**, preserving the reasoning chain for especially
  helpful queries to enhance the example database.
- Analyze **patterns in user questions** to identify clusters benefiting from
  specialized handling (e.g., narrower schema portions, more focused examples).

### 15.4.2 Enhancing core capabilities

- **Schema handling** — emulate how experts build understanding of a KG (running
  preliminary queries beyond the basic schema definition) via **schema enrichment
  agents** that augment the base schema with additional context for query generation and
  result interpretation.
- **Multilayer schema management** — mirror experts working with large KGs at different
  abstraction levels: a detailed bottom layer (all nodes/relationships) and higher,
  domain-focused layers (e.g., vehicle monitoring, criminal justice records) — using
  higher layers for broad understanding while preserving detail for query generation.

### 15.4.3 Advanced evolution paths

- Move beyond pure **in-context learning** (embedding schema/examples in prompts) —
  effective but faces scalability challenges with larger KGs.
- **Fine-tuning** as an alternative: use the schema itself as training data for KG-aware
  agents with deeper, more efficient understanding of graph structure. Cited finding:
  *"in-context learning, although flexible, consistently underperforms compared to
  task-specific adaptation approaches"* — even with the same example sets.
- This wouldn't require abandoning the expert-emulating architecture — components could
  be selectively replaced or augmented with fine-tuned alternatives while keeping the
  observable pipeline structure, and could enable more sophisticated **query planning**.

## Takeaways

- LangGraph's **state-based design** (`StateGraph` + `TypedDict` state + nodes as agent
  functions + edges, including **dynamic conditional edges**) decouples pipeline stages
  while giving each one full context — the pattern generalizes well beyond KG QA to any
  multi-stage LLM pipeline needing branching, retries, and shared context.
- The **expert-emulating pipeline** (intent detection → schema extraction → text-to-Cypher
  → query execution → conditional summarize/retry/end) is a concrete, reusable template
  for "text-to-X" query agents over structured data sources.
- **Configuration and schema providers** externalize prompts, notes, examples, and
  schema-filtering rules from code — separating "what the LLM needs to know" from "how
  the pipeline runs," which eases tuning and versioning.
- **Retry-as-a-conditional-edge** (`post_query_execution` routing to `"retry"` up to 3
  attempts) is a clean, minimal error-handling pattern: no separate try/except
  orchestration logic outside the graph itself.
- The **generator-based streaming interface** (`processQuestion` yielding
  `(type, payload, state)` triplets) is a reusable pattern for exposing any LangGraph
  pipeline's intermediate steps to a frontend without coupling the pipeline to
  presentation concerns.
- **Observability is a feature, not just a debugging aid** — every intermediate
  reasoning step captured in state doubles as a dataset for identifying failure patterns,
  harvesting good few-shot examples, and deciding where to invest in fine-tuning.
- Streamlit is presented explicitly as a **prototyping/demo tool**, not a production
  recommendation — the author flags that production deployments would likely need a more
  specialized frontend.
