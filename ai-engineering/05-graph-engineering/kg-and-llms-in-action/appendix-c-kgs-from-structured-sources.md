---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Appendix C: Building knowledge graphs from structured sources"
confidence: high
cleaned: 2026-07-29
---

# Appendix C — Building Knowledge Graphs from Structured Sources

## Overview and process model

The appendix builds a knowledge graph (KG) from structured biomedical data sources, using
a biomedical use case: predicting **microRNA (miRNA)–disease associations**. The target KG
connects a disease node (e.g., celiac disease) to a set of miRNA nodes through `RELATED_TO`
relationships. The construction follows the **CRISP-DM model** adapted to KGs (introduced
in chapter 2): business understanding, data understanding, data preparation, modeling
(defining ML algorithms), evaluation, and deployment — with data preparation feeding both
the current scope and the next iteration's KG model. This appendix focuses on the
construction phase (data understanding, data preparation, initial schema modeling), noting
that understanding the eventual ML analysis matters early since it shapes the graph model.

## C.1 MicroRNA–disease association: domain background

**MicroRNA (miRNA)** is a relatively newly discovered type of noncoding RNA — RNA not
translated into a protein. These small molecules (19–22 nucleotides) interfere with
complementary messenger RNAs (mRNAs), which are normally translated into proteins, causing
**gene silencing**: "regulation of or interference with gene expression." miRNAs silence
through a combination of translational repression and mRNA destabilization: a miRNA binds
to a portion of a target mRNA, blocking it from flowing through the ribosome so protein
synthesis cannot take place — in contrast to normal encoding, where DNA is transcribed into
mRNA and translated into amino acid chains via the ribosome and transfer RNA.

miRNAs are involved in cell differentiation, proliferation, signal transduction, and viral
infection, and are implicated in complex human diseases such as cancer and metabolic
disorders (e.g., mir-433 is involved in gastric carcinoma by regulating protein GRB2).

**Business goal**: predict connections between miRNAs and diseases. Thousands of miRNAs
have been identified, so the combinatorial space of possible miRNA–disease links is huge,
and in vitro validation experiments are expensive — a predictive model helps researchers
prioritize which correlations to investigate, reducing cost and time (an intelligent
advisor system, a recurring theme in the book).

