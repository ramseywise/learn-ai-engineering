---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Appendix A: Introduction to graphs"
confidence: high
cleaned: 2026-07-29
---

# Appendix A — Introduction to Graphs

## A.1 What Is a Graph?

A **graph** is a simple, old mathematical data structure consisting of a set of
**vertices** (nodes/points) and **edges** (relationships/lines) used to model
relationships among a collection of objects.

### Origin: the Königsberg bridge problem

> "Legend says that it was the lazy Leonhard Euler who first started talking about
> graphs in 1736."

Königsberg (now Kaliningrad) straddled the Pregel River, with two islands connected to
each other and to the mainland by seven bridges. Euler wanted to cross each bridge
exactly once without retracing his steps. He formalized the city as a graph and proved
the walk was impossible — inventing graph theory rather than doing the walk.

### Formal definition

A graph is a pair `G = (V, E)`:
- `V` is a collection of vertices, `V = {V_i, i = 1, ..., n}`
- `E` is a collection of edges over `V`, designated by `E_ij = {(V_i, V_j) : V_i ∈ V, V_j ∈ V}`
- `E ⊆ [V]²` — the elements of `E` are two-element subsets of `V`

The simplest representation: draw a dot/circle per vertex, join two vertices with a
line to form an edge.

### Directed vs. undirected

- **Undirected graph** — edge traversal is valid in both directions. Example:
  `V = {1, 2, 3, 4, 5}`, `E = {(1,2), (1,5), (2,5), (2,4), (4,3)}`.
- **Directed graph** — a direction is defined on each edge. For edge `E_ij`, traversal
  runs from `V_i` to `V_j` but not the reverse. `V_i` is called the **tail** or
  **start node**; `V_j` is the **head** or **end node**.

### Weighted vs. unweighted

By default, edges are **unweighted**. When a numerical **weight** (a value conveying
significance) is assigned to edges, the graph is **weighted**. Weighting applies
independently to directed or undirected graphs.

### Adjacency, incidence, completeness

- Two vertices `x` and `y` of `G` are **adjacent** (or **neighbors**) if `{x,y}` is an
  edge of `G`.
- Edge `E_ij` connecting `V_i` and `V_j` is said to be **incident on** those two
  vertices.
- Two distinct edges `e` and `f` are adjacent if they share a vertex.
- If all vertices of `G` are pairwise adjacent, `G` is **complete** — every vertex is
  connected to every other vertex.

### Degree

The **degree** of a vertex is the total number of edges incident to it, equal to its
number of neighbors.

- Example (undirected graph, weighted figure A.4): vertex 2 has degree 3 (neighbors
  1, 4, 5); vertices 1, 4, 5 each have degree 2; vertex 3 has degree 1 (connected
  only to 4).
- **Directed graphs** split degree into:
  - **in-degree** — number of edges for which the vertex is the end node (arrowhead)
  - **out-degree** — number of edges for which the vertex is the start node (tail)
- **Average degree** of a graph, where `N` is the number of vertices:

  ```
  a = (1/N) · Σ(i=1..N) degree(V_i)
  ```

### Paths, simple paths, cycles

- A **path** is a sequence of vertices where each consecutive pair is connected by an
  edge.
- A **simple path** is a path with no repeating vertices.
- A **cycle** is a path in which the first and last vertex coincide.
- Example (figure A.2): `[1,2,4]`, `[1,2,4,3]`, `[1,5,2,4,3]` are paths; `[1,2,5]` is a
  cycle.

## A.2 Graphs as Models of Networks

A **network** is what a graph becomes once names and meanings are assigned to its
edges and vertices. The graph is the mathematical model for describing a network; the
network is the set of real-world relationships between objects (people,
organizations, nations, search results, brain cells, electrical transformers, etc.).
This flexibility — plus a graph's small disk-storage footprint — is what makes graphs
powerful for modeling complex systems.

> **NOTE.** In this context, the verb *model* means representing a system or
> phenomenon in a simplified way that a computer system can also easily process.

### Network types (same underlying graph, different semantics)

