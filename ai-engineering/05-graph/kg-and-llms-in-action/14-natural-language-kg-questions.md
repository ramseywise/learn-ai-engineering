---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 14: Asking a KG questions with natural language"
confidence: high
cleaned: 2026-07-29
---

# Ch 14 — Asking a KG Questions with Natural Language

Chapter goal: build an advanced question-answering system over a knowledge graph (KG)
that mimics domain-expert reasoning, using a law-enforcement analyst as the running
example. Contrasts standard **retrieval-augmented generation (RAG)** with a new
**"expert emulation"** method that captures how a skilled analyst actually queries a KG.
Chapter 15 follows with a full hands-on implementation.

Four pillars of the framework:
- Understanding and properly routing different types of user questions
- Extracting and representing domain knowledge in a form LLMs can use effectively
- Implementing expert-like reasoning patterns for query construction
- Ensuring results are presented in meaningful, actionable ways

The system is designed integration-first, assuming a front-end layer will render
results as graphs, tables, charts, or maps — this assumption shapes prompt design
throughout (response structuring, output-type routing, visualization-aware summaries).

## 14.1 Querying a Knowledge Graph in the Policing Domain

Running example: a law-enforcement analyst who has strong domain intuition and
contextual judgment but lacks the technical skill to write graph queries directly.
The agency has built a KG as a "single source of truth" connecting roles, processes,
and data across frontline officers, detectives, forensic experts, and analysts.

### 14.1.1 Enabling domain experts with knowledge graphs

Querying KGs is traditionally a technical task, walling off domain experts. Removing
that barrier unlocks:

- **Using expertise** — domain experts bring contextual knowledge for nuanced,
  accurate queries.
- **Timely decisions** — direct KG access removes bottlenecks in time-critical fields.
- **Overcoming technical barriers** — most experts lack the skill to write complex
  graph queries; removing this barrier expands accessibility.
- **Resource efficiency** — less reliance on IT/data science teams to generate queries.
- **Skill specialization** — experts stay focused on domain mastery, not query syntax.
- **New perspectives** — hands-on access surfaces insights technical users might miss.
- **Enhanced problem-solving** — hands-on exploration enables creative, tailored
  problem solving.
- **Maximizing ROI** — KGs are a significant investment; broad usability maximizes
  their value.
- **Cross-functional collaboration** — shared data access bridges technical/nontechnical
  teams.
- **Shared understanding** — broader access builds a unified approach to problem solving.

## 14.2 RAG for KG Querying: Capabilities and Challenges

LLMs alone answer from training data, which is of little use to domain experts asking
specialized questions (e.g., "What is the legal definition of probable cause?" is not
useful to a trained officer). To be beneficial an LLM must give access to
organization-specific information — the standard approach is **RAG** (from chapter 13).

### 14.2.1 RAG effectiveness with complete context

Demonstration: asking an LLM to "Generate a summary of witness statements related to
CASE123" fails without context (no prior knowledge of the case) but succeeds well once
witness statements are retrieved and injected as context — this turns the task into
straightforward summarization, which LLMs handle well.

