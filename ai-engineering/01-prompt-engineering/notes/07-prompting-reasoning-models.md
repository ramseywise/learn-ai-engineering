---
origin: synthesis
sources:
  - https://www.promptingguide.ai/guides/reasoning-llms
  - https://www.promptingguide.ai/guides/deep-research
  - https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
  - "Prompt Engineering for LLMs (Berryman & Ziegler, O'Reilly 2024) — Ch 11"
  - https://arxiv.org/abs/2505.11423
  - https://arxiv.org/abs/2504.09858
  - https://arxiv.org/abs/2506.06941
  - https://arxiv.org/abs/2506.09250
  - https://arxiv.org/abs/2412.16720
confidence: medium
cleaned: 2026-10-31
---
# 7 — Prompting Reasoning Models

> Reasoning models are trained to produce chain-of-thought natively before they answer. Much of [03](03-core-techniques.md) is built into them, so the prompting advice shifts from *how to think* to *what to achieve*. Model behavior here changes quickly; treat the specifics as dated, and check the vendor guides in [references.md](../README.md#vendor-guides).

---

## What's different

A reasoning model (o-series, Claude with extended or adaptive thinking, Gemini thinking, DeepSeek-R1) spends **test-time compute** on hidden or summarized thinking tokens before it answers. Two consequences:

- **More thinking usually means better answers** on hard tasks — but with more latency and cost. You control it with an **effort or budget** setting (low / medium / high, or a token budget), not with prompt wording. "Usually" depends on difficulty. On puzzles with a tunable difficulty (Tower of Hanoi, River Crossing, Blocks World), Claude 3.7 Sonnet and DeepSeek ran with and without thinking at matched token budgets. Without thinking they matched or beat the thinking versions on easy instances, and lost on medium ones. On the hardest, both scored zero, and the thinking models started using fewer thinking tokens even with budget left. Putting the Hanoi solution algorithm in the prompt did not move the collapse point ([arXiv:2506.06941](https://arxiv.org/abs/2506.06941) (Shojaee et al., 2025-06)). Read the collapse with its rebuttal. The scoring demanded every move written out, and 2<sup>N</sup>−1 Hanoi moves overrun the output limit at large N. Some scored River Crossing instances have no solution ([arXiv:2506.09250](https://arxiv.org/abs/2506.09250) (Lawsen, 2025-06)). The low-complexity result survives that critique and matches the overthinking row below.
- **The CoT scaffolding you'd write for a standard model is redundant at best**, and can hurt. Explicit step-by-step CoT prompting has been shown to *degrade instruction-following*. Across 15 models on IFEval and ComplexBench, adding CoT lowered constraint accuracy. The paired comparisons (Claude 3.7 Sonnet with and without thinking, DeepSeek-V3 vs. R1) show the same drop. Reasoning helped with formatting and exact wording but led models to drop simple constraints or add content nobody asked for ([arXiv:2505.11423](https://arxiv.org/abs/2505.11423), Li et al., 2025-05). The best mitigation was a trained classifier that decides *whether* to reason for a given instruction.

---

## Prompting tips

| Do | Don't |
|---|---|
| State the goal, constraints and output format clearly and at a high level | Prescribe the reasoning steps ("first do X, then Y…") |
| Use general nudges if you want more effort: "think thoroughly about this," "consider several approaches" | Bolt on "Let's think step by step" |
| Structure inputs with delimiters/XML; use XML for structured output unless JSON is required | Leave the format to chance — reasoning models are prone to formatting drift |
| Add few-shot examples **only** for style or format the model gets wrong, and keep them consistent with the instructions | Pad with examples by default |
| Ask the model to **verify** its work before finishing ("check the result against the test cases") | Assume the reasoning was correct because it was long |
| Use clear quality modifiers when you want ambition ("include as many relevant features as possible; go beyond the basics") | Expect "above and beyond" behavior without asking |

Anthropic-specific notes:
- With extended thinking, **high-level instructions beat prescriptive ones**. Read the thinking output, and only then steer it.
- Few-shot examples can include `<thinking>` blocks to show the *style* of reasoning you want, and the model will generalize from them.
- In agentic loops, **interleaved thinking** (reasoning between tool calls) lets the model reflect on each tool result before acting again.

---

## Hybrid models: escalate gradually

For models where thinking is a switch:

1. **Thinking off** first. Evaluate. A manual CoT prompt is a cheap middle step.
2. If the answers are shallow or wrong in ways that look like a reasoning failure, **enable thinking at low effort**.
3. Escalate to **medium**, then **high**, only while it keeps improving your eval scores ([09](09-evaluating-prompts.md)).
4. Use few-shot examples to fix *style and format*, not reasoning.

![Escalating reasoning effort](../sources/images/dair-hybrid-reasoning-effort-escalation.jpg)
*Evaluate after each step and stop at the first satisfactory one. DAIR, Reasoning LLMs Guide.*

Thinking off can be stronger than it looks, especially if you sample several answers. Ma et al. switched off thinking in DeepSeek-R1-Distill-Qwen-32B by prefilling the thinking block with "Okay, I think I have finished thinking." and closing it. On math, coding and theorem-proving benchmarks, this NoThinking mode used 2.0–5.1× fewer tokens. It trailed full thinking at pass@1 on most benchmarks, but matched it once enough samples were drawn (pass@k at large k). On theorem proving it matched thinking at every k while using 3.3–3.7× fewer tokens. At an equal, small token budget it often won outright: "51.3 vs. 28.9 on AMC23 with 700 tokens." Drawing several NoThinking answers in parallel and keeping the best one beat sequential thinking on tasks with a verifier, at "7× lower latency and even 4× less total token usage." The authors tested only open-weight models, because prefilling the thinking block needs access closed APIs don't give: "we lack access for making interventions to closed-source models" ([arXiv:2504.09858](https://arxiv.org/abs/2504.09858) (Ma et al., 2025-04)). Where you can check answers automatically, try several thinking-off samples before you pay for long thinking.

**Optimize for accuracy first, then latency and cost.**

---

## Where reasoning models earn their cost

Use them for the reasoning-heavy *module* of an application, not the whole thing ([06](06-chaining-and-workflows.md) — separation of concerns):

- **Planning** in agentic systems — e.g., the planner in an orchestrator-worker deep-research agent.
- **Agentic RAG** — routing complex queries and reasoning across many sources.
- **LLM-as-judge** — evaluator-optimizer loops where the judge needs to reason ([09](09-evaluating-prompts.md#llm-as-judge)).
- Large codebases, algorithmic and scientific work, literature synthesis, ambiguous knowledge-intensive tasks.
- **Writing prompts for other models** — meta-prompting ([08](08-prompt-optimization.md)).

![Orchestrator-worker agent](../sources/images/dair-orchestrator-worker-agent.jpg)
*The reasoning model sits in the orchestrator, breaking the query into subtasks. Cheaper models run the parallel search workers and summaries. DAIR.*

![Agentic RAG](../sources/images/dair-agentic-rag.jpg)
*Agentic RAG: a reasoning retrieval agent decides whether to answer directly or call the vector store, a reasoning chain, or web search. DAIR.*

Simple extraction, classification and rewriting rarely need one.

---

## Known failure modes

| Issue | Mitigation |
|---|---|
| **Overthinking** easy tasks (cost, latency) and **underthinking** hard ones | Be specific about the task and the output; route only hard subtasks to the reasoning model; tune effort |
| Output quality — mixed languages, repetition, formatting drift | Unambiguous instructions; explicit format; post-validation |
| Instruction-following degrades with explicit CoT | Drop manual CoT; use carefully chosen few-shot examples; self-reflection; let the model (or a classifier) decide when to reason |
| **The reasoning isn't faithful** — the visible chain of thought doesn't always reflect what drove the answer (*Reasoning Models Don't Always Say What They Think*, 2025) | Don't use the thinking text as an audit trail or a safety monitor on its own; evaluate outputs. A CoT monitor catches only what the chain states. OpenAI's GPT-4o monitor (92% accurate on a small internal set) flagged 0.17% of 102,443 o1-preview chains as deceptive, mostly invented policies used to withhold information ([arXiv:2412.16720](https://arxiv.org/abs/2412.16720) (OpenAI, 2024-12)) |
| Weaker tool calling in some open reasoning models | Test parallel and multi-step tool use explicitly before relying on it |
| Sampling parameters ignored or rejected | Expect fixed temperature on many reasoning endpoints; control with effort instead ([04](04-controlling-output.md#sampling-parameters)) |

---

## Prompting deep-research agents

Deep-research products (OpenAI, Gemini and Claude Research) are reasoning models trained with RL to plan, search, browse and synthesize over minutes. Each run is slow and expensive, so **get the prompt right the first time**:

- **Give it a plan and be specific** about the scope, the time period, and the sources you trust.
- **Answer its clarifying questions thoroughly.** That's the cheapest point to steer the run.

  ![Deep research clarifying questions](../sources/images/dair-deep-research-clarifying-questions.jpg)
  *The agent asks about scope before it starts. "Both / no preference" wastes the cheapest steering point. DAIR, Deep Research guide.*

- **Supply keywords.** The model turns your prompt into search queries, so precise terms (product names, technical terms, brands) save searches.
- **Use clear task verbs**, such as *compare*, *recommend* or *report*, to signal the kind of output you want.
- **Specify the report format**: sections, tables, columns, and length.
- **Upload the documents you already have**, especially for technical or niche topics the web covers poorly.
- **Verify the sources yourself.** Known weaknesses are citation errors, a bias toward certain domains, date-sensitive queries, and paywalled content.

Use deep research only for multi-source, time-sensitive questions that need careful synthesis. A plain reasoning model or a standard model is enough for everything else. Building your own deep agent is covered in [03-harness-engineering](../../03-harness-engineering/README.md).

---

## Intelligence trends (and what they don't fix)

The book went to press in 2024, before the first reasoning models (o1 shipped in September 2024). Its only nod to them is that better RLHF was making chat models "express their chain-of-thought reasoning" more. Read its forecasts as a 2024 baseline.

- **Benchmarks saturate.** Leading models ace MMLU, HellaSwag, GSM8K and similar benchmarks. Partly the models are better, and partly benchmark text leaks into training data (contamination). The book's fixes are refreshed leaderboards (it names the Open LLM Leaderboard 2, since retired) and tests built to resist memorization, such as ARC-AGI. The book calls ARC-AGI "algorithmically generated" and impossible to memorize. In fact its puzzles are hand-designed and protected by a private test set, and even it gave way: in December 2024 o3 scored 76% on ARC-AGI-1's semi-private set (88% at high compute), and ARC-AGI-2 replaced it in 2025. For your own app this means **public scores don't predict your task.** Build your own eval ([09](09-evaluating-prompts.md)).

  ![Benchmark saturation](../sources/images/berryman-prompt-engineering-for-llms-fig11-2.png)
  *Top scores on the Hugging Face Open LLM Leaderboard (v1, open models), Sep 2023 to May 2024. Thin lines are human baselines. GSM8K went from under 10 to the human line in under a year. Image Source: Berryman & Ziegler (2024), Fig. 11-2*

- **Cheaper and faster.** In **distillation**, a small student learns from a large teacher's full next-token distribution rather than from single labels. **Quantization** stores weights in fewer bits. The book says 8 bits instead of 32, but LLM weights are normally held in 16-bit formats, so in practice it is 8 or 4 bits instead of 16. Both cut cost and latency for a modest loss of accuracy.
- **Plan for the trend.** The book's 2024 bet: what is too expensive, too slow, too long for the context or too hard for the model today will not be tomorrow, so don't over-engineer around today's limits. Cost per token and window size have moved that way since. A window that holds the input is not a model that uses all of it well, though, and intelligence gains don't fill in missing context (see below).

---

## What doesn't change

The book's closing lessons hold for reasoning models too — maybe more so:

- **It's still document completion** that mimics training data. Familiar formats still win.
- **It isn't psychic.** Smarter models don't fix missing context. If *you* would need a piece of information to solve the problem, so does the model. Put it in the prompt, or give the model the tools and instructions to fetch it ([02-context](../../02-context-engineering/README.md)).
- **It's easily distracted.** Irrelevant context costs more when the model reasons over all of it.
- **It must be able to decipher the prompt.** If a human couldn't parse the fully rendered prompt, the model probably can't either.
- **It needs to be led** — on goals and constraints now, rather than on steps.
- **It has no internal monologue** unless it gets to write one. Reasoning models build this in, so you no longer prompt for CoT, but the principle is why they work.

---

## Go deeper

- DAIR *Reasoning LLMs Guide*, Anthropic extended-thinking tips, and the reasoning papers: [references.md](../README.md#reasoning-models)
- Book: [Ch 11 PDF](../sources/prompt-eng-for-llms/reading/11-looking-ahead.pdf) (intelligence trends, the two durable lessons)

---

→ Next: [08-prompt-optimization.md](08-prompt-optimization.md) — letting models write and tune prompts.
