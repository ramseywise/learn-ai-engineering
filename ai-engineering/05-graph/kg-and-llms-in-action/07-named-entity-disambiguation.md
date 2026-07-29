---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 7: Named entity disambiguation"
confidence: high
cleaned: 2026-07-29
---

# Ch 7 — Named Entity Disambiguation

## From recognition to disambiguation

Natural language processing (NLP) plays a critical role in the automatic construction of
knowledge graphs (KGs) from unstructured data. **Named entity recognition (NER)**
identifies mentions of relevant named entities in raw text and assigns them to predefined
categories (people, organizations, locations, diseases). NER alone does not give a precise
understanding of text in an application domain — it doesn't resolve which specific
real-world entity a mention refers to.

Motivating example: an intelligent advisory system (IAS) for healthcare stakeholders needs
**interactivity** — the ability to exchange information with humans through multiple
interactions. This requires: (1) detecting meaningful entities in natural language, and
(2) retrieving information about these entities from different knowledge sources. NER
inference alone can't provide these features.

Example text (ECDC weekly bulletin):

> In the week of 13 April, Belize reported for the first time mosquito-borne Zika virus
> transmission. Update on the observed increase of congenital Zika syndrome and other
> neurological complications Microcephaly and other fetal malformations potentially
> associated with Zika virus infection.

The term *Zika* appears three times with different meanings depending on context: the
first mention refers to a *virus* entity, the second and third both refer to a *disease*
entity — but they are not necessarily the same disease. It is important to distinguish the
traditional Zika disease/infection (third mention) from its congenital form (second
mention). This distinction can be straightforward for a domain expert but becomes
impractical at document-collection scale.

**Named entity disambiguation (NED)** is the NLP task that addresses this: it
automatically removes the uncertainty or ambiguity of the meaning of a term by examining
the context of each mention and connecting that mention to an entity in a knowledge base
(a **ground entity** and its reference knowledge base). Example: *Congenital Zika virus
infection* is a distinct entity in the Unified Medical Language System (UMLS), separate
from *Zika virus* and *Zika virus infection* (also both in UMLS).

Each UMLS entity has a **concept unique identifier (CUI)**, a semantic type, and a set of
definitions, broader concepts, and narrower concepts sourced from datasets like MeSH and
the National Cancer Institute (NCI) thesaurus.

By mapping "Zika" mentions to UMLS entities, both IAS requirements are satisfied: entity
detection, and (implicitly) the ability to explore contextual knowledge from multiple
biomedical ontologies starting from the disambiguated entity. Medical ontologies define
connections between entities — sometimes trivially (e.g., *Zika virus* is the
`CAUSATIVE_AGENT` of both syndromes), sometimes less trivially (e.g., Campylobacter
infection and AIDS connect because the first affects the intestine like a specific form of
the second, known as *AIDS with intestinal malabsorption*).

## Understanding named entity disambiguation

Knowledge bases collect structured representations of entities in a specific domain. NED
systems link text mentions to the correct KB entity through three primary phases:

1. **Candidate selection** — identifies the best candidates for a recognized named entity
   mention, performed against an existing knowledge base with useful structural
   information, enabling precise identification of different entities.
2. **Candidate ranking** — assigns a score to each candidate based on contextual
   information (words surrounding the recognized entity). The entity that achieves the
   best score represents the **target entity** of the detected mention.
3. **Ontology integration** — enriches the target entity representation by aggregating
   information from multiple ontologies, feeding a knowledge graph.

**scispaCy** is a Python-based library used for disambiguating named entities. Its model
can recognize named entities, select candidates against a knowledge base, and rank
candidates to identify the target entity.

```python
import spacy
from scispacy.linking import EntityLinker

nlp = spacy.load("en_core_sci_md")
nlp.add_pipe("scispacy_linker",
             config={"resolve_abbreviations": True, "linker_name": "umls"})

linker = nlp.get_pipe("scispacy_linker")
linker_dict = linker.kb.cui_to_entity

doc = nlp("""In the week of 13 April, Belize reported for the first time
mosquito-borne Zika virus transmission. Update on the observed increase
of congenital Zika syndrome and other neurological complications
Microcephaly and other fetal malformations potentially associated with
Zika virus infection.""")
for ent in doc.ents:
  if "Zika" in ent.text:
    print("Recognized entity:", ent.text, ent.start_char, ent.end_char)
  print("Ranked target candidates:")
  for kb_ent in ent._.kb_ents:
    print('-', linker_dict[kb_ent[0]][0], linker_dict[kb_ent[0]][1])
```

Results (candidates ranked by scispaCy model score, first result = best):

```
Recognized entity: Zika virus 75 85
Ranked target candidates:
- C0318793 Zika Virus                     #1 (best)
- C0276289 Zika Virus Infection
- C4687930 Zika Virus Antibody Measurement

Recognized entity: congenital Zika syndrome 135 159
Ranked target candidates:
- C4546023 Congenital Zika Syndrome       #2 (best)

Recognized entity: Zika virus infection 268 288
Ranked target candidates:
- C0276289 Zika Virus Infection           #3 (best)
- C0318793 Zika Virus
- C4687930 Zika Virus Antibody Measurement
```

A different UMLS entity ID is correctly associated with each of the three "Zika" mentions,
producing annotated text where each detected entity is linked to the UMLS knowledge base.

### Ontology integration

