---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 3: Create your first knowledge graph from ontologies"
confidence: high
cleaned: 2026-07-29
---

# Ch 3 — Create your first knowledge graph from ontologies

## Chapter scope

This chapter covers selecting the best KG technology based on use cases, constructing a
KG to support clinicians' activities, and performing analysis and ontology-based reasoning
on top of a KG.

KG construction is complex because it requires extracting and integrating information from
sources that differ in format (XML, CSV, JSON), storage technology (relational or
document-oriented), information syntax (e.g., `2022-08-09` vs `9 August 2022`), and
especially the *meaning* of the data. In healthcare, varied expressions that identify the
same concept (type 2 diabetes vs. ketosis-resistant diabetes), identical acronyms that
define distinct concepts (PE as physical examination or pulmonary embolism), and
information granularity (necrosis vs. lobular necrosis) are obstacles to data integration.

The goal of building a KG is a unified, well-grounded, meaningful representation of data
from various sources, where individual pieces of information are integrated into a coherent
view. A common strategy for addressing semantic heterogeneity is to adopt one or more
**ontologies** as a reference schema and vocabulary for incoming data. An ontology "lets you
model data using a standard vocabulary that includes elements such as formal names,
properties, categories, and relationships between entities described within the data."

The ontology acts as an intermediary between semantically heterogeneous information. A
**mapping** bridges a data source's local schema to the ontology's reference schema. Each
data element can be mapped to concepts expressed by the ontology; these annotations bring
together data elements from different origins.

