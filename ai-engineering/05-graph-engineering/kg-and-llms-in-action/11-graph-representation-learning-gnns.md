---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 11: Graph representation learning and graph neural networks"
confidence: high
cleaned: 2026-07-29
---

# Ch 11 — Graph Representation Learning and Graph Neural Networks

Chapters 9–10 covered manual feature engineering for graph ML (node classification, link
prediction, community detection). Manual features are interpretable but don't scale to KGs
with millions of nodes/relations. **Graph representation learning (GRL)** solves this by
using deep learning (DL) to automatically learn optimal representations — **embeddings** —
directly from graph structure and node attributes, capturing patterns too complex to hand-specify.

## 11.1 Embeddings in Graph Representation Learning

GRL has evolved through three generations [1]:

1. **First generation** — traditional graph embedding rooted in classical dimensionality
   reduction (analogous to flattening a 3D object into a faithful 2D drawing).
2. **Second generation** — sparked by NLP breakthroughs (word2vec); **Node2Vec** showed
   nodes could get meaningful numerical vectors the same way words did, capturing
   relationships rather than just compressing complexity.
3. **Third (current) generation** — deep learning via **graph neural networks (GNNs)**,
   analogous to how DL automated feature learning from raw pixels in computer vision; GNNs
   automatically learn complex relational patterns.

### 11.1.1 From discrete to continuous

A graph embedding transforms a discrete graph (nodes + edges) into a continuous vector
space — like replacing a verbal list of city streets with a coordinate map, making distance
and similarity computable. The goal is to learn an **encoder function**, `encode(x)`, that
maps nodes to a multidimensional embedding space such that distances between embeddings
reflect meaningful relationships in the original graph (Figure 11.1).

**The geometry of embeddings.** Images and text have regular structure (fixed neighbor
counts), enabling CNNs/RNNs. Graphs are irregular — node degree varies — so most graph
embedding methods default to **Euclidean space** (straight-line distances, Pythagorean
theorem), which works well when relationships are uniform.

Some graphs — especially **hierarchical** ones (corporate orgs, biological taxonomies,
internet topology) — are better represented in **non-Euclidean** spaces, particularly
**hyperbolic space**:

| Property | Euclidean space | Hyperbolic space |
|---|---|---|
| Growth of available space | Polynomial with dimension | Exponential outward (like a branching tree) |
| Vectors | Straightforward coordinates | Coordinates, but behave differently |
| Distance | Grows linearly with coordinate difference | Grows exponentially near the boundary |
| Uniformity | Space between points is constant | Same coordinate difference means larger distance near boundary |
| Distance calc | Standard Euclidean formula | Requires special distance formulas |

Use non-Euclidean embeddings only with strong evidence the graph structure benefits (e.g.,
hierarchy) — the choice affects the whole pipeline (distance calculations, visualization,
interpretation). This falls under **geometric deep learning (GDL)**, the study of applying
DL to nonstandard geometric structures.

### Local vs. global: positional vs. structural embeddings

- **Positional embeddings** preserve *absolute* position — who is central, who bridges
  communities, path lengths. Use techniques like matrix factorization and random walks to
  capture global properties. Valuable for **unsupervised** tasks driven by overall topology:
  link prediction, clustering.
- **Structural embeddings** preserve *relative* position / local patterns — two nodes far
  apart but playing similar local roles (e.g., both group organizers) get similar vectors.
  This is where **GNNs excel**. Valuable for **supervised** tasks: node classification,
  whole-graph classification.

Recent work (positional GNNs) blurs this boundary, and theory suggests positional and
structural embeddings capture complementary aspects of graph structure.

### Learning strategies: transductive vs. inductive

- **Transductive learning** — learns embeddings for a fixed, known set of nodes, optimized
  directly for that structure. Works for static graphs; cannot handle unseen nodes without
  retraining. Allows inferring new info (unlabeled node classification, missing edges)
  *within* the trained structure.
