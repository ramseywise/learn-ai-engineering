---
origin: book-condensed
sources:
  - sources/kg-and-llms-in-action/09-ml-on-knowledge-graphs.md
  - sources/kg-and-llms-in-action/10-graph-feature-engineering.md
  - sources/kg-and-llms-in-action/11-graph-representation-learning-gnns.md
  - sources/kg-and-llms-in-action/12-node-classification-link-prediction.md
confidence: medium-high
cleaned: 2026-10-28
---
# 13 — Learning on Graphs: Features, Embeddings, GNNs

> Notes 09–12 query the edges a graph already has. Graph ML predicts the ones it doesn't: missing links, unlabeled nodes, hidden communities. A prediction is a claim, not a fact, so it enters the graph with a confidence score.

---

## Where it sits

This is the **Learning** pillar from [note 09](09-kg-fundamentals-and-cypher.md#what-a-knowledge-graph-is). You can build, query and share a KG without it. It earns its place when:

- the graph is **incomplete** and you want candidate edges ("which drug might treat this disease?", "which accounts are linked to this fraud ring?");
- you need **labels** for nodes nobody has labelled (bot, fraudster, protein function);
- the graph is too large to inspect, and **communities** give you a summary of it.

Two pieces of the earlier notes are already graph ML: **WCC** clusters mentions in entity resolution ([note 10](10-building-kgs-with-llms.md#graph-based-er-ch6)), and GraphRAG's **community summaries** rest on community detection ([note 11](11-kg-rag-and-text-to-cypher.md#retrieval-modes)).

---

## Why graphs need their own ML

Classical ML assumes data points are **i.i.d.** (independent and identically distributed). Nodes aren't. Three patterns break the assumption (ch9):

| Pattern | Means | Example |
|---|---|---|
| **Homophily** | Connected nodes tend to be alike | Friends share interests |
| **Structural equivalence** | Nodes with similar neighbourhoods play similar roles, even far apart | Proteins with the same interaction shape share function |
| **Heterophily** | Connected nodes tend to differ | Buyers connect to sellers |

So node tasks are usually **semisupervised**: training sees the whole graph, including the unlabelled nodes, and only their labels are missing.

### The task map

| Task | Data point | Typical use | Needs training? |
|---|---|---|---|
| **Node classification** | A node in one graph | Fraud, bots, AML, protein function | Yes |
| **Link prediction** | A node pair in one graph | KG completion, recommendations, drug repurposing | Yes; sample non-links as negatives |
| **Community detection** | The whole graph | Summarising, fraud rings, functional modules | No: WCC, Louvain, label propagation act on the graph directly |
| **Graph classification** | One whole graph among many | Molecule toxicity, malware | Yes |

A small set of tasks covers a large set of business problems. That is the book's main argument for the graph framing.

---

## Features: the bottleneck

Models want vectors, so every node, edge or graph has to be **featurised**, and the same featurisation has to run at training and at prediction time. The approaches trade interpretability for effort (ch10):

| Approach | Examples | Interpretability | Effort |
|---|---|---|---|
| **Manual** | Degree, triangles, density, closeness, betweenness, PageRank; for edges, combine node vectors (Hadamard, average, L1, L2, concatenation) or count metapaths | High: every number traces to a graph property | High |
| **Semiautomated** | ReFeX: recursive local, egonet and aggregated features from topology alone, then pruned by correlation | Balanced, and deterministic | Medium |
| **Learned** | Node2Vec, GNN embeddings | Low | Low |

**The karate-club lesson** (ch9). Predicting which faction each member joined after the club split:

| Features | F1 |
|---|---|
| Degree only | 0.43 |
| Node2Vec, 64-dim, untuned | 0.65, and unstable between runs (30–70%) |
| Degree + "neighbours in faction A" + "neighbours in faction B" (homophily, written by hand) | **0.93**, stable |

The classifier was the same logistic regression each time. Domain knowledge expressed as three numbers beat a generic embedding. Learned features don't remove the need to understand the graph. They need tuning, and a domain-informed baseline tells you whether the tuning worked.

### DWPC: discount the hubs

Counting paths between two nodes overrates connections that go through **hubs**, the nodes connected to everything. **Degree-weighted path count** damps each path by the degrees of the nodes it passes through, so specific connections outrank generic ones (ch4, ch10; demonstrated on Hetionet drug repurposing). It is the same instinct as dropping hub nodes in NED ([note 10](10-building-kgs-with-llms.md#ned-against-an-ontology-ch78)): a path through "Infectious process" says almost nothing.

### LLMs help with manual features

Because manual features rest on well-known algorithms, an LLM can reason about them. Ch10 uses one to turn metapath descriptions into Cypher computing path count and DWPC, given the schema, one worked example and the list of metapaths. Treat the output as a draft, the same way [note 11](11-kg-rag-and-text-to-cypher.md#text-to-cypher) treats text-to-Cypher.

---

## Representation learning

### Encoder–decoder: one frame for everything

Every graph representation learning method is an **encoder** (structure → vector) plus a **decoder** (vector → the property you care about) (ch11). Matrix factorisation, Node2Vec's random walks and GNNs differ only in how good the encoder is and which task the decoder serves.

Choose the embedding along three axes:

| Axis | Options | Pick by |
|---|---|---|
| What it preserves | **Positional** (where a node sits globally) vs. **structural** (what role it plays locally) | Link prediction and clustering lean positional; classification leans structural, which is where GNNs do well |
| New nodes | **Transductive** (fixed node set) vs. **inductive** (works on unseen nodes) | A graph that grows needs inductive |
| Geometry | **Euclidean** vs. **hyperbolic** | Hyperbolic only with evidence of strong hierarchy (taxonomies, org charts) |

**Shallow embeddings** (one learned vector per node, as in Node2Vec) are simple but share no parameters, ignore node features and can't embed a node they never saw. Those limits are why GNNs exist.

**KG embeddings** add relationship types. A multirelational decoder (TransE, RESCAL, DistMult, ComplEx) scores a (head, relation, tail) triple, trained with **negative sampling** because almost every possible edge is absent. The decoders differ in which relation patterns they can represent: symmetric, asymmetric, compositional.

### Message passing

A GNN layer has each node **aggregate** its neighbours' vectors and **update** its own. After *k* layers a node's embedding encodes its *k*-hop neighbourhood.

![Message passing for target node A: A aggregates messages from its neighbours D, B and C, and each of those messages was itself aggregated from that neighbour's own neighbours, so two layers reach A's two-hop neighbourhood](../sources/images/negro-kg-and-llms-in-action-fig11-5.png)
*Image Source: Negro et al., Knowledge Graphs and LLMs in Action, Fig. 11.5 (2025)*

The picture is two layers unrolled: the boxes on the right are the first layer's aggregations at D, B and C, and the big box is the second layer's aggregation at A. The variants fix specific problems:

- **Normalisation** stops high-degree nodes from dominating.
- **Attention** (GAT) weights neighbours by relevance. Multi-head attention is the transformer mechanism applied to a neighbourhood.
- **Skip connections, gating and jumping knowledge** fight **over-smoothing**, where deep stacks make every node look the same.

### In practice (ch12, PyTorch Geometric)

| | Node classification: AML (Elliptic) | Link prediction: recommendations (MovieLens) |
|---|---|---|
| Graph | Homogeneous (`Data`) | Heterogeneous (`HeteroData`, users and movies; `to_hetero()` converts the base GNN) |
| Decoder | `log_softmax` + cross-entropy | Dot product + binary cross-entropy on logits |
| Splitting | Node masks; most nodes are unlabelled | `RandomLinkSplit`, with **message-passing edges kept apart from supervision edges** to avoid leakage |
| Result | SAGE best F1 (82.7% of illicit nodes caught); GCN missed 32% | SAGE fewest false positives; GCN best recall |

Across both tasks **GAT** had the most parameters and the slowest training, with no accuracy gain to show for it. GCN vs. SAGE is a precision/recall choice. Make it from the cost of each error: AML can't afford missed illicit accounts, and a recommender shouldn't over-suggest.

---

## GNNs and LLMs together

GNNs handle structure and struggle with text. LLMs are the reverse. Ch11 names three ways to combine them:

| Pattern | Flow | Example |
|---|---|---|
| **LLM as predictor** | GNN encodes the structure; the LLM produces the final output | KG question answering that explains a structural finding |
| **LLM as encoder** | The LLM embeds node text; the GNN propagates it over edges | Paper abstracts as node features for citation prediction |
| **LLM as aligner** | Both run in parallel, aligned by contrastive training | Multimodal KGs where both text and structure matter |

The predictor pattern is what the book's advisory systems do: a structural result (a DWPC ranking, a predicted link) gets explained in domain language. The LLM narrates; it doesn't decide. That is ch4's rule for clinical use, and a reasonable default anywhere.

---

## Predictions in a shared graph

A predicted edge is the clearest case of note 12's rule that **claims are not truths**. If a link-prediction model writes into a graph that agents read:

- Write it through the `GraphUpdate` path with a distinct edge type or a `predicted: true` property, the model's `confidence`, and the `run_id` of the training run ([note 12](12-kg-as-shared-agent-memory.md#the-write-path-graphupdate)).
- Keep predicted edges out of default traversals. A query should opt in to them.
- Evaluate on held-out edges, and watch the **false-positive rate**. A false link does what a false merge does in [note 10](10-building-kgs-with-llms.md): every later traversal follows it confidently.

---

## Working reference

`~/.claude/refs/agent-eval.md`: precision/recall trade-offs and held-out evaluation.

Depth: [ch9](../sources/kg-and-llms-in-action/09-ml-on-knowledge-graphs.md) (task taxonomy, karate club), [ch10](../sources/kg-and-llms-in-action/10-graph-feature-engineering.md) (manual features, metapaths, DWPC, ReFeX), [ch11](../sources/kg-and-llms-in-action/11-graph-representation-learning-gnns.md) (embeddings, KG decoders, message passing), [ch12](../sources/kg-and-llms-in-action/12-node-classification-link-prediction.md) (PyG walkthroughs). Practice: [lab B9](../practice/exercises.md#b9--predict-missing-links).

---

→ Back to the start: [01-graph-vs-loop.md](01-graph-vs-loop.md). Next pillar: [06-eval](../../06-eval/README.md).
