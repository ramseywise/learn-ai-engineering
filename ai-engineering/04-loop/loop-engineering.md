---
origin: notion-export
confidence: medium
sources:
  - https://www.langchain.com/blog/the-art-of-loop-engineering
  - https://claude.com/blog/getting-started-with-loops
  - https://levelup.gitconnected.com/what-is-loop-engineering-how-it-is-different-than-harness-engineering-0e764f373fb1
cleaned: 2026-07-17
---

https://www.langchain.com/blog/the-art-of-loop-engineering

https://claude.com/blog/getting-started-with-loops

https://levelup.gitconnected.com/what-is-loop-engineering-how-it-is-different-than-harness-engineering-0e764f373fb1

from https://www.langchain.com/blog/the-art-of-loop-engineering

**Level 1: Agent loop**

*(missing diagram — not exported from Notion)*

*(missing diagram — not exported from Notion)*

**Level 2: Verification loop - evals and rollback if fails**

When consistency matters, it's often useful to wrap it in a verification loop that checks the output and sends feedback back to the model when it falls short.

*(missing diagram — not exported from Notion)*

*(missing diagram — not exported from Notion)*

One tradeoff: adding verification increases latency and cost per run. It's worth it when quality matters more than speed, which is most production use cases.

**Level 3: Event driven loop**

integrations layer: connecting your agent to your ecosystem so that it can run in the background.

this loop connects your agent to your ecosystem.

the agent runs continuously inside a larger system.

*(missing diagram — not exported from Notion)*

*(missing diagram — not exported from Notion)*

**Level 4: Hill climbing loop — self improving - distinct from harness engineering**

The first three loops automate work. The fourth (and arguably most important) automates improvement!

*(missing diagram — not exported from Notion)*

*(missing diagram — not exported from Notion)*

agent running trace → analysis it (analysis agent) → rewrite harness with improved configs (prompt/tool tweaks or grader tweaks ects.)

analysis agent in LangSmith: https://www.langchain.com/langsmith/engine
