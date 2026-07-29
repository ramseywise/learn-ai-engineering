---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 10: Graph feature engineering: Manual and semiautomated approaches"
confidence: high
cleaned: 2026-07-29
---

# Ch 10 — Graph Feature Engineering: Manual and Semiautomated Approaches

## Overview

ML algorithms (logistic regression, random forests, deep learning) cannot process graph
structures directly — they require numerical input vectors. **Vectorization**
(**featurization**) converts nodes, relationships, or whole graphs into vectors, and the
quality of this representation directly determines downstream model performance
(classification, link prediction, graph-level analysis).

There are two fundamental approaches to building graph-based features:

- **Feature engineering** — manually designed features based on graph properties and
  domain knowledge. Highly interpretable but time-consuming and may miss complex
  patterns. Examples: node degree, clustering coefficients, centrality measures.
- **Representation learning** — automatically learns feature representations from graph
  structure with minimal human input; adapts to specific tasks via training. Captures
  complex patterns more effectively but produces features that are harder to interpret
  (covered in chapters 11–12).

Spectrum of approaches, trading interpretability for efficiency:

| Approach | Interpretability | Effort | Chapter |
|---|---|---|---|
| Manual features | High | High (labor-intensive) | 9, 10 |
| Semiautomated features | Balanced | Medium | 10 |
| Fully automated features | Low | Low (efficient) | 11, 12 |

Manual feature engineering stays valuable for two reasons: (1) it produces interpretable,
human-validatable features, and (2) it informs the design of automated approaches. A
further advantage: manually extracted features — being based on well-understood graph
algorithms — are easier for **LLMs** to interpret and reason about autonomously.

The chapter's running example is a **fraud detection network**: a social graph where black
nodes are known fraudsters (D, E, F, I) and white nodes are legitimate or unlabeled. The
goal is node classification — predict whether an unlabeled node is a fraudster.

```python
import networkx as nx

def create_fraud_network():
    G = nx.Graph()
    fraudsters = ['D', 'E', 'F', 'I']
    nodes = ['A','B','C','D','E','F','G','H','I','J',
             'K','L','M','N','O','P','Q','R','S','T']
    G.add_nodes_from(nodes)
    for node in G.nodes():
        G.nodes[node]['is_fraudster'] = node in fraudsters
    edges = [
        ('A','B'), ('A','G'), ('A','H'), ('A','I'), ('A','O'),
        ('A','T'), ('B','D'), ('B','C'), ('D','E'), ('D','F'),
        ('D','G'), ('E','F'), ('F','G'), ('G','I'), ('H','K'),
        ('I','K'), ('I','N'), ('K','J'), ('L','M'), ('L','N'),
        ('N','M'), ('O','P'), ('O','Q'), ('Q','R'), ('Q','S')
    ]
    G.add_edges_from(edges)
    return G
```

## 10.1 Manual Node Features

A classifier (logistic regression, decision tree, random forest, etc.) needs each node
represented as a feature vector. Features fall into two categories:

- **Local features** — extracted from a node's one-hop neighborhood, or **egonet**
  (**ego** = center node, **alters** = surrounding neighbors). Can extend to an
  *n*-order neighborhood (*n* hops from the node).
- **Global features** — measure a node's role across the entire network or a large
  portion of it (not just the egonet). Includes centrality metrics: betweenness,
  closeness, Eigenvector centrality, PageRank. These capture influence and how a node is
  influenced by others.

The chapter builds features incrementally, local → global, showing how each new metric
adds a dimension to the node representation.

### 10.1.1 Degree

**Degree** = number of neighbors a node has. In the fraud context, split into:

- **Fraud degree** — count of neighbors marked as fraudsters
- **Legit degree** — total degree minus fraud degree

More fraudulent direct neighbors raises the chance the node itself is a fraudster.

```python
def compute_degree_metrics(G):
    degree_metrics = {}
    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        total_degree = len(neighbors)
        fraud_degree = sum(1 for neighbor in neighbors
                            if G.nodes[neighbor].get('is_fraudster', False))
        legit_degree = total_degree - fraud_degree
        degree_metrics[node] = {
            'total_degree': total_degree,
            'fraud_degree': fraud_degree,
            'legit_degree': legit_degree
        }
    return degree_metrics
```

