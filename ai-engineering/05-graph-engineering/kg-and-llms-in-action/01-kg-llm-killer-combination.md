---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 1: Knowledge graphs and LLMs: A killer combination"
confidence: high
cleaned: 2026-07-29
---

# Ch 1 — Knowledge graphs and LLMs: A killer combination

## Framing: why KGs and LLMs need each other

**Generative artificial intelligence** (GenAI), powered by **large language models**
(LLMs) like Google's Gemini and OpenAI's GPT, has transformed how we work, but it falls
short in domains where specific domain knowledge, high accuracy, and explainability are
essential. LLMs suffer from hallucinations and a lack of context and relations. This is
where **knowledge graphs** (KGs) come in, providing contextual information — experiences,
environmental characteristics, cultural aspects, and social norms — needed to build the
"third wave of AI" for mission-critical applications.

KGs are sophisticated graph structures that represent real-world entities (people,
places, diseases, proteins), define meaningful connections between them, and provide
context. KGs provide structured, explainable knowledge representation but are
challenging to build and query; LLMs offer natural language processing capabilities but
suffer from hallucinations, stale information, and a lack of domain-specific grounding.

> "Together, they are a 'killer combination': LLMs can extract entities and
> relationships from unstructured text to build KGs more efficiently, providing more
> autonomous and powerful graph querying and analysis. Meanwhile, KGs provide reliable,
> up-to-date domain knowledge to ground LLM responses and prevent hallucinations."

Blending KGs and LLMs is a powerful approach to building sophisticated data-driven
applications that can harmonize disparate data sources, provide natural language
interfaces, and deliver contextually grounded intelligent responses. The book's roadmap:
adopt business-focused approaches, model KG schemas, use LLMs for entity extraction,
validate information integrity, and create conversational AI systems that answer
complex domain-specific questions using structured and unstructured data.

## 1.1 Knowledge graphs

KGs incorporate a structured representation of human knowledge into machines, enabling
more intelligent behavior. This is achieved by creating a sophisticated graph structure
with three elements:

- **Nodes** represent real-world entities (people, places, organizations, diseases,
  proteins, genes).
- **Relationships** define meaningful connections between these nodes (a person born in
  a place, a disease causing symptoms, a gene encoding a protein).
- **Properties** provide context (birth dates, geographic coordinates, organizational
  history, disease descriptions in multiple languages).

The book's running example (Figure 1.1) is a healthcare KG in which diseases, drugs, and
anatomical structures are connected through meaningful relationships — e.g., `DIABETES`
`HAS SUBCLASS` `TYPE 1 DIABETES` / `TYPE 2 DIABETES`; `TYPE 1 DIABETES` `USED FOR TREAT`
`INSULIN`; `DIABETES` `CAUSES` `RETINOPATHY`; `TYPE 2 DIABETES` `USED FOR TREAT`
`THIAZOLIDINEDIONES`; `FOOT ULCERS` `LOCATION` `FOOT`; `INSULIN` `INJECTION AREA` `ARM`
`IS A` `ANATOMICAL STRUCTURE`. This explicit representation enables machines to perform
reasoning and inference on structured knowledge, supporting complex intelligent systems
for decision-making.

### Why KGs haven't been widely adopted

Despite their effectiveness, KGs haven't seen wide adoption for several reasons:

- They are expensive to build and maintain in terms of time, effort, and money.
- Intricate access patterns are required to navigate multiple hops.
- Their results scatter information across multiple nodes and relationships.

Building a KG requires recognizing and extracting relevant entities and connections from
heterogeneous data sources, both structured and unstructured.

**Structured/semistructured data** (relational databases, CSV/XML/JSON files) is far
less complicated to work with: items are isolated, identified, and often typed. This
data must still be mapped from its original schema to a common graph schema, but the
process is controllable and predictable.

**Unstructured data** is a different story — extracting information from text has
always been complex, for these reasons:

- **Multiple languages** — each language has its own grammatical rules, vocabulary,
  idioms, and nuances; some use unique writing systems (Latin, Cyrillic, Chinese)
  requiring support for various scripts and encodings.
