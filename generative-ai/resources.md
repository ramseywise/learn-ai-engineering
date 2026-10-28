---
origin: curated
sources:
  - generative-ai/Packages.md (local paste of three upstream lists; merged here and deleted 2026-10-28)
  - https://github.com/aadi1011/AI-ML-Roadmap-from-scratch (Packages.md + roadmap README)
  - https://github.com/owainlewis/awesome-artificial-intelligence (MIT; old and current editions)
cleaned: 2026-10-28
---

# External resources

A curated list of external links, organized by the gen-AI pillars and their ai-engineering
companions. It is built from three awesome-style lists that had been pasted into a single
`Packages.md`. Duplicates were merged. Stale, low-depth or off-topic entries were dropped:
journals, philosophy and Prolog, Instagram and fan sites, link farms, and per-library `pip`
boilerplate. Local PDFs and books already in the repo are listed in each pillar's *Readings*
section, not here.

★ marks the place to start in each section.

## Python and ML toolchain

These are the libraries the notebooks assume. Install per project with `uv`/`pip` from
each project's `pyproject.toml`. Don't install them all at once.

| Area | Libraries |
|---|---|
| Data | [NumPy](https://numpy.org/doc/), [pandas](https://pandas.pydata.org/docs/), [SciPy](https://docs.scipy.org/doc/scipy/), [Matplotlib](https://matplotlib.org/stable/), [seaborn](https://seaborn.pydata.org/) |
| Classical ML | [scikit-learn](https://scikit-learn.org/stable/), [XGBoost](https://xgboost.readthedocs.io/), [LightGBM](https://lightgbm.readthedocs.io/), [CatBoost](https://catboost.ai/docs/) |
| Deep learning | [PyTorch](https://pytorch.org/docs/), [TensorFlow](https://www.tensorflow.org/learn) / [Keras](https://keras.io/) |
| Vision | [OpenCV](https://docs.opencv.org/), [scikit-image](https://scikit-image.org/docs/stable/), [Pillow](https://pillow.readthedocs.io/) |

## Foundations (math, Python, classical ML)

- [MIT 18.06 Linear Algebra](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/) — Strang's lectures.
- [CS50's Introduction to Programming with Python](https://www.edx.org/learn/python/harvard-university-cs50-s-introduction-to-programming-with-python); practice on [HackerRank Python](https://www.hackerrank.com/domains/python) (see [`programming/`](../programming/README.md)).
- [Machine Learning Specialization (Andrew Ng)](https://www.coursera.org/specializations/machine-learning-introduction) — the course behind [`data-science/`](../data-science/README.md)'s Ng notebooks.
- [CS50's Introduction to AI](https://cs50.harvard.edu/ai/) and [AIMA](https://aima.cs.berkeley.edu/) — classical AI: search, reasoning, planning.
- [Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/) (Huyen) and [Made With ML](https://madewithml.com/) — production ML.

## 01 — LLM fundamentals → [pillar](01-llm-fundamentals/README.md)

**Courses**
- ★ [Karpathy, Neural Networks: Zero to Hero](https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ). Code is in [`01-llm-fundamentals/nn-zero-to-hero/`](01-llm-fundamentals/).
- [Stanford CS336: Language Modeling from Scratch](https://cs336.stanford.edu/)
- [Hugging Face LLM Course](https://huggingface.co/learn/llm-course/chapter1/1)
- [fast.ai Practical Deep Learning](https://course.fast.ai/) · [MIT 6.S191](https://introtodeeplearning.com/) · [Full Stack Deep Learning](https://fullstackdeeplearning.com/)
- [DeepLearning.AI Neural Networks and Deep Learning](https://www.coursera.org/learn/neural-networks-deep-learning) · [DeepLearning.AI short courses](https://learn.deeplearning.ai/)
- [Google Generative AI learning path](https://www.cloudskillsboost.google/paths/118)
- [TensorFlow NLP Zero to Hero](https://youtube.com/playlist?list=PLQY2H8rRoyvzDbLUZkbudP-MFQZwNmU4S). Pairs with `intro-to-nlp/`.

**Books**
- ★ [Hands-On Large Language Models](https://www.llm-book.com/) (Alammar & Grootendorst)
- [Build a Large Language Model from Scratch](https://www.manning.com/books/build-a-large-language-model-from-scratch) (Raschka)
- [The 100-Page Language Models Book](https://www.thelmbook.com/) (Burkov)
- [Understanding Deep Learning](https://udlbook.github.io/udlbook/) (Prince) · [Deep Learning: Foundations and Concepts](https://www.bishopbook.com/) (Bishop) · [Deep Learning](https://www.deeplearningbook.org/) (Goodfellow et al.)
- [Speech and Language Processing](https://web.stanford.edu/~jurafsky/slp3/) (Jurafsky & Martin)
- [LLM Engineer's Handbook](https://www.packtpub.com/en-us/product/llm-engineers-handbook-9781836200079) — LLMOps, fine-tuning, serving

**Foundational papers.** These are the canon. A ✓ means the PDF is already in [`01-llm-fundamentals/readings/`](01-llm-fundamentals/readings/).
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) · [Scaling Laws](https://arxiv.org/abs/2001.08361) · [Chinchilla](https://arxiv.org/abs/2203.15556) · [GPT-3 / few-shot](https://arxiv.org/abs/2005.14165)
- [LoRA](https://arxiv.org/abs/2106.09685) ✓ · [InstructGPT](https://arxiv.org/abs/2203.02155) · [Constitutional AI](https://arxiv.org/abs/2212.08073) ✓ · [DPO](https://arxiv.org/abs/2305.18290)

## 02 — RAG & retrieval → [pillar](02-rag-retrieval/README.md)

- ★ [RAG from Scratch (LangChain)](https://www.youtube.com/watch?v=sVcwVQRHIc8) — a video series that goes past the DeepLearning.AI course in this pillar.
- [Retrieval-Augmented Generation (Lewis et al.)](https://arxiv.org/abs/2005.11401) — the original paper.
- [LlamaIndex](https://docs.llamaindex.ai/) · [Haystack](https://docs.haystack.deepset.ai/) — retrieval pipelines.
- [Docling](https://github.com/docling-project/docling) — document parsing before you chunk.
- *AI Agents in Depth* ch. 3 ([upstream](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter3.md)): contextual retrieval, agentic RAG and memory, synthesised into [04-retrieval](../ai-engineering/02-context-engineering/notes/04-retrieval.md) and [06-memory](../ai-engineering/02-context-engineering/notes/06-memory.md) with labs linked upstream.

## 03/04 — Agents and frameworks → [03](03-agentic-foundations/README.md) · [04](04-agentic-frameworks/README.md)

**Guides**
- ★ [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic)
- [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) (OpenAI)
- [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)
- [ReAct](https://arxiv.org/abs/2210.03629) — the reason + act paper.

**Frameworks**
- [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) · [Google ADK](https://google.github.io/adk-docs/) — both covered in pillar 04.
- [Pydantic AI](https://ai.pydantic.dev/) · [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) · [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/) (AutoGen's successor)

**Durable and long-running agents.** These go deeper in [ai-engineering/03-harness](../ai-engineering/03-harness-engineering/README.md).
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- OpenAI Agents SDK: [running agents](https://openai.github.io/openai-agents-python/running_agents/) · [human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/)
- [Gemini + Temporal durable agent](https://ai.google.dev/gemini-api/docs/temporal-example)
- [How We Built Our Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) (Anthropic)

## 05 — RL & alignment → [pillar](05-RL/README.md)

- ★ [Sutton & Barto, *Reinforcement Learning: An Introduction*](http://incompleteideas.net/book/the-book-2nd.html)
- [Hugging Face Deep RL Course](https://huggingface.co/learn/deep-rl-course/en/unit0/introduction)
- [OpenAI Spinning Up](https://spinningup.openai.com/)
- *AI Agents in Depth* ch. 7–8 ([upstream](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter7.md)): synthesised into [post-training-for-agents.md](05-RL/post-training-for-agents.md), with labs linked upstream.

## 06 — Observability and evals → [pillar](06-observability/README.md) · [ai-engineering/06-eval](../ai-engineering/06-eval/README.md)

- ★ [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (Anthropic)
- [Langfuse docs](https://langfuse.com/docs) — the tool this pillar's three course repos use.
- [Promptfoo](https://www.promptfoo.dev/docs/) · [Ragas](https://docs.ragas.io/) · [OpenAI Evals](https://github.com/openai/evals)
- Serving: [vLLM](https://docs.vllm.ai/) · [LiteLLM](https://docs.litellm.ai/)
- Security: [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)

## Prompting → [ai-engineering/01-prompt](../ai-engineering/01-prompt-engineering/README.md)

- [Anthropic prompt engineering docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) · [OpenAI Cookbook](https://cookbook.openai.com/)

## 07 — Applications and coding agents → [pillar](07-agentic-applications/README.md)

- Coding agents: [Claude Code](https://code.claude.com/) · [Codex CLI](https://github.com/openai/codex) · [Gemini CLI](https://github.com/google-gemini/gemini-cli) · [Aider](https://aider.chat/) · [OpenHands](https://docs.all-hands.dev/) · [Cline](https://github.com/cline/cline)
- Benchmarks: [SWE-bench](https://www.swebench.com/) · [Terminal-Bench](https://www.tbench.ai/)
- [Harness Engineering (OpenAI)](https://openai.com/index/harness-engineering/) — a field report on software built by agents.
- Speech: [FunASR](https://github.com/modelscope/FunASR). It fills the voice gap noted for *AI Agents in Depth* ch. 9.
- Project idea bank: [500 AI/ML/DL/CV/NLP projects with code](https://github.com/ashishpatel26/500-AI-Machine-learning-Deep-learning-Computer-vision-NLP-Projects-with-code)

## Staying current

- Papers: the [AI Papers of the Week](../ai-engineering/02-context-engineering/references.md) flow (`/papers` skill) · [Distill](https://distill.pub/) (archive)
- Newsletters: [TLDR AI](https://tldr.tech/ai) · [The Rundown AI](https://www.therundown.ai/)