Example: node D has 4 total neighbors, 2 fraudulent, 2 legitimate.

### 10.1.2 Triangles

A **triangle** is a subgraph of three mutually connected nodes (A–B, A–C, B–C all exist).
Triangles indicate strong local clustering — "your friends are probably friends with each
other." A triangle is classified by the fraud status of its members:

- **Fraudulent triangle** — both alters (besides the target) are fraudsters
- **Legitimate triangle** — neither alter is a fraudster
- **Semifraudulent triangle** — exactly one alter is a fraudster

```python
def compute_triangle_metrics(G):
    triangle_metrics = {}
    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        triangles = []
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                if G.has_edge(neighbors[i], neighbors[j]):
                    triangles.append((neighbors[i], neighbors[j]))

        total_triangles = len(triangles)
        fraud_triangles = legit_triangles = semi_fraud_triangles = 0
        for n1, n2 in triangles:
            n1_fraud = G.nodes[n1].get('is_fraudster', False)
            n2_fraud = G.nodes[n2].get('is_fraudster', False)
            if n1_fraud and n2_fraud:
                fraud_triangles += 1
            elif not n1_fraud and not n2_fraud:
                legit_triangles += 1
            else:
                semi_fraud_triangles += 1

        triangle_metrics[node] = {
            'total_triangles': total_triangles,
            'fraud_triangles': fraud_triangles,
            'legit_triangles': legit_triangles,
            'semi_fraud_triangles': semi_fraud_triangles
        }
    return triangle_metrics
```

### 10.1.3 Density

**Density** measures the extent to which nodes in a graph are connected — the portion of
all possible edges that actually exist. For a fully connected graph of *N* nodes, the
total possible edges is:

```
(N choose 2) = N(N-1)/2
```

If *M* is the number of actual edges, network density is:

```
d = M / (N choose 2) = 2M / (N(N-1))
```

Density can also be computed **per node** using its egonet: e.g., node A's egonet has 7
nodes (A + 6 neighbors), so max possible edges = 7·6/2 = 21; if 7 edges are observed,
density = 7/21 ≈ 0.33. Unlike degree/triangles, density has no fraud-specific variant
(no "fraud density").

```python
def compute_density_metrics(G):
    density_metrics = {}
    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        egonet_nodes = neighbors + [node]
        N = len(egonet_nodes)
        if N < 2:
            density_metrics[node] = 0.0
            continue
        M = 0
        for i in range(len(egonet_nodes)):
            for j in range(i + 1, len(egonet_nodes)):
                if G.has_edge(egonet_nodes[i], egonet_nodes[j]):
                    M += 1
        max_possible_edges = (N * (N - 1)) / 2
        density = M / max_possible_edges
        density_metrics[node] = round(density, 2)
    return density_metrics
```

### 10.1.4 Geodesic (Shortest) Path

The **geodesic path** (**shortest path**) is the minimum distance between two nodes. For
fraud detection, the relevant question is: how close is a node to *known fraudulent*
nodes, and how many such paths exist? More/shorter paths to fraudsters implies higher
contamination risk. Features extracted:

- `geodesic_path` — shortest distance to the nearest fraudulent node (0 if the node
  itself is fraudulent)
- `#1-hop_paths`, `#2-hop_paths`, `#3-hop_paths` — count of paths to fraudster nodes at
  each hop distance, up to `max_hops`

> **Note (verbatim):** "Dijkstra's algorithm finds the shortest path between nodes in a
> graph by iteratively selecting the unvisited node with the smallest tentative distance,
> calculating distances through it to each unvisited neighbor, and marking the node as
> visited. The algorithm efficiently builds up the shortest path tree one vertex at a
> time."

