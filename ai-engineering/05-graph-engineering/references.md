# References — Graph Engineering

> Every source the notes cite, mapped to notes. **★** = read first. Local PDFs live in [sources/](sources/). Vendor and secondary posts are flagged in [Source quality](#source-quality); the notes flag numbers that rest on them.

---

## Books and courses

| | Source | Notes |
|---|---|---|
| ★ | Negro et al., *Knowledge Graphs and LLMs in Action* (Manning, 2025). Chapter PDFs in [sources/kg-and-llms-in-action/](sources/kg-and-llms-in-action/). Folded in as: ch. 1–3 and appendices A–B → [09](notes/09-kg-fundamentals-and-cypher.md); ch. 4–8 and appendix C → [10](notes/10-building-kgs-with-llms.md); ch. 13–15 → [11](notes/11-kg-rag-and-text-to-cypher.md); ch. 9–12 → [13](notes/13-graph-ml-and-gnns.md). Ch. 4's DWPC material is in 13. Notes cite it as `(*KG & LLMs in Action*, ch. N)` | 09, 10, 11, 13 |
| ★ | DeepLearning.AI × Neo4j, [*Knowledge Graphs for RAG*](https://www.deeplearning.ai/short-courses/knowledge-graphs-rag/) (Kollegger, 2024). Notebooks folded in as commented snippets (L1–L2 → 09, L3–L7 graph building → 10, L3–L7 retrieval → 11); figures in [sources/images/](sources/images/) as `kollegger-knowledge-graphs-for-rag-*`. An `L#` in a note is a lesson of this course | 09, 10, 11 |
| ★ | Bojie Li, *AI Agents in Depth* (2026), [ch. 10 Multi-Agent Collaboration](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter10.md): two design dimensions, the new-information test, handoff packages, A2A, Byzantine faults, MAST. Ch. 3's RAPTOR vs GraphRAG comparison is in 11 | 05, 07, 11 |
| ★ | Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* (Packt, 2025). Chapter PDFs in [sources/building-ai-agents-llms-rag-kgs/](sources/building-ai-agents-llms-rag-kgs/). Folded in as: ch. 7 → [09](notes/09-kg-fundamentals-and-cypher.md#taxonomies-ontologies-and-just-enough-semantics) (upper vs domain ontologies; `married_to` is symmetric, not transitive), [10](notes/10-building-kgs-with-llms.md#after-the-load-assess-clean-enrich-retire) (KG lifecycle and quality dimensions; the Cypher-writing prompt as a counter-example), [11](notes/11-kg-rag-and-text-to-cypher.md#what-to-retrieve-and-how-to-hand-it-over) (granularity, retrievers, graph-to-prompt formats, HybridRAG), [13](notes/13-graph-ml-and-gnns.md#when-the-llm-does-the-graph-reasoning-itself) (RotatE/ATTH, LLM as labeller, LLM graph reasoning and its limits); ch. 9 → [05](notes/05-topology-patterns.md) (Virtual Lab, HuggingGPT), [06](notes/06-when-not-to-build-a-graph.md) (travel planner as a pipeline), [07](notes/07-failure-modes-at-scale.md) (nine-judge court). Figures 7.20, 7.31, 9.7, 9.26 in [sources/images/](sources/images/) as `building-ai-agents-llms-rag-kgs-*`. A survey-style book: most claims are relayed from papers, which the notes mark as not yet read | 05, 06, 07, 09, 10, 11, 13 |
| | Albada, *Building Applications with AI Agents* (O'Reilly, 2025). Chapter PDF in [sources/building-applications-with-ai-agents/](sources/building-applications-with-ai-agents/). Folded in as: ch. 8 → [05](notes/05-topology-patterns.md) (actor-critic as self-review, supervisor mis-routing, hierarchical and semantic tool selection, A2A, ADAS with Fig. 8-1, transports from in-process to actor frameworks), [07](notes/07-failure-modes-at-scale.md) (mis-routing) | 05, 07 |
| | Oshin & Campos, *Learning LangChain* (O'Reilly, 2025). Chapter PDFs in [../../generative-ai/01-llm-fundamentals/sources/learning-langchain/](../../generative-ai/01-llm-fundamentals/sources/learning-langchain/). Folded in as: ch. 5 → [02](notes/02-graph-primitives.md) (the agency ladder with Fig. 5-1, the LLM router), [03](notes/03-state-and-reducers.md#input-and-output-schemas-the-graphs-public-interface) (input and output schemas). Written against 2025 LangGraph; keyword names have changed since | 02, 03 |
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
| | Agentopia: 100 agents over ten simulated years | [2606.07513](https://arxiv.org/abs/2606.07513) | 05 |
| | Pan et al., *Unifying Large Language Models and Knowledge Graphs: A Roadmap* (2023). Via Raieli & Iuculano ch. 7 (KG distillation from an LLM, LLMs as encoders for KG completion); not yet read | [2306.08302](https://arxiv.org/abs/2306.08302) | 10 |
| | Peng et al., *Graph Retrieval-Augmented Generation: A Survey* (2024). Via ch. 7 (G-indexing / G-retrieval / G-generation, granularity, prompt formats); not yet read | [2408.08921](https://arxiv.org/abs/2408.08921) | 11 |
| | Sarmah et al., *HybridRAG* (2024). Via ch. 7; not yet read | [2408.04948](https://arxiv.org/abs/2408.04948) | 11 |
| | Wu et al., *Medical Graph RAG* (MedGraphRAG, 2024). Via ch. 7; SOTA claim not checked | [2408.04187](https://arxiv.org/abs/2408.04187) | 11 |
| | Graph-and-LLM survey (2024) cited for ch. 7's Figs. 7.24–7.30. Via ch. 7 (task taxonomy, prompting methods, think/verify on graphs); not yet read | [2404.14809](https://arxiv.org/abs/2404.14809) | 13 |
| | SFT on graph tasks (source of ch. 7's Fig. 7.31). Via ch. 7; not yet read | [2403.04483](https://arxiv.org/abs/2403.04483) | 13 |
| | Hamilton, nine-judge simulated court (2023). Via Raieli & Iuculano ch. 9 | [2301.05327](https://arxiv.org/abs/2301.05327) | 07 |
| | Shen et al., *HuggingGPT* (2023). Via ch. 9 | [2303.17580](https://arxiv.org/abs/2303.17580) | 05 |
| | Hu, Lu & Clune, *Automated Design of Agentic Systems* (ADAS, ICLR 2025). Via Albada ch. 8 | [2408.08435](https://arxiv.org/abs/2408.08435) | 05 |

<!-- citegraph:origins start -->
## Where the ideas come from

Generated by `citegraph.py refs --write` on 2026-10-31; rerun it instead of editing between the markers. These works are cited by at least 3 of this pillar's papers, at least 2 of them for the method, so an idea most likely starts there. When a note states one of these ideas, cite the origin as well as the recent paper. **Cited by** counts this pillar's papers; **For method** counts those citing it for its method. ⚑ = not peer-reviewed. Fetch the missing ones with `citegraph.py primary --download`.

| Paper | Venue | Cited by | For method | We hold |
|---|---|---|---|---|
| [Brown 2020, Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) | NeurIPS 2020 | 6 | 2 | [✓ PDF](../../generative-ai/01-llm-fundamentals/sources/brown-2020-language-models-few-shot-learners.pdf) |
| [Lewis 2020, Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) | NeurIPS 2020 | 5 | 3 | [✓ PDF](../../generative-ai/02-rag-retrieval/sources/2005.11401v4.pdf) |
| [Touvron 2023, LLaMA: Open and Efficient Foundation Language Models](https://arxiv.org/abs/2302.13971) | ⚑ | 4 | 2 | [✓ PDF](../../generative-ai/01-llm-fundamentals/sources/touvron-2023-llama.pdf) |
<!-- citegraph:origins end -->

## AI Papers of the Week

| | Paper | arXiv | Notes |
|---|---|---|---|
| ★ | Rusu, Khanzadeh, Alalfi, *Selective Forgetting: A Graph-Based Memory Framework for Long-Term LLM Agents* (2026): an extraction-based conversational KG loses to flat retrieval on LongMemEval (F1 0.417 vs. 0.468); importance-scored pruning removes 9.8% of nodes at no F1 cost | [2608.28978](https://arxiv.org/abs/2608.28978) · [PDF](sources/rusu-2026-selective-forgetting.pdf) | [12](notes/12-kg-as-shared-agent-memory.md#build-path) |
| | Tran & Kiela, *Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets* (2026): single agent best or tied at matched budgets on FRAMES and MuSiQue; the DPI argument assumes perfect context use, and heavy context corruption reverses it | [2604.02460](https://arxiv.org/abs/2604.02460) · [PDF](sources/tran-2026-single-agent-llms-outperform-multi.pdf) | [05](notes/05-topology-patterns.md#when-multi-agent-beats-single-agent) · [06](notes/06-when-not-to-build-a-graph.md#what-fan-out-costs) |
| ★ | Kim et al., *Towards a Science of Scaling Agent Systems* (2025, Google/MIT): 260 controlled configurations; +80.8% to −70% vs. a single agent depending on task structure, mean −0.3%; negative returns once the single agent passes ~45%; 1.6–6.2× tokens; error amplification 17.2× independent vs. 4.4× centralized | [2512.08296](https://arxiv.org/abs/2512.08296) · [PDF](sources/kim-2025-towards-science-scaling-agent-systems.pdf) | [06](notes/06-when-not-to-build-a-graph.md#what-fan-out-costs) · [07](notes/07-failure-modes-at-scale.md#cascading-amplification) · [05](notes/05-topology-patterns.md#when-multi-agent-beats-single-agent) |

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
| Raieli & Iuculano, *Building AI Agents with LLMs, RAG, and Knowledge Graphs* | Ch. 7's extraction prompt says both "Be creative" and "Do not hallucinate", its few-shot answer stores a year as `age:1993` and writes each friendship in both directions, and the generated Cypher is executed unchecked (note 10 explains each); `LLMGraphTransformer` is from `langchain_experimental`; the `GraphCypherQAChain` call lacks `allow_dangerous_requests` and uses the old `langchain.chains` import; the graph-of-thoughts example turns "60 miles" into "60 km"; the ontology example calls `married_to` transitive (it is symmetric); "SFT beats larger models" rests on one example figure; most results are relayed from papers. Ch. 9's nine-judge ensemble is one model nine times, which the authors acknowledge. Other pillars' references credit this book to Rothman: the authors are Raieli & Iuculano | The cited papers; run the code against current LangChain |
| Albada, *Building Applications with AI Agents* | Ch. 8's actor-critic critic is the same model with the same history (self-review); the supervisor's exact-string router falls through to `END` silently (note 05) | LangGraph docs; Huang et al. on self-correction |
| Oshin & Campos, *Learning LangChain* | Ch. 5 uses `StateGraph(State, input=..., output=...)`, renamed `input_schema=` / `output_schema=` in later releases; it notes that `stream()` still emits internal keys | Current LangGraph API reference |
| *KG & LLMs in Action* | Some listings and numbers don't hold: Neo4j 5 procedure syntax, an unbound variable in the DWPC query, the IRF1 arithmetic, ch. 15 retry count and bug names. The notes give the corrected versions; ch. 10's PageRank figures don't reproduce and the note says so. Also: ch. 3 listing 3.11 has syntax errors, 3.13 needs Enterprise (`CREATE DATABASE`), 3.24 uses deprecated `id()`; appendix A dates the Panama Papers to 2023 (2016) and appendix B describes master/slave clustering (Raft since 4.0); ch. 4 gives Louvain modularity as ~0.40 in prose, 0.546 in Table 4.2, and its LLM prompt mixes DWPC scores from two metapaths; ch. 7 calls Zika a Togavirus (it's a flavivirus); appendix C's miRNA counts sum to 3,872, not the 4,874 claimed; ch. 10's betweenness table doesn't match its `normalized=True` code and Table 10.4 counts walks, not hops; ch. 11 calls GraphSAGE attention-based and swaps the BFS/DFS reading of Node2Vec; ch. 12's training loader gets the full graph (`data=data`, so test edges leak), and its counts disagree between figure, table and prose; ch. 14's few-shot template puts query before reasoning, against its own response format | Run the query yourself |
