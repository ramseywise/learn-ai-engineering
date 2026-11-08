---
origin: synthesis
sources:
  - "Wang et al. 2025, Efficient Agents: Building Effective Agents While Reducing Cost — https://arxiv.org/abs/2508.02694"
  - "Yang et al. 2026, Toward Efficient Agents: A Survey of Memory, Tool Use, and Planning — https://arxiv.org/abs/2601.14192"
  - "Xing et al. 2026, Critique of Agent Model — https://arxiv.org/abs/2606.23991"
  - "Zhao & Zhao 2026, Runtime-Independent Persistent Agents — https://arxiv.org/abs/2609.00546"
  - "Arsanjani & Bustos, Agentic Architectural Patterns for Building Multi-Agent Systems (Packt, 2026), ch. 2, 11"
confidence: medium
cleaned: 2026-11-06
---

# 1b — What an agent costs

> One model call has a price. An agent run has a price that grows with every step, because each step re-reads everything before it. Price the run, then divide by how often it succeeds.

[Note 01](01-agent-fundamentals.md) built the restock agent as a loop: the model reads the context, picks a tool, reads the result, and goes round again. This chapter prices that loop. It asks three questions. Where do the tokens go? What is the right unit for comparing two agent designs? And which parts of an agent are worth what they cost?

The evidence is thin. There is one systematic study of components on one benchmark, plus a survey that names the levers but measures nothing. Read the numbers as the shape of the trade-off, not as prices.

---

## Where the tokens go

