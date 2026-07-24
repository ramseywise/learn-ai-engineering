---
origin: notion-export
confidence: medium
sources:
  - unknown (Notion notes, no URL captured)
cleaned: 2026-07-17
---

How to track the execution process of the Agent:

What needs to be recorded in the Trace:

```markdown
For each Agent run:

├── Complete Prompt, including system prompts

├── Complete messages[] for multiple rounds of interaction

├── Each tool call + parameters + return value

├── Inference chain, if thinking mode is present

├── Final output

└── Token consumption + latency
```

If possible, this system should also have semantic retrieval capabilities, able to query questions such as "which Trace Agents are obfuscating two tools", rather than just precise string matching. — this workflow automation

2 layers Observability  — can help to evaluator validation

1.  manual sampling and labeling. Based on rules, it samples error cases, long dialogues, and negative user feedback. Humans judge the execution quality and reasons for failure, primarily to identify failure patterns and provide calibration data for the second layer.
2. LLM as a judge, providing full coverage of a wider range of traces. It uses the labeling results from the first layer as the calibration basis. Running only the second layer makes the scoring criteria prone to drift, while relying solely on the first layer doesn't cover real-world traffic on a large scale. Both layers must be used together.

*(missing diagram — not exported from Notion)*