The final step before the extracted information can be used is **ontology integration**:
incorporating knowledge from domain ontologies where the structural and contextual
information of extracted entities is integrated into a unique KG. UMLS provides
terminology, classification, and coding standards from multiple sources, enabling
interoperable biomedical information systems.

Sample UMLS entity file entry (`MRCONSO.RRF`):

```
C0276289|ENG|S|L0388876|VC|S0517846|Y|A2985635|8552019|3928002||SNOMEDCT_US|PT|3928002|Zika virus disease|9|N|256|
C0276289|ENG|P|L13115709|PF|S16069662|N|A27369917||C128423||NCI|PT|C128423|Zika Virus Infection|0|N|256|
C0276289|ENG|S|L0392793|VW|S16069660|Y|A26676017||M000613823|D000071243|MSH|ET|D000071243|Zika Fever|0|N|256|
```

Key fields (left to right): entity ID, ontology, and the name associated with the entity
ID in that ontology. The UMLS ID for *Zika Virus Infection* maps to ID `3928002` from the
SNOMEDCT_US ontology, one of whose names is *Zika virus disease*.

**SNOMEDCT_US (SNOMED)** — Systematized Nomenclature of Medicine — is one of the most
comprehensive, multilingual clinical terminologies, encompassing more than 450,000
concepts, with a rich set of relationship types (e.g., `CAUSATIVE_AGENT`, `FINDING_SITE`).

SNOMED description file sample (entity names):

```
84087010    20020131  1  900000000000207008  50471002
    en      900000000000013009             Zika virus         900000000000017005

8552019     20020131  1  900000000000207008  3928002
    en      900000000000013009             Zika virus disease  900000000000017005
```

SNOMED edge/relationship file sample (triples):

```
769900023   20020131  1  900000000000207008
    3928002        50471002       0      246075003
    900000000000011006            900000000000451002
```

Triple elements: source ID for *Zika virus disease* (3928002), target ID for *Zika virus*
(50471002), relationship ID representing *Causative agent* (246075003).

By incorporating external ontologies, the NED model's output becomes the entry point for
exploring and discovering information, letting analysts bridge unstructured and structured
knowledge in a unified view.

**Exercise (from the text)**: the Zika example shows a single term referring to distinct
entities depending on context. The opposite also occurs — different terms referring to the
same entity (e.g., "AIDS" and "Acquired Immunodeficiency Syndrome"). The KG models both
directions: the `DISAMBIGUATED_TO` relationship connects distinct mention strings to a
shared entity, or one mention string to distinct entities based on context.

## Domain-based NED and LLMs

To test whether a general LLM can replace dedicated NED tooling, the authors ran a simple
ChatGPT experiment using the Zika example text with the prompt: "Disambiguate all the
medical entities you can detect."

ChatGPT's output was a flat list of surface terms (Zika virus, Mosquito-borne
transmission, Congenital Zika syndrome, Neurological complications, Microcephaly, Fetal
malformations) — it did **not** distinguish that the first "Zika" mention refers to a
virus entity while the last refers to the virus infection. When asked, "Can you assign
UMLS ids to these extracted entities?", ChatGPT responded:

> As an AI language model, I am not able to assign UMLS ids to extracted entities.
> However, UMLS Metathesaurus is a biomedical and health ontological resource that
> provides normalized names and mappings to concepts in various biomedical ontologies. It
> can be used to map extracted entities to their corresponding UMLS concepts and obtain
> their unique identifiers (UMLS ids). This requires domain-specific knowledge and
> expertise in utilizing the UMLS resources.

The critical finding: the **UMLS knowledge base is not incorporated in the ChatGPT
model**. This confirms that domain-specific NED + KG technologies must be combined with
LLMs to add value in critical, high-precision domains like healthcare — LLMs alone are not
sufficient (note also that ChatGPT is a continuously evolving generative model, so results
vary run to run).

## Business and domain understanding

Real-world scenario: standards and regulations for managing **substances of human origin
(SoHO)** — blood, tissues, cells, and organs (**BTC**) used in medical therapies (blood
transfusions, kidney transplants, gametes/IVF). KG technology addresses this via
representation flexibility and harmonization of multiple sources in a unified view. The
chapter's mental model follows a specification of CRISP-DM adapted to KGs (introduced in
chapter 2): business understanding → data understanding → data preparation → KG model
creation/update → analysis (SoHO use cases).

### Context

Patient safety during blood transfusion, transplantation, and medically-assisted
reproduction is a critical healthcare-domain concern. From substance donation to the
patient application, BTC components pass through stages: donor evaluation, procurement,
processing/storage, quality control/release criteria, packaging/distribution,
traceability, biovigilance, and application to patients. Each stage has its own
characteristics (e.g., donor evaluation involves general criteria, donor characteristics,
exclusion criteria; biovigilance covers unforeseen events, adverse reactions, residual
effects).

The BTC sector depends on citizen donations, with availability significantly reduced
during public health crises (e.g., COVID-19). A legal framework is needed that is
"effectively implemented, future proof, crisis resistant and agile enough" (quoted from
source) to provide requirements continuously as risks and technology evolve.

In 2022, the European Commission (EC) proposed a regulation on SoHO standards and quality
for human applications, built on the expertise of the **European Centre for Disease
Prevention and Control (ECDC)** and the **European Directorate for the Quality of
Medicines & HealthCare (EDQM)**:

- **ECDC** — short reports on health surveillance, responses to health threats, emerging
  trends, and SoHO safety.