**Listing 14.1 Sample witness statements for LLM prompt context** (five witnesses, A–E,
describing a suspect's appearance/actions at a crime scene).

Prompt template used to test this:

```
You are a detective assistant helping answer the detective's question

[Witness statements]

{{ witness_statements }}

[Question]

{{ question }}
```

Asked to "summarize the witness statements," the model correctly extracts physical
characteristics, actions/behaviors, and scene evidence into a clean bulleted summary.

Asked "Is the perpetrator left-handed?" **with full context (including Witness C)**,
the model reasons across statements (right hand for wallet vs. bandage on left index
finger vs. holding phone with left hand while walking) and concludes: *"Based on the
available evidence, I would say that it's likely that the perpetrator is left-handed."*
It correctly hedges ("people can be ambidextrous... further investigation is needed").

This shows RAG can direct the LLM toward relevant pieces of information and surface
insights useful to an investigation — but only when the retrieval is complete.

### 14.2.2 RAG fragility with incomplete retrieval

RAG's success is tightly coupled to retrieval quality: LLMs cannot generate accurate
answers without sufficient context.

**Same question, Witness C's statement removed.** The model now answers using only
Witnesses A, B, D, E and concludes the *opposite*: *"it seems more likely that the
perpetrator is right-handed rather than left-handed."* Removing a single witness
statement flips the model's conclusion — the model is confident in both cases despite
the underlying context being incomplete.

> Verbatim: "Figure 14.1 illustrates this process. Even though the AI agent confidently
> processes the available context—caused by the retriever failing to identify critical
> documents—leads to wrong conclusions. This visualization emphasizes a key limitation
> of RAG systems: their outputs are only as good as their retrieval step, regardless of
> the model's confidence in its response."

**Figure 14.1** (RAG system limitations): private data → embedded/indexed into a vector
database → semantic retriever fails to identify some relevant document → context is
incomplete (missing critical info from unidentified documents) → AI agent's brain still
reasons confidently ("Considering these facts, I can generate an answer") → agent
generates the wrong answer.

Additional nuance:
- RAG performs better when source material is divisible into fine-grained, independent
  **passages** — small blocks of information usable to construct relevant context.
- In practice answers often span multiple documents, and retrieval may not capture all
  of them; some documents may be relevant without containing the literal answer.
- When retrieved passages lack appropriate granularity, or the retriever misjudges
  relevance, context becomes fragmented, pushing the model toward incorrect assumptions
  and plausible-but-inaccurate details.

This motivates an approach that captures the nuanced, structured insight a domain
expert applies when querying a KG directly — **structured retrieval combined with
context-aware reasoning**, rather than passage-level semantic retrieval.

## 14.3 Schema-Based Approach for Querying KGs

Thought experiment: constrain a panel of domain experts to a "human-powered RAG"
approach — read documents, mark similar/relevant paragraphs, select a dozen as context,
answer using only that subset plus common sense. Even with real experts, this process
is unimpressive: forced into RAG-like constraints, their answers lack the depth their
genuine expertise would normally produce.

**What would an expert do instead?** Understand the **schema** — the graph's blueprint.
If a question involves people, it likely involves a node labeled `Person`. Understanding
the schema converts natural-language requests like "show me the red Camaros seen in
this area at that time" into a precise traversal, e.g. entities/relationships such as
`Person —Owns_car→ Car —Captured_by→ ANPR` (automatic number-plate recognition), refined
by constraints (car color = red, model = Camaro, ANPR camera in a specific area/time
frame). The schema guides which nodes/relationships to select and how to constrain them.

### 14.3.1 Understanding and using graph schemas

> Verbatim: "Understanding a graph schema—the data modeler's structured interpretation
> of the domain—is like understanding the layout of a city before navigating through
> it: it lets us identify where specific types of information are stored and how they
> are linked."

**Figure 14.2** walks the mental process an expert follows translating a natural-language
question into a formal Cypher query, in three stages:

1. **Parsing** the natural-language request into semantic components. "Red Camaro
   spotted in this area at that time" maps concepts (red Camaros, area, time) to their
   graph counterparts:
   - **Entities** — e.g., "red Camaro" maps to node label `Car` with properties `Color`
     and `Model`.
   - **Relationships** — the query implies relationships like "`Person` owns `Car`" and
     "`Car` captured by `ANPRCamera`."
   - **Constraints** — specific conditions refining the traversal: color red, model
     Camaro, ANPR camera in a specified area.
2. **Mapping** these semantic components to schema elements/classes (`Vehicle`,
   `CameraEvent`, `ANPRCamera` nodes with their relationships).
3. **Constructing** a formal Cypher query with the appropriate traversal patterns and
   constraints.

This produces **constrained traversals** — e.g., "Among all these entities (cars,
people, cameras), connected in this specific way (`OWNS_CAR`, `CAR_CAPTURED_BY_ANPR`),
which ones possess the characteristics I'm interested in?" Constrained traversals are
the fundamental building blocks for constructing formal queries of any complexity —
they compose to build sophisticated queries navigating intricate data relationships,
possibly through multiple layers (e.g., an initial constrained traversal — possibly with
aggregations — identifies a subgraph that seeds further exploration). This compositional
approach translates human-language intent into structured queries a graph database can
execute, bridging human language and machine-readable data.

Example Cypher pattern shown in Figure 14.2:

```cypher
MATCH path = (v:Vehicle)<-[:PLATE_READ]-(e:CameraEvent)-[:HAS_EVENT]-(c:ANPRCamera)
WHERE
  v.model = "Camaro" AND
  v.color = "Red" AND
  $startTime >= e.timestamp >= $endTime AND
  point.distance(c.position, $areaCenter) < $areaRadius
RETURN path
```

## 14.4 Think Like an Expert: Using Metadata for Enhanced Querying

Expert reasoning = systematically understanding and navigating a KG's schema. LLMs,
trained on massive text corpora, can recognize patterns and interpret schema structure
similarly, effectively "thinking like an expert" when given the right inputs.

Core steps in answering questions using KGs (mapped to remaining chapter sections):

1. **Intent detection** (§14.5) — understand the intent behind the question first, to
   route the request to specialized pipelines and pick the right answering method.
2. **Schema/metadata extraction** (§14.6) — extract and enrich the schema so the LLM
   has a deeper, navigable understanding of the graph.
3. **Expert reasoning mimicry** (§14.7) — techniques to push the LLM's reasoning closer
   to a human expert's, despite intrinsic LLM reasoning limitations.
4. **Summarization** (§14.8) — integrate a summarization step to distill and highlight
   the important parts of the answer.

**Figure 14.3** (system overview) — six components: **Intent detection** → **Query
generation** (also fed by **Schema extraction**) → **Query execution** → **Output**
(feeds **Visualization** and **Summary generation**). System processes user questions
and selection inputs while supporting error feedback during query execution (execution
errors loop back into query generation).

**Key paradigm shift**: from *generating an answer* to *asking the right question*.
Traditional RAG builds context around a question so a grounded answer can be generated
from question+context — emphasis on crafting a relevant, accurate answer. This chapter's
approach instead converts questions into **formal queries** — the challenge is properly
*formulating the question* so it can directly extract factual data from the KG, ensuring
precise, factual retrieval rather than free-form generation.

## 14.5 Intent Detection: Understanding User Expectations

First component in the pipeline (Figure 14.4). Needed because how an answer should be
*presented* depends on user intent — e.g., the "red Camaros" example could be rendered
as an investigation board (graph with nodes/relationships), a table (plate number,
camera location, time of capture), or a map (camera locations). Each presentation has
trade-offs depending on user needs/preferences.

Reasons to do intent detection first:
- Mimics expert reasoning — understanding intent is the first step any expert takes.
- Relies on **semantic understanding**, a task LLMs excel at.
- Relatively straightforward, so it's easy to follow/debug and forms a solid foundation.

### 14.5.1 Classifying by visualization type

The classifier's output set is not fixed — it can be revised as the system evolves.
Example front-end capability set:
- Graphs as interactive canvases with nodes/relationships
- Tables with basic sort/search
- Charts or plots
- Interactive maps (GIS-like)

