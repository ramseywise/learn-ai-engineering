---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 8: NED with open LLMs and domain ontologies"
confidence: high
cleaned: 2026-07-29
---

# Ch 8 — NED with Open LLMs and Domain Ontologies

## 8.1 Limitations of traditional NED systems

Chapter 7 covered **scispaCy**, a specialized NLP tool built on spaCy that performs named
entity disambiguation (NED) using biomedical vocabularies/ontologies such as **UMLS**
(Unified Medical Language System). scispaCy has four limitations:

- Designed for one application domain (biomedical) — not portable.
- Hard to expand/update the reference knowledge base with new entities and terms.
- Doesn't fully use the extensive information already present in the knowledge base.
- Doesn't use existing relationships and paths between entities for disambiguation.

### Illustrating the last limitation: context-dependent disambiguation

Using the ECDC quote from chapter 7 (mentioning Zika virus, congenital Zika syndrome, Zika
virus infection, with supporting context words like "congenital" and "syndrome" nearby),
scispaCy correctly disambiguates all three mentions of "Zika" (Listing 8.1):

```
Recognized entity: Zika virus 75 85
Ranked target candidates:
- C0318793 Zika Virus  #1
- C0276289 Zika Virus Infection
- C4687930 Zika Virus Antibody Measurement

Recognized entity: congenital Zika syndrome 135 159
Ranked target candidates:
- C4546023 Congenital Zika Syndrome  #2

Recognized entity: Zika virus infection 268 288
Ranked target candidates:
- C0276289 Zika Virus Infection  #3
- C0318793 Zika Virus
- C4687930 Zika Virus Antibody Measurement
```

But with a different passage lacking supporting words like "congenital" and "syndrome"
(mentioning Zika, chikungunya, viral myalgia, edema, conjunctivitis, microcephaly),
scispaCy fails (Listing 8.2):

```
Recognized entity: Zika 0 4
Ranked target candidates:
- C0276289 Zika Virus Infection
- C0318793 Zika Virus
- C4687930 Zika Virus Antibody Measurement

Recognized entity: Zika disease 109 121
Ranked target candidates:
(none)

Recognized entity: Zika 278 282
Ranked target candidates:
- C0276289 Zika Virus Infection
- C0318793 Zika Virus
- C4687930 Zika Virus Antibody Measurement
```

The model disambiguates "Zika" to **C0276289 Zika Virus Infection** in the first and third
sentences but finds **no target entity** for the "Zika disease" mention in the second
sentence — it can't use co-occurring context or ontology relationships to fill the gap.

The chapter's proposed fix: combine **open LLMs** with **domain ontologies**. Unlike
domain-specific tools such as scispaCy, this approach generalizes to any application
domain with a rich ontology.

## 8.2 Ingesting the domain ontology

The chapter reuses **SNOMED** (Systematized Nomenclature of Medicine), introduced in
chapter 7 — a multilingual clinical terminology repository with 450,000+ concepts and a
rich set of relationship types. Source files (same as section 7.5.2):

- `sct2_Description_Full-en_US1000124_20220901.txt` — entity names, aliases, relationships.
- `sct2_Relationship_Full_US1000124_20220901.txt` — numerical codes for entities and
  relationships.

**Figure 8.1** shows SNOMED's hierarchical structure: a `SNOMED root` node connects to
**first-level nodes** representing archetypal entities (e.g., *Body structure*,
*Pharmaceutical product*, *Substance*, *Disease*). Deeper nodes (e.g., *Enzyme inhibitor*
→ *Ecallantide*, or *AIDS-associated disorder* → *Retinopathy assoc. with AIDS*) inherit
their **type** from whichever first-level node they trace back to via hierarchical
relationships — deep nodes' types derive from the first-level nodes.

Three ingestion listings build this graph in Neo4j:

**Listing 8.3 — loading relationships** (`SnomedRelationshipsImporter`): sets constraints
(unique `SnomedEntity.id`) and indexes (`name`, relationship `id`, `type`, `umls`), then
runs a batch `MERGE` query that creates `SnomedEntity` nodes and generic
`SNOMED_RELATION` edges typed by `item.typeId`. A special case: when `typeId` equals
`'116680003'` (the SNOMED "is a" relationship code), an additional `SNOMED_IS_A`
relationship is also created via `FOREACH`/`CASE WHEN` conditional logic
(`MERGE (e1)-[:SNOMED_IS_A]->(e2)`).

**Listing 8.4 — loading names and aliases** (`SnomedNamesImporter`): two queries populate
`type`/`aliases` on relationships and `name`/`aliases` on entities, using `CASE`/`coalesce`
to append new aliases without duplicating existing ones.

