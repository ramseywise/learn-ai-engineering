---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 9: Machine learning on knowledge graphs: A primer approach"
confidence: high
cleaned: 2026-07-29
---

# Ch 9 — Machine Learning on Knowledge Graphs: A Primer

## Why ML on Graphs

Building KGs supports querying, navigation, and statistical validation — but extracting
insight users cannot get on their own requires **machine learning** on top of the graph.
This is the core of **intelligent advisory systems (IASs)**: e.g., navigating a disease/
protein/gene/compound graph to find drug-repurposing opportunities, or combining patient
data with literature to build personalized treatment plans.

Three reasons ML on graphs is often the best (or only feasible) approach:

- **Data representation** — graphs are a universal representation; matrices, tensors,
  sequences, and time series from diverse systems can all be transformed into graphs.
- **Problem modeling** — a large set of real-world problems reduce to a small set of
  graph computational tasks. Anomaly detection and medication suggestion are both node
  classification; recommendations and interaction discovery are relationship prediction.
- **Data item dependency** — traditional ML assumes data points are **independent and
  identically distributed (i.i.d.)**. Real-world data is often intrinsically connected;
  ignoring those relationships produces incomplete or wrong results. Storing data as
  graphs and computing over them captures this dependency structure.

**GNN + LLM integration** is a powerful combination for IASs: GNNs detect complex
structural patterns (e.g., patient similarity networks, biological pathway graphs) while
LLMs synthesize natural-language context (literature, guidelines) to explain results in
domain-appropriate language — making structural insights accessible and actionable.

ML is problem-driven: choose the best tool for the business goal. For many scenarios in
this book's remaining chapters, ML on graphs will be that tool.

## Task Taxonomy: Node-Focused vs. Graph-Focused

Classical ML divides algorithms into **supervised** (labeled data, predict labels for the
rest — e.g., a spam filter) and **unsupervised** (fully unlabeled, extract patterns/
clusters). These categories remain valid for graphs but are **not the most useful
distinction** — node classification is "supervised" only loosely, and doesn't fit the
classical definition cleanly (see semisupervised discussion below).

Instead, ML tasks on graphs split into two categories:

- **Node-focused tasks** — the entire dataset is one graph; nodes and relationships are
  the data points.
- **Graph-focused tasks** — the dataset is a *set* of graphs; each data point is an
  entire graph.

| Category | Data point | Example output |
|---|---|---|
| Node-focused | node or relationship within one graph | class label, link probability |
| Graph-focused | an entire graph | graph class, graph-level function/property |

## Node-Focused Tasks

### Node Classification

Given a graph with a small set of manually labeled nodes, predict the label `y_u` for
every unlabeled node `u`, using only a training subset `V_train ⊂ V`. Classic use cases:
detecting bots in a social network, classifying protein function in an interactome,
classifying document topic from citation/hyperlink graphs.

Flow (two phases, mirroring supervised ML):

1. **Training** — take the graph as input, extract features for nodes using graph
   structure/node/relationship properties, produce a model.
2. **Classification/prediction** — use the same featurization on target (unlabeled)
   nodes, feed to the model, get predicted classes.

**Why it's not classical supervised learning**: nodes in a graph violate the i.i.d.
assumption. Real network patterns break independence and identical distribution in
distinct ways:

- **Homophily** — nodes influence each other via relationships, sharing interests,
  attributes, and behaviors with neighbors (common in social networks). Effective models
  must consider both node features *and* network relationships.
- **Structural equivalence** — in networks like protein interaction graphs, nodes with
  similar neighborhood structure tend to share functional properties, regardless of
  direct connection.
- **Heterophily** — the opposite pattern: nodes preferentially connect to others with
  *different* characteristics.

> **Is node classification supervised or unsupervised?** Many researchers call it
> **semisupervised** [9]: training typically has access to the full graph, including all
> unlabeled (test) nodes — only their *labels* are missing. Neighborhood information about
> test nodes can still improve training. This differs from standard supervised learning,
> where unlabeled points are wholly unobserved during training. Standard semisupervised
> learning also assumes i.i.d., which doesn't hold here — node classification does not
> cleanly fit classical categories.

Node classification generalizes to **multilabel** classification: e.g., Flickr users
belong to multiple interest groups simultaneously, and the task predicts groups a user
might want to join but hasn't yet [10].

### Link Prediction (a.k.a. Relationship Prediction)

Identifies potential future or missing connections between nodes. Example: build a
co-authorship graph from research databases (PubMed, MedRxiv, CORD-19, Web of Science,
DBLP) with authors as nodes and "collaborated on a paper" as edges; predict future
collaborations between authors who haven't yet worked together. Extends to law
enforcement, security, friend/product recommendations, KG completion, drug side-effect
prediction, relational-database fact inference, and protein–protein interaction
discovery.

