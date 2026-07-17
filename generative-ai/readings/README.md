# Readings Library (local-only index)

Primary-source tier of the [interviewing KB](../../interviewing/README.md). The PDFs in this
folder are **not committed** (copyrighted books/chapters and paper mirrors — see `.gitignore`);
this index is the committed record of what the library contains. Papers are listed by arXiv ID
where that is the filename — resolve at `https://arxiv.org/abs/<id>`.

## Topic folders (numbered = suggested study order)

| Folder | Contents | Feeds |
|---|---|---|
| `0.rag/` | Core RAG papers: RAG (2005.11401), Self-RAG (2310.11511), RAGAS (2309.15217), RAG survey (2312.10997), retrieval eval (SIGIR '24) + `new/` follow-ups | rag guide |
| `1.prompt engineering/` | *Prompt Engineering for Generative AI* (O'Reilly, chapters) + CoT (2201.11903), Constitutional AI (2212.08073), LLaMA (2302.13971), GPT-4 (2303.08774), Gorilla (2305.15334), ToolLLM (2307.16789), generative agents (2304.03442) | llm-fundamentals, agents guides |
| `2.knowledge graphs/` | *Knowledge Graphs and LLMs in Action* (Manning, chapters incl. KG-RAG, GNNs, LangGraph QA agent) + word2vec (1301.3781), interpretability/calibration papers | rag + agents guides (KG-RAG section) |
| `3.reinforcement_learning/` | *Reinforcement Learning* (book chapters) + DQN (1312.5602), PPO (1707.06347), RLHF preferences (1706.03741), InstructGPT (2203.02155) | llm-fundamentals guide (RLHF section), future RL notes |
| `ai_engineering/` | Chapter collections by theme: ai design (*Generative AI Design Patterns*), ai engineer, ai performance, agent applications, building agents, langchain, llm-from-scratch, llm handbook, mcp, multi-agent context | agents, context-engineering-cost, system-design guides |
| `data mesh/` | Data mesh / warehouse topology handouts (DM topologies, MDW) | data-engineering-mlops guide |
| `general/` | Classic-paper canon: attention (1706.03762), BERT (1810.04805), InstructGPT (2203.02155), Constitutional AI, ReAct, Tree-of-Thoughts, TruthfulQA, hidden technical debt (NIPS 2015), SE-for-ML (ICSE 2019), human-AI interaction guidelines; `evaluation/` sub-collection | llm-fundamentals, evals-observability, ml-foundations guides |
| `stats_recs/` | Stats bookshelf: ISLR (Python), Practical Statistics for Data Scientists, Statistics Done Wrong, Think Stats/Bayes, Statistical Rethinking, Computer Age Statistical Inference, Storytelling with Data | future stats/experimentation guide (deferred milestone) |

## Loose classics (root)

attention-is-all-you-need, wavenet, batch-normalization (+ rethinking), Bengio neural LM,
conversational-ai, Rasa dialogue transformers / dual-intent-entity, ALiBi (2108.12409),
agentic architectural patterns, memory-trustworthiness pilot study (Yan et al. 2025),
*Machine Learning Engineering in Action* (Manning), *The Data Warehouse Toolkit* (Kimball).

## Conventions

- Books/chapters: keep local, never commit; cite by title + publisher in guides.
- Papers: cite by arXiv ID or venue; prefer linking the abstract page in guides.
- New material: drop into the matching topic folder and add a row here.
