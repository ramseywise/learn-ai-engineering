---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 12: Node classification and link prediction with GNNs"
confidence: high
cleaned: 2026-07-29
---

# Ch 12 — Node Classification and Link Prediction with GNNs

## Overview

This chapter applies **graph neural networks (GNNs)** to two fundamental graph-ML tasks:
**node classification** (anti-money laundering / AML) and **link prediction**
(movie recommendations). Despite different domains, both are solved with the same
end-to-end **encoder–decoder framework**:

1. **Input data** — semistructured source files describing objects and their interactions.
2. **Graph processor** — preprocessing that converts raw data into a PyTorch Geometric
   (PyG) graph structure (`Data` for homogeneous graphs, `HeteroData` for heterogeneous).
3. **Encoder** — a GNN (GCN, GraphSAGE/SAGE, or GAT) that learns node embeddings via
   message passing.
4. **Decoder** — a task-specific function (log-softmax + cross-entropy for classification;
   dot product + binary cross-entropy for link prediction) that turns embeddings into
   predictions.
5. **Trained model** — used at inference time.

Three encoder architectures are compared throughout using PyG: **graph convolutional
networks (GCNs)**, **GraphSAGE (SAGE)**, and **graph attention networks (GATs)**.
Evaluation uses precision, recall, F1-score, and confusion matrices.

## 12.1 Node Classification for Anti-Money Laundering

Financial transactions are modeled as a graph: nodes = accounts/transactions, edges =
transaction relationships. The task is classifying nodes as **licit** or **illicit**.

### 12.1.1 Input data — the Elliptic dataset

The **Elliptic dataset** is a time-series graph of Bitcoin transactions: 200,000+ nodes
(transactions), 234,000 directed payment-flow edges, 166 anonymized node features.
Provided as three CSVs:

- `elliptic_txs_features.csv` — 203,769 rows × 167 columns (node ID + 166 features).
- `elliptic_txs_edgelist.csv` — 234,355 rows, source/target node ID pairs.
- `elliptic_txs_classes.csv` — 203,769 rows, label per node: `1`, `2`, or `unknown`.

| Class | Label | Count | Percentage |
|---|---|---|---|
| Unknown | Unknown | 157,205 | 77.15% |
| Licit | 2 | 42,019 | 20.62% |
| Illicit | 1 | 4,545 | 2.23% |

Note the severe class imbalance, and that most nodes are unlabeled (`unknown`).

### 12.1.2 Graph processor: data preparation

Preprocessing steps:

1. **Remap original transaction IDs to incremental integer IDs** (a dict comprehension
   mapping `txId → idx`), then apply the mapping to the edge list, drop edges whose
   endpoints aren't in the mapping, and cast IDs to `int64`.
2. **Build `edge_index`** — a `[2, num_edges]` `torch.long` tensor from the remapped
   source/target columns.
3. **Build `node_features`** — a `[203769, 166]` float tensor from the features file
   (original ID column dropped; row order = incremental ID order).
4. **Encode labels numerically** with scikit-learn's `LabelEncoder`, producing a
   `node_labels` tensor where label `0` = licit (original "2"), `1` = illicit
   (original "1"), `2` = unknown.

```python
tx_id_mapping = {tx_id: idx for idx, tx_id in enumerate(features['txId'])}
edges_with_features = edges.assign(
    Id1=edges['txId1'].map(tx_id_mapping),
    Id2=edges['txId2'].map(tx_id_mapping),
)
edges_with_features = edges_with_features.dropna(subset=['Id1', 'Id2'])
edges_with_features = edges_with_features.astype({'Id1': 'int64', 'Id2': 'int64'})

edge_index = torch.tensor(
    edges_with_features[['Id1', 'Id2']].values.T,
    dtype=torch.long
)

node_features = torch.tensor(
    features.drop(columns=['txId']).values,
    dtype=torch.float
)

from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
class_labels = le.fit_transform(classes['class'])
node_labels = torch.tensor(class_labels, dtype=torch.long)
```

### 12.1.3 Graph processor: homogeneous PyG graph

Combine the three tensors into a PyG `Data` object:

```python
from torch_geometric.data import Data
data = Data(x=node_features, edge_index=edge_index, y=node_labels)
```

Because only labeled nodes (licit/illicit) should be used for training/evaluation, a
**mask filter** hides unknown nodes:

```python
known_mask = (data.y == 0) | (data.y == 1)   # licit or illicit
unknown_mask = data.y == 2                    # unknown
```