- **EDQM** — detailed guidelines on quality/safety issues beyond communicable-disease
  transmission risk; technical standards for BTC collection, processing, storage, and
  distribution.

### Use case definition

Scenario: a health policy officer must identify guidelines and possible risks related to
transplantation of pancreatic islets (islets of Langerhans), while in parallel analyzing
the spread of Zika virus in a region. NED + KG technologies support four capabilities:

- **Conceptual search** — a retrieval method finding information based on meaning rather
  than exact keywords. Reconciles different expressions referring to the same entity
  (e.g., "pancreatic islets" and "islets of Langerhans") or distinguishes entities with
  similar names but different meanings.
- **Structured knowledge-based search** — retrieves information by using formalized
  ontology knowledge to create nontrivial relationships between pieces of text across
  multiple documents (e.g., navigating ontology paths to find disorders caused by
  diabetes and retrieve all documents mentioning them).
- **KG-based interpretability and discovery** — relationships/paths in the ontology can
  reflect essential information in the text (*interpretability* — why entities co-occur)
  or provide insights via connections not obvious from the text alone (*discovery*). E.g.,
  type 1 diabetes (T1D) and islets of Langerhans co-occur because T1D affects the islets
  (interpretability); AIDS and T1D can co-occur because pathologies associated with T1D
  can involve the immune system (discovery).
- **Uncovering new knowledge** — when co-occurring entities are not yet connected in
  ontologies but relevant knowledge exists in guidelines/documents (e.g., the pancreatic
  islets entity mentioned alongside SoHO-management info not yet formalized), or when
  stakeholders want to correlate communicable and non-communicable diseases (COVID-19 and
  diabetes mellitus) across ECDC bulletins in a graph-based view.

## Understanding the data

Building the IAS requires integrating heterogeneous information from various repositories
into a unified source, combining unstructured and semantically structured data.

### Unstructured data

Document types processed:

- Impact assessment reports in the BTC field and related regulatory proposals — outline
  the political/legal context, revise legislation, discuss BTC supply interruptions and
  new diseases/tech developments, analyze policy options, propose regulations.
- Reports on stakeholders' positions on the regulation proposal — position papers, lessons
  learned, general comments. Example: the International Society for Stem Cell Research
  (ISSCR) raised concerns about unproven cellular therapies and businesses making
  unsubstantiated clinical-effectiveness claims, and suggested EU expert bodies harmonize
  standards with international norms and simplify guidance consultations.
- Guidelines and newsletters for SoHO management from the EDQM — e.g., "Guide to the
  Quality and Safety of Tissues and Cells for Human Application," providing minimum
  standards aligned with EU directives, best practices, scientific knowledge, expert
  opinions, and international project results.
- Reports and bulletins from the ECDC monitoring infectious-disease progress — weekly
  communicable disease threat reports (CDTRs) consolidating epidemic-intelligence data,
  worldwide conditions, and epidemiology changes relevant to Europe.

### Domain ontologies

Ontologies serve as the reference schema for integrating different sources (chapter 3
background). This scenario uses **UMLS**, **SNOMED**, and **HPO**.

**UMLS** is a meta-thesaurus composed of multiple controlled vocabularies in the
biomedical domain, providing a mapping structure among these vocabularies to simplify
translation between terminology systems (2022AA version used in examples). Two key files:

- `MRCONSO.RRF` — biomedical entity names from multiple vocabularies; each name includes
  the entity ID it comes from.
- `MRSTY.RRF` — semantic types categorizing UMLS entities.

Both use pipe (`|`) delimiter-separated values (DSV), processable like CSV. Sample
`MRSTY.RRF`:

```
C0022131|T023|A1.2.3.1|Body Part, Organ, or Organ Component|AT19674993|256|
C0011311|T047|B2.2.1.2.1|Disease or Syndrome|AT41932582|256|
C0018681|T184|A2.2.2|Sign or Symptom|AT17679733|256|
```

Other ontology/vocabulary sources referenced: SNOMED, Foundational Model of Anatomy (FMA),
Read Codes (RC), Medical Subject Headings (MSH), ICPC2/ICD10ENG, HPO.

**SNOMED** provides >450,000 concepts and relationship types, downloadable under the UMLS
free license. Version used: released 2022-09-01. Two files:

- `sct2_Description_Full-en_US1000124_20220901.txt` — entity names/aliases and
  relationship-defining terms.
- `sct2_Relationship_Full_US1000124_20220901.txt` — triples (plus metadata) defining all
  relationships between SNOMED entities, using numerical codes.

Both use TSV format. In the relationship file, entities like *Islets of Langerhans*,
*Dengue Fever*, and *Cephalgia* appear as **target** entities of an `IS_A` relationship
(ID `116680003`), with source entities *Endocrine pancreas cell*, *Dengue hemorrhagic
fever*, and *Posttraumatic headache*, respectively.

**Human Phenotype Ontology (HPO)** is released as an RDF/XML file (`hpo.owl`) containing
standardized information on phenotypic anomalies. Example (Turtle-serialized) for type 1
diabetes (T1D):

