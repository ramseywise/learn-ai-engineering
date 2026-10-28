---
origin: synthesis
sources:
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 9"
  - https://www.promptingguide.ai/techniques/prompt_chaining
  - https://www.promptingguide.ai/agents/ai-workflows-vs-ai-agents
  - https://www.promptingguide.ai/applications/pf
  - https://www.anthropic.com/research/building-effective-agents
confidence: high
cleaned: 2026-10-28
---
# 6 — Chaining and Workflows

> When one prompt can't do the job, split it. This note covers the patterns at the prompt level. Running them as long-lived loops is [04-loop](../../04-loop/README.md), and orchestrating agents is [03-harness/07-orchestration](../../03-harness/notes/07-orchestration.md).

---

## Why split

A single general prompt trades **strength for generality**: it will attempt anything, but it executes multi-step work poorly. The book's example (scrape Shopify stores → invent a plug-in per store → email the owner) degrades predictably as you push one agent at it:

- The system prompt grows until it distracts the model.
- There's no clean way to process work items one at a time.
- When a step fails, a system-prompt instruction is only a suggestion. There's no correction mechanism.

Splitting into steps buys back strength. Each prompt has one job, a short context, and an output you can check. It's also easier to debug, because a bad result traces to one step.

---

## Prompt chaining

The output of one prompt becomes the input of the next. The standard example is **document QA in two steps**:

```
Prompt 1 (extract)
  You are a helpful assistant. Given the document in <document></document>,
  extract the quotes relevant to the question. Output them inside <quotes></quotes>.
  If there are no relevant quotes, respond "No relevant quotes found!"
  <document>{{document}}</document>

Prompt 2 (answer)
  Given the quotes in <quotes></quotes> and the original document, compose an
  answer to the question. Be accurate, helpful, and well-written.
  <quotes>{{quotes}}</quotes>
  <document>{{document}}</document>
```

Each step can be tested and tuned separately, and you can add a third step (strip citations, translate, reformat) without touching the others. XML tags at the hand-off points make the parsing trivial ([04](04-controlling-output.md#structured-output)).

---

## Building a workflow — five steps

1. **Define the goal** — the output or change the workflow should produce.
2. **Specify tasks** — ordered steps, each with its tools, inputs and outputs.
3. **Implement each task in isolation** with defined I/O.
4. **Connect them** and adjust until they work together.
5. **Optimize** for quality, latency and cost.

**I/O contracts matter more than internals.** You can iterate on a step's prompt freely, but changing its input or output schema forces you to rearrange its neighbors.

**First question for every task: does it need an LLM?** Use plain code for scraping and writes, and a small classifier (BERT) for pure classification. LLMs are slow, costly and nondeterministic, so spend them only where they're needed. Mix model sizes too: a cheap model for easy steps, a frontier model for hard ones.

---

## Implementing an LLM task

| Approach | How | Use for |
|---|---|---|
| **Templated prompt** | Fill a template, parse the completion. A prefix and suffix bracket the output (`Dear {name},` … `We hope to hear from you soon,`), so the completion is *exactly* the body | Generation |
| **Forced tool call** | Define a tool whose parameters are the output schema; force it with `tool_choice` | Extraction into structured data |
| **Two-step with scratch work** | Brainstorm with CoT, then a clean step that writes up only the winner | Keeping reasoning out of the stored output |

If extraction fails, check two things. Is the source hard to parse even for a human? Then clean it. Is the target schema too big (many keys, nesting, nullable fields)? Then split it across several calls.

When quality is still short:
- **Force a planning pass.** Disable tool execution for one turn (`tool_choice: "none"`, keeping the tool specs) so the model reasons before acting.
- **Reflexion at the task level.** Check the output with a validator, tests or a judge; on failure, re-prompt with the requirements, the failed attempt and the critique ([03](03-core-techniques.md#reflexion)).
- **Human-in-the-loop** for irreversible actions and for tasks that keep failing.

**Prompt functions** (DAIR) are the chat-UI version of the same idea: define a named function in the prompt (`function_name: trans_word`, `input: …`, `rule: …`), then call it, or chain several, by name. They're useful for personal workflows. In an application, write the function in code.

---

## Topologies

| Topology | Shape | Trade-off |
|---|---|---|
| **Pipeline** | A → B → C | Simplest. Information not passed along is lost downstream, so you get odd couplings |
| **DAG** | Fan-out and fan-in, no cycles | **Default choice.** Each task gets what it needs directly; dependency reasoning stays simple (the Airflow model) |
| **Cyclic** | Loops back on failure | Sometimes needed, but costly: you must carry the failure context back, every task must handle retried items, and you need an attempt cap. **Prefer hiding a retry loop inside a task** |

Run **batch** for a known set of items (simpler) and **streaming** for open-ended arrivals (lower latency, more complex).

---

## Workflow patterns (Anthropic's taxonomy)

| Pattern | What it does | Example |
|---|---|---|
| **Prompt chaining** | Sequential steps, with optional gates between them | Outline → check against criteria → draft |
| **Routing** | Classify the input, then send it to a specialized prompt or model | Support triage: billing / technical / general; small model for easy queries |
| **Parallelization** | *Sectioning* (independent subtasks) or *voting* (same task N times) | Content moderation on several axes at once; self-consistency ([03](03-core-techniques.md#self-consistency)) |
| **Orchestrator–workers** | An LLM splits the task dynamically and delegates | Multi-file code changes |
| **Evaluator–optimizer** | One prompt generates, another critiques, loop | Translation with a critic; Reflexion |

---

## Workflows vs. agents

| | Workflow | Agent |
|---|---|---|
| Control flow | Predefined in code | Chosen by the model |
| Tool use | Orchestrated by code | Selected by the model |
| Predictability | High | Lower |
| Good for | Well-defined, repeatable tasks; production reliability; cost control | Open-ended tasks where the steps can't be known up front |

**Start with a workflow.** Move to agentic routing only when fixed topologies can't express the problem. Most production systems are hybrids: a workflow routes requests to agents that handle the open-ended subtasks. The advanced end of this spectrum — LLM-driven routing, stateful task agents, role-based multi-agent setups (AutoGen, CrewAI) — trades stability for flexibility. It's covered in [03-harness](../../03-harness/notes/07-orchestration.md) and [04-loop](../../04-loop/README.md).

---

## Operating a workflow

- **Evaluate per task before end-to-end.** Modularity is the point — a failure usually lives in one task ([09](09-evaluating-prompts.md)).
- Collect each task's real inputs and outputs. They become the offline test set and the training data for prompt optimizers like DSPy ([08](08-prompt-optimization.md)).
- In production, sample traffic for quality drift and A/B test competing task implementations.

---

## Go deeper

- Book: [Ch 9](../sources/prompt-eng-for-llms/09-llm-workflows.md) (Shopify DAG worked example, advanced workflows)
- Anthropic, *Building Effective Agents*, and the chaining docs: [references.md](../README.md#vendor-guides)
- Runnable: [notebooks/pe-chatgpt-langchain.ipynb](../notebooks/pe-chatgpt-langchain.ipynb)

---

→ Next: [07-prompting-reasoning-models.md](07-prompting-reasoning-models.md) — what changes when the model thinks for itself.