`known_mask` is then split 80/10/10 into training/validation/testing via random
permutation, and boolean mask tensors (`train_mask`, `val_mask`, `test_mask`) are
attached to `data`.

| Dataset | Number of nodes | Percentage |
|---|---|---|
| Training | 37,251 | 80% |
| Validation | 4,656 | 10% |
| Testing | 4,657 | 10% |

Class balance is preserved across splits (~90% licit / ~10% illicit in each):

| Dataset | Total | Licit | Licit % | Illicit | Illicit % |
|---|---|---|---|---|---|
| Training | 37,251 | 33,645 | 90.32 | 3,606 | 9.78 |
| Validation | 4,656 | 4,193 | 90.06 | 463 | 9.88 |
| Testing | 4,657 | 4,181 | 89.78 | 476 | 9.45 |

This manual splitting approach is contrasted later with PyG's built-in split utilities
used for link prediction (section 12.2).

### 12.1.4 Encoder–decoder architecture

**Decoder wrapper** — a thin module wrapping any GNN encoder, applying log-softmax to
produce per-class probabilities:

```python
class NodeClassifier(torch.nn.Module):
    def __init__(self, gnn_model):
        super().__init__()
        self.gnn = gnn_model

    def forward(self, x, edge_index):
        x = self.gnn(x, edge_index)
        return F.log_softmax(x, dim=1)
```

**Encoder — shared base class.** A two-layer message-passing architecture parameterized
by the convolution type, so GCN/SAGE/GAT can all reuse it:

```python
class BaseGraphModel(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, out_dim, conv_layer, **conv_kwargs):
        super(BaseGraphModel, self).__init__()
        self.conv1 = conv_layer(input_dim, hidden_dim, **conv_kwargs)
        self.conv2 = conv_layer(hidden_dim, out_dim, **conv_kwargs)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        return x
```

**SAGE** is a direct instantiation (`SAGEConv` needs no extra params):

```python
from torch_geometric.nn import SAGEConv

class SAGE(BaseGraphModel):
    def __init__(self, input_dim, hidden_dim, out_dim):
        super(SAGE, self).__init__(
            input_dim=input_dim, hidden_dim=hidden_dim,
            out_dim=out_dim, conv_layer=SAGEConv
        )
```

**GAT** requires extending the base class because `GATConv` needs multi-head attention
parameters (`num_heads`, `add_self_loops`) and concatenation handling across layers:

```python
from torch_geometric.nn import GATConv

class GAT(BaseGraphModel):
    def __init__(self, input_dim, hidden_dim, out_dim, num_heads=8, add_self_loops=True):
        concat_hidden_dim = hidden_dim * num_heads

        conv1 = GATConv(
            in_channels=input_dim, out_channels=hidden_dim,
            heads=num_heads, add_self_loops=add_self_loops
        )
        conv2 = GATConv(
            in_channels=concat_hidden_dim, out_channels=out_dim,
            heads=1, add_self_loops=add_self_loops, concat=False
        )
        super(BaseGraphModel, self).__init__()
        self.conv1 = conv1
        self.conv2 = conv2
```

The first GAT layer concatenates outputs across `num_heads` attention heads (hence
`concat_hidden_dim = hidden_dim * num_heads`); the second layer uses a single head with
`concat=False` to produce the final output dimension.

**The decoder — `log_softmax` + `CrossEntropyLoss`.** `log_softmax` is preferred over
plain `softmax` because it improves numerical stability (mitigates extremely small/large
number effects) during probability computation. It's paired with PyTorch's
`CrossEntropyLoss`, which combines the log of softmax probabilities with negative
log-likelihood loss — an efficient classification objective. If the model predicts high
probability for illicit but the true label is licit, the loss function penalizes and
drives correction.

### 12.1.5 Evaluation and analysis — node classification

Trained for 400 epochs on a T4 Colab machine.

| Encoder | Parameters | Training time (s) |
|---|---|---|
| GCN | 2,723 | 19.02 |
| GAT | 22,025 | 43.45 |
| SAGE | 5,427 | 36.71 |

GCN is most efficient; GAT least efficient (its attention mechanism adds learnable
coefficients per neighborhood edge, increasing parameter count and training time
proportionally).

**Precision / recall / F1** (weighted average, to account for class imbalance) were
computed with `sklearn`'s scoring functions on the validation set across training epochs:

- **Precision** — SAGE is most accurate and consistent (fewest false positives); GAT
  close behind; GCN weakest, especially early in training.