```turtle
obo:HP_0100651 a owl:Class ;
    rdfs:label "Type I diabetes mellitus" ;
    obo:IAO_0000115 "A chronic condition in which the pancreas produces
        little or no insulin..." ;
    oboInOwl:hasDbXref "MSH:D003922", "SNOMEDCT_US:46635009", "UMLS:C0011854" ;
    oboInOwl:hasExactSynonym "Diabetes mellitus Type I", "Juvenile diabetes
        mellitus", "Type 1 diabetes", "Type I diabetes" ;
    oboInOwl:hasRelatedSynonym "Insulin-dependent diabetes mellitus" ;
    oboInOwl:id "HP:0100651" ;
    rdfs:comment "The onset of type 1 diabetes is typically during
        adolescence..." ;
    rdfs:subClassOf obo:HP_0000819 .
```

This defines T1D as an ontology class, describes it in natural language, records
authorship/creation metadata, lists cross-references to external data sources (MSH,
SNOMEDCT_US, UMLS), and declares it a subclass of the phenotypic feature `HP_0000819`
(diabetes mellitus).

## Building a SoHO knowledge graph

Constructing the KG and developing use cases on top of it involves five steps:

1. Define the KG schema.
2. Process and ingest documents.
3. Disambiguate and ingest medical entities.
4. Process, load, and map ontologies.
5. Generate co-occurrence relationships.

Two paths through the chapter: build the full KG from scratch (all five steps), or start
from an intermediate version with documents already processed via scispaCy (skip to
loading ontologies and mapping extracted entities). Full code is in the book's repository.

### Defining the schema

The KG schema's main node labels and relationships:

- `File` —[`CONTAINS_PAGE`]→ `Page` — SoHO files and their pages.
- `Page` —[`MENTIONS_ENTITY`]→ `EntityMention` — all recognized entities in the text.
- `EntityMention` —[`DISAMBIGUATED_TO`]→ `MedicalEntity` — resolves mentions to entities.
  This relationship models both directions of ambiguity: the same string mapping to
  different entities in different contexts (e.g., "Zika"), and different strings mapping
  to the same entity (e.g., "AIDS" / "Acquired Immunodeficiency Syndrome").
- `Page` —[`MENTIONS_ENTITY`]→ `MedicalEntity` — direct link from page to disambiguated
  entity.
- `MedicalEntity` —[`IS_SNOMED_ENTITY`]→ `SnomedEntity`
- `MedicalEntity` —[`IS_HPO_ENTITY`]→ `HpoEntity`
- `MedicalEntity` —[`IS_DISEASE_ENTITY`]→ `HpoDiseaseEntity`
- `SnomedEntity` —[`SNOMED_RELATION`]→ `SnomedEntity`
- `HpoDiseaseEntity` —[`HAS_PHENOTYPIC_FEATURE`]→ `HpoEntity`
- `MedicalEntity` —[`COOCCUR`]→ `MedicalEntity`

Nodes/relationships fall into two groups: those resulting from the NED process (mentions
and disambiguated entities extracted from text), and those from imported ontologies
(connected to the disambiguated medical entities).

### Processing and ingesting documents

Most source documents are PDF or DOCX. Raw content is extracted using the **Amazon
Textract** OCR service (AWS, automatically extracts text/handwriting/data from scanned
documents), then reconstructed via Python scripts handling different document structures
(one-column vs. two-column). OCR produces a JSON file per document, including bounding
boxes for each extracted text line; text processing aggregates lines at the page level.

```python
class DocsImporter:
    def set_constraints(self):
        queries = ["CREATE FULLTEXT INDEX pageText FOR (n:Page) ON EACH [n.text]"]
        for q in queries:
            self.connection.query(q, db=self.db)

    def load_docs(self):
        with open(self.docs_file) as json_file:
            docs = json.load(json_file)

        query = """
            MERGE (f:File {id: $name})
            SET f.type = $type, f.path = $name
            WITH f

            UNWIND $pages as page
            MERGE (p:Page {id: replace($name, '.pdf', '') + '_' + page.page_idx})
            SET p.page_idx = page.page_idx,
                p.text = page.text

            MERGE (f)-[:CONTAINS_PAGE]->(p)
            """

        for i in tqdm(docs):
            name = i['name']
            type = i['type']
            pages = i['pages']
            self.connection.query(query,
                                   parameters={'name': name, 'type': type, 'pages': pages},
                                   db=self.db)
```

### Disambiguating and ingesting medical entities

Documents are processed directly from the OCR JSON, results stored in a Python
dictionary, then loaded into Neo4j:

```python
{'id': 'sample_dataset-PublicUse/ECDC Documents/west nile virus/EU-summary-report-trends-sources-zoonoses-2013_120',
 'ents': [{'sentenceIndex': 0,
    'value': 'zoonoses',
    'lemma': 'zoonosis',
    'label': 'ENTITY',
    'beginCharacter': 60,
    'endCharacter': 68,
    'selected_ned_id': 'C0043528',
    'selected_ned_name': 'Zoonoses',
    'selected_ned_definition': 'Diseases of non-human animals that may be
        transmitted to HUMANS or may be transmitted from humans to non-human
        animals.',
    'selected_ned_aliases': ['Zoonotic Disease', 'Zoonosis, NOS', 'Zoonoses',...],
    'selected_ned_types_id': ['T047'],
    'selected_ned_types': ['Disease or Syndrome']...
}
```

Each entry stores the sentence index, character span (`beginCharacter`/`endCharacter`) of
the mention, and the selected NED result (ID, name, definition, aliases, semantic types) —
used later for advanced queries.

The loading Cypher query (`NLPImporter.load_nlp_res`) performs, per page:

1. Marks the page `:NEDProcessed` to avoid reprocessing.
2. Creates `EntityMention` nodes (normalized/lowercased name) and connects them to `Page`
   via `MENTIONS_MENTION` (storing start/end char offsets, sentence index, entity type).