| Network type | Vertices | Edges represent |
|---|---|---|
| Social network | People | Any relationship (friendship, family, coworker) |
| Informational network | Web pages, documents, papers | Logical connections (hyperlinks, citations, cross-references) |
| Communication network | Computers/devices | Direct message-relay links |
| Transportation network | Cities | Direct flight/train/road connections |

The same graph structure can represent any of these depending purely on the meaning
(**semantics**) assigned to vertices and edges.

### Networks as information maps

Because graphs display connections clearly, they are often used as **information
maps**. Representing data as networks and applying graph algorithms lets analysts:
- find complex patterns
- make those patterns visible for further investigation and interpretation

Combining graph-powered ML with human interpretation (via visualization) enables
sophisticated pattern recognition.

**Case study — Panama Papers (ICIJ, 2023 reporting).** The International Consortium
of Investigative Journalists extracted entities (people, organizations,
intermediaries) and relationships (protector, beneficiary, shareholder, director)
from leaked financial documents, stored them as a network, and used graph
visualization to expose offshore tax structures used by global elites — a discovery
the text states "would have been impossible ... using traditional data mining tools."

**Case study — Amazon political-books network (Krebs, 2008 vs. 2012).** Vertices are
books; an edge is an **also-bought** pair (frequently purchased by the same
customer).
- **2008**: three distinct, non-overlapping clusters — an Obama-biography cluster, a
  Democratic (blue) cluster, and a Republican (red) cluster — with no bridging
  connections between red and blue, reflecting a polarized electorate.
- **2012**: the same analysis produced a much more interconnected network, with many
  books acting as **bridges** between clusters and no isolated clusters remaining —
  voters were reading across both candidates' material.

### Surrounding contexts

Because networks are abstractions of a concrete system, they are subject to
**surrounding contexts**: factors that exist outside a network's vertices and edges
but nonetheless shape how its structure evolves. A pure graph, by contrast, is a
mathematical object living in its own "Platonic world."

> **NOTE.** Mathematical Platonism is the metaphysical view that abstract
> mathematical objects exist independently of human language, thought, and
> practices.