**Naming**: the task goes by *link prediction*, *graph completion*, or *relational
inference* depending on domain. **Link prediction** strictly means predicting existence
of a connection (relationship type fixed/predetermined); **relationship prediction**
means predicting the type of relationship too. The book uses the terms interchangeably.

Graphs are typically incomplete for one of two reasons:

- Connections exist but are unobserved, unrecorded, or deliberately hidden by actors in
  the network.
- The graph is naturally evolving (e.g., new co-authorships form as new papers are
  written).

Flow:

1. **Training** — sample negative cases (pairs of nodes with no link) alongside existing
   links; extract relationship features from graph structure/node/relationship
   properties; train a model.
2. **Prediction** — for each target node pair, extract features the same way, and the
   model outputs an existence probability. A threshold (e.g., 0.5) converts this into a
   binary classifier. The same approach can predict relationship *type* by computing a
   probability per type.

Like node classification, link prediction is typically **semisupervised**: specific links
may be missing, but existing connections plus rich node-level information let the model
infer patterns for likely missing or future edges.

### Clustering and Community Detection

Given a co-authorship (or similar) graph, real-world networks are rarely a uniform
"hairball" — they partition into clusters shaped by research area, institution, geography,
etc. **Community detection** identifies these latent groupings using only network
topology and relationships — no prelabeled data required (generally unsupervised).

Flow: input a graph → community detection algorithm → output a mapping of nodes to
groups.

Applications: identifying functional modules in genetic interaction networks [18],
detecting fraudulent user groups in financial transaction networks [19]. One especially
powerful use is **graph description/summarization** — clustering gives a higher-level
structural view of graphs too large to visualize or manually analyze directly.

**Naming and distinction from classical clustering**: *community detection* and *graph
clustering* are used interchangeably, but differ fundamentally from algorithms like
K-means and DBSCAN:

| Algorithm | Requires k upfront? | Data structure |
|---|---|---|
| K-means | Yes — partitions n points into k clusters via iterative centroid assignment | independent points in vector space |
| DBSCAN | No — groups densely-packed points, marks low-density points as outliers | independent points in vector space |
| Community detection / graph clustering | No | interconnected data — relationships determine group membership |

Graph clustering is generally unsupervised, though some methods (e.g., **label
propagation**) can incorporate existing labels to guide community assignment, bridging
supervised and unsupervised approaches.

**Label propagation algorithm (LPA)** [20]: a fast community-detection method. Labels
propagate throughout the network; nodes ending with the same label are considered part
of the same community. LPA does not guarantee consistent output due to its randomness —
repeated runs on the same network can yield slightly different communities.

Community detection maximizes **modularity** — optimizing the difference between actual
and expected edge density within communities.

## Graph-Focused Tasks

### Graph Classification

Consider predicting toxicity/solubility of chemical molecules — properties that emerge
not just from individual atoms but from how atoms connect (represent atoms as nodes,
bonds as edges [21]). Graph classification analyzes atomic composition and structural
patterns to categorize unlabeled molecules (solubility, toxicity, etc.), and can predict
multiple properties simultaneously.

Key distinction from node classification: **each entire graph is one i.i.d. data point**
with its own label (e.g., "is this molecule toxic?"), rather than individual nodes within
one graph.

Flow:

1. **Training** — takes several graphs as input, extracts graph-level features
   (structure, node/relationship properties) for each, trains a classifier.
2. **Prediction** — the same featurization is applied to unlabeled graphs; the model
   outputs a class with a likelihood for each.

The primary challenge in graph-level tasks: designing features that capture both the
internal structure of each graph and the properties of its components.

**Other examples**: enzyme classification (proteins as graphs — amino acids as nodes,
edges when amino acids are within a distance threshold — predict enzyme vs. not);
malware classification (represent a program's syntax/data flow as a graph, classify
malicious vs. benign [22]).

**Graph clustering at the graph level** extends unsupervised clustering to categorize
entire graphs rather than nodes.

## Implementation Approaches: How?

Two general implementation directions (figure 9.6):

1. **Graph-native / collective classification** [23] — algorithms designed specifically
   for graphs; they take the graph directly as input and simultaneously consider node
   features and neighborhood relationships, with no intermediate transformation step.
2. **Feature engineering + traditional ML** — convert the graph into a feature vector
   (feature matrix) first, then apply any existing ML/deep-learning algorithm. The
   central challenge shifts to defining features that capture the essential
   characteristics of nodes, edges, and (for graph classification) the whole graph
   structure.

The rest of the book progresses: manual feature engineering (thorough but tedious) →
semiautomated approaches → **graph neural networks (GNNs)** as a powerful automated
feature-learning solution. GNNs excel at capturing both structural patterns and node
properties, which is valuable especially for incomplete KGs, and produce vector
embeddings usable directly by downstream ML tasks like classification.

