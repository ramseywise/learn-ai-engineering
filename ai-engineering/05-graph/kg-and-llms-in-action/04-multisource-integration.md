---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 4: From simple networks to multisource integration"
confidence: high
cleaned: 2026-07-29
---

# Ch 4 — From Simple Networks to Multisource Integration

This chapter extends knowledge graph (KG) construction from a single ontology-backed
knowledge base (chapter 3) to KGs built by merging **multiple structured data sources**
in graph-friendly formats (CSV, relational databases, APIs). The focus shifts to graph
modeling decisions, integration strategies, and analysis methods. Examples use
biomedical data, but the techniques transfer directly to other domains.

LLMs play a **complementary but limited** role in this phase of the KG lifecycle:
because the source data is structured (CSVs, relational databases, APIs), traditional
data-integration techniques are the primary approach, with LLMs serving as auxiliary
tools (e.g., interpreting analysis results) rather than core components of the
construction pipeline.

## Biomedical KG Applications — Overview

Biomedical science focuses on organs and systems of the human body: diseases, gene
expression, proteins, drugs, and related topics. KGs help researchers find new uses for
existing drugs, diagnose patients, identify disease–biomolecule associations, identify
protein functions, prioritize cancer genes, and recommend safer drugs. Applications
group into three primary types, each with different business goals and data sources:

- **Multi-omic applications** — genes, RNA, disease, protein nodes; `INTERACTS`,
  `TREATS` relationships (genomics, transcriptomics, proteomics).
- **Pharmaceutical applications** — drug, disease nodes; `INTERACTS`, `CAUSES`,
  `TREATS` relationships (drug–drug interaction, drug side effects, drug repurposing).
- **Clinical applications** — drug, patient, disease nodes; `PRESCRIBED`, `HAS`
  relationships (safe drug recommendations, patient diagnosis).

## Multi-Omic Applications of KGs

**Multi-omic** refers to a biological analysis approach that uses many "omics"
datasets — genomes, proteomes, and transcriptomes. The suffix *ome* in molecular
biology means a totality: for instance, *genome* refers to all the genetic information
of an organism.

- **Genome** — the entire genetic complement of a living organism. Most genomes are
  DNA (deoxyribonucleic acid); a few viruses have RNA genomes. Both are polymeric
  molecules made of chains of monomeric subunits called nucleotides.
- **Transcriptome** — a collection of RNA molecules that direct synthesis of the
  proteome. Constructed via **transcription**, in which individual genes are copied
  into RNA molecules.
- **Proteome** — the final product of genome expression, comprising all the functioning
  proteins synthesized by a living cell. It is the culmination of genome expression and
  the starting point for the biochemical activities that constitute cellular life.

The three are biologically connected through transcription (genome → transcriptome)
and translation (transcriptome → proteome). Multi-omic KG applications include
detecting miRNA–disease associations, gene–symptom prioritization, and predicting
protein–protein interactions (PPIs).

Yang et al. proposed a KG model to identify candidate genes associated with given
symptoms by merging many heterogeneous data sources. To unify and integrate disparate
disease terms, they mapped disease identifiers from different databases to **Unified
Medical Language System (UMLS)** codes. The general integration pattern: merge nodes
from multiple sources, link nodes representing the same concept, and remove irrelevant
nodes and relationships.

PPI networks and protein–disease associations have also been used successfully in
computational discovery of **disease pathways** (groups of proteins associated with a
specific disease) — a strong use case for intelligent advisor systems (IASs), since
understanding disease proteins in isolation cannot fully explain most human diseases.

### Creating a KG from PPI and Protein-Disease Networks

Approach (Agrawal et al.): start from a KG of diseases connected to associated known
proteins, which are in turn connected in the PPI network. A **disease pathway** is a
subgraph of the PPI network defined by the set of proteins associated with a disease.
The resulting KG is composed of a **monopartite graph** (the PPI network) plus a
**bipartite graph** (the disease–protein association network). The discovery task: given
known disease–protein connections, predict a set of potential proteins and related
pathways associated with the disease (proteins can extend an existing pathway or form a
new one).