- **Inductive learning** — learns general, parametric mappings (using node features) rather
  than memorizing per-node embeddings. Applies to nodes never seen during training — useful
  for dynamic graphs (e.g., new users/products in a recommender system).

### Role of supervision

- **Unsupervised** — discovers natural patterns/structures using graph structure alone
  (assumes structure alone is informative — often true).
- **Supervised** — uses additional labels/context to guide learning toward specific goals.

### 11.1.2 Real-world applications

| Domain | Positional/Structural | Geometry | Learning | Supervision |
|---|---|---|---|---|
| Social network (LinkedIn) | Structural for similar roles; positional for influencers/bridges | Euclidean (typical) | Inductive (new users) | Supervised (job titles/skills) |
| Biological networks (protein interaction) | — | Hyperbolic (hierarchical) | Inductive (new discoveries) | Supervised (experimental data) |
| Medical KGs | Structural (similar concepts across branches) | Hyperbolic (medical term hierarchy) | — | Supervised (expert-labeled relationships) |

The choice of embedding strategy reflects understanding of problem structure, not just a
technical decision.

## 11.2 The Encoder–Decoder Model

A unifying framework for graph embedding methods (Figure 11.4): the **encoder** converts
graph information into compact vector representations; the **decoder** reconstructs
meaningful graph properties from those vectors — like a translation system.

### 11.2.1 The encoder

Converts graph structure to vectors. Inputs:
- **Graph structure** — an adjacency matrix showing connections.
- **Node features** — additional per-node information.

Encoders range from a simple lookup table to a full neural network processing both
structure and features. Some prioritize global structure/relative position; others
prioritize local neighborhood patterns.

### 11.2.2 The decoder

Reconstructs important graph properties from embeddings, providing the training signal:
- Predicts whether nodes are connected (structure-focused methods).
- Reconstructs neighborhood-overlap measures (node similarity).
- Predicts node labels or other properties (supervised settings).

Minimizing the difference between decoder predictions and actual graph properties optimizes
the encoder to learn better representations.

### 11.2.3 The power of the framework

Matrix factorization, random-walk methods, and GNNs are all different implementations of
this same encode–decode pattern. Simpler encoders are computationally cheap but capture
less complex patterns; neural-network encoders learn richer representations but need more
data/compute.

### 11.2.4 Node2Vec as an encoder–decoder example

