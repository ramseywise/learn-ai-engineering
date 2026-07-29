---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 6: Building knowledge graphs with large language models"
confidence: high
cleaned: 2026-07-29
---

# Ch 6 — Building Knowledge Graphs with Large Language Models

This chapter picks up from Chapter 5's extraction work on the Rockefeller Archive Center
(RAC) project — historical typewritten documents describing conversations between
Rockefeller Foundation (RF) program officers and researchers. Having extracted knowledge
with LLMs, the chapter covers transforming that extracted knowledge into a knowledge
graph (KG), and then using the KG for **intellectual network analysis**.

The end-to-end path (mental model): unstructured data sources → digitization (OCR, table
extraction, image extraction/classification) → custom knowledge extraction (NER, relation
extraction via traditional models or prompt-based/fine-tuned LLMs) → graph modeling,
normalization/cleansing, entity resolution → knowledge graph → graph data science (node
scoring/centralities, community detection, graph pattern analysis, graph ML) → downstream
uses (question answering, pattern/insight discovery, visualization).

## 6.1 Transforming an Archive to a KG

Challenges specific to the RAC project that need to be handled before a usable KG exists:

- **Analog typewritten documents** — must be scanned and processed by optical character
  recognition (OCR) (cloud providers like Amazon/Microsoft, or the open source Tesseract
  library) to produce a digital corpus.
- **Historical documents** — many of the research disciplines discussed are no longer
  pursued, so there's no hope of compiling a comprehensive NER dictionary or knowledge
  base to use as a disambiguation/entity-resolution reference.
- **Uncommon linguistic conventions** — program officers used idiosyncratic abbreviations
  (e.g., "S." for "J. R. Smith," "U.Cal." for "University of California"). Off-the-shelf
  coreference models failed to resolve these into canonical forms, but GPT succeeded at
  implicitly performing NER, entity resolution, and relation extraction (RE) in response
  to prompts.
- **Domain-specific named entities** — the domain is natural sciences; the primary
  custom-named entities are `Occupation`s, covering research disciplines, technologies,
  treatments, and diseases at varying granularity. No traditional NER model exists for
  these (except diseases). A custom ML-based NER plus an unsupervised entity resolution
  system (clustering semantically similar occupations) is a viable path.
- **High relational complexity** — a single page can contain dozens of relevant relations.
  Defining the RE schema properly matters: a bad schema either retrieves useless
  knowledge or misses opportunities for higher accuracy — true whether training an RE
  model on manually labeled data or guiding an LLM with the schema.
- **KG normalization, cleansing, entity resolution, and disambiguation** — significant
  effort is required because documents use different name variants for the same entity,
  multiple participants describe similar research in different words, and conversations
  chain together over months or years. The chapter explicitly scopes this kind of deep
  chain analysis out, focusing instead on producing and analyzing **interaction
  networks**.
- **Matching/linking unstructured data sources** — ideally, officer diaries would be
  reconciled with a second data source (e.g., board of directors minutes) in a single KG,
  enabling questions like "Are there any patterns that typically precede the funding of an
  idea?" This is also out of scope but illustrates the possibilities of combining
  unstructured sources.

> **Author's framing**: "we can call ourselves lucky to live in the LLM era" — many of
> these obstacles, which previously required significant resources to solve with
> traditional ML, can now be solved "with the right choice of a knowledge representation
> system, an LLM model, and prompt engineering."

### 6.1.1 Graph Modeling

The chapter focuses on one aspect of the full RAC KG schema: **influence networks** — the
relations among people interviewed by RF representatives (who talked with whom about whom
else).

The graph is designed in **three layers**:

| Layer | Contents |
|---|---|
| **Document-level layer** | Result of initial data ingestion. Each diary file is a `File` node (properties: file name, location, author). Each `Page` node results from OCR extraction of a file and carries the final clean text of the page. |
| **Metagraph layer** | Unmerged GPT entities (`Entity` nodes) and the relations among them, plus their linkage back to the originating `Page`. |
| **KG layer** | Final, normalized, cleansed, resolved entities (`Person`, `Title`, `Organization`, `Occupation`) and relations among them (`WORKS_ON`, `WORKS_FOR`, etc.). |

Key design point: **an LLM does its best to produce the desired output, but it cannot be
used to produce a KG directly** — normalization and entity resolution steps must happen
first, and the three-layer schema is what enables them.

