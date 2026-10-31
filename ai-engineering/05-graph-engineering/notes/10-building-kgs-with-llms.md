---
origin: book-and-course-condensed
sources:
  - sources/kg-and-llms-in-action/04-multisource-integration.md
  - sources/kg-and-llms-in-action/05-extracting-domain-knowledge.md
  - sources/kg-and-llms-in-action/06-building-kgs-with-llms.md
  - sources/kg-and-llms-in-action/07-named-entity-disambiguation.md
  - sources/kg-and-llms-in-action/08-ned-open-llms-ontologies.md
  - sources/kg-and-llms-in-action/appendix-c-kgs-from-structured-sources.md
  - "Knowledge Graphs for RAG (DeepLearning.AI × Neo4j, 2024), L3–L6: https://www.deeplearning.ai/short-courses/knowledge-graphs-rag/"
  - https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide
confidence: medium-high
cleaned: 2026-10-28
---
# 10 — Building KGs with LLMs: Extraction and Resolution

> Extraction is the easy part. The graph is only as good as its entity resolution: one false merge silently joins two people, and every multi-hop answer that passes through the join is wrong.

---

## Where it sits

[Note 09](09-kg-fundamentals-and-cypher.md) gave you a graph to query. This note covers how one gets built from text. [Note 11](11-kg-rag-and-text-to-cypher.md) covers asking it questions. The pipeline here is itself a Track A graph: fixed stages, a model tier per stage, and a verifier at the end.

---

## Why resolution is the load-bearing step

Treat each hop of a traversal as independently correct with probability *p*. Then an *n*-hop answer is correct with probability *pⁿ*:

| Per-hop accuracy | 2 hops | 3 hops | 5 hops |
|---|---|---|---|
| 95% | 90% | 86% | 77% |
| 85% | 72% | 61% | **44%** |
| 70% | 49% | 34% | 17% |

This is arithmetic, not a measurement. Hops aren't really independent, but the shape holds: **errors compound with depth**. A graph is only worth traversing deeply when resolution is good. Most per-hop errors are resolution errors: two different entities merged, or one entity split across several nodes.

---

## The pipeline

```
 documents
    │
    ▼
 1. Chunk ────────── split, keep doc/page/offset         (L3–L4: Chunk nodes + NEXT links)
    │
    ▼
 2. Extract ──────── NER + relation extraction            cheap model, schema-constrained output
    │                into MENTIONS, not entities
    ▼
 3. Normalise ────── strip titles, case, punctuation      deterministic
    │
    ▼
 4. Resolve ──────── cluster mentions → canonical          stronger model and/or graph signals
    │                (ER) and/or link to an ontology (NED)
    ▼
 5. Assemble ─────── MERGE nodes/edges + provenance       deterministic
    │
    ▼
 6. Evaluate ─────── P/R on entities and edges,           gold set; blocks the load if it regresses
    │                false-merge rate
    ▼
 7. Load / query
```

This is the same shape as Anthropic's KG construction cookbook ([`capabilities/knowledge_graph/guide.ipynb`](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide)). The cookbook extracts with `claude-haiku-4-5` into Pydantic models, resolves and queries with `claude-sonnet-4-6`, assembles a NetworkX `MultiDiGraph` that keeps `source_docs` on nodes and `source_doc` on edges, and scores entity precision and recall against a gold set. In short:

| Stage | Model tier | Output |
|---|---|---|
| Extract | Small/fast (Haiku-class) | Schema-constrained mentions and relations |
| Resolve | Stronger (Sonnet-class) | Clusters: canonical name and aliases |
| Assemble | None (deterministic) | Graph with provenance |
| Query | Stronger | Bounded subgraph, cited edges ([note 11](11-kg-rag-and-text-to-cypher.md)) |

This is the "spend agency per node" rule from [note 02](02-graph-primitives.md): use the model only where judgement is needed.

---

## Stage 2: extraction

Extraction is two tasks: **NER** (find the mentions and assign types) and **relation extraction** (a typed edge between two mentions). Lessons from the book (ch5):