Worked example: the **karate club network** (34 members, split into instructor's faction
(node 0) and administrator's faction (node 33)).

**Encoding process:**
1. **Random walk generation** — walk through the friendship graph (e.g., `0 → 1 → 2 → 3`).
   Node2Vec tunes `p`/`q` to balance breadth (exploring different social circles) vs. depth
   (staying within tight-knit groups).
2. **Vector creation** — members co-occurring frequently in walks get similar vectors.

**Decoding process:** uses the **softmax function** to ask "given member *i*'s vector, how
likely are we to see member *j* nearby in random walks?" — predicting friendship likelihood.

Patterns revealed: **community structure** (same-faction members get similar vectors),
**bridge members** (dual-faction friends get intermediate vectors, flagging mediators), and
**leadership roles** (instructor/administrator get distinct vectors reflecting their central
but opposing positions).

```python
import networkx as nx
import numpy as np
from node2vec import Node2Vec
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

G = nx.karate_club_graph()

faction_labels = {
    0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0,
    9: 1, 10: 0, 11: 0, 12: 0, 13: 0, 14: 1, 15: 1, 16: 0,
    17: 0, 18: 1, 19: 0, 20: 1, 21: 0, 22: 1, 23: 1, 24: 1,
    25: 1, 26: 1, 27: 1, 28: 1, 29: 1, 30: 1, 31: 1, 32: 1,
    33: 1
}
nx.set_node_attributes(G, faction_labels, 'faction')

node2vec = Node2Vec(
    G, dimensions=16, walk_length=10, num_walks=20,
    p=1, q=1, workers=4
)
model = node2vec.fit(window=5)

def decode_similarity(model, node1, node2):
    return model.wv.similarity(str(node1), str(node2))

# Similarity comparisons predict faction alignment for unlabeled nodes
```

Running it: t-SNE visualization shows encoded vectors clustering by faction; decoded
similarity scores between members and the instructor (0) vs. administrator (33) predict
faction assignment, reflecting the real social dynamics behind the club's split.

## 11.3 Shallow Embeddings: A First Approach

**Shallow embeddings** are the simplest encoder–decoder implementation. The encoder is a
**lookup table**: each node maps directly to its vector row — no transformation of input,
just direct retrieval (like a dictionary: each word/node has a dedicated entry). The decoder
reconstructs connectivity or neighborhood similarity to optimize those vectors during
training.

### Limitations

- **Parameter inefficiency** — one vector per node; parameter count grows linearly with
  graph size (millions of users → millions of vectors). Impractical at scale.
- **No parameter sharing** — can't reuse patterns across nodes; similar social roles in
  different parts of the graph must be learned independently.
- **Feature blindness** — no natural way to incorporate node attributes (age, interests,
  role, etc.).
- **Transductive nature** — can only embed nodes seen during training; a new member requires
  full retraining since there's no lookup entry for them.

Despite this, shallow embeddings remain a useful historical baseline and are practical for
small, static graphs with limited compute. Their limitations motivate GNNs (section 11.6),
which learn from both structure and features, enabling inductive learning and parameter
sharing.

## 11.4 Embeddings in Knowledge Graphs

KGs are **multirelational** — edges carry types, not just presence/absence (e.g.,
(*Aspirin*, `TREATS`, *Headache*), (*Aspirin*, `INHIBITS`, *COX-2*), (*Inflammation*,
`CAUSES`, *Headache*)). Embedding approaches must encode not just *whether* entities relate
but *how*. This requires a **loss function** to measure representation quality and a
**multirelational decoder** to handle relation types.

### 11.4.1 Loss function

Naive mean-squared-error over all node pairs fails at scale:
- **Computational efficiency** — 1M users implies ~1 trillion potential connections to check.
- **Sparsity** — most real-world graphs are sparse; the loss must handle severe imbalance.

Modern approaches use **negative sampling with cross-entropy loss**:

```
L = Σ_(u,τ,v)∈ε  −log(σ(DEC(z_u, τ, z_v)))
              − γ·E_(v_n~p_n,v(v))[log(σ(−DEC(z_u, τ, z_v_n)))]
```

Where:
- **L** — total loss to minimize; **Σ** — sum over all existing edges in the KG.
- **σ** — sigmoid function (converts scores to probabilities in [0,1]).
- **DEC** — decoder function scoring relationship plausibility.
- **γ** (gamma) — balancing parameter controlling importance of negative samples.
- **u, τ, v** — head node, relationship type, tail node (e.g., Aspirin, TREATS, Headache).
- **z_u, z_v** — embedding vectors for u and v.

**Positive term** `−log(σ(DEC(z_u, τ, z_v)))`: scores the true relationship, converts to
probability, penalizes low probability on true facts (reward true facts).

**Negative term** `−γ·E[log(σ(−DEC(z_u, τ, z_v_n)))]`: `v_n` is a negative sample (e.g.,
COX-2 substituted for Headache); `p_n,v(v)` is the negative-sampling distribution;
`E` is expectation over negative samples. Penalizes false facts.

Because KGs are usually sparse, γ > 1 is typical, emphasizing correct rejection of false
relationships. This is computationally efficient — only true relationships plus a small
sample (typically **5–10 negative samples per true relationship**) need evaluation, not all
possible pairs.

**The art of negative sampling.** Random sampling (e.g., (Aspirin, TREATS, Laptop)) is cheap
but has two problems:
- **False negatives** — may accidentally sample relationships that actually exist (some
  systems filter these out).
- **Overly simple examples** — obviously wrong samples don't teach subtle distinctions.

More sophisticated strategies:
- **Type-constrained sampling** — only sample semantically plausible nodes (e.g., only
  diseases as `TREATS` targets), forcing subtler distinctions.
- **Adversarial sampling** — generate challenging negatives likely to be confused with true
  relationships.
- Negative samples can replace the subject, the object, or both (e.g., "Sunlight TREATS
  Headache", "Aspirin TREATS Happiness", "Sunlight TREATS Happiness") — considering both
  directions helps prevent bias, especially where relationship direction matters.

### 11.4.2 Multirelationship decoder

Decoders must capture KG relationship patterns:
- **Symmetric vs. asymmetric** — e.g., `similar_to` is symmetric; `causes` is asymmetric.
- **Compositional patterns** — A treats B, B is-a C ⟹ infer A treats C.
- **Inverse relations** — A `contains` B ⟹ B `part_of` A.

Three decoder families:

| Approach | Example | Mechanism | Trade-off |
|---|---|---|---|
| Translation-based | TransE [5] | Relationship = vector that "translates" one entity into another (add `TREATS` vector to *Aspirin* → near *Headache*) | Intuitive, good at compositional patterns; struggles with many-to-one relationships |
| Matrix-based | RESCAL [6] | Relationship = matrix transforming entity vectors | Expressive but parameter-heavy (millions of params for 1,000 entities × 100 relation types) |
| Semantic matching | DistMult [7], ComplEx [8] | Measures entity similarity conditioned on relation type; ComplEx uses complex numbers | ComplEx handles asymmetric relations elegantly but may miss compositional patterns |

This loss-function + multirelational-decoder framework underlies modern KG embeddings and
extends into GNN-based approaches.

## 11.5 Message Passing and Graph Neural Networks

GNNs address shallow embeddings' scaling limits via **neural message passing**: nodes
iteratively learn from neighbors.

### 11.5.1 The message-passing framework

Think of it as a structured "neural conversation": each round lets information travel one
hop further. During each iteration, every node:

1. Collects messages from its neighbors.
2. Processes messages to extract relevant information.
3. Updates its own representation.

Formalized via two functions (Figure 11.5):
- **`AGGREGATE`** — collects and combines messages from neighboring nodes.
- **`UPDATE`** — uses the aggregated messages to update the node's representation.

The GNN's computation graph forms a **tree** by unfolding the neighborhood around the target
node (a target node aggregates from its neighbors, who in turn aggregate from *their*
neighbors).

Example (social network interests): initial representation = stated interests → round 1
adds friends' interests → round 2 adds friends-of-friends' interests → after several rounds,
representation captures broader social-circle interest patterns.

### 11.5.2 Why message passing works

After *k* iterations, each node's representation encodes its **k-hop neighborhood**,
serving two purposes:
- **Structural information** — encodes graph topology (e.g., an atom's representation may
  come to encode membership in a benzene ring).
- **Feature-based information** — propagates neighbor features (e.g., a paper's
  representation gradually incorporates related papers' content).

### 11.5.3 The basic GNN model

Update rule for node *u* at iteration *k*:

```
h_u^(k) = σ( W_self^(k)·h_u^(k−1) + W_neigh^(k)·Σ_{v∈N(u)} h_v^(k−1) + b^(k) )
```

- `h_u^(k)` — node u's representation at iteration k.
- `W_self^(k)`, `W_neigh^(k)` — trainable parameter matrices (can be shared across
  iterations or trained separately per layer).
- `σ` — nonlinear activation (ReLU, tanh).
- Summation runs over all neighbors v of u.
- `b^(k)` — bias term (often omitted; can be shared or per-layer).

This is analogous to a standard neural network layer, but handles varying neighbor counts
via the summation instead of fixed-size inputs. Split into `AGGREGATE`/`UPDATE`:

```
m_N(u)^(k−1) = AGGREGATE^(k−1)({h_v^(k−1), ∀v ∈ N(u)}) = Σ_{v∈N(u)} h_v^(k−1)

UPDATE(h_u^(k), m_N(u)^(k−1), b^(k)) =
    σ( W_self^(k)·h_u^(k−1) + W_neigh^(k)·m_N(u)^(k−1) + b^(k) )
```

### 11.5.4 Message passing with self-loops

Treats the node itself as one of its own neighbors during aggregation, simplifying to:

```
h_u^(k) = AGGREGATE^(k−1)({h_v^(k−1), ∀v ∈ N(u) ∪ {u}})
```

Advantages: simpler (combines AGGREGATE/UPDATE), helps prevent overfitting via parameter
sharing, improves training stability. Trade-off: treating self and neighbors identically
loses flexibility in how a node combines its own state with neighborhood info. Standard
message passing suits tasks where self vs. neighbor distinction matters; self-loops suit
tasks where it doesn't (chapter 12 uses this variant).

## 11.6 Generalized Aggregation and Update Methods

Just as neural networks evolved with skip connections, attention, and normalization, GNNs
benefit from analogous architectural innovations adapted to irregular graph connectivity.

- **Skip (residual) connections** — bypass layers to preserve earlier-layer node features,
  countering **over-smoothing** (node representations becoming too similar after many
  message-passing steps) and enabling deeper architectures via better gradient flow.
- **Attention mechanisms** — dynamically weight neighbor contributions by relevance rather
  than treating all neighbors equally.
- **Normalization layers** — stabilize training by controlling output distribution, which
  matters because node degree varies widely.

### 11.6.1 Neighborhood normalization

Naive summation aggregation causes numerical instability across varying neighborhood sizes.

**Mean normalization:**
```
m_N(u)^(k−1) = ( Σ_{v∈N(u)} h_v^(k−1) ) / |N(u)|
```

**Symmetric normalization** (Kipf & Welling's GCN [9]):
```
m_N(u)^(k−1) = Σ_{v∈N(u)} h_v^(k−1) / sqrt(|N(u)| · |N(v)|)
```

Symmetric normalization accounts for both sender and receiver degree — useful in citation
networks to prevent highly cited papers from dominating message passing disproportionately.

| Scheme | Effect | Best when |
|---|---|---|
| Mean | Comparable scale across varying neighbor counts | Simple degree variance |
| Symmetric | Accounts for both sender/receiver degree | Directed graphs, wide degree variance |
| Learned | Model adjusts normalization during training | Task-specific tuning needed |

Trade-off: normalization is lossy — can make it hard to distinguish nodes by degree after
the fact. Most helpful when node features matter more than structural information, or when
degree range is wide enough to destabilize optimization.

### 11.6.2 Neighborhood attention

Normalization treats all neighbors equally (after scaling); **attention** lets the model
learn which neighbors matter most. **Graph attention networks (GAT)** [10] were the first
GNN to apply this:

```
m_N(u)^(k−1) = Σ_{v∈N(u)} α_{u,v}·h_v^(k−1)

α_{u,v} = exp(a^T[Wh_u ⊕ Wh_v]) / Σ_{v'∈N(u)} exp(a^T[Wh_u ⊕ Wh_v'])
```

`a` is a trainable attention vector, `W` a trainable matrix, `⊕` denotes concatenation.
**GraphSAGE** [11] provides a practical example integrating attention into aggregation.
Attention is valuable when neighbor importance varies by task/context, the graph has
noisy/irrelevant connections, or nonlinear relationship patterns must be captured.

### 11.6.3 Multihead attention and transformer connections

Graph attention parallels transformer attention: just as transformer tokens attend to all
other tokens, graph nodes selectively attend to neighbors. **Multihead attention** runs
several independent attention mechanisms in parallel, each specializing (e.g., one head on
chemical bond types, another on spatial arrangement in a molecular graph).

```python
class MultiHeadGraphAttention(nn.Module):
    def __init__(self, input_dim, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = input_dim
        self.attention_heads = nn.ModuleList([
            GraphAttentionHead(self.head_dim)
            for _ in range(num_heads)
        ])  # init multiple attention heads

    def forward(self, node_features, neighbor_features):
        node_chunks = torch.chunk(node_features, self.num_heads, dim=-1)
        neighbor_chunks = torch.chunk(neighbor_features, self.num_heads, dim=-1)
        head_outputs = []
        for i, head in enumerate(self.attention_heads):
            head_outputs.append(head(node_chunks[i], neighbor_chunks[i]))
        return torch.cat(head_outputs, dim=-1)  # concat all head outputs
```

The transformer parallel is explicit through **query (Q)**, **key (K)**, **value (V)**
projections:

```python
class TransformerStyleGraphAttention(nn.Module):
    def __init__(self, feature_dim):
        super().__init__()
        self.query_transform = nn.Linear(feature_dim, feature_dim)
        self.key_transform = nn.Linear(feature_dim, feature_dim)
        self.value_transform = nn.Linear(feature_dim, feature_dim)

    def forward(self, node_features, neighbor_features):
        Q = self.query_transform(node_features)
        K = self.key_transform(neighbor_features)
        V = self.value_transform(neighbor_features)

        attention_scores = torch.matmul(Q, K.transpose(-2, -1))
        attention_scores = attention_scores / math.sqrt(K.size(-1))
        attention_weights = F.softmax(attention_scores, dim=-1)
        return torch.matmul(attention_weights, V)
```

Benefits of transformer-style graph attention: **scale/efficiency** (parallelizable over
large neighborhoods), **flexible feature learning** (each head specializes), and
**interpretability** (attention weights expose which neighbor relationships matter).

Just as transformers use positional encodings for sequence position, some GNNs add
**structural/positional encodings** to capture graph topology:

```python
class StructuralGraphTransformer(nn.Module):
    def __init__(self, feature_dim, num_heads):
        super().__init__()
        self.structural_encoding = nn.Embedding(max_degree, feature_dim)
        self.attention = MultiHeadGraphAttention(feature_dim, num_heads)

    def forward(self, node_features, neighbor_features, degrees):
        structural_features = self.structural_encoding(degrees)
        enhanced_features = node_features + structural_features
        return self.attention(enhanced_features, neighbor_features)
```

This convergence of GNNs and transformers points toward continued cross-pollination — e.g.,
LLMs generating natural-language descriptions of graph structures, and graph structures
enhancing LLM language understanding.

### 11.6.4 Generalized update methods

**Skip connections in GNNs** (GraphSAGE innovation) — preserve information across
message-passing layers via concatenation:

```python
class GraphSAGEUpdate(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()
        self.update_nn = nn.Linear(input_dim * 2, hidden_dim)

    def forward(self, node_features, aggregated_neighbor_features):
        combined = torch.cat([node_features, aggregated_neighbor_features], dim=1)
        updated = self.update_nn(combined)
        return F.relu(updated)
```

Purposes: **information preservation** (keeps access to original node features),
**feature separation** (model learns which of original vs. neighborhood info matters),
**gradient flow** (extra backprop paths, enabling deeper GNNs).

**Gated updates** (RNN-inspired) — finer control over how much old vs. new information to
retain:

```python
class GatedGraphUpdate(nn.Module):
    def __init__(self, feature_dim):
        super().__init__()
        self.update_gate = nn.Linear(feature_dim * 2, feature_dim)
        self.transform = nn.Linear(feature_dim * 2, feature_dim)

    def forward(self, node_features, aggregated_features):
        gate_input = torch.cat([node_features, aggregated_features], dim=1)
        update_gate = torch.sigmoid(self.update_gate(gate_input))

        combined = torch.cat([node_features, aggregated_features], dim=1)
        candidate = torch.tanh(self.transform(combined))

        return (1 - update_gate) * node_features + update_gate * candidate
```

Useful when: some nodes should stay stable across layers, neighborhood relevance varies by
node, or the graph has noisy/irrelevant connections.

**Jumping knowledge networks** — maintain representations from multiple layers and combine
them adaptively (via LSTM here), capturing multiscale structural information:

```python
class JumpingKnowledge(nn.Module):
    def __init__(self, feature_dim, num_layers):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=feature_dim, hidden_size=feature_dim, batch_first=True
        )

    def forward(self, layer_representations):
        stacked = torch.stack(layer_representations, dim=2)
        batch_size, num_nodes, num_layers, feature_size = stacked.shape
        reshaped = stacked.reshape(batch_size * num_nodes, num_layers, feature_size)
        output, _ = self.lstm(reshaped)
        last_output = output[:, -1, :]
        return last_output.reshape(batch_size, num_nodes, -1)
```

Advantages: different nodes can effectively use information from different hop-distances;
the model combines local and global structural info while avoiding loss of distinctive
node features across layers.

**Practical considerations** when choosing update mechanisms: **computational efficiency**
(complex mechanisms cost more time/memory), **task requirements** (different tasks favor
different strategies), **graph properties** (input graph structure influences the best
choice). Example: citation networks (balancing content vs. citation influence) may favor
gated updates; molecular graphs (multiscale structural patterns) may favor jumping
knowledge. Update mechanism choice is as important as aggregation strategy, and the two
should be designed to complement each other.

## 11.7 The Synergy of GNNs and LLMs

GNNs excel at processing structured graph data via message passing (local neighborhood
info, global topology) — strong at node classification and link prediction — but struggle
with rich textual information on nodes/edges. LLMs excel at long sequential text, semantic
relationships, and reasoning, but don't naturally handle graph structure.

Three integration patterns [13]:

- **LLMs as predictors** — LLM is the final component making predictions/generating output;
  graph structure is encoded into a sequence format, or the LLM architecture is modified for
  graphs directly. Example: a GNN processes graph structure, then an LLM generates natural
  language answers from graph embeddings + question context (KG-based QA).
- **LLMs as encoders** — LLMs process textual node/edge information into rich feature
  representations, which are then passed to GNNs for structural processing. Example: an LLM
  encodes paper abstracts into vectors; a GNN models citation relationships and predicts
  future citations.
- **LLMs as aligners** — LLMs and GNNs work in parallel, each handling its specialized
  domain (text or structure), with outputs combined/aligned via contrastive learning or
  mutual training. Useful for multimodal KGs where both connection patterns and textual
  content carry important information.

Success depends on understanding each technology's complementary strengths and designing
architectures that use them appropriately for the task.

## Takeaways

- **GRL automates feature engineering**: three generations — classical dimensionality
  reduction, word2vec-inspired methods (Node2Vec), and modern GNNs — each learn embeddings
  directly from graph structure and features instead of requiring manual design.
- **Positional vs. structural, transductive vs. inductive, Euclidean vs. hyperbolic**: these
  three axes determine embedding fit — global topology tasks favor positional/Euclidean;
  local-pattern tasks favor structural/GNN; dynamic graphs with new nodes require inductive
  methods; hierarchical graphs may benefit from hyperbolic space.
- **The encoder–decoder framework unifies GRL**: matrix factorization, random walks
  (Node2Vec), and GNNs are all encode(structure→vector)/decode(vector→property)
  implementations, differing only in encoder sophistication and decoder task.
- **Shallow embeddings (lookup tables) are simple but don't scale**: parameter inefficiency,
  no parameter sharing, feature blindness, and transductive-only limits motivate GNNs.
- **KG embeddings need negative sampling + multirelational decoders**: cross-entropy loss
  with negative sampling (γ > 1 typical) makes training tractable on sparse graphs;
  TransE/RESCAL/DistMult/ComplEx decoders trade off expressiveness, parameter count, and
  ability to capture symmetric/asymmetric/compositional relationship patterns.
- **Message passing (AGGREGATE + UPDATE) is the core GNN mechanism**: after k iterations,
  each node encodes its k-hop neighborhood; architectural enhancements (normalization,
  attention, multihead/transformer-style attention, skip connections, gated updates,
  jumping knowledge) address over-smoothing, varying neighborhood sizes, and multiscale
  information capture.
- **GNNs and LLMs are complementary**: GNNs handle structure, LLMs handle text/reasoning;
  combine as predictors, encoders, or aligners depending on whether the end task needs
  language generation, richer node features, or aligned dual representations.