- **Recall** — all three models perform similarly, achieving close values as training
  progresses (recall alone doesn't penalize false positives).
- **F1-score** — SAGE highest (best precision/recall balance); GAT nearly as strong; GCN
  weaker due to lower precision despite high recall.

**Confusion matrices** on the testing dataset:

| Model | Illicit correctly classified | Licit correctly classified | Illicit→Licit errors | Licit→Illicit errors |
|---|---|---|---|---|
| GCN | ~68% | ~99% (98.8%) | ~32% (145/451) | ~1.2% (52/4206) |
| GAT | ~81% (80.9%) | ~99.5% (99.0%) | ~19% (86/451) | ~1.0% (40/4206) |
| SAGE | ~83% (82.7%) | ~99% (98.9%) | ~17% (78/451) | ~1.1% (47/4206) |

**> "Based on the overall analysis, the SAGE model's superior balance, higher accuracy
for both licit and illicit nodes, and minimal misclassifications make it the most
effective and reliable choice."** SAGE is particularly well suited for applications
where detecting illicit nodes is critical (e.g., AML) while maintaining high accuracy on
licit nodes.

## 12.2 Link Prediction for Movie Recommendations

Recommendation systems can be framed as **link prediction**: users and movies are nodes,
ratings are edges, and the model predicts the likelihood of new user–movie links.

### 12.2.1 Input data — MovieLens (small)

The small MovieLens dataset: 100,000 ratings and 3,600 tag applications across 9,000
movies by 600 users. Files:

- `movies.csv` — 9,742 rows, 3 columns (movieId, title, genres). Genres are `|`-separated
  categorical strings.
- `ratings.csv` — 100,836 rows, 4 columns (userId, movieId, rating, timestamp). Only
  `userId` and `movieId` are used here (no rating value/threshold — presence of a rating
  edge is what's predicted).

### 12.2.2 Graph processor: data preparation

**Movie features** — one-hot encode genres into a feature vector:

```python
movies_df = pd.read_csv(movies_path, index_col='movieId')
genres = movies_df['genres'].str.get_dummies('|')
movie_feat = torch.from_numpy(genres.values).to(torch.float)
assert movie_feat.size() == (9742, 20)
```

**Edge index** — remap original `userId`/`movieId` to incremental IDs starting at 0 (via
mapping DataFrames merged onto the ratings), then stack into `edge_index`:

```python
ratings_df = pd.read_csv(ratings_path)

unique_user_id = ratings_df['userId'].unique()
unique_user_id = pd.DataFrame(data={
    'userId': unique_user_id,
    'mappedID': pd.RangeIndex(len(unique_user_id)),
})
unique_movie_id = pd.DataFrame(data={
    'movieId': movies_df.index,
    'mappedID': pd.RangeIndex(len(movies_df)),
})

ratings_user_id = pd.merge(ratings_df['userId'], unique_user_id,
                            left_on='userId', right_on='userId', how='left')
ratings_user_id = torch.from_numpy(ratings_user_id['mappedID'].values)

ratings_movie_id = pd.merge(ratings_df['movieId'], unique_movie_id,
                             left_on='movieId', right_on='movieId', how='left')
ratings_movie_id = torch.from_numpy(ratings_movie_id['mappedID'].values)

edge_index_user_to_movie = torch.stack([ratings_user_id, ratings_movie_id], dim=0)
```

Resulting `edge_index` shape: `[2, 100836]`.

### 12.2.3 Graph processor: heterogeneous PyG graph

Because there are **two node types** (user, movie) and **one edge type**
(`user`–`rates`–`movie`), the graph uses PyG's `HeteroData` (vs. `Data` for the
homogeneous AML graph). `HeteroData` differentiates features per node type and
associates each `edge_index` with a specific relation.

```python
from torch_geometric.data import HeteroData
data = HeteroData()
data["user"].node_id = torch.arange(len(unique_user_id))
data["movie"].node_id = torch.arange(len(movies_df))
data["movie"].x = movie_feat
data["user", "rates", "movie"].edge_index = edge_index_user_to_movie
data = T.ToUndirected()(data)
```

`T.ToUndirected()` adds reverse edges (`rev_rates`) so message passing flows both
user→movie and movie→user.

**Splitting** uses PyG's built-in `transforms.RandomLinkSplit` (vs. the manual masking
approach used for node classification):

