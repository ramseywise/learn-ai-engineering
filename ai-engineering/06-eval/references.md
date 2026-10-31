# References — Eval Engineering

> Papers and further reading, mapped to chapters. **★** = read first. Local PDFs live in [sources/](sources/), or in the home linked on each row.

---

## Books and courses

| | Source | Notes |
|---|---|---|
| ★ | Chip Huyen, *AI Engineering* (O'Reilly, 2025). Chapter PDFs in [sources/huyen-ai-engineering/](sources/huyen-ai-engineering/). Folded in as: ch. 3 → [04](notes/04-graders.md) (reference-metric limits), [05](notes/05-llm-as-judge.md) (judge identity, scales, biases, Arena caveats), [07](notes/07-evaluating-rag-and-grounding.md), [12](notes/12-failure-modes.md#saturation) (saturation); ch. 4 → [02](notes/02-defining-correct.md) (eval-to-business mapping, rubric examples), [03](notes/03-eval-datasets.md), [04](notes/04-graders.md#multiple-choice-format-is-part-of-the-score) (MCQ format), [05](notes/05-llm-as-judge.md), [07](notes/07-evaluating-rag-and-grounding.md) (SAFE, NLI verifiers, hallucination), [09](notes/09-reading-results.md) (sample size, bootstrap, Simpson's paradox), [12](notes/12-failure-modes.md#contamination) (contamination detection, benchmark correlation, model-update drift); ch. 10 → [08](notes/08-tracing-and-observability.md) (monitoring metrics), [11](notes/11-production-and-the-maturity-ladder.md#implicit-signals-worth-logging) (implicit feedback, FITS complaints, feedback biases, degenerate loops). Ch. 5 is folded into the prompt pillar. Notes cite it as `(*AI Engineering*, ch. N)` | 02, 03, 04, 05, 07, 08, 09, 11, 12 |
| | Michael Albada, *Building Applications with AI Agents* (O'Reilly, 2025). Chapter PDFs in [sources/building-applications-with-ai-agents/](sources/building-applications-with-ai-agents/). Folded in as: ch. 9 → [03](notes/03-eval-datasets.md) (mutation moves), [04](notes/04-graders.md) (contradiction: similarity metrics), [06](notes/06-evaluating-agents.md) (tool recall/precision, contradiction: whole-dict param match), [10](notes/10-evals-in-ci.md); ch. 10 → [08](notes/08-tracing-and-observability.md#what-to-watch-and-when-to-page-someone) (MTTD/MTTR/CFR, alert thresholds), [10](notes/10-evals-in-ci.md) (RACI), [11](notes/11-production-and-the-maturity-ladder.md#online-experiments) (shadow mode, canary, regression traces). Notes cite it as `(*Building Applications with AI Agents*, ch. N)` | 03, 04, 06, 08, 10, 11 |
| | Mayo Oshin & Nuno Campos, *Learning LangChain* (O'Reilly, 2025). Chapter PDFs in [generative-ai/01-llm-fundamentals/sources/learning-langchain/](../../generative-ai/01-llm-fundamentals/sources/learning-langchain/). Folded in as: ch. 10 → [03](notes/03-eval-datasets.md) (starter set size), [04](notes/04-graders.md) (build order), [05](notes/05-llm-as-judge.md) (no 0–10 scales, correction loop), [06](notes/06-evaluating-agents.md) (three trajectory granularities, repetitions), [11](notes/11-production-and-the-maturity-ladder.md#user-feedback-as-signal) (feedback on spans). Notes cite it as `(*Learning LangChain*, ch. 10)` | 03, 04, 05, 06, 11 |
| | Paul Iusztin & Maxime Labonne, *LLM Engineer's Handbook* (Packt, 2024). Chapter PDFs in [generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/](../../generative-ai/01-llm-fundamentals/sources/llm-engineers-handbook/). Folded in as: ch. 7 → [03](notes/03-eval-datasets.md), [04](notes/04-graders.md) (generation over log-likelihood), [05](notes/05-llm-as-judge.md) (contradiction: judge temperature 0.8), [07](notes/07-evaluating-rag-and-grounding.md) (RAGAS and ARES mechanics), [09](notes/09-reading-results.md#a-cautionary-write-up) (TwinLlama table as a cautionary example), [12](notes/12-failure-modes.md#contamination) (+10 MMLU tell). Notes cite it as `(*LLM Engineer's Handbook*, ch. 7)` | 03, 04, 05, 07, 09, 12 |
| | James Phoenix & Mike Taylor, *Prompt Engineering for Generative AI* (O'Reilly, 2024). Home is the prompt pillar ([01-prompt-engineering](../01-prompt-engineering/README.md)). Ch. 3's seeded-error judge check is in [05](notes/05-llm-as-judge.md). Notes cite it as `(*Prompt Engineering for Generative AI*, ch. N)` | 05 |

---

## Practitioner guides

| | Source | Chapters |
|---|---|---|
| ★ | Anthropic, [*Demystifying evals for AI agents*](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): tasks, trials, graders, pass@k vs. pass^k, capability vs. regression, the two-expert test | 01, 02, 04, 06, 12 |
| ★ | Hamel Husain & Shreya Shankar, [*A field guide to rapidly improving AI products*](https://hamel.dev/blog/posts/field-guide/): error analysis, open/axial coding, the benevolent dictator | 02, 03 |
| ★ | Bojie Li, *AI Agents in Depth* (2026), [ch. 7 Evaluating Agents](https://github.com/bojieli/ai-agent-book/tree/main/chapter7) (Apache-2.0). Folded into [03](notes/03-eval-datasets.md#contamination-how-public-benchmarks-fight-it) (contamination, SWE-bench Verified QC, GAIA levels), [04](notes/04-graders.md#veto-items) (veto rubrics), [05](notes/05-llm-as-judge.md#pairwise-ranking-elo-and-bradleyterry) (multi-family judges, Elo), [06](notes/06-evaluating-agents.md#multi-turn-evaluation) (progressive disclosure, τ²-bench, Best@k, cost growth, budget curves), [09](notes/09-reading-results.md#from-a-benchmark-report-to-hypotheses) (multiple comparisons, report → hypotheses) and [11](notes/11-production-and-the-maturity-ladder.md#eval-infrastructure-inside-the-product) (ablation, feature flags, eval → RL environments). Labs upstream (chapter-7 numbering): [7-8 Elo leaderboard](https://github.com/bojieli/ai-agent-book/tree/main/chapter7/elo-leaderboard) (core folded into 05) · [7-5 TTS judge](https://github.com/bojieli/ai-agent-book/tree/main/chapter7/tts-quality-eval) · [7-10 cost breakdown](https://github.com/bojieli/ai-agent-book/tree/main/chapter7/agent-cost-analysis) · [7-11 provider benchmark](https://github.com/bojieli/ai-agent-book/tree/main/chapter7/model-benchmark) · [7-13 AndroidWorld report](https://github.com/bojieli/ai-agent-book/tree/main/chapter7/android-world) · [public-health eval](https://github.com/bojieli/ai-agent-book/tree/main/chapter7/public-health-reporting-eval) | 01–12 |
| ★ | Hamel Husain, [*Using LLM-as-a-judge*](https://hamel.dev/blog/posts/llm-judge/): binary judges, critique-then-verdict, calibrating against a domain expert | 05 |
| | OpenAI Cookbook, [*Realtime eval guide*](https://developers.openai.com/cookbook/examples/realtime_eval_guide): regression suite + rolling discovery set | 03, 11 |
| | LangChain, [*Trajectory evals*](https://docs.langchain.com/langsmith/trajectory-evals) and [*Agent evaluation readiness checklist*](https://www.langchain.com/blog/agent-evaluation-readiness-checklist): trajectory matching; rule out infra first | 06, 12 |
| | AI Builder Club, [*How to evaluate AI agents*](https://www.aibuilderclub.com/blog/how-to-evaluate-ai-agents): the maturity ladder, layered graders, cost per success | 04, 11 |
| | Nick Talwar, [*6 things your AI agents need*](https://nicktalwar.substack.com/p/6-things-your-ai-agents-need-that): evals, fallback, drift, HITL, audit logs, handoffs | 11 |
| | Berryman & Ziegler, *Prompt Engineering for LLMs* (O'Reilly 2024), Ch. 10: offline/online evaluation, SOMA judges | 01, 03, 04, 05 |
| | DeepLearning.AI, [*Evaluating AI Agents*](https://www.deeplearning.ai/short-courses/evaluating-ai-agents/) (Arize): router, skill and trajectory evals in Phoenix. Notebooks: [upstream repo](https://github.com/ginny100/DeepLearning.AI-Evaluating-AI-Agents); code folded into 06, 08, 09 | 06, 08, 09 |

---

## Papers

### Judges and graders

| | Paper | arXiv | Chapters |
|---|---|---|---|
| ★ | Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* (2023): position, verbosity, self-preference biases; judges reach human–human agreement | [2306.05685](https://arxiv.org/abs/2306.05685) | 05 |
| | Liu et al., *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment* (2023): judge-generated evaluation steps | [2303.16634](https://arxiv.org/abs/2303.16634) | 05 |
| ★ | Shankar et al., *Who Validates the Validators? Aligning LLM-Assisted Evaluation with Human Preferences* (2024): criteria drift | [2404.12272](https://arxiv.org/abs/2404.12272) | 02, 05 |
| | Guo et al., *On Calibration of Modern Neural Networks* (2017): confidence calibration background. [PDF](../../data-science/sources/guo-2017-calibration-modern-neural-networks.pdf) | [1706.04599](https://arxiv.org/abs/1706.04599) | 05 |

### Agents

| | Paper | arXiv | Chapters |
|---|---|---|---|
| | Chen et al., *Evaluating Large Language Models Trained on Code* (Codex, 2021): the unbiased pass@k estimator | [2107.03374](https://arxiv.org/abs/2107.03374) | 06 |
| ★ | Yao et al., *τ-bench: A Benchmark for Tool-Agent-User Interaction* (2024): pass^k, simulated users, policy-following | [2406.12045](https://arxiv.org/abs/2406.12045) | 06 |
| | Yang et al., *Terminal-RSI: Recursive Self-Improving Terminal Agents via Recursive Self-Rewrite and Policy-Refine* (2026): partial credit vs. strict verified success (failures took 50% of dense-reward mass), Mean@R vs. pass@R, difficulty-stratified results. [PDF](sources/yang-2026-terminal-rsi.pdf) | [2610.22192](https://arxiv.org/abs/2610.22192) | 06, 09, 12 |

### RAG and grounding

| | Paper | arXiv | Chapters |
|---|---|---|---|
| ★ | Es et al., *RAGAS: Automated Evaluation of Retrieval Augmented Generation* (2023). [PDF](sources/es-2023-ragas.pdf) | [2309.15217](https://arxiv.org/abs/2309.15217) | 07 |
| | Saad-Falcon et al., *ARES: An Automated Evaluation Framework for RAG Systems* (2023) | [2311.09476](https://arxiv.org/abs/2311.09476) | 07 |
| | Gao et al., *Enabling Large Language Models to Generate Text with Citations* (ALCE, 2023): citation precision/recall | [2305.14627](https://arxiv.org/abs/2305.14627) | 07, 13 |
| | Qi et al., *Model Internals-based Answer Attribution for Trustworthy Retrieval-Augmented Generation* (EMNLP 2024): self-generated citations are often unreliable | [2406.13663](https://arxiv.org/abs/2406.13663) | 13 |
| | Chen et al., *Concise and Sufficient Sub-Sentence Citations for RAG* (2025): sub-sentence citations cut verification cost | [2509.20859](https://arxiv.org/abs/2509.20859) | 13 |
| | Manakul et al., *SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection* (2023). [PDF](sources/manakul-2023-selfcheckgpt.pdf) | [2303.08896](https://arxiv.org/abs/2303.08896) | 07 |
| | Lin et al., *TruthfulQA: Measuring How Models Mimic Human Falsehoods* (2021). [PDF](sources/lin-2021-truthfulqa.pdf) | [2109.07958](https://arxiv.org/abs/2109.07958) | 07 |
| | Shuster et al., *Retrieval Augmentation Reduces Hallucination in Conversation* (EMNLP Findings 2021). [PDF](../../generative-ai/02-rag-retrieval/sources/retrieval-augmentation-reduces-hallucination-conversation.pdf) | [2104.07567](https://arxiv.org/abs/2104.07567) | 07 |

### Statistics and metrics

| | Paper | Link | Chapters |
|---|---|---|---|
| ★ | Miller, *Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations* (Anthropic, 2024): CLT error bars, clustered SEs, paired differences | [2411.00640](https://arxiv.org/abs/2411.00640) | 09 |
| ★ | Dmitriev et al., *A Dirty Dozen: Twelve Common Metric Interpretation Pitfalls in Online Controlled Experiments* (KDD 2017). [PDF](../../data-engineering/sources/2017-08-kddmetricinterpretationpitfalls.pdf) | — | 09, 11 |

### Systems and practice

| | Paper | Link | Chapters |
|---|---|---|---|
| | Sculley et al., *Hidden Technical Debt in Machine Learning Systems* (NeurIPS 2015). [PDF](../../data-engineering/sources/hidden-technical-debt-machine-learning-systems.pdf) | — | 12 |
| | Amershi et al., *Software Engineering for Machine Learning: A Case Study* (ICSE-SEIP 2019). [PDF](../../data-engineering/sources/amershi-icse-2019-software-engineering-machine.pdf) | — | 10, 12 |
| | Gao et al., *Learning towards Conversational AI: A Survey* (2022). [PDF](../../generative-ai/07-agentic-applications/sources/learning-towards-conversational-ai-survey-07d04bbf.pdf), [longer version](../../generative-ai/07-agentic-applications/sources/learning-towards-conversational-ai-survey.pdf) | — | 06 |

---

## AI Papers of the Week

Recent papers picked up by the weekly [DAIR](https://github.com/dair-ai/AI-Papers-of-the-Week) sync (`make papers`, then `/papers`). Newest first.

| | Paper | arXiv | Chapters |
|---|---|---|---|
| ★ | Bodhwani et al. (Amazon), *GAUGE: When Not to Trust LLM-as-a-Judge in User-Simulated Evaluation of Task-Oriented Agents* (2026): on τ²-bench and SimulatorArena (25 agents), 57.5% of conversations a blind panel rated satisfied had failed the task, the same as the base failure rate. A judge panel flips the same near-equal pairs (31% error), and persona simulators cut reward 42% against a cooperative user. [PDF](sources/bodhwani-2026-gauge.pdf) | [2609.12191](https://arxiv.org/abs/2609.12191) | [05](notes/05-llm-as-judge.md#the-procedure) · [05](notes/05-llm-as-judge.md#multi-family-judging) · [06](notes/06-evaluating-agents.md#multi-turn-evaluation) |
| ★ | Norman et al. (UC Berkeley), *Reliability without Validity: A Systematic, Large-Scale Evaluation of LLM-as-a-Judge Models* (2026): 21 judges, about 541k judgments. Exact-match agreement overstates κ by 33.8–41.3 points, test–retest near 0.99 coexists with strong position bias, and verbosity bias is below 0.011 for every judge under one pairwise rubric. [PDF](sources/norman-2026-reliability-without-validity.pdf) | [2606.19544](https://arxiv.org/abs/2606.19544) | [05](notes/05-llm-as-judge.md#known-biases) · [05](notes/05-llm-as-judge.md#what-to-measure) |
| | Zhao et al. (Princeton, Tencent AI Lab), *One Token to Fool LLM-as-a-Judge* (2025): reference-based judges pass content-free answers such as `:` or `Thought process:` (GPT-4o up to 35% false positives, open 70B judges 60–90%); fine-tuning on truncated negatives fixes it. [PDF](sources/zhao-2025-one-token-fool-llm-as.pdf) | [2507.08794](https://arxiv.org/abs/2507.08794) | [05](notes/05-llm-as-judge.md#known-biases) |
| | Li et al. (Tsinghua), *LLMs-as-Judges: A Comprehensive Survey on LLM-based Evaluation Methods* (2024): taxonomy of 15 judge biases in four groups, plus methods, applications and meta-evaluation benchmarks. A catalogue with no new experiments. [PDF](sources/li-2024-llms-as-judges.pdf) | [2412.05579](https://arxiv.org/abs/2412.05579) | [05](notes/05-llm-as-judge.md#known-biases) |
| ★ | Kapoor et al. (Princeton), *AI Agents That Matter* (2024): on HumanEval, a simple retry baseline matches the best agent's accuracy, while LATS costs over 50× more for less, so plot accuracy against cost. Most agent benchmarks lack a holdout at the generality they claim, and task order and scoring bugs shift leaderboard numbers. [PDF](sources/kapoor-2024-ai-agents-that-matter.pdf) | [2407.01502](https://arxiv.org/abs/2407.01502) | [06](notes/06-evaluating-agents.md#efficiency-metrics) · [06](notes/06-evaluating-agents.md#environment-hygiene) · [03](notes/03-eval-datasets.md#lessons-from-public-benchmarks) |
| | Ma et al. (HKU, HKUST), *AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents* (NeurIPS 2024 D&B): progress rate over annotated subgoals (Pearson > 0.95 with human raters) separates agents whose success rates are all near zero, and grounding accuracy isolates invalid actions. [PDF](sources/ma-2024-agentboard.pdf) | [2401.13178](https://arxiv.org/abs/2401.13178) | [06](notes/06-evaluating-agents.md#outcome-and-trajectory) |
| | Li et al. (PKU, Beihang), *Leveraging Large Language Models for NLG Evaluation: Advances and Challenges* (2024): taxonomy of LLM-based NLG metrics. Its comparison table puts G-Eval at 0.51 Spearman on SummEval against 0.19 for ROUGE-1, at 200–400× the run time. [PDF](sources/li-2024-leveraging-large-language-models-nlg.pdf) | [2401.07103](https://arxiv.org/abs/2401.07103) | [04](notes/04-graders.md#reference-based-text-metrics) |

---

## Standards and tools

| Tool | Link | Chapters |
|---|---|---|
| OpenTelemetry GenAI semantic conventions | [opentelemetry.io/docs/specs/semconv/gen-ai](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | 08 |
| Arize Phoenix | [arize.com/docs/phoenix](https://arize.com/docs/phoenix) | 08 |
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