**Figure 14.5**: Intent detection routes `Data-related` requests to Graph / Chart /
Table / Map, and separately routes `System-related` / `Feedback-Issues` requests.

Characteristics of a good classification prompt:
- **Clear instructions** — task explicitly stated up front.
- **Defined categories** — clearly differentiated so the model knows the boundaries.
- **Examples** — few-shot examples give a clear idea of expected classification.
- **Boundary cases** — examples near category boundaries teach nuance.
- **Expected output format** — guides consistent presentation of answers.
- **Fallback options** — a catch-all category plus instructions on when to use it,
  preventing forced/incorrect classifications.

Example classification prompt (paraphrased structure):

```
Given a Text delimited by triple backticks representing a user question,
identify the best output of the presentation.

Select one of the possible outputs in the following list:
"graph", "table", "chart", "map".

The first step is to understand if the user explicitly asks for a specific
output type to show the results.

For example, if the user asks for graph elements such as paths or nodes or
relationships, then the output must be a graph in any case.

If the output type is not explicit it is usually "graph":
- "table", only when the user asks about aggregation, ordering, and statistics;
- "chart", if the user asks for plotting distributions;
- "map", if the user asks for showing locations, places or other entities
  with a strong location property;

If you do not understand the output from previous cases the output
should be "graph".

Here you can find some examples:

Example: Location of last 10 narcotics related crimes
Output: {"type": "map", "reason": "type is map because it involves showing locations"}

Example: Distribution of crimes over time
Output: {"type": "chart", "reason": "type is chart because a distribution can be plotted"}

Example: Maximum, minimum, and average number of crimes per district
Output: {"type": "table", "reason": "type is table because aggregations are requested"}

Example: People involved in or related to crimes investigated by Inspector Morse
Output: {"type": "graph","reason": "type is graph because entities and relationships are implied"}

The output must be in JSON format. Do not explain the result.

###Text:```{{question}}```
###Output:
```

The prompt is divided into three sections:
- **Task definition** — the generic task plus bias toward graph representation and
  per-class expectations.
- **Few-shots section** — examples with expected responses; format is simple and
  easier to demonstrate than explain, in the law-enforcement domain, each including a
  reasoning step in the response.
- **The actual question** — inserted following the same format as the few-shots.

Test results (via the prompt) correctly classify: "location of latest shooting" → map;
"crimes per month 2020 vs 2019" → chart; "main suspects in recent burglaries" → graph;
"traffic fatalities last year vs previous" → table.

> **Note (reason field)**: the `reason` field is included for debugging and to later
> exploit generated tokens to improve response quality — not used in downstream
> processing at this stage.

**Boundary-case handling**: "What are the most common types of organized crime involved
in human trafficking?" is ambiguous — it implies both visual entity/relationship
networks and requires aggregation/summarization of "common types." The prompt classified
it "graph" because relationships between crime types and trafficking outweighed simple
listing — not a clear-cut answer, but exactly the kind of example that belongs in the
few-shot section to shape nuanced behavior. The book deliberately biases fallback
toward **"graph"** as a reasonable catch-all, since the system is querying a graph
database after all.

### 14.5.2 Is it data, documentation, or just complaining?

To fully empower nontechnical users, intent detection must also handle non-data
questions:
- *"Is it possible to export data from the system into a CSV file?"*
- *"How do I use the system to assess the risk level associated with a suspect?"*
- *"The system is too slow and keeps freezing. What can be done about it?"*
- *"It would be great if the system had [feature XYZ]. Can this be added?"*

These reflect real user needs even though they don't map to KG queries. Users may seek
system functionality, explanations, or give feedback. Three broad categories:
- **Data-related questions** — require direct KG access (covered above).
- **System-related questions** — about system capabilities/operation/risk.
- **Feedback and complaints** — frustration or improvement requests.

System-related questions split into two subcategories:
- **Documentation-related** — resolvable via user documentation/manual/help.
- **Schema-related** — technical questions about how the KG is structured/modeled.

**Figure 14.6**: broadens intent detection — Data-related → Graph/Chart/Table/Map;
System-related → Documentation or Schema; Feedback/Complaints → separate category.

Expanded classification prompt (paraphrased):

```
You are an AI assistant tasked with categorizing questions related to a law
enforcement knowledge management system. Your job is to classify each
question into one of three main categories:

1. **Data-Related:** Questions that require direct access to or knowledge of the data
2. **System-Related:** Questions related to the system's functionality, features, and access
3. **Feedback/Complaints:** Questions that are either not answerable by the system...

**If the question is classified as "System-Related,"** you will further classify it:
- **Documentation-Related:** Questions answerable by referring to system docs
- **Schema-Related:** Questions related to the structure of the knowledge graph

**Task:** For each question below, first classify it into one of the three main
categories...

**Example Questions and Expected Output:**

1. **Question:** "Is it possible to export data from the system into a CSV file?"
   **Answer:**
   {
     "question": "Is it possible to export data from the system into a CSV file?",
     "category": "System-Related",
     "subcategory": "Documentation-Related",
     "reason": "The question asks about the capability of the system regarding
     data export, which falls under system functionality."
   }

2. **Question:** "How do I use the system to assess the risk level associated
   with a suspect or location?"
   **Answer:**
   {
     "question": "...",
     "category": "System-Related",
     "subcategory": "Schema-Related",
     "reason": "The question involves assessing risk, which requires
     understanding the graph schema and structure of the data related
     to suspects and locations."
   }

3. **Question:** "What permissions do I need to access restricted data?"
   → category: System-Related, subcategory: Documentation-Related

4. **Question:** "Why isn't the system responding to my queries?"
   → category: Feedback/Complaints (expresses a complaint about system
   performance, rather than asking for specific data or features)

5. **Question:** "What types of data visualizations can the system generate?"
   → category: System-Related, subcategory: Documentation-Related

**Begin classification:**
{{question}}
```