```python
import torch_geometric.transforms as T

transform = T.RandomLinkSplit(
    num_val=0.1,                    # 10% validation edges
    num_test=0.1,                   # 10% test edges
    disjoint_train_ratio=0.3,       # 30% of train edges reserved for supervision
    neg_sampling_ratio=2,           # 2 negative samples per positive edge (val/test)
    add_negative_train_samples=False,
    edge_types=("user", "rates", "movie"),
    rev_edge_types=("movie", "rev_rates", "user"),
)
```

Key concept: **`disjoint_train_ratio`** splits training edges into two disjoint groups:
- edges used for **message passing**, stored in `edge_index`
- edges used for **supervision** (the loss signal), stored in `edge_label_index`

These sets must not overlap. In the resulting `train_data`: `edge_index` has 56,469
edges (70% of the 80,669 training edges) and `edge_label_index` has 24,201 (30%).
Reverse edges (`rev_edge_types`) are used only for message passing, never for training
supervision.

Validation/test sets reuse all prior edges for message passing (e.g., test `edge_index`
= 90,753 = train + val edges) and add their own `edge_label_index` plus negative samples
generated by `RandomLinkSplit` (e.g., validation: 30,249 = 10,083 positive + 20,166
negative).

**Mini-batch loading** via `LinkNeighborLoader` — necessary for graphs exceeding
CPU/GPU memory, sampling a subgraph of neighbors per iteration:

```python
from torch_geometric.loader import LinkNeighborLoader

edge_label_index = train_data["user", "rates", "movie"].edge_label_index
edge_label = train_data["user", "rates", "movie"].edge_label

train_loader = LinkNeighborLoader(
    data=data,
    num_neighbors=[20, 10],   # 20 neighbors hop 1, 10 neighbors hop 2
    neg_sampling_ratio=2,
    edge_label_index=(("user", "rates", "movie"), edge_label_index),
    edge_label=edge_label,
    batch_size=128,
    shuffle=True,
)
```

### 12.2.4 Encoder–decoder architecture

**Top-level model**, combining embedding generation + heterogeneous GNN + dot-product
decoder:

```python
class MovieLensLinkPredictor(torch.nn.Module):
    def __init__(self, gnn_model, data, hidden_channels):
        super().__init__()
        self.embedding = MovieLensEmbedding(
            data["user"].num_nodes, data["movie"].num_nodes, hidden_channels
        )
        self.gnn = gnn_model(
            data.metadata(), hidden_channels, hidden_channels, hidden_channels
        )
        self.classifier = DotProduct()

    def forward(self, data):
        x_dict = self.embedding(data)
        x_dict = self.gnn(x_dict, data.edge_index_dict)
        pred = self.classifier(
            x_dict["user"], x_dict["movie"],
            data["user", "rates", "movie"].edge_label_index
        )
        return pred
```

**Embedding generation** — different strategies per node type. Users have no intrinsic
features, so their embeddings are learned purely from an `nn.Embedding` lookup table.
Movies use a two-step approach: a linear transform of the 20-dim genre feature vector,
summed with a learned `nn.Embedding`, giving both a meaningful cold-start representation
and trainable capacity:

```python
class MovieLensEmbedding(torch.nn.Module):
    def __init__(self, user_input_dim, movie_input_dim, out_dim):
        super().__init__()
        self.movie_lin = torch.nn.Linear(20, out_dim)
        self.user_emb = torch.nn.Embedding(user_input_dim, out_dim)
        self.movie_emb = torch.nn.Embedding(movie_input_dim, out_dim)

    def forward(self, data):
        return {
            "user": self.user_emb(data["user"].node_id),
            "movie": self.movie_lin(data["movie"].x) +
                     self.movie_emb(data["movie"].node_id),
        }
```

**Heterogeneous encoder** — PyG's `to_hetero()` automatically converts a homogeneous
base GNN model into a heterogeneous one, driven by the graph's `metadata()` (node/edge
types):

```python
from torch_geometric.nn import to_hetero

class HeteroBaseModel(torch.nn.Module):
    def __init__(self, metadata, input_dim, hidden_dim, out_dim, base_model):
        super(HeteroBaseModel, self).__init__()
        self.base_model = base_model(input_dim, hidden_dim, out_dim)
        self.hetero_model = to_hetero(self.base_model, metadata=metadata)

    def forward(self, x_dict, edge_index_dict):
        return self.hetero_model(x_dict, edge_index_dict)

class HeteroSAGE(HeteroBaseModel):
    def __init__(self, metadata, input_dim, hidden_dim, out_dim):
        super(HeteroSAGE, self).__init__(
            metadata, input_dim, hidden_dim, out_dim, SAGE
        )
```