```python
import networkx as nx
from collections import defaultdict

def compute_geodesic_metrics(G, max_hops=3):
    path_metrics = {}
    fraudster_nodes = [n for n, attr in G.nodes(data=True)
                        if attr.get('is_fraudster', False)]

    for node in G.nodes():
        if G.nodes[node].get('is_fraudster', False):
            geodesic_path = 0
            hop_counts = defaultdict(int)
        else:
            paths_to_fraudsters = []
            hop_counts = defaultdict(int)
            for fraudster in fraudster_nodes:
                try:
                    path = nx.shortest_path(G, node, fraudster)
                    path_length = len(path) - 1
                    paths_to_fraudsters.append(path_length)
                    if path_length <= max_hops:
                        hop_counts[path_length] += 1
                except nx.NetworkXNoPath:
                    continue
            geodesic_path = min(paths_to_fraudsters) if paths_to_fraudsters else float('inf')

        path_metrics[node] = {
            'geodesic_path': geodesic_path,
            '#1-hop_paths': hop_counts[1],
            '#2-hop_paths': hop_counts[2],
            '#3-hop_paths': hop_counts[3]
        }
    return path_metrics
```

This implementation computes distance from each node to fraudster nodes only, up to a
predefined hop limit — not full all-pairs shortest paths.

### 10.1.5 Closeness

**Closeness centrality** represents how "close" a node is to all other nodes. First,
compute mean geodesic distance ("farness") from node *i* to all other nodes:

```
g(v_i) = ( Σ_{j=1, j≠i}^{N} d(v_i, v_j) ) / (N - 1)
```

- Numerator sums shortest-path distances from node *i* to every other node *j*
  (excluding itself).
- Denominator *(N-1)* is the count of other nodes.

Closeness centrality is the **inverse of farness** — central nodes get higher scores:

```
closeness_centrality(v_i) = ( Σ_{j=1, j≠i}^{N} d(v_i, v_j) / (N-1) )^{-1}
```

A node with many direct connections has small shortest paths to others → low `g(v_i)` →
well-connected/central. In fraud detection, a fraudulent node with low `g(v_i)` (i.e.,
high closeness) suggests fraud could spread quickly through the network.

Two practical problems and fixes:
- Closeness values across nodes can cluster tightly — inspect decimal places to see
  differences.
- When a node can't reach another (disconnected components), distance is infinite. Fix:
  exclude unreachable nodes and normalize only over the **reachable** portion of the
  network, rather than the full node count.

```python
import networkx as nx

def compute_closeness_metrics(G):
    closeness_metrics = {}
    for node in G.nodes():
        total_distance = 0
        reachable_nodes = 0
        shortest_paths = nx.single_source_shortest_path_length(G, node)
        for other_node, distance in shortest_paths.items():
            if other_node != node:
                total_distance += distance
                reachable_nodes += 1
        n = len(G.nodes()) - 1
        if reachable_nodes > 0 and n > 0:
            closeness = (reachable_nodes / n) * (reachable_nodes / total_distance)
        else:
            closeness = 0.0
        closeness_metrics[node] = round(closeness, 2)
    return closeness_metrics
```

In the example graph, node A is the most closely connected node overall (closeness =
0.5); nodes R and S are the farthest from everyone else (0.24).

### 10.1.6 Betweenness

**Betweenness centrality** measures how often a node acts as a **bridge** on shortest
paths between other node pairs — a different lens than closeness (which measures reach
speed). A node with high betweenness controls information flow between many other nodes.

```
betweenness(v) = Σ_{s,t (s≠t≠v)} σ_st(v) / σ_st
```

where `σ_st` = total number of shortest paths between nodes *s* and *t*, and `σ_st(v)` =
number of those paths passing through node *v*. The sum is taken over all pairs *s, t*
where neither equals *v*.

```python
import networkx as nx

def compute_betweenness_metrics(G, normalized=True):
    betweenness_metrics = {}
    betweenness = nx.betweenness_centrality(G, normalized=normalized, endpoints=False)
    for node in G.nodes():
        betweenness_metrics[node] = round(betweenness[node], 3)
    return betweenness_metrics

def identify_potential_bottlenecks(G, threshold=0.5):
    metrics = compute_betweenness_metrics(G)
    return {node: score for node, score in metrics.items() if score > threshold}
```

`networkx`'s betweenness is normalized by default (scaled 0–1), making values comparable
across networks. In the example graph, node A has betweenness 104 (unnormalized in the
table shown) — a crucial bridge controlling much of the network's information flow.
Nodes C, E, J, L, M, P, R, S, T all have betweenness 0 — they never act as bridges.

### 10.1.7 PageRank

