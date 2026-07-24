# Pillar 7 — Security & Safety (prompt injection, guardrails, PII)

The adversarial pillar: what happens when inputs are hostile, outputs are harmful, or
data is sensitive. This repo's notes are unusually strong here (deeper than the librarian
wiki) — prompt injection mechanics, agent threat models, and the guardrail patterns that
actually hold.

## Learning path

1. **The core attack** — [prompt-injection.md](../../../ai-engineering/01-prompt/prompt-injection.md): the
   source–sink model (untrusted content flowing to privileged actions), why "just prompt
   it not to" fails, the dual-LLM pattern.
2. **The threat landscape** — [security.md](../../notes/security.md): OWASP AI Agent
   Security taxonomy; OWASP cheat-sheet links in
   [reading-list.md](../../notes/reading-list.md).
3. **Defenses in layers** — [agents-guardrails.md](../../../ai-engineering/03-harness/agents-guardrails.md) +
   librarian *Input Guardrails Pipeline*: templating, content boundaries, sanitizers,
   moderation, output validation — and what each layer misses.
4. **Agentic protection** — *Protecting Agentic Systems* (agent-applications book ch 12)
   + *Setting Safeguards* (design-patterns book ch 9,
   `ai-engineering/readings/ai_engineering/ai design/`); MCP-specific: librarian *MCP Server Security
   Patterns*.
5. **Compliance reality** — PII handling, GDPR/HIPAA constraints, governance layers —
   the banking-chatbot worked example in [case-interview.md](../../notes/case-interview.md)
   is the interview-shaped version.

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| prompt-injection.md · agents-guardrails.md | note | [ai-engineering/01-prompt/](../../../ai-engineering/01-prompt/) · [ai-engineering/03-harness/](../../../ai-engineering/03-harness/) | the pillar's primary depth (wiki gap) |
| security.md | note | [../../notes/security.md](../../notes/security.md) | OWASP AI Agent taxonomy |
| *Building Applications with AI Agents* ch 12 | pdf | `ai-engineering/readings/ai_engineering/ai_agent_applications/` | protecting agentic systems |
| *Generative AI Design Patterns* ch 9 | pdf | `ai-engineering/readings/ai_engineering/ai design/` | safeguard patterns |
| Constitutional AI (2212.08073) | pdf | `generative-ai/01-llm-fundamentals/readings/` | principle-guided harmlessness training |
| Input Guardrails Pipeline · MCP Server Security Patterns · PII pages | wiki | librarian | deployed defense patterns |
| OWASP LLM Top-10 + cheat sheets | link | [../../notes/reading-list.md](../../notes/reading-list.md) | the standard taxonomy |

## Test yourself
[interview-guide.md](interview-guide.md) · rounds:
[system-design-round](../../rounds/system-design-round/README.md) (governance layers in
regulated designs), [technical-questions](../../rounds/technical-questions/README.md).