**Misclassification example / model-size effect**: "How often is the knowledge graph
updated to reflect the latest information?"
- A **smaller/quantized LLM** answered: `category: "Data-Related"`, reasoning "concerns
  the frequency of updates within the data itself" — incorrect, since inferring update
  cadence from node timestamps wouldn't reliably reflect actual update scheduling.
- A **full-scale LLM** answered: `category: "System-Related"`, `subcategory:
  "Documentation-Related"`, reasoning it's about update frequency (a system/process
  fact, not data content) — correct.

> Verbatim: "Larger models can detect that this question pertains to system
> functionality and refer to the documentation, labeling it as 'System-Related' under
> 'Documentation -Related.' Smaller or quantized models, however, may misinterpret the
> question as concerning the data itself and incorrectly classify it as 'Data-Related.'"

Lesson: the `reason` field's content in both cases is diagnostic — it reveals the
smaller model lacks context, signaling that the task-definition section should be
enriched with more background information to guide correct classification.

**Design considerations for classification prompts** — trade-off between a single
broad prompt and a multistage approach (applies to classification tasks generally):

| Approach | When to prefer | Benefits |
|---|---|---|
| **Single broad prompt** | Simplicity and reduced management overhead are priorities; model accuracy is acceptable even for complex tasks | Streamlines classification, quicker implementation, easier maintenance, good for rapid deployment |
| **Multistage approach** | Accuracy/flexibility is more critical, or frequent adjustments to categorization are anticipated | More granular control, better handling of complex questions/edge cases, each stage can be refined independently, more robust/reliable results |

Recommended path: start broad/simple, evaluate effectiveness in practice, and
transition to multistage only as request complexity or new requirements emerge.
Postponing the split also lets you gather real-world examples first, which are
invaluable for refining the eventual multistage classification.

## 14.6 From Schema to LLM-Ready Context

**Figure 14.7**: the schema-extraction phase transforms raw schema information into
formats LLMs can effectively process — foundational for enabling nontechnical users to
query KGs the way an expert would.

### 14.6.1 Schema extraction and representation

The challenge: extract the schema from the KG and convert it into a form usable by an
LLM to help it understand the question and produce a proper Cypher query.

First approach: **`apoc.meta.schema`** [1] — computes the schema from the graph's
current structure.

**Listing 14.2 Response format for `apoc.meta.schema`** (abbreviated):

```json
[
  {
    "label": "[LabelName]",
    "properties": {
      "[PropertyName1]": {
        "type": "[PropertyType1]",
        "mandatory": [true|false],
        "unique": [true|false]
      },
      "[PropertyName2]": { "type": "...", "mandatory": [true|false], "unique": [true|false] },
      ...
    },
    "relationships": [
      {
        "type": "[RelationshipType]",
        "target": "[TargetLabelName]",
        "properties": {
          "[RelationshipPropertyName]": {
            "type": "[RelationshipPropertyType]",
            "mandatory": [true|false],
            "unique": [true|false]
          }
        }
      },
      ...
    ]
  },
  ...
]
```

Problem: this is a **technical database schema** — it includes many details irrelevant
to the goal: helper/administrative nodes, technical metadata properties, unnecessary or
redundant type labels, unused relationships/properties. These clutter the schema with
elements useful for database management but not for domain understanding. The fix is a
**conceptual KG schema**: a distilled, meaningful structure focusing only on entities
and relationships that convey the essential domain model.

The **conceptual schema** is a simplified, domain-relevant subset of the technical
schema, stripping technical complexities and irrelevant metadata, prioritizing clarity
and usability. Why this simplification matters:

- **Alignment with human reasoning** — reflects how domain experts understand the KG
  using only relevant entities/relationships/properties, aligning the schema more
  closely with natural-language reasoning and making it easier to map questions
  accurately to graph elements.
- **Reduced cognitive load for LLMs** — LLMs are more efficient when given focused,
  relevant data rather than the full complex technical schema; a streamlined schema
  lets the model concentrate on meaningful information, increasing accuracy without
  distraction from extraneous details.
- **Minimized risk of query errors** — technical schemas often contain
  implementation-specific elements, redundant labels, or metadata that could confuse
  the model and lead to query-generation errors; the conceptual schema eliminates this
  noise.
- **Enhanced model interpretability** — presents the KG in a more human-readable form,
  aligning it with how LLMs are trained to interpret text, capturing the structure LLMs
  most effectively use to infer intentions and mappings.

Transition path from `apoc.meta.schema` output to a conceptual schema requires human
intervention: either manually describe the domain model ("curating" the schema), or
define a **skip list** to filter unneeded elements from the APOC results, distilling
the technical schema to its conceptual core.

**Figure 14.8**: pipeline — technical schema (via APOC) → **Schema filtering** →
conceptual schema → **Schema mapping** → LLM-friendly description (text).

Two representation formats compared:

**Narrative schema representation** — nodes/relationships described in natural language
with rich context and examples; useful for human readers needing thorough understanding
but more challenging for an LLM to process efficiently when the goal is query
generation.

**Listing 14.3 Narrative schema representation** (excerpt):