### Node Classification and Link Prediction — Detailed Flow

**Training** (figure 9.7): featurize each node into a vector (using node attributes,
neighbors at any level, or the entire graph as needed). For node classification, the
vectors feed a classifier directly. For link prediction, node-pair vectors must first be
combined into a relationship vector — common combination operators are **Hadamard
product, average, L1, L2, and concatenation**. Existing links are labeled "Exists"; a
sampled subset of non-existent links is labeled "Does not exist." Either way, both tasks
reduce to a classic classification algorithm (logistic regression, random forest,
Bayesian, etc.).

**Prediction** (figure 9.8): the featurization process must be *identical* to training.
Node classifier output = probability of class membership (thresholdable). Link
prediction output = probability that a link exists (also thresholdable), and can extend
to per-type probabilities for relationship-type prediction.

> **NOTE** The featurization process used during training must be the same as that used
> for making predictions. Otherwise, the prediction phase will not function correctly.

### Worked Example: Zachary Karate Club

A classic, small (34-node) benchmark graph documenting friendships among karate club
members before a real-world split into two factions (following administrator "John A."
vs. instructor "Mr. Hi"). Ground truth: each node's post-split club affiliation. Task:
predict this affiliation using only the pre-split friendship structure.

```python
import networkx as nx
import matplotlib.pyplot as plt

G = nx.karate_club_graph()          # loads the karate club graph
draw_and_save_graph_picture(G)      # displays + saves the graph (PNG/SVG)

def set_club_colors(G):             # assigns a color per node group
    for node in G.nodes(data=True):
        color = '#00fff9'
        if node[1]['club'] == 'Mr. Hi':
            color = '#e6e6fa'
        node[1]['color'] = color
```

**Attempt 1 — degree as embedding** (simplest possible feature: connection count):

```python
def compute_degree_embeddings(G):
    embeddings = np.array(list(dict(G.degree()).values()))
    embeddings = [[i] for i in embeddings]   # single-value embedding per node
    return embeddings
```

**Attempt 2 — Node2Vec** [25], a pre-GNN autonomous representation-learning technique
computing node embeddings purely from network structure (random walks, Word2Vec-style
training):

```python
def compute_complex_embeddings(G):
    node2vec = Node2Vec(
        G,
        dimensions=64,
        walk_length=30,
        num_walks=200,
        workers=4,
        seed=0)

    model = node2vec.fit(
        window=10,
        min_count=1,
        batch_words=4,
        seed=0)

    embeddings = [model.wv.get_vector(i) for i in G.nodes]
    return embeddings
```
Node2Vec: builds a 64-dim vector per node from 200 random walks of length 30 (4 parallel
workers, fixed seed for reproducibility); trains Word2Vec-style with a window of 10
nodes before/after each walk step. Output embeddings can feed node classification or
link prediction directly.

**Training function** (logistic regression classifier):

```python
def train(self, train_dataset):
    node_embeddings = train_dataset.embeddings.values.tolist()
    node_labels = train_dataset.label.values.tolist()

    self.scaler = StandardScaler().fit(node_embeddings)
    scaled_embeddings = self.scaler.transform(node_embeddings)

    clf = LogisticRegressionCV(
        random_state=0,
        solver='liblinear',
        multi_class='ovr',
        max_iter=1000)
    self.model = clf.fit(scaled_embeddings, node_labels)
```

**Why feature scaling matters**: ML algorithms relying on Euclidean distance let
larger-range features dominate regardless of true importance (e.g., degree 1–1,000 vs.
centrality 0–1) — biasing predictions and hurting accuracy. `StandardScaler` normalizes
to zero mean / unit variance so each feature contributes proportionally.

**Logistic regression** is a classification algorithm despite the name — it transforms
linear feature combinations into class probabilities (0–1) via the logistic function,
well-suited to binary node classification tasks like this one.

**Evaluation**:

```python
def evaluate(self, test_dataset):
    test_embeddings = test_dataset.embeddings.values.tolist()
    true_labels = test_dataset.label.values.tolist()

    scaled_test_embeddings = self.scaler.transform(test_embeddings)
    predicted_labels = self.model.predict(scaled_test_embeddings)

    metrics = precision_recall_fscore_support(true_labels,
        predicted_labels, average='weighted')
    conf_matrix = confusion_matrix(true_labels, predicted_labels)
```

**Results comparison**:

| Embedding | Precision | Recall | F-score |
|---|---|---|---|
| Degree only | 0.446 | 0.429 | 0.429 |
| Node2Vec (64-dim) | 0.653 | 0.643 | 0.645 |

