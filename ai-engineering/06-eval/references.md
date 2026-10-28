# References — Eval Engineering

> Papers and further reading, mapped to chapters. **★** = read first. Local PDFs live in [readings/general/](../readings/general/).

---

## Practitioner guides

| | Source | Chapters |
|---|---|---|
| ★ | Anthropic, [*Demystifying evals for AI agents*](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): tasks, trials, graders, pass@k vs. pass^k, capability vs. regression, the two-expert test | 01, 02, 04, 06, 12 |
| ★ | Hamel Husain & Shreya Shankar, [*A field guide to rapidly improving AI products*](https://hamel.dev/blog/posts/field-guide/): error analysis, open/axial coding, the benevolent dictator | 02, 03 |
| ★ | Bojie Li, *AI Agents in Depth* (2026), [ch. 6 Evaluating Agents](https://github.com/bojieli/ai-agent-book) (Apache-2.0). Folded into [03](notes/03-eval-datasets.md#contamination-how-public-benchmarks-fight-it) (contamination, SWE-bench Verified QC, GAIA levels), [04](notes/04-graders.md#veto-items) (veto rubrics), [05](notes/05-llm-as-judge.md#pairwise-ranking-elo-and-bradleyterry) (multi-family judges, Elo), [06](notes/06-evaluating-agents.md#multi-turn-evaluation) (progressive disclosure, τ²-bench, Best@k, cost growth, budget curves), [09](notes/09-reading-results.md#from-a-benchmark-report-to-hypotheses) (multiple comparisons, report → hypotheses) and [11](notes/11-production-and-the-maturity-ladder.md#eval-infrastructure-inside-the-product) (ablation, feature flags, eval → RL environments). Lab 6-6 is in [practice/02-elo-leaderboard](practice/02-elo-leaderboard/README.md). Other labs upstream: [6-5 TTS judge](https://github.com/bojieli/ai-agent-book/tree/main/chapter6/tts-quality-eval) · [6-7 cost breakdown](https://github.com/bojieli/ai-agent-book/tree/main/chapter6/agent-cost-analysis) · [6-8 provider benchmark](https://github.com/bojieli/ai-agent-book/tree/main/chapter6/model-benchmark) · [6-10 AndroidWorld report](https://github.com/bojieli/ai-agent-book/tree/main/chapter6/android-world) · [public-health eval](https://github.com/bojieli/ai-agent-book/tree/main/chapter6/public-health-reporting-eval) | 01–12 |
| ★ | Hamel Husain, [*Using LLM-as-a-judge*](https://hamel.dev/blog/posts/llm-judge/): binary judges, critique-then-verdict, calibrating against a domain expert | 05 |
| | OpenAI Cookbook, [*Realtime eval guide*](https://developers.openai.com/cookbook/examples/realtime_eval_guide): regression suite + rolling discovery set | 03, 11 |
| | LangChain, [*Trajectory evals*](https://docs.langchain.com/langsmith/trajectory-evals) and [*Agent evaluation readiness checklist*](https://www.langchain.com/blog/agent-evaluation-readiness-checklist): trajectory matching; rule out infra first | 06, 12 |
| | AI Builder Club, [*How to evaluate AI agents*](https://www.aibuilderclub.com/blog/how-to-evaluate-ai-agents): the maturity ladder, layered graders, cost per success | 04, 11 |
| | Nick Talwar, [*6 things your AI agents need*](https://nicktalwar.substack.com/p/6-things-your-ai-agents-need-that): evals, fallback, drift, HITL, audit logs, handoffs | 11 |
| | Berryman & Ziegler, *Prompt Engineering for LLMs* (O'Reilly 2024), Ch. 10: offline/online evaluation, SOMA judges | 01, 04, 05 |
| | DeepLearning.AI, [*Evaluating AI Agents*](https://www.deeplearning.ai/short-courses/evaluating-ai-agents/) (Arize): router, skill and trajectory evals in Phoenix. Notebooks: [Evaluating-AI-Agents-master/](notebooks/evaluating-ai-agents/) | 06, 08, practice |

---

## Papers

### Judges and graders

| | Paper | arXiv | Chapters |
|---|---|---|---|
| ★ | Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* (2023): position, verbosity, self-preference biases; judges reach human–human agreement | [2306.05685](https://arxiv.org/abs/2306.05685) | 05 |
| | Liu et al., *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment* (2023): judge-generated evaluation steps | [2303.16634](https://arxiv.org/abs/2303.16634) | 05 |
| ★ | Shankar et al., *Who Validates the Validators? Aligning LLM-Assisted Evaluation with Human Preferences* (2024): criteria drift | [2404.12272](https://arxiv.org/abs/2404.12272) | 02, 05 |
| | Guo et al., *On Calibration of Modern Neural Networks* (2017): confidence calibration background. [PDF](../readings/general/1706.04599v2.pdf) | [1706.04599](https://arxiv.org/abs/1706.04599) | 05 |

### Agents

| | Paper | arXiv | Chapters |
|---|---|---|---|
| | Chen et al., *Evaluating Large Language Models Trained on Code* (Codex, 2021): the unbiased pass@k estimator | [2107.03374](https://arxiv.org/abs/2107.03374) | 06 |
| ★ | Yao et al., *τ-bench: A Benchmark for Tool-Agent-User Interaction* (2024): pass^k, simulated users, policy-following | [2406.12045](https://arxiv.org/abs/2406.12045) | 06 |

### RAG and grounding

| | Paper | arXiv | Chapters |
|---|---|---|---|
| ★ | Es et al., *RAGAS: Automated Evaluation of Retrieval Augmented Generation* (2023). [PDF](../readings/general/ragas_automated_evaluation.pdf) | [2309.15217](https://arxiv.org/abs/2309.15217) | 07 |
| | Saad-Falcon et al., *ARES: An Automated Evaluation Framework for RAG Systems* (2023) | [2311.09476](https://arxiv.org/abs/2311.09476) | 07 |
| | Gao et al., *Enabling Large Language Models to Generate Text with Citations* (ALCE, 2023): citation precision/recall | [2305.14627](https://arxiv.org/abs/2305.14627) | 07 |
| | Manakul et al., *SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection* (2023). [PDF](../readings/general/2303.08896v3.pdf) | [2303.08896](https://arxiv.org/abs/2303.08896) | 07 |
| | Lin et al., *TruthfulQA: Measuring How Models Mimic Human Falsehoods* (2021). [PDF](../readings/general/truthfulQA_how_models_mimic_human_falsehoods.pdf) | [2109.07958](https://arxiv.org/abs/2109.07958) | 07 |
| | Shuster et al., *Retrieval Augmentation Reduces Hallucination in Conversation* (EMNLP Findings 2021). [PDF](../readings/general/2021.findings-emnlp.320.pdf) | [2104.07567](https://arxiv.org/abs/2104.07567) | 07 |

### Statistics and metrics

| | Paper | Link | Chapters |
|---|---|---|---|
| ★ | Miller, *Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations* (Anthropic, 2024): CLT error bars, clustered SEs, paired differences | [2411.00640](https://arxiv.org/abs/2411.00640) | 09 |
| ★ | Dmitriev et al., *A Dirty Dozen: Twelve Common Metric Interpretation Pitfalls in Online Controlled Experiments* (KDD 2017). [PDF](../readings/general/2017-08%20KDDMetricInterpretationPitfalls.pdf) | — | 09, 11 |

### Systems and practice

| | Paper | Link | Chapters |
|---|---|---|---|
| | Sculley et al., *Hidden Technical Debt in Machine Learning Systems* (NeurIPS 2015). [PDF](../readings/general/NIPS-2015-hidden-technical-debt-in-machine-learning-systems-Paper.pdf) | — | 12 |
| | Amershi et al., *Software Engineering for Machine Learning: A Case Study* (ICSE-SEIP 2019). [PDF](../readings/general/amershi-icse-2019_Software_Engineering_for_Machine_Learning.pdf) | — | 10, 12 |
| | Gao et al., *Learning towards Conversational AI: A Survey* (2022). [PDF](../readings/general/conversational-ai.pdf), [longer version](../readings/general/conversational-ai-longer-version.pdf) | — | 06 |

---

## Standards and tools

| Tool | Link | Chapters |
|---|---|---|
| OpenTelemetry GenAI semantic conventions | [opentelemetry.io/docs/specs/semconv/gen-ai](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | 08 |
| Arize Phoenix | [arize.com/docs/phoenix](https://arize.com/docs/phoenix) | 08, practice |
| Langfuse | [langfuse.com/docs](https://langfuse.com/docs) | 08 |
| LangSmith | [docs.langchain.com/langsmith](https://docs.langchain.com/langsmith) | 06, 08 |
| Inspect AI (UK AISI): dataset + solver + scorer | [inspect.aisi.org.uk](https://inspect.aisi.org.uk/) | 01 |
| RAGAS | [docs.ragas.io](https://docs.ragas.io/) | 07 |
| DeepEval | [deepeval.com](https://deepeval.com/) | 05, 07 |

---

## Unsorted

To read and place:
- OpenAI, [*Trustworthy third-party evaluations: foundations*](https://openai.com/index/trustworthy-third-party-evaluations-foundations/)
- [*How to build production-ready AI engineering projects*](https://medium.com/data-science-collective/how-to-build-production-ready-ai-engineering-projects-3142a88f06ea): unit tests per tool, integration tests per workflow, adversarial tests
