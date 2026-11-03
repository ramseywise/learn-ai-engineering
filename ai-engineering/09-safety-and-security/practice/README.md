# Practice: safety and security

Run everything from this folder, `ai-engineering/09-safety-and-security/practice/`.

| File | What it does | Runtime on a laptop CPU | Packages |
|---|---|---|---|
| [`injection_replay.py`](injection_replay.py) | Replays an illustrative corpus of injection payloads and honest tickets against a stubbed support agent, with an input filter, an egress allowlist and a provenance policy to toggle, and reports attack success and utility per defence. For [Prompt injection and jailbreaks](../notes/02-prompt-injection-and-jailbreaks.md) | Under a second | Standard library |

```bash
uv run injection_replay.py                          # every defence setting, side by side
uv run injection_replay.py --defence filter,policy  # one setting, with each payload's outcome
```

No API key and no download. The payloads were written for this lab and the model is a stub that obeys whatever it can read, so the rates describe this corpus and this stub. They don't measure any model or product.