- **Define entity types for the domain, and name them carefully.** Renaming the type "Topic" to "Occupation" improved extraction in ch5. The type name works as an instruction to the model.
- **Use schema-constrained output.** Structured outputs, tool schemas or Pydantic models ([01-prompt note 04](../../01-prompt-engineering/notes/04-controlling-output.md)). Free-text extraction then needs a parser, and the parser becomes another place for errors.
- **Set temperature to 0, then test stability.** Run the same document several times and compare the outputs. Instability tells you the prompt is ambiguous.
- **Write prompt unit tests.** Use small inputs with known outputs, and run them on every prompt change.
- **Look at a mini-KG.** Build the graph from 10 documents and look at it before scaling up. Missing edge types and junk hubs are easy to spot.
- **Don't trust LLM character offsets.** Recompute span positions deterministically (ch8).
- **Fine-tune only when prompting plateaus**, and only once you have the labelled data the evaluation section below would produce anyway.

### Traditional NLP or LLM?

| | spaCy/scispaCy-style pipeline | LLM extraction |
|---|---|---|
| Setup | Needs a trained model for the domain | A prompt and a schema |
| Cost per doc | Very low | Model calls |
| New entity types | Retrain | Edit the prompt |
| Relation extraction | Weak without custom training | Strong |
| Determinism | High | Needs temperature 0 and stability tests |
| Domain IDs (UMLS CUIs, etc.) | Built in when a linker exists | Not by itself (ch7: ChatGPT can't assign UMLS IDs) |

A common hybrid uses a traditional linker where a domain knowledge base exists and an LLM for relations and long-tail types.

---

## Stages 3–4: normalisation, resolution, disambiguation

There are two related problems:

- **Entity resolution (ER):** which mentions are the same thing? ("E. O. Lawrence", "Ernest Lawrence", "Dr. Lawrence").
- **Named-entity disambiguation (NED):** which entry in a reference knowledge base does a mention refer to? ("Zika" → the virus, the disease, or congenital Zika syndrome in UMLS or SNOMED.)

### Keep mentions, never merge at extraction time

The book's three-layer model (ch6):

```
(:Document)-[:HAS_PAGE]->(:Page)-[:MENTIONS]->(:Entity)        ← metagraph: raw mentions
(:Entity)-[:META_SIMILAR]->(:Entity)                            ← resolution evidence
(:Entity)-[:RESOLVES_TO]->(:Canonical)                          ← the KG proper
```

Extraction writes **mentions**. Resolution writes **similarity edges and canonical nodes** on top of them. Nothing is deleted, so the KG can be rebuilt from the metagraph whenever resolution changes. Ch7 does the same thing with `EntityMention` and `MedicalEntity` nodes joined by `DISAMBIGUATED_TO`, and appendix C with a `REPRESENTS` edge to a `NormalizedDisease` node. In all three, **resolution is reversible**. That property is what [note 12](12-kg-as-shared-agent-memory.md) depends on.

### Graph-based ER (ch6)

1. **Normalise** names (strip titles, lowercase, remove punctuation).
2. **Collect evidence** that two mentions are the same entity:
   - **String similarity**, the obvious signal and also the risky one;
   - **Relational signals**: same employer, same topics, same Louvain community, close in embedding space.
3. Write a `META_SIMILAR` edge wherever the evidence is strong enough.
4. Run **weakly connected components** over `META_SIMILAR`. Each component becomes one canonical entity, named after its longest name.
5. Send borderline clusters to a **human review queue**. Ch6 found **Laurence Irving**, a physiologist, inside the cyclotron subgraph. GPT had spelled his name "Lawrence" because Ernest Lawrence appeared on the same page. That was an extraction error, and only a person looking at the graph caught it.

String similarity alone causes false merges, and a misspelled extraction gives it more to match on. Relational evidence is what tells two Lawrences apart.

### LLM-based ER (cookbook)

Give the model the unique names of one type *together with their extraction descriptions*, and ask for clusters of the form `{canonical, aliases[]}`. The descriptions are what stop two different people named Armstrong from being merged. The failure modes are **dropped names** (a name that appears in no cluster; fall back to a singleton cluster) and **over-merging** (the cookbook's example folds "Gemini 12" into "Project Gemini").

### NED against an ontology (ch7–8)

Three phases:

1. **Candidate selection.** Look up the ontology for possible matches, using a full-text index search in Neo4j with fuzzy terms (`~0.8`), filtered by the entity types NER returned. **No LLM here**: candidates must come from the ontology, not from what the model remembers, and the ontology won't fit in a prompt anyway.
2. **Candidate ranking and disambiguation.** Choose the candidate that fits the context. Ch8 does this by finding **shortest paths** between candidate concepts and the other entities in the document (dropping **hub** nodes such as "Infectious process", which connect everything to everything), turning the paths into sentences, summarising them, and then asking the LLM to choose. That is how "Zika" next to "microcephaly" resolves to *congenital Zika virus infection*.
3. **Ontology integration.** The resolved entity gains its ontology neighbourhood: synonyms, parents and related concepts.

Use NED when a reference ontology exists (medicine, law, finance identifiers). Use ER when it doesn't.

### Measure what normalisation did

Appendix C compares the graph before and after normalisation using WCC counts and all-pairs shortest-path distributions. After normalisation, related nodes sit closer together. Three spellings of Burkitt lymphoma had been splitting one disease into three nodes. Do the same with your own graph. If resolution has no measurable effect on structure, it probably isn't doing anything.

---

## Stage 6: evaluating extraction

The hop table above is the reason this stage exists. Hand-label a gold set (50–100 mentions is enough to start), then measure:

| Metric | Over | Catches |
|---|---|---|
| **Entity precision / recall** | Extracted entities vs. gold | Missed and hallucinated entities |
| **Edge precision / recall** | (subject, type, object) triples vs. gold | Wrong or missing relations; wrong edge type |
| **False-merge rate** | Pairs in one canonical cluster that are actually different | Over-merging (the expensive error) |
| **False-split rate** | Gold entities spread over more than one canonical | Under-merging (cheaper: lowers recall, doesn't corrupt) |
| **Stability** | Same input, repeated runs | Prompt ambiguity |

**Weight false merges more heavily than false splits.** A split loses a connection. A merge creates connections that don't exist, and traversal then follows them confidently. Gate the load step on these metrics the way [06-eval note 10](../../06-eval/notes/10-evals-in-ci.md) gates a deploy, and see [06-eval note 03](../../06-eval/notes/03-eval-datasets.md) for building the gold set.

---

## Stage 5: assembly, with the course as worked example

The Neo4j course builds an SEC filings graph one stage at a time:

| Lesson | Builds |
|---|---|
| L3 | Vector index and embeddings with `genai.vector.encode` |
| L4 | 10-K text split into `Chunk` nodes with embeddings, so Neo4j is also the vector store |
| L5 | `NEXT` links between chunks (a linked list), `PART_OF` to the form; window retrieval over neighbours |
| L6 | A second source (Form 13 investment managers) merged onto the same `Company` nodes; uniqueness constraints; full-text index |
| L7 | `Address` nodes geocoded from the company and manager address strings, a point index, `LOCATED_AT` edges |

L6 is appendix C's lesson at small scale: **`MERGE` on a shared identity key is how sources are fused**, and it only works if identities have been resolved first.

The course names its build loop **extract, enhance, expand**: pull out nodes from a source, give them an index or a unique key, then connect them. Its advice is to start with a **minimum viable graph** and grow it one source at a time.

![Extract, enhance, expand for four node types: Chunk from the 10-K JSON (vector embedding, NEXT), Form (unique chunk IDs, PART_OF), Company from Form 13 (unique cusip6, FILED) and Manager (full-text index of names, OWNS_STOCK_IN)](../sources/images/kollegger-knowledge-graphs-for-rag-extract-enhance-expand.png)
*Image Source: Knowledge Graphs for RAG, DeepLearning.AI × Neo4j (Kollegger, 2024)*

**Before the graph: clean the source.** The 10-K filings come from SEC EDGAR as text files with embedded XML. The course's JSON was produced by regex clean-up, parsing the XML with Beautiful Soup, pulling out the company's CIK (the SEC's company identifier) and keeping four sections: Items 1, 1A, 7 and 7A. The instructor's prep code is public at [neo4j-product-examples/data-prep-sec-edgar](https://github.com/neo4j-product-examples/data-prep-sec-edgar). Its plan of attack for L4 is five steps: split each section into chunks, make each chunk a node with its metadata as properties, create a vector index, embed every chunk into it, then search by similarity. At that point Neo4j is only a vector store; the graph starts in L5.

![Two node types and their properties: Chunk (chunkId, chunkSeqId, cik, cusip6, f10kItem, formId, names, source, text, textEmbedding) and Form (formId, source, cik, cusip6)](../sources/images/kollegger-knowledge-graphs-for-rag-form10k-chunk-and-form-nodes.png)
*Image Source: Knowledge Graphs for RAG, DeepLearning.AI × Neo4j (Kollegger, 2024)*

**L3–L4: chunks as nodes, with a key and an embedding.** Each 10-K section is split (`RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)`) and every chunk gets a deterministic ID, so reloading is idempotent:

```cypher
// The constraint first: it makes MERGE safe and indexes the key
CREATE CONSTRAINT unique_chunk IF NOT EXISTS
FOR (c:Chunk) REQUIRE c.chunkId IS UNIQUE;

// chunkId = "{formId}-{item}-chunk{seq:04d}": same input, same node
MERGE (c:Chunk {chunkId: $chunk.chunkId})
  ON CREATE SET c.text = $chunk.text, c.formId = $chunk.formId,
                c.f10kItem = $chunk.f10kItem, c.chunkSeqId = $chunk.chunkSeqId;

// Neo4j as the vector store: embed in the database, then index
MATCH (c:Chunk) WHERE c.textEmbedding IS NULL
WITH c, genai.vector.encode(c.text, "OpenAI", {token: $openAiApiKey}) AS v
CALL db.create.setNodeVectorProperty(c, "textEmbedding", v);
```

`genai.vector.encode` was the GenAI plugin's API when the course was recorded. Check your Neo4j version's GenAI docs before reusing it, because the embedding functions have since been renamed. One bug to avoid if you run the L4 notebook: `split_form10k_data_from_file` loops over `item1_text_chunks[:20]` instead of the current item's chunks, so every item's chunks contain Item 1 text.

**L5: structure between chunks.** Chunks of one section become a linked list, and each chunk points to its form:

![Three Chunk nodes linked in order by NEXT, each with a PART_OF edge up to one Form node](../sources/images/kollegger-knowledge-graphs-for-rag-chunk-next-part-of.png)
*Image Source: Knowledge Graphs for RAG, DeepLearning.AI × Neo4j (Kollegger, 2024)*

```cypher
// Order a section's chunks and link neighbours with NEXT (APOC)
MATCH (c:Chunk {formId: $formId, f10kItem: $item})
WITH c ORDER BY c.chunkSeqId ASC
WITH collect(c) AS section
CALL apoc.nodes.link(section, "NEXT", {avoidDuplicates: true})
RETURN size(section);

// Every chunk belongs to its form
MATCH (c:Chunk), (f:Form) WHERE c.formId = f.formId
MERGE (c)-[:PART_OF]->(f);
```

The `NEXT` links are what make window retrieval possible in [note 11](11-kg-rag-and-text-to-cypher.md#retrieval-modes). The course also adds a `SECTION` edge from the form to the first chunk of each item (`chunkSeqId = 0`).

**L6: fuse a second source on a shared key.** Form 13 is filed by institutional investment managers to report the companies they hold. It adds `Manager` nodes and attaches them to the **same** `Company` nodes, matched on the CUSIP:

![Two new node types from Form 13: Manager (managerCIK, managerName, managerAddress) and Company (companyName, cusip6, cusip)](../sources/images/kollegger-knowledge-graphs-for-rag-form13-manager-and-company-nodes.png)
*Image Source: Knowledge Graphs for RAG, DeepLearning.AI × Neo4j (Kollegger, 2024)*


```cypher
CREATE CONSTRAINT unique_manager IF NOT EXISTS
FOR (m:Manager) REQUIRE m.managerCik IS UNIQUE;

MERGE (com:Company {cusip6: $row.cusip6})
  ON CREATE SET com.companyName = $row.companyName
MERGE (mgr:Manager {managerCik: $row.managerCik})
  ON CREATE SET mgr.managerName = $row.managerName
// The quarter is part of the edge's identity; value and shares are data on it
MERGE (mgr)-[o:OWNS_STOCK_IN {reportCalendarOrQuarter: $row.quarter}]->(com)
  ON CREATE SET o.value = toFloat($row.value), o.shares = toInteger($row.shares);

// Full-text index so "royal bank" finds "Royal Bank of Canada"
CREATE FULLTEXT INDEX fullTextManagerNames IF NOT EXISTS
FOR (m:Manager) ON EACH [m.managerName];
```

Why a constraint when `MERGE` already matches on `managerCik`? The Cypher manual is explicit: *"Under concurrent updates, `MERGE` only guarantees the existence of the `MERGE` pattern, but not uniqueness."* The constraint is what guarantees one node per key. After L6 the course graph holds 643 nodes (`Chunk`, `Form`, `Company`, `Manager`) and 722 relationships (`NEXT`, `PART_OF`, `SECTION`, `FILED`, `OWNS_STOCK_IN`).

Notice that `value` and `shares` live on the **edge**, not on `Company`. That detail is what trips text-to-Cypher up in [note 11](11-kg-rag-and-text-to-cypher.md#the-failure-to-expect).

**L7: one more extract, enhance, expand round.** Both `Company` and `Manager` carry an address string. The course turns them into nodes: **extract** the full address strings and geocode them to city, state, country and latitude/longitude; **enhance** with a geospatial index on `Address.location` so distance queries are cheap; **expand** with `(:Manager|:Company)-[:LOCATED_AT]->(:Address)`. Queries then read location from the `Address` node, not from the old string properties. The location questions this answers are in [note 11](11-kg-rag-and-text-to-cypher.md#structured-lookups-by-name-and-by-place).

![Address nodes: source is the Company and Manager address strings; extract Address with city, state and country; enhance with a geospatial location index; expand with LOCATED_AT from Manager and Company, alongside the Manager OWNS_STOCK_IN Company edge](../sources/images/kollegger-knowledge-graphs-for-rag-address-nodes.png)
*Image Source: Knowledge Graphs for RAG, DeepLearning.AI × Neo4j (Kollegger, 2024)*

The course's list of where to grow next is a useful default: cross-link companies that mention each other (suppliers, competitors), extract people, places and topics from the text, add more form types or related sources, and add users so feedback can refine relevance.

**Curate before you scale** (appendix C). Start from a few sources that matter for the task. Every extra loosely related dataset adds reconciliation work and noise.

### Integrating structured sources (ch4)

Not every KG starts from text. Ch4 fuses public structured datasets: protein–protein interactions with disease associations (DisGeNET), the pharmacology graph **Hetionet**, and the **Clinical Knowledge Graph**. The work moves from extraction to three other steps:

- **Identity mapping.** Every source is mapped onto shared codes (UMLS, Disease Ontology) before `MERGE`. This is entity resolution, made easier because the identifiers are curated.
- **Schema alignment.** Reconcile what each source means by its edge types before they share a graph.
- **Validation.** Check counts, orphans and degree distributions after each load.

Two analysis lessons carry over to any integrated graph:

- **Generic clustering and domain subgraph metrics answer different questions.** WCC and Louvain show the global community structure, but they treat every node alike. A meaningful subgraph (one disease's pathway, say) needs its own metrics, such as largest component, density and conductance.
- **Raw path counts favour hubs.** DWPC discounts paths through high-degree nodes ([note 13](13-graph-ml-and-gnns.md#dwpc-discount-the-hubs)).

The LLM's role here is to **interpret** the quantitative output (a DWPC ranking, a set of protein–disease links) as a domain narrative. It doesn't replace expert judgement, which matters most in the clinical case.

---

## Domain examples in the book (one paragraph each)

- **Archives (ch6).** Rockefeller Archive Center documents: people, institutions and funding. This is the source of the Ernest Lawrence ER example. Three mentions on different pages were resolved to one person using string similarity, a shared employer and related `Occupation`s. Two of the mentions were six hops apart in the graph, which a relational database would make hard to find.
- **Biomedical NED (ch7–8).** ECDC bulletins linked to UMLS (scispaCy) and SNOMED (open LLM with graph paths). Co-occurrence edges are checked against ontology paths. A co-occurrence with no ontology path is a candidate new fact.
- **Biomedical integration (ch4).** PPI and disease networks, Hetionet (a celiac-disease case study using metapaths and DWPC) and the Clinical Knowledge Graph, with LLM-assisted interpretation of pathway analyses.
- **miRNA (appendix C).** A KG built from structured sources: curated datasets, disease-ontology normalisation and DWPC path scoring to rank disease–target hypotheses.

---

## Working reference

`~/.claude/refs/agent-eval.md`: gold sets and gating. `~/.claude/refs/agent-memory.md`: semantic memory writes.

Depth: [ch4](../sources/kg-and-llms-in-action/04-multisource-integration.md) (multisource integration, DWPC), [ch5](../sources/kg-and-llms-in-action/05-extracting-domain-knowledge.md), [ch6](../sources/kg-and-llms-in-action/06-building-kgs-with-llms.md), [ch7](../sources/kg-and-llms-in-action/07-named-entity-disambiguation.md), [ch8](../sources/kg-and-llms-in-action/08-ned-open-llms-ontologies.md), [appendix C](../sources/kg-and-llms-in-action/appendix-c-kgs-from-structured-sources.md). Practice: [lab B3](../practice/exercises.md#b3--build-the-10-k-graph) and [lab B4](../practice/exercises.md#b4--tiered-extraction-with-a-false-merge-rate).

---

→ Next: [11-kg-rag-and-text-to-cypher.md](11-kg-rag-and-text-to-cypher.md): asking the graph questions in natural language.
