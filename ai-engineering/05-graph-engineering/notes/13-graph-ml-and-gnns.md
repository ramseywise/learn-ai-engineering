---
origin: book-condensed
sources:
  - sources/kg-and-llms-in-action/ch04-multisource-integration.pdf
  - sources/kg-and-llms-in-action/ch09-ml-on-knowledge-graphs.pdf
  - sources/kg-and-llms-in-action/ch10-graph-feature-engineering.pdf
  - sources/kg-and-llms-in-action/ch11-graph-representation-learning-gnns.pdf
  - sources/kg-and-llms-in-action/ch12-node-classification-link-prediction.pdf
  - "Salvatore Raieli & Gabriele Iuculano, Building AI Agents with LLMs, RAG, and Knowledge Graphs (Packt, 2025), ch. 7"
confidence: medium-high
cleaned: 2026-10-31
---
# 13 — Learning on Graphs: Features, Embeddings, GNNs

> Notes 09–12 query the edges a graph already has. Graph ML predicts the ones it doesn't: missing links, unlabeled nodes, hidden communities. A prediction is a claim, not a fact, so it enters the graph with a confidence score.

All book citations in this note are to Negro et al., *Knowledge Graphs and LLMs in Action* (Manning, 2025), abbreviated *KG & LLMs in Action*.

---

## Where it sits