Both are poor and unstable — multiple runs show F-scores fluctuating between 30% and
70%. Since logistic regression is well-established, the instability points to weak
**feature engineering**, not the classifier.

**Attempt 3 — domain-informed features using homophily**: instead of raw degree, build a
3-element vector per node: total degree, "Mr. Hi degree" (connections to the instructor's
group), and "officer degree" (connections to the administrator's group) — assuming group
membership is influenced by neighbors' group affiliations:

```python
def compute_specific_degree_embeddings(G):
    clubs = nx.get_node_attributes(G, "club")
    mr_hi_degree = [[clubs[c] for c in G.neighbors(i)].count('Mr. Hi')
        for i in G.nodes()]
    officer_degree = [[clubs[c] for c in G.neighbors(i)].count('Officer')
        for i in G.nodes()]
    degree = list(dict(G.degree()).values())
    embeddings = [[degree[i], mr_hi_degree[i], officer_degree[i]] for i in G.nodes]
    return embeddings
```

Result: Precision 0.937, Recall 0.929, F-score 0.927 — dramatically better and stable
across repeated runs, close to 100%.

**Three takeaways from this experiment**:

- **Feature engineering is critical** — how nodes/relationships are represented
  fundamentally impacts success; domain-informed features often beat simple metrics like
  degree centrality.
- **Autonomous embeddings require careful tuning** — Node2Vec doesn't guarantee optimal
  results by default; parameters must be tuned to avoid overly homogeneous
  representations (exercise: try lower `walk_length`/`num_walks`).
- **Domain understanding matters** — knowledge of graph dynamics (e.g., homophily) can
  guide feature strategies that outperform generic approaches.

### Graph Classification — Detailed Flow

Similar overall approach to node classification/link prediction, but features are
computed/extracted for **entire graphs** rather than individual nodes, with multiple
graphs as input.

**Training** (figure 9.10): featurize each graph into a vector (node-attribute averages,
global statistics, etc.); each graph has an assigned class; feed vectors + labels to any
classifier (logistic regression, random forest, Bayesian, etc.) → classifier model.

**Prediction** (figure 9.11): apply the same featurization to unlabeled graphs, run
through the classifier, get class + probability per graph.

Feature extraction for nodes, relationships, and whole graphs is the vital step —
downstream accuracy and performance largely depend on feature quality and tuning of
downstream algorithm parameters (the focus of chapter 10 and much of part 4).

### Graph Clustering — Detailed Flow

Not every graph ML task needs the training/featurization pipeline above. Graph
clustering's input is the entire graph (or subgraph); the algorithm uses nodes and
relationships directly to extract communities — **no feature extraction step, no
training phase**, purely unsupervised.

Certain algorithms (e.g., **weakly connected components (WCC)**) use a fixed mechanism
and consider only independent subgraphs. Others (**Louvain**, **label propagation**)
optimize an outcome such as modularity.

**Louvain on the karate club graph**:

```python
import networkx as nx

if __name__ == '__main__':
    G = nx.karate_club_graph()
    communities = nx.community.louvain_communities(G, seed=123)
    for community in communities:
        subGraph = G.subgraph(community)
        draw_and_save_graph_picture(subGraph)
```

Result: 4 communities identified. Each is largely homogeneous (nodes from the same
post-split group), with one spurious node (node 8) landing in a community with the
opposite group — despite being well-connected to that group, suggesting it may genuinely
sit at the boundary.

Two distinguishing aspects vs. classification/prediction tasks: **no representation
transformation** (algorithm acts directly on the graph) and **no training phase**
(purely unsupervised, no labels used at all).

## Takeaways

- ML on graphs handles interconnected data natively, offers a universal data
  representation, and reduces many disparate real-world problems to a small set of
  computational tasks.
- Unlike traditional ML's i.i.d. assumption, graph-based approaches model connections and
  dependencies between data points, better reflecting real-world structure — **homophily**,
  **structural equivalence**, and **heterophily** are named patterns that break i.i.d.
- Tasks split into **node-focused** (node classification, link prediction — one graph,
  data points are nodes/relationships) and **graph-focused** (graph classification/
  clustering — data points are entire graphs).
- Node classification and link prediction are typically **semisupervised**; community
  detection is typically **unsupervised** and operates directly on graph structure with no
  training phase.
- **Feature engineering is the critical bottleneck**: node embeddings range from manual
  (degree), to autonomous-but-tunable (Node2Vec), to domain-informed (homophily-aware
  features) — the karate club experiment showed domain-informed features (F-score ~0.93)
  vastly outperforming raw degree (~0.43) or untuned Node2Vec (~0.65).
- Success on graph ML tasks depends on balancing automated feature learning, injected
  domain knowledge, and appropriate algorithm choice — setting up GNNs (next chapters) as
  the way to automate and improve this feature-learning step.
