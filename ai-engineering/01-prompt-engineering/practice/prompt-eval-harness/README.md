# Lab: a prompt eval harness

Language: TypeScript. Supports [Evaluating prompts](../../notes/09-evaluating-prompts.md) and
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
RUN_OUTPUT
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
