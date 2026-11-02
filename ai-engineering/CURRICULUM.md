# AI engineering: course curriculum

> Engineer LLM systems that remain useful under real context limits, unreliable tools, long-running work, cost constraints, multimodal inputs, and adversarial pressure.

This syllabus covers the production-engineering layer around generative models. Pillar READMEs are the chapter-level teaching surface: they provide note order, decks, labs, run instructions, and complete references.

## Course outcomes

By the end, you can design prompts and context deliberately; build verifiable harnesses; create bounded autonomous loops and multi-agent graphs; reason about inference cost and performance; build multimodal features; and threat-model, test, and respond to unsafe systems.

## Before you begin

**Required:** [Generative AI Unit 01](../generative-ai/01-llm-fundamentals/README.md) and practical Python or TypeScript. [Generative AI Unit 08](../generative-ai/08-eval/README.md) is a strong companion for measurement. Data Analytics helps with experiments and metrics.

**Learning model:** take Units 01–05 in order. Unit 07 is the serving substrate; Units 08–09 are cross-cuts to use whenever the system has non-text inputs or meaningful risk. Study notes, review decks, complete side-by-side Python/TypeScript labs when present, and retain mastery evidence.

## Course map

| Unit | Focus | Mastery evidence |
|---|---|---|
| [01 Prompt engineering](01-prompt-engineering/README.md) | Instructions, decomposition, prompt evaluation | Versioned prompt and evaluation result |
| [02 Context engineering](02-context-engineering/README.md) | Context as a constrained system | Context budget and retrieval decision |
| [03 Harness engineering](03-harness-engineering/README.md) | Verification, tools, state, scope | Tested agent harness |
| [04 Loop engineering](04-loop-engineering/README.md) | Goal, scorekeeper, stopping | Offline loop with independent verifier |
| [05 Graph engineering](05-graph-engineering/README.md) | Multi-agent topology and state | Graph with routing, recovery, and checkpoints |
| [07 Inference engineering](07-inference-engineering/README.md) | Latency, throughput, cost | Measured serving optimisation proposal |
| [08 Multimodal engineering](08-multimodal-engineering/README.md) | Image, document, speech, generation | Modal feature with quality/cost evaluation |
| [09 Safety and security](09-safety-and-security/README.md) | Threats, guardrails, response | Threat model and mitigated red-team finding |

## Unit syllabus

### 01 — Prompt engineering
**Objectives:** turn a task into instructions, examples, structure, and constraints; diagnose prompt failures; compare prompt variants with an evaluation set; account for adversarial prompting. **Learning:** [chapters, deck, and practice](01-prompt-engineering/README.md). **Evidence:** a versioned prompt with task cases, pass criteria, and observed failure modes. **Key sources:** [pillar references](01-prompt-engineering/references.md).

### 02 — Context engineering
**Objectives:** model a context window as a budget; select, compress, retrieve, and order information; preserve state across sessions; test context quality rather than assuming more is better. **Learning:** [chapters, deck, and practice](02-context-engineering/README.md). **Evidence:** a context budgeter or design showing inclusion rules, truncation policy, measurements, and failure cases. **Key sources:** [pillar references](02-context-engineering/references.md).

### 03 — Harness engineering
**Objectives:** build a system around a model with tool boundaries, state, verification, retries, scope, and an auditable definition of done. **Learning:** [chapters, deck, and practice](03-harness-engineering/README.md). **Evidence:** a harness with a task contract, independent checks, recorded state, and a safe stop path. **Key sources:** [pillar references](03-harness-engineering/references.md).

### 04 — Loop engineering
**Objectives:** design goal-plus-scorekeeper cycles; select stop conditions and autonomy; externalise state; handle long-running execution; identify loop failure modes. **Learning:** [chapters, deck, and paired labs](04-loop-engineering/README.md). **Evidence:** a Python or TypeScript loop that runs offline, records iterations, uses an independent scorekeeper, and ends with an explicit reason. **Key sources:** [pillar references](04-loop-engineering/references.md).

### 05 — Graph engineering
**Objectives:** choose a graph only when structure is earned; design routing, fan-out, reducers, retries, approvals, checkpoints, and knowledge-graph integration; distinguish agent graphs from knowledge graphs. **Learning:** [chapters, deck, and paired labs](05-graph-engineering/README.md). **Evidence:** a graph design or implementation with state schema, transition rules, failure handling, and a justification for every added node. **Key sources:** [pillar references](05-graph-engineering/references.md).

### 07 — Inference engineering
**Objectives:** relate latency, throughput, and cost to hardware, batching, KV cache, prefill/decode, kernels, compilers, serving, and adaptive inference. **Learning:** [chapters and practice](07-inference-engineering/README.md). **Evidence:** a profiling or serving proposal that names the bottleneck, expected trade-off, metric, and rollback criterion. **Key sources:** [pillar references](07-inference-engineering/references.md).

### 08 — Multimodal engineering
**Objectives:** design image/document input, multimodal retrieval, voice, image/video generation, and multimodal evaluation with explicit quality, latency, and provenance constraints. **Learning:** [chapters and references](08-multimodal-engineering/README.md). **Evidence:** a modality feature specification or prototype with an input-quality check, budget, evaluation set, and fallback. **Key sources:** [pillar references](08-multimodal-engineering/references.md).

### 09 — Safety and security
**Objectives:** threat-model an LLM system; resist prompt injection and unsafe tool use; select guardrails and sandboxes; red-team systems; protect data and supply chain; prepare an incident response. **Learning:** [chapters and references](09-safety-and-security/README.md). **Evidence:** a threat model, one red-team test, layered mitigation plan, and incident response path. **Key sources:** OWASP LLM/Agentic Top 10 and [pillar references](09-safety-and-security/references.md).

## Completion standard and next steps

Complete a portfolio containing a measured prompt/context design, tested harness, bounded loop or graph, inference trade-off analysis, and a threat model with red-team evidence. Each item must identify the task, operator control, verification method, cost or latency budget, failure mode, and stop/rollback condition.

For model fundamentals and application patterns, return to [Generative AI](../generative-ai/README.md); for data and evaluation foundations, use [Data Analytics](../data-analytics/README.md) and [Data Science](../data-science/README.md).