**Data understanding**: the field is young but data-rich. **Tools4miRs**
(https://tools4mirs.org) offers "all the tools you need to analyze your miRNAs," with 170+
methods and many databases, recommended as an entry point for extending this KG.

## C.2 Building the miRNA knowledge graph

### Design philosophy: curated ingestion over "throw everything in"

A tempting "greedy" approach ingests every available miRNA/disease dataset and lets the ML
model sort signal from noise, assuming more data means a better domain model. This is
unwise for two reasons:

- **Signal-to-noise ratio**: every dataset has noise; if a dataset is only marginally
  relevant to link prediction, noise can overwhelm its signal's benefit.
- **Reconciliation cost**: new datasets must be reconciled with the existing KG before
  graph ML algorithms can exploit them fully — often not straightforward, and errors
  introduced during reconciliation amplify noise.

The chosen approach starts with a small set of datasets directly relevant to the task
(predicting pathology links), producing a KG of manageable complexity as a baseline; new
sources are added and benchmarked against it later.

### C.2.1 Importing known miRNA–disease connections

Three independently curated sources, each encoding relations differently, are selected for
the first ingestion round:

- **HMDD** — Human miRNA Disease Database (http://www.cuilab.cn/hmdd)
- **dbDEMC** — Database of Differentially Expressed miRNAs in Human Cancers
  (https://www.biosino.org/dbDEMC)
- **miR2Disease** (www.mir2disease.org)

The **first iteration target schema** uses two distinct relationship types to preserve
each dataset's semantic nuance and let query results reveal provenance:

| Node | Relationship | Node | Meaning |
|---|---|---|---|
| MiRNA | `REGULATES` | Disease | dbDEMC / miR2Disease semantics (regulation direction known) |
| MiRNA | `RELATED_TO` | Disease | HMDD semantics (association, not necessarily regulation) |
| MiRNA | `HAS_REFERENCE` | Reference | links miRNA to supporting PubMed publication |

These two relationship types can be merged later during modeling if needed.

**HMDD import.** HMDD provides experiment-supported evidence for human miRNA–disease
associations and is manually curated — "a solid foundation for our KG." `HMDDImporter`
reads tab-separated latin-1 rows into dicts keyed by header, then runs:

```cypher
UNWIND $batch as item
WITH trim(toLower(item.disease)) as disease, toLower(item.mir) as mir, item
MERGE (d:Disease {name: disease})
MERGE (m:MiRNA {name:mir})
SET m:MiRNA_HMDD
MERGE (m)-[r:RELATED_TO]->(d)
SET r.description = item.description, r.pmid=item.pmid, r.category = item.category
MERGE (ref:Reference {pubmed_id:item.pmid})
MERGE (m)-[:HAS_REFERENCE]->(ref)
```

Mechanism: lowercases/trims disease and miRNA names for identity matching; `MERGE`s
Disease and MiRNA nodes on `name` (idempotent upsert); tags the miRNA node with an extra
`MiRNA_HMDD` label for provenance; `MERGE`s `RELATED_TO` storing description, PubMed ID,
and category as relationship properties; `MERGE`s a `Reference` node keyed by PubMed ID,
connected via `HAS_REFERENCE`. A companion `set_constraints` method issues `CREATE
CONSTRAINT ... IS UNIQUE` for `Disease.name`, `MiRNA.name`, `Reference.pubmed_id`, and
`Target.name` up front, catching Neo4j's "constraint already exists" error to stay
idempotent.

Sample HMDD record: `{'category': 'genetics_GWAS', 'mir': 'hsa-mir-502', 'disease':
'Carcinoma, Renal Cell, Clear-Cell', 'pmid': 27346408, 'description': "Polymorphism at the
miR-502 binding site..."}` — hsa-mir-502 associated with clear cell renal cell carcinoma,
supported by PubMed ID 27346408. After the HMDD import: **1,207 distinct miRNAs, 18,732
distinct connections, 849 distinct diseases**.

**dbDEMC import.** dbDEMC is an integrated database of differentially expressed miRNAs in
human cancer, with 403 expression datasets from microarray and sequencing platforms.
`DBDEMCImporter.get_rows` filters incomplete records and non-human species, prefers the
more specific `CancerSubtype` field over `CancerType` when present, and normalizes
punctuation in the disease string. The import query:

```cypher
UNWIND $batch as item
MERGE (m:MiRNA {name: item.name})
SET m:MiRNA_dbDEMC
WITH m,item
MERGE (n:Disease {name: item.disease})
SET n:DiseaseDbDEMC, n.name_in_db_demc = item.disease
MERGE (m)-[r:REGULATES {regulated: item.regulated}]->(n)
SET r.source = 'dbDEMC', r.experiment = item.experiment
```

merges MiRNA/Disease nodes by name, tags provenance labels (`MiRNA_dbDEMC`,
`DiseaseDbDEMC`), and merges `REGULATES` carrying `regulated` (up/down status), `source`,
`experiment`. Sample: `{'name': 'hsa-miR-155', 'disease': 'glioblastoma', 'experiment':
'EXP00065', 'regulated': 'UP'}` — elevated hsa-miR-155 in glioblastoma tumors vs. healthy
brain tissue.

Because `MERGE` never creates duplicate nodes on a match, cross-dataset knowledge
accumulates on the same node. From HMDD, hsa-mir-155 is already known to be overexpressed
in active multiple sclerosis lesions and ischemic cardiomyopathy; after dbDEMC, the same
node connects to both tumor and non-tumor brain disease (glioblastoma, multiple sclerosis)
and both brain and heart disease — **information fusion via merging**: if these pathologies
share a mechanism (e.g., inflammation from elevated hsa-miR-155), and a new pathology is
independently linked to that mechanism, a link-prediction model has enough structure to
infer an undocumented relationship to hsa-miR-155.

**miR2Disease import.** A manually curated database of miRNA deregulation across human
diseases, with a public submission page so it keeps growing. Its importer mirrors dbDEMC's
shape: parse tab-separated rows into `{name, disease, regulated}`, then `MERGE (d:Disease
{name: item.disease})`, `MERGE (m:MiRNA {name:item.name})`, `MERGE (m)-[r:REGULATES]->(d)`,
`SET r.regulation = item.regulated`.

**After all three datasets**: **4,874 distinct miRNAs, 118,806 distinct connections,
1,144 distinct diseases.**

### Analyzing dataset overlap

Grouping miRNA nodes by their combination of provenance labels (excluding the generic
`MiRNA` label) shows the ingested distribution:

```cypher
MATCH (n:MiRNA)
WITH DISTINCT LABELS(n) AS labels, COUNT(*) as count
RETURN [l in labels where "MiRNA"<> l ] AS labels, Count
ORDER by count DESC
```

| Label combination | Count |
|---|---|
| MiRNA_dbDEMC | 2550 |
| MiRNA_HMDD, MiRNA_dbDEMC | 583 |
| MiRNA_HMDD, MiRNA_dbDEMC, MiRNA_miR2Disease | 328 |
| MiRNA_HMDD | 280 |
| MiRNA_dbDEMC, MiRNA_miR2Disease | 84 |
| MiRNA_miR2Disease | 32 |
| MiRNA_HMDD, MiRNA_miR2Disease | 15 |

The distribution is fairly balanced between shared and nonshared miRNAs. Shared miRNAs
benefit downstream ML from cross-dataset knowledge; nonshared miRNAs represent each
dataset's unique contribution.

### C.2.2 Importing the disease ontology (entity normalization)

**Problem**: different sources name the same disease differently — a common issue for
biological/medical data. A misalignment lets two miRNAs connect to what are actually the
same disease under different names, making the KG unreliable and biasing link prediction
toward false negatives. Example: three datasets referred to Burkitt lymphoma as "burkitt's
lymphoma," "lymphoma, burkitt," and "burkitt lymphoma," producing three separate nodes.

#### Disease normalization with UMLS and scispaCy

The fix uses the **Unified Medical Language System (UMLS)** ontology
(https://www.nlm.nih.gov/research/umls), which "integrates and distributes key
terminology, classification, and coding standards... to promote the creation of more
effective and interoperable biomedical information systems and services, including
electronic health records." Entity linking uses **scispaCy**
(https://allenai.github.io/scispacy), a Python package of spaCy models for
biomedical/scientific/clinical text that performs named entity recognition of UMLS
entities and returns each entity's canonical name, concept ID, and type ID.

**Schema decision**: rather than merging the differently-named nodes directly, a new
`NormalizedDisease` node is created and connected to each original `Disease` node via a
`REPRESENTS` relationship — preserving the original structure so errors are easy to review
and the normalization step is easy to reset and rerun. Updated schema: `MiRNA
-[REGULATES|RELATED_TO]-> Disease -[REPRESENTS]-> NormalizedDisease`, with `MiRNA
-[HAS_REFERENCE]-> Reference` unchanged.

The **`Reconciliator`** class drives the import: it queries all `(d:Disease)` nodes, reverses
comma-separated name fragments (normalizing e.g. "leukemia, lymphocytic, chronic, b-cell"
to "b-cell chronic lymphocytic leukemia"), runs each through a `DiseaseResolver`, and writes:

```cypher
UNWIND $batch as item
MATCH (d:Disease)
WHERE id(d) = item.source_id
MERGE (nd:NormalizedDisease {name:item.name})
SET nd.umnls_id = item.umnls_id
MERGE (d)-[:REPRESENTS]->(nd)
```

The **`DiseaseResolver`** class holds the entity-typing logic. It loads scispaCy's
`en_core_sci_sm` model, attaches the `scispacy_linker` pipe (config `resolve_abbreviations:
True, linker_name: "umls"`), and exposes the linker's `semantic_type_tree` (maps UMLS
semantic types to canonical type names, e.g. "Disease or Syndrome") and `cui_to_entity`
(maps a UMLS Concept ID/CUI to full entity metadata including canonical name). Two type
lists drive validity: `full = ["Finding", "Organ or Tissue Function", "Tissue"]` — types
that can represent a disease only if the match spans the *entire* input text — and `banned
= ["Human", "Body Part, Organ, or Organ Component", "Qualitative Concept", "Temporal
Concept", "Functional Concept", "Body Space or Junction", "Spatial Concept"]` — types that
can never represent a disease. `validEntity` rejects an entity whose types are entirely
within `banned`; accepts an entity whose types are entirely within `full` only if it
matches the whole text; otherwise accepts it. `normalize(item)` is the entrypoint: if
exactly one entity (`item.ents`) is detected and it's valid, it returns `(canonical_name,
UMLS CUI)`; if zero or multiple entities are detected, or the single entity is invalid, it
falls back to `normalize_default`, which title-cases the raw string and returns `(name,
None)`.

**Result**: the three Burkitt lymphoma spelling variants are now all connected via
`REPRESENTS` to a single `NormalizedDisease` node named *Burkitt Lymphoma*.

#### Evaluating the effect of normalization with WCC

To quantify how much normalization reduces fragmentation, **weakly connected components
(WCC)** from Neo4j GDS runs before and after — WCC identifies disconnected subgraphs and
labels each node with its subgraph id. Two in-memory projections:

```cypher
CALL gds.graph.project("not-normalized", ["MiRNA","Disease"], ["REGULATES","RELATED_TO"]);
CALL gds.graph.project("normalized", ["MiRNA","Disease","NormalizedDisease"],
                        ["REGULATES","RELATED_TO","REPRESENTS"])
```

```cypher
CALL gds.wcc.stream('not-normalized')
YIELD nodeId,componentId
RETURN componentId AS subgraph, count(nodeId) AS componentSize
```

| subgraph | before | after |
|---|---|---|
| 0 | 5010 | 6033 |
| 1166 | 3 | 4 |
| 1838 | 2 | 3 |

The graph was already well-connected before normalization (one dominant component holding
almost every node), so WCC shows only modest change; other GDS community-detection
algorithms could quantify impact further but are harder to interpret for this purpose.

#### Measuring distance reduction with all-pairs shortest path (APSP)

A more direct measurement: two miRNAs connected only through differently-named-but-
identical diseases should have their shortest-path distance reduced after normalization.
Example: hsa-mir-199a* to hsa-mir-182 via one shared Disease node (distance 1), vs.
hsa-mir-199a* to hsa-mir-4728 via two Disease nodes (distance 2) — but since "burkitt's
lymphoma" and "lymphoma, burkitt" are the same disease, that distance should really be 1.

Pre-normalization projection (miRNA–miRNA edge if a shared Disease connects both):

```cypher
call gds.graph.project.cypher("DiseaseDistance",
    "MATCH (n:MiRNA) return id(n) as id",
    "MATCH (a:MiRNA)-[:REGULATES|RELATED_TO]->(:Disease)<-[:REGULATES|RELATED_TO]-(b:MiRNA)
     WHERE id(a)<id(b)
     RETURN distinct id(a) as source, id(b) as target")
```

Post-normalization projection (edge if a `Disease-[]-(NormalizedDisease)-[]-Disease` chain
connects both):

```cypher
call gds.graph.project.cypher("NormalizedDiseaseDistance",
    "MATCH (n:MiRNA) return id(n) as id",
    "MATCH p1=(a:MiRNA)-[:REGULATES|RELATED_TO]->()-[:REPRESENTS]->(d)
     MATCH p2=(d)<-[:REPRESENTS]-()<-[:REGULATES|RELATED_TO]-(b:MiRNA)
     WHERE id(a)<id(b)
     RETURN distinct id(a) as source, id(b) as target")
```

Note: `gds.graph.project` (label/relationship-type based) is generally faster than
`gds.graph.project.cypher` since it reuses information already indexed in the database;
Cypher projections are slower but more flexible, better suited to exploratory work,
including projecting one graph onto another via computed traversals as done here.

```cypher
CALL gds.allShortestPaths.stream('DiseaseDistance',{})
YIELD distance
RETURN distinct distance, count(distance) AS Count
```

| Distance | before | after | Variation |
|---|---|---|---|
| 1 | 5,911,305 | 6,179,329 | +4.5% |
| 2 | 1,244,305 | 1,010,851 | −18.7% |
| 3 | 35,795 | 25,888 | −27.6% |
| 4 | 870 | 612 | −29.6% |
| 5 | 46 | 22 | −52.1% |
| 6 | 1 | 0 | −100% |

Pairs at distance 1 increased ~4.5%, and every longer distance decreased — a clear shift
toward shorter distances. This matters because many graph embedding techniques rely on
**message passing**, which propagates information along relationships to compute node
embeddings each iteration; shorter connections between relevant nodes translate directly
into higher-quality embeddings.

#### Using LLMs for entity normalization (alternative approach)

LLMs offer an alternative to scispaCy when specialized biomedical NLP tools are unavailable
or unsuitable, benefiting from exposure to vast biomedical literature during pretraining:

- **Handling terminology variations** — LLMs can recognize semantic equivalence between
  terms without predictable transformation patterns, e.g. "Gastric adenocarcinoma" and
  "Stomach cancer" as the same entity.
- **Domain-agnostic application** — the reconciliation approach isn't limited to
  biomedical text; LLMs could normalize entities in legal, financial, or technical
  documents where tools like scispaCy don't exist.
- **Zero-shot capabilities** — unlike the UMLS-based approach, LLMs might normalize common
  entities reasonably well without any external knowledge base.

Limitations: LLM output is probabilistic, so mappings may be inconsistent across runs,
compromising reproducibility of KG construction; and deploying LLMs for reconciliation at
scale requires substantially more compute than lightweight approaches like scispaCy.

### C.2.3 Importing miRNA information (enriching with similarity signals)

Beyond miRNA-to-disease associations, the KG can be enriched with data connecting miRNAs to
each other: **direct similarity** (`SIMILAR_TO`) and **indirect similarity** induced
through shared nodes (two miRNAs sharing a `Target` mRNA, or cited together in the same
`Reference`). If two miRNAs bind the same target mRNA they're similar in that they
regulate/silence the same gene expression; two miRNAs cited in the same publication are
somehow related from the authors' perspective. The embedding model learns during training
which implicit signal is most useful for link prediction.

**Updated schema**: adds `MiRNA -[HAS_FEATURE]-> MiRNA` (self-referential, e.g. miRNA
family members from miRBase), `MiRNA -[SIMILAR_TO]-> MiRNA` (functional similarity), and
`MiRNA -[HAS_TARGET]-> Target`.

**miRBase** (www.mirbase.org) is a searchable database of ~200 published miRNA sequences
and annotations; for each miRNA it lists relevant publications and connected miRNAs.
`BioImporter` parses the EMBL-format file with Biopython's `Bio.SeqIO`, keeping only human
("hsa"-prefixed) miRNAs with valid names, and extracting nested publication references and
related-miRNA "features" from each record. The import query:

```cypher
UNWIND $batch as item
MATCH (m:MiRNA {name: item.name})
SET m:MiRNA_miRBase, m.description = item.description, m.seq = item.seq,
    m.comment = item.comment
WITH m,item
FOREACH (feature in item.features |
    MERGE (f:MiRNA {name: feature.name})
    MERGE (m)-[:HAS_FEATURE]->(f)
)
WITH m,item
UNWIND item.references as reference
MERGE (r:Reference {pubmed_id: reference.pubmed_id})
ON CREATE SET r.authors = reference.authors, r.title = reference.title,
              r.journal = reference.journal
MERGE (m)-[:HAS_REFERENCE]->(r)
```

sets biological metadata (description, sequence, comment) on the existing MiRNA node, tags
it `MiRNA_miRBase`, iterates `features` to `MERGE` `HAS_FEATURE` edges to other MiRNA
nodes, and iterates `references` to `MERGE` `Reference` nodes (setting authors/title/
journal only `ON CREATE`, i.e. first time seen), connected via `HAS_REFERENCE`.

**miRDB** (https://mirdb.org) is an online database for miRNA target prediction and
functional annotation, built with the bioinformatics tool **miRTargetLink 2.0**
(https://ccb-compute.cs.uni-saarland.de/mirtargetlink2) by analyzing miRNA–target
interactions from high-throughput sequencing. It contains 3.5 million predicted targets
regulated by 7,000 miRNAs across 5 species; only human miRNAs already in the graph are
kept. Each record carries a **confidence score**: `{'name': 'hsa-mir-96-5p', 'target':
'NM_012214', 'value': 90.3926}`, stored as `MiRNA -[HAS_TARGET {value: 90.3926}]-> Target`.

**MISIM** (http://www.limed.com/misim) computes miRNA functional similarity by comparing
the semantic values of diseases associated with two miRNAs: `{"sourceName": "hsa-mir-376a",
"destinationName": "hsa-mir-449a", "value": 0.9101}`, stored as `MiRNA -[SIMILAR_TO {value:
0.9101}]-> MiRNA`.

This completes ingestion. Before deeper analysis, the book suggests self-check exercises:
node counts per type; which disease connects to the most miRNAs (and the median); which
miRNAs connect to the most diseases (and the median) — building intuition about graph size,
which affects both algorithm runtime and model quality.

A prebuilt backup of the resulting database
(https://downloads.graphaware.com/neo4j-db-seeds/hmdd2.0.backup) can be restored by adding
`dbms.databases.seed_from_uri_providers=URLConnectionSeedProvider` to `neo4j.conf`, then:

```cypher
CREATE DATABASE `hmdd2.0` OPTIONS {existingData: "use", seedUri:
  "https://downloads.graphaware.com/neo4j-db-seeds/hmdd2.0.backup"}
```

## C.3 Exploring and analyzing the miRNA KG

### Similarity between miRNAs via shared targets

Two miRNAs are functionally similar if they share many `Target` nodes — more shared
targets, stronger the implied connection. Computed with GDS's **`nodeSimilarity`** in its
**weighted** version, so higher-confidence `HAS_TARGET.value` scores contribute more:

```cypher
CALL gds.graph.project("MiRNA_Target_similarity", ["Target","MiRNA"],
                        {HAS_TARGET:{properties:["value"]}})
```

```cypher
CALL gds.nodeSimilarity.stream("MiRNA_Target_similarity",
    {relationshipWeightProperty: 'value'})
YIELD node1,node2, similarity
WITH gds.util.asNode(node1) AS source, gds.util.asNode(node2) AS target, similarity
RETURN source.name AS source, target.name AS target, similarity
ORDER BY similarity DESC, source, target
```

Top results included obvious cases (hsa-let-7a-5p / hsa-let-7c-5p, hsa-let-7a-5p /
hsa-let-7e-5p — all let-7 family members) and less obvious ones (hsa-mir-107 /
hsa-mir-103a-3p, hsa-mir-570-5p / hsa-mir-548ai), all at similarity 1.0; literature search
confirmed some less-obvious pairs are discussed together for diseases like osteoarthritis
and cystic fibrosis.

### Similarity between Disease and Target entities

Since miRNAs regulate gene expression by interfering with specific mRNAs, and abnormal
regulation can cause disease, it's reasonable to ask how similar a target mRNA is to a
disease by how many miRNAs the two share — comparing **different entity types** (`Disease`
and `Target`) using cross-dataset information. This uses **filtered** `nodeSimilarity` to
restrict comparison to Disease–Target pairs specifically:

```cypher
CALL gds.graph.project("Disease_Target_similarity", ["Target","MiRNA","Disease"],
                       {HAS_TARGET:{orientation:"UNDIRECTED"},
                        RELATED_TO:{orientation:"UNDIRECTED"},
                        SIMILAR_TO:{orientation:"UNDIRECTED"}})
```

```cypher
CALL gds.nodeSimilarity.filtered.stream("Disease_Target_similarity",
    {sourceNodeFilter:"Disease",targetNodeFilter:"Target"})
yield node1,node2, similarity
WITH gds.util.asNode(node1) AS source, gds.util.asNode(node2) AS target, similarity
MATCH (source)-[]-(m:MiRNA)-[:HAS_TARGET]-(target)
WITH source, target, similarity, count(m) as miRNAs
WHERE miRNAs > 10
RETURN source.name AS source, target.name AS target, similarity, miRNAs
ORDER BY similarity DESCENDING, source, target
```

Top result: *meningioma* and target *NM_203347* share 11 miRNAs (similarity 0.0476); a
follow-up traversal (`Disease <- MiRNA -> Target`) shows almost all miRNAs associated with
NM_203347 are also related to meningioma. Such findings need not be medically significant
alone, but represent usable structure for a downstream ML algorithm.

### Degree-weighted path count (DWPC) for disease-to-target relevance

The same **degree-weighted path count (DWPC)** metric used elsewhere in the book (chapter
4, with Hetionet) finds relevant paths from a disease to a target, penalizing paths through
highly connected ("hub") nodes so popularity alone doesn't bias ranking. Reference disease:
**celiac disease** (chosen so the authors could independently evaluate plausibility).

```cypher
MATCH path = (d:Disease)<-[:REGULATES|RELATED_TO]-(m)-[:HAS_TARGET]->(t)
WHERE d.name = "celiac disease"
WITH
[
  size([(d)<-[:REGULATES|RELATED_TO]-() | d]),
  size([()<-[:REGULATES|RELATED_TO]-(m) | m]),
  size([(m)-[:HAS_TARGET]->() | m]),
  size([()-[:HAS_TARGET]->(t) | t])
] AS degrees, path, d, t
WITH d.name as disease_name, t.name as target_name, count(path) as PC,
sum(reduce(pdp = 1.0, d in degrees| pdp * d ^ -0.4)) AS DWPC,
  size([(t)-[:HAS_TARGET]-() | t]) AS n_miRNA
WHERE n_miRNA >= 5 and PC >= 2
RETURN disease_name, target_name, PC, DWPC, n_miRNA
ORDER BY DWPC desc
LIMIT 10
```

Selected results (celiac disease → target, by DWPC descending):

| Target | PC | DWPC | # miRNA |
|---|---|---|---|
| NM_080601 | 2 | 0.00417 | 25 |
| NM_001224 | 2 | 0.00322 | 111 |
| NM_032982 | 2 | 0.00318 | 114 |
| NM_152617 | 2 | 0.00295 | 136 |
| NM_032983 | 2 | 0.00278 | 160 |
| NM_198926 | 3 | 0.00241 | 158 |

The top result, NM_080601, is protein tyrosine phosphatase non-receptor type 11 (PTPN11);
external research links this family to immune system regulation and chronic intestinal
inflammation, plausible for celiac disease. Targets 2, 3, and 5 are all variants of caspase
2 (CASP2); single-cell RNA-seq of gluten-specific T cells found marked upregulation of
apoptosis-related genes (FAS, TRAIL, CASP2) in tetramer-positive cells, supporting
activation-induced cell death of gluten-specific T cells as a candidate therapeutic
mechanism. No easy-to-access literature connects celiac disease to the remaining targets,
though active research may eventually surface such links. A final traversal query retrieves
all paths between celiac disease and NM_080601 directly, showing the two independent miRNA
bridges (`Disease <-RELATED_TO- MiRNA -HAS_TARGET-> Target`) that produced PC=2.

## Takeaways

- **Curate before you scale**: start KG construction from a small, task-relevant dataset
  set rather than ingesting everything; noise in loosely-related data and reconciliation
  cost against the existing graph can outweigh the benefit of "more data."
- **`MERGE` is the mechanism for cross-source fusion**: since `MERGE` matches on identity
  properties (e.g., `name`) instead of always creating new nodes, importing multiple
  datasets onto the same node accumulates knowledge from independent sources — this is what
  lets a link-prediction model see one miRNA tied to brain, heart, and autoimmune disease
  simultaneously.
- **Entity normalization is a prerequisite for correctness, not a nice-to-have**: unresolved
  naming variants (three spellings of Burkitt lymphoma) silently fragment the graph and
  bias link prediction toward false negatives; scispaCy + UMLS resolves this via semantic
  type filtering (`banned` vs. `full` type lists) and canonical CUI lookup, preserving
  original nodes via a `REPRESENTS` edge to a `NormalizedDisease` node for auditability.
- **Measure normalization's effect with WCC and APSP**, not just intuition — APSP distance
  distributions (distance-1 pairs up ~4.5%, longer distances down to −100%) directly
  predict better message-passing-based embeddings, since embedding quality depends on
  shorter, cleaner connections between semantically related nodes.
- **Different relationship types preserve provenance**: `RELATED_TO` vs. `REGULATES` for
  different source datasets keeps dataset-specific meaning visible in query results while
  still allowing later merging during modeling.
- **Similarity spans node types**: `nodeSimilarity` (plain or `filtered`, weighted or
  unweighted) can compare Disease against Target using shared MiRNA connections as the
  bridge, surfacing cross-dataset structure useful for ML.
- **DWPC generalizes beyond Hetionet** to any KG needing hub-penalized path relevance
  scoring — applied here to rank plausible disease-to-target-mRNA relationships for celiac
  disease, with independently verifiable results (PTPN11, CASP2 variants) validating it.
