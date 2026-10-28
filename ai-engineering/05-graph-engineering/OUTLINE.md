---
origin: planning
status: Track A (01–08) written with labs and templates; Track B (09–12) not yet written
confidence: medium
cleaned: 2026-10-28
---
# 05 — Graph Engineering: chapter outline

> The plan for turning this pillar into a `notes/01-…md` chapter sequence like [03-harness](../03-harness-engineering/README.md) and [04-loop](../04-loop-engineering/README.md). **Progress (2026-10-28):** Track A is split into [notes/01–08](notes/01-graph-vs-loop.md), with [practice/01-agent-graph-labs.md](practice/01-agent-graph-labs.md) and two runnable [templates](templates/). Track B (09–12) is still outline only. [graph-engineering.md](graph-engineering.md) is kept intact until Track B is written.

---

## Shape of the pillar

There are two tracks. They share the word "graph" and meet in chapter 12.

| Track | Graph is | Nodes | Edges | Chapters |
|---|---|---|---|---|
| **A: agent graphs** | Execution topology | Units of computation | Permitted transitions | 01–08 |
| **B: knowledge graphs** | Retrieval structure | Entities | Typed relationships | 09–12 |

Chapter 12 (KG as shared agent memory) is the bridge: the knowledge graph becomes the state layer the execution graph coordinates through.

**Target layout** (matches 04-loop):

```
05-graph-engineering/
  README.md            mental model, rules of thumb, resource map (rewrite last)
  graph-engineering.md overview note (shrinks to a pillar summary once chapters exist)
  notes/01-…12-….md    the chapter sequence below
  practice/            labs (one file per track, or per chapter, see "Practice track")
  templates/           copy-ready graph skeletons (LangGraph generate-then-verify, fan-out/merge)
  sources/             book chapter PDFs + source PDFs
  kg-and-llms-in-action/        book notes (kept as the depth layer under Track B)
  Knowledge_Graphs_for_RAG-main/ Neo4j course (labs for Track B)
```

**Chapter conventions to follow** (from 04-loop-engineering/notes and 03-harness-engineering/notes): YAML frontmatter (`origin`, `sources`, `confidence`, `cleaned`); `# N — Title`; a one-line `>` summary; `---` between sections; tables for comparisons; a short "Where it sits" section; a "Working reference" line pointing at `~/.claude/refs/…`; and a closing `→ Next:` link to the following chapter.

**Key to the source references below.** `§N` = a section of [graph-engineering.md](graph-engineering.md). `KG chN` = a chapter of [kg-and-llms-in-action/](kg-and-llms-in-action/) (PDFs in [sources/](sources/)). `L#` = a notebook in [Knowledge_Graphs_for_RAG-main/code/](Knowledge_Graphs_for_RAG-main/code/). `LG L#` = `generative-ai/04-agentic-frameworks/AI-Agents-in-LangGraph-main/Lesson_#_Student.ipynb` (L1 ReAct from scratch, L2 LangGraph components, L3 agentic search, L4 persistence and streaming).

---

## Track A: agent graphs

### 01 — Graph vs. loop

**File:** `notes/01-graph-vs-loop.md`

**Scope.** What graph engineering is and where it sits (prompt → context → harness → loop → **graph**). The containment claim ("a loop is just a directed, cyclic graph"), why production agents are not DAGs, and where loop ends and graph begins. It closes on the default plus escalation rule: start with a loop, add a node only when one of five signals forces it. This chapter is the pillar's map. It should also say plainly that "graph" means two different things here, and point ahead to Track B.

**Feeds from.** §1 (definition, three framings, containment, where loop ends); §2 (production agents need cycles); §11 (choosing table, the escalation framing, five signals, 30-second decision tree, cost of a premature graph). The agent-graph vs. KG table from §9 goes in as a forward pointer only. Back-links: 04-loop `notes/01-what-a-loop-is.md` and `notes/02-loop-shapes.md`.

**New writing.** A "where it sits" section that mirrors 04-loop note 01, and a map of the pillar (the table of 12 chapters). §1's three framings lean on vendor blogs (TrueFoundry, Eigent), so rebase the definition on LangChain/LangGraph docs and Anthropic's *Building Effective Agents* (workflows vs. agents).