```
**Nodes:**

1. **Vehicle**:
   - **Properties**: `color`, `make`, `model`, `style`, `plate_number`
   - Node example:
     - (:Vehicle {make: "Toyota", model: "Camry", style: "Sedan", plate_number: "XYZ123"})

**Relationships:**

1. **OWNED_BY**: Represents the relationship of ownership between a vehicle and a person
   - Example:
     - (:Vehicle {plate_number: "XYZ123"})
       -[:OWNED_BY]->
       (:Person {name: "Alice"})
```

As the schema grows, this verbose narrative style becomes less systematic and harder
for a language model to parse consistently.

**LLM-friendly schema representation format** — a concise, consistent structure with
just entity names, properties, and relationships, stripped of verbose description:

**Listing 14.4 LLM-friendly schema representation format:**

```
Nodes:
(:Vehicle {
    color: STRING,
    make: STRING,
    model: STRING,
    style: STRING,
    plate_number: STRING
})

Relationships:
(:Vehicle)-[:OWNED_BY {since: DATE}]->(:Person)
```

This is easy for the LLM to process because it uses a standardized syntax aligning
with entity types and their attributes, with relationships described clearly via
property types and minimal-but-necessary contextual information.

### 14.6.2 Enriching schemas with descriptive annotations

Schema structure alone can be insufficient — two concrete failure modes:

1. **Value-encoding ambiguity**: user asks to "find all black vehicles involved in a
   crime." A naive LLM might translate this to `Vehicle.color == "black"`, assuming
   the string is stored in readable form. If the database actually stores abbreviations
   (e.g., `"BLK"` for "black"), the query silently misses all matching records, giving
   the false impression no black cars were involved.

2. **Relationship ambiguity**: KG includes both `COMMITTED` and `CO_OFFENDS_WITH`
   relationships. Asked to "list all suspects who have been involved in multiple crimes
   with another person," the LLM has no clear basis to choose between them (direct
   co-commission vs. co-offending histories) — it may guess incorrectly, amplifying
   ambiguity and leaving the user feeling the system doesn't fully grasp their request.

**Fix — mimic expert familiarization**: an expert facing unfamiliar data familiarizes
themselves with the KG structure, consults documentation/data dictionaries, and builds
a "cheat sheet" capturing terminology, abbreviations, and relationship meanings (e.g.,
noting "BLK" = "black" in the vehicle color property, or that `COMMITTED` and
`CO_OFFENDS_WITH` capture involvement in criminal activities from different angles).
This is replicated by systematically **annotating** the KG's schema — documenting node
classes, relationship types, and properties with descriptions that capture these
nuances — producing an annotated schema that guides the LLM to more informed and
contextually accurate query translations.

**Listing 14.5 Annotated schema representation format:**

```
Nodes:
/* Represents a vehicle involved in various incidents or owned by individuals */
(:Vehicle {
    color: STRING, /* Color of vehicle, BLK, GRY, SIL, WHI, etc*/
    make: STRING,  /* Manufacturer: BMW, BUIC, CADI, CHEV, etc */
    model: STRING, /* Model of the vehicle: IMP, ALT, SON, SEB, CIV, etc */
    style: STRING, /* Body style: SUV, SEDAN, etc */
    plate_number: STRING /* Vehicle license plate */
})

Relationships:
/* Ownership relationship from vehicle to person, with start date of ownership */
(:Vehicle)-
[:OWNED_BY {since: DATE /* Date ownership began, ISO format */}]
->(:Person)
```

With annotations as inline comments, the LLM has access to detailed descriptions that
guide it in accurately interpreting the schema, leading to more precise queries that
reflect the true data structure.

### 14.6.3 A practical approach to schema representation

Recommended approach: a **YAML configuration file** to manage the output of
`apoc.meta.schema` — distilling it by skipping irrelevant elements and adding rich
descriptions. Two main sections: `skip` and `descriptions`.

**Skip list** — lets users filter out certain classes, relationships, or properties
deemed not part of the core conceptual KG schema.

**Listing 14.6 Schema config: `skip` section:**

```yaml
schema:
  skip:
    classes: []          #1
    relationships: []    #2
    properties: []       #3
```
- `#1` Classes to skip
- `#2` Relationships to skip
- `#3` Properties to skip

**Descriptions** — where detailed annotations are added for schema elements, describing
purpose/semantics of classes, relationships, and properties, as granular as needed, so
both the LLM and human users share a clear understanding of the structure.

**Listing 14.7 Schema config: `descriptions` section:**

```yaml
descriptions:
  classes:
    Class1: "Description of class 1"
  relationships:
    Rel1: "Description for relationship type 1"
  properties:
    Class1:
      property1: "Description for Class1.property1"
      property2: "Description for Class1.property2"
      [...]
    Rel1:
      property1: "Description for relationship property Rel1.property1"
```

Benefits of the YAML-driven approach:
- **Customization** — easily adjust the schema representation by editing the YAML to
  include only necessary components and tailored descriptions.
- **Maintainability** — a centralized, human-readable configuration that's easy to
  update as the schema evolves, keeping it aligned with the domain and the LLM's needs.
- **Scalability** — as the KG grows, this provides a manageable way to handle schema
  modifications so the LLM keeps up with new data/relationships without being
  overwhelmed by unnecessary complexity.

**Listing 14.8 Schema description: output example** (abbreviated):