**Listing 8.5 — label propagation from first-level nodes** (`SnomedLabelPropagator`): a
Cypher query starting at the root node (`id = "138875005"`) walks all `SNOMED_IS_A`
descendants via `apoc.path.expandConfig` (unbounded `maxLevel: -1`, `relationshipFilter:
'<SNOMED_IS_A'`) and propagates each **first-level node's name as a label/type** down to
every node reachable beneath it (skipping ones that already carry that type). This is how
deep nodes get categorized (e.g., a "Pharmaceutical product" or "Disease" type) purely
from their position in the hierarchy. The `SNOMED_IS_A` relationship is what propagates
semantic types through the tree.

## 8.3 Setting up the model with Ollama and Llama 3.1 8B

Previous chapters used OpenAI APIs. This chapter deploys the NED system **locally** with
**Ollama** + **Llama 3.1 8B** (Meta, open source).

- **Ollama** — open source tool to run LLMs directly on a local machine, giving full data
  control and reducing latency/dependency on external providers.
- **Llama 3.1 8B** — 8-billion-parameter open LLM, supports up to **128,000 tokens**
  context length, optimized for multilingual processing, designed for efficient
  deployment on consumer-grade hardware.

Installation: download Ollama from `https://ollama.com/` (macOS, Linux, Windows;
CLI or GUI).

```
ollama serve
ollama pull llama3.1:latest
```

Ollama is compatible with the **OpenAI Chat Completions API**, so the existing Python
integration pattern from earlier chapters carries over unchanged (Listing 8.7): an
`LLM_Model` class wraps the `openai.OpenAI` client pointed at `base_url='http://localhost:
11434/v1'` (`api_key` is required by the SDK but unused by open models) and calls
`client.chat.completions.create(model="llama3.1:latest", messages=messages, temperature=0,
max_tokens=4000, ...)`, returning `response.choices[0].message.content` exactly as the
ChatGPT API format assumes.

**Note**: results in this chapter were generated in October 2024 using the latest Llama
3.1 model at the time.

## 8.4 End-to-end NED process

**Figure 8.2** gives the mental model: input document (unstructured text) → **LLM-based
NER** → annotated mentions → **NED candidate selection (CS)** → multiple candidates per
mention → **NED candidate disambiguation (CD)** → disambiguated entities per mention. The
domain ontology (SNOMED) is fully integrated into every stage, not bolted on afterward.

Three stages:

1. **Named entity recognition (NER)** — LLM identifies and labels biomedical entities
   using categories drawn directly from the ontology (e.g., "Zika" recognized as a
   *Disease* concept per SNOMED).
2. **Candidate selection (CS)** — a full-text search against the ontology retrieves
   possible matches for each mention (e.g., "Zika" → *Zika Virus*, *Zika Virus Infection*,
   *Congenital Zika Virus Infection*).
3. **Candidate disambiguation (CD)** — LLM picks the most precise match per mention using
   a multistep approach: shortest-path detection between candidates, path-to-text
   translation, and textual path summarization.

This LLM-driven approach integrates domain ontologies at each step, letting the model
make more informed decisions in cases where terms have multiple meanings or associations.

### 8.4.1 Named entity recognition

Goal: identify and classify named entities into predefined categories (diseases,
organisms, procedures, etc.) using prompt engineering, where entity types of interest are
explicitly defined in the prompt (typically decided jointly by a data scientist/engineer
and a domain expert). Here, SNOMED's structured knowledge supplies those categories.

**Listing 8.8** retrieves the predefined categories from SNOMED (the propagated first-level
node names):

```cypher
MATCH (n:SnomedEntity)
UNWIND n.type as named_entity
WITH DISTINCT named_entity, count(named_entity) as num_of_entities
ORDER BY num_of_entities DESC
RETURN collect(named_entity) as named_entities
```

**Listing 8.9** — simplified NER prompt structure:

- **System instruction** — extract ALL single mentions of named entities from the text,
  restricted only to categories in `{named_entities}` (no other categories allowed);
  output valid JSON, sentence by sentence.
- **Input text** — example: *"Risk factors for rhinocerebral mucormycosis include poorly
  controlled diabetes mellitus and severe immunosuppression."*
- **Assistant output** — JSON with `sentence` (the analyzed sentence) and `entities`
  (array of `{id, mention, label}`), e.g. "Risk factors" → *Events*, "rhinocerebral
  mucormycosis" → *Disease*, "poorly controlled diabetes mellitus" → *Disease*, "severe
  immunosuppression" → *Qualifier value*.