3. For each entity, merges a `MedicalEntity` node keyed by `selected_ned_id`, enriching it
   with name, type IDs/types, original mention, definition, aliases, and character/
   sentence spans.
4. Connects `EntityMention` → `MedicalEntity` via `DISAMBIGUATED_TO` (storing a confidence
   score).
5. Connects `Page` → `MedicalEntity` directly via `MENTIONS_ENTITY`.

Both `EntityMention` and disambiguated `MedicalEntity` nodes are kept in the graph to
improve representational flexibility.

### Processing, loading, and mapping ontologies

UMLS is the entry point for accessing information across multiple biomedical ontologies,
so SNOMED and HPO are loaded first and then mapped to UMLS via each entity's `umls_ids`.

**Ingesting SNOMED relationships** — constraints/indexes are created (uniqueness on
`SnomedEntity.id`; indexes on name and on `SNOMED_RELATION` id/type/umls), then
relationships are imported from the triples file:

```python
class SnomedRelationshipsImporter(BaseImporter):
    def import_snomed_rels(self):
        query = """
            UNWIND $batch as item
            MERGE (e1:SnomedEntity {id: item.sourceId})
            MERGE (e2:SnomedEntity {id: item.destinationId})
            MERGE (e1)-[:SNOMED_RELATION {id: item.typeId}]->(e2)
            FOREACH(ignoreMe IN CASE WHEN item.typeId = '116680003'
                THEN [true] ELSE [] END|
              MERGE (e1)-[:SNOMED_IS_A]->(e2)
            )
            """
```

SNOMED includes hundreds of relationship types; to keep the schema simple, all are
represented as a single `SNOMED_RELATION` relationship type with the actual relation name
stored as a `type` property. A separate `SNOMED_IS_A` relationship type is created
explicitly for hierarchical connections (`typeId = '116680003'`) so that hierarchy
traversal is easy and can propagate information from root to leaf nodes.

**Ingesting SNOMED names/aliases** from the description file, propagating relationship
`type` and node `aliases`:

```python
class SnomedNamesImporter(BaseImporter):
    def import_snomed_names(self, snomedNames_file):
        snomed_names_concepts_query = """
        UNWIND $batch as item
        MATCH (e1:SnomedEntity)
        -[r:SNOMED_RELATION {id: item.conceptId}]->
        (e2:SnomedEntity)
        WHERE item.conceptId <> '116680003' AND r.id = item.conceptId
        SET r.type = CASE
                WHEN r.type IS NULL THEN item.termAsType
                ELSE r.type END,
            r.aliases = CASE
                WHEN item.termAsType IN r.aliases THEN r.aliases
                ELSE coalesce(r.aliases,[]) + item.termAsType END
        """

        snomed_names_entities_query = """
        UNWIND $batch as item
        MATCH (e:SnomedEntity {id: item.conceptId})
        SET e.name = CASE
                WHEN e.name IS NULL THEN item.term
                ELSE e.name END,
            e.aliases = CASE
                WHEN item.term in e.aliases THEN  e.aliases
                ELSE coalesce(e.aliases, []) + item.term END
        """
```

**Propagating semantic types from first-level nodes.** SNOMED's first-level nodes (direct
children of the SNOMED root, via the `IS_A` hierarchy) represent archetypal entity types
in the medical domain — diseases, body structures, substances, events. These define the
semantic types of SNOMED entities, but this typing is *implicit* — for every other entity
there are only names/aliases in the raw data, no explicit type. A propagation mechanism
transfers the first-level type down the hierarchy tree so deep entities (e.g.,
*Ecallantide* under *Pharmaceutical product*, *Retinopathy associated with AIDS* under
*Disease*) can be typed correctly:

```python
class SnomedLabelPropagator():
    def get_rows(self):
        propagation_query = """
        MATCH p=(n:SnomedEntity)<-[:SNOMED_IS_A]-(m:SnomedEntity)
        WHERE n.id= "138875005" // Root node
        WITH distinct m as first_node

        CALL apoc.path.expandConfig(first_node, {
                relationshipFilter: '<SNOMED_IS_A',
                minLevel: 1,
                maxLevel: -1,
                uniqueness: 'RELATIONSHIP_GLOBAL'
            }) yield path

        UNWIND nodes(path) as other_level
        WITH first_node, collect(DISTINCT other_level) as uniques
            UNWIND uniques as unique_other_level
            WITH first_node,unique_other_level
            WHERE not first_node.name in coalesce(unique_other_level.type,[])

            RETURN unique_other_level.id as id, first_node.name as label
        """
```

Uses `apoc.path.expandConfig` to traverse the `SNOMED_IS_A` hierarchy from each first-level
node down to all descendants, then propagates the first-level node's name as a `type`
label on every descendant that doesn't already have it.

**Ingesting HPO.** The HPO ontology is imported via the Neosemantics (n10s) plugin:

```cypher
CALL n10s.rdf.import.fetch("http://purl.obolibrary.org/obo/hp.owl","RDF/XML");
```

Phenotypic-feature nodes get the `HpoEntity` label and a normalized `id`:

```cypher
MATCH (n:Resource)
WHERE n.uri STARTS WITH "http://purl.obolibrary.org/obo/HP"
SET n:HpoEntity,
 n.id = coalesce(n.id, replace(apoc.text.replace(n.uri,'(.*)obo/',''),'_', ':'))
```

