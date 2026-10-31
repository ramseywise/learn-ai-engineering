# References — Graph Engineering

> Every source the notes cite, mapped to notes. **★** = read first. Local PDFs live in [sources/](sources/). Vendor and secondary posts are flagged in [Source quality](#source-quality); the notes flag numbers that rest on them.

---

## Books and courses

| | Source | Notes |
|---|---|---|
| ★ | Negro et al., *Knowledge Graphs and LLMs in Action* (Manning, 2025). Chapter PDFs in [sources/kg-and-llms-in-action/](sources/kg-and-llms-in-action/). Folded in as: ch. 1–3 and appendices A–B → [09](notes/09-kg-fundamentals-and-cypher.md); ch. 4–8 and appendix C → [10](notes/10-building-kgs-with-llms.md); ch. 13–15 → [11](notes/11-kg-rag-and-text-to-cypher.md); ch. 9–12 → [13](notes/13-graph-ml-and-gnns.md). Ch. 4's DWPC material is in 13. Notes cite it as `(*KG & LLMs in Action*, ch. N)` | 09, 10, 11, 13 |
| ★ | DeepLearning.AI × Neo4j, [*Knowledge Graphs for RAG*](https://www.deeplearning.ai/short-courses/knowledge-graphs-rag/) (Kollegger, 2024). Notebooks folded in as commented snippets (L1–L2 → 09, L3–L7 graph building → 10, L3–L7 retrieval → 11); figures in [sources/images/](sources/images/) as `kollegger-knowledge-graphs-for-rag-*`. An `L#` in a note is a lesson of this course | 09, 10, 11 |
| ★ | Bojie Li, *AI Agents in Depth* (2026), [ch. 10 Multi-Agent Collaboration](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter10.md): two design dimensions, the new-information test, handoff packages, A2A, Byzantine faults, MAST. Ch. 3's RAPTOR vs GraphRAG comparison is in 11 | 05, 07, 11 |
| | *LangGraph: A Visual Guide* ([sources/langgraph_extended.pptx](sources/langgraph_extended.pptx), 26 slides): nodes, edges, state, reducers, checkpointers, interrupts, streaming, subgraphs, LangGraph vs Google ADK. Also the house style for `make slides` | 03, 04, 05 |

## First-party docs and engineering posts

| | Source | Notes |
|---|---|---|
| ★ | LangGraph [docs](https://docs.langchain.com/langgraph) and [GitHub](https://github.com/langchain-ai/langgraph) | 02, 03, 04, 05, 07, 08 |
| ★ | LangChain, [*3 years of graph engineering with LangGraph*](https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph): production agents need cycles; loops are simplified graphs | 01–06 |
| ★ | Anthropic, [*Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents) | 01, 06, 12 |
| ★ | Anthropic, [*How we built our multi-agent research system*](https://www.anthropic.com/engineering/multi-agent-research-system): source of the ~15× token figure | 06, 07, 12 |
| | Anthropic, [knowledge graph construction cookbook](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide) | 10, 12 |
| | n8n, [*Hosting n8n*](https://docs.n8n.io/deploy/host-n8n): deployment surface for a self-hosted graph runtime | 08 |

## Papers

| | Paper | arXiv | Notes |
|---|---|---|---|
| ★ | Edge et al., *From Local to Global: A Graph RAG Approach to Query-Focused Summarization* (GraphRAG, 2024) | [2404.16130](https://arxiv.org/abs/2404.16130) | 11 |
| | Self-correction survey (TACL): self-review without tools is often neutral or harmful | [2406.01297](https://arxiv.org/abs/2406.01297) | 05 |
| | RLEF: training on execution feedback | [2410.02089](https://arxiv.org/abs/2410.02089) | 05 |
| | Plan-and-Act: a fine-tuned planner trained on synthetic plans, replanning after each step; 57.6% on WebArena-Lite | [2503.09572](https://arxiv.org/abs/2503.09572) | 05 |
| | Tran & Kiela: debate among copies of one model matches a single agent at equal compute | [2604.02460](https://arxiv.org/abs/2604.02460) | 05 |
| | Agentopia: 100 agents over ten simulated years | [2606.07513](https://arxiv.org/abs/2606.07513) | 05 |

## Secondary and vendor posts

Use these as gap-detectors, not citations of record (see [SOURCES.md](../SOURCES.md) Tier 2).

| Source | What the notes take from it | Notes |
|---|---|---|
| flowtivity.ai, [*Graph engineering 2026 guide*](https://flowtivity.ai/blog/graph-engineering-2026-guide-openclaw-codex/) | parallel review graph, typed edges, loop-vs-graph cost, 5-stage adoption | 01, 02, 05, 06, 09, 11, 12 |
| TrueFoundry, [*Graph engineering: enterprise guide*](https://www.truefoundry.com/blog/graph-engineering-enterprise-guide) | identity, cost attribution, approval checkpoints, 7-question production checklist | 01, 02, 04, 08 |
| Eigent, [*Graph engineering for AI agents*](https://www.eigent.ai/blog/graph-engineering-ai-agents) | control-theory framing: loop failure modes at scale, paired metrics, anchors | 01, 07 |
| AI Builder Club, [*Graph engineering with Claude Code*](https://www.aibuilderclub.com/blog/graph-engineering-with-claude-code) | subagents as nodes, hooks as deterministic edges | 01, 05 |
| GaoDalie, [*Forget loop engineering*](https://medium.com/@GaoDalie_AI/forget-loop-engineering-graph-engineering-is-about-this-713a9cf2e985) | the organisational-structure argument | 01 |
| pkhamdee, [*From Karpathy's loops to shared knowledge graphs*](https://pkhamdee.blog/2026/07/21/graph-engineering-from-karpathys-loops-to-shared-knowledge-graphs/) | loop → swarm → graph; KG as shared memory; tiered extraction; five-plane architecture | 12 |
| youmind, [*Graph engineering vs agent loops*](https://youmind.com/landing/x-viral-articles/graph-engineering-ai-agent-loops) | the true-dependency test, verifier context isolation, swarm cost anchors | 03, 07, 12 |
| Rathod, [*Inside n8n's AI Workflow Builder*](https://medium.com/@rajveer.rathod1301/inside-n8ns-ai-workflow-builder-a-complete-architecture-deep-dive-f2eeb2d57ec8) | supervisor-pattern case study: six agents, per-node iteration bounds, optimistic locking, context budgets | 03, 04, 05, 07, 08 |
| *Graph Engineering: The Karpathy Loop, Improved 1000x by Itself* (2026), [PDF](sources/graph-engineering-karpathy-loop-anthropic-playbook-2026.pdf) | community-compiled playbook | 12 |

---

## Source quality

| Source | Problem | Corroborate via |
|---|---|---|
| flowtivity.ai | Vendor marketing; supplies most of the hard numbers (~3× tokens, ~50% break-even, ~18% typed-edge gain, 53.4 vs 42.9% multi-hop, "~3× faster") and the OpenClaw / Codex tooling claims | Your own measurements; the GraphRAG paper; LangGraph docs |
| youmind.com viral-article landing page | Source of the Bun $165k figure and Dynamic Workflows limits | Anthropic docs for Dynamic Workflows; Bun's own post; otherwise drop |
| pkhamdee.blog | Personal blog synthesising primary sources | Karpathy's autoresearch repo; Anthropic's KG cookbook; Anthropic engineering posts |
| Karpathy-loop playbook PDF | Community-compiled; carries an Anthropic logo but says "not affiliated … not endorsed" | Cite as secondary only |
| explainx.ai/post/graph-engineering | SEO aggregator | Drop; LangChain's "3 years of graph engineering" has the same line first-hand |
| Medium, GaoDalie | Opinion piece; overstates | A quote at most, not evidence |
| Medium, Rathod n8n deep dive | Third-party teardown | n8n's own source and `docs.n8n.io` |
| aibuilderclub.com | Tier 2 aggregator | Claude Code docs (subagents, hooks), Claude Agent SDK docs, *Building effective agents* |
| truefoundry.com | Vendor (sells an AI gateway); gateway-centric framing | OpenTelemetry GenAI semantic conventions; LangSmith / LangGraph tracing docs |
| eigent.ai | Vendor blog; sound framing but uncited | Keep as framing; anchor Goodhart in the original literature |
| *KG & LLMs in Action* | Some listings and numbers don't hold: Neo4j 5 procedure syntax, an unbound variable in the DWPC query, the IRF1 arithmetic, ch. 15 retry count and bug names. The notes give the corrected versions; ch. 10's PageRank figures don't reproduce and the note says so | Run the query yourself |
