# Lab: a prompt eval harness (Python)

The Python twin of the [TypeScript lab](../prompt-eval-harness/README.md). Both read the same
`cases.json`, use the same variants and stub rules, and print the same report, so you can compare
them file by file. Read the TypeScript README for why the lab exists and for the exercises.

```bash
uv run run.py      # the report
uv run test.py     # the assertions
```

Real output with the stub, identical to the TypeScript version:

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

The stub is a rule-based stand-in, so these scores show how the harness behaves, not how a real
model scores.

## Swap in a real model

```bash
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 uv run --with anthropic run.py    # or claude-haiku-5-5, claude-sonnet-5-5, claude-fable-5-1
```

This spends real money: 36 calls. `model.py` is the only file that knows about the provider, and it
enables the server-side refusal fallback (`fallbacks="default"`); its comment says how to remove it.
