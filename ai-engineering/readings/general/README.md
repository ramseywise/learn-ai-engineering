# Readings Library

Primary-source tier of the [interviewing KB](../interviewing/README.md) and its
[curriculum pillars](../interviewing/guides/00-start-here.md). Folder names carry the
pillar number they feed (`0-` = cross-cutting). Papers are listed by arXiv ID where that
is the filename — resolve at `https://arxiv.org/abs/<id>`.

## Topic folders (number = pillar)

| Folder | Contents | Feeds pillar |
|---|---|---|
| `data-analytics/readings/` | Stats bookshelf: ISLR (Python), Practical Statistics for Data Scientists, Statistics Done Wrong, Think Stats/Bayes, Statistical Rethinking, Computer Age Statistical Inference, Python for Data Analysis, Storytelling with Data | 1-foundations, 10-product-delivery, deferred stats pillar |
| `2-llm-fundamentals/` | *Prompt Engineering for Generative AI* (O'Reilly, chapters) + CoT (2201.11903), Constitutional AI (2212.08073), LLaMA (2302.13971), GPT-4 (2303.08774), Gorilla (2305.15334), ToolLLM (2307.16789), generative agents (2304.03442) | 2-llm-fundamentals, 4-agents |
| `2-llm-rlhf/` | *Reinforcement Learning* (book chapters) + Sutton & Barto (RLbook2020), DQN (1312.5602), PPO (1707.06347), RLHF preferences (1706.03741), InstructGPT (2203.02155), DPO (2305.18290), ReAct, Reflexion, Tree-of-Thoughts | 2-llm-fundamentals (RLHF/reasoning) |
| `3-rag/` | Core RAG papers: RAG (2005.11401), Self-RAG (2310.11511), RAGAS (2309.15217), ARES (2311.09476), RAG survey (2312.10997), retrieval eval (SIGIR '24) | 3-rag, 6-evals-observability |
| `3-rag-knowledge-graphs/` | *Knowledge Graphs and LLMs in Action* (Manning, chapters incl. KG-RAG, GNNs, LangGraph QA agent) + word2vec (1301.3781), interpretability/calibration papers, human-AI interaction guidelines | 3-rag (KG-RAG), 10-product-delivery |
| `ai_engineering/` | Cross-pillar book library by theme: `ai design` (*Generative AI Design Patterns*), `ai engineer` (*AI Engineering*, Huyen), `ai performance` (*AI Systems Performance Engineering*), `ai_agent_applications` (*Building Applications with AI Agents*), `building_ai_agent`, `langchain`, `llm from scratch`, `llm handbook`, `mcp`, `multiagent context` | 4-agents, 5-context-cost, 6-evals, 7-security, 9-system-design |
| `8-data-eng-data-mesh/` | Data mesh / warehouse topology handouts (DM topologies, MDW) | 8-data-eng-mlops |
| `general/` | Classic-paper canon: attention (1706.03762), BERT (1810.04805), InstructGPT, Constitutional AI, TruthfulQA, SHAP, LIME, hidden technical debt (NIPS 2015), KDD metric pitfalls, LLM survey (2303.18223) | 1-foundations, 2-llm-fundamentals, 6-evals |

## Loose classics (root)

attention-is-all-you-need, wavenet, batch-normalization (+ rethinking), Bengio neural LM,
conversational-ai, Rasa dialogue transformers / dual-intent-entity, ALiBi (2108.12409),
agentic architectural patterns, memory-trustworthiness pilot study (Yan et al. 2025),
*Machine Learning Engineering in Action* (Manning), *The Data Warehouse Toolkit* (Kimball).

## Conventions

- Cite in guides by title + publisher (books) or arXiv ID/venue (papers).
- New material: drop into the matching pillar folder and add a row here.
- Committing binaries is Ramsey's decision per folder (policy decision 2026-07-17:
  library is committed).