This is the **Learning** pillar from [note 09](09-kg-fundamentals-and-cypher.md#what-a-knowledge-graph-is). You can build, query and share a KG without it. It earns its place when:

- the graph is **incomplete** and you want candidate edges ("which drug might treat this disease?", "which accounts are linked to this fraud ring?");
- you need **labels** for nodes nobody has labelled (bot, fraudster, protein function);
- the graph is too large to inspect, and **communities** give you a summary of it.

Two pieces of the earlier notes are already graph ML: **WCC** clusters mentions in entity resolution ([note 10](10-building-kgs-with-llms.md#graph-based-er-ch6)), and GraphRAG's **community summaries** rest on community detection ([note 11](11-kg-rag-and-text-to-cypher.md#retrieval-modes)).

The book frames all of this as the engine of an **intelligent advisory system**: one that surfaces something a user couldn't extract by querying alone, such as a drug-repurposing candidate in a disease–gene–compound graph (*KG & LLMs in Action*, ch. 9). Its case for graph ML has three parts: almost any data (tables, sequences, time series) can be recast as a graph; many business problems reduce to a handful of graph tasks; and graph models use the dependencies between records that classical ML throws away. [ch. 9 PDF](../sources/kg-and-llms-in-action/ch09-ml-on-knowledge-graphs.pdf)

---

## Why graphs need their own ML

Classical ML assumes data points are **i.i.d.** (independent and identically distributed). Nodes aren't. Three patterns break the assumption (*KG & LLMs in Action*, ch. 9):

| Pattern | Means | Example |
|---|---|---|
| **Homophily** | Connected nodes tend to be alike | Friends share interests |
| **Structural equivalence** | Nodes with similar neighbourhoods play similar roles, even far apart | Proteins with the same interaction shape share function |
| **Heterophily** | Connected nodes tend to differ | Buyers connect to sellers |

So node tasks are usually **semisupervised**. Training sees the whole graph, unlabelled nodes included; only their labels are missing, and their neighbourhoods still inform the model. That differs from textbook supervised learning, where test points are unseen at training time, and from textbook semisupervised learning, which still assumes i.i.d. (ch. 9).

Graphs are incomplete for two reasons: the edge exists but was never recorded (or is deliberately hidden, as in fraud), or the graph is still evolving (next year's co-authorships) (ch. 9). The book stops at the two causes, but they call for different evaluation. Random held-out edges test the first; the second needs a time-based split, or the model is scored on edges it could only know from the future.

### The task map

The book's main split is not supervised vs. unsupervised but **what one data point is**: a node or edge inside one graph (*node-focused*), or a whole graph in a set of graphs (*graph-focused*) (ch. 9).

| Task | Data point | Typical use | Needs training? |
|---|---|---|---|
| **Node classification** | A node in one graph | Fraud, bots, AML, protein function; multilabel variants (which groups will this user join?) | Yes |
| **Link prediction** | A node pair in one graph | KG completion, recommendations, drug repurposing, side effects | Yes, and semisupervised like node classification; sample non-links as negatives |
| **Community detection** | The whole graph | Summarising, fraud rings, functional modules | No: WCC, Louvain, label propagation act on the graph directly |
| **Graph classification** | One whole graph among many | Molecule toxicity, enzyme vs. non-enzyme, malware | Yes; here each graph *is* an i.i.d. data point, so ordinary supervised learning applies |

A small set of tasks covers a large set of business problems. That is the book's main argument for the graph framing.

Two terms worth keeping apart: **link prediction** asks whether an edge of a fixed type exists; **relationship prediction** also predicts its type (ch. 9). The book then uses the two "interchangeably", and ch. 10 frames the difference as the classifier's output: binary (does an edge exist?) or multiclass (which type of edge?).

**Community detection is not K-means.** K-means needs *k* up front and DBSCAN groups dense points in vector space; both treat records as independent points. Graph clustering needs no *k* and lets the edges decide membership, usually by maximising **modularity** (how much denser a community's internal edges are than chance would predict). **Label propagation** is fast but random: rerun it and the communities shift slightly, so pin a seed or check stability before you store community IDs. It can also take the labels you already have as seeds, which makes it a cheap semisupervised baseline. Louvain on the 34-node karate-club graph (seed 123) finds four communities that mostly match the real post-split factions, with one boundary node landing on the wrong side (ch. 9).

### Two ways to implement

1. **Graph-native** ("collective classification"): the algorithm takes the graph itself and uses node features and neighbourhoods together. GNNs are the modern form.
2. **Featurise, then classic ML**: turn each node, edge or graph into a vector, then use any classifier (logistic regression, random forest).

For the second route, both node and link tasks reduce to ordinary classification (ch. 9):

```mermaid
flowchart LR
  G[Graph] --> F[Featurise nodes]
  F -->|node task| C[Classifier]
  F -->|link task| P["Combine pair vectors<br/>(Hadamard, avg, L1, L2, concat)"]
  N["Sample non-edges<br/>label 'does not exist'"] --> P
  P --> C
  C --> O["Probability<br/>threshold, e.g. 0.5"]
```

The one hard rule: **the featurisation at prediction time must be exactly the one used at training time** (ch. 9). In a graph that keeps changing, that means versioning the feature code and recomputing features from the same snapshot logic, not reusing stale columns.

---

## Features: the bottleneck

Models want vectors, so every node, edge or graph has to be **featurised**. The approaches trade interpretability for effort (*KG & LLMs in Action*, ch. 10):

| Approach | Examples | Interpretability | Effort |
|---|---|---|---|
| **Manual** | Degree, triangles, density, closeness, betweenness, PageRank; for edges, combine node vectors (Hadamard, average, L1, L2, concatenation) or count metapaths | High: every number traces to a graph property | High |
| **Semiautomated** | ReFeX: recursive local, egonet and aggregated features from topology alone, then pruned by correlation | Balanced, and deterministic | Medium |
| **Learned** | Node2Vec, GNN embeddings | Low | Low |

Manual features keep a place even when you plan to learn embeddings: they are explainable to a reviewer, they work on small graphs, they tell you what the automated methods ought to capture, and an LLM can reason about them because they rest on well-known algorithms (ch. 10). [ch. 10 PDF](../sources/kg-and-llms-in-action/ch10-graph-feature-engineering.pdf)

**The karate-club lesson** (ch. 9). Predicting which faction each member joined after the club split:

| Features | F1 |
|---|---|
| Degree only | 0.43 |
| Node2Vec, 64-dim, untuned (walk length 30, 200 walks per node, window 10, default p = q = 1) | 0.64 |
| Degree + "neighbours in faction A" + "neighbours in faction B" (homophily, written by hand) | **0.93**, "very stable" |

Read the numbers small. The test set is 40% of 34 nodes, i.e. 14 members, so one node moves F1 by several points. The classifier was the same one-vs-rest `LogisticRegressionCV` each time, on standardised features (without scaling, a 1–1,000 degree column drowns a 0–1 centrality column), scored with weighted P/R/F1. The book says repeated runs of *both* the degree and the Node2Vec setups swing between 30% and 70% F1. With the split fixed (`random_state=0`), only the multi-worker Node2Vec walks can actually vary between runs, so the swing presumably comes from changing the split. Domain knowledge expressed as three numbers beat a generic embedding. Learned features don't remove the need to understand the graph. They need tuning (here, shorter and fewer walks was the suggested fix for over-homogeneous vectors), and a domain-informed baseline tells you whether the tuning worked. The homophily feature is a two-liner:

```python
def homophily_features(G, label="club"):
    lab = nx.get_node_attributes(G, label)
    return {n: [G.degree(n)] + [sum(lab[m] == c for m in G[n]) for c in sorted(set(lab.values()))]
            for n in G}
```

The catch: counting labelled neighbours uses the labels you're predicting. Compute it from **training labels only**, or the test nodes leak their answers into their neighbours' features. The book's listing counts the club label of every neighbour, test nodes included, so its 0.93 is an optimistic upper bound.

### Manual node features

Ch. 10 builds one feature vector per node on a 20-node toy fraud network (four known fraudsters), local features first, then global ones (*KG & LLMs in Action*, ch. 10). A node's **egonet** is the node (the ego) plus its one-hop neighbours (the alters).

| Feature | Scope | Fraud-aware variant | What it says | Value on the toy graph |
|---|---|---|---|---|
| **Degree** | Local | Split into fraud degree and legit degree | More fraudulent neighbours, more risk | D: 4 neighbours, 2 of them fraudsters |
| **Triangles** | Local | Fraudulent (both alters fraud), semifraudulent (one), legitimate (none) | Tight clustering; a fraud triangle is a ring signal | D: 2 triangles, D–E–F fraudulent, D–F–G semifraudulent |
| **Egonet density** | Local | None | Share of possible egonet edges that exist: 2M / N(N−1) | A: 7 nodes, 7 of 21 possible edges, 0.33 |
| **Geodesic distance** | Global | Distance to the nearest fraudster, and the number of fraudsters at 1, 2, 3 hops | Proximity to contamination | 0 for a fraudster; A: 1 (I is a neighbour) |
| **Closeness** | Global | None | Inverse of mean shortest-path distance to everyone | A highest (0.5); R, S lowest (0.24) |
| **Betweenness** | Global | None | Share of shortest paths that pass through the node: a bridge | A = 104 (unnormalised; the book's code passes `normalized=True`, which gives 0.61); nine nodes are 0 |
| **PageRank** | Global | Personalised toward known fraudsters | Importance weighted by the importance of who points at you | A tops base PageRank (0.108) |

Two practical fixes from the chapter. Closeness breaks on disconnected graphs (distance to an unreachable node is infinite), so average over **reachable nodes only** and scale by the reachable fraction, which is what `networkx` does. And the PageRank pair is more useful than either number: the gap between base and fraud-personalised PageRank flags nodes whose fraud exposure is larger than their general prominence. The book reports D jumping to the top of the fraud-weighted ranking (0.168). Rerunning its setup as described (personalisation weight 2.0 on fraudsters) leaves A on top with D at about 0.085, so treat the exact numbers as sensitive to the weight; the divergence idea is what transfers.

The fraudster counts by hop have two definitions in the chapter, and they disagree. Its code counts fraudsters by shortest-path distance (A has 1, 2 and 1 at one, two and three hops). Its table counts walks, entries of the adjacency matrix raised to the power 2 or 3, which revisit nodes and count a fraudster once per route (A gets 4 and 18, and D's count includes walks that return to D). Pick one and document it; walk counts grow with degree and mostly re-measure it.

Assembling and training is ordinary tabular ML: one row per node, a **stratified** 80/20 split so both sides keep the fraud/legit ratio, `StandardScaler`, logistic regression, and the absolute coefficients as a first read on feature importance (ch. 10). With 20 nodes and four fraudsters, that split leaves one fraudster in the test set. The book draws the same conclusion and doesn't report the toy's results at all, since the graph is "too small to be statistically relevant".

### Manual relationship features

For link prediction a node *pair* needs one vector. Two families (ch. 10):

**Node-based combination**: merge the two node vectors *u* and *v*.

| Operator | Element *i* | Length | Notes |
|---|---|---|---|
| Concatenate | u ‖ v | 2n | Keeps direction; order matters |
| Average | (uᵢ + vᵢ) / 2 | n | Symmetric |
| L1 | \|uᵢ − vᵢ\| | n | Symmetric; a per-dimension distance |
| L2 | (uᵢ − vᵢ)² | n | Symmetric; penalises big gaps |
| Hadamard | uᵢ · vᵢ | n | Symmetric; the operator that won node2vec's own link-prediction benchmarks (Grover & Leskovec, 2016), not a claim the book makes |

There is no rule for which one wins; benchmark them on your task. With hand-made node features this family tends to lose to path-based features. It does better once the node vectors are learned (ch. 10).

**Path-based features** describe the pair by how it is connected. A **metapath** is a typed walk through the schema (the *metagraph*), e.g. Compound–binds–Gene–associates–Disease, abbreviated CbGaD. For drug repurposing on Hetionet (19 public databases, more than 50,000 nodes), every compound–disease pair gets one column per metapath, whether or not the pair is directly linked. Himmelstein et al. evaluated every compound-to-disease metapath of length 2 to 4, and the approach surfaced depression and alcoholism drugs as candidates for smoking addiction and epilepsy (ch. 10):

| Metapath | Length | Reads as |
|---|---|---|
| CbGaD | 2 | The drug binds a gene associated with the disease |
| CdGuD | 2 | The drug down-regulates a gene the disease up-regulates |
| CrCtD | 2 | The drug resembles a drug that treats the disease |
| CbGbCtD | 3 | It binds a gene that another treating drug also binds |
| CbGeAlD | 3 | It binds a gene expressed in tissue where the disease localises |
| CbGiGiGaD | 4 | It binds a gene two interaction steps from a disease gene |
| CbGpPWpGaD | 4 | It binds a gene in a pathway shared with a disease gene |

### DWPC: discount the hubs

Counting paths between two nodes overrates connections that go through **hubs**, the nodes connected to everything. **Degree-weighted path count** damps each path by the degrees of the nodes it passes through, so specific connections outrank generic ones (*KG & LLMs in Action*, ch. 4 and ch. 10). It was introduced by Himmelstein et al. for Hetionet, adapting the PathPredict method from social network analysis (ch. 4). It is the same instinct as dropping hub nodes in NED ([note 10](10-building-kgs-with-llms.md#ned-against-an-ontology-ch78)): a path through "Infectious process" says almost nothing. [ch. 4 PDF](../sources/kg-and-llms-in-action/ch04-multisource-integration.pdf)

**The formula.** For one path, collect the metaedge-specific degree of both endpoints of every edge on it (degree counted only over edges of that type), raise each to −*w*, and multiply. That is the **path-degree product** (PDP). DWPC sums PDPs over all paths that match the metapath:

```
PDP(path)        = ∏ d^(−w)      over the 2 × (path length) degrees on the path
DWPC_m(s, t)     = Σ PDP(path)   over all paths of metapath m from s to t
```

*w* = 0 gives plain path count; the book's queries use *w* = 0.4. Worked example (ch. 4): a two-edge path IRF1–CXCR4–multiple sclerosis with endpoint degrees 4, 2, 1, 4 and *w* = 0.5 gives 4^−0.5 · 2^−0.5 · 1 · 4^−0.5 ≈ 0.177.

In Cypher (Neo4j 5), one metapath for one pair:

```cypher
// CbGaD between one compound and one disease, damping w = 0.4
MATCH path = (c:Compound {name: $compound})-[:BINDS_CbG]-(g:Gene)
             -[:ASSOCIATES_DaG]-(d:Disease {name: $disease})
WITH path, [COUNT { (c)-[:BINDS_CbG]-() },      COUNT { (g)-[:BINDS_CbG]-() },
            COUNT { (g)-[:ASSOCIATES_DaG]-() }, COUNT { (d)-[:ASSOCIATES_DaG]-() }] AS degs
RETURN count(path) AS PC,
       sum(reduce(p = 1.0, k IN degs | p * k ^ -0.4)) AS DWPC
```

Every node on the path must be bound in the `MATCH`; the book's own listing counts degrees on an unbound variable, a slip worth checking for when you adapt it. For metformin and type 2 diabetes on CbGaD the book gets DWPC ≈ 0.0007, one cell of the feature matrix (ch. 10).

**Why it matters, in one table.** Ranking Gene Ontology processes by their connection to celiac disease (ch. 4):

| GO process | PC | Genes in process | DWPC | Rank by PC | Rank by DWPC |
|---|---|---|---|---|---|
| Positive regulation of immune system process | 21 | 880 | 0.0272 | Top | Drops down the list |
| T cell costimulation | 10 | 75 | **0.0335** | Lower | **Top** |

Raw counts surface the generic, well-studied process; DWPC surfaces the specific mechanism a researcher can act on.

DWPC scores are comparable only within one metapath and one damping exponent *w*. Ch. 4's own LLM prompt breaks this: it lists a glycoprotein-biosynthesis score (0.00342, from the GWAS + gene–gene metapath of Table 4.4) alongside four from the disease–gene–process metapath of Table 4.3 as if they were one ranking.

**Cost.** DWPC over every pair and every metapath is expensive and noisy. Himmelstein et al. cut the metapaths from 1,026 to 709 by keeping those whose values differ between known treatments and non-treatments, then restricted the candidate pairs using domain knowledge and degree-based probabilities (ch. 10). Do the same: select metapaths against labelled positives before computing the full matrix.

### LLMs help with manual features

Because manual features rest on well-known algorithms, an LLM can reason about them. Ch. 10 gives it three jobs: translating metapath descriptions into Cypher, suggesting patterns a human might miss, and writing the code that runs the queries and collects the results. The prompt that produced per-metapath PC and DWPC queries contained four things: the schema (from `apoc.meta.schema()`), one worked query for CbGaD, the list of target metapaths, and sample node names to test with. Treat the output as a draft, the same way [note 11](11-kg-rag-and-text-to-cypher.md#text-to-cypher) treats text-to-Cypher; the book itself calls it a prompting pattern, not a pipeline (ch. 10).

### Semiautomated: ReFeX

**ReFeX** (Recursive Feature eXtraction) sits between hand-made and learned features. It works on **topology alone**, ignoring labels and types, and is built on two rules: needing no node or edge attributes, and producing features that predict attributes where they exist and transfer across graphs (*KG & LLMs in Action*, ch. 10). The features describe the *kind* of nodes a node connects to, not which nodes: "it is who you know, or who you relate to". That is why they can be compared across different networks, or across snapshots of one network over time, which embeddings trained separately per graph can't offer.

It runs in three stages, then prunes:

1. **Local**: degree (in/out separately on directed graphs; weighted variants sum edge weights).
2. **Egonet**: edges inside the egonet, and edges leaving it.
3. **Recursive**: for every existing feature, the **sum** and **mean** over the node's neighbours (over in- and out-neighbours separately on directed graphs); repeat, so each round reaches one hop further (`sum(mean(degree))` describes the two-hop region; the book's example of a deeper name is `degree(sum)(mean)(mean)(sum)`).
4. **Prune**: recursion multiplies the feature count each round, so drop any feature highly correlated with an earlier one. The original method also uses logarithmic binning and threshold-based pruning.

Node A of the toy fraud graph, by hand (ch. 10):

| Stage | Feature | A |
|---|---|---|
| Local | Degree | 6 |
| Egonet | Edges inside the egonet | 7 |
| Egonet | Edges leaving the egonet | 9 |
| Recursive 1 | Sum / mean of neighbours' degrees | 17 / 2.83 |
| Recursive 2 | Sum / mean of neighbours' round-1 sums | 69 / 11.5 |

A minimal version. With `max_corr` above 1 (pruning off) it reproduces the table above; at the default 0.95 the round-2 sum (69) is pruned on this graph, because it tracks an earlier column. The book's own code computes different egonet features (node count, edge count and density, not edges leaving the egonet), so its vectors won't match this one column for column.

```python
import networkx as nx, numpy as np

def refex(G, rounds=2, max_corr=0.95):
    nodes = list(G); pos = {n: i for i, n in enumerate(nodes)}
    def ego(n):
        e = set(G[n]) | {n}
        return [G.subgraph(e).number_of_edges(), sum(v not in e for u in e for v in G[u])]
    F = np.array([[G.degree(n), *ego(n)] for n in nodes], float)
    for _ in range(rounds):
        nbrs = [[pos[m] for m in G[n]] for n in nodes]
        F = np.hstack([F, [F[i].sum(0) for i in nbrs], [F[i].mean(0) for i in nbrs]])
        C = np.abs(np.corrcoef(F.T))
        F = F[:, [j for j in range(F.shape[1]) if not (C[:j, j] > max_corr).any()]]
    return nodes, F
```

What it buys: **deterministic** output (same graph, same features, which matters for reproducible production runs), features that still have a structural meaning, and **selective recomputation** when part of the graph changes. What it can't do: use node attributes or edge types. A domain expert still has to validate which surviving features matter (ch. 10).

---

## Representation learning

Manual features don't scale to KGs with millions of nodes. **Graph representation learning** learns the vectors instead. The book describes three generations: classical dimensionality reduction; word2vec-style methods such as Node2Vec, which treat random walks as sentences; and GNNs, which do for graphs what deep learning did for raw pixels (*KG & LLMs in Action*, ch. 11). [ch. 11 PDF](../sources/kg-and-llms-in-action/ch11-graph-representation-learning-gnns.pdf)

### Encoder–decoder: one frame for everything

Every graph representation learning method is an **encoder** (structure → vector) plus a **decoder** (vector → the property you care about) (ch. 11). Matrix factorisation, Node2Vec's random walks and GNNs differ only in how good the encoder is and which task the decoder serves.

| Part | Takes | Ranges from | Trains on |
|---|---|---|---|
| **Encoder** | Adjacency (structure) and, optionally, node features | A lookup table up to a deep GNN | — |
| **Decoder** | One or two embeddings | Dot product, softmax, a classifier head | The training signal: "are these connected?", neighbourhood overlap, or a node label |

**Node2Vec in this frame** (ch. 11): the encoder generates biased random walks and gives nodes that co-occur on walks similar vectors; the decoder is a softmax asking "given *i*'s vector, how likely is *j* to appear near it on a walk?". The bias comes from the original paper (Grover & Leskovec, 2016): having just stepped from *t* to *v*, the walk moves to a next node *x* with unnormalised weight 1/*p* if *x* = *t* (go back), 1 if *x* is also a neighbour of *t*, and 1/*q* if *x* is farther from *t*. Low *q* pushes the walk outward (DFS-like, finds communities); high *q* keeps it local (BFS-like, finds structural roles). The book's gloss swaps the labels, calling exploring other circles "going broad" and staying in a tight group "going deep"; in the paper's terms that is the other way round. With *p* = *q* = 1 the walk is unbiased, i.e. DeepWalk, and that is what the book runs: its karate listing sets 16 dimensions, walk length 10, 20 walks per node, window 5, *p* = *q* = 1. The book reports the result only qualitatively: the vectors cluster by faction, members with friends in both camps land in between, and the two leaders get distinct vectors. Similarity to each leader predicts which faction a member joins.

Choose the embedding along four axes (ch. 11):

| Axis | Options | Pick by |
|---|---|---|
| What it preserves | **Positional** (where a node sits globally) vs. **structural** (what role it plays locally) | Link prediction and clustering lean positional; classification leans structural, which is where GNNs do well |
| New nodes | **Transductive** (fixed node set) vs. **inductive** (works on unseen nodes) | A graph that grows needs inductive |
| Geometry | **Euclidean** vs. **hyperbolic** | Hyperbolic only with evidence of strong hierarchy (taxonomies, org charts) |
| Supervision | **Unsupervised** (structure alone) vs. **supervised** (labels steer the vectors) | Labels for the task you care about → supervised |

Why hyperbolic suits hierarchies: available space grows exponentially outward, as a tree's node count does, while Euclidean space grows only polynomially. The cost is special distance functions everywhere downstream (indexing, visualisation, interpretation), so it is a whole-pipeline decision, not a model flag (ch. 11). The book's examples: a professional network wants structural vectors for similar roles, inductive learning for new members, and supervision from job titles; a medical KG wants hyperbolic geometry for its term hierarchy.

**Shallow embeddings** (one learned vector per node, as in Node2Vec) are simple but have four limits (ch. 11):

- **Parameters grow with the graph**: a million users means a million vectors.
- **No parameter sharing**: the same role in two parts of the graph is learned twice.
- **Feature-blind**: no natural place for node attributes.
- **Transductive**: a new node has no row in the table, so it means retraining.

They remain a fair baseline for small, static graphs. Those limits are why GNNs exist.

### KG embeddings

KGs are **multirelational**: (Aspirin, TREATS, Headache) and (Aspirin, INHIBITS, COX-2) are different facts about the same pair, so the embedding must encode *how* entities relate, not just *whether* (*KG & LLMs in Action*, ch. 11). That takes two pieces: a loss that scales, and a decoder that understands relation types.

**Loss: negative sampling.** Scoring all pairs is hopeless (a million nodes means about a trillion candidate edges, nearly all absent). Instead, each true triple (u, τ, v) is scored against a few corrupted ones (u, τ, vₙ):

```
L = Σ over true triples [ −log σ(DEC(z_u, τ, z_v))  −  γ · E_{vₙ}[ log σ(−DEC(z_u, τ, z_vₙ)) ] ]
```

The first term rewards a high score for the true fact; the second penalises a high score for the corruption. Because KGs are sparse, γ > 1 is typical, and 5–10 negatives per true triple is the usual budget (ch. 11).

**How you pick negatives matters** (ch. 11):

| Strategy | Example for (Aspirin, TREATS, ?) | Problem it addresses |
|---|---|---|
| Random | Laptop | Cheap, but too easy to teach anything; may hit a true-but-unrecorded edge (filter known triples out) |
| Type-constrained | Another disease | Forces finer distinctions |
| Adversarial | A disease the model currently confuses with the real one | Hardest examples, most signal |
| Corrupt head, tail or both | Sunlight TREATS Headache; Aspirin TREATS Happiness | Avoids a directional bias |

**Decoders** differ in which relation patterns they can represent: symmetric (`similar_to`), asymmetric (`causes`), inverse (`contains` / `part_of`) and compositional (A treats B, B is-a C, so A treats C) (ch. 11):

| Family | Example | Relation is… | Strength | Weakness |
|---|---|---|---|---|
| Translation | TransE | A vector added to the head to land on the tail | Intuitive; handles composition | Many-to-one relations |
| Matrix | RESCAL | A matrix transforming the head | Expressive | Parameter-heavy: one d × d matrix per relation type |
| Semantic matching | DistMult, ComplEx | A relation-conditioned similarity; ComplEx uses complex numbers | ComplEx handles asymmetry | DistMult's score is symmetric in head and tail, so it can't tell `causes` from `caused_by`; both may miss composition |

RESCAL's cost is per relation, not per entity. The book's illustration, "1,000 entities and 100 relationship types, we'd need millions of parameters", holds because of the relation count: 100 matrices at d = 100 is already 1M parameters, whatever the number of entities. DistMult is RESCAL with each matrix restricted to its diagonal (d parameters per relation), which is where its symmetry comes from.

Raieli and Iuculano add two decoders that answer the table's weaknesses (*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 7). **RotatE** models each relation as a rotation in complex space, which covers symmetry, antisymmetry, inversion and composition together. Their examples: marriage is symmetric, and "my nephew is my brother's son" is a composition. **ATTH** embeds in hyperbolic space to keep hierarchies (the geometry row above) together with logical patterns. Their reason for caring about structure: standard embeddings lose a large KG's hierarchies, chains and rings, and those are the structures that reasoning and subgraph extraction depend on (ch. 7, Fig. 7.26). Pick the decoder by the relation patterns your questions use. If they depend on composition or symmetry, DistMult can't represent them.

### Message passing

A GNN layer has each node **aggregate** its neighbours' vectors and **update** its own. After *k* layers a node's embedding encodes its *k*-hop neighbourhood, both its shape (an atom can come to "know" it sits in a benzene ring) and its neighbours' features (a paper absorbs related papers' content) (*KG & LLMs in Action*, ch. 11).

![Message passing for target node A: A aggregates messages from its neighbours D, B and C, and each of those messages was itself aggregated from that neighbour's own neighbours, so two layers reach A's two-hop neighbourhood](../sources/images/negro-kg-and-llms-in-action-fig11-5.png)
*Image Source: Negro et al., Knowledge Graphs and LLMs in Action, Fig. 11.5 (2025)*

The picture is two layers unrolled: the boxes on the right are the first layer's aggregations at D, B and C, and the big box is the second layer's aggregation at A. The basic layer is a normal neural-network layer whose input is a sum over however many neighbours the node has:

```
h_u⁽ᵏ⁾ = σ( W_self · h_u⁽ᵏ⁻¹⁾  +  W_neigh · Σ_{v ∈ N(u)} h_v⁽ᵏ⁻¹⁾  +  b )
          └── UPDATE ──┘          └──── AGGREGATE ────┘
```

*W* can be shared across layers or learned per layer, and the bias is often dropped (ch. 11).

The **self-loop** variant treats a node as its own neighbour, h_u⁽ᵏ⁾ = AGGREGATE({h_v : v ∈ N(u) ∪ {u}}), and uses one weight matrix. The book credits it with simplicity, stability and less overfitting through parameter sharing. The cost is that it can no longer weigh "me" differently from "my neighbours", which matters when a node's own features are its strongest signal (ch. 11). GCN is built this way.

The variants fix specific problems (ch. 11):

**Normalisation** stops high-degree nodes from dominating.

| Scheme | Aggregate | Use when |
|---|---|---|
| Sum | Σ h_v | Degree itself is informative |
| Mean | Σ h_v / \|N(u)\| | Simple degree variance |
| Symmetric (GCN, Kipf & Welling) | Σ h_v / √(\|N(u)\| · \|N(v)\|) | Wide degree range; stops a heavily cited paper from flooding its citers |

Normalisation is lossy: after it, nodes are harder to tell apart by degree. Prefer it when features matter more than structure, or when degree spread destabilises training.

**Attention** (GAT) weights neighbours by relevance instead of equally: m_u = Σ α_uv · h_v, with α_uv a softmax over the neighbourhood of a score aᵀ[W h_u ‖ W h_v] (ch. 11). The book's formula leaves out the LeakyReLU that the original GAT paper (Veličković et al., 2018) and PyG's `GATConv` apply to that score before the softmax. The parameters are one shared *W* and one vector *a* per head; the score is *computed* per edge, not learned per edge. Use it when neighbour importance varies or many edges are noise. **Multi-head attention** is the transformer mechanism applied to a neighbourhood: each head learns its own query/key/value projections and can specialise (bond type vs. spatial layout in a molecule), and the per-edge weights double as an explanation. Some graph transformers also add **structural encodings** (e.g. a learned vector per degree), playing the role positional encodings play for token order.

**Update variants** fight **over-smoothing**, where deep stacks make every node look the same:

| Update | How | Use when |
|---|---|---|
| Skip / concat (GraphSAGE) | Concatenate the node's own vector with the aggregate before the linear layer | Default; keeps the node's original features reachable and helps gradients. (The book also cites GraphSAGE as an example of attention in aggregation; it isn't. Its aggregators are mean, LSTM and pooling.) |
| Gated (GRU-style) | A learned gate mixes old state and new candidate per dimension | Some nodes should stay stable; noisy neighbourhoods (the book suggests citation graphs) |
| Jumping knowledge | Keep every layer's output and combine them (concat, max, or an LSTM) | Different nodes need different hop depths; multiscale structure (the book suggests molecules) |

The choice of update matters as much as the choice of aggregation, and the richer options cost time and memory (ch. 11).

The three layers ch. 12 compares, as PyG implements them (one layer, node *u*, before the activation):

```
GCN   (GCNConv)   h_u' = W · Σ_{v ∈ N(u) ∪ {u}} h_v / √(d̂_u · d̂_v)          d̂ = degree + 1 (self-loop)
SAGE  (SAGEConv)  h_u' = W_root · h_u  +  W_neigh · mean_{v ∈ N(u)} h_v        = W · [h_u ‖ mean h_v]
GAT   (GATConv)   h_u' = Σ_{v ∈ N(u) ∪ {u}} α_uv · W h_v,
                  α_uv = softmax_v( LeakyReLU( aᵀ [W h_u ‖ W h_v] ) )          one (W, a) per head
```

So GCN is self-loops plus symmetric normalisation plus one matrix, SAGE is the concat update with a mean aggregator, and GAT is self-loops plus attention.

### In practice (ch12, PyTorch Geometric)

Ch. 12 runs the same pipeline on two problems and compares three PyG encoders: **GCN**, **GraphSAGE** and **GAT**, each two layers with a ReLU between (*KG & LLMs in Action*, ch. 12). [ch. 12 PDF](../sources/kg-and-llms-in-action/ch12-node-classification-link-prediction.pdf)

```mermaid
flowchart LR
  R[Raw CSVs] --> P["Graph processor<br/>remap IDs to 0..n−1,<br/>edge_index [2, E], features"]
  P --> D["Data (homogeneous)<br/>or HeteroData"]
  D --> E["Encoder<br/>GCN / SAGE / GAT"]
  E --> H["Decoder<br/>log_softmax or dot product"]
  H --> L["Loss<br/>cross-entropy or BCE-with-logits"]
```

| | Node classification: AML (Elliptic) | Link prediction: recommendations (MovieLens) |
|---|---|---|
| Data | 203,769 Bitcoin transactions, 234,355 payment edges, 166 anonymised features; 77% unlabelled, 2.2% illicit | 610 users, 9,742 movies, 100,836 ratings; movie features = 20 one-hot genres; only "rated or not" is predicted |
| Graph | Homogeneous (`Data`) | Heterogeneous (`HeteroData`, users and movies; `ToUndirected()` adds reverse `rev_rates` edges so messages flow both ways; `to_hetero()` converts the base GNN) |
| Input vectors | The 166 features | Users: a learned lookup only (no features). Movies: linear map of genres **plus** a learned lookup. The genre path carries some signal for a new movie, but the lookup is indexed by node ID, so the model is still transductive |
| Decoder | `log_softmax` + cross-entropy | Dot product + binary cross-entropy on logits |
| Splitting | Node masks; most nodes are unlabelled | `RandomLinkSplit`, with **message-passing edges kept apart from supervision edges** to avoid leakage |
| Result | SAGE caught the most illicit nodes (82.7%) and had the best weighted F1; GCN missed 32% | SAGE fewest false positives; GCN best recall |

**Node-classification details.** Unknown-label nodes stay in the graph, so they still pass messages, but a mask keeps them out of the loss and the metrics. The labelled nodes split 80/10/10 at random (37,251 / 4,656 / 4,657), and each split keeps roughly 90% licit / 10% illicit (ch. 12). Elliptic is a time series, and a random node split lets the model train on transactions later than the ones it is tested on; the dataset's authors (Weber et al., 2019) split by time step instead, which is the harder and more honest test.

The book scores with sklearn's `average='weighted'`. That doesn't escape the imbalance: weighting by class support makes the 90% licit class dominate, which is why all three models sit near 0.95–0.98 weighted F1 on validation while catching only 68–83% of illicit nodes. For AML, report the illicit class's own recall and precision (or macro F1).

**Link-prediction details.** The leakage trap is the core lesson. A minimal split:

```python
import torch_geometric.transforms as T
split = T.RandomLinkSplit(
    num_val=0.1, num_test=0.1,
    disjoint_train_ratio=0.3,          # 30% of train edges become labels, never messages
    neg_sampling_ratio=2.0,            # 2 non-edges per positive in val/test
    add_negative_train_samples=False,  # the loader samples fresh negatives each batch
    edge_types=("user", "rates", "movie"),
    rev_edge_types=("movie", "rev_rates", "user"),
)
train, val, test = split(data)
```

If an edge the model is asked to predict is also present in the message-passing graph, the model can simply see it, and training metrics become meaningless. In the book's run the 80,669 training edges split into 56,469 message-passing edges (`edge_index`) and 24,201 supervision edges (`edge_label_index`). Reverse edges are only ever messages. Validation and test reuse all earlier edges for message passing and add their own labelled positives plus sampled negatives (validation: 10,083 positives, 20,166 negatives; test passes messages over 90,753 edges). For graphs that don't fit in memory, `LinkNeighborLoader` samples a subgraph per batch, e.g. 20 neighbours at hop 1 and 10 at hop 2, 128 supervision edges per batch with 2 sampled negatives each (ch. 12).

Check what the loader samples from. As printed, the book's training loader is built with `data=data`, the full graph, while taking `edge_label_index` from `train_data`. Message passing then runs over every rating, including the supervision edges and the validation and test edges: exactly the leakage the split was set up to prevent. Pass `data=train_data` (and `val_data` / `test_data` for the evaluation loaders).

Two PyG gotchas from the chapter: GAT needs its own subclass because the first layer's multi-head output is `hidden × heads` wide and the last layer must not concatenate (`concat=False`); and a heterogeneous "GCN" uses `GraphConv`, not `GCNConv`, because `GCNConv` assumes one node and edge type, whereas `GraphConv` has separate root and neighbour weights. `GraphConv` sums neighbours with no degree normalisation, so the link-prediction "GCN" is really an unnormalised two-matrix layer, structurally the same as SAGE with a sum in place of the mean.

**Cost and confusion matrices** (ch. 12; Colab T4, 400 epochs for AML, 55 for MovieLens; one run each, no seeds or error bars). The AML rates are read from the book's confusion-matrix figure, whose test set (451 illicit, 4,206 licit) doesn't match its split table (476 / 4,181), and the prose gives other counts again (SAGE missing 88 illicit nodes where the figure shows 78). Treat them as one illustrative run:

| Encoder | AML params / time | AML illicit caught | AML licit flagged | Links params / time | Links found (recall) | Non-links wrongly predicted |
|---|---|---|---|---|---|---|
| GCN | 2,723 / 19 s | 68% | 1.2% | 713k / 826 s | **78.6%** | 8.3% |
| GAT | 22,025 / 43 s | 81% | 1.0% | 1.07M / 956 s | 75.4% | 11.7% |
| SAGE | 5,427 / 37 s | **83%** | 1.1% | 713k / 777 s | 71.5% | **5.4%** |

Across both tasks **GAT** had the most parameters and the slowest training. It beat GCN on AML (81% vs. 68% of illicit caught) but never beat SAGE, and on MovieLens it had the most false positives (11.7%). (The book's prose says GAT "struggles with recall" there, but its own test confusion matrix puts GAT's recall at 75.4%, above SAGE's 71.5%.) The book puts its size down to "learnable coefficients for the neighborhood edges"; the counts say otherwise. The AML figures fit exactly with a hidden width of 16 and a 3-way output (the "unknown" class gets an output too, though the mask never trains it): GCN 166·16+16 + 16·3+3 = 2,723; SAGE doubles each weight matrix (root and neighbour) for 5,427; GAT's 8 heads make the first layer 128 wide, 166·128 = 21,248 weights, against only 262 attention parameters, for 22,025. The cost of attention is computing a score on every edge, not storing one. On MovieLens, GCN and SAGE have identical counts (713,408) because `GraphConv` and `SAGEConv` both carry one root and one neighbour matrix per layer, and most of those parameters are the user and movie lookup tables (10,352 rows), which the book names as the main reason link prediction is so much heavier. GCN vs. SAGE is a precision/recall choice. Make it from the cost of each error: AML can't afford missed illicit accounts, and a recommender shouldn't over-suggest. The book's verdicts follow this: SAGE for AML, and GCN as the best overall balance for recommendations despite SAGE's lower false-positive rate.

---

## GNNs and LLMs together

GNNs handle structure and struggle with text. LLMs are the reverse. Ch. 11 names three ways to combine them (*KG & LLMs in Action*, ch. 11). Raieli and Iuculano give the same encoder example, abstracts embedded as node features for a citation network, and add a fourth pattern (*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 7):

| Pattern | Flow | Example |
|---|---|---|
| **LLM as predictor** | GNN encodes the structure; the LLM produces the final output | KG question answering that explains a structural finding |
| **LLM as encoder** | The LLM embeds node text; the GNN propagates it over edges | Paper abstracts as node features for citation prediction |
| **LLM as aligner** | Both run in parallel, aligned by contrastive training | Multimodal KGs where both text and structure matter |
| **LLM as labeller** | The LLM labels nodes zero-shot from their text; the GNN trains on those labels | Topic labels for papers from their titles, instead of paying annotators |

The predictor pattern is what the book's advisory systems do: a structural result (a DWPC ranking, a predicted link) gets explained in domain language. The LLM narrates; it doesn't decide. That is ch. 4's rule for clinical use, where the authors warn against acting on LLM interpretations of clinical-KG findings without expert review, and a reasonable default anywhere (*KG & LLMs in Action*, ch. 4).

The labeller row is worth noting for cost. [The task map](#the-task-map) says node classification needs training, and training needs labels. A zero-shot LLM pass gives a first set of labels quickly, and a person can check a sample of them before the GNN learns from them. The book also mentions fine-tuning the LLM and the GNN jointly (ch. 7).

### When the LLM does the graph reasoning itself

The alternative to pairing an LLM with a GNN is asking the LLM to reason over the graph directly. Raieli and Iuculano separate two kinds of task, following a graph-and-LLM survey ([arXiv 2404.14809](https://arxiv.org/abs/2404.14809), not yet read for this course) (ch. 7):

- **Structure understanding**: degree, path search, shortest path, topological sort, Hamilton path. The first ones are easy and the last two are much harder.
- **Graph learning**: node, edge and graph classification, explaining a node's features, and KG question answering. These need the attributes as well as the structure.

There are three ways to prompt for it: a **manual** prompt with the graph inlined (plus an explanation of the algorithm, such as DFS, if you want it followed), limited by context length; **self-prompting**, where the model rewrites its own prompt over several rounds; and **API-call** prompts, where the model calls graph tools. The fourth option is **supervised fine-tuning** on graph tasks (ch. 7).

The chapter is frank about the limits. LLMs read a graph as linear text and attend to node labels more than to topology. Tokenisation breaks numbers apart, which hurts tasks that count or compare. Training corpora contain little graph data. The models "succeed in solving simple tasks on small graphs, but their performance decays rapidly as both graph and task complexity increase" (ch. 7). The book's evidence that fine-tuning helps is one figure:

![A directed graph listed edge by edge, with the question "Which are the predecessor nodes of node 3?" ChatGPT answers 4, 2 and 6 and misses node 0; the fine-tuned model answers 4, 2, 6 and 0, which is correct](../sources/images/building-ai-agents-llms-rag-kgs-fig7-31.png)
*Image Source: Salvatore Raieli & Gabriele Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), Fig. 7.31*

The figure comes from the paper the book cites ([arXiv 2403.04483](https://arxiv.org/abs/2403.04483), not yet read for this course). It shows a single question. Behind the book's claim that "SFT on graph datasets allows for results that are better than much larger models", the chapter gives one example, not a benchmark. The miss is worth studying anyway. Node 0's edge to 3 is on the **last line** of the list, and ChatGPT's answer goes through the edges in order and leaves that one out. Asking a model to scan a list of edges is a poor way to run a graph algorithm.

The practical rule follows. **Don't ask the model to do what a graph query does exactly.** Degree, paths, predecessors and topological order are one line of Cypher or `networkx`, and both are always right. Give the model those as tools (the API-call approach and the canned traversals of [note 11](11-kg-rag-and-text-to-cypher.md#retrieval-modes)), and keep the model for reading the question and explaining the result. Fine-tune only if you have a graph task no algorithm covers and enough labelled examples.

The chapter ends with **graph-formed reasoning** ([01-prompt note 03](../../01-prompt-engineering/notes/03-core-techniques.md#tree-of-thoughts)). *Think on the graph* treats intermediate thoughts as nodes and their dependencies as edges, as in Graph of Thoughts. It is expensive, with several calls per answer, and used for reasoning problems such as maths. *Verify on the graph* generates several lines of reasoning, joins them in a graph and has a verifier, usually another LLM, look for contradictions between paths. The book's worked example contradicts itself: the question is about "60 miles in 1.5 hours", and the thought nodes it lists are "Distance = 60 km" and "Speed = 40 km/h". The arithmetic is right and the unit has changed. It is an accidental demonstration of the point of verification. A checker that compares each node with the question would have caught it, and a single chain of thought never looks back.


---

## Predictions in a shared graph

A predicted edge is the clearest case of note 12's rule that **claims are not truths**. If a link-prediction model writes into a graph that agents read:

- Write it through the `GraphUpdate` path with a distinct edge type or a `predicted: true` property, the model's `confidence`, and the `run_id` of the training run ([note 12](12-kg-as-shared-agent-memory.md#the-write-path-graphupdate)).
- Keep predicted edges out of default traversals. A query should opt in to them.
- Never feed predicted edges back in as message-passing or supervision edges for the next training run unless they've been confirmed; otherwise the model learns from its own guesses.
- Evaluate on held-out edges, and watch the **false-positive rate**. A false link does what a false merge does in [note 10](10-building-kgs-with-llms.md): every later traversal follows it confidently.

---

## Working reference

`~/.claude/refs/agent-eval.md`: precision/recall trade-offs and held-out evaluation.

Try it: rerun the karate-club comparison 10 times per feature set and report the mean and spread of F1, then tune Node2Vec until it matches the homophily baseline or explain why it can't. On a graph of your own, hold out 10% of one edge type, score candidates with manual pair features (common neighbours, Adamic–Adar, DWPC) and with GraphSAGE plus a dot-product decoder, write the top 20 back as flagged predictions, and read them by hand to count real missing links against hub artefacts.

Depth: [ch. 4 PDF](../sources/kg-and-llms-in-action/ch04-multisource-integration.pdf) (Hetionet, metapaths, DWPC, celiac case), [ch. 9 PDF](../sources/kg-and-llms-in-action/ch09-ml-on-knowledge-graphs.pdf) (task taxonomy, karate club), [ch. 10 PDF](../sources/kg-and-llms-in-action/ch10-graph-feature-engineering.pdf) (manual features, metapaths, DWPC, ReFeX), [ch. 11 PDF](../sources/kg-and-llms-in-action/ch11-graph-representation-learning-gnns.pdf) (embeddings, KG decoders, message passing), [ch. 12 PDF](../sources/kg-and-llms-in-action/ch12-node-classification-link-prediction.pdf) (PyG walkthroughs). Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025), ch. 7: a short survey of KG embeddings, GNNs and LLM graph reasoning.

---

→ Back to the start: [01-graph-vs-loop.md](01-graph-vs-loop.md). Next pillar: [06-eval](../../06-eval/README.md).