**PageRank** measures node importance based on the structure of incoming connections —
originally developed by Google to rank web pages. Unlike simpler centrality measures, it
considers not just the quantity of connections but their *quality*: a node connected to
other highly ranked nodes receives a higher PageRank score.

Two variants computed for fraud detection:
- **Base PageRank** — treats all connections equally.
- **Fraud-weighted PageRank** — uses `personalization` weighting so connections from
  known fraudulent nodes carry more weight (e.g., weight 2.0 vs. 1.0 for legit nodes),
  revealing a node's specific relationship to fraudulent activity vs. its general network
  importance.

```python
import networkx as nx

def compute_pagerank_metrics(G, fraud_weight=2.0, damping_factor=0.85):
    pagerank_metrics = {}
    base_pagerank = nx.pagerank(G, alpha=damping_factor,
                                 personalization=None, weight=None)

    fraud_personalization = {}
    for node in G.nodes():
        if G.nodes[node].get('is_fraudster', False):
            fraud_personalization[node] = fraud_weight
        else:
            fraud_personalization[node] = 1.0

    fraud_pagerank = nx.pagerank(G, alpha=damping_factor,
                                  personalization=fraud_personalization, weight=None)

    for node in G.nodes():
        pagerank_metrics[node] = {
            'pagerank_base': round(base_pagerank[node], 3),
            'pagerank_fraud': round(fraud_pagerank[node], 3)
        }
    return pagerank_metrics
```

Example finding: node A has the highest **base** PageRank (0.108, general importance),
but node D has the highest **fraud-weighted** PageRank (0.168) despite not leading on
base PageRank — indicating D has stronger connections to fraudulent activity than its
overall network position suggests. Divergence between base and fraud-weighted PageRank
flags nodes worth closer investigation.

### 10.1.8 Prediction

The extraction process is iterative — keep adding features until classifier quality is
sufficient. All metrics are assembled into one feature vector per node, converted to a
pandas DataFrame, then fed to a classifier (logistic regression, consistent with ch. 9).

```python
def create_node_features_dataset(G):
    degree_metrics = compute_degree_metrics(G)
    triangle_metrics = compute_triangle_metrics(G)
    density_metrics = compute_density_metrics(G)
    path_metrics = compute_geodesic_metrics(G)
    closeness_metrics = compute_closeness_metrics(G)
    betweenness_metrics = compute_betweenness_metrics(G)
    pagerank_metrics = compute_pagerank_metrics(G)

    features_dict = {}
    for node in G.nodes():
        features_dict[node] = {
            'total_degree': degree_metrics[node]['total_degree'],
            'fraud_degree': degree_metrics[node]['fraud_degree'],
            'legit_degree': degree_metrics[node]['legit_degree'],
            'total_triangles': triangle_metrics[node]['total_triangles'],
            'fraud_triangles': triangle_metrics[node]['fraud_triangles'],
            'legit_triangles': triangle_metrics[node]['legit_triangles'],
            'semi_fraud_triangles': triangle_metrics[node]['semi_fraud_triangles'],
            'density': density_metrics[node],
            'geodesic_path': path_metrics[node]['geodesic_path'],
            'paths_1hop': path_metrics[node]['#1-hop_paths'],
            'paths_2hop': path_metrics[node]['#2-hop_paths'],
            'paths_3hop': path_metrics[node]['#3-hop_paths'],
            'closeness': closeness_metrics[node],
            'betweenness': betweenness_metrics[node],
            'pagerank_base': pagerank_metrics[node]['pagerank_base'],
            'pagerank_fraud': pagerank_metrics[node]['pagerank_fraud'],
            'is_fraudster': G.nodes[node]['is_fraudster']  # label
        }
    return pd.DataFrame.from_dict(features_dict, orient='index')
```

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix

def train_fraud_classifier(G):
    df = create_node_features_dataset(G)
    X = df.drop('is_fraudster', axis=1)
    y = df['is_fraudster']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    clf = LogisticRegression(random_state=42, max_iter=1000)
    clf.fit(X_train_scaled, y_train)
    y_pred = clf.predict(X_test_scaled)

    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': abs(clf.coef_[0])
    }).sort_values('importance', ascending=False)

    return {
        'classification_report': classification_report(y_test, y_pred),
        'confusion_matrix': confusion_matrix(y_test, y_pred),
        'feature_importance': feature_importance,
        'model': clf,
        'scaler': scaler
    }