Disease entities and phenotype–disease relationships are loaded from the HPO annotation
file (`phenotype.hpoa`) via `LOAD CSV` (tab-delimited, skipping the first 5 header rows),
creating `HpoDiseaseEntity` nodes and `HAS_PHENOTYPIC_FEATURE` relationships to `HpoEntity`
nodes.

**Mapping disambiguated entities to ontologies via UMLS:**

```cypher
MATCH (m:MedicalEntity)
WITH m
MATCH (d:SnomedEntity)
WHERE m.id in d.umls_ids
WITH m, d
MERGE (m)-[:IS_SNOMED_ENTITY]->(d)
```

An analogous query connects `MedicalEntity` to `HpoDiseaseEntity` via `IS_DISEASE_ENTITY`
using `umls_ids` on the HPO annotation-derived nodes.

### Generating entity co-occurrences

Identifying co-occurrences of medical entities in text is fundamental for advanced use
cases combining unstructured content with structured ontology knowledge. **Co-occurrence**
is defined as: the projection of `Page` nodes onto `Entity` nodes.

```cypher
CALL apoc.periodic.iterate(
  "MATCH (n:Page) WHERE exists( (n)-[:MENTIONS_ENTITY]->(:MedicalEntity) )
  RETURN n",
  "MATCH (n)-[r:MENTIONS_ENTITY]->(m:MedicalEntity)
  WITH n, r.sentence_index as sentences, m
  UNWIND sentences as sentence
  WITH n, sentence, collect(distinct m) as entities

  UNWIND range(0, size(entities)-2) as i
  UNWIND range(i+1, size(entities)-1) as j

  WITH n, sentence, entities, i, j
  MATCH (m1) WHERE id(m1) = id(entities[i])
  MATCH (m2) WHERE id(m2) = id(entities[j])

  WITH n, sentence, entities, i, j, m1, m2
  MERGE (m1)-[s:COOCCURR]-(m2)
  ON CREATE SET s.count = 1,
      s.sentences = [sentence]
  ON MATCH SET s.count = s.count + 1,
   s.sentences = s.sentences + sentence",
  {batchSize: 50})
```

For every page, entities mentioned in the same sentence are paired up and connected with a
`COOCCUR` relationship, incrementing a `count` and accumulating the sentence indices where
the co-occurrence happened. This query produced more than **25,000 relationships** in the
example KG.

## KG-based use cases

Four use cases demonstrated with Cypher against the built KG:

### 1. Conceptual search

A full-text search for "breakbone fever" (a colloquial synonym for dengue fever, UMLS ID
`C0011311`) against indexed page text:

```cypher
CALL db.index.fulltext.queryNodes("PageText", "breakbone fever")
YIELD node, score
WITH node as p, score as score
MATCH (f:File)-[:CONTAINS_PAGE]->(p)
RETURN f.id as `File ID`, p.page_idx as `Page index`, score as Score
LIMIT 5
```

Since "breakbone" never literally appears in the text, full-text fuzzy matching latches
onto "fever" instead and returns high-scoring but largely irrelevant pages. Conceptual
search instead resolves "breakbone fever" as an **alias** of the disambiguated dengue
entity (`C0011311`) and searches for actual mentions of that entity:

```cypher
MATCH (f:File)-[:CONTAINS_PAGE]->(p)
      -[r:MENTIONS_MENTION]->(m)-[:DISAMBIGUATED_TO]->(e)
WHERE "breakbone fever" IN [x IN e.aliases | toLower(x)]

UNWIND range(0, size(r.start_chars) - 1) AS mention
WITH f, p, e, m, r, mention
RETURN DISTINCT
  f.id AS `File ID`,
  p.page_idx AS `Page index`,
  apoc.text.join(
    collect(
      substring(
        p.text,
        apoc.coll.max([r.start_chars[mention] - 100, 0]),
        r.end_chars[mention] - r.start_chars[mention] + 200
      )
    )[0..3],
    '\n\n'
  ) AS `Mention contexts`,
  size(collect(m.name)) AS `Number of mentions`
ORDER BY `Number of mentions` DESC
LIMIT 5
```

Comparing results: the top full-text-search page appears only 19th in the conceptual
search results. The full-text top hit has 17 mentions of the UMLS entity, while the
conceptual-search top hit has 22 mentions. Conceptual search returns more precise,
detailed information — document path, page index, the actual matched text span, and
mention counts — improving explainability and enabling precise debugging of NED-model
misfires. It also disambiguates polysemous terms in-context, e.g. "islands" vs. "islets of
Langerhans," filtering irrelevant land-mass hits while broadening the search to synonymous
expressions like "pancreatic islets."

### 2. Structured knowledge-based search

Retrieves information by using ontology-formalized knowledge to build nontrivial
cross-document relationships. Example: find text mentioning diseases that can affect the
*islets of Langerhans*, via the SNOMED `FINDING_SITE` relationship:

```cypher
MATCH (m1:MedicalEntity)-[:IS_SNOMED_ENTITY]->(s1:SnomedEntity)
<-[r1:SNOMED_RELATION]-(s2:SnomedEntity)
<-[:IS_SNOMED_ENTITY]-(e:MedicalEntity)
WHERE m1.name = "Islets of Langerhans" AND r1.type = "FINDING_SITE"
WITH e
MATCH path = (f:File)-[:CONTAINS_PAGE]->(p)
-[r:MENTIONS_MENTION]->(m)-[:DISAMBIGUATED_TO]->(e)
UNWIND range(0, size(r.start_chars) - 1) AS mention
...
```