- **Typos** — human-written text often contains typographical errors and mistakes
  requiring sophisticated algorithms to understand intended meaning.
- **Pronouns** — resolving what a pronoun refers to (**coreference resolution**) is
  vital for accurate comprehension. Example given: in "John saw Bob and he waved," it's
  unclear whether "he" refers to John or Bob.
- **Different writing styles** — authors use synonyms, varied sentence structures, and
  unique expressions, making it hard for systems to maintain consistency across texts.
- **Domain-specific terminology and concepts** — many specialized fields use unique
  vocabularies and technical jargon requiring domain expertise to extract accurately.

Beyond extraction, a KG holds vast interconnected information (**knowledge**) that must
be accessed correctly to answer questions. Flexibility in defining the schema helps
handle heterogeneous sources and complex domain connections but complicates access for
those who don't know how to query properly. Predefined queries/analyses help build
specific intelligent systems but limit the users and support those systems can provide,
and results are often hard for non-experts to interpret across UIs.

**Real-world examples of KG use so far:**
- Google was the best-known early adopter, using KGs to enhance search by surfacing
  "relevant" connected information — searching for *things*, not just strings — but this
  is limited to search applications.
- Analysts use KGs to answer complex investigative questions, but the complexity of graph
  querying and the need for specific interfaces confines this to a smaller user base.

The book's target scenario: individuals posing questions to a KG in natural language,
with an intelligent system finding correct answers by querying the graph effectively and
transforming results into simple summaries.

## 1.2 Large language models

LLMs specialize in handling natural language and can eliminate barriers to the evolution
of intelligent systems that use KGs as their core technology, helping users accomplish
tasks in complex domains.

### Transfer learning and the model lineage

The foundation of LLMs is **transfer learning**: the ability to reuse patterns learned in
generic tasks (e.g., predicting masked tokens) for specific tasks (e.g., relation
extraction). This breakthrough shifted the paradigm from training many small,
task-specific models to training a few large models reusable across multiple tasks,
significantly reducing the training data and compute required for supervised learning.

In transfer learning (Figure 1.2): during training, the first layers of a neural network
find general features independent of task and dataset; features computed by the last
layer depend on the dataset and task. Knowledge transfer copies the model from one task
to another; the model is then adapted for the new task either by fine-tuning it from the
previous task or by using the previous model as a feature extractor whose output feeds a
new model/head.

**Pretrained language models** (PLMs), trained with transformer architectures on
large-scale corpora, demonstrated the capacity to perform NLP tasks with a single big
model. Enhancements in model scaling increased model capacities, and further
investigation of scaling effects expanded the parameter scale. The term **large language
model** refers to a PLM with significant scale — typically tens or hundreds of billions
of parameters. LLMs such as GPT-2, trained on enormous volumes of textual data,
transformed the field of AI; their modern counterparts including GPT-4, Gopher, and PaLM
breathed new life into the phrase "unreasonable effectiveness of data."

### Why LLM performance is "unreasonable" — three interconnected reasons

1. Model complexity (a.k.a. number of parameters)
2. Size — and, in the case of GPT, quality — of the training corpus
3. Their ability to reduce tasks requiring human intelligence to next-token prediction

As shown in the paper "Scaling Laws for Neural Language Models," larger neural models
(more trainable parameters) require fewer data samples to reach the same test-set-loss
performance. The same paper proves the size of the training corpus is of paramount
importance — more data yields better performance — but **data quality is equally
crucial**.

- Traditional machine learning typically followed a **model-centric** paradigm: focus on
  identifying the best model architecture and fine-tuning hyperparameters. But faulty
  data can lead to faulty predictions.
- A **data-centric** paradigm prioritizes data engineering to improve both the quality
  and quantity of data used to train high-complexity ML models. With these
  improvements, tasks can be formulated in natural language, and LLMs generate accurate
  answers with minimal model engineering required.

### LLM building blocks (Figure 1.3)

Six characteristics form the core of LLMs:

- **Tokenization** — breaks text into units called tokens, simplifying text
  representation and making it easier for models to understand and process language.
  This improves operational efficiency, preserves meaning, and enhances LLM performance.