```

The **stratified split** (`stratify=y`) preserves the fraud/legit proportion in both
train and test sets. `StandardScaler` normalizes feature scale, important for logistic
regression. A key advantage of this manual approach: even though the process is complex,
each extracted feature is easy to explain by looking at the graph — valuable when
database size is limited or explainability matters.

## 10.2 Manual Relationship Features

Beyond node classification, **relationship prediction** (**link prediction**) asks:
given two nodes, how likely is a relationship between them? Framed as binary
classification (does a link exist or not) or multiclass (what type of relationship).

Worked example: **drug repurposing** — finding new therapeutic uses for existing drugs,
modeled as link prediction between **compounds** and **diseases** on the **Hietonet**
dataset (19 public databases, 50,000+ nodes: drugs, diseases, genes, symptoms — same
dataset as ch. 4/9).

Two distinct approaches to represent a node pair for link prediction:

- **Node-based combination** — derive the relationship representation by combining the
  feature vectors of source and target nodes (concatenation, element-wise operations).
- **Path-based features** — characterize relationships by analyzing the ways nodes are
  connected in the graph (e.g., number of two-hop paths, presence of specific
  **metapaths**), capturing structural context rather than node identity.

Node-based combinations work well with node embeddings; path-based features excel at
capturing complex network patterns.

### 10.2.1 Node-Based Representation

Combine two node feature vectors *u* and *v* of length *n* into one relationship vector.
Common composition operators:

| Operator | Definition | Output length | Example (u=[1,2], v=[3,4]) |
|---|---|---|---|
| **Catenate** | join *u* end-to-end with *v* | 2n | [1,2,3,4] |
| **Average** | element-wise mean `(u[i]+v[i])/2` | n | (u=[2,4],v=[4,8]) → [3,6] |
| **L1 (Manhattan distance)** | `\|u[i] - v[i]\|` per element | n | (u=[1,4],v=[3,1]) → [2,3] |
| **L2 (Euclidean distance)** | `(u[i]-v[i])^2` per element | n | (u=[1,4],v=[3,1]) → [4,9] |
| **Hadamard (element-wise product)** | `u[i] * v[i]` per element | n | (u=[2,4],v=[3,1]) → [6,4] |

```python
def catenate(u, v):
    return u + v

def operator_avg(u, v):
    return (u + v) / 2.0

def operator_l1(u, v):
    return np.abs(u - v)

def operator_l2(u, v):
    return (u - v) ** 2

def operator_hadamard(u, v):
    return u * v
```

There's no generic rule for which operator to use — benchmark to find the best fit for
your scenario. Link prediction quality depends directly on the quality of the node
representations *and* the choice of composition operator.

### 10.2.2 Path-Based Features

Path-based features describe a node pair using the paths connecting them, independent of
(or in addition to) individual node representations. This process is manual and
domain-specific.

**Metagraph** and **metapath**: a metapath is a typed sequence of relationship types
connecting a source type to a target type through the schema (metagraph). Example
metapaths between **Compound** and **Disease** in Hietonet:

| Metapath | Length | Abbr. |
|---|---|---|
| Compound–binds–Gene–associates–Disease | 2 | CbGaD |
| Compound–downregulates–Gene–upregulates–Disease | 2 | CdGuD |
| Compound–resembles–Compound–treats–Disease | 2 | CrCtD |
| Compound–binds–Gene–binds–Compound–treats–Disease | 3 | CbGbCtD |
| Compound–binds–Gene–expresses–Anatomy–localizes–Disease | 3 | CbGeAlD |
| Compound–binds–Gene–interacts–Gene–interacts–Gene–associates–Disease | 4 | CbGiGiGaD |
| Compound–binds–Gene–participates–Pathway–participates–Gene–associates–Disease | 4 | CbGpPWpGaD |

For each compound–disease pair, one feature value is computed per metapath (regardless
of whether a direct connection exists), forming a feature matrix: rows = compound–disease
pairs, columns = metapaths.

Naively **counting distinct path instances** per metapath is biased: highly connected
("hub") genes inflate path counts without indicating meaningful biological relationships.

**Degree-weighted path count (DWPC)** corrects this by damping paths through
high-degree intermediate nodes:

- Each path is weighted inversely to the degrees of its intermediate nodes.
- Nodes with many connections contribute less to the final score.
- The damping effect highlights more specific, focused biological pathways.

Example: two paths between metformin and type 2 diabetes — one through a highly connected
gene (degree 100), another through a more specific gene (degree 10). The second path
contributes more to the DWPC score.

```cypher
// Listing 10.15 — DWPC between metformin and type 2 diabetes for CbGaD
MATCH path = (c:Compound)-[:BINDS_CbG]-(g:Gene)-[:ASSOCIATES_DaG]-(d:Disease)
WHERE c.name = 'Metformin' AND d.name = 'type 2 diabetes mellitus'
WITH
[
  count((v)-[:BINDS_CbG]-()),
  count(()-[:BINDS_CbG]-(g)),
  count((g)-[:ASSOCIATES_DaG]-()),
  count(()-[:ASSOCIATES_DaG]-(d))
]
AS degrees, path, d
WITH
  d.identifier AS disease_id,
  d.name AS disease_name,
  count(path) AS PC,
  sum(reduce(pdp = 1.0, d in degrees| pdp * d ^ -0.4)) AS DWPC