**Exercises.**
- *A loop is a one-node graph.* Take the agent loop from 04-loop (or `LG L1`) and re-express it as a LangGraph `StateGraph` with one node and a conditional self-edge. Confirm that behaviour is identical.
- *Decision-tree drill.* Run three real workloads through the 30-second decision tree (§11) and write one paragraph per workload: loop or graph, and which signal decided it.

### 02 — Graph primitives

**File:** `notes/02-graph-primitives.md`

**Scope.** The building blocks: nodes (deterministic code, a single LLM call, a tool call, a full agent), the node taxonomy (agent / deterministic function / router / human checkpoint), and edges (static and conditional: adaptive branching, error paths, approval gates, early exit). Also how much agency to spend per node, and the minimal LangGraph program. The reader should leave able to build and run a graph.

**Feeds from.** §3 Nodes, Edges; §12 LangGraph reference implementation; §13 tooling landscape (as a sidebar); `LG L2` (LangGraph components); KG ch15 §15.1 "Core LangGraph concepts" (a second worked vocabulary).

**New writing.** The "spend agency per node" design rule with a worked example (LangChain's docs agent: fixed API call → single LLM call → agent node). The §13 tooling list should be cut down to what first-party docs back up, since OpenClaw and Codex "graph-max" come from flowtivity only.

**Exercises.**
- *Generate-then-verify, the first graph.* Generator (LLM) → deterministic validator (schema/tests) → LLM reviewer → conditional edge back to the generator, or `END`. Bound it at N iterations. Save it as `templates/generate-then-verify.py`.
- *Agency audit.* Take the graph above and turn one LLM node into deterministic code. Record the token and variance change.

### 03 — State and reducers

**File:** `notes/03-state-and-reducers.md`

**Scope.** State as the substrate (a shared typed structure that nodes transform and edges route on), the difference between short-term and long-term state, and reducers as *the* concurrency primitive. Dynamic fan-out with the Send API. The single-writer rule. The handoff protocol (coupling lives in state, not in code). The concrete failure this chapter teaches is that parallel writes to a key with no reducer race.

**Feeds from.** §3 State; §2 (static edges are not enough; Send API); §4 handoff protocol; §9 "Cost of the swarm tier" (the true-dependency test: *does the next step read the previous step's output?*); §14 optimistic locking (`versionId` + `expectedChecksum`) as the production form of single-writer; `~/.claude/refs/agent-memory.md` single-writer rule.

**New writing.** Most of the chapter. graph-engineering.md has about ten lines on state. It needs: typed state schemas, built-in vs. custom reducers, what "the same key from two branches" does with and without a reducer, Send API semantics, and how to tell state from context (pointer to 02-context).

**Exercises.**
- *Fan-out / merge.* Use Send to spawn one reviewer per item in a list. Each writes `findings` into one key. Run it **without** a reducer and observe the concurrent-update error, then add an `operator.add` reducer, then a custom dedupe reducer.
- *True-dependency test.* Take a sequential pipeline you own and mark each edge as "reads previous output" or "incidental". Rewrite the incidental ones as fan-out and measure wall-clock time.

### 04 — Durable execution and interrupts

**File:** `notes/04-durable-execution-and-interrupts.md`

**Scope.** Checkpointers as the single mechanism behind human-in-the-loop interrupts, resume after crash, and time-travel debugging. Thread IDs, checkpoints per super-step, editing state while paused, resuming. Why a loop that pauses "has nowhere to put its stack". Where approval gates belong: at the edges where consequence concentrates, not uniformly across every node.

**Feeds from.** §3 Durable execution and interrupts; §12 (`compile(checkpointer=...)`); §7 Structural checkpoints; §14 (Planner pauses for approval; `MemorySaver`; session key and TTL); `LG L4` (persistence and streaming); `~/.claude/refs/agent-reliability.md` (checkpoint after each plan step, resumability).

**New writing.** Nearly all of it. The source has about six lines on this. Base it on the LangGraph persistence and human-in-the-loop docs (first-party), and cross-link to 03-harness `notes/06-long-horizon-execution.md` (state externalization) and 04-loop `notes/05-long-running-loops.md`.

**Exercises.**
- *Checkpoint + interrupt.* Add a SQLite checkpointer to the chapter 02 graph. Put an interrupt before a "send/publish" node, inspect and **edit** state while paused, then resume.
- *Crash and resume.* Kill the process mid-run, restart with the same `thread_id`, and confirm it resumes from the last checkpoint. Then use the state history to replay from an earlier checkpoint (time travel).

### 05 — Topology patterns

**File:** `notes/05-topology-patterns.md`

**Scope.** The pattern catalogue: supervisor, parallel fan-out/fan-in, hierarchical (subgraphs as nodes), handoff, and the parallel review graph. Generate-then-verify as the highest-yield first graph. Also how these patterns map onto Claude Code: subagents as nodes, orchestration decisions as edges, hooks as deterministic edges, the Agent SDK for programmatic topology.

**Feeds from.** §4 (all patterns + generate-then-verify); §8 (Claude Code mapping, three implementation levels, the workspace's `/akira`, `/workflow-research fan-out` and `/workflow-review` as live examples); §14 (n8n supervisor + five specialist subgraphs, as a pattern example); KG ch15 (intent → schema → text-to-Cypher → execute pipeline as a worked supervisor-less sequential graph with a dynamic conditional edge). Cross-link 03-harness `notes/07-orchestration.md` (subagents as a context firewall).

**New writing.** A per-pattern section in the same shape each time (use when / cost / failure mode / diagram), and the subgraph mechanics (state passing between parent and child). The "~3× faster" parallel-review claim (flowtivity) should be reproduced in the exercise, not cited.

**Exercises.**
- *Subgraphs.* Build the parallel review graph (security / logic / style reviewers → synthesizer → pass/fail gate) as a **subgraph** and embed it as one node in a parent planner → worker → review graph. Measure wall-clock time and tokens against a sequential version.
- *Same topology, Claude Code.* Re-implement the review graph as `.claude/agents/` subagents with a hook as the deterministic pass/fail edge. Note what you lose compared with LangGraph (state, checkpoints) and what you gain.

### 06 — When NOT to build a graph

**File:** `notes/06-when-not-to-build-a-graph.md`

**Scope.** The negative case. Work you cannot name ahead of time (generic deep research) belongs in a harness with a good loop. "Structure what you know, leave agency where you don't." The cost gate (fan-out tokens, a break-even pass rate), the cost of a premature graph, and "strengthen the verifier and ship the loop" (the most common "we need a graph" is really an overloaded verifier). Ends with incremental adoption: start at 3–5 nodes and measure a baseline before adding more.

**Feeds from.** §5 (LangChain on deep research, cost table, Anthropic ~15× tokens); §11 (cost of a premature graph, overloaded-verifier clause); §10 (five-stage adoption, "start small"); 04-loop `notes/03-the-scorekeeper.md` (the verifier).

**New writing.** Rebuild the cost argument on first-party numbers. The "~3× tokens per cycle" and "~50% break-even" figures come from flowtivity alone. Replace them with Anthropic's multi-agent research system post (the 15× figure, first-party) and with numbers you measure yourself in the exercise. The §10 AUDIT → TYPE methodology is flowtivity's too; keep it as one practitioner view or fold it into a shorter "start small" rule.

**Exercises.**
- *Break-even measurement.* Run the same task as a loop and as a fan-out graph across 20 trials. Record tokens, wall-clock time and pass rate, and find where the graph stops paying for itself.
- *Split the verifier, not the system.* Take a failing loop whose verifier judges several criteria. First split the verifier into per-criterion checks inside the loop and measure. Only then try a graph.

### 07 — Failure modes at scale

**File:** `notes/07-failure-modes-at-scale.md`

**Scope.** How graphs fail where single loops don't: mis-routing, deadlock and oscillation, double-writes to shared state, lost accountability. The control-theory failures of many interacting loops: Goodhart, upward blindness, inter-loop conflict, measurement decay. And the counter-measures: paired metrics, owned references, separated cadences, frozen nodes, anchors, per-node iteration bounds. It also covers swarm-scale risks: correlated errors across workers, verifier self-agreement bias (verifiers need isolated context), and file-space collisions.

**Feeds from.** §6 (Eigent: four failures, four principles, anchors, the `/sanyi` 不易 mapping); §1 ("what changes at the boundary is the failure mode"); §9 "Cost of the swarm tier" (two safeguards, correlated errors); §14 (Discovery bounded at 50, Builder at 100); 03-harness `notes/07-orchestration.md` (oscillation, deadlock) and `notes/08-maturity-and-failure-modes.md`.

**New writing.** A failure taxonomy table (symptom / root cause / detection signal / fix) that joins the Eigent control-theory list with the mechanical failures (deadlock, races, unbounded fan-out). Eigent is a vendor blog. Keep its framing but anchor Goodhart in the original literature, and check the claims against LangGraph's recursion-limit docs.

**Exercises.**
- *Fault injection.* Break your chapter 05 graph on purpose: (a) two nodes that route to each other forever, (b) two branches that write one key, (c) a reviewer that can see the generator's reasoning. For each, write down how you detected it and the guard that fixes it (recursion limit, reducer, context isolation).
- *Anchor drill.* Add a frozen held-out set as an anchor node that the graph's optimiser cannot edit. Show that a metric can climb while the anchor score falls (Goodhart in miniature).

### 08 — Governance and production

**File:** `notes/08-governance-and-production.md`

**Scope.** Operating a graph rather than demoing one. Covers attribution: stable `graph_id` / `run_id` / `node_id` carried through every model and tool call, and recording the *actual* runtime work graph, not just the declared one. Also node-level cost attribution and budgets beyond a per-run cap, approval checkpoints at consequential edges, model isolation behind routing, and the seven-question production checklist. The n8n AI Workflow Builder serves as the capstone case study: prompt-only specialisation, per-node bounds, optimistic locking, validation at the tool boundary, and published context budgets (compaction at 75% of the window, the artifact under construction capped at 30K tokens).

**Feeds from.** §7 (identity and tracing, cost control, structural checkpoints, the checklist); §14 (the whole case study incl. deployment); `~/.claude/refs/agent-runtime.md`; 06-eval (measuring graph correctness: forward link).

**New writing.** A tracing section built on first-party standards (OpenTelemetry GenAI semantic conventions; LangSmith / LangGraph tracing docs) rather than TrueFoundry's gateway framing. Verify the n8n case study against n8n's own source/docs (the AI Workflow Builder lives in the n8n repo) before reusing its constants. Add a short "Next layer → 06-eval" section.

**Exercises.**
- *Trace and attribute.* Instrument the chapter 05 graph so every span carries graph, run and node IDs. Produce a per-node cost table for 10 runs and find the node that dominates spend.
- *Checklist audit.* Score your graph against the seven-question checklist (§7). Fix the two weakest answers.

---

## Track B: knowledge graphs

### 09 — KG fundamentals and Cypher

**File:** `notes/09-kg-fundamentals-and-cypher.md`

**Scope.** What a knowledge graph is and why it pairs with LLMs: graph basics, the property-graph (LPG) vs. RDF choice, ontologies as schema, and typed edges ("the edge type IS the knowledge"). Then Neo4j and enough Cypher to read and write: `MATCH`, `MERGE`, variable-length paths, and parameters. Opens with the agent-graph vs. KG distinction table so Track B starts clean.

**Feeds from.** KG appendix A (intro to graphs); KG appendix B (Neo4j, Cypher, APOC); KG ch1 (§1.1, §1.3 drawbacks of LLMs mitigated by KGs, §1.4.1 four pillars of KGs); KG ch3 ("RDF or LPG? A goal-driven discussion", ontology ingestion with Neosemantics); KG ch2 (KG vs. LLM knowledge acquisition: a short excerpt only); §9 (distinction table); §3 Typed edges. Notebook: `L2-query_with_cypher.ipynb`; course notes `Lesson_0.md`–`Lesson_2.md`.

**New writing.** A one-page Cypher cheat sheet, and a condensed "RDF vs. LPG" decision. The book chapters run long (ch3 alone is 850 lines of notes), so the chapter should be a summary that links down to them. The "~18% accuracy from typed edges" figure is from flowtivity. Either cite a primary source or drop the number.

**Exercises.**
- *Neo4j lab.* Work through `L2-query_with_cypher.ipynb` (restore `data/neo4j_L2.dump` or use a Neo4j Aura free instance).
- *Model your own domain.* Model this repo's notes as a small KG: notes, concepts and sources as nodes; `DEPENDS_ON`, `REFERENCES` and `SUPERSEDES` as typed edges. Write five Cypher queries, including one variable-length path ("what does chapter 12 transitively depend on?").

### 10 — Building KGs with LLMs: extraction and NED

**File:** `notes/10-building-kgs-with-llms.md`

**Scope.** Turning unstructured text into a graph: named-entity recognition, relation extraction, schema-constrained structured output, graph modelling and metagraphs, normalisation, and entity resolution / named-entity disambiguation (NED) against a domain ontology. It also covers when traditional NLP beats LLMs, and why entity resolution is the load-bearing sub-problem: at 85% per-hop accuracy a 5-hop traversal is ~44% trustworthy.

**Feeds from.** KG ch5 (extraction pipeline, LLM roles in KG generation, prompt guidelines, "traditional NLP or LLMs?"); KG ch6 (graph modelling, metagraph, normalisation, graph-based entity resolution); KG ch7 (NED, ontology integration, SoHO KG); KG ch8 (NED with open LLMs: candidate selection, path-to-text disambiguation); KG appendix C (entity normalisation with UMLS/scispaCy, LLM normalisation alternative); §9 (per-hop accuracy compounding; the Extract/Resolve/Assemble/Query model-tier table). Notebooks: `L3-prep_text_for_RAG.ipynb`, `L4-construct_kg_from_text.ipynb`, `L5-add_relationships_to_kg.ipynb`, `L6-expand_the_kg.ipynb` (course notes `Lesson_3.md`–`Lesson_6.md`).

**New writing.** A single end-to-end pipeline diagram (chunk → extract → resolve → assemble → load) that ties the book and the course together, plus a section on evaluating extraction (precision/recall of entities and edges, false-merge rate) that links to 06-eval. The book's domain examples (biomedical, archives, SoHO) should become one short paragraph each, not reproductions.

**Exercises.**
- *Neo4j labs L3–L6.* Build the SEC Form 10-K graph: chunk, embed, add relationships, expand with a second data source.
- *Tiered extraction with a measured false-merge rate.* Extract entities with a cheap model under a JSON schema, then resolve with a stronger model. Hand-label 50 mentions and report precision, recall and false merges. Make resolution **reversible**: store alias edges, never destructive merges.

### 11 — KG-powered RAG and text-to-Cypher

**File:** `notes/11-kg-rag-and-text-to-cypher.md`

**Scope.** Querying a KG from natural language. Covers vector RAG and its multi-hop limits, GraphRAG (graph-enhanced retrieval, hybrid vector + graph), and text-to-Cypher with schema injection, metadata and intent detection. Also the fragility of RAG under incomplete retrieval. The book's LangGraph QA agent is the hinge back to Track A: intent detection → schema extraction → text-to-Cypher → execution → a dynamic conditional edge that retries or answers.

**Feeds from.** KG ch13 (vector RAG limits, Graph RAG, KG-enhanced retriever tool, ReAct over a KG); KG ch14 (policing KG, RAG fragility, schema-based querying, metadata, intent detection); KG ch15 (LangGraph pipeline: state design, the four agents, post-query conditional edge); §9 (vector vs. graph rule of thumb; the 53.4% vs. 42.9% multi-hop claim). Notebook: `L7-chat_with_kg.ipynb` (course note `Lesson_7.md`).

**New writing.** A comparison of retrieval modes (vector / graph traversal / text-to-Cypher / hybrid) with when-to-use guidance. Replace the flowtivity accuracy numbers with a first-party GraphRAG source (Microsoft Research's GraphRAG paper, arXiv 2404.16130, plus Neo4j's GraphRAG docs) or with your own measurement.

**Exercises.**
- *Neo4j lab L7.* Chat with the 10-K KG through a Cypher-generating chain.
- *Text-to-Cypher as generate-then-verify.* Build a LangGraph pipeline (the chapter 02 pattern) where the generator writes Cypher and the validator runs `EXPLAIN` / checks the schema. Failures route back with the error. Compare vector-only vs. hybrid retrieval on 20 hand-written multi-hop questions.

### 12 — KG as shared agent memory (the bridge)

**File:** `notes/12-kg-as-shared-agent-memory.md`

**Scope.** Where the two tracks meet. Read loop → swarm → graph as three capacity unlocks: swarms add redundancy because nothing connects the workers, and a shared typed KG turns that redundancy into accumulation. "The agent forgets, the graph does not." The KG plays three roles at once: shared memory, grounding layer, persistent world model. Workers publish structured `GraphUpdate`s carrying provenance. The chapter also covers the five planes (control, execution, artifact, graph, evaluation) and the anti-pattern "the chat transcript became the database". The non-negotiables are reversible entity resolution and complete provenance, because a false merge poisons every agent that reads after it. Swarm cost anchors go here too.

**Feeds from.** §9 "The two senses converge: KG as shared memory" and "Cost of the swarm tier"; [sources/graph-engineering-karpathy-loop-anthropic-playbook-2026.pdf](sources/graph-engineering-karpathy-loop-anthropic-playbook-2026.pdf) (community synthesis of the same loop → swarm → graph argument); `~/.claude/refs/agent-memory.md` (memory taxonomy, single-writer, cross-agent store); 02-context `notes/06-memory.md` and [memory-augmented-rag-notion-export.md](../02-context-engineering/sources/memory-augmented-rag-notion-export.md) (memory taxonomy, product memory designs; link to them, don't duplicate); chapters 03 (reducers / single-writer) and 10 (reversible ER).

**New writing.** The chapter that ties the pillar together: how the execution graph's state (chapter 03) and a persistent KG divide responsibilities (in-run state vs. cross-run, cross-agent memory). §9's sources are secondary (pkhamdee.blog, youmind, the untitled PDF). Re-source the core claims from first-party material: Karpathy's autoresearch repo, Anthropic's own docs for the Dynamic Workflows limits (1,000 sub-agents / 16 concurrent), and the KG construction cookbook in Anthropic's `claude-cookbooks` repo. Verify the Bun port "$165,000" figure against Bun's own write-up or drop it.

**Exercises.**
- *Swarm with and without shared memory.* Fan out N research workers over a corpus. Run A: no shared state, synthesizer reads all outputs. Run B: workers publish `GraphUpdate`s (nodes, edges, run_id, agent_id, source span) to a shared NetworkX or Neo4j graph, and the synthesizer queries a bounded subgraph with cited edges. Compare redundant findings, tokens, and answer quality.
- *Contamination drill.* Inject one false merge into run B's graph. Trace which downstream answers it corrupts, then roll it back using provenance alone.

---

## Optional readings

Not core. Read when you need graph ML rather than graph engineering.

| Reading | Why optional |
|---|---|
| KG ch9 — [ML on knowledge graphs](kg-and-llms-in-action/09-ml-on-knowledge-graphs.md) | Task taxonomy (node/link/graph-level); worth a skim for vocabulary |
| KG ch10 — [Graph feature engineering](kg-and-llms-in-action/10-graph-feature-engineering.md) | Centrality and PageRank features; useful for analytics on a KG you've built |
| KG ch11 — [Graph representation learning and GNNs](kg-and-llms-in-action/11-graph-representation-learning-gnns.md) | Embeddings, encoder–decoder, Node2Vec |
| KG ch12 — [Node classification and link prediction](kg-and-llms-in-action/12-node-classification-link-prediction.md) | PyG case studies (Elliptic AML, MovieLens) |
| KG ch4 — [Multisource integration](kg-and-llms-in-action/04-multisource-integration.md) | Biomedical case studies (PPI, Hetionet, metapaths); good domain example, not needed for the track |
| KG ch2 — [Intelligent systems: a hybrid approach](kg-and-llms-in-action/02-intelligent-systems-hybrid.md) | Conceptual background; chapter 09 takes one table from it |

---

## Source quality: replace before splitting

graph-engineering.md leans on secondary and SEO-grade posts. Per [SOURCES.md](../SOURCES.md), Tier 2 sources are gap-detectors, not citations of record. Before the chapters are written, swap or corroborate:

| Source in graph-engineering.md | Problem | Used in | Replace with / corroborate via |
|---|---|---|---|
| flowtivity.ai, "graph engineering 2026 guide" | Vendor marketing; supplies most of the hard numbers (~3× tokens, ~50% break-even, ~18% typed-edge gain, 53.4 vs 42.9% multi-hop, "~3× faster"), plus the OpenClaw / Codex "graph-max" tooling claims | §1, §3, §4, §5, §9, §10, §13 | Your own measurements (ch 06 exercise); GraphRAG paper (arXiv 2404.16130); LangGraph docs |
| youmind.com/landing/x-viral-articles/… | Viral-article landing page; source of the Bun $165k figure and Dynamic Workflows limits | §9 | Anthropic docs for Dynamic Workflows; Bun's own post; otherwise drop |
| pkhamdee.blog (Khamdee synthesis) | Personal blog synthesising primary sources | §9 | Karpathy's autoresearch repo; Anthropic's KG construction cookbook (`claude-cookbooks`); Anthropic engineering posts |
| [sources/graph-engineering-karpathy-loop-anthropic-playbook-2026.pdf](sources/graph-engineering-karpathy-loop-anthropic-playbook-2026.pdf) | Community-compiled; carries an Anthropic logo but says "not affiliated … not endorsed" | ch 12 | Same as above; cite as secondary only |
| explainx.ai/post/graph-engineering | SEO aggregator; also quoted in the 04-loop README | frontmatter | Drop; LangChain's "3 years of graph engineering" carries the same line first-hand |
| medium.com/@GaoDalie_AI, "forget loop engineering" | Opinion piece; the doc itself says it overstates | §1 | Keep as a quote at most; don't cite as evidence |
| medium.com/@rajveer.rathod1301, n8n deep dive | Third-party teardown of n8n | §14 | n8n's own source and docs for the AI Workflow Builder; `docs.n8n.io` (already cited) |
| aibuilderclub.com (two posts) | Tier 2 aggregator per SOURCES.md | §8, §11 | Claude Code docs (subagents, hooks), Claude Agent SDK docs; Anthropic *Building Effective Agents* |
| truefoundry.com enterprise guide | Vendor (sells an AI gateway); framing is gateway-centric | §1, §7 | OpenTelemetry GenAI semantic conventions; LangSmith / LangGraph tracing docs |
| eigent.ai blog | Vendor blog; framing is sound but uncited | §1, §6 | Keep as a framing source; anchor Goodhart in the original literature |
| Anthropic multi-agent research system ("~15× tokens") | First-party, but quoted without a link | §5, §8 | Add the direct link to Anthropic's engineering post |

Keep as first-party: LangChain's "3 years of graph engineering with LangGraph", LangGraph docs/GitHub, `docs.n8n.io`, Addy Osmani (Tier 1 in SOURCES.md).

---

## Practice track

Following 04-loop, labs go in `practice/` at the pillar root. 03-harness uses `notes/practice/`, so pick one and use it in both pillars. Suggested files:

- `practice/01-agent-graph-labs.md`: chapters 01–08 exercises as one progressive build, where the generate-then-verify graph from ch 02 gains state (03), checkpoints (04), subgraphs (05), fault guards (07) and tracing (08). Uses `LG L1`–`L4`.
- `practice/02-knowledge-graph-labs.md`: the Neo4j course run in order (`L2` → `L7`), then the own-domain KG and the shared-memory swarm (ch 12).
- `templates/`: `generate-then-verify.py`, `fan-out-merge.py`, `graph-update.schema.json` (the `GraphUpdate` shape from ch 12).

Before running the Neo4j labs: `Knowledge_Graphs_for_RAG-main/code/.env` holds live credentials. It is gitignored and has never been committed, but rotate the keys if the repo or that folder is ever shared.

---

## Housekeeping and open items

- **memory.md overlap (to resolve later).** The Notion export on memory-augmented RAG moved to [02-context-engineering/sources/memory-augmented-rag-notion-export.md](../02-context-engineering/sources/memory-augmented-rag-notion-export.md). It overlaps 02-context `notes/06-memory.md`. Merge what's new into that note, then decide whether the export stays as a source.
- **Off-topic papers.** The 20 non-graph papers (word2vec, InstructGPT, GPT-4 report, CoT, SelfCheckGPT, Generative Agents, Gorilla, ToolLLM, batch norm, calibration, interpretability, ML tech debt and others) were byte-identical copies of files already in `06-eval/evaluation/` (and, all but one, in `readings/general/`). They are parked in `06-eval/evaluation/_duplicates-from-05-graph-engineering/` and can be deleted.
- **README rewrite.** Do this after the chapters exist. Add a numbered topic-notes list like 03-harness, and drop the external-reference list once sources are re-based.
- **graph-engineering.md** becomes the pillar overview (as `harness-engineering.md` is for 03) once its sections have moved into chapters. Keep the §-to-chapter mapping above as the split plan.