- **Generation capacity** — the ability to generate text is a defining feature of LLMs
  that places them in the generative AI category. Training on vast, diverse datasets
  enables LLMs to mimic human-like language.
- **High-dimensional embedding** — high-dimensional embeddings provide continuous vector
  representations of tokens that capture their semantic meanings and encode
  relationships and patterns among them.
- **Transformers and attention** — LLMs use a transformer architecture with parallel
  processing, enabling efficient training on large datasets and impressive performance.
  Transformers assign weights to words in a sentence so the model can focus on the
  relevant parts of the input.
- **Large dataset for pretraining** — LLMs are characterized by their vast size and
  pretraining on massive datasets. During pretraining, these models learn general
  linguistic patterns, world knowledge, and contextual understandings, becoming
  repositories of language expertise.
- **Transfer learning** — LLMs can be used for different tasks just by changing
  instructions (the prompt) or fine-tuning them; a single model can thus serve
  multiple purposes.

## 1.3 KGs and LLMs: Stronger together

KGs and LLMs support each other in delivering better service, and together enhance the
implementation of powerful, intelligent systems. Three ways LLMs assist KG-based
solutions:

- **Building KGs** — extracting relevant concepts and connections from unstructured
  data. This task has traditionally required training custom NLP models for specific
  domains. LLMs simplify this by providing a single model that can serve multiple
  purposes with minimal configuration (such as the prompt). Covered in parts 2 and 3 of
  the book.
- **Querying KGs** — extracting knowledge can involve multiple steps, or **hops**, from
  the starting concept to the destination. Such hops often require understanding the
  schema and query language. LLMs help by extracting relevant, precise information to
  support querying and search. Covered in part 5.
- **Summarizing** — information extracted from KGs can be returned in text form rather
  than as a table, graph, chart, or other format.

Figure 1.4 depicts the full pipeline: unstructured sources (documents, emails/chats,
domain expert input) and structured sources (databases) feed into KG construction.
LLMs process unstructured text and recognize relevant entities and relationships,
mapping them to the schema; structured data's entities/relationships must likewise be
mapped to the target schema. Users ask questions in natural language; the question is
converted into a query executed on the KG (or used to retrieve information via vector
similarity); results returned from the KG are further processed by LLMs to generate a
more appropriate answer (in structure and content) for the user.

### Drawbacks of LLMs mitigated by integrating KGs

- **Hallucinations** — KGs provide structured, verified knowledge that acts as a factual
  foundation, significantly reducing LLMs' tendency to generate plausible but incorrect
  information. LLMs complement this by offering sophisticated query mechanisms, such as
  **text-to-cypher translation**, converting natural language questions into precise
  graph queries that extract reliable information directly from the structured
  knowledge base.
- **Stale information** — KGs enable dynamic knowledge updates through advanced
  retrieval-augmented architectures. LLMs cannot be constantly retrained, but KGs can be
  continuously updated and accessed via techniques such as KG-based prompting and
  **GraphRAG**. GraphRAG organizes knowledge into meaningful clusters and community
  summaries, providing LLMs with the most current information available in constantly
  updated KGs.
- **Explainability** — KGs provide transparent information paths and structured
  reasoning that users can trace and validate, building trust through explainable AI
  processes. Combined with LLMs' natural language processing, this creates systems
  where knowledge extraction is understandable and repeatable, and findings can be
  summarized in an intelligible, human-readable format.

Figure 1.5 (yin-yang summary):

| | LLMs | KGs |
|---|---|---|
| Pros | General knowledge, language processing, generalizability | Accuracy, interpretability, domain-specific knowledge, evolving knowledge |
| Cons | Hallucinations, black box, lack domain-specific/new knowledge | Incompleteness, lack language understanding, complex querying |

## 1.4 The paradigm shift in data-driven applications