### 6.1.2 Creating a Metagraph

For texts longer than a few pages, the first step is defining a **chunking strategy** to
avoid the max-token limit or degraded processing quality on very long texts. The simplest
approach shown here: split by page.

> **Note from the text**: The full RAC project had more than 10,000 pages, but the
> chapter's worked example uses a subset of 150 pages of Warren Weaver's diary (the OCRed
> dataset and full ingestion code are in the book's code repository). The documents are
> typewritten and date from 1939, so digitization may have misspelled some entity names.

Process, per page:

1. Create (never merge at this stage) all identified entity mentions as `Entity` nodes
   with a `name` property.
2. Link each entity mention to its originating page via `RELATED_TO_ENTITY`, with a
   `type` property representing the relation class.
3. This page-scoped, unmerged representation is what makes normalization and entity
   resolution possible later, based on knowledge about each individual mention.

Benefits of keeping the metagraph layer around after the final KG is built:

- All extracted knowledge can be aggregated into the final KG while **preserving
  provenance** — the underlying information about which page/text snippet each entity or
  relation came from.
- Enables an **explainable graph visualization platform** that can show the original text
  snippet behind any selected entity or relation on demand.
- Lets data scientists maintaining the KG system track the origin of nodes/relationships
  and, e.g., fine-tune entity resolution as needed — because **the final KG can be
  re-created at any time from the metagraph**.

### 6.1.3 Normalization and Cleansing

Once the metagraph exists, inspect statistics — top entities per class, top relation
classes, etc. — for a quick overview of the knowledge structure. Opportunities to increase
future graph connectivity get implemented as normalization rules, for example:

- **Lowercasing entity names** where case is irrelevant (e.g., `Occupation`s) — important
  for KG consistency and efficient integration across documents.
- **Stripping irrelevant tokens from names** — GPT occasionally included a person's title
  as part of their name even though it was instructed to treat title and name separately.
  Without cleansing, the same person could end up represented by two different nodes (one
  with the title folded in, one without).

```python
# Listing 6.1 — Normalizing people and occupations
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")
NEO4J_DB = "neo4j"

REMOVE_TITLES = ["dr.", "prof.", "dean", "president", "pres.", "sir",
                 "mr.", "mrs."]
QUERY_NORM_PERSONS = """   #1
    MATCH (e:Entity {label: "Person"})
    WITH e, CASE WHEN ANY(title IN $remove_titles WHERE toLower(e.name)
    STARTS WITH title) THEN apoc.text.join(split(e.name, " ")[1..], " ")
    ELSE e.name END AS name
    SET e.name_normalized = name
"""

QUERY_NORM_OCCUPATIONS = """   #2
MATCH (e:Entity {label: "Occupation"})
SET e.name_normalized = toLower(e.name)
"""

if __name__ == "__main__":
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session(database=NEO4J_DB) as session:   #3
            print("Normalizing Person names")
            session.run(QUERY_NORM_PERSONS, remove_titles=REMOVE_TITLES)
            print("Normalizing Occupations")
            session.run(QUERY_NORM_OCCUPATIONS)
```
`#1` Cleans Person names: removes titles/degrees
`#2` Lowercases Occupation entity names
`#3` Executes the queries

A new `name_normalized` node property is created and used in place of the raw `name`
property when linking to final nodes in the KG layer.

### 6.1.4 Graph-Based Entity Resolution

The generative nature of LLMs helps produce cleaner, more accurate KGs. Unlike
traditional NER and RE models, an LLM that is properly guided (via prompt or fine-tuning)
tends to return only full, clean entity names — effectively performing **coreference
resolution** implicitly, a task normally handled as a distinct step in standard NLP
pipelines. This **reduces, but does not remove**, the need for explicit entity
resolution.

**Entity resolution** (or entity disambiguation) remains necessary: is "Eleanor Smith" in
one document the same person as "E. Smith" in another? Linking each subject to a concrete
concept in a knowledge base is a vital part of any KG creation process.

**Approach**: take advantage of the graph structure to build a graph-based entity
resolution system. Most entity mentions in the metagraph layer have one or more relations
to other mentions, and most of these relations are useful signals for resolution:

- If two names have high string similarity ("Eleanor Smith" and "E. Smith") **and** both
  work for the same university (via `WORKS_FOR`), that's a strong signal they're the same
  person.
- Conversely, it's unlikely that people with identical or very similar names are working
  on the same research topic if they're actually different people — shared topic can also
  serve as corroborating (or contradicting) evidence.
- Amassing multiple signals of this type increases confidence in a resolution decision.

**Baseline mechanics**:

- Link two mentions with a `META_SIMILAR` relationship if they have identical or very
  similar string representations.
- Use domain knowledge to set similarity thresholds — e.g., a person's name is composed
  of first name, middle name(s), and surname; middle names are often abbreviated or
  skipped, same for first names. Relying on surname alone produces many false positives;
  requiring a match on surname **and** at least the first name (or its abbreviation)
  gives higher confidence.
- Similar reasoning applies to other entity types, such as `Organization`s.

> **Tip from the text**: Names sometimes include generic words — many foundation
> `Organization` names include the keyword "Foundation" — so it would be
> counterproductive to link all of them as similar. Analyze the situation and define a
> stop-word list before creating `SIMILAR` relationships. Different datasets and domains
> require adjusted approaches.

**Worked example** (Figure 6.3): three mentions of nuclear physicist Ernest Lawrence
(Nobel laureate for inventing the cyclotron) appear on pages 26, 99, and 126: *Ernest
Orlando Lawrence*, *Ernest O. Lawrence*, and *Lawrence*. Evidence these refer to the same
person:

- Strong string similarity per the rules above.
- *Ernest Orlando Lawrence* and *Ernest O. Lawrence* are three hops apart in the graph,
  both identified as employees of the University of California.
- *Lawrence* connects to the others through `WORKS_ON` relationships and similarity
  between the `Occupation`s *cyclotron* and *100,000,000 to 200,000,000 volt cyclotron*.
- Notably, *Ernest Orlando Lawrence* and *Lawrence* are **six hops apart** — a traversal
  this deep would be much harder to discover in a relational database, underscoring a
  practical advantage of the graph representation.

**Extending the signal set**:

- A "graphier" approach: use the intellectual network relations `TALKED_ABOUT` and
  `TALKED_WITH`, and run graph community detection algorithms such as **Louvain** to
  identify clusters of people who interact. Rationale: *John Doe* working on *maritime
  research* in *Antarctica* will probably sit in a different interaction network than a
  different *John Doe* specializing in *cosmology*. Community membership is another
  disambiguating signal.
- Adding ML: design a semantic similarity approach for `Occupation`s, creating
  `META_SIMILAR` links even with **zero string similarity** but high topical relatedness
  (e.g., *fertility* and *human ovulation*). A frequent choice is to embed with GPT and
  cluster the embeddings by similarity — the authors report very good results with
  **agglomerative clustering**.

**Baseline resolution flow, final steps**:

1. Create `META_PERSONS_SIMILAR` relationships among person mentions that satisfy the
   defined criteria (string similarity and relatedness through RE outputs).
2. Run the **weakly connected components (WCC)** algorithm on the `META_PERSONS_SIMILAR`
   metagraph to identify groups of mentions that should resolve to the same KG entity
   (final graph layer).
3. For each WCC group, select a common name to represent it — the chosen convention is
   the **longest name** in the group (in the worked example, *Ernest Orlando Lawrence*).
4. Create the final KG layer with fully resolved entities.

## 6.2 Intellectual Network Analysis: The Value of Graphs

With the KG built, the chapter turns to graph data science as the analytical payoff.
Certain parts of the KG are especially suited to graph analytics — notably the
**intellectual network** of people (scientists) formed by `TALKED_ABOUT`, `TALKED_WITH`,
`WORKS_WITH`, and `STUDENT_OF` relations.

Using Neo4j's Graph Data Science library, the authors run **PageRank**, **eigenvector
centrality**, **node degree**, and **betweenness centrality** to identify:

- **Influencers** — people who stand out in terms of recommending other people's work.
- **Influencees** — popular targets of other people's referrals (or professional gossip).
- **Bridges** — those who act as connectors among different communities of people.

Different visualization styling choices help guide exploration and analysis of these
roles.

**Betweenness centrality view** (Figure 6.4): the largest connected component of the
extracted intellectual network, styled so node size grows with betweenness centrality
(bigger = more shortest paths between other node pairs pass through it). This highlights
people acting as bridges among sub-graphs of researchers who would otherwise be loosely
connected or disconnected. Famous scientists such as **Niels Bohr** (father of atomic
physics) and **Ernest Lawrence** (inventor of the cyclotron) appear as bridges, but less
famous people are highlighted too — a route to potentially surprising insights worth
investigating.

**Focused query — cyclotron influence network** (Listing 6.2): answers "Who played an
important role related to the cyclotron research and its funding?" via a few-hop Cypher
query.

```cypher
-- Listing 6.2 — Showing the influence network related to cyclotron research
MATCH path = ()<-[:WORKS_ON|WORKS_FOR]-(p2:Person)
  -[:TALKED_ABOUT|TALKED_WITH|WORKS_WITH|STUDENT_OF*1..2]->
  (p:Person)-[:WORKS_ON]->()-[:SIMILAR_OCCUPATION*0..1]-(o:Occupation)
WHERE o.name = toLower($occupation) AND
  NOT ANY(x IN nodes(path1) WHERE x.name = "WW")
RETURN path
```

The query allows up to a two-hop distance between the person working on cyclotron
research and some other person, exploring more complex referral patterns. Node sizes in
the resulting visualization (Figure 6.5) are scaled by **PageRank centrality** computed on
the full influence-network graph. Besides Ernest Lawrence and Niels Bohr, other important
people surface nearby: **Harlow Shapley** (astronomer, head of Harvard College
Observatory) and **James B. Conant** (organic chemist, 23rd president of Harvard
University).

> Historical aside from the text: Harvard built a cyclotron which, after secret
> negotiations with General Leslie Groves, President Conant later sold to the U.S.
> government for $1 to help develop the first nuclear bomb.

**A cautionary finding — LLM/RE failure mode**: the visualization also surfaces
**Laurence Irving** (first name misspelled by GPT as *Lawrence* — likely a mixup caused by
Ernest Lawrence appearing on the same page), a pioneer in comparative physiology who has
no real connection to the cyclotron invention. Investigating the underlying data confirms
this is a **failure in the relation extraction (RE) task**: he should not appear in this
subgraph.

> **Key caution from the text**: "This is an important reminder that LLMs are not magic;
> they do make mistakes, and sometimes silly ones. It is important to design a feedback
> loop in your KG applications so that analysts can validate or invalidate the content of
> the graph."

**Second focused example — connecting institutions across a personnel transition**:
scenario — project officer Warren Weaver leaves their post, and a new hire must handle a
physics research project spanning Johns Hopkins University and Harvard University. Who
should they approach first? Ideally someone with exposure to the physics domain at both
institutions. This is answered by taking all employees of both universities (via
`WORKS_FOR`) and searching for connections among them (`TALKED_ABOUT`, `TALKED_WITH`,
`WORKS_WITH`, `STUDENT_OF`) up to three hops, where at least one person works on physics
research (Figure 6.6).

Only a handful of people stand out as useful connectors at first glance. A good candidate
is **Irving Langmuir** (chemist, physicist, engineer, 1932 Nobel Prize in Chemistry), who
talked positively about **Dorothy M. Wrinch** (studied insulin and protein structures
using X-rays) and has a direct one-hop link to both universities. Note that two separate
nodes represent this one scientist — *Irving Langmuir* and *Langmuir* — because his
surname alone was mentioned on a page lacking additional relations usable for entity
resolution, so the two mentions were never merged.

By examining the properties of `TALKED_ABOUT` relationships that carry **sentiment**, the
authors discover Bernal has a negative attitude toward Dorothy Wrinch, and Irving Langmuir
has a negative attitude toward Bernal — suggesting that to get balanced insight, both
should be interviewed.

## 6.3 Next Steps in the Rockefeller Archive Center Project

The results shown are based on only 150 pages out of a much larger source, but they
demonstrate the KG's complexity. A full production-quality project would need to also:

- **Improve knowledge extraction** — more iterations of prompt engineering or fine-tuning
  the LLM to improve KG accuracy.
- **Handle multipage documents** — each diary has hundreds of pages, but there's a token
  limit on how much data can be sent to/retrieved from the LLM at once. In the RAC
  project, ChatGPT-3.5-Turbo was used to identify the boundaries of individual diary
  entries (typically fewer than three pages) so entries could be processed as coherent
  units simultaneously.
- **Perform entity resolution** more thoroughly — improve on the chapter's baseline,
  expand it to other entity types, and complement it with entity disambiguation against
  an external knowledge base such as **WikiData**.
- **Add grants** — mine details about grants awarded by the RF from board of directors
  minutes and link grants to conversations in the diaries, enabling questions like "Do
  granted projects tend to run through recommendations of influential scientists or
  previous grantees?"
- **Perform entity resolution of `Occupation`s** — these named entities vary widely in
  granularity (e.g., *nuclear physics*, *isotopes*, and *heavy nitrogen* are related —
  heavy nitrogen is an isotope, and isotopes are part of nuclear physics). Answering
  complex questions requires linking (resolving) these to gain access to the entire
  history of a given topic. Best results came from creating `Occupation` embeddings
  (using **SentenceBERT** or GPT) and clustering them with **agglomerative hierarchical
  clustering**.
- **Create conversations** — build `Conversation` nodes using high-quality RE plus other
  information: a `Conversation` needs a date, an interviewer, interviewee(s), and a topic
  (the `Occupation`s of the interviewees). Once `Conversation` nodes exist, their
  follow-up chains can be identified and linked to grants. Both tasks depend on the
  unsupervised resolution of occupations already described.

## 6.4 The Value of Knowledge Graphs in the LLM Era

Framing question: in the era of super-powerful LLMs, why build KGs at all instead of
feeding data to an LLM and asking questions directly? The chapter offers a short answer
(the whole book is the long answer):

- **Explainability** — KG-based applications are natively explainable. They let users
  inspect and verify underlying data and reasoning, handle conflicting sources of
  information, and expose the entire chain of "thought" when required.
- **Demystification (de-black-boxing)** — advanced ML models are often treated as black
  boxes users are expected to blindly trust. Simply fine-tuning an LLM on a dataset and
  querying it gives no way to assess confidence in responses, and no assurance the model
  hasn't missed crucial information. Using an LLM's language understanding to extract
  specific factual information and produce a KG instead provides confidence in the
  generated insights.
- **Democratization** — LLMs are massive and expensive to train/fine-tune. KGs are a way
  to democratize their use: the expensive model is invoked once to produce the KG, and
  the KG is then reused for a long time (with occasional inexpensive batch updates) for
  downstream tasks and analyses.
- **Explorability** — graphs let users view and interactively "touch" their relational
  data from new angles. KG visualization and explorability inspire people to hypothesize
  and then verify or disprove their theories via drill-down investigation.
- **Advanced analytics** — perhaps most importantly, KGs empower data scientists and
  analysts to perform downstream graph-based analyses and graph ML, giving them full
  control over how answers to user questions are generated (rather than deferring that
  control entirely to an opaque model).

## Takeaways

- A KG cannot be produced directly from an LLM — go through a **three-layer pipeline**
  (document layer → metagraph of unmerged entity mentions → resolved/normalized KG layer)
  so normalization and entity resolution can happen with full provenance back to source
  text.
- LLMs implicitly perform coreference resolution during extraction (returning cleaner
  full names than traditional NER/RE), which **reduces but does not eliminate** the need
  for explicit entity resolution.
- **Graph-based entity resolution** combines string similarity with relational signals
  (shared employer, shared topic, shared community via Louvain) and semantic similarity
  (embeddings + agglomerative clustering) — then resolves clusters via weakly connected
  components (WCC), naming each cluster after its longest member.
- Graph structure surfaces relationships (e.g., six-hop links) that would be impractical
  to discover in a relational database.
- Centrality algorithms (PageRank, eigenvector, degree, betweenness) on an intellectual
  network reveal **influencers**, **influencees**, and **bridges** between communities —
  directly useful for questions like "who should I talk to first."
- LLM-driven extraction is not magic — verify surprising graph findings; entity mixups
  (e.g., Laurence Irving vs. Lawrence) are a real RE failure mode, so a **human feedback
  loop** to validate/invalidate KG content is essential.
- KGs justify their existence even in the LLM era through explainability,
  demystification, democratization (expensive model run once, KG reused cheaply),
  explorability, and enabling advanced downstream graph analytics under analyst control.