RETURN
  disease_id, disease_name, PC, DWPC
```

Running this on Hietonet gives DWPC = 0.0007 for the Metformin–Type 2 Diabetes /
CbGaD pair. Similar queries (listings 10.16, 10.17) compute DWPC for CbGeAlD and
CbGpPWpGaD metapaths by chaining additional relationship hops and degree terms.

Computing DWPC across **all** possible compound–disease pairs and metapaths is
computationally expensive and can introduce noise. Himmelstein et al. used a two-step
reduction:

1. **Metapath reduction** — a statistical method identifies the most significant
   metapaths by analyzing frequency in known treatment vs. non-treatment relationships,
   reducing relevant metapaths from 1,026 to 709 while maintaining predictive power.
2. **Pair selection** — domain knowledge plus degree-based probabilistic analysis
   identifies the most promising compound–disease pairs, reducing computational overhead
   and improving classifier performance by focusing on the most relevant pairs.

Node-based combination (10.2.1) is simpler but often performs worse than path-based
features when working with manually extracted node features; it becomes more effective
when features are automatically extracted (chapters 11–12).

### Using LLMs for Graph Feature Engineering

LLMs can support graph feature engineering in three ways:

- **Query generation** — translate metapath descriptions into optimized Cypher queries.
- **Feature engineering** — suggest relevant patterns/relationships that might not be
  immediately obvious.
- **Code generation** — help build infrastructure to execute and process query results.

Example prompt structure for generating Cypher queries across multiple metapaths: supply
the LLM with (1) the graph schema (e.g., from `apoc.meta.schema()`), (2) an example query
for one metapath (e.g., CbGaD), (3) the list of target metapaths, and (4) sample node
names for testing. Ask it to generate, for each metapath, a query computing both Path
Count (PC) and DWPC (with a specified damping factor), returning `disease_id`,
`disease_name`, `PC`, `DWPC`. This seeds a workflow where LLMs draft the boilerplate
Cypher and the practitioner refines it — this is a prompting pattern, not a
production-ready pipeline.

## 10.3 Semiautomated Feature Extraction: ReFeX

Manual feature engineering (10.1–10.2) gives deep insight but requires extensive domain
expertise and must be customized per use case. **ReFeX (Recursive Feature eXtraction)**
offers a middle ground between fully manual engineering and fully automated
representation learning (chapters 11–12): it automatically identifies and extracts
relevant structural features while remaining transparent, interpretable, and
deterministic.

Key advantages:

- **Efficiency** — automated extraction of recursive structural features.
- **Consistency** — systematic, repeatable feature generation.
- **Interpretability** — generated features retain clear structural meaning.
- **Scalability** — handles larger graphs while maintaining feature quality.

ReFeX still needs human oversight — domain experts **validate** relevance, **incorporate**
domain knowledge into feature selection, **understand/explain** each feature's
contribution, and **modify** the extraction process per specific requirements.

ReFeX operates on **pure graph topology** — nodes and relationships without labels or
types — following two founding rules:

- **Structural** — construction of the feature matrix *F* should not require additional
  attribute information on nodes or links.
- **Effective** — good node features should (1) help predict node attributes when such
  attributes are available, and (2) be transferable across graphs (e.g., when the graph
  changes over time).

Feature extraction proceeds in three stages:

1. **Local feature extraction** — immediate node characteristics, primarily **degree**
   (weighted and unweighted). For directed graphs, in-degree and out-degree are computed
   separately; weighted degree = sum of incident edge weights.
2. **Egonet feature extraction** — metrics on each node's immediate neighborhood:
   number of incoming egonet edges, outgoing egonet edges, and total egonet edges (plus
   weighted variants).
3. **Recursive feature extraction** — aggregates existing features via summary
   statistics (**sum**, **mean**) applied recursively, capturing increasingly complex
   regional patterns (e.g., `degree(sum)(mean)(sum)` reaches beyond the immediate
   neighborhood). For directed graphs, computed separately for incoming/outgoing paths.

Because recursion can generate an exponentially growing number of features, ReFeX applies
pruning techniques:

- **Correlation analysis** — identifies and eliminates highly correlated feature pairs.
- **Logarithmic binning** — maps feature values to discrete intervals for efficient
  comparison.
- **Threshold-based pruning** — removes features that differ by less than a specified
  threshold.

### 10.3.1 Performing ReFeX Manually

Worked on the small fraud network (figure 10.9), treated as **undirected and
unweighted** with no pruning applied — node types/colors are ignored since ReFeX doesn't
consider them.

**Step 1 — local feature (degree):** same values as section 10.1.1 (e.g., A=6, B=3, C=1,
D=4, E=2).

**Step 2 — egonet features:** for node A, egonet = {A, B, G, H, I, O, T} (7 nodes: A plus
6 neighbors). Internal edges = 7 (6 edges connecting A to neighbors, plus 1 edge between
G and I). In/out egonet edges = 9 (edges connecting egonet nodes to nodes outside:
B→C,D; G→D,F; H→K; I→K,N; O→P,Q).

**Step 3 — recursive feature aggregation** (multi-phase, using node A as example):

*First iteration* — A's neighbors are H, I, G, B, T, O with degrees 2, 4, 4, 3, 1, 3
respectively.

```
sum(neighbor_degrees) = degree(H)+degree(I)+degree(G)+degree(B)+degree(T)+degree(O)
                       = 2 + 4 + 4 + 3 + 1 + 3 = 17