Data sources:
- **Disease Pathways in the Human Interactome** (Stanford SNAP,
  http://snap.stanford.edu/pathways/) — Agrawal's simpler network derived from more
  complex sources.
- Human PPI network compiled by Menche et al. and Chatr-Aryamontri et al.: 342,354
  experimentally documented interactions among 21,559 proteins.
- **DisGeNET** (www.disgenet.org) — protein–disease associations: >21,000
  associations across 519 diseases, each with ≥10 disease proteins.
- **Disease Ontology** (https://disease-ontology.org/) — disease categories and
  subcategories, also mapped to UMLS codes. Of 519 DisGeNET diseases, 290 have a UMLS
  code mapping to a Disease Ontology code (second level: 10 categories, e.g. cancers
  [68], nervous system diseases [44], cardiovascular diseases [33], immune system
  diseases [21]).
- NCBI gene info (https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz) — improves
  protein readability (symbol, description) since SNAP data uses codes only.

```cypher
// Node key constraints ensure uniqueness
CREATE CONSTRAINT protein_key IF NOT EXISTS FOR
(n:Protein) REQUIRE (n.id) IS NODE KEY;
CREATE CONSTRAINT disease_key IF NOT EXISTS FOR
(n:Disease) REQUIRE (n.id) IS NODE KEY;
```

```cypher
// Importing the PPI network
:auto LOAD CSV FROM 'file:///PPI/bio-pathways-network.csv' AS line
CALL {
    WITH line
    MERGE (f:Protein {id: trim(line[0])})
    MERGE (s:Protein {id: trim(line[1])})
    MERGE (f)-[:INTERACTS_WITH]->(s)
} IN TRANSACTIONS OF 100 ROWS
```

```cypher
// Importing protein–disease associations (tuples u, d: protein u altered in disease d)
:auto LOAD CSV WITH HEADERS
FROM 'file:///PPI/bio-pathways-associations.csv' AS line
CALL {
    WITH line
    WITH trim(line["Associated Gene IDs"]) AS proteins,
         trim(line["Disease Name"]) AS diseaseName,
         trim(line["Disease ID"]) AS diseaseId
    MERGE (d:Disease {id: diseaseId, name: diseaseName})
    WITH d, proteins
    UNWIND split(proteins, ",") AS protein
    WITH d, protein
    MERGE (p:Protein {id: trim(protein)})
    MERGE (d)-[:ASSOCIATED_WITH]->(p)
} IN TRANSACTIONS OF 100 ROWS
```

```cypher
// Importing disease classes (from Disease Ontology mapping)
:auto LOAD CSV WITH HEADERS
FROM 'file:///PPI/bio-pathways-diseaseclasses.csv' AS line
CALL {
    WITH line
    WITH line["Disease ID"] as diseaseId, line["Disease Class"] as class
    MATCH (d:Disease {id: diseaseId})
    SET d.class = class
} IN TRANSACTIONS OF 100 ROWS
```

```cypher
// Importing gene information (NIH) for readability
:auto LOAD CSV WITH HEADERS FROM 'file:///PPI/gene_info' AS line FIELDTERMINATOR '\t'
CALL {
    WITH line
    WITH trim(line["GeneID"]) AS proteinId, trim(line["Symbol"]) AS symbol,
    trim(line["description"]) AS description
    WITH proteinId, symbol, description
    MATCH (p:Protein {id:proteinId})
    SET p.name = symbol, p.description = description
} IN TRANSACTIONS OF 100 ROWS
```

### High-Level Analysis of the Resulting KG

A prebuilt Neo4j 5.x backup is available for the PPI database
(https://mng.bz/5v7O) to skip manual import.

Generic graph evaluation starts with the **weakly connected component (WCC)**
algorithm: a community-detection algorithm that finds disconnected subgraphs, run via
the Neo4j Graph Data Science (GDS) library.

```cypher
// Mark connected proteins
MATCH (p:Protein)-[:INTERACTS_WITH]-()
SET p:PPIProtein
```

```cypher
// Create the in-memory graph projection
call gds.graph.project(
    'ppi-graph',
    'PPIProtein',
    {
        INTERACTS_WITH: {
            orientation: 'UNDIRECTED'
        }
    }
)
```

```cypher
// Run WCC
CALL gds.wcc.write('ppi-graph', { writeProperty: 'componentId' })
YIELD nodePropertiesWritten, componentCount, componentDistribution;
```

Results (Table 4.1): 21,559 nodes written, 27 components. Distribution shows p99 =
21,521 (99% of connected components have fewer than 21,521 proteins), mean = 798.481,
p50 = 1. **Interpretation**: the PPI network is highly connected — 21,559 proteins group
into 27 non-overlapping subgraphs, one of which is very large (21,521 proteins); the
rest are single nodes or islands of up to four components.

WCC assigns proteins to the same group merely because they're connected, without
regard to internal density. To find groups more densely connected internally than
externally, use the **Louvain modularity algorithm**: one of the fastest
modularity-based algorithms, works well on large graphs, reveals hierarchies of
communities at different scales. It maximizes the **modularity score** — how well
groups have been partitioned into communities, evaluated by how much more densely
connected the nodes are compared to how connected they would be in a random network.

```cypher
CALL gds.louvain.write('ppi-graph',
    { writeProperty: 'componentLouvainId' })
YIELD communityCount, modularity, modularities, communityDistribution
```

Results (Table 4.2): 48 communities, modularity 0.546 (~54%), mean size ~450
proteins/community, p50 = 3, p99 = 3,533. Some communities exceed 3,500 proteins; the
top 10 communities were inspected via:

```cypher
MATCH (p:PPIProtein)
WITH p.componentLouvainId as communityId, count(p) as members
ORDER BY members desc
LIMIT 10
MATCH (p:PPIProtein)-[:INTERACTS_WITH]-(o)
WHERE p.componentLouvainId = communityId
WITH communityId, members, p.name as name, count(o) as connections
ORDER BY connections DESC
RETURN communityId, members, collect(name)[..20] as keyMembers
```

The largest cluster includes proteins like APP, NTRK1, GRB2, EGFR, HSP90AA1 — a
biologically plausible grouping (verified informally by the authors, non-experts).

**Key point**: generic algorithms like WCC/Louvain are easy to use but generic — they
treat every node and relationship the same way, ignoring domain semantics.

### Domain-Specific Analysis of the PPI and Disease KG

Formalized as graph theory: PPI network *G = (V, E)*, nodes *V* = proteins, edges *E* =
protein–protein interactions. The disease pathway for disease *d* is an unstructured
subgraph *H_d = (V_d, E_d)* of the PPI network specified by:
- *V_d* = the set of proteins associated with *d*
- *E_d* = `{(u,v) | (u,v) ∈ E and u,v ∈ V_d}`

```cypher
// Extracting disease pathways from the KG
MATCH (d:Disease {id:$id})-[:ASSOCIATED_WITH]->(p)
WITH collect(p) as proteins
UNWIND proteins as m0
UNWIND proteins as m1
OPTIONAL MATCH (m0)-[r:INTERACTS_WITH]->(m1)
RETURN DISTINCT m0, r, m1
```

This subnetwork is **monopartite** — it doesn't contain protein–disease connections.
Pathways for different diseases can overlap. To relate a pathway to the rest of the PPI
network, define the boundary set:

*B_d = {(u,v) | (u,v) ∈ E and u ∈ V_d and v ∈ V\V_d}*

where *V\V_d* = all nodes in the global *V* but not in *V_d* — i.e., nodes not
associated with the target disease.

Three per-disease measures characterize connectivity inside and outside the pathway:

**1. Largest pathway component** — the relative size of a disease pathway's largest
connected component:

*relativeLargestCC(d) = |nodes(largestCC(H_d))| / |V_d|*

```python
class MultiOmicAnalysis(GraphDBBase):  # extends base class with Neo4j connection handling
    def __init__(self, argv, database):
        super().__init__(command=__file__, argv=argv)
        self.__database = database

    def load_hd(self, disease):  # loads the disease pathway subgraph
        query = """
            MATCH (d:Disease {id:$id})-[:ASSOCIATED_WITH]->(p)
            WITH collect(p) as proteins
            UNWIND proteins as m0
            UNWIND proteins as m1
            OPTIONAL MATCH (m0)-[r:INTERACTS_WITH]->(m1)
            return distinct m0, r, m1
        """
        param = {"id": disease}
        return self.load_graph_and_get_nx_graph(query, param)

    def load_graph_and_get_nx_graph(self, query, param={}):
        data = self.get_raw_data(query, param)
        G = networkx_utility.graph_undirected_from_cypher(data)  # convert to networkx graph
        return G

    def get_raw_data(self, query, param):
        with self.__driver.session(database=self.__database) as session:
            results = session.run(query, param)
            return results.graph()

    def compute_largest_components(self, networkx_graph):
        largest_cc = max(nx.connected_components(networkx_graph), key=len)
        return largest_cc

if __name__ == '__main__':
    analysis = MultiOmicAnalysis(argv=sys.argv[1:], database="ppi")
    disease_id = 'celiac disease'
    networkx_graph = analysis.load_Hd(disease_id)
    nodes_count = networkx_graph.nodes.__len__()
    largest_cc = analysis.compute_largest_components(networkx_graph)
    relative_size_of_largest_cc = float(largest_cc.__len__())/nodes_count
```

**2. Density** — how densely connected the proteins are in a pathway:

*density(d) = 2|E_d| / (|V_d|(|V_d| − 1))*

Numerator = real edges, denominator = number of possible edges. Result in [0, 1]: higher
density means a higher fraction of possible edges appear between nodes in *H_d*.

```python
def compute_density(networkx_graph):
    nodes_count = networkx_graph.nodes.__len__()
    edges_count = networkx_graph.edges.__len__()
    density_pathway = 2.0 * float(edges_count) / (nodes_count * (nodes_count - 1))
```

**3. Conductance** — independence of the disease pathway from the rest of the graph;
uses edges connecting a node inside the subgraph to a node outside, regardless of
direction:

*conductance(d) = |B_d| / (|B_d| + 2|E_d|)*

Result in [0, 1]: lower conductance means the pathway is a tighter-knit community,
separated from the rest of the network.

```python
def compute_bd(self, disease):
    query = """
        MATCH (d:Disease {id:$id})-[:ASSOCIATED_WITH]->(p)
        WITH collect(p) as proteins
        MATCH (m0)-[r:INTERACTS_WITH]-(m1)
        WHERE m0 in proteins and not m1 in proteins
        RETURN count(DISTINCT r) as bd
    """
    param = {'id': disease}
    return self.get_data(query, param)["bd"][0]

def get_data(self, query, param={}):
    with self.__driver.session(database=self.__database) as session:
        results = session.run(query, param)
        data = pd.DataFrame(results.values(), columns=results.keys())
        return data

if __name__ == '__main__':
    analysis = MultiOmicAnalysis(argv=sys.argv[1:], database="ppi")
    disease_id = 'celiac disease'
    networkx_graph = analysis.load_hd(disease_id)
    bd = analysis.compute_bd(disease_id)
    edges_count = networkx_graph.edges.__len__()
    conductance = float(bd) / (bd + 2 * edges_count)
```

Full analysis code: `chapter/ch04/analysis/multiomic_analysis.py` (repo).

### Analyzing Disease Pathways and Clusters

Running the three metrics across all diseases (frequency histograms):

- **Largest CC**: median 16 connected components per disease pathway; median only 21%
  of proteins in the largest pathway component. Only ~10% of pathways have >60% of
  their proteins in the largest component — pathways are fragmented in the PPI network.
- **Density**: median 0.07 (overall PPI network density is 0.0015); 90% of diseases have
  density below 0.17. Pathways are not well connected internally.
- **Conductance**: median 0.96 — disease pathways are well connected *externally*.

Running the same three measures on the WCC/Louvain clusters (not disease pathways)
gives a very different picture: most proteins reside in one large connected component
(near-1.0 largest-CC); density tracks overall network connectivity rather than cluster
structure; conductance improves markedly (clusters are better connected internally than
externally) — confirming that domain-defined disease pathways and generic
community-detection clusters capture fundamentally different structures.

## Pharmaceutical Applications of KGs

Developing a new therapeutic drug is estimated at **$1.4 billion** and typically takes
**15 years** from first compound to market, with a remarkably low likelihood of
success. Drug analysis and repurposing can drastically reduce duration, failure rates,
and cost by reusing preexisting information on approved drugs (toxicology profiling,
preclinical models, clinical trials, post-release surveillance). KGs have been used to
predict drug interactions, identify molecular targets a drug might interact with, and
determine new diseases treatable with established drugs.

Dai et al. used recommendation systems (collaborative filtering) to infer
drug–disease associations; others used related techniques to infer drug–target
interactions and drug–disease treatments. These approaches are limited to the drugs and
diseases already contained in the graph — enriching the KG with chemical structures,
biological processes, and other knowledge could enable predictions about novel
compounds.

### Hetionet

Himmelstein et al. constructed **Hetionet** ("heterogeneous network") — a graph
encoding knowledge from 29 public resources connecting compounds, diseases, genes,
anatomies, pathways, biological processes, molecular functions, cellular components,
pharmacological classes, side effects, and symptoms. Publicly available at
https://het.io/, in Neo4j format via a prebuilt backup (https://mng.bz/648e).

Imported KG stats: **47,031 nodes** of **11 types**, **2,250,197 relationships** of
**24 types**. Nodes: genes, 137 complex diseases, 1,552 small-molecule compounds,
anatomies, pathways, biological processes, molecular functions, cellular components,
perturbations, pharmacologic classes, drug side effects, disease symptoms. Edges
encapsulate knowledge from millions of studies over the last half century — e.g.
Compound–binds–Gene (a compound binding to a protein encoded by a gene); Hetionet
includes 11,571 such edges, each storing its supporting reference as a relationship
attribute.

```cypher
# Add to neo4j.conf:
# dbms.databases.seed_from_uri_providers=URLConnectionSeedProvider
CREATE DATABASE hetionet OPTIONS { existingData: "use",
seedUri: "https://mng.bz/648e"}
```

### Metapaths and Degree-Weighted Path Count (DWPC)

A **metagraph** (schema) describes the structure of a database — types of nodes and
relationship types that exist. A **metapath**, by contrast, is a sequence of node and
relationship *classes* describing potential real paths between a node of one type and a
node of another type — a pattern you can "query" the schema for, independent of actual
data instances. Example: metapaths for a generic pattern (Gene)—...—(Disease) of max
length 4.

- **Path count (PC)** — simplest metapath-based metric: number of actual paths, for a
  specified metapath, between the source and target nodes. PC doesn't adjust for graph
  connectivity along the path (each path has value 1 regardless of how "well-known" the
  intermediate nodes are).

- **Degree-weighted path count (DWPC)** — introduced by Himmelstein, adapting
  PathPredict (a method from social network analysis), to quantify metapath prevalence
  while discounting for highly-connected ("well-known") intermediate nodes. Built from
  the **path-degree product (PDP)**:

  *PDP(path) = ∏_{d ∈ D_path} d^(−w)*

  Steps:
  1. Extract all metaedge-specific degrees along the path (*D_path*) — each edge
     contributes two degree values (its endpoints' degree counts for that edge type).
  2. Raise each degree to the −w power, where w ≥ 0 is the **damping exponent**.
  3. Multiply all exponentiated degrees together to yield the PDP.

  Example: path (IRF1)—[]—(CXCR4)—[]—(Multiple sclerosis), w = 0.5. Degrees:
  4 (IRF1 outgoing INTERACTS), 2 (CXCR4 has two incoming INTERACTS edges), 1, 4:
  `4^-0.5 * 2^-0.5 * 1^-0.5 * 4^-0.5 = 0.167 ≈ 0.177`.

  *DWPC_m(s,t) = Σ_{path ∈ Paths_m(s,t)} PDP(path)*

  DWPC sums the PDPs across all paths for a specific metapath, evaluating path
  prevalence while ignoring the distorting effect of "well-known" hub nodes — a common
  issue in KG analysis.

### Deep Analysis of the Hetionet KG (Celiac Disease Case Study)

Celiac disease (CD): a common (prevalence 1:100), chronic, immune-mediated
enteropathy caused by intolerance to gluten in genetically predisposed individuals. 48
genes are associated with CD.

```cypher
MATCH p = (:Disease {name: 'celiac disease'})-[rel:
ASSOCIATES_DaG]-() RETURN p.
```

**GO process enrichment** — compute DWPC between CD and each Gene Ontology (GO)
process in which at least two celiac-related genes participate, restricted to processes
with ≥5 participating genes:

```cypher
MATCH path = (n0:Disease)-[:ASSOCIATES_DaG]-(n1)-[:PARTICIPATES_GpBP]-
(n2:BiologicalProcess)
WHERE n0.name = 'celiac disease'
WITH
[
  size([(n0)-[:ASSOCIATES_DaG]-() | n0]),
  size([()-[:ASSOCIATES_DaG]-(n1) | n1]),
  size([(n1)-[:PARTICIPATES_GpBP]-() | n1]),
  size([()-[:PARTICIPATES_GpBP]-(n2) | n2])
] AS degrees, path, n2
WITH
  n2.identifier AS go_id,
  n2.name AS go_name,
  count(path) AS PC,
  sum(reduce(pdp = 1.0, d in degrees| pdp * d ^ -0.4)) AS DWPC,
  size([(n2)-[:PARTICIPATES_GpBP]-() | n2]) AS n_genes
WHERE n_genes >= 5 AND PC >= 2
RETURN
  go_id, go_name, PC, DWPC, n_genes
ORDER BY DWPC DESC
LIMIT 10
```

Results (Table 4.3): top process by PC is GO:0002684 "positive regulation of the
immune system process" (PC=21, connected to 880 genes) — but by DWPC it drops toward
the bottom because it's involved in many other (non-CD-specific) processes. Top by
DWPC is **GO:0031295 "T cell costimulation"** (PC=10, DWPC=0.03347, 75 genes) — highly
relevant to celiac disease. **Key insight: ordering by raw PC surfaces generic hub
processes; ordering by DWPC surfaces specific, mechanistically relevant processes.**

A refined query adds protein-interaction relationships, restricts to gene–disease
associations sourced from GWAS Catalog (less biased by prior knowledge), and considers
only genes upregulated in celiac-affected tissue:

```cypher
MATCH path = (n0:Disease)-[e1:ASSOCIATES_DaG]-(n1)-[:INTERACTS_GiG]-(n2)-
[:PARTICIPATES_GpBP]-(n3:BiologicalProcess)
WHERE n0.name = 'celiac disease'
  AND 'GWAS Catalog' in e1.sources
  AND exists((n0)-[:LOCALIZES_DlA]-()-[:UPREGULATES_AuG]-(n2))
WITH
[
  size([(n0)-[:ASSOCIATES_DaG]-() | n0]),
  size([()-[:ASSOCIATES_DaG]-(n1) | n1]),
  size([(n1)-[:INTERACTS_GiG]-() | n1]),
  size([()-[:INTERACTS_GiG]-(n2) | n2]),
  size([(n2)-[:PARTICIPATES_GpBP]-() | n2]),
  size([()-[:PARTICIPATES_GpBP]-(n3) | n3])
] AS degrees, path, n3 as target
WITH
  target.identifier AS go_id,
  target.name AS go_name,
  count(path) AS PC,
  sum(reduce(pdp = 1.0, d in degrees| pdp * d ^ -0.4)) AS DWPC,
  size([(target)-[:PARTICIPATES_GpBP]-() | target]) AS n_genes
WHERE 5 <= n_genes <= 100 AND PC >= 2
RETURN
  go_id, go_name, PC, DWPC, n_genes
ORDER BY DWPC DESC
LIMIT 10
```

Results (Table 4.4) sharpen further: alongside T cell/lymphocyte costimulation, new
top-ranked processes emerge with a strong dominance of glycoprotein-related processes
(e.g. "positive regulation of glycoprotein biosynthetic process," DWPC=0.00342).
Paths behind a specific DWPC score can be retrieved directly with a `MATCH path =
(...) WHERE n0.name = ... AND n3.name = ... RETURN path` query.

### LLM-Assisted Interpretation of Pathway Analysis Results

DWPC-based queries provide quantitative rankings of biological processes, but
translating results into clinically actionable insight requires domain expertise and
context. LLMs can serve as intelligent interpreters, synthesizing complex pathway
analysis results into coherent biological narratives and clinical recommendations.

Example prompt structure for an LLM (Claude Sonnet 4.0 used in the book):
1. Role framing ("You are a biomedical research assistant...")
2. Raw query results (DWPC, PC, gene counts per process)
3. Context (how the metrics were derived)
4. Numbered analysis requests: interpret biological significance, explain
   relationship to disease pathogenesis, identify therapeutic implications, highlight
   unexpected findings, suggest follow-up research questions.

In the book's example, the LLM connected "T cell costimulation" to antigen-presenting
cells presenting gliadin peptides via HLA-DQ2/DQ8 causing aberrant costimulation;
"tolerance induction" (few genes, high DWPC) to breakdown of oral tolerance to dietary
antigens; "positive regulation of T cell activation" (201 genes) to the chronic
inflammatory response driving villous atrophy.

## Clinical Applications of KGs

Clinical KG applications are early-stage. The long-term goal is to support **precision
medicine** — using a person's genetics, environment, and lifestyle to determine the
best treatment approach — which requires integrating omics data (proteomics, genomics,
transcriptomics) with clinical data such as **electronic health records (EHRs)**.
Challenges: quantity/diversity of biomedical data, clinically relevant knowledge spread
across multiple databases and publications, and privacy concerns.

EHRs are designed to contain information from all clinicians involved in a patient's
care; they can be challenging to interpret, contain considerable subjectivity, and
information a clinician deems irrelevant may be omitted, causing missing information.
Clinical KGs merge EHRs with multi-omics datasets, ontologies, and other sources. Key
elements: nodes represent patients, drugs, and diseases; edges encode relationships
such as a patient being treated with a drug or diagnosed with a disease.

Related concepts:
- **Patient journey mapping** (also *patient experience mapping*) — a rapidly growing
  approach to understanding how people enter, experience, and exit health services.
- **Clinical pathways** — establish the standard of care for a patient's clinical
  presentation for a specific disease; often linked to a companion patient journey map.

Privacy-preserving approaches: (1) extract only statistical information (diseases,
symptoms, treatment outcomes, and their weighted relationships) into the KG rather than
raw patient data; (2) build a deidentified, generic clinical KG from nonsensitive,
anonymized, experimental/statistical data, using patient EHR data only when strictly
necessary and with patient consent.

### Clinical Knowledge Graph (CKG)

The **Clinical Knowledge Graph (CKG)** (Albertos Santos et al.) is a platform with a KG
at its core, harmonizing and integrating data by connecting **33 node labels** with
**51 relationship types**. It supports queries revealing altered functions, suggesting
drugs for regulated proteins, and revealing possible confounding factors. Available in
Neo4j format at https://github.com/MannLabs/CKG, backup at https://mng.bz/oZQZ.

```cypher
# neo4j.conf: dbms.databases.seed_from_uri_providers=URLConnectionSeedProvider
CREATE DATABASE ckg OPTIONS { existingData: "use",
seedUri: "https://mng.bz/oZQZ"}
```

```cypher
// Finding known protein-disease associations for a target protein list and disease
WITH
  ['A1BG-P04217','A2M-P01023','ACACB-O00763',
   'ACTC1-P68032','ADIPOQ-Q15848','AGT-P01019',
   'AIFM2-Q9BRQ8','APOA2-V9GYM3'] as proteins,
  3 as minScore,
  "DOID:0050700" as parentDisease
MATCH (protein:Protein)-[r]-(disease:Disease)
WHERE (
  (protein.name+"-"+protein.id) IN proteins AND
  toFloat(r.score)> minScore  AND
  ((disease)-[:HAS_PARENT*0..]->(:Disease {id: parentDisease}))
)
RETURN
  (protein.name+"-"+protein.id) AS node1,
  disease.name+" <"+disease.id+">" AS node2,
  r.score AS weight, type(r) AS type,
  r.source AS source
ORDER BY weight DESC
```

Result: protein **ACTC1-P68032** is strongly associated (score 5) with several types
of intrinsic cardiomyopathy (intrinsic cardiomyopathy, left ventricular
noncompaction, familial hypertrophic cardiomyopathy, hypertrophic cardiomyopathy,
dilated cardiomyopathy, restrictive cardiomyopathy — all via DISEASES source) — a
specific starting point for further investigation. Note: **DOID** is the Disease
Ontology identifier (www.disease-ontology.org).

### LLM-Guided Clinical Decision Support

Clinical KGs contain complex relationships between patients, treatments, and outcomes
requiring careful interpretation. LLMs can help synthesize multidimensional clinical
data into coherent treatment recommendations and research directions. Example prompt
pattern for the CKG cardiomyopathy findings: role framing (clinical informatics
specialist), the clinical scenario, the KG findings (protein–disease associations with
scores), the target protein list, and numbered clinical requests (interpret clinical
significance, suggest patient stratification, identify safety considerations,
recommend screening/monitoring, suggest biomarkers/genetic testing, propose
inclusion/exclusion criteria changes).

**Explicit caution from the authors**: do not use LLM outputs from clinical KGs
without proper interpretation by physicians and researchers. The purpose is to show how
LLMs can convert complex data extracted from large KGs into interpretable insights —
the goal is to empower humans via IASs, **not to replace them**.

## Takeaways

- KGs built from structured, multisource data require systematic integration:
  entity resolution (e.g., mapping to UMLS/Disease Ontology codes), schema alignment,
  and data quality validation to produce coherent, queryable knowledge representations.
- Generic clustering algorithms (WCC, Louvain) reveal a graph's global structure and
  community organization but treat every node/relationship identically — they answer a
  different question than domain-specific subgraph metrics (largest CC, density,
  conductance) applied to meaningful subgraphs like disease pathways.
- **DWPC** (degree-weighted path count) generalizes simple path counting by discounting
  paths through highly-connected "hub" nodes, surfacing mechanistically specific
  relationships that raw path count buries under generic, highly-connected processes.
- Large public KGs — Hetionet (pharma), the PPI/DisGeNET network (multi-omic), and CKG
  (clinical) — serve as ready-made testbeds for integration and analysis techniques
  without requiring authors to build multisource KGs from scratch.
- LLMs' role in this phase is auxiliary: interpreting quantitative KG analysis output
  (DWPC scores, protein–disease associations) into biological/clinical narratives —
  never as an unsupervised replacement for expert clinical judgment.