Traditional paradigms build systems for specific purposes with structured, homogeneous
databases — workable for tailored needs but impractical for complex domains that must
adapt to user characteristics and integrate heterogeneous data. KGs capture connections,
enabling relationship discovery through graph pattern matching and traversal. Both the
**Resource Description Framework (RDF)** and **Labeled Property Graphs (LPGs)** provide
machine-readable formats interpretable by humans. KGs emphasize rich, meaningful data
representations usable by both humans and machines, enabling a paradigm shift where
intelligent behavior is encoded in a unique source of truth.

> According to McKinsey & Company, addressing data fragmentation can cut annual data
> spending by 5% to 15% in the short term. KGs overcome siloed data issues, creating
> knowledge sources while lowering barriers to data access and enhancing governance.

### 1.4.1 The four pillars of knowledge graphs

The book proposes a definition of KG that captures both technical and business sides:

> **DEFINITION** — A **knowledge graph** is an ever-evolving graph data structure
> composed of a set of typed entities, their attributes, and meaningful named
> relationships. Built for a specific domain, it integrates both structured and
> unstructured data to craft knowledge for humans and machines.

This definition grounds the **four pillars of KGs** (Figure 1.6):

- **Evolution** — KGs allow continuous ingestion, integration, and unification of
  information into a single source. The graph structure can be easily extended
  according to the needs of the analysis and purposes. A KG can seamlessly incorporate
  new interactions or content without needing a complete overhaul of the existing
  structure. (Constantly updated information; nodes, edges, and properties; dynamic
  graph algorithms.)
- **Semantics** — a KG makes the meaning of the data explicit, modeling information in a
  knowledge infrastructure characterized by typed entities and meaningful relationships.
  New data is combined with existing data and immediately available for analysis.
  Contextual knowledge emerges from this infrastructure and drives business activities
  and decisions. Such knowledge connects typed entities describing categorizations and
  supports, for instance, identity, transitive, or inverse relationships. This
  expressiveness in representing data opens the doors to **explainability**. KGs provide
  a backbone for reasoning mechanisms ranging from consistency checking to causal
  inference. (Meaningful data; entities and relationships; knowledge infrastructure.)
- **Integration** — the KG serves as the central reference for all structured and
  unstructured data related to a domain. Because a KG represents information by
  focusing on the meaning of data, users can overcome challenges related to data types,
  formats, and provenance, connecting information from multiple sources. (Flexibility;
  structured/unstructured sources; contextual knowledge.)
- **Learning** — a KG represents the core information and big picture of a domain.
  Humans can analyze, visualize, and query graph data to extract insights. Inference
  rules and machine learning algorithms are performed on top of the KG to infer new
  information not explicitly encoded within it. Analysts can use methods such as
  centrality and connectivity analysis to identify influential nodes, network analysis
  to detect the shortest path between nodes, and community analysis to recognize groups
  of similar nodes. (Query, visualization, and inference; humans and machines;
  representation learning.)

## 1.5 Building data-driven applications using KGs and LLMs

> **NOTE** — The book frequently uses healthcare examples because its characteristics,
> issues, and requirements easily generalize to other domains, and healthcare offers
> abundant publicly available data comparable to real-world use cases.

### 1.5.1 Example use case: Drug discovery and development

Drug development integrates knowledge from numerous domains (biology to chemistry), and
bringing a new drug to market is costly with a high chance of failure. Fast, practical
approaches are essential to guide research.

- **Challenge** — integration of medical and pharmaceutical data must ensure data
  integrity, accuracy, and consistency while correctly contextualizing data points.
- **KG-based solution** — models interactions between biological entities at different
  scales, connecting genes, diseases, and drugs using relationship types. Typed
  relationships with multiple rules better represent domain meaning, enabling
  transitive bonds and inference.
- **Role of LLMs** — process unstructured data from scientific publications, clinical
  reports, and databases, ensuring consistency in integrated knowledge bases. LLMs
  expand KGs by analyzing literature and inferring potential relationships, as well as
  performing sophisticated text mining for chemical structures and experimental
  results.

Integrating LLMs enhances data integration, augments KGs, facilitates hypothesis
generation, improves information retrieval, and enables advanced text mining — capabilities
that ultimately accelerate the development of new therapeutics.

### 1.5.2 Example use case: Conversational AI for customer support