mean(neighbor_degrees) = 17 / 6 ≈ 2.83
```

*Second iteration* — each neighbor now carries its first-iteration sum (agg); aggregate
those:

```
sum(neighbor_aggregates) = agg(B)+agg(G)+agg(H)+agg(I)+agg(O)+agg(T)
                          = 11 + 17 + 9 + 16 + 10 + 6 = 69
mean(neighbor_aggregates) = 69 / 6 = 11.5
```

Final feature table for node A (before pruning):

| Feature type | Feature | Value |
|---|---|---|
| Local feature | Degree | 6 |
| Egonet feature | Number of edges in egonet | 7 |
| Recursive, 1st iteration | Sum of neighbor degrees | 17 |
| Recursive, 1st iteration | Mean of neighbor degrees | 2.83 |
| Recursive, 2nd iteration | Sum of neighbor sums | 69 |
| Recursive, 2nd iteration | Mean of neighbor sums | 11.5 |

### 10.3.2 Performing ReFeX Automatically with Code

```python
import networkx as nx
import numpy as np
from collections import defaultdict
from sklearn.preprocessing import StandardScaler

class ReFeX:
    def __init__(self, max_iterations=2, correlation_threshold=0.95):
        self.max_iterations = max_iterations
        self.correlation_threshold = correlation_threshold

    def extract_features(self, G):
        features = self._extract_local_features(G)
        egonet_features = self._extract_egonet_features(G)
        features = np.column_stack((features, egonet_features))

        for iteration in range(self.max_iterations):
            new_features = self._generate_recursive_features(G, features)
            features = np.column_stack((features, new_features))
            features = self._prune_features(features)
        return features

    def _extract_local_features(self, G):
        """Extract local (node-level) features"""
        n_nodes = G.number_of_nodes()
        features = np.zeros((n_nodes, 3))
        for idx, node in enumerate(G.nodes()):
            features[idx, 0] = G.degree(node)
            if G.is_directed():
                features[idx, 1] = G.in_degree(node)
                features[idx, 2] = G.out_degree(node)
            else:
                features[idx, 1] = features[idx, 2] = G.degree(node)
        return features

    def _extract_egonet_features(self, G):
        n_nodes = G.number_of_nodes()
        features = np.zeros((n_nodes, 3))
        for idx, node in enumerate(G.nodes()):
            ego = nx.ego_graph(G, node, radius=1)
            features[idx, 0] = ego.number_of_nodes()
            features[idx, 1] = ego.number_of_edges()
            features[idx, 2] = nx.density(ego)
        return features

    def _generate_recursive_features(self, G, current_features):
        n_nodes = G.number_of_nodes()
        n_features = current_features.shape[1]
        new_features = np.zeros((n_nodes, n_features * 2))
        for idx, node in enumerate(G.nodes()):
            neighbors = list(G.neighbors(node))
            if not neighbors:
                continue
            neighbor_feats = current_features[[list(G.nodes()).index(n) for n in neighbors]]
            new_features[idx, :n_features] = np.sum(neighbor_feats, axis=0)
            new_features[idx, n_features:] = np.mean(neighbor_feats, axis=0)
        return new_features

    def _prune_features(self, features):
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        corr_matrix = np.corrcoef(scaled_features.T)
        to_remove = set()
        for i in range(corr_matrix.shape[0]):
            for j in range(i + 1, corr_matrix.shape[1]):
                if abs(corr_matrix[i, j]) > self.correlation_threshold:
                    to_remove.add(j)
        keep_features = list(set(range(features.shape[1])) - to_remove)
        return features[:, keep_features]
