---
origin: notion-export
confidence: medium
sources:
  - https://medium.com/data-science-collective/how-to-build-production-ready-ai-engineering-projects-3142a88f06ea
  - https://ai.gopubby.com/agentic-ai-security-patterns-ad4ff80b9351
cleaned: 2026-07-17
---

### Agents:

https://medium.com/data-science-collective/how-to-build-production-ready-ai-engineering-projects-3142a88f06ea

- Error handling: LLMs make mistakes. Your agent needs to handle this gracefully. What happens when a tool call fails? Does the agent retry? Try a different approach? You need explicit error handling logic for all of these cases.
- Security: If your agent can execute code or call APIs, you have security concerns. Don’t blindly execute whatever the LLM decides to do — validate inputs to tools. If your agent runs code, run it in a container or sandbox. Limit what your agent can access.
- Preventing infinite loops: Agents can get stuck trying the same failed action repeatedly. You need max iterations to stop after N steps, loop detection to catch repeated actions, and cost budgets to stop if token usage exceeds a threshold.
- Monitoring agent behavior: Log everything your agent does: what tools it called, what the outputs were, what decisions it made at each step, how long each step took, and where it succeeded or failed. This lets you debug when things go wrong and improve your agent over time.

for agents evals: Evals

### Guardrails:

https://medium.com/data-science-collective/ai-agents-complete-course-f226aa4550a1

Guardrails are basically a quality gate between what the agent says is done and the task actually being finalized.

three main approaches to guardrails, and most production systems use at least two:

1. standard code snippets:  for deterministic stuff like output format and length — fast and cheap and should be preferred when possible.

    *(missing diagram — not exported from Notion)*

2. LLM as a judge: more nuanced things like “Is this response factually consistent with the sources?”

    If the LLM judge says “no, this fails,” it explains why. That feedback gets sent back to your agent, and the agent revises and tries again.

    *(missing diagram — not exported from Notion)*

3. HITL: make it stop and ask for approval first. You can give feedback and ask the agent to try again.

### Common bad Patterns in Agent Deployment

These problems are very common. Many seem to indicate insufficient model capabilities, but in retrospect, they stem from inadequate engineering constraints:

1. System prompts as a knowledge base: The system becomes increasingly long, key rules are ignored, conventions should be used for prompts, and knowledge should be moved to Skills.
2. Uncontrolled number of tools: Agents frequently choose the wrong tools; merge overlapping tools and define clear namespaces.
3. Lack of verification loop: Agents claim completion but cannot verify it; assign acceptance criteria to each task type.
4. Boundaryless multi-agent system: State drift, difficulty in attributing failures; define roles and permissions, and use a worktree for isolation.
5. Inconsistent memory: Decision quality declines after the 20th round of long dialogues; monitor tokens and automatically trigger thresholds.
6. Lack of evaluation: It's unclear whether changes have introduced regression testing; failure cases are immediately converted to test cases.
7. Premature introduction of multiple agents: Coordination overhead exceeds parallel benefits; verify the single-agent limit before scaling.
8. Constraints based on expectations rather than mechanisms: Rules in documentation are selectively followed by agents; use tools for verification/Linter/Hook.


https://ai.gopubby.com/agentic-ai-security-patterns-ad4ff80b9351

*(missing diagram — not exported from Notion)*

with logging, observability, and responsible AI guardrails.

security risks:

- R1: Misaligned & Deceptive Behaviors (Dynamic Deception)
- R2: Intent Breaking & Goal Manipulation (Goal Misalignment)
- R3: Tool Misuse (Tool/ API Misuse)
- R4: Memory Poisoning (Agent Persistence)
- R5: Cascading Hallucination Attacks (Cascading System Attacks)

(**Security** Vulnerabilities)

- R6: Privilege Compromise
- R7: Identity Spoofing & Impersonation
- R8: Unexpected RCE & Code Attacks

(Operational **Resilience**)

- R9: Resource Overload
- R10: Repudiation & Untraceability

(Multi-agent **Collusion**)

- R11: Rogue Agents in Multi-agent Systems
- R12: Agent Communication Poisoning
- R13: Human Attacks on Multi-agent Systems

(Human **Oversight**)

- R14: Human Manipulation
- R15: Overwhelming Human in the Loop
- R16: (Persona-driven Bias)

从风险缓解的角度来看，有趣的是，风险缓解通常交给中央**监管层**来负责。然而，这并不现实。

> *防护措施需要针对具体的底层用例，并在各自的平台组件/层中实施——这会对整体解决方案架构产生直接影响。*
>

图 7 展示了智能 AI 组件的风险架构映射。

按回车键或点击查看完整尺寸的图片

*(missing diagram — not exported from Notion)*


- durable messaging
- explicit task state
- dependency tracking
- idempotent processing
- isolated side effects
- structured handoffs
- deterministic verification