Personalized assistant systems must answer user queries and ask follow-up questions,
combining general expertise with specific user requests while managing vast amounts of
information efficiently.

- **Challenge** — despite advances in natural language generation (NLG), answers from
  language models can be repetitive and uninformative (Zhang et al.). For a
  conversational system to provide useful suggestions, it needs to extract relevant
  entities and relationships from the text while being supported by external and
  internal structured knowledge to ground the conversation.
- **KG-based solution** — Zhang et al. claim that "conversations often develop around
  knowledge" — natural conversations evolve around concepts that form this knowledge.
  KGs connect such concepts and establish meaningful relationships between them, and
  can ground conversations, integrate information, and support response generation: NLP
  technologies extract entities and relationships, and the graph-based background
  context of the dialogue drives the conversational flow.
- **Role of LLMs** — LLMs can handle a wide range of topics and provide coherent
  responses, making them valuable for building sophisticated conversational systems.
  However, without additional contextual grounding, their responses can become generic
  and lack depth.

By integrating LLMs with knowledge sources such as KGs, the conversational system can
enhance its responses: LLMs use structured information in KGs to provide more accurate
and contextually relevant answers, navigate complex queries, offer precise information,
and maintain a natural conversational flow.

### 1.5.3 Deciding whether to use a KG

Despite their diversity, the previous scenarios share common challenges. The following
questions help determine whether a KG is the right solution.

**Consider KGs if you answer *yes* to these questions:**

- Do I need to harmonize disparate data silos into consistent overviews?
- Do I need to connect data meaningfully across structured and unstructured sources?
- Do I need flexible data representations where structure evolves?
- Do I need to track pipeline provenance and consistency?
- Do I need to equip advanced search and recommendation services?
- Do I need to visualize network structures, showing communities and
  interdependencies?
- Do I need to apply ML models that benefit from the relational nature of data?

**Consider LLMs if you answer *yes* to these questions:**

- Do I need to extract entities and relationships from unstructured data?
- Do I need to interpret complex user queries for accurate answers?
- Do I need to provide conversational interfaces?
- Do I need to summarize comprehensive results into text?

If you answer *yes* to even one of the LLM questions, you need LLMs to empower your
KG-based solution.

## 1.6 Knowledge graph technologies

The book adopts a technologically agnostic approach, providing code examples that
interchange two common paradigms for creating and querying KGs:

- **RDF and the SPARQL query language**, both defined by the World Wide Web Consortium
  (W3C). RDF is a data model that focuses on knowledge representation, where the graph
  is encoded as a collection of statements or triplets. It aims to standardize data
  publication and sharing on the web. The core of intelligent systems built on RDF is
  based on reasoning performed on the semantic layer.