One notable result: a page from *Guide to the Quality and Safety of Organs for
Transplantation* (7th ed.) mentions *Hyperglycemia*, explicitly connected to *Islets of
Langerhans* via `FINDING_SITE`, in a section on donor-maintenance protocols for a donor
with head trauma — information that would **not** have surfaced via conceptual search
alone, but was reached by using the ontology connection from the *Islets of Langerhans*
starting entity.

Structured search can also chain multiple relationships of the same type across an
ontology path. Example: Zika virus is a Togavirus; find all diseases in the documents
caused by any Togavirus by chaining three `CAUSATIVE_AGENT` hops:

```cypher
MATCH (m1:MedicalEntity)-[:IS_SNOMED_ENTITY]->(s1:SnomedEntity)
-[r1:SNOMED_RELATION*3..3]-(s2:SnomedEntity)
      <-[:IS_SNOMED_ENTITY]-(e:MedicalEntity)
WHERE m1.name = "Zika Virus"
AND all(x IN r1 WHERE x.type = "CAUSATIVE_AGENT")
WITH DISTINCT e

MATCH path = (f:File)-[:CONTAINS_PAGE]->(p)
-[r:MENTIONS_MENTION]->(m)-[:DISAMBIGUATED_TO]->(e)
WITH f, e, collect(p.page_idx) AS pages_list
RETURN DISTINCT
  f.id AS `File ID`,
  pages_list,
  collect(DISTINCT e.name) AS `Mentioned entity`
ORDER BY size(`Mentioned entity`) DESC
LIMIT 5
```

This surfaces documents mentioning diseases (Yellow Fever, Rift Valley Fever, Rubella,
Dengue Fever, Chikungunya Fever) that share no direct connection with Zika virus but do
share the same causative-agent family (Togavirus) — useful for retrieving documents about
related diseases sharing a virus type.

### 3. KG-based interpretability and discovery

Starting from entity co-occurrence within the same sentence, this use case analyzes *how*
entities connect in the ontologies:

- **Interpretability**: the ontology connection explains why entities co-occurred in the
  text, and also validates the co-occurrence. Example: "AIDS" and "Hepatitis" co-occur
  (both listed as infectious-disease risk factors in a blood-donation document); SNOMED
  paths show both connect via `PATHOLOGICAL_PROCESS` → `Infectious disease` →
  `Inflammatory disorder of liver`, confirming the shared-risk-factor relationship.
- **Discovery**: ontology connections reveal information beyond what the co-occurring
  sentence itself states. Example: AIDS is separately related to *Hepatomegaly associated
  with AIDS* (a liver disorder) and to *Lupus hepatitis* (via
  `HAS_DEFINITIONAL_MANIFESTATION` → immune system finding) — new facts not stated in the
  original sentence.

Top entity types co-occurring with "Zika virus" (UMLS `C0318793`):

| Entity Type | # Co-occurrences |
|---|---|
| Geographic Area | 255 |
| Qualitative Concept | 132 |
| Disease or Syndrome | 125 |
| Functional Concept | 106 |
| Finding | 98 |

Geographic Area dominates because bulletins report disease spread by location; the chapter
focuses on Disease or Syndrome as most relevant. Filtering co-occurring diseases and
retrieving context reveals Zika virus co-occurs frequently with *Zika Virus Infection*,
*Dengue Fever*, and *Chikungunya Fever* — all directly explainable via SNOMED (e.g.,
`Zika virus disease -[:CAUSATIVE_AGENT]-> Zika virus`).

**Shortest-path query** between two SNOMED concepts (up to 8 hops), rendering a
pretty-printed path string:

```cypher
MATCH (s1), (s2)
WHERE s1.id = "3928002" AND s2.id = "50471002"
WITH s1, s2, allShortestPaths((s1)-[:SNOMED_RELATION*1..8]-(s2)) AS paths
UNWIND paths AS path
WITH relationships(path) AS path_edges, nodes(path) AS path_nodes
WITH
  [n IN path_nodes | n.name] AS node_names,
  [r IN path_edges | COALESCE(r.type, 'IS_A')] AS rel_types,
  [n IN path_edges | startnode(n).name] AS rel_starts
WITH [i IN range(0, size(node_names) - 1) |
  CASE
    WHEN i = size(node_names) - 1
    THEN '(' + node_names[i] + ')'
    WHEN node_names[i] = rel_starts[i]
    THEN '(' + node_names[i] + ')' + '-[:' + rel_types[i] + ']->'
    ELSE '(' + node_names[i] + ')' + '<-[:' + rel_types[i] + ']-'
  END
] AS string_paths
RETURN DISTINCT apoc.text.join(string_paths, '') AS `Extracted paths`
```

For *Zika virus disease* ↔ *Zika virus*, the shortest path is the direct relationship:
`(Zika virus disease)-[:CAUSATIVE_AGENT]->(Zika virus)`. For *Dengue* ↔ *Zika virus*,
multiple shortest paths exist via shared parent concepts (*Disease due to Flavivirus*,
*Mosquito-borne flavivirus fever*, *Viral disease*, *Togavirus*, *Arthropod-borne
organism*), interpreting the co-occurrence without a direct edge.

