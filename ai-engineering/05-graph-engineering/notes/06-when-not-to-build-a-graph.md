---
origin: web-authored
sources:
  - https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph
  - https://www.anthropic.com/engineering/multi-agent-research-system
  - https://www.anthropic.com/engineering/building-effective-agents
  - https://flowtivity.ai/blog/graph-engineering-2026-guide-openclaw-codex/
  - https://arxiv.org/abs/2512.08296
  - https://arxiv.org/abs/2604.02460
  - "Salvatore Raieli & Gabriele Iuculano, Building AI Agents with LLMs, RAG, and Knowledge Graphs (Packt, 2025), ch. 9"
confidence: medium
cleaned: 2026-11-01
---
# 6 — When Not to Build a Graph

> Structure what you know; leave agency where you don't. A graph is overhead you justify with a signal and a measurement.

A graph drawn over work nobody understands yet fixes the first guess in place, and then charges for it: Anthropic reports multi-agent systems at about 15× a chat turn's tokens, with more prompts to drift and more places for a wrong answer to come from. This chapter is the negative case: the test for work you can't name in advance, the arithmetic of fan-out, and what to try before adding a node.

---

## Work you can't name ahead of time

LangChain is explicit that some work is too fluid to pin down:

> Generic deep research *"requires planning and delegation in ways that are hard to pin down ahead of time."* Forcing agentic tasks *"into deterministic paths is the wrong move."* Use an agent harness instead.

> **Structure what you know, leave agency where you don't.**

The test: can you name the nodes before the run starts? If not, can `Send` derive them from a step you do know (one worker per document the retriever returns)? If neither, you want a harness with a good loop ([03-harness](../../03-harness-engineering/README.md), [04-loop](../../04-loop-engineering/README.md)), not a graph. A graph drawn over work you don't understand yet just fixes your first guess in place.

---

## What fan-out costs

Anthropic's multi-agent research system is the first-party anchor. In their write-up, agents use about **4× the tokens of a chat interaction**, and multi-agent systems about **15×**. In exchange, the multi-agent version beat a single agent by a wide margin on their research eval, and token usage alone explained most of the variance in performance. Their conclusion: multi-agent systems pay off for tasks whose value is high enough to cover the tokens, and that **parallelise well**. Tasks where every agent needs the same context, or with many dependencies between agents, are a poor fit.