A chat reply costs its prompt plus its answer. An agent pays for its prompt again on every step, and the prompt keeps growing. A 2026 survey of efficient agents ([arXiv:2601.14192](https://arxiv.org/abs/2601.14192) (Yang et al., 2026-01, preprint survey)) puts it this way: "the output of step n becomes the input cost of step n+1". It writes agent cost as model generation plus terms for tool calls, memory operations and retries, so efficiency is "not only about reducing language generation, but also about reducing the frequency and improving the selectivity of tool or memory invocations and retries along a trajectory". The survey runs no experiments of its own. Its one per-task scale figure is second-hand: a deep-research agent calling search up to 600 times on one problem. Its introduction calls the growth "exponential". With a fixed amount added per step, total input grows with the square of the step count, which is bad enough.

```text
step 1  [system][q]                                  → out₁, obs₁
step 2  [system][q][out₁ obs₁]                       → out₂, obs₂
step 3  [system][q][out₁ obs₁][out₂ obs₂]            → out₃, obs₃
  ...
step n  [system][q][out₁ obs₁] ... [outₙ₋₁ obsₙ₋₁]   → answer
        └──────────── re-read on every call ───────────┘
total input ≈ n·system + (n²/2)·(out + obs)
```

Prefix caching makes the repeated part cheaper (01's [choosing a model](01-agent-fundamentals.md#choosing-a-model) explains keeping the prefix byte-stable). It doesn't change the shape: the context still grows, and every new observation is read at full price on each step after it.

---

## The unit: cost per solved task

Cost per run hides failure. A run that costs $0.10 and succeeds half the time costs $0.20 per success. **Cost-of-pass** is that number: the cost of one attempt divided by the success rate. Efficient Agents ([arXiv:2508.02694](https://arxiv.org/abs/2508.02694) (Wang et al., 2025-08, preprint)) uses it to compare one agent framework's components on the GAIA validation set (about 165 tasks, one run per setting, May 2025 prices).

**The backbone mattered most.** Claude 3.7 Sonnet was the most accurate (61.8%) but cost $3.54 per solved task, against $0.98 for GPT-4.1 at 53.3% and $0.13 for Qwen3-30B-A3B at 17.6%. Reasoning models got much worse per success on harder tasks: o1's cost-of-pass rose from $1.96 on Level 1 to $12.66 on Level 3.

**Most extra machinery bought little.** Sampling four candidate actions per step and picking one with a reward model raised accuracy from 53.3% to 53.9% and cost-of-pass from $0.98 to $1.28. Capping the loop at 8 steps instead of 12 gave 52.7% against 53.3% accuracy, at $0.70 against $0.98 per success. The cheapest memory was also the best: keeping the plain action and observation history scored 56.4% at $0.74, while having the model summarise the history scored 51.5% at $1.52. More search sources helped on both counts (53.3% → 59.4% accuracy, $1.32 → $0.81).

Putting the cheapest setting of each component together kept 51.5% accuracy against 53.3% for the OWL framework, at $0.285 against $0.398 per attempt. The paper reports that as a 28.4% cut in cost-of-pass, but it is the cut in cost per attempt. Cost-of-pass fell from $0.75 to $0.55. The limits are real. It is one benchmark of about 165 tasks with no repeated runs, so 1–3 point differences are noise. It changes one component at a time, so interactions are untested, and some cost figures disagree between its tables.

---

## Pricing a run

The code below prices the restock agent's loop with the token model from the diagram, then applies cost-of-pass.

```python
# What one agent run costs: every step re-reads the whole context so far.
PRICE_IN, PRICE_OUT = 2.00, 8.00     # $ per million tokens (illustrative)

def run_cost(steps, system=2_000, out=300, obs=1_500, keep_last=None):
    """Tokens and dollars for one run of `steps` model calls.

    Each call reads the system prompt plus the history; each step adds the
    model's output and a tool observation to the history. keep_last=k keeps
    only the last k steps of history (a simple sliding window)."""
    history, tin, tout = [], 0, 0
    for _ in range(steps):
        window = history if keep_last is None else history[-keep_last:]
        tin += system + sum(window)
        tout += out
        history.append(out + obs)
    dollars = (tin * PRICE_IN + tout * PRICE_OUT) / 1e6
    return tin, tout, dollars

def cost_of_pass(dollars_per_attempt, success_rate):
    """Expected spend per solved task: cost of one attempt / success rate."""
    return dollars_per_attempt / success_rate

for steps in (4, 8, 12, 24):
    tin, tout, d = run_cost(steps)
    print(f"{steps:>2} steps: {tin:>7,} in, {tout:>5,} out, ${d:.3f}")

# Step caps with success rates measured in Efficient Agents (GAIA, GPT-4.1);
# the token model above is ours, so only the shape of the result carries over.
print()
for steps, success in ((4, 0.418), (8, 0.527), (12, 0.533)):
    _, _, d = run_cost(steps)
    print(f"cap {steps:>2}: success {success:.1%}, cost-of-pass ${cost_of_pass(d, success):.3f}")

print()
_, _, full = run_cost(24)
_, _, window = run_cost(24, keep_last=4)
print(f"24 steps, full history ${full:.3f}; last 4 steps only ${window:.3f}")
```

Output:

```text
 4 steps:  18,800 in, 1,200 out, $0.047
 8 steps:  66,400 in, 2,400 out, $0.152
12 steps: 142,800 in, 3,600 out, $0.314
24 steps: 544,800 in, 7,200 out, $1.147

cap  4: success 41.8%, cost-of-pass $0.113
cap  8: success 52.7%, cost-of-pass $0.288
cap 12: success 53.3%, cost-of-pass $0.590

24 steps, full history $1.147; last 4 steps only $0.463
```

Doubling the steps from 12 to 24 nearly quadruples the input. The step from 8 to 12 bought 0.6 points of success and doubled the cost per solved task. The sliding window cuts the 24-step run by 60%, but only if the agent doesn't need what fell out of the window. The model assumes every run uses all its steps. A real cap stops runs that finish early sooner, so measure your own step distribution before you choose one.

---

## The levers, and what each costs

The survey sorts the levers by where they cut cost. The table keeps the ones with a home elsewhere in the course; the survey itself gives no measured comparison between them.

| Lever | Cuts | Costs | Where in the course |
|---|---|---|---|
| Cap the steps | Tail runs | Hard tasks that needed the extra steps | [AIE 04/02 Loop shapes](../../../ai-engineering/04-loop-engineering/notes/02-loop-shapes.md) |
| Bound the history (window, compaction) | Input per step | What was dropped; summarising is itself a model call | [AIE 02/05 Compression](../../../ai-engineering/02-context-engineering/notes/05-compression-compaction.md) |
| Retrieve tools, don't list them all | Prompt size | A retrieval miss means the right tool is never offered | [02b](02b-planning-and-tool-use.md#choosing-among-many-tools) |
| Run independent calls together | Waits | Nothing in tokens; needs a plan with dependencies | [02b](02b-planning-and-tool-use.md#plan-as-a-graph-run-independent-calls-together) |
| Cheaper backbone per role | Price per token | Success rate, so check cost-of-pass, not price | [01](01-agent-fundamentals.md#choosing-a-model) |
| Cache skills and plans | Repeat work | Building and maintaining them; pays only with reuse | [03b](03b-learning-from-experience.md) |
| Fewer agents, sparser messages | Coordination tokens | Diversity, where it helped | [04b](04b-when-more-agents-pay.md) |

*Agentic Architectural Patterns* (ch. 2) adds two serving-side levers that the survey does not cover. First, split the work by role: a larger model orchestrates and delegates sub-tasks to smaller specialised models or plain tools, so the flagship price is paid only where the reasoning needs it. Its two worked examples are a research assistant that reads dozens of papers (large model, large context, higher cost accepted) and a smart-home controller that only maps a short voice command to an API call (a small distilled model, minimal cost per task). Second, cut round trips: if one tool's output can feed the next tool directly, skip the intermediate reasoning step, or let the model plan several tool calls in a single pass instead of deciding, calling and waiting one call at a time. The chapter also notes that a fast model does not help if the tools are slow. These are the authors' design guidance. The chapter gives no measured savings for either.

A learning loop has its own bill. *Agentic Architectural Patterns* (ch. 11) puts a **cost circuit breaker** around it: a monitor compares token spend with a budget and throttles or blocks the next job. Its prose says a breaker trips at 90% of a $50 per-job allowance. Its code (rate $0.002 per 1,000 tokens, invented) holds a $50 monthly budget and blocks only once spend exceeds 100%, so there is no 90% warning. With $7 already spent, a job that logs $10 and then $40 more takes the total to $57 and blocks the next job after the overspend, not before it. A breaker that checks after the call limits the next call only; to cap one run you need the check before each call. The chapter's return-on-investment example (a refund agent saving "$45,000 in December", from an assumed $0.50 per agent ticket against $12.00 per human ticket) is invented, and its ROI code never computes a saving, only a ratio of satisfaction to success rate over two days.

The survey's rule for judging any of these is the one this chapter uses: first check the agent is still effective, then compare cost at matched quality, or quality at a matched budget. It notes that most papers don't report that cleanly.

---

## Where the competence lives

One more cost is easy to miss: who maintains the agent. A 2026 position paper ([arXiv:2606.23991](https://arxiv.org/abs/2606.23991) (Xing et al., 2026-06, preprint)) argues that current LLM agents are **"largely agentic but not yet agentive"**: "much of their competence resides in their workflows and harnesses, not in the model itself". Goals come from the user's instruction, identity from a hand-written system prompt, and changing behaviour means editing the prompt or retraining. It runs no experiments. Its theorems hold only under assumptions such as a world model with a known error bound, and the authors promote their own world-model line. Read it as a reminder, not a result: the restock agent's routines, step caps and memory rules are code and prompts that someone writes, tests and keeps up to date, and that work belongs in the cost too.

If the competence lives in those files, they are what has to survive a change of model or host. Runtime-Independent Persistent Agents ([arXiv:2609.00546](https://arxiv.org/abs/2609.00546) (Zhao & Zhao, 2026-09, preprint)) defines the persistent agent as identity, memory and an executable body (code, prompts, tools, policies, tests), with model, harness and server as a replaceable substrate. A transcript is raw evidence, not memory, and a resumed run rebuilds its context from the durable state. Copying the directory does not copy authority: a migrated agent's old copy is fenced so it can't act twice, and every external effect is recorded with an idempotency key first. The evidence is one existing installed agent, moved between a laptop and a desktop, from Codex to Claude Code and from Slack to Telegram, with identity and memory hashes and 22 task IDs preserved, plus five supervised round trips on simple arithmetic tasks. The authors say this doesn't establish that the agent behaves the same afterwards.

---

## Pitfalls

- **Comparing price per token instead of cost per success.** The most accurate backbone in Efficient Agents cost 3.6× more per solved task than the runner-up.
- **Reading cost per attempt as cost-of-pass.** They differ by the success rate. The same paper's headline mixes them up.
- **Raising the step cap "to be safe".** Input grows with the square of the steps. Measure what fraction of runs need the extra steps.
- **Summarising history to save tokens without measuring.** Summarised memory cost twice as much per success as the plain history in Efficient Agents, because the summary call is not free and lost detail cost accuracy.
- **Trusting a 1-point difference.** On about 165 tasks with one run, it is noise.
- **Leaving the harness out of the cost.** Routines, guards and prompts are maintained by people, and they are what must survive a model or host change.

---

## Try it

1. In `run_cost`, raise `obs` from 1,500 to 6,000 tokens (a tool that returns a whole web page). What happens to the 12-step cost, and which lever from the table would you reach for first?
2. A design costs $0.20 per attempt and succeeds 40% of the time. A second costs $0.50 and succeeds 90%. Which is cheaper per solved task?
3. Your agent uses all 12 steps on 10% of tasks and finishes in 5 on the rest. Should you cut the cap to 8?

<details>
<summary>Answers</summary>

1. Each step now adds 6,300 history tokens instead of 1,800, so the 12-step input rises from 142,800 to 439,800 tokens (66 × 6,300 + 12 × 2,000), and the run from $0.314 to about $0.91. Bound the observation first: return only the fields the agent needs, or keep the full page out of the history and store a handle to it.
2. The first, narrowly: $0.20 / 0.4 = $0.50 per success against $0.50 / 0.9 ≈ $0.56 for the second. If a failure costs you anything beyond tokens (a missed stockout), the second wins.
3. Only if the long runs mostly fail anyway. Check the success rate of runs that reach step 8. If they rarely succeed, the cap saves money at little cost. If they often succeed, you lose those tasks.

</details>

---

## Interview checklist

| Question | Answer |
|---|---|
| Why does agent cost grow faster than step count? | Each step re-reads the whole context, so total input grows roughly with the square of the steps. |
| What is cost-of-pass? | The cost of one attempt divided by the success rate: expected spend per solved task. |
| Which agent component matters most for cost per success? | The backbone. In Efficient Agents (GAIA), Claude 3.7 Sonnet scored 61.8% at $3.54 per solved task against GPT-4.1's 53.3% at $0.98. |
| Does step-level best-of-N pay? | Not there: N=4 moved accuracy 53.3% → 53.9% and raised cost-of-pass from $0.98 to $1.28. |
| Is summarising history a cheap memory? | Not by default. Plain history scored 56.4% at $0.74 per success; model-summarised memory scored 51.5% at $1.52. |
| How should you compare two agent designs on cost? | Check both still work, then compare cost at matched quality or quality at a matched budget. |

---

## Next

→ [01c — model as agent and how agents learn](01c-model-as-agent-and-how-agents-learn.md), then [02 — tool use and the ReAct loop](02-tool-use-and-react.md): the mechanics of a tool call, from raw function calling to MCP.