This validation approach generalizes to HPO: co-occurrence patterns between phenotypic
features (e.g., *Renal cell carcinoma*, *Leukemia*) and associated disease entities (e.g.,
*von Hippel-Lindau syndrome*, *Colorectal cancer*, *RETINOBLASTOMA*) can be systematically
extracted and validated, enabling identification of clinically relevant
phenotype–disease associations grounded in document-level evidence.

### 4. Uncovering new knowledge

Not all co-occurring entities have direct, meaningful ontology connections — some
knowledge simply hasn't been consolidated into ontologies yet given fast-moving research.
Rather than using the ontology to *enrich* the KG, this use case flips the direction: use
KG co-occurrence patterns (built from text) to *suggest new facts* that could later be
integrated back into the ontology.

Example: *Zika virus* co-occurs heavily with *Guillain-Barré Syndrome* (195 occurrences,
per the top co-occurring diseases table), which — unlike the other top co-occurring
diseases (Dengue Fever, Chikungunya Fever) — is **not a vector-borne disease**, making this
co-occurrence clinically significant and potentially indicating a complication rather than
mere co-endemicity. Text confirms Zika virus is understood as a *cause* of Guillain-Barré
syndrome (e.g., "Guillain-Barré is known to be triggered by bacterial infections,
respiratory viruses, entero-viruses, and arboviruses such as dengue and Zika").

However, querying SNOMED paths between *Zika virus disease* and *Infectious neuronitis*
(the SNOMED term for Guillain-Barré syndrome) at first returns many spurious 3-hop paths
routed through generic **hub nodes** like *Infectious process (qualifier value)* and
*Inflammation* — nodes connected to a massive number of unrelated infectious-process
concepts, producing noisy, non-meaningful connections.

**Filtering hub nodes with Neo4j Graph Data Science (GDS).** First project the SNOMED
subgraph:

```cypher
CALL gds.graph.project(
  'snomedGraph',
  'SnomedEntity',
  'SNOMED_RELATION'
)
YIELD graphName AS graph,
  relationshipProjection AS knowsProjection,
  nodeCount AS nodes,
  relationshipCount AS rels;
```

Then compute node degree (centrality) in streaming mode, collect the top 350
highest-degree nodes as hubs, and exclude any path passing through them:

```cypher
CALL gds.degree.stream('snomedGraph')
YIELD nodeId, score
WITH gds.util.asNode(nodeId).name AS name, score AS degree
ORDER BY degree DESC
LIMIT 350
WITH collect(name) AS hub_nodes

MATCH (s1), (s2)
WHERE s1.id = "3928002" AND s2.id = "40956001"
WITH s1, s2,
     allShortestPaths((s1)-[:SNOMED_RELATION*1..8]-(s2)) AS paths,
     hub_nodes
UNWIND paths AS path
WITH relationships(path) AS path_edges, nodes(path) AS path_nodes, hub_nodes
WITH
  [n IN path_nodes | n.name] AS node_names,
  [r IN path_edges | COALESCE(r.type, 'IS_A')] AS rel_types,
  [n IN path_edges | startnode(n).name] AS rel_starts,
  hub_nodes
WHERE NOT any(x IN node_names WHERE x IN hub_nodes)
...
RETURN DISTINCT apoc.text.join(string_paths, '') AS `Extracted paths`
```

Filtering hubs reduced the result set from 11,185 paths to 9 entries — still routed
through general entities like *Viral disease*, meaning **no direct, meaningful connection
between *Zika virus disease* and *Infectious neuronitis* is encoded in SNOMED**. This is
the payoff case: the text-derived co-occurrence (and confirming textual evidence) signals
a real-world causal relationship (`CAUSATIVE_AGENT`) that is missing from the ontology and
is a candidate for enrichment — closing a virtuous circle where the KG built from
unstructured text feeds back into improving the domain ontology.

## Takeaways

- **NER identifies entities; NED disambiguates them** — NER alone cannot resolve which
  specific KB entity ("ground entity") a mention refers to; NED links mention → context →
  KB entity via candidate selection, candidate ranking, and ontology integration.
- **General-purpose LLMs (ChatGPT) cannot perform domain NED out of the box** — they lack
  incorporated domain knowledge bases like UMLS and cannot assign UMLS IDs; NED/KG
  technologies must be combined with LLMs for high-precision domains like healthcare.
- **The KG schema deliberately keeps both raw mentions and disambiguated entities** —
  `EntityMention` nodes plus `MedicalEntity` nodes, linked by `DISAMBIGUATED_TO`, model
  both many-mentions-to-one-entity and one-mention-to-many-entities cases.
- **Ontology integration turns disambiguated entities into an exploration/discovery
  substrate** — UMLS is the hub connecting to SNOMED and HPO; SNOMED relationships are
  normalized into a single `SNOMED_RELATION` type with a `type` property (plus an explicit
  `SNOMED_IS_A` for hierarchy) to keep the schema simple while preserving semantics.
- **Co-occurrence relationships bridge unstructured text and structured ontologies**,
  enabling four use cases: conceptual search (meaning over keywords), structured
  knowledge-based search (ontology-path-driven retrieval), interpretability/discovery
  (explaining or enriching co-occurrences via ontology paths), and uncovering new
  knowledge (flagging co-occurrences with no ontology path as candidates for ontology
  enrichment).
- **Hub nodes pollute ontology-path analysis** — generic high-degree concepts (e.g.,
  "Infectious process") create spurious paths between unrelated entities; GDS degree
  centrality can identify and filter these hubs before interpreting path results.
