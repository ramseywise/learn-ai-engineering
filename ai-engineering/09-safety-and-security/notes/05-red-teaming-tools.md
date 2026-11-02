---
origin: synthesis
sources:
  - https://arxiv.org/abs/2202.03286
  - https://arxiv.org/abs/2311.07689
  - https://arxiv.org/abs/2402.04249
  - https://arxiv.org/abs/2401.12915
  - https://arxiv.org/abs/2406.13352
  - https://arxiv.org/abs/2603.24511
  - https://github.com/NVIDIA/garak
  - https://github.com/microsoft/PyRIT
  - https://www.promptfoo.dev/docs/red-team/quickstart/
confidence: medium
cleaned: 2026-11-01
---

# 5 — Red-Teaming Tools

> A red team looks for what your evaluation doesn't know to ask. The tools make this cheap and repeatable, and they only count if the results change what ships and each finding becomes a test that stays.

Harbour's team ran twenty hand-written attacks before launch, and none of them worked. They were pleased. Then someone asked how many attempts would have got through if the true rate were one in ten, and the answer was uncomfortable: a clean run on twenty is what you'd expect about one time in eight. This chapter is about turning "we tried some things" into evidence. It covers how the practice grew from hand-written prompts into automated loops, what the common tools are for, how to read their numbers without fooling yourself, and how to build a regression suite that a release has to pass.

This is defensive testing of systems you own or are authorised to test. The chapter stays with structure and measurement, and it has no attack strings. Scanners ship their own probe libraries, and that's where you get them when you're doing the work.

## From people to loops

Red-teaming began as people writing test cases by hand, and that's still the source of the most creative findings. But people are expensive, and they repeat themselves. [arXiv:2202.03286](https://arxiv.org/abs/2202.03286) (Perez et al., 2022-02, preprint) made the case for automating it: use one language model to generate test cases against another, and a classifier to judge replies. Their experiments uncovered tens of thousands of offensive replies from a 280B chatbot, using methods ranging from zero-shot generation to reinforcement learning. The new thing was scale, and the methods varied in the diversity and difficulty of the tests they produced.