**Homophily** (Greek: *love of the same*) is one of the most basic forces governing
social-network structure: links tend to connect people who are similar to one
another. Formally, if two people share characteristics in a proportion greater than
expected from the population (or subgroup) they're drawn from, they are more likely
to be connected — and the converse also holds: connected people are more likely to
share characteristics. This is why a person's Facebook friends aren't a random
sample but skew similar along ethnic, racial, geographic, age, occupation, interest,
and belief dimensions. The idea predates modern social networks — traced to Plato
("similarity begets friendship"), Aristotle ("people love those who are like
themselves"), and folk sayings ("birds of a feather flock together"). Homophily also
applies at the group, organization, or country level, not just individuals.

Understanding surrounding contexts and their forces aids ML tasks:
- **Networks are conduits for both wanted and unwanted flows** — marketers exploit
  personal-contact effectiveness via **viral marketing**.
- **Understanding these forces enables predicting how networks evolve**, letting data
  scientists proactively react to structural change or exploit it for business
  purposes (e.g., recommendation engines rely on homophily to make predictions for
  users with no history, based on the tastes of connected users).

## A.3 Representing Graphs

There are two standard ways to represent a graph `G = (V, E)` for computational
processing: **adjacency lists** and **adjacency matrices**. Both apply to directed,
undirected, and weighted graphs.

### Adjacency list

An array `Adj` of lists, one per vertex in `V`. For each vertex `u`, `Adj[u]`
contains every vertex `v` for which edge `E_uv` exists — i.e., all vertices adjacent
to `u` in `G`.

- **Undirected example** (figure A.11): vertex 1 has neighbors 2 and 5, so
  `Adj[1] = [2,5]`; vertex 2 has neighbors 1, 4, 5, so `Adj[2] = [1,4,5]`. Since
  undirected relationships have no inherent order, `Adj[1]` could equally be `[5,2]`.
- **Directed example** (figure A.12): only outgoing relationships are stored by
  convention (though the same technique works for ingoing ones — the key requirement
  is choosing one direction and staying consistent). Vertex 1 has one outgoing edge
  to 2, so `Adj[1] = [2]`; vertex 2 has outgoing edges to 4 and 5, so
  `Adj[2] = [4,5]`; vertex 4 has no outgoing edges, so `Adj[4] = []`.
- Implementation note: adjacency lists are commonly implemented as linked lists
  (each entry references the next), which makes adding/deleting elements efficient.

**Memory cost:**
- Directed `G`: sum of all adjacency-list lengths = `|E|` (each edge traversable in
  one direction, appears only in `Adj[u]`).
- Undirected `G`: sum of all adjacency-list lengths = `2 × |E|` (each undirected edge
  `E_uv` appears in both `Adj[u]` and `Adj[v]`).
- General: memory required is directly proportional to `|V| + |E|`.

**Weighted graphs:** adapt by storing the weight `w` of edge `E_uv` alongside `v` in
`Adj[u]`.

**Disadvantage:** no fast way to check whether a specific edge `E_uv` exists — you
must linearly search `Adj[u]` for `v`.

### Adjacency matrix

Assume vertices are numbered `1, 2, ..., |V|` consistently for the matrix's lifetime.
The adjacency matrix representation of `G` is a `|V| × |V|` matrix
`A = (a_uv)` such that:
- `a_uv = 1` if edge `E_uv` exists in the graph
- `a_uv = 0` otherwise

- **Undirected example** (figure A.13): row 1 has a 1 in columns 2 and 5 (vertex 1's
  connections); row 2 has 1s in columns 1, 4, 5; and so on.
- **Directed example** (figure A.14): row 1 has a 1 only in column 2 (vertex 1's one
  outgoing edge). Reading by **column** instead of row reveals inbound relationships
  — e.g., column 4 shows vertex 4 has inbound connections from vertices 2 and 3.
- **Weighted graphs:** set `a_uv = w` (the edge weight) instead of `1`.

**Memory cost:** directly proportional to `|V| × |V|`, independent of edge count. For
an undirected graph the matrix is symmetric along the main diagonal, so only half the
matrix needs to be stored, roughly halving memory.

**Advantages:** simpler to reason about for small graphs; for unweighted graphs, each
entry needs only one bit; supports fast `O(1)`-style lookup of whether a specific
edge exists.

### Choosing a representation

| Graph property | Preferred representation |
|---|---|
| **Sparse** (`\|E\|` much less than `\|V\|`) | Adjacency list — compact, usually the default choice |
| **Dense** (`\|E\|` close to `\|V\| × \|V\|`) | Adjacency matrix |
| Need fast edge-existence lookup | Adjacency matrix |
| Graph is reasonably small | Adjacency matrix (simpler, and unweighted graphs cost only 1 bit/entry) |

The adjacency list is at least as asymptotically space-efficient as the adjacency
matrix and is the method of choice for sparse graphs; the adjacency matrix trades
memory for simplicity and O(1) edge lookups, and wins when the graph is dense or
small.

## Takeaways

- A **graph** `G = (V, E)` is a set of vertices plus a set of edges connecting them;
  graph theory originated with Euler's 1736 solution to the Königsberg bridges
  problem.
- Core formal properties: **directed vs. undirected**, **weighted vs. unweighted**,
  **adjacency/incidence**, **completeness**, **degree** (split into in-degree/
  out-degree for directed graphs), and **paths/simple paths/cycles**.
- A **network** is a graph with semantic meaning attached to its vertices and edges
  (social, informational, communication, transportation, etc.) — the same graph
  structure can model very different real-world systems.
- Real networks are shaped by **surrounding contexts** — external forces like
  **homophily** ("similarity begets friendship") that drive structural evolution;
  understanding these forces powers applications like viral marketing and
  recommendation engines.
- Graphs are represented computationally as **adjacency lists** (compact, `O(|V|+|E|)`
  memory, ideal for sparse graphs, but slow edge-existence checks) or **adjacency
  matrices** (`O(|V|²)` memory, simple, fast edge lookups, ideal for dense or small
  graphs).
- Case studies (Panama Papers, Amazon political-book networks) show how combining
  graph algorithms with visualization surfaces patterns invisible to traditional data
  mining.
