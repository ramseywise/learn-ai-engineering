# Lab: a prompt eval harness

Language: TypeScript. The [Python version](../prompt-eval-harness-py/README.md) does the same job on the same inputs. Supports [Evaluating prompts](../../notes/09-evaluating-prompts.md) and
[Controlling output](../../notes/04-controlling-output.md).

Prompt changes feel like improvements until a number says otherwise. This harness runs three prompt
variants over twelve labelled support tickets, grades each output on three checks, and shows which
cases each change fixed and broke. Four of the cases are hard on purpose: a crash on the billing
page (a bug, not billing), and a ticket that tries to instruct the classifier.

## Run it (offline, no key)

```bash
npx tsx run.ts     # the report
npx tsx test.ts    # the assertions
```

Real output with the stub:

```text
model: stub, 12 cases

variant          pass   95% CI       json  known  correct  tokens
v1-bare            0%  [  0%, 24%]    0%    0%      0%     407
v2-format         83%  [ 55%, 95%]  100%  100%     83%     556
v3-rule+shots    100%  [ 76%,100%]  100%  100%    100%    1694

v1-bare -> v2-format
  fixed:  refund-1, refund-2, login-1, login-2, bug-1, bug-2, how-1, how-2, edge-2, edge-3
  broken: none

v2-format -> v3-rule+shots
  fixed:  edge-1, edge-4
  broken: none

still failing in v3-rule+shots: 0
```

Read the confidence intervals before the point estimates. At 12 cases, 100% has a 95% lower bound
near 76%: the harness shows you a direction, not a measurement. Grow the case set before you trust
a small gap.

The stub is a rule-based stand-in in `stub.ts`, not a model. Its scores show how the harness
behaves, and say nothing about how a real model scores on these prompts.

## Swap in a real model

```bash
npm install                                 # installs @anthropic-ai/sdk
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 npx tsx run.ts        # or claude-haiku-5-5, claude-sonnet-5-5, claude-fable-5-1
```

`model.ts` is the only file that changes behaviour. This spends real money: 3 variants times 12
cases is 36 calls. It enables the server-side refusal fallback (`fallbacks: "default"`); `model.ts`
says how to remove it.

## Exercises

1. Add a fourth variant that drops the examples and keeps the rule. Which cases flip, and does the
   token saving justify them?
2. Add a grader that fails any output over 20 tokens. Which variant does it hurt, and why?
3. Add six more edge cases from your own support queue. How wide is the interval now?