This chapter builds a KG using a reference ontology, focusing on helping clinicians identify
rare diseases, using the **Human Phenotype Ontology** (HPO; https://hpo.jax.org/app/) and an
HPO-annotated dataset. HPO provides information about the connections between diseases and
their associated phenotypic abnormalities — observable physical or biochemical
characteristics that deviate from typical human traits and may result from genetic
mutations, environmental influences, or a combination of both.

The chapter's mental model follows a subset of the CRISP-DM phases introduced in chapter 2:
business understanding → data understanding → data preparation → KG model
creation/update. The pipeline: the HPO ontology and HPO annotations are ingested/processed
separately, then integrated into the KG's unified representation, which clinicians or
applications can then query directly.

## Business and domain understanding

The target persona of the KG is the **clinician** — a healthcare professional who diagnoses
and treats diseases. One of the clinician's most complex activities is correctly identifying
a disease based on symptoms (phenotypic traits), particularly for rare syndromes.

Beyond prescribing tests, the clinician can use a structured knowledge base of available
information. It should have two features:

- *A contextual description of the phenotype domain* — for instance, phenotypic anomalies
  related to the same organs or systems should be explicitly connected.
- *Data describing the relationship between phenotypic anomalies and diseases* — this
  information must be tracked so clinicians can access the sources of the connections.

**Definitions given in the chapter:**

> **DEFINITION** The *phenotype* of an individual with a disease can be said to be the sum
> of all of the phenotypic features manifested by that individual [1].

> **DEFINITION** A *disease* is an entity characterized by (1) a set of causes for a
> specific condition, (2) a time course, (3) a group of phenotypic features, and (4)
> characteristic response to a particular treatment.

Example: the common cold is characterized by distinct phenotypic features, including fever
and fatigue. Its time course ranges from a couple of days to a week, and treatments such as
aspirin can support healing.

The clinician's work also involves gray areas. Diabetes mellitus, for instance, can be
classified either as a disease or as a phenotypic characteristic of other rare syndromes.
**Type 1 diabetes mellitus** can be considered either a disease or a phenotypic feature —
based on context, two different IDs are adopted to distinguish between the two cases:
`OMIM:222100` (disease) and `HP:0100651` (phenotypic feature). This use case (handling that
kind of uncertainty) drives the rest of the chapter.

## Data understanding

The data source is the **HPO repository**, which provides two sets of information:

1. **`hpo.owl`** — an RDF/XML ontology file containing standardized information on
   phenotypic anomalies (http://purl.obolibrary.org/obo/hp.owl). This standardization
   enables interoperability and lets us integrate data from multiple sources. The file is
   serialized in **Turtle** (Terse RDF Language) in the book's listings for readability.
2. **`phenotype.hpoa`** — a tab-separated-values (TSV) annotation file linking diseases to
   phenotypic features, discovered/recognized in the scientific literature.

### hpo.owl example (Turtle)

```turtle
obo:HP_0100651 a owl:Class ;    #1
    rdfs:label "Type I diabetes mellitus" ^^xsd:string ;
    obo:IAO_0000115 "A chronic condition in which the pancreas produces
        little or no insulin…" ^^xsd:string ;
    oboInOwl:created_by "doelkens"^^xsd:string ;   #2
    oboInOwl:creation_date "2010-12-29T06:37:55Z"^^xsd:string ;
    oboInOwl:hasDbXref "MSH:D003922"^^xsd:string,  #3
        "SNOMEDCT_US:46635009" ^^xsd:string,
        "UMLS:C0011854" ^^xsd:string ;
    oboInOwl:hasExactSynonym "Diabetes mellitus Type I"^^xsd:string,
        "Juvenile diabetes mellitus" ^^xsd:string,
        "Type 1 diabetes",
        "Type I diabetes";
    oboInOwl:hasRelatedSynonym "Insulin-dependent diabetes
        mellitus"^^xsd:string ;
    oboInOwl:id "HP:0100651"^^xsd:string ;
    rdfs:comment "The onset of type 1 diabetes is typically during
        adolescence…" ^^xsd:string ;
    rdfs:subClassOf obo:HP_0000819 .   #5
```

Annotations: #1 defines Type I diabetes mellitus, identified by URI `obo:HP_0100651`, as an
ontology class; #2 describes the disease in natural language; #3 shows metadata about the
entry's author ("doelkens"); #4 gives IDs of external data sources referencing this form of
diabetes; #5 defines Type I diabetes mellitus as a subclass of the phenotypic feature
identified by `obo:HP_0000819`, which corresponds to diabetes mellitus.

Reading an OWL file directly can be challenging, so the chapter uses the **`rdflib`** Python
library to explore it as a collection of **triples** (subject, predicate, object).

```python
from rdflib import Graph, URIRef
g = Graph()
g.parse("hp.owl", format="xml")

g.bind("obo", "http://purl.obolibrary.org/obo/")
g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
g.bind("xsd", "http://www.w3.org/2001/XMLSchema#")

subject_uri = URIRef("http://purl.obolibrary.org/obo/HP_0100651")
filtered_statements = g.triples((subject_uri, None, None))
for subject, predicate, obj in filtered_statements:
  print(
        f"({g.qname(subject)}, {g.qname(predicate)}, "
        f"{g.qname(obj) if isinstance(obj, URIRef) else obj})"
    )
  print()
```

Output as a set of triples (truncated for clarity):

```
(obo:HP_0410050, rdf:type, owl:Class)

(obo:HP_0410050, owl:equivalentClass, N25507ac984704bd78a0effd951947a7f)

(obo:HP_0410050, rdfs:subClassOf, obo:HP_0011013)

(obo:HP_0410050, obo:IAO_0000115, A decrease in the level of…)

(obo:HP_0410050, dc:date, 2018-01-27T00:26:24+00:00)

(obo:HP_0410050, dcterms:creator, ns1:0000-0001-5208-3432)

(obo:HP_0410050, oboInOwl:hasExactSynonym, Decreased level of 1,5-AG…)

(obo:HP_0410050, oboInOwl:hasExactSynonym, Decreased level of 1,5-anhydro…)

(obo:HP_0410050, rdfs:label, Decreased level of 1,5 anhydroglucitol in serum)
```

### phenotype.hpoa fields

The `phenotype.hpoa` TSV collects recognized, discovered, and annotated phenotypic features
associated with different diseases, including rare syndromes. Annotations include modifiers
clarifying the age of onset and frequency of each feature.

```
database_id  disease_name  qualifier  hpo_id  reference  evidence
onset  frequency  sex  modifier  aspect  biocuration

OMIM:222100  Diabetes mellitus, insulin-dependent-1
    HP:0410050  PMID:9357814;PMID:17659063;PMID:16731998
    PCS  30/30      P
    HPO:NicoleVasilevsky[2018-02-23];HPO:NicoleVasilevsky[2018-03-02]

OMIM:222100  Diabetes mellitus, insulin-dependent-1
    HP:0000103  OMIM:222100
    IEA         P  HPO:iea[2009-02-17]
```

Fields:

- `database_id` (`OMIM:222100`) — disease identifier from ontologies such as Online
  Mendelian Inheritance in Man (OMIM) and Orphanet.
- `disease_name` (`Diabetes mellitus, insulin-dependent-1`) — disease name from the related
  ontology.
- `hpo_id` (`HP:0410050`) — HPO identifier of the related phenotypic abnormality.
- `reference` (`PMID:9357814;PMID:17659063;PMID:16731998`) — source of information used for
  the annotation, possibly a PubMed ID (PMID).
- `evidence` (`PCS`) — level of evidence supporting the annotation. PCS stands for
  published clinical study.
- `frequency` (`30/30`) — a count of patients affected within a group sharing a common
  statistical characteristic; `30/30` means 30 of 30 patients with the disease were found to
  have the phenotypic abnormality referred to by the HPO term.
- `aspect` (`P`) — phenotypic aspect; P means phenotypic abnormality.
- `biocuration` (`HPO:NicoleVasilevsky[2018-02-23];HPO:NicoleVasilevsky[2018-03-02]`) —
  research center or user making the annotation and the date the annotation was made.

## Understanding knowledge graph technologies

Two of the most popular approaches for creating KGs are the **Resource Description
Framework (RDF)** and **Labeled Property Graph (LPG)**.

- **RDF** is a standard framework, defined and regulated by the World Wide Web Consortium
  (W3C), for exchange on the web. Each statement is a **triple**: subject, predicate,
  object. The subject is a node (vertex), the predicate represents a relationship (edge),
  and the object is another node. RDF models a KG as a collection of statements, and web
  technologies can be used to represent, store, and exchange information. RDF is
  particularly suitable for creating ontologies that describe a specific domain of
  knowledge.
- **LPG** provides fast, query-based traversal of graph data and path analysis. Efficiency
  of data storage and access is guaranteed by structured information in the form of
  key–value pairs associated with nodes and relationships in the graph.

In RDF, relationships (predicates) are defined globally, so metadata applied to a predicate
affects all instances of that relationship throughout the graph. To address this limitation,
RDF supports **named graphs**, which let us treat groups of triples as a single entity and
provide context-specific information. In contrast, LPG supports unique edges between nodes,
allowing metadata and properties to be attached to individual relationships — a flexible
model for edge-specific information. The RDF-DEV Community Group is working on an
**RDF\*** ("RDF-star") specification that lets users add properties to edges, reconciling RDF
and LPG technologies.

LPG can't express the advanced semantics of RDF. To address this, vendors such as Neo4j
provide tools to reduce the gap between RDF and LPG. The **Neosemantics** plugin lets you
use RDF and its vocabularies (OWL, RDFS, SKOS, and others) in Neo4j to run basic inference.
Other vendors, such as Amazon Neptune, use alternative strategies that let you execute
Cypher queries (the LPG query language) on RDF data.

### RDF or LPG? A goal-driven discussion

To select the best technology, you need a clear understanding of the available information
(the HPO ontology and annotations data) and a clear goal. RDF is particularly suitable for
creating ontologies — that's why the HPO ontology file is serialized in RDF (`.owl`
extension). **OWL** stands for Web Ontology Language, and its primary goal is to enrich the
semantic information available in RDF to support expressive class definitions and property
definitions. OWL ontologies are widely used, and many LLMs, including GPT and Claude, have
been trained on them, making it easier for these models to interpret and reason over
OWL-based data.

The clinicians in the example use case don't care how the knowledge is modeled: they're
interested in an unambiguous representation of phenotypic features, possibly in a
hierarchical structure. The core information in the annotated data comes from scientific
literature and consists of cases in which a specific phenotypic feature is identified with a
disease — e.g., the connection between "Diabetes Mellitus, Insulin-dependent-1"
(`OMIM:222100`) and "Decreased level of 1,5 anhydroglucitol in serum" (`HP:0410050`) was
published in a clinical study titled "A kinetic mass balance model for
1,5-anhydroglucitol: applications to monitoring of glycemic control" [3] (PMID: 9357814),
created by Nicole Vasilevsky in February 2018. The best way to model this is to incorporate
these details into a **relationship** between a disease and a phenotypic feature — modeling
data this way lets you create multiple relationships, each potentially representing a
specific annotation characterized by a provenance and date.

Converting from a table row (in the annotations file) to a KG edge: the disease and the
phenotypic feature become nodes, and information about the annotation author, creation date,
and source becomes properties of the edge (`HAS_PHENOTYPIC_FEATURE`).

**Exercise (from the text)**: select the best technology to support clinicians' activities,
given these requirements:

- The clinician's goal is to use available data to make informed decisions when diagnosing
  diseases, especially rare pathologies.
- Clinicians are not interested in a knowledge base representing the entire clinical
  domain. They want to see cases in which anomalous phenotypic features (or combinations)
  can be associated with diseases that are not easy to detect. They want information that
  reports such cases, including the provenance and date of the information.
- Using this metadata, clinicians want to easily compare all the cases in which a specific
  phenotypic feature is associated with a disease.

There is no unique right answer, but selecting the most suitable technology helps you reach
your goals more straightforwardly.

### Representing edge properties with RDF and LPG

From the book's point of view, **LPG is the best solution** for representing this data,
since it emphasizes information about an edge connecting a phenotypic feature and a disease.
The chapter compares RDF mechanisms against LPG to justify this.

**RDF: n-ary relations.** A standard approach for modeling data related to a specific edge
is to create a new concept ("annotation") that connects the data.

```turtle
_:Annotation rdf:type :PhenotypicAnnotation ;
    :forDisease       OMIM:222100 ;
    :phenotypicFeature HP:0410050 ;
    :source           PMID:9357814 ;
    :createdBy        "Nicole Vasilevsky" ;
    :creationDate     "2018-02-23"^^xsd:date .
```

This snippet represents a phenotypic annotation using Turtle syntax. The annotation is a
**blank node** (`_:Annotation`) — an unnamed resource used to group related information
without assigning it a global identifier, like an anonymous object in programming. The
blank node is typed as a `:PhenotypicAnnotation` and links a disease (OMIM ID) to a
phenotypic feature (HPO). Additional metadata includes the data source (PubMed ID), the
author, and the creation date. This structure supports provenance tracking and semantic
interoperability in biomedical datasets.

```sparql
SELECT ?source ?author ?date
WHERE {
    ?annotation a :PhenotypicAnnotation ;
        :forDisease OMIM:222100 ;
        :phenotypicFeature HP:0410050 ;
        :source ?source ;
        :createdBy ?author ;
        :creationDate ?date .
}
```

This SPARQL query retrieves metadata about a specific phenotypic annotation: it filters
annotations by a given disease (`OMIM:222100`) and phenotypic feature (`HP:0410050`), then
returns the source, author, and creation date. In many cases, data consumers can easily
interpret and adapt to changes in the original schema. However, as the ontology evolves, its
complexity may increase, introducing challenges related to backward compatibility and
long-term maintenance.

**RDF: named graphs.** Named graphs add a fourth element specifying that a statement
belongs to a named (sub)graph, itself treatable as a node of the RDF graph, letting you
attach new statements to the annotation data.

```trig
:Graph1 {
    OMIM:222100 :hasPhenotypicFeature HP:0410050 .
}

:Graph1
    :source PMID:9357814 ;
    :createdBy "Nicole Vasilevsky" ;
    :creationDate "2018-02-23"^^xsd:date .
```

This uses **TriG** syntax to define the named graph `:Graph1`. TriG lets you group RDF
statements under a label (the named graph) and add metadata. Here, the triple asserts that
disease `OMIM:222100` has the phenotypic feature `HP:0410050`; metadata about this assertion
(source, creator, creation date) is attached to `:Graph1`.

```sparql
SELECT ?source ?author ?date
WHERE {
    GRAPH :Graph1 {
        OMIM:222100 :hasPhenotypicFeature HP:0410050 .
    }
    :Graph1 :source ?source ;
            :createdBy ?author ;
            :creationDate ?date .
}
```

This query looks in graph `:Graph1` to find the triple asserting `OMIM:222100` has phenotype
`HP:0410050`, then queries metadata about `:Graph1` and returns source, author, and creation
date. Although named graphs are powerful for representing contextual metadata and
provenance, they can add complexity — managing a large number of named graphs may lead to
inefficiencies in data storage and exchange, and fine-grained updates to individual
statements in named graphs can be challenging.

**RDF-star.** RDF-star is an extension of RDF that narrows the gap between RDF and property
graph models such as LPG.

```turtle
<<OMIM:222100 :hasPhenotypicFeature HP:0410050>>
    :source PMID: 9357814 ;
    :createdBy "Nicole Vasilevsky" ;
    :creationDate "2018-02-23"^^xsd:date .
```

```sparql
SELECT ?source ?author ?date {
    <<OMIM:222100 :hasPhenotypicFeature HP:0410050>>
        :source ?source ;
        :createdBy ?author ;
        :creationDate ? date .
}
```

RDF-star represents a step forward in attaching properties to edges and uses a more
readable SPARQL query. However, its query performance must be improved; as noted by Orlandi
et al. [2]:

> "The use of a new syntax extension requires a specific implementation of RDF engines and,
> therefore, limits the adoption of this approach."

Other methods exist for annotating RDF statements, such as **reification** and **singleton
properties**. These are less used in real-world applications, where more scalable and
maintainable alternatives like named graphs and n-ary relations are preferred.

**LPG.** The LPG approach represents annotation details directly within the relationship,
using key–value pairs.

```cypher
(d { id: "OMIM:222100" })
-[:HAS_PHENOTYPIC_FEATURE {
        source: "PMID:9357814",
        createdBy: "Nicole Vasilevsky",
        creationDate: "2018-02-23"}]->
(p { id: "HP:0410050" })
```

The two nodes represent entities: a disease (`OMIM:222100`) and a phenotype (`HP:0410050`).
The relationship `:HAS_PHENOTYPIC_FEATURE` connects them and includes key–value pairs
describing the source of the annotation (`PMID:9357814`), the creator (`Nicole Vasilevsky`),
and the date it was created (`2018-02-23`).

```cypher
MATCH (d)-[r:HAS_PHENOTYPIC_FEATURE]->(p)
WHERE d.id = "OMIM:222100" and p.id = "HP:0410050"
RETURN r.source, r.createdBy, r.creationDate
```

This Cypher query retrieves the metadata attached to the `:HAS_PHENOTYPIC_FEATURE`
relationship between the disease and phenotype nodes. It matches the pattern in the graph,
filters based on the node IDs, and returns the annotation details stored in the
relationship.

As these examples demonstrate, the LPG model is well-suited for modeling metadata-rich
relationships in a way that is expressive and accessible. **For these reasons, the chapter
adopts LPG and Cypher as the core tools for building its KG system.**

## Building a knowledge graph

Building the KG has two steps: loading the ontology, and ingesting a data source using the
ontology as a reference. Code is available in the GitHub repository
(https://github.com/alenegro81/knowledge-graphs-and-llms-in-action/tree/main/chapters/ch03)
and can be tested via Cypher queries in the Neo4j browser. The chapter's code was tested
using Neo4j version 5.20.0 Enterprise Edition (Neo4j Desktop 1.6.1), APOC library (5.20.0),
and the Neosemantics plugin (5.20.0). Results are derived from the HPO version available in
February 2025.

### Ontology ingestion and processing with Neosemantics

First, create and initialize the HPO database:

```cypher
CREATE DATABASE hpo IF NOT EXISTS
```

Next, establish constraints ensuring uniqueness of the `uri` and `id` properties of nodes
labeled `Resource`, and create indexes for the `id` properties of `HpoPhenotype` and
`HpoDisease` nodes to speed up the KG-building phase and information retrieval. The
`HpoPhenotype` and `HpoDisease` labels define the phenotypic abnormality and disease nodes.

```cypher
CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Resource) REQUIRE (n.id) IS UNIQUE;
CREATE INDEX disease_id IF NOT EXISTS FOR (n:HpoDisease) ON (n.id);
CREATE INDEX phenotype_id IF NOT EXISTS FOR (n:HpoPhenotype) ON (n.id);
```

Then define an initial configuration for the Neosemantics component:

```cypher
CALL n10s.graphconfig.init();
CALL n10s.graphconfig.set({ handleVocabUris: "IGNORE" });
CALL n10s.graphconfig.set({ applyNeo4jNaming: True });
```

This configuration sets two main import rules: (1) ignore namespaces during import (namespaces
help keep track of distinct ontologies using similar expressions), and (2) encode
relationship types in uppercase, following the standard LPG relationship-naming convention.

Load the HPO vocabulary:

```cypher
CALL n10s.rdf.import.fetch("http://purl.obolibrary.org/obo/hp.owl","RDF/XML")
```

During the authors' tests, this command loaded **899,558 statements** into Neo4j. Before
processing and loading the annotation data, enrich the loaded nodes with the `HpoPhenotype`
label and an `id` property computed from the resource's original URI:

```cypher
MATCH (n:Resource)
WHERE n.uri STARTS WITH "http://purl.obolibrary.org/obo/HP"
SET n:HpoPhenotype,
    n.id = coalesce(n.id,
      replace(apoc.text.replace(n.uri,'(.*)obo/','') ,'_', ':'))    #1
```

`#1` sets `n.id` as `HP:0000001` (i.e., converts the OBO-style URI suffix into the
colon-delimited HPO ID format).

To view a small portion of the graph so far (works only if run step-by-step, not after the
full ingestion/cleaning pipeline — the final cleaning phase removes the intermediate
structure this query depends on):

```cypher
MATCH path1=(n:HpoPhenotype)<-[:SUBCLASSOF]-(m:HpoPhenotype)
WHERE n.label = "Diabetes mellitus"
WITH path1
MATCH path2=(i:HpoPhenotype)<-[:ANNOTATEDSOURCE]-(j)
WHERE i.label in ["Diabetes mellitus", "Type I diabetes mellitus"]
WITH path1, path2, j
MATCH path3=(j)-[:ANNOTATEDPROPERTY|HASSYNONYMTYPE]-()
RETURN path1, path2, path3
```

The HPO ontology provides different types of information: ontological information about the
nature of the nodes, and domain-specific hierarchical connections related to diabetes
mellitus.

### Annotation ingestion and processing

The `phenotype.hpoa` file (HPO annotation format, HPOA) is a TSV, unlike the RDF-based
`hpo.owl`. It includes:

- An explicit association between a disease and multiple phenotypic features or
  abnormalities.
- Evidence supporting the association (e.g., inferred from an electronic annotation, or from
  a published clinical study or traceable author statement).
- The age of onset.
- The frequency with which a disease and a phenotypic feature appear together.
- Additional metadata describing the ontology source.

Create disease nodes (skipping the first 5 metadata rows):

```cypher
LOAD CSV FROM 'https://mng.bz/qRyr' AS row
FIELDTERMINATOR '\t'
WITH row
SKIP 5      #1
MERGE (dis:Resource:HpoDisease {id: row[0]})
ON CREATE SET dis.label = row[1];
```

Create relationships between disease nodes and phenotypic feature nodes:

```cypher
LOAD CSV FROM 'https://mng.bz/qRyr' AS row
FIELDTERMINATOR '\t'
WITH row
SKIP 5
MATCH (dis:HpoDisease)
WHERE dis.id = row[0]
MATCH (phe:HpoPhenotype)
WHERE phe.id = row[3]
MERGE (dis)-[:HAS_PHENOTYPIC_FEATURE]->(phe)
```

Creating these relationships integrates information from both `hpo.owl` and
`phenotype.hpoa`. Query the result of this integration:

```cypher
MERGE (dis:HpoDisease)-[:HAS_PHENOTYPIC_FEATURE]->(phe:HpoPhenotype)
RETURN dis.label, collect(phe.label)
LIMIT 3
```

Sample results (Table 3.1: sample associations between `HpoDisease` and `HpoPhenotype`
nodes):

| HpoDisease entry | Associated HpoPhenotype entries |
|---|---|
| Developmental and epileptic encephalopathy 96 | Hydrops fetalis, Autosomal dominant inheritance, Death in infancy, Epileptic spasm, Primary microcephaly, EEG with burst suppression, Intellectual disability, profound, Small for gestational age, Epileptic encephalopathy, Neonatal respiratory distress, Tonic seizure |
| Pseudohyperkalemia, familial, 2, due to red cell leak | Generalized muscle weakness, Hyperkalemia, Periodic paralysis, Muscle spasm, Hemolytic anemia, Hand tremor, Autosomal dominant inheritance |
| Immunoglobulin kappa light chain deficiency | Chronic diarrhea, Recurrent infections, Recurrent respiratory infections, Absent circulating immunoglobulin kappa chain, Childhood onset, Diarrhea, Autosomal recessive inheritance |

Add relationship properties as key–value pairs, resiliently (only setting a property if the
corresponding TSV column is not null, avoiding overwriting values with nulls):

```cypher
LOAD CSV FROM 'https://mng.bz/qRyr' AS row
FIELDTERMINATOR '\t'
WITH row
SKIP 5
MATCH (dis:HpoDisease)-[rel:HAS_PHENOTYPIC_FEATURE]->(phe:HpoPhenotype)
WHERE phe.id = row[3] and dis.id = row[0]
FOREACH(_ IN CASE WHEN row[4] is not null THEN [1] ELSE [] END|
  SET rel.source = row[4])
FOREACH(_ IN CASE WHEN row[5] is not null THEN [1] ELSE [] END|
  SET rel.evidence = row[5])
FOREACH(_ IN CASE WHEN row[6] is not null THEN [1] ELSE [] END|
  SET rel.onset = row[6])
FOREACH(_ IN CASE WHEN row[7] is not null THEN [1] ELSE [] END|
  SET rel.frequency = row[7])
FOREACH(_ IN CASE WHEN row[8] is not null THEN [1] ELSE [] END|
  SET rel.sex = row[8])
FOREACH(_ IN CASE WHEN row[9] is not null THEN [1] ELSE [] END|
  SET rel.modifier = row[9])
FOREACH(_ IN CASE WHEN row[10] is not null THEN [1] ELSE [] END|
  SET rel.aspect = row[10])
FOREACH(_ IN CASE WHEN row[11] is not null THEN [1] ELSE [] END|
  SET rel.biocuration = row[11])
```

Each `FOREACH` block adds a new property to the relationship only if the corresponding
column in the TSV is not null; this makes the script resilient to missing data.

Then enrich `HAS_PHENOTYPIC_FEATURE` with human-readable derived properties, using
`apoc.periodic.iterate` to process updates in batches:

```cypher
CALL apoc.periodic.iterate(
  "MATCH (dis:HpoDisease)-[rel:HAS_PHENOTYPIC_FEATURE]->(phe:HpoPhenotype)
   RETURN rel",
  "SET rel.createdBy = apoc.text.regexGroups(
      rel.biocuration, 'HPO:(\\w+)\\['
    )[0][1],
  rel.creationDate = apoc.text.regexGroups(
      rel.biocuration, '\\[(\\d{4}-\\d{2}-\\d{2})\\]'
    )[0][1],
  rel.aspectName = CASE
    WHEN rel.aspect = 'P' THEN 'Phenotypic abnormality'
    WHEN rel.aspect = 'I' THEN 'Inheritance'
  END,
  rel.aspectDescription = CASE
    WHEN rel.aspect = 'P' THEN
      'Terms with the P aspect are located in the Phenotypic abnormality ' +
      'subontology'
    WHEN rel.aspect = 'I' THEN
      'Terms with the I aspect are from the Inheritance subontology'
  END,
  rel.evidenceName = CASE
    WHEN rel.evidence = 'IEA' THEN
      'Inferred from electronic annotation'
    WHEN rel.evidence = 'PCS' THEN
      'Published clinical study'
    WHEN rel.evidence = 'TAS' THEN
      'Traceable author statement'
  END,
  rel.evidenceDescription = CASE
    WHEN rel.evidence = 'IEA' THEN
      'Annotations extracted by parsing the Clinical Features sections ' +
      'of the Online Mendelian Inheritance in Man resource are assigned ' +
      'the evidence code IEA.'
    WHEN rel.evidence = 'PCS' THEN
      'PCS is used for information extracted from articles in the medical ' +
      'literature. Generally, annotations of this type will include the ' +
      'pubmed id of the published study in the DB_Reference field.'
    WHEN rel.evidence = 'TAS' THEN
      'TAS is used for information gleaned from knowledge bases such as ' +
      'OMIM or Orphanet that have derived the information from a ' +
      'published source.'
  END,
  rel.url = CASE
    WHEN rel.source STARTS WITH 'PMID:' THEN
      'https://pubmed.ncbi.nlm.nih.gov/' + apoc.text.replace(
        rel.source, '(.*)PMID:', ''
      )
    WHEN rel.source STARTS WITH 'OMIM:' THEN
      'https://omim.org/entry/' + apoc.text.replace(
        rel.source, '(.*)OMIM:', ''
      )
  END",
  {batchSize: 1000}
)
```

This query extracts the curator and creation date from the `biocuration` property via regex,
and adds `aspectName`/`aspectDescription`/`evidenceName`/`evidenceDescription`/`url`
properties to improve human readability during graph exploration — translating the file's
abbreviated codes (`P`/`I` for aspect; `IEA`/`PCS`/`TAS` for evidence) into descriptive text.

Finally, clean the KG by removing nodes/relationships that came from the ontology but are
not needed for this purpose:

```cypher
CALL apoc.periodic.iterate(
    "MATCH (n:Resource) RETURN id(n) as id",
    "MATCH (n)
     WHERE id(n) = id AND
           NOT 'HpoPhenotype' in labels(n) AND
           NOT 'HpoDisease' in labels(n)
     DETACH DELETE n",
    {batchSize:10000})
YIELD batches, total return batches, total
```

## Querying the data

Clinicians can use the KG as a support tool for diagnosing rare diseases, starting from
detected phenotypic abnormalities in a patient.

**Worked scenario**: a clinician examines a boy affected by Type 1 diabetes. The patient's
clinical history is stored in the hospital's EHR. The hospital has embraced the KG paradigm
change, so patient information is stored using HPO/OMIM terms. Type 1 diabetes is classified
as both a phenotypic feature and a disease, so it's stored with two different identification
codes:

- `HP:0100651` (phenotypic feature): https://hpo.jax.org/app/browse/term/HP:0100651
- `OMIM:222100` (disease): https://www.omim.org/entry/222100

The clinician wants to see the typical phenotypic features of Type 1 diabetes already in the
KG:

```cypher
MATCH path=(dis:HpoDisease)-[:HAS_PHENOTYPIC_FEATURE]->(phe:HpoPhenotype)
WHERE dis.id = "OMIM:222100"
RETURN path
```

The central node is Type 1 diabetes; the other nodes are its associated phenotypic
features: Diabetes mellitus, Polyuria, Autoimmunity, Polyphagia, Decreased level of 1,5
anhydroglucitol in serum, Ketoacidosis, Hyperglycemia, Polydipsia.

During the exam, the clinician recognizes **new** symptoms classified as phenotypic
features that are *not* directly connected to Type 1 diabetes in the KG:

- Growth delay: https://hpo.jax.org/app/browse/term/HP:0001510
- Large knee: https://hpo.jax.org/app/browse/term/HP:0030866
- Sensorineural hearing impairment: https://hpo.jax.org/app/browse/term/HP:0000407
- Pruritus: https://hpo.jax.org/app/browse/term/HP:0000989

The clinician wants to identify other pathologies connected to these phenotype features:

```cypher
MATCH (phe:HpoPhenotype)
WHERE phe.label IN [
  "Growth delay",
  "Large knee",
  "Sensorineural hearing impairment",
  "Pruritus",
  "Type I diabetes mellitus"
]
WITH phe
MATCH path=(dis:HpoDisease)-[HAS_PHENOTYPIC_FEATURE]->(phe)
UNWIND dis as nodes
RETURN
  dis.id as disease_id,
  dis.label as disease_name,
  collect(phe.label) as features,
  count(nodes) as num_of_features
ORDER BY num_of_features DESC, disease_name
LIMIT 5
```

Results (Table 3.2 — top diseases matching clinician-identified phenotypic features):

| disease_id | disease_name | features | num_of_features |
|---|---|---|---|
| OMIM:619269 | Ondontochondrodysplasia 2 with hearing loss and diabetes | Growth delay, Sensorineural hearing impairment, Pruritus, Large knee, Type I diabetes mellitus | 5 |
| OMIM:618500 | Holoprosencephaly 12 with or without pancreatic agenesis | Sensorineural hearing impairment, Growth delay, Type I diabetes mellitus | 3 |
| OMIM:614700 | 3-methylglutaconic aciduria, type VIII | Growth delay, Sensorineural hearing impairment | 2 |
| OMIM:616192 | Alobar holoprosencephaly | Growth delay, Sensorineural hearing impairment | 2 |
| OMIM:602782 | Alpha-Thalassemia/mental retardation syndrome, X-linked | Growth delay, Sensorineural hearing impairment | 2 |

These results point to a diagnosis of **Ondontochondrodysplasia 2 with hearing loss and
diabetes**. From here, the clinician can investigate further to determine the frequency with
which these phenotypic features are associated with the disease and identify more potential
sources of information.

**Exercise (from the text)**: extend the query in listing 3.26 to retrieve relationship
properties including `evidence_name`, `evidence_description`, `source`, and `url`.

## Reasoning over the KG

One of the most powerful tools of a KG is **inference**, using deductive reasoning based on
logical rules to derive results from implicit information. Example question: *which
diseases are characterized by an abnormality of the endocrine system?*

Some annotations are explicitly connected to this phenotypic feature, but a clinician would
also be interested in more specific phenotypic traits involving, e.g., the thyroid. This
requires the **hierarchical representation** of HPO (its subclass structure). The following
query retrieves phenotype nodes that are subclasses (up to 3 levels deep) of endocrine
system abnormalities (`id=HP:0000818`):

```cypher
MATCH (p:HpoPhenotype)<-[:SUBCLASSOF*1..3]-(n:HpoPhenotype)    #1
WHERE p.id = "HP:0000818"
RETURN p,n
```

`#1` finds all phenotype nodes (`n`) that are one to three subclass levels more specific
than another phenotype node (`p`).

Using this hierarchical structure, you can infer annotations implicitly linked to
abnormalities of the endocrine system via a Neosemantics inference procedure:

```cypher
MATCH (cat:HpoPhenotype {label: "Abnormality of the endocrine system"})   #1
CALL n10s.inference.nodesInCategory(cat, {
  inCatRel: "HAS_PHENOTYPIC_FEATURE",
  subCatRel: "SUBCLASSOF"})   #2
YIELD node as dis
WHERE dis.label IN [
  "Congenital atransferrinemia",
  "Deafness, autosomal recessive 4, with enlarged vestibular aqueduct",
  "Diabetes mellitus, transient neonatal, 1",
  "Edema, familial idiopathic, prepubertal",
  "Familial dysalbuminemic hyperthyroxinemia"
]    #3
MATCH (dis)-[:HAS_PHENOTYPIC_FEATURE]->(phe:HpoPhenotype)   #4
RETURN dis.label as disease, collect(DISTINCT phe.label) as features
ORDER BY size(features) ASC, disease
```

Annotations: `#1` finds the top-level phenotype node; `#2` gets diseases linked (directly or
indirectly) to this phenotype via `n10s.inference.nodesInCategory`, which walks the
`SUBCLASSOF` hierarchy under `inCatRel`/`subCatRel` parameters; `#3` restricts to selected
diseases for reproducible output; `#4` matches their phenotype features.

Sample results (Table 3.3 — subset of annotations implicitly connected to "Abnormality of
the endocrine system"; features that are direct or inferred subclasses of this phenotypic
feature are noted in **bold** in the book):

| disease | features |
|---|---|
| Congenital atransferrinemia | Anemia, Abnormality of the pancreas, Recurrent infections, Arthritis, Abnormality of the cardiovascular system, **Hypothyroidism** |
| Deafness, autosomal recessive 4, with enlarged vestibular aqueduct | Enlarged vestibular aqueduct, Congenital onset, **Goiter**, Autosomal recessive inheritance, Incomplete partition of the cochlea type II, Sensorineural hearing impairment |
| Diabetes mellitus, transient neonatal, 1 | **Transient neonatal diabetes mellitus**, Autosomal dominant inheritance, Dehydration, Hyperglycemia, Intrauterine growth retardation, Severe failure to thrive |
| Edema, familial idiopathic, prepubertal | **Diabetes mellitus**, Abnormality of the genitourinary system, Irritability, Vomiting, Autosomal dominant inheritance, Edema |
| Familial dysalbuminemic hyperthyroxinemia | **Abnormal circulating free T4 concentration**, **Abnormal thyroid-stimulating hormone level**, Autosomal dominant inheritance, Autosomal recessive inheritance, **Euthyroid hyperthyroxinemia**, **Increased circulating free T4 concentration** |

These results demonstrate how reasoning over subclass relationships and phenotypic features
can reveal meaningful disease associations within an ontology-driven graph. The use of the
Neosemantics plugin highlights the power of semantic inference in enriching biomedical
queries, enabling you to go beyond direct connections and tap into the structure of domain
knowledge.

## Takeaways

- An **ontology** (standard vocabulary of formal names, properties, categories, relationships)
  plus per-source **mappings** is the standard mechanism for resolving semantic heterogeneity
  across data sources when building a KG — this is the intermediary strategy used throughout
  the chapter.
- RDF and LPG solve different problems: RDF (triples: subject–predicate–object) is
  purpose-built for exchange and *ontology definition* (hence HPO ships as `.owl`/RDF), while
  LPG (key–value properties on nodes *and* edges) is purpose-built for fast, expressive
  traversal and edge-level metadata (provenance, source, date). Global predicate semantics is
  RDF's core limitation for edge metadata; named graphs, n-ary relations, RDF-star,
  reification, and singleton properties are all workarounds with real tradeoffs (complexity,
  performance, non-standard tooling) — none is as direct as LPG's native edge properties.
  Choose based on the concrete query/metadata goal, not on ideology.
  Choose based on the concrete query/metadata goal, not on ideology.
- Neo4j's **Neosemantics** (`n10s`) plugin bridges RDF and LPG: it can import an OWL/RDF
  ontology directly into LPG nodes/relationships (`n10s.rdf.import.fetch`) and run
  ontology-aware inference (`n10s.inference.nodesInCategory`) over LPG-native subclass
  hierarchies (`SUBCLASSOF`).
- A disease can simultaneously be an ontology **disease** entity and a **phenotypic feature**
  of another disease (e.g., Type 1 diabetes: `OMIM:222100` vs. `HP:0100651`) — the same
  real-world concept needs two IDs depending on the modeling context; this ambiguity must be
  handled explicitly rather than collapsed.
  handled explicitly rather than collapsed.
- Practical ingestion pattern demonstrated: create DB → constraints/indexes → configure
  Neosemantics import rules (`handleVocabUris: IGNORE`, `applyNeo4jNaming: True`) → bulk-load
  ontology RDF → label/derive IDs on loaded nodes → `LOAD CSV` the annotation TSV to
  create disease nodes and `HAS_PHENOTYPIC_FEATURE` relationships → enrich relationship
  properties conditionally (`FOREACH` + null checks) → derive human-readable fields via
  `apoc.periodic.iterate` + regex → clean up ontology scaffolding nodes not needed downstream.
- **Inference over subclass hierarchies** (e.g., "abnormality of the endocrine system" →
  goiter, hypothyroidism, abnormal T4 levels) surfaces disease associations that direct
  queries miss — this is the concrete payoff of choosing an ontology-grounded KG over a flat
  annotation table.