**Live example (Listing 8.10 → 8.11)**: given user input *"Severe outcomes of Zika are due
to its capacity to cross the placental barrier during pregnancy, causing microcephaly and
congenital malformations."*, Llama 3.1 returns three entities: "Zika" labeled
**Organism** (chars 19–22), "microcephaly" labeled **Clinical finding (finding)** (chars
105–116), and "congenital malformations" labeled **Clinical finding (finding)** (chars
122–145).

**Known LLM weakness**: LLMs have trouble accurately detecting the exact starting/ending
character offsets of mentions. The `start`/`end` fields are therefore computed in
**post-processing**, not trusted from the LLM output, via **Listing 8.12**:

```python
def find_all_mention_indices(self, string, substring):
    indices = []
    start_index = 0

    while True:
        start_index = string.find(substring, start_index)

        if start_index == -1:
            break  # No more occurrences found

        end_index = start_index + len(substring) - 1
        indices.append((start_index, end_index))

        # Move start_index forward to search for the next occurrence
        start_index += len(substring)

    return indices
```

### 8.4.2 Candidate selection

Goal: for each mention found by NER, identify relevant ontology entities/concepts that
could match its intended meaning (Figure 8.4).

**Design decision — no LLM here**, for two reasons:

1. We want candidates retrieved directly from the domain ontology, not from knowledge
   embedded in the LLM (which may be stale or hallucinated).
2. The ontology is too large to load in its entirety into a prompt.

Instead, **Neo4j's full-text search** capabilities identify ontology strings closely
matching each mention (Listing 8.13, `CandidateSelection` class):

```cypher
CALL db.index.fulltext.queryNodes("names", $fulltextQuery, {limit: $limit})
YIELD node
WHERE node:SnomedEntity AND ANY(x IN node.type WHERE x IN $labels)
RETURN distinct node.name AS candidate_name, node.id AS candidate_id
```

`generate_full_text_query` builds a fuzzy query joining words with `~0.80` similarity and
`AND`. The `$labels` parameter — collected from the NER phase's output labels — narrows
the search space to only entity types relevant to the mention.

**Note**: the full-text mechanism could be enhanced with **vector-based search** to
surface additional candidates that text matching alone would miss.

**Example (Listing 8.14)** — passing "Zika" as input yields:

```json
{
  "id": 0,
  "mention": "Zika",
  "label": "Organism",
  "start": 19,
  "end": 22,
  "candidates": [
    {"snomed_id": "50471002", "name": "Zika virus"},
    {"snomed_id": "3928002", "name": "Zika virus disease"},
    {"snomed_id": "762725007", "name": "Congenital Zika virus infection"}
  ]
}
```

Each candidate has `snomed_id` (unique SNOMED concept identifier) and `name` (the
associated medical entity name). These represent possible medical meanings of "Zika" and
set the stage for the disambiguation phase.

### 8.4.3 Candidate disambiguation

Final phase (Figure 8.5): use contextual information from **other medical entities
co-occurring in the same sentence** as the target mention, cross-referenced against the
ontology's structured relationships, to verify and refine which candidate is the best
match.

**Motivating example**: a sentence mentioning both "Zika" and "microcephaly." The presence
of "microcephaly" suggests an association with **Congenital Zika virus infection** (known
to cause microcephaly), letting the disambiguation process prioritize that candidate over
other meanings of "Zika" (general virus, unrelated term, etc.).

Three steps (Figure 8.6):

1. **Detecting shortest paths** — identify minimal-length paths between candidate entities
   associated with different mentions in a sentence, establishing potential relationships
   that clarify intended meaning.
2. **Translating paths to text** — convert each graph path into a natural-language
   sentence so the LLM can process the relational information in its native format.
3. **Summarizing textual paths** — condense all translated-path sentences into one
   synthetic explanation, supporting more accurate disambiguation decisions.

LLMs power steps 2 and 3 (path-to-text translation and summarization); step 1 uses
**Neo4j's Graph Data Science (GDS) library** to find connections between candidates.

#### Detecting shortest paths

Goal: find the shortest path between all possible candidates associated with each medical
entity mention identified during CS. **Listing 8.15** (`PathExtraction` class,
`get_co_occs_query` method) implementation, critical steps:

- **Degree calculation** — retrieve the highest-"degree" (most-connected) nodes in the
  graph via `CALL gds.degree.stream('snomedGraph')`, keeping the top 350 as `hub_nodes`.
  These represent generic, highly connected concepts to be excluded later so the
  disambiguation focuses on more meaningful, less generic connections.
- **Shortest-path search** — `allShortestPaths((s1)-[:SNOMED_RELATION*1..2]-(s2))` finds
  all shortest paths between two entities `s1` and `s2` (by ID), limiting path length to
  1–2 hops, and filtering out paths that pass through hub nodes to avoid generic/overly
  broad relationships.