```
### Graph Schema Overview

#### Node Types
(:Vehicle /* Represents a vehicle involved [...] */ {
    color: STRING, /* Color of vehicle, BLK, GRY, SIL, WHI, etc*/
    make: STRING,  /* Manufacturer: BMW, BUIC, CADI, CHEV, etc */
    model: STRING, /* Model of the vehicle: IMP, ALT, SON, SEB, CIV, etc */
    style: STRING, /* Body style: SUV, SEDAN, etc */
    plate_number: STRING /* Vehicle license plate */
})

#### Relationships
(:Vehicle)-[:OWNED_BY /*<description>*/ {since: DATE /* <description> */}]->(:Person)
```

## 14.7 It's Time to Think: Understanding LLM Reasoning

With intent detection and an LLM-friendly annotated schema in place, the next step is
the most challenging: translating text into Cypher queries. **Figure 14.9** shows query
generation as the convergence point — combining processed user intent and schema data,
while also using execution-error feedback to iteratively refine query formulation.

LLMs, despite appearing to reason, may "rush" to a conclusion on complex/nuanced
questions, relying on data-pattern shortcuts rather than fully reasoning through the
problem. Two established techniques give the model "time to think" by forcing
token-by-token generation before the final answer, effectively scaling computational
effort to question complexity:

- **Chain-of-thought prompting** [2] — introduces intermediate reasoning steps into the
  response, structuring prompts to require step-by-step articulation, using the LLM's
  pattern-based generation to take a more calculated approach rather than jumping to
  conclusions.
- **Scratchpad techniques** [3] — embed intermediate "workings" in the LLM's output,
  where the model produces tokens representing steps/computations needed to reason
  through complex questions.

### 14.7.1 The order matters: Answer first vs. reasoning first

If an LLM is instructed to give the answer **first**, followed by reasoning, the model
tends to stick with its initial answer. This happens because LLMs generate one token
at a time, effectively committing to prior choices as generation progresses — leading
to reasoning that rationalizes a predetermined response rather than an impartial,
step-by-step thought process.

This is linked to **semantic consistency** [4] — training text typically exhibits
logical coherence (what's said earlier supports what's said later; contradictions are
rare), which acts as a guardrail against rambling but becomes a constraint here, due to:

- **Cumulative context** — because tokens generate sequentially, reasoning/context
  build cumulatively, so the model's commitment to a particular answer can be
  influenced (reinforced) by tokens it has already generated — reinforcing output
  consistency even when wrong.
- **Error propagation** — an error early in token generation can propagate through
  subsequent tokens, since each new token is generated based on prior ones —
  highlighting the importance of careful reasoning and validation at each step.

**Figure 14.10** compares two prompt structures for the same path-finding task
("Find the shortest path between City A and City B"):

| Structure | Behavior | Failure/benefit mode |
|---|---|---|
| **Answer-first** (`{"answer": ..., "reasoning": ...}`) | Model commits to a highway choice early | Defends its choice even when mentioning potential problems (construction); dismisses alternatives without evaluation; adds post hoc rationalizations to support the initial answer; misses opportunity to recalculate |
| **Reasoning-first** (`{"reasoning": ..., "answer": ...}`) | Model identifies all possible routes, evaluates each systematically before concluding | Keeps options open during analysis; considers multiple factors systematically; reaches conclusion based on evidence; maintains appropriate uncertainty; arrives at a different (and more reliable) answer than the quick-response approach |

> Verbatim takeaway: "To encourage transparent and reliable reasoning from LLMs, it's
> important to prompt the model to first provide its step-by-step reasoning, followed
> by the final answer. This structure forces the model to engage in a more thoughtful,
> deliberate process, as it must justify its conclusion through a balanced exploration
> of the problem, rather than simply rationalizing a predetermined response."

Exception: **postponing reasoning until after the answer can make sense for
classification tasks**, where the goal is understanding *how* the system justifies a
choice (especially when it misclassifies) — the reasoning then becomes diagnostic
material for building better few-shot examples that clarify classification boundaries
(as done in §14.5).

### 14.7.2 Thinking in queries: From text to Cypher

Prompt structure for text-to-Cypher generation, combining everything built so far:

- A brief task description and question
- A schema definition with annotations
- Intent-dependent requirements
- Examples
- Optional user selection
- KG-specific annotations
- A reminder of the question
- A reminder of the requirements
- Output format specification

**Figure 14.11** shows the complete flow: three inputs (natural-language question,
schema definition with annotations, optional user selection) → **Input processing**
(1. brief task description and question, 2. schema definition with annotations, 3.
intent-dependent requirements) → **Context building** (4. examples, 5. optional user
selection, 6. KG-specific annotations) → **Final guidelines** (7. question reminder, 8.
requirements reminder, 9. output format specification) → generated output (relationships,
reasoning, Cypher query, success flag).

**1. Brief task description and question** — introduces the translation task, wraps
the user's question in an HTML-like tag (`<QUESTION>...</QUESTION>`) to clearly bound
it from the rest of the instructions:

```
Your task is to generate a Cypher query for a Neo4j graph database, based on the
schema definition provided, that answers the user Question.

The question we need to answer is:

<QUESTION>
{{ question }}
</QUESTION>
```

**2. Schema definition with annotations** — reuses the LLM-friendly schema format from
§14.6, wrapped in an HTML-like `<SCHEMA>` tag, with `/* comments */` annotating classes,
relationships, and properties:

```
The knowledge graph has the following schema, which the Cypher query must follow:

<SCHEMA>
{{ schema }}
</SCHEMA>

consider the comments as annotations
```

**3. Intent-dependent requirements** — incorporates output from intent detection: for
graph/map responses, retrieve not just the answering nodes but also the connecting
relationships; for table responses, clarify that specific properties should be selected
as columns rather than full nodes/relationships. Uses templating syntax (Jinja-like
`{%if%}`/`{%endif%}`):