- **The LPG approach** and query languages such as **openCypher**
  (https://opencypher.org/) and **Gremlin** (https://tinkerpop.apache.org/gremlin.html).
  The LPG representation focuses on the structure (properties and relationships) of the
  graph. Nodes and edges have properties, emphasizing the features of the graph data.

**Comparison:**

- RDF excels at data interoperability and consistency across systems through
  standardized statements, offering powerful hypergraph and federation features that
  enable linking different RDF graphs with rich contextual information.
- LPG implementations provide advantages in pathfinding queries and graph traversal
  operations.
- In LPG, each edge has a unique identity and properties; in RDF, relationships are
  global predicates that can be reused across statements throughout the knowledge base.
- RDF and LPG are distinct paradigms but can be complementary depending on use case: RDF
  excels in scenarios requiring semantic consistency, web-scale interoperability, and
  the use of ontologies for knowledge inference; LPG provides rich property-based
  representations and efficient graph traversals.

### 1.6.1 Taxonomies and ontologies

Modern KG implementations must use traditional graph data features and, per [15], the
organizing principle enabled by semantics turns the latent knowledge of a graph into a
KG. Graph models can be instantiated from a collection of statements (RDF) or through
the LPG model — but just incorporating structural information does not fully capture the
relationships within the data. Semantic features can be injected into KGs using
taxonomies and ontologies:

- **Taxonomies** represent the hierarchical dimension of the data, organizing categories
  in broader-narrower relationships. Example: in a taxonomy, a "Vehicle" category might
  be broader than a "Car" category, which in turn is broader than a "Sedan" category.
  Complex KGs can integrate multiple taxonomies.
- **Ontologies** introduce more complex relationships beyond simple hierarchies — they
  clarify identity, difference, and more intricate interconnections between entities.
  Example: an ontology might specify that "Car" and "Automobile" are identical
  (synonyms), whereas "Car" and "Bicycle" are disjoint (cannot be the same). Ontologies
  support class definitions including union, complement, disjointness, and cardinality
  restrictions. They capture the domain's conceptual structure. Without an ontology, a
  vocabulary remains vague because it does not encode the intrinsic relationships
  between concepts.

Traditional approaches to defining taxonomies and ontologies are rigid and complex,
making systems less adaptable to evolving knowledge and diverse data sources. Modern
KGs adopt a pragmatic approach characterized by **"just enough semantics"** — selecting
a subset of ontology features that address current issues without being overly
prescriptive. Example: in a healthcare KG, practitioners might focus on a specific
medical domain (oncology or cardiology) while leaving room to expand into other
specialties as needed.

Rather than enforcing rigid, complete taxonomies, modern KGs integrate partial
ontologies that can be extended organically. This flexibility enables dynamic, scalable
knowledge representation that adapts to real-world constraints and evolving business
needs.

## 1.7 How do we teach KGs and LLMs?

The book equips readers with essential tools for creating and using KGs while
demonstrating how to use LLMs for advanced intelligent applications. Skills covered:

- Adopt a business-need mindset focusing on goals, then data, and then algorithms.
- Model KG schemas, considering future extensions, taxonomies, and ontologies.
- Import data from structured sources and map entities/relationships to schemas.
- Use LLMs to extract domain-relevant entities and relationships from text.
- Validate ingested information, ensuring integrity and accuracy.
- Perform analysis using the latest ML technologies, such as graph neural networks.
- Query and visualize graph portions, using LLMs for natural language questions.

These concepts are explained through concrete, practical examples drawn from the
authors' direct experience.

## Takeaways

- KGs and LLMs have complementary failure modes: KGs are accurate, interpretable, and
  hold evolving domain knowledge but are incomplete and hard to query; LLMs generalize
  and process language well but hallucinate, are black boxes, and lack domain-specific
  or fresh knowledge. Combining them is explicitly framed as a "killer combination."
- LLMs assist KGs in three concrete ways: **building** (entity/relationship extraction
  from unstructured text), **querying** (multi-hop traversal via text-to-cypher and
  similar techniques), and **summarizing** (turning graph results into readable text).
  KGs in turn ground LLMs, reducing hallucinations and staleness (via GraphRAG /
  KG-based prompting) and enabling explainability.
- A KG is formally defined as "an ever-evolving graph data structure composed of a set
  of typed entities, their attributes, and meaningful named relationships," built for a
  specific domain, integrating structured and unstructured data for both humans and
  machines — and rests on four pillars: evolution, semantics, integration, learning.
  Data-centric quality/quantity engineering matters at least as much as model
  architecture (scaling laws).
- Two competing but complementary technology paradigms implement KGs: RDF/SPARQL
  (W3C standard, statement/triplet-based, strong for interoperability and semantic
  reasoning) versus LPG (openCypher/Gremlin, property-based, strong for traversal and
  pathfinding); the book teaches both.
- Taxonomies (broader/narrower hierarchies) and ontologies (identity, disjointness,
  cardinality, richer relations) inject semantics into raw graph structure; modern
  practice favors "just enough semantics" — partial, extensible ontologies over rigid,
  complete ones.
- Decision framework: reach for a KG when you need to harmonize silos, connect
  structured+unstructured data, support evolving schemas, track provenance, power
  search/recommendation, visualize network structure, or use relational ML; reach for
  LLMs (layered on top) as soon as you need entity/relationship extraction, complex
  query interpretation, conversational interfaces, or text summarization of results.
