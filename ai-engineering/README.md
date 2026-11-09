# AI Engineering

> Engineer LLM systems that remain useful under real context limits, unreliable tools, long-running work, cost constraints, multimodal inputs, and adversarial pressure.
>
> **Depth domain.** This folder goes deep on the five foundations of AI engineering, and on the disciplines beneath and across them. Eval, which measures all of them, is the [Eval pillar in generative-ai](../generative-ai/08-eval/README.md).

## Builds on

| Chapter | Why |
|---|---|
| [GA 01 LLM fundamentals](../generative-ai/01-llm-fundamentals/README.md) | The model: tokens, attention and what a prompt becomes |
| [DS 02 Deep learning](../data-science/02-deep-learning/README.md) | Training, and what a forward pass costs |
| [DA 02 Probability and statistics](../data-analytics/02-probability-and-statistics/README.md) | Intervals and tests behind every measurement here |
| [DA 03 Experimentation and causality](../data-analytics/03-experimentation-and-causality/README.md) | Prompt A against prompt B is an A/B test, with the same sample-size arithmetic |

## The five peer foundations

```
prompt → context → harness → loop → graph
```

The order is not a matter of taste: it encodes a nesting rule.

- **Harness** implements loops.
- Each **loop** step assembles **context**.
- Each assembled **context** contains **prompts**.
- **Graph** builds on loops: graphs make multi-agent organizations programmable the way loops make individual agent behavior programmable.

All five are peer foundations. Graph is ordered fifth (after loop) because it *presumes loop mastery*, but it is a first-class discipline, not a frontier add-on.

**Measuring all five: [Eval](../generative-ai/08-eval/README.md)**, in generative-ai. It grades
prompt quality, context composition, harness reliability, loop behavior and graph correctness.
Each pillar here keeps its own chapter on what to measure; the Eval pillar owns the shared machinery.

**Underneath all five: [inference](07-inference-engineering/README.md)** (added 2026-10-31).
Serving, KV cache, batching and GPU performance decide what every call above costs in
latency and money. It is read after the five, not because it sits on top. Number 06 is unused here: Eval
moved to generative-ai, and the folders were not renumbered.

**Across all five: [multimodal](08-multimodal-engineering/README.md) and
[safety and security](09-safety-and-security/README.md)** (both added 2026-10-31). Each
changes every layer rather than adding one. Multimodal swaps text for images, documents and
audio at the edges. Safety and security model the attack surface each layer opens. Read them
after the five, in either order.
## Course outcomes

By the end, you can design prompts and context deliberately; build verifiable harnesses; create bounded autonomous loops and multi-agent graphs; reason about inference cost and performance; build multimodal features; and threat-model, test, and respond to unsafe systems.

## Before you begin

**Required:** [Generative AI Unit 01](../generative-ai/01-llm-fundamentals/README.md) and practical Python or TypeScript. [Generative AI Unit 08](../generative-ai/08-eval/README.md) is a strong companion for measurement. Data Analytics helps with experiments and metrics.

**Learning model:** take Units 01 to 05 in order. Unit 07 is the serving substrate; Units 08 and 09 are cross-cuts to use whenever the system has non-text inputs or meaningful risk. Study notes, review decks, complete side-by-side Python/TypeScript labs when present, and retain mastery evidence.

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

## Units

### [01 Prompt engineering](01-prompt-engineering/README.md)

**Objectives:** turn a task into instructions, examples, structure, and constraints (Berryman and Ziegler); diagnose prompt failures from each note's Pitfalls and the [tool-call debugging table](01-prompt-engineering/notes/05-tools-and-function-calling.md#debugging-tool-calls); compare prompt variants with an evaluation set (Huyen, ch. 5); account for adversarial prompting.

**Learning:** [chapters, deck, and practice](01-prompt-engineering/README.md). **Evidence:** a versioned prompt with task cases, pass criteria, and observed failure modes.

### [02 Context engineering](02-context-engineering/README.md)