Note: for heterogeneous GCN, the book uses **`GraphConv`** (not `GCNConv`) wrapped by
`to_hetero`, because `GCNConv` assumes a single node/edge type and degree normalization
that doesn't generalize, while `GraphConv` supports the separate root/neighbor
transformations required in heterogeneous settings.

**The decoder — dot product.** Computes the dot product between user and movie
embeddings to quantify compatibility; higher values indicate stronger predicted
interaction likelihood. Paired with `F.binary_cross_entropy_with_logits`, which fuses
sigmoid activation (converting scores to probabilities) with binary cross-entropy loss
(measuring divergence from actual interaction labels) — analogous to how `log_softmax` +
`CrossEntropyLoss` pair for node classification.

### 12.2.5 Evaluation and analysis — link prediction

Trained for 55 epochs on a T4 Colab machine.

| Encoder | Parameters | Training time (s) |
|---|---|---|
| GCN | 713,408 | 826 |
| GAT | 1,066,880 | 956 |
| SAGE | 713,408 | 777 |

SAGE is most efficient, GAT least. Parameter counts here are far larger than for node
classification, due to the added embedding layers and heterogeneous processing;
training time scales accordingly.

**Precision / recall / F1** on the validation set:

- **Precision** — SAGE highest and most reliable (fewest false positives → fewer
  irrelevant recommendations). GCN slightly worse but still high. GAT lowest, with more
  variability, meaning more incorrect predictions of user engagement.
- **Recall** — GCN highest (most comprehensive at capturing true ratings), SAGE close
  behind, GAT weakest (misses a significant portion of actual user–movie links).
- **F1-score** — SAGE highest (best balance). GCN performs well thanks to high recall but
  weaker precision. GAT struggles on both axes, yielding the weakest F1.

**Confusion matrices** on the testing dataset:

| Model | True negatives (non-existing links) | True positives (existing links) | False negatives | False positives |
|---|---|---|---|---|
| SAGE | 94.6% (19,084) | 71.5% (7,211) | 28.5% (2,872) | 5.4% (1,082) |
| GCN | 91.7% (18,488) | 78.6% (7,924) | 21.4% (2,159) | 8.3% (1,678) |
| GAT | 88.3% (17,808) | 75.4% (7,607) | 24.6% (2,476) | 11.7% (2,358) |

- **SAGE** — strongest at filtering out unlikely links (highest true-negative rate,
  lowest false-positive rate) but occasionally overlooks potential true ratings.
- **GCN** — best balance overall: high true-negative rate, best true-positive/recall,
  moderate false positives. "GCN offers the best balance between capturing potential
  ratings and avoiding irrelevant recommendations."
- **GAT** — weakest: highest false-positive rate, tends to over-recommend movies users
  are unlikely to rate.

## Takeaways

- Both node classification and link prediction fit the same **encoder–decoder
  framework**: preprocess raw data into a PyG graph (`Data` for homogeneous,
  `HeteroData` for heterogeneous), encode with a GNN (GCN/GAT/SAGE), decode with a
  task-specific head.
- **Node classification** (AML/Elliptic) uses a homogeneous graph, `log_softmax` +
  `CrossEntropyLoss` decoding, and manual node masking for train/val/test splits since
  most nodes are unlabeled.
- **Link prediction** (MovieLens) uses a heterogeneous graph (two node types, reverse
  edges via `ToUndirected`), dot-product + `binary_cross_entropy_with_logits` decoding,
  and PyG's `RandomLinkSplit`/`LinkNeighborLoader` for edge-level splitting and
  mini-batching at scale.
- `disjoint_train_ratio` matters: training edges must be split into message-passing
  edges (`edge_index`) and supervision edges (`edge_label_index`) to avoid leakage.
- `to_hetero()` converts any homogeneous base GNN into a heterogeneous one using the
  graph's `metadata()`; heterogeneous GCN uses `GraphConv` rather than `GCNConv`.
- Across both tasks, **GAT** is consistently the most parameter-heavy and slowest to
  train due to its multi-head attention mechanism, without a clear accuracy payoff.
- **SAGE** wins on precision/F1 in both tasks (best at avoiding false positives), while
  **GCN** tends to win on recall — a precision/recall trade-off to weigh per use case
  (e.g., AML favors catching illicit nodes; recommendations favor not over-suggesting).
- GNNs generalize well across very different domains (fraud detection, recommendation
  systems) using the same core architecture pattern.