```

The full implementation connecting to a Neo4j-backed Hietonet database is in the book's
code repository.

ReFeX represents a significant step toward automated feature extraction, occupying an
important middle ground between manual feature engineering and fully autonomous
representation learning. Its focus on pure graph structure demonstrates how structural
patterns alone can capture meaningful characteristics of nodes and their neighborhoods.
Although automated, it remains transparent and verifiable step by step — valuable for
practitioners who must validate their feature engineering process. Its **deterministic**
nature (identical inputs → identical outputs) is valuable in production environments
where reproducibility matters, and when the graph changes, ReFeX allows selective
recomputation of affected features rather than a full regeneration — useful in dynamic
graph environments.

**Limitations**: reliance on structural features means ReFeX cannot directly incorporate
node attributes or edge types, and although pruning helps manage complexity, it sometimes
requires human oversight to ensure optimal feature selection. The next chapter covers
fully automated representation learning, trading some of this interpretability and
determinism for more sophisticated pattern recognition.

## Takeaways

- **Manual feature engineering** builds interpretable node features by combining local
  metrics (degree, triangles, density, egonet structure) with global centrality measures
  (closeness, betweenness, PageRank); each feature is traceable back to a graph property,
  which matters for explainability and small/limited datasets.
- **Relationship (link prediction) features** come from two families: node-based
  combination operators (catenate, average, L1, L2, Hadamard) applied to node feature
  vectors, or path-based features like **metapaths** that describe structural connectivity
  directly.
- **DWPC (degree-weighted path count)** fixes the hub-node bias of naive path counting by
  damping contributions from high-degree intermediate nodes, surfacing biologically
  specific (or domain-specific) connections — demonstrated on Hietonet drug repurposing.
- LLMs are useful assistants for graph feature engineering: translating metapath
  descriptions into Cypher, suggesting non-obvious relevant patterns, and generating
  supporting code — because manually-defined features are well-understood enough for an
  LLM to reason about.
- **ReFeX** is a semiautomated middle ground: it recursively extracts local, egonet, and
  aggregated (sum/mean) structural features from pure topology (no attribute
  dependence), then prunes via correlation analysis — automated yet interpretable and
  deterministic.
- The manual-vs-semiautomated choice depends on interpretability needs, available compute,
  and domain expertise on hand; both still require careful feature pruning/selection
  before feeding a downstream classifier.