**Objectives:** model a context window as a budget ([Mei et al.](https://arxiv.org/abs/2507.13334)); select, compress, retrieve, and order information; preserve state across sessions; test context quality rather than assuming more is better ([Chroma, *Context Rot*](https://research.trychroma.com/context-rot)).

**Learning:** [chapters, deck, and practice](02-context-engineering/README.md). **Evidence:** a context budgeter or design showing inclusion rules, truncation policy, measurements, and failure cases.

### [03 Harness engineering](03-harness-engineering/README.md)

**Objectives:** build a system around a model with tool boundaries, state, verification, retries, scope, and an auditable definition of done ([Anthropic, *Effective harnesses*](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents); [OpenAI, *Harness engineering*](https://openai.com/index/harness-engineering/)).

**Learning:** [chapters, deck, and practice](03-harness-engineering/README.md). **Evidence:** a harness with a task contract, independent checks, recorded state, and a safe stop path.

### [04 Loop engineering](04-loop-engineering/README.md)

**Objectives:** design goal-plus-scorekeeper cycles; select stop conditions and autonomy (Albada); externalise state (Oshin and Campos); handle long-running execution; identify loop failure modes.

**Learning:** [chapters, deck, and paired labs](04-loop-engineering/README.md). **Evidence:** a Python or TypeScript loop that runs offline, records iterations, uses an independent scorekeeper, and ends with an explicit reason.

### [05 Graph engineering](05-graph-engineering/README.md)

**Objectives:** choose a graph only when structure is earned ([Anthropic, *Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents)); design routing, fan-out, reducers, retries, approvals, checkpoints, and knowledge-graph integration (Negro et al.); distinguish agent graphs from knowledge graphs.

**Learning:** [chapters, deck, and paired labs](05-graph-engineering/README.md). **Evidence:** a graph design or implementation with state schema, transition rules, failure handling, and a justification for every added node.

### [07 Inference engineering](07-inference-engineering/README.md)

**Objectives:** relate latency, throughput, and cost to hardware, batching, KV cache, prefill/decode, kernels, compilers, serving, and adaptive inference (Fregly; Huyen, ch. 9).

**Learning:** [chapters and practice](07-inference-engineering/README.md). **Evidence:** a profiling or serving proposal that names the bottleneck, expected trade-off, metric, and rollback criterion.

### [08 Multimodal engineering](08-multimodal-engineering/README.md)

**Objectives:** design image/document input, multimodal retrieval, voice, image/video generation (Phoenix and Taylor, ch. 7 and 9), and multimodal evaluation with explicit quality, latency, and provenance constraints.

**Learning:** [chapters and references](08-multimodal-engineering/README.md). **Evidence:** a modality feature specification or prototype with an input-quality check, budget, evaluation set, and fallback.

### [09 Safety and security](09-safety-and-security/README.md)

**Objectives:** threat-model an LLM system ([OWASP Top 10 for LLM](https://genai.owasp.org/llm-top-10/)); resist prompt injection and unsafe tool use ([Debenedetti et al.](https://arxiv.org/abs/2503.18813)); select guardrails and sandboxes; red-team systems; protect data and supply chain; prepare an incident response.

**Learning:** [chapters and references](09-safety-and-security/README.md). **Evidence:** a threat model, one red-team test, layered mitigation plan, and incident response path.

## Labs

Decision (2026-11-01): **labs in both TypeScript and Python.** Each of pillars 01 to 05 and 07, and the Eval pillar in generative-ai, has one lab in
`practice/`, in both languages side by side on the same inputs, so you can compare them. Every lab
runs offline with a stub model by default, and each README says how to swap in a real model.

| Pillar | Lab | TypeScript | Python |
|---|---|---|---|
| 01 prompt | Prompt eval harness | [prompt-eval-harness](01-prompt-engineering/practice/prompt-eval-harness/README.md) | [prompt-eval-harness-py](01-prompt-engineering/practice/prompt-eval-harness-py/README.md) |
| 02 context | Context budgeter | [context-budgeter](02-context-engineering/practice/context-budgeter/README.md) | [context-budgeter-py](02-context-engineering/practice/context-budgeter-py/README.md) |
| 03 harness | Tool server with sandboxing | [tool-server-sandbox](03-harness-engineering/practice/tool-server-sandbox/README.md) | [tool-server-sandbox-py](03-harness-engineering/practice/tool-server-sandbox-py/README.md) |
| 04 loop | Loop with a scorekeeper | [loop-scorekeeper](04-loop-engineering/practice/loop-scorekeeper/README.md) | [loop-scorekeeper-py](04-loop-engineering/practice/loop-scorekeeper-py/README.md) |
| 05 graph | LangGraph graph | [langgraph-graph-ts](05-graph-engineering/practice/langgraph-graph-ts/README.md) | [langgraph-graph](05-graph-engineering/practice/langgraph-graph/README.md) |
| Eval (generative-ai/08) | Eval suite in CI | [eval-suite-ci](../generative-ai/08-eval/practice/eval-suite-ci/README.md) | [eval-suite-ci-py](../generative-ai/08-eval/practice/eval-suite-ci-py/README.md) |
| 07 inference | Inference simulator | [inference-lab-ts](07-inference-engineering/practice/inference-lab-ts/README.md) | [inference-lab](07-inference-engineering/practice/inference-lab/README.md) |

## Completion standard and next steps

Complete a portfolio containing a measured prompt/context design, tested harness, bounded loop or graph, inference trade-off analysis, and a threat model with red-team evidence. Each item must identify the task, operator control, verification method, cost or latency budget, failure mode, and stop/rollback condition.

For model fundamentals and application patterns, return to [Generative AI](../generative-ai/README.md); for data and evaluation foundations, use [Data Analytics](../data-analytics/README.md) and [Data Science](../data-science/README.md).

## Primary texts

- Berryman and Ziegler, *Prompt Engineering for LLMs*: the backbone of Unit 01
- Huyen, *AI Engineering*: Units 01 and 07
- Stratis, *AI Agents with MCP*: Unit 02
- Albada, *Building Applications with AI Agents*: Units 03 and 04
- Negro et al., *Knowledge Graphs and LLMs in Action*: Unit 05
- Fregly, *AI Systems Performance Engineering*: Unit 07
- Debenedetti et al., *Defeating Prompt Injections by Design*: Unit 09
- Wilson and Yen, *The Developer's Playbook for Large Language Model Security*: recommended for Unit 09; not in the repo, and the notes do not rely on it

Everything else: each pillar's own `references.md`.