```
{%if output_type == "graph" or output_type == "map" -%}
The result must be a graph so make sure to follow the schema and the following
requirements:

- Return all the nodes and relationships matched, do not use anonymous
relationships ( such as has (node0)-[:RELATIONSHIP]->(node1) instead use
(node0)-[rel0:RELATIONSHIP]->(node1)

- Aggregate multiple traversals in a single MATCH pattern if possible:
`MATCH path=(p:Person)-[acted:ACTED_IN]->(m:Movie)<-[directed:DI-
RECTED]-(d:Director) RETURN path` instead of `MATCH path=(p:Person)-
[acted:ACTED_IN]->(m:Movie), (d:Director)-[directed:DIRECTED]->(m)`
{%-endif%}

{%if output_type == "table" -%}
The result must be a table, i.e. you must select nodes and relationship
properties and rename them to be presented in a table
{%-endif%}
```

**4. Examples** — few-shot examples of foundational question→Cypher building blocks,
also demonstrating expected format:

```
Use only the provided labels, relationships, and properties; do not use
anything else that is not specified.

If you cannot generate a Cypher statement based on the provided schema,
explain the reason to the user.

{{examples}}

You must respect relationship types and directions.
```

**5. Optional user selection** — if the system supports node/relationship selection,
incorporate the current selection so users can refer to it (e.g., "give me the older
siblings of the selected person"). Represented as a list of items, each with node label
and properties; if the user references a selection that is empty, the model must flag
the issue rather than fabricate a response:

```
{%if selection -%}
Current selection:
{% for node in selection%}
- {{node.label}} node with this properties {{node.properties}}
{% endfor %}
{%-else-%}
The selection is currently EMPTY. If there are references to selected nodes
in the question, it is almost
certainly an error and therefore it is not possible to generate a response.
In this case, 'success' should be false.
{%-endif-%}
```

**6. KG-specific annotations** — user-supplied clarification notes relevant to the
specific KG, kept separate from the core prompt (via a template variable) so the prompt
remains reusable across different KGs without altering its core structure:

```
{{annotations.notes if annotations.notes}}

Do not include any explanations or apologies in your responses.
```

**7. Reminder of the question** — repeated near the end of the prompt to reinforce
context/intent, since the schema section can be long, placing the original question far
from the response start. Also includes an optional `information` field:

```
The question we like to answer may have some information that is relevant for the
Cypher query:

<QUESTION>
{{ question }} {{ information }}
</QUESTION>

{%if output_type == "graph" or output_type == "map" -%}
Remember the requirements:
- Return all the nodes and relationships matched, never use anonymous
  relationships(ie [:RELATIONSHIP]), always use named ones (ie [rel1:RELATIONSHIP]).
- Aggregate multiple traversals in a single MATCH pattern if possible
{%-endif%}
```

The optional `information` field can carry, e.g., a **previous failure's error message**
from the database, letting the model review its prior decision and generate an
error-free query on a retry — this is the chapter's core **validation/retry loop**
mechanism for generated Cypher (paired with the "Execution error" feedback path shown
in Figure 14.9/14.11).

**8./9. Output format specification** — final JSON schema for the response, with field
hints and comments describing expected content:

```
Use the "reasoning" field to explain your plan for the cypher query

Answer only in valid JSON in the following JSON format, nothing else (no
<ANSWER> tags or anything like that):

{
"relationships": [...], list of relationships to traverse, empty if not traversal
is needed
"reasoning": "...", this is the scratch pad for your reasoning
"query": "<Cypher query>", must be a string and a valid Cypher query.
"success": <true/false>, where true means that a Cypher query (following
the schema) was returned.
}
```

### 14.7.3 Structuring output for reliable query generation

Field ordering in the JSON output is deliberate, following the "reasoning-first"
principle from §14.7.1:

1. **`relationships`** (listed first) — the model lists relationships it believes it
   should traverse *before* committing to the query. LLMs may hallucinate relationships
   not present in the schema; asking the model to list intended relationships "out
   loud" first significantly reduces this hallucination risk. Tuning note: if a model
   doesn't hallucinate relationships, this field can safely be dropped; if a model
   commits too early to relationships, soften the requirement to ask for relationships
   it will "potentially traverse."
2. **`reasoning`** — gives the model time to think by breaking down the problem,
   defining a plan, etc., before committing to an answer. Can be extended with more
   specific guidance for particular use cases via phrasing like *"Use the 'reasoning'
   field to explain your plan for the cypher query."*
3. **`query`** — the final Cypher query, generated last, after relationships and
   reasoning — because it's requested after `relationships`/`reasoning`, the model is
   pushed to be coherent and avoid nonexistent relationships. Guiding the model through
   relationship identification → reasoning → final query formulation grounds the output
   the way a human expert would tackle the task, producing more reliable/trustworthy
   results than asking for the Cypher query directly.

**Ensuring example consistency** — few-shot examples must conform to the same response
format to avoid introducing ambiguity during generation:

```
{%for example in examples%}
Example:
<QUESTION>{{example.question}}</QUESTION>
{
...
"query": "{{example.answer}}"
{{ '"reasoning":"'+example.reasoning+'"' if example.reasoning else "..."}}
}
{%endfor %}
```

The `"..."` notation acts as a placeholder giving the model freedom to generate content
autonomously for fields not fully specified in an example. This lets you test how the
model handles reasoning without dictating it, then selectively add critical reasoning
content to examples without radically changing the overall response.

## 14.8 Response Summarization: From Results to Insights

Having converted questions into Cypher queries and executed them, focus shifts to
ensuring results are accessible and insightful, not just correct. Graph visualization
excels at showing relationships/structure, but valuable information often lies in node
properties or the broader context of results, which isn't always visually obvious —
this is where **summarization** comes in (Figure 14.12).

The summarization step is unique in the pipeline: it's the **first and only component
with access to the actual data** the user is seeking. Earlier steps focus on
understanding the question and formulating the right query; summarization bridges the
gap between raw data and user understanding, providing a quick overview before the user
dives into the detailed graph exploration. It can also be extended with post-processing
for additional context/insights beyond basic presentation.

**Figure 14.12**: Output generation pipeline — processed query results feed a
**dual-output** approach: **Visualization** (graphs/tables/etc.) and **Summary**
(creates summaries and analyzes the query results).

Summarization prompt structure:

```
Our user asked this question:

<QUESTION>
{{ question }}
</QUESTION>

To answer the question, we decided to execute this cypher query:

<QUERY>
{{ query }}
</QUERY>

The query returned a graph containing this data:

<RESULTS>
{{ records }}
</RESULTS>

{%if selection -%}
Current selection:
{% for node in selection%}
- {{node.label}} node with this properties {{node.properties}}
{% endfor %}
{%-endif-%}

Your task is to summarize the results we sent to the user with the information
just provided. Consider that the user will see the results in a graph format
within a graphical user interface, but we also want to provide a
textual summary along with the canvas.

Please keep in mind that much of the resulting data is actually irrelevant
considering the question, but is returned anyway for completeness. Your job
is to filter out this data so the summary contains only factual information
that is relevant considering the question.

Does the question request analysis of the returned data? If so, include a
few sentences to extract the requested analysis/insight.

This is the question again

<QUESTION>
{{ question }}
</QUESTION>

Answer only in valid JSON in the following JSON format, nothing else (no
<ANSWER> tags or code blocks and so on):

{
"results_analysis": true|false, Check if the question contains an implicit or
explicit request for analysis of the returned raw data

"reasoning": "...", Scratch pad for your reasoning. include reasoning about
the summary and reasoning about the result analysis if needed

"summary": "..." must be a string and a meaningful and factual summary
(use \n and basic markdown tags to highlight the important bits).
}
```

Structural breakdown, achieving summarization goals while remaining flexible for
future enhancements:

- **Context chain reconstruction** — reconstructs the complete chain (original
  question → executed Cypher query → results), each wrapped in HTML-like tags for
  clear boundaries: the question conveys user intent, the query shows how intent was
  interpreted, the results are the raw data, and the current selection (if any)
  maintains user context.
- **Dual-output awareness** — task description explicitly acknowledges results will be
  shown both as a visual graph *and* a textual summary, guiding the LLM to
  **complement** rather than merely repeat what's visible in the graph interface.
- **Explicit filtering instruction** — graph queries often return complete paths for
  visualization purposes containing much irrelevant data; the model is explicitly
  instructed to filter this out so summaries stay focused and meaningful.
- **Opt-in analysis** — result-analysis capability is gated behind a simple question:
  "Does the question request analysis of the returned data?" This keeps analysis tied
  to user intent rather than generating unrequested insights, while providing a
  foundation for future analytical expansion.
- **Question reminder** — repeated before the output format spec, ensuring the model
  stays focused despite potentially lengthy results sections.
- **Progressive JSON output** — `results_analysis` flag (compels an explicit yes/no
  decision, useful for monitoring, and when `true` it materially influences the
  subsequent `reasoning` step) → `reasoning` (must align with both the prompt and the
  analysis decision) → `summary` (final output, with markdown formatting hints for
  readability).

This structured approach keeps summaries consistent, relevant, and adaptable, with a
clear separation of concerns (decision-making via reasoning → final output) that keeps
the component maintainable and extensible. The summarization step completes the
pipeline, transforming raw data into accessible insights while remaining flexible to
evolving user needs — it is the final touchpoint with users, critical for both
answering questions accurately and presenting those answers usefully.

## Takeaways

- **Expert emulation** provides a systematic framework for building and improving KG
  question-answering systems: for any challenge, ask "What would an expert do?" and
  break their approach into implementable steps.
- Standard **RAG is fragile** for KG querying — its output quality is strictly bounded
  by retrieval completeness; a single missing document/passage can flip an LLM's
  conclusion even though the model remains confident.
- **Intent detection** needs two layers of classification: a first layer for broad
  query categories (data-related vs. system-related vs. feedback), and a second layer
  identifying specific visualization needs (graph/table/chart/map) for data-related
  requests.
- Converting technical database schemas (e.g., raw `apoc.meta.schema` output) into
  **LLM-friendly conceptual schemas** requires filtering out irrelevant elements (via a
  skip list) and adding contextual annotations (value encodings, relationship
  semantics) — structuring information the way LLMs process text best.
- **Prompt engineering for LLM reasoning** means giving the model "time to think":
  structure output to generate reasoning (and intended relationships) *before* the
  final answer/query, using chain-of-thought-style ordering to avoid the model
  prematurely committing to and rationalizing a wrong answer.
- Reliable **text-to-Cypher generation** needs comprehensive schema context, current
  user-selection state, intent-specific formatting requirements, and carefully chosen
  few-shot examples — plus an **error-feedback retry loop** (previous query failure
  messages fed back into the prompt) to self-correct invalid queries.
- **Result summarization** works best as a complement to visualization, not a
  duplicate of it — filtering irrelevant returned data and surfacing insights/patterns
  that aren't immediately obvious from the graph alone, gated by whether the user's
  question actually asked for analysis.