Kim et al. ([arXiv:2512.08296](https://arxiv.org/abs/2512.08296), 2025-12) tested that conclusion under controlled conditions: 260 configurations across six agentic benchmarks, five architectures and three model families (GPT-5, Gemini 2.x, Claude Sonnet 3.7–4.5), with compute matched. The spread was enormous. A centralized team scored 80.8% higher than a single agent on Finance Agent, where the work decomposes into parallel subtasks; every multi-agent variant lost 39–70% on PlanCraft, where each step constrains the next; and the mean change across all multi-agent configurations was −0.3% (95% CI [−58.7%, +77.2%]). The one predictor that held up under their most conservative statistics was the single agent's own score: once it was above about 45%, adding agents had negative returns. Multi-agent runs spent 1.6–6.2× the tokens of a single agent at matched performance. Their caveats: only 20 tasks per cell on SWE-bench Verified and Terminal-Bench, and prompts were not tuned per model. Tran & Kiela ([arXiv:2604.02460](https://arxiv.org/abs/2604.02460), 2026-04) get the same answer from the other side: on multi-hop QA at matched thinking-token budgets, a single agent was best or tied with every multi-agent variant ([05](05-topology-patterns.md#when-multi-agent-beats-single-agent)).

![Box plots for six benchmarks comparing a single agent with four multi-agent architectures: every multi-agent variant gains 57–81% on Finance Agent and loses 39–70% on PlanCraft, with small losses on SWE-bench Verified](../sources/images/kim-2025-scaling-agent-systems-fig2.png)
*Image Source: Kim et al., [Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296) (2025), Fig. 2*

flowtivity puts the trade-off as a table. Its numbers are vendor estimates, so use them as a shape to test rather than as constants:

| Metric | Loop | Graph (fan-out) |
|---|---|---|
| Wall-clock time | Higher | Lower |
| Tokens per cycle | Lower | ~3× higher (flowtivity) |
| Break-even pass rate | — | ~50% (flowtivity) |

The logic behind the break-even is sound even if the number isn't: when most cycles fail and get redone, you pay the fan-out cost for work that gets thrown away. Fan-out pays when per-cycle success is high and the branches are genuinely independent. Find your own break-even: run the same task set through the loop and through the graph, and record tokens, wall-clock time and pass rate for each.

Tokens per accepted result make the arithmetic concrete. A graph that costs three times as much per cycle has to pass three times as often to tie, so past a certain loop pass rate it can't tie at all, and the case for it has to rest on wall-clock time:

```python
# Cost per accepted result = tokens per cycle / pass rate per cycle.
# The 3x multiplier is flowtivity's vendor estimate; the pass rates are inputs you measure.
def cost_per_accept(tokens, pass_rate):
    return tokens / pass_rate

loop_tokens, graph_tokens = 1, 3
print("loop_pass  loop_cost  graph_pass_needed_to_tie")
for p in (0.2, 0.3, 1 / 3, 0.5):
    needed = p * graph_tokens / loop_tokens
    print(f"{p:<10.2f} {cost_per_accept(loop_tokens, p):<10.2f} "
          f"{needed:.2f}{'  impossible' if needed > 1 else ''}")
```

Output:

```text
loop_pass  loop_cost  graph_pass_needed_to_tie
0.20       5.00       0.60
0.30       3.33       0.90
0.33       3.00       1.00
0.50       2.00       1.50  impossible
```

> **Rule: a graph needs genuine job separation to justify its overhead.** If the branches share most of their context, you're paying N times for the same reading.

---

## The cost of a premature graph

Beyond tokens, every node you add brings:

- **More prompts to maintain**, each of which can drift.
- **State synchronisation** across nodes: schema, reducers, single-writer discipline ([03](03-state-and-reducers.md)).
- **Coordination latency**: routing calls, waiting at joins.
- **Harder debugging**: a wrong answer now has N places it could have come from.

All of that is pure overhead when the problem had one specialty to begin with.

**A "multi-agent system" that is a pipeline.** Raieli & Iuculano's travel planner (*Building AI Agents with LLMs, RAG, and Knowledge Graphs*, ch. 9) has four "agents":

- a random-forest weather model that picks the best month;
- an embedding search over hotel descriptions (top k = 5 by cosine similarity);
- a GPT-2 itinerary writer;
- a GPT-2 email writer.

A controller calls them in a fixed order. No step decides anything, so no edge is conditional and nothing loops. That makes it a four-stage pipeline, and it is better for it: each stage can be tested on its own, and the cheapest model that works is used per stage. The one design choice worth copying is that the trip price (`price × nights + $100 × days`) is computed in code, because "LLMs are not good at arithmetic". Before calling something multi-agent, check whether any node chooses what runs next ([02](02-graph-primitives.md#edges-choose-what-runs-after-a-node)). If none does, build a function chain and skip the graph runtime.

---

## Split the verifier, not the system

The most common "we need a graph" is really an **overloaded verifier**: one check judging correctness, style, safety and completeness at once, and doing all four badly.

Before adding nodes:

1. Split the verifier into **per-criterion checks** inside the existing loop.
2. Make the ones that can be code into code ([04-loop note 03](../../04-loop-engineering/notes/03-the-scorekeeper.md)).
3. Measure again.

If pass rate recovers, ship the loop. If one criterion still fails because it needs a different model, tools or context, that criterion has earned its own node, and now you know exactly which node to add.

---

## Adopting incrementally

When a graph is justified, grow it in this order:

1. **Find the bottleneck.** Write down the current workflow and where it stalls or fails.
2. **Find the real edges.** Mark each step "reads the previous output" or "incidental" ([03](03-state-and-reducers.md#which-edges-are-real)). Only the incidental ones can parallelise.
3. **Sketch 3–5 nodes.** Not twelve.
4. **Measure a baseline** with the loop you have, then with the graph: tokens, wall-clock time, pass rate.
5. **Add nodes one at a time**, each justified by a signal from [01](01-graph-vs-loop.md#the-default-plus-an-escalation-rule).

```mermaid
flowchart TD
    A[Loop fails or stalls] --> B{Overloaded verifier?}
    B -- yes --> C[Split into per-criterion checks<br/>make what you can code]
    C --> D{Pass rate recovers?}
    D -- yes --> SHIP([Ship the loop])
    D -- no --> E[That one criterion earns a node]
    B -- no --> F[Mark real vs incidental edges]
    E --> G[Sketch 3–5 nodes]
    F --> G
    G --> H[Baseline loop vs graph:<br/>tokens, wall-clock, pass rate]
    H --> I[Add nodes one at a time,<br/>each justified by a signal from note 01]
```

This is [flowtivity](https://flowtivity.ai/blog/graph-engineering-2026-guide-openclaw-codex/)'s AUDIT → IDENTIFY → DESIGN → IMPLEMENT sequence, with "measure" made explicit. Their fifth stage, **TYPE**, comes last on purpose: once the topology is stable, give the relationships it records explicit types (`DEPENDS_ON`, `SUPERSEDES`, `DECIDED_BY` …) so later runs can reason over why things are connected, not only that they are. That is the knowledge-graph side of the pillar; the edge-type list and its caveats are in [09](09-kg-fundamentals-and-cypher.md#typed-edges-the-edge-type-is-the-knowledge). A 3–5 node graph with one honest verification step beats a twelve-node topology whose failure modes you can't reason about.

---

## Quick reference

| Situation | Use |
|---|---|
| Single agent, tool-augmented reasoning | Loop |
| Open-ended research with unknowable steps | Harness + loop, **not** a graph |
| Simple task, low per-cycle pass rate | Loop: fan-out cost isn't recovered |
| Single agent already passes more than ~45% | Loop: extra agents had negative returns (Kim et al.) |
| Verifier failing on several criteria | Split the verifier first |
| Several agents with conditional handoffs | Graph |
| 3+ independent verification or research steps | Graph (parallel review) |
| Long-running work needing resume, or human approval mid-run | Graph (checkpointer + interrupts) |
| Parallel specialists merging results | Graph (fan-out with reducers) |

---

## Pitfalls

- **Graphing unknowable work.** Symptom: generic deep research forced onto fixed nodes, which get rewritten every time the task changes. Fix: if you can't name the nodes and `Send` can't derive them from a step you do know, use a harness with a good loop.
- **Adding agents to a task that already works.** Symptom: the token bill grows and the pass rate stays flat or falls. Fix: stay with the loop when a single agent passes more than about 45%, the point past which Kim et al. saw negative returns.
- **Quoting vendor multipliers as constants.** Symptom: a design doc says "3× tokens, 50% break-even" with no measurement behind it. Fix: those are flowtivity's estimates, so run the same task set through both and record tokens, wall-clock time and pass rate.
- **Branches that share most of their context.** Symptom: N workers read the same documents and return overlapping findings. Fix: without genuine job separation you are paying N times for one reading, so don't fan out.
- **Calling a pipeline a multi-agent system.** Symptom: Raieli & Iuculano's four-"agent" travel planner has no conditional edge and no loop. Fix: call it a pipeline and test each stage on its own; that is cheaper and easier to reason about.
- **Letting the model do arithmetic that code can do.** Symptom: a wrong trip price in otherwise fine prose. Fix: compute it in code, as that planner does with `price × nights + $100 × days`.
- **Sketching twelve nodes.** Symptom: a first design nobody can debug, where a wrong answer has twelve places to come from. Fix: sketch 3–5, and add nodes one at a time, each with a signal.

## Try it

1. Your loop costs 10,000 tokens per cycle and passes 25%. A fan-out graph at 3× tokens would pass 70%. Which is cheaper per accepted result, and which pass rate would make them tie?

   <details><summary>Answer</summary>

   Loop: 10,000 / 0.25 = 40,000 tokens. Graph: 30,000 / 0.70 ≈ 42,857 tokens. The loop is slightly cheaper, and they tie at a graph pass rate of 75%. If the graph is also faster and time matters, you may still choose it, but that is a decision about wall-clock time, not tokens.

   </details>

2. Test each with "can you name the nodes before the run starts?": (a) summarise each document a retriever returns; (b) find out why a competitor's revenue fell; (c) classify, draft, then review a support ticket.

   <details><summary>Answer</summary>

   (a) Not by name, but `Send` can derive them from the retriever: a graph. (b) No, and nothing derives them, because the steps depend on what turns up: a harness and a loop. (c) Yes: a graph, and if every ticket takes the same path, a pipeline.

   </details>

3. One check judges correctness, style, safety and completeness, and pass rate has fallen. Write the next three steps in order.

   <details><summary>Answer</summary>

   Split it into per-criterion checks inside the existing loop. Turn the checks that can be code into code. Measure again. Only a criterion that still fails because it needs a different model, tools or context has earned its own node.

   </details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| How do you decide if work is too fluid for a graph? | Ask if you can name the nodes before the run starts, or if `Send` can derive them from a step you know. If neither, use a harness with a good loop. |
| What does fan-out cost, per Anthropic? | In their write-up, agents use about 4× the tokens of a chat interaction and multi-agent systems about 15×, so it pays only for tasks whose value justifies that. |
| What did Kim et al. add to that? | 260 configurations across six benchmarks showed an enormous spread: a centralized team scored 80.8% above a single agent on Finance Agent, where work decomposes, and extra agents had negative returns once a single agent passed about 45%. |
| A vendor says fan-out breaks even at a 50% pass rate. How do you treat that? | As a shape to test, not a constant. Run the same task set through the loop and the graph, and compare tokens, wall-clock time and pass rate. |
| Your verifier is failing. Do you add a node? | First split it into per-criterion checks in the loop, make what can be code into code, and measure. A criterion that still fails because it needs a different model, tools or context has earned a node. |
| What does a premature graph cost besides tokens? | More prompts that can drift, state synchronisation, coordination latency and harder debugging, since a wrong answer now has N places it could have come from. |
| How do you adopt a graph once it is justified? | Find the bottleneck, mark which edges are real, sketch 3–5 nodes, baseline the loop against the graph, and add nodes one at a time, each with a signal. |

## Next

[07-failure-modes-at-scale.md](07-failure-modes-at-scale.md): how graphs fail where single loops don't.