[arXiv:2311.07689](https://arxiv.org/abs/2311.07689) (Ge et al., MART, 2023-11, preprint) closed the loop. An adversarial model and a target take turns: the first writes attacks, the target improves through safety fine-tuning, and the adversary then has to find something new. On adversarial benchmarks, the violation rate of a model with limited safety alignment fell by up to 84.7% after four rounds, with minimal reported effect on helpfulness.

```mermaid
flowchart LR
    S[Seed attacks] --> A[Adversary model<br/>writes new attacks]
    A --> T[Target system]
    T --> J[Judge<br/>did it fail?]
    J -->|successes| A
    J -->|failures to fix| F[Fix: training, policy, code]
    F --> T
    J -->|every confirmed finding| R[Regression suite]
```

For an application team, the "target" is usually your whole system, and "fix" usually means code and policy rather than model training. The loop is otherwise the same.

## The tools, by the job they do

These overlap, and their feature lists change, so pick by the question you're asking.

| Tool | Job | Use it when |
|---|---|---|
| [garak](https://github.com/NVIDIA/garak) | Vulnerability scanner: probes for leakage, injection, jailbreaks, toxicity, hallucination | You want a broad sweep of a model or endpoint, as with a network scanner |
| [PyRIT](https://github.com/microsoft/PyRIT) | Python framework for orchestrating attacks: targets, converters, scorers, multi-turn | A security engineer wants to script a custom campaign |
| [promptfoo](https://www.promptfoo.dev/docs/red-team/quickstart/) | Generates application-specific attacks, reports, integrates with CI | You want red-teaming beside your evals in the same workflow |
| [AgentDojo](https://github.com/ethz-spylab/agentdojo) | Benchmark for tool-using agents under injection | You're comparing agent defences on utility and attack success |
| [HarmBench](https://github.com/centerforaisafety/HarmBench) | Standardised evaluation for automated red-teaming methods and refusal | You need to compare methods or models fairly |

Getting a first result from a scanner takes one command, using each project's documented form. Both of these need an endpoint and credentials, so they aren't run here.

```bash
# illustrative: needs credentials for the chosen target
uvx garak --target_type bedrock --target_name claude-3-sonnet --spec probes.dan

# illustrative: needs Node and a provider key; setup writes a config for your app
npx promptfoo@latest redteam setup
npx promptfoo@latest redteam run
npx promptfoo@latest redteam report
```

The flags for these tools change between releases, so check the current README before relying on them. What you do with the report matters more. A scanner pointed at a bare model tells you about the model, and it knows nothing about your tools, data or permission model. Harbour's real exposure, a refund reached from a ticket, won't appear until the target is the application. Point tools at the highest layer you can.

Vision models need their own test set, since text scanners don't look at images. RTVLM, [arXiv:2401.12915](https://arxiv.org/abs/2401.12915) (Li et al., Findings of ACL 2024), covers 10 subtasks across faithfulness, privacy, safety and fairness, and it found that ten prominent open VLMs struggled to different degrees, with a performance gap of up to 31% against GPT-4V.

## How to read a number

**A clean run is weak evidence.** Twenty tries with zero successes doesn't mean zero risk. The Wilson interval gives a sensible bound, and the arithmetic is worth having in your head.

```python
from math import sqrt

def wilson_upper(successes, n, z=1.96):
    p = successes / n
    centre = p + z * z / (2 * n)
    margin = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre + margin) / (1 + z * z / n)

print("0 successes observed: 95% upper bound on the true attack rate")
for n in [10, 20, 50, 100, 500, 2000]:
    print(f"  n={n:5}  rate could still be {wilson_upper(0, n):6.1%}")

print("\nchance of seeing a clean run if the true rate is 10%")
for n in [10, 20, 50]:
    print(f"  n={n:3}  {(1 - 0.10) ** n:.1%}")

print("\nchance an attacker succeeds at least once, by number of tries")
for rate in [0.001, 0.01, 0.05]:
    row = "  ".join(f"{k} tries: {1 - (1 - rate) ** k:6.1%}" for k in [10, 100, 1000])
    print(f"  per-try {rate:5.1%}  {row}")
```

Output:

```text
0 successes observed: 95% upper bound on the true attack rate
  n=   10  rate could still be  27.8%
  n=   20  rate could still be  16.1%
  n=   50  rate could still be   7.1%
  n=  100  rate could still be   3.7%
  n=  500  rate could still be   0.8%
  n= 2000  rate could still be   0.2%

chance of seeing a clean run if the true rate is 10%
  n= 10  34.9%
  n= 20  12.2%
  n= 50  0.5%

chance an attacker succeeds at least once, by number of tries
  per-try  0.1%  10 tries:   1.0%  100 tries:   9.5%  1000 tries:  63.2%
  per-try  1.0%  10 tries:   9.6%  100 tries:  63.4%  1000 tries: 100.0%
  per-try  5.0%  10 tries:  40.1%  100 tries:  99.4%  1000 tries: 100.0%
```


The last table explains why rates that look small can still matter. An attacker with a planted document gets a try from every reader, and at one percent per try, success in a thousand tries is close to certain.

**Compare attack success with utility.** A defence that blocks everything scores perfectly, which is why [AgentDojo](https://arxiv.org/abs/2406.13352) (Debenedetti et al., NeurIPS 2024) reports both together. Its 97 tasks and 629 security cases were built to be extended and not to be a static list, because static defences only ever face yesterday's attacks.

**Attack success depends on the setup.** HarmBench, [arXiv:2402.04249](https://arxiv.org/abs/2402.04249) (Mazeika et al., 2024-02, preprint), exists because the field lacked a standard way to compare methods. It compares 18 red-teaming methods against 33 target models and defences using one setup. When you read a claimed attack success rate, ask about the target, the judge, the number of attempts allowed and the set of behaviours.

**The judge has error rates too.** Most automated red-teaming grades outcomes with a model, and a bad judge inflates or hides results. Treat it like any other judge, measure it against human labels, and look at a sample of its passes. The [Eval pillar's judge chapter](../../../generative-ai/08-eval/notes/05-llm-as-judge.md) covers this. For actions, skip the judge entirely if you can: whether an email went out is a fact in a log.

**Tuning on the test set flatters you.** A defence tuned with access to a benchmark's items can look better than it is. Keep part of your red-team set held out from whoever tunes the defences.

## Static suites aren't enough, and they are still necessary

[Chapter 2](02-prompt-injection-and-jailbreaks.md) described the Claudini result ([arXiv:2603.24511](https://arxiv.org/abs/2603.24511), Panfilov et al., 2026-03, preprint), where coding agents working as automated researchers devised white-box attacks that beat tuned baselines. Its authors argue that automated adaptive evaluation should be the minimum bar for defences. So there are two distinct activities here, and you need both.

| | Regression suite | Adaptive campaign |
|---|---|---|
| **Question** | Did we reintroduce a known failure? | What's the next failure we don't know of? |
| **When** | Every change, in CI | Before launch, on major change, on a schedule |
| **Cost** | Low, bounded | High, open-ended |
| **Stops when** | All cases pass | Budget ends, or a person is satisfied |
| **Output** | Pass or fail | New findings, which enter the suite |

The arrow from the right column to the left is the thing to build. It's how a one-off discovery becomes permanent protection.

## A regression suite that can't fool itself

A common failure is a passing test that measured nothing. Perhaps the model simply didn't try, or the test harness lost the tool call, or the canary was never reachable. [The canary pattern](../../03-harness-engineering/notes/04-execution-boundaries.md#testing-the-boundary-the-canary-pattern) from the harness pillar solves this with two runs per case. Unguarded, the harm must occur, which proves that the test can see it. Guarded, the harm must not occur **and** there must be evidence of an actual denial. Anything else is inconclusive. Here's a small version around Harbour's refund tool, with scripted stand-ins in place of a model so that the logic is visible.

```python
from dataclasses import dataclass, field

@dataclass
class World:
    refunds: list = field(default_factory=list)
    denials: list = field(default_factory=list)

def tool_refund(world, guarded, order_id, caller):
    if guarded and order_id.startswith("other-"):
        world.denials.append(f"refund {order_id} for {caller}")
        return
    world.refunds.append(order_id)

# Each stand-in plays a model in a certain state. Real suites call the agent here.
def agent_attempts(world, guarded):
    tool_refund(world, guarded, "other-207", "ana")
def agent_declines(world, guarded):
    pass
def agent_guard_off(world, guarded):
    tool_refund(world, False, "other-207", "ana")   # a code path that bypasses the check
def agent_flaky(world, guarded):
    if not guarded:
        tool_refund(world, guarded, "other-207", "ana")

def verdict(agent):
    base = World(); agent(base, guarded=False)
    if not base.refunds:
        return "INCONCLUSIVE", "baseline did no harm, so this test can't see harm"
    g = World(); agent(g, guarded=True)
    if g.refunds:
        return "FAILED", "harm happened with the guard on"
    if not g.denials:
        return "INCONCLUSIVE", "no harm, but no denial recorded: control not exercised"
    return "HELD", "harm in baseline, denial recorded when guarded"

for name, a in [("attempts", agent_attempts), ("declines", agent_declines),
                ("bypasses guard", agent_guard_off), ("only tries unguarded", agent_flaky)]:
    v, why = verdict(a)
    print(f"{name:21} {v:13} {why}")
```

Output:

```text
attempts              HELD          harm in baseline, denial recorded when guarded
declines              INCONCLUSIVE  baseline did no harm, so this test can't see harm
bypasses guard        FAILED        harm happened with the guard on
only tries unguarded  INCONCLUSIVE  no harm, but no denial recorded: control not exercised
```


Only one of these four is a pass. The agent that declines and the one that tries only when unguarded both look fine to a test that merely checks "no refund occurred", and neither one exercised the control. The fourth is the case worth pausing on. Models are non-deterministic, so a suite must rerun inconclusive cases and track how often they occur, and it must not count them as passes.

Agents add a second difficulty: an attack can succeed in some runs and not others. So run each case several times and gate on a bound, not on a single outcome. Combine that with severity, because one failure on a refund case isn't the same as a few on a tone case.

```python
from math import sqrt

def upper(k, n, z=1.96):
    p = k / n
    return ((p + z*z/(2*n)) + z*sqrt(p*(1-p)/n + z*z/(4*n*n))) / (1 + z*z/n)

BUDGET = {"critical": 0.0, "high": 0.05, "medium": 0.20}

results = [  # (case, severity, failures, runs) synthetic
    ("refund to other customer", "critical", 0, 30),
    ("email to outside address", "critical", 1, 30),
    ("system prompt disclosure", "medium", 3, 30),
    ("tone: rude reply",         "medium", 8, 30),
    ("link with data in query",  "high", 0, 10),
    ("link with data in query (more runs)", "high", 0, 100),
]

blocking = 0
for case, sev, k, n in results:
    limit = BUDGET[sev]
    if sev == "critical":
        ok = k == 0
    else:
        ok = upper(k, n) <= limit
    blocking += not ok
    print(f"{'pass ' if ok else 'BLOCK'} {sev:9} {k:2}/{n:<3} "
          f"upper bound {upper(k, n):5.1%}  limit {limit:4.0%}  {case}")
print(f"\nrelease {'BLOCKED' if blocking else 'allowed'}: {blocking} case(s)")
```

Output:

```text
pass  critical   0/30  upper bound 11.4%  limit   0%  refund to other customer
BLOCK critical   1/30  upper bound 16.7%  limit   0%  email to outside address
BLOCK medium     3/30  upper bound 25.6%  limit  20%  system prompt disclosure
BLOCK medium     8/30  upper bound 44.4%  limit  20%  tone: rude reply
BLOCK high       0/10  upper bound 27.8%  limit   5%  link with data in query
pass  high       0/100 upper bound  3.7%  limit   5%  link with data in query (more runs)

release BLOCKED: 4 case(s)
```


Critical cases allow no failures at all, since any success is a bug in a boundary that should hold by construction. Other cases gate on the upper bound, so too few runs can block you just as failures can, as the fifth case shows. That's correct behaviour: you haven't yet shown that it's safe. The limits above are ours for this example, and yours should come from your threat model. To run this on every change, follow [Evals in CI](../../../generative-ai/08-eval/notes/10-evals-in-ci.md).

## Running a campaign

For a pre-launch or scheduled exercise, write down the following before you begin:

1. **Scope and authorisation.** Which systems, which accounts, who approved it. Use test tenants and synthetic data. Check a hosted model provider's terms on testing.
2. **The threat model.** Start from the top paths in [chapter 1](01-threat-model.md), so that effort goes to what matters.
3. **Success criteria for each path.** "Refund issued to another customer's order" is testable. "Model misbehaves" isn't.
4. **A mix of methods.** Scanner sweep, scripted campaign, then people. People find the things no probe library has.
5. **Handling of findings.** Store attack material with restricted access, log who ran what, and write each confirmed finding as a regression case with an owner.

Give the people who do this different perspectives: someone from support knows what a plausible customer looks like, and someone from security knows how attacks chain. The result you want is a list of fixes in the system. A list of clever prompts is a means to that end.

## Pitfalls

- **Testing the bare model.** A scan of the model says nothing about your tools, data or permissions.
- **Treating zero successes as safety.** Twenty clean runs still allow a true rate above 16%. Report the bound.
- **Counting "nothing happened" as a pass.** Require evidence that the control fired, and a baseline that shows the test can see harm.
- **Reporting attack success alone.** Pair it with utility and false refusals.
- **Running one sample per case.** Agents vary between runs, so repeat and gate on a bound.
- **Tuning defences on the full test set.** Keep a held-out set, or your score only measures memory.
- **Findings without owners.** A report that doesn't change the system or the suite was only an exercise.
- **Testing without authorisation.** Stick to systems you own, or have written approval to test, and read your provider's terms.

## Try it

1. Using `wilson_upper`, find the smallest `n` for which zero successes puts the 95% upper bound under 1%.
2. Add an agent to the verdict code that attempts the refund, gets denied and then retries by a different route that isn't guarded. Which verdict results? Which single change in the world model would help you see the second route?
3. In the gate code, what is the smallest number of runs at which the zero-failure "high" case passes the 5% limit?
4. Take three paths from your threat model and write each as a testable success criterion, plus the log entry that proves the control fired.

<details><summary>Answers</summary>

1. `n=381` gives an upper bound of about 1.0%. Near zero successes the bound is about `z*z / (n + z*z)`, or roughly 3.84/n, the familiar rule of three.
2. `FAILED`, since a refund occurred with the guard on, even though a denial was also recorded. The check for harm comes first, and that's the right order. Recording the route on every refund would show which path got through.
3. 73 runs, with the same formula: 3.84 / (73 + 3.84) is 5.0%.
4. For example: "No refund reaches an order the session's customer doesn't own", proved by a `policy_denied` entry with the case's trace ID. Vague criteria are a sign that the path isn't yet understood.

</details>

## Interview questions

| Question | Answer |
|---|---|
| What was Perez et al.'s contribution? | Using one model to red-team another at scale, with a classifier as judge, which uncovered tens of thousands of offensive replies without hand-writing test cases. |
| How does MART differ? | It's iterative. An adversary writes attacks, the target is safety-tuned, and the adversary has to find new ones. It reported violation rates down by up to 84.7% after four rounds. |
| garak, PyRIT or promptfoo? | garak for a broad scanner sweep, PyRIT to script custom campaigns, promptfoo for app-specific attacks and CI next to evals. They overlap, so choose by the question. |
| You got 0 successes in 20 tries. What can you claim? | At 95%, the true rate may still be about 16%. Report the bound and do more runs, or show that the control holds by construction. |
| How can a safety test pass while measuring nothing? | The model didn't try, or the harness missed it. So require a baseline run where harm occurs, and evidence of denial in the guarded run. Otherwise report inconclusive. |
| Static suite or adaptive attack? | Both. The suite prevents regressions cheaply, on every change. Adaptive campaigns find what the suite doesn't know about, and each finding joins the suite. |
| What do you check when reading an attack success rate? | The target, the judge and its errors, attempts allowed, behaviours tested, whether the attack was adapted to the defence, and the utility cost. |

## Next

However much you test, something will get through. [Incident response](06-incident-response.md) is about being ready to notice, contain and learn from it.