- **Path transformation** — unwinds nodes/relationships in each path and formats them
  into readable strings showing direction and relationship type, e.g.
  `(n1)-[:REL_TYPE]->(n2)`.

**Example output (Listing 8.16)** — detected paths for "Congenital Zika virus infection,"
"Micrencephaly," "Acrocephaly," etc.:

```json
[
  {"id": 1, "path": "(Congenital Zika virus infection)-[:OCCURRENCE]->(Congenital)<-[:OCCURRENCE]-(Micrencephaly)"},
  {"id": 2, "path": "(Congenital Zika virus infection)-[:OCCURRENCE]->(Congenital)<-[:OCCURRENCE]-(Acrocephaly)"},
  {"id": 10, "path": "(Acrocephaly)-[:IS_A]->(Craniosynostosis syndrome)-[:IS_A]->(Congenital malformation)"}
]
```

Details:

- **Congenital Zika virus infection paths** — many paths begin with *Congenital Zika
  virus infection* linked via `[:OCCURRENCE]` to various congenital conditions
  (*Micrencephaly*, *Acrocephaly*, *Multiple congenital malformations*), implying this
  infection is associated with those conditions, possibly as cause or occurrence.
- **Shared congenital condition** — *Congenital* is a common node linking multiple
  congenital conditions like *Micrencephaly* and *Acrocephaly*, indicating a shared
  occurrence attribute.
- **Alternative relationships** — some paths use `[:IS_A]` and
  `[:PATHOLOGICAL_PROCESS_(ATTRIBUTE)]`, showing hierarchical or attribute-based
  relationships (e.g., *Acrocephaly* classified under *Craniosynostosis syndrome*, linked
  to *Congenital malformation*).

#### Translating paths to text

Converts graph paths into natural language so the LLM can interpret connections between
entities in the format it's optimized for, aiding disambiguation between similar terms.

**Listing 8.17** — simplified prompt:

```python
system = """You are an assistant capable of translating a Neo4j graph path
into a clear sentence.
Use the exact entity names from the path while generating the sentence.
The sentences will assist a large language model (LLM) in disambiguating
biomedical entities.
Ensure the output is a valid JSON with no extraneous characters."""

input = {
  "path": "(Hypertension)-[:RISK_FACTOR_FOR]->(Cardiovascular Disease)<-[:ASSOCIATED_WITH]-(Myocardial Infarction)"
}

assistant = {
  "sentence": "Hypertension is a risk factor for cardiovascular disease. Myocardial infarction is also associated with cardiovascular disease, indicating that hypertension may increase the risk of experiencing a myocardial infarction through its connection to cardiovascular disease."
}
```

- **System instruction** — translate Neo4j graph paths into clear, human-readable
  sentences.
- **Input graph path** — a path from Neo4j representing complex relationships.
- **Assistant output** — valid JSON with the generated sentence.

**Result on the Zika paths (Listing 8.18)** — each path becomes a distinct sentence, e.g.:
*"A Congenital Zika virus infection occurrence is associated with a Congenital
occurrence, which in turn is associated with Micrencephaly."* and *"Micrencephaly occurs
in Congenital and Multiple congenital malformations also occur in Congenital."*

#### Summarizing textual paths

Before final disambiguation, the translated sentences are summarized to reduce
"cognitive load" (fewer tokens) for the model — easier to interpret entity relationships
and select the best candidate without being overwhelmed by excessive detail.

**Listing 8.19** — simplified prompt:

```python
system = """You are an assistant that can summarize multiple sentences
derived from ontology paths into a short summary. This summary will be
used to support a named entity disambiguation task.
Ensure the output is a valid JSON with no extraneous characters."""
```

- **System instruction** — summarize sentences from ontology paths, retaining all
  identified entities; output valid JSON with each summary under key `context`.
- **Input sentences** — multiple sentences, each containing relationships between medical
  conditions and their effects/associations.
- **Assistant output** — one summarized sentence per group of related entities, valid
  JSON.

**Result on the Zika example (Listing 8.20)**:

> "A Congenital Zika virus infection occurrence is associated with various congenital
> malformations, including Micrencephaly, Acrocephaly, Multiple congenital
> malformations, and Other congenital malformations. These conditions all share a common
> link to the Congenital entity."

This distilled `context` string gives the LLM a focused view of the most relevant
relational information for disambiguation.

#### Disambiguation

Final stage: combine the selected candidates and the textual summary from the
summarization phase into one prompt.

**Listing 8.21** — prompt for final disambiguation:

- **System instruction** — identify and accurately disambiguate entities in a sentence,
  relying heavily on contextual entities in surrounding sentences. Inputs: (1) original
  sentence with ambiguous entities, (2) candidate entities (list of possible meanings per
  mention), (3) contextual sentences (the summarized `context`). Objective: use the
  contextual entities as the primary source of information; analyze candidates for each
  ambiguous mention and select the one aligning best with both context and candidate
  meaning. Output must be valid JSON.
- **Assistant output** — for each `id` (entity mention), a `disambiguation` object with
  the chosen `snomed_id` and `name`.

Worked example: input sentence *"Asthma and allergic rhinitis are commonly addressed
together in treatment protocols, given their shared underlying inflammatory processes in
allergic individuals."* with 9 candidates for "asthma" (e.g. *Extrinsic asthma with
asthma attack*, *Asthma*, *Intrinsic asthma*, *Asthma attack*, *Mild asthma*, *Moderate
asthma*, etc.) and context *"Asthma is associated with respiratory disorders. Allergic
rhinitis is also linked to respiratory disorders..."* → the model correctly resolves to
plain **Asthma** (195967001) and **Allergic rhinitis** (61582004), rather than a more
specific/attribute-qualified variant.

**Full end-to-end result (Listing 8.22)** for the sentence *"Severe outcomes of Zika are
due to its capacity to cross the placental barrier during pregnancy, causing microcephaly
and congenital malformations"*:

```json
{
  "entities": [
    {"id": 0, "disambiguation": {"snomed_id": "762725007", "name": "Congenital Zika virus infection"}},
    {"id": 1, "disambiguation": {"snomed_id": "204030002", "name": "Micrencephaly"}},
    {"id": 2, "disambiguation": {"snomed_id": "116022009", "name": "Multiple congenital malformations"}}
  ]
}
```

Each entity is matched to the most relevant SNOMED concept, achieved through contextual
information — this resolves exactly the case (a bare "Zika" mention with supporting
context words like "microcephaly" but no adjacent "congenital"/"syndrome" tokens) where
scispaCy failed in section 8.1's second example.

## 8.5 Conclusions

By integrating domain ontologies like SNOMED with open, general-purpose LLMs such as
Llama 3.1 8B, this approach addresses limitations of traditional NLP tools like scispaCy
in the biomedical domain. The approach is flexible across application domains: Neo4j's
GDS library for shortest-path detection and full-text search, combined with the
disambiguation power of LLMs, forms a robust system for identifying and accurately
disambiguating entities in complex texts. Path-to-text translation and textual path
summarization improve the LLM's ability to process relational data in natural-language
format, enhancing its capacity to distinguish between similar entities. This framework
lays the groundwork for future applications of LLMs in domain-specific NED tasks.

## Takeaways

- Traditional domain-specific NED tools (scispaCy + UMLS) are locked to one domain, hard
  to extend, underuse the knowledge base's full relational structure, and don't leverage
  entity-to-entity paths — causing failures when disambiguating context (like a "Zika"
  mention with no adjacent supporting words) is present.
- The proposed pipeline replaces this with **open LLMs (Llama 3.1 8B via Ollama)** plus a
  **domain ontology (SNOMED)**, generalizable to any domain with a rich ontology.
- SNOMED is ingested into Neo4j as `SnomedEntity` nodes connected by `SNOMED_RELATION`
  edges, with a parallel `SNOMED_IS_A` hierarchy used to **propagate first-level node
  types** down to all descendant nodes — this is how NER categories are derived directly
  from ontology structure rather than hardcoded.
- The end-to-end NED pipeline has three stages: **NER** (LLM extracts mentions using
  ontology-derived categories), **candidate selection** (Neo4j full-text search, no LLM —
  to stay ontology-grounded and avoid context-size limits), and **candidate
  disambiguation** (LLM-driven, using graph-derived context).
- Candidate disambiguation itself is a three-step process: **shortest-path detection**
  (Neo4j GDS, filtering out high-degree "hub" nodes to avoid generic connections),
  **path-to-text translation** (LLM converts graph paths to natural language), and
  **textual path summarization** (LLM condenses translated sentences to reduce cognitive
  load before the final disambiguation call).
- LLMs are unreliable at computing exact character offsets for extracted mentions — offset
  computation is deferred to a deterministic post-processing function rather than trusted
  from LLM output.
- The worked Zika/microcephaly example shows the full pipeline succeeding exactly where
  scispaCy failed: correctly resolving "Zika" to *Congenital Zika virus infection* using
  co-occurring "microcephaly" context via graph paths, with no adjacent supporting words
  needed in the sentence itself.
