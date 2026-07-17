# Security & Safety — Study Guide

Every serious agent/LLM design question ends with "…and how do you make it safe?" FDE loops
add compliance framing (banking, healthcare). Anchor answers in the OWASP AI Agent Security
and Prompt Injection cheat sheets — citing them by name lands well.

## 1. Threat model (name risks precisely)

**Prompt injection** — untrusted text entering the system carries instructions that override
the system's. Two forms: **direct** (user input) and **indirect** (retrieved docs, webpages,
emails, tool outputs). Attack techniques worth knowing by name: encoding/obfuscation,
typoglycemia, Best-of-N jailbreaking, HTML/markdown injection, multi-turn persistence,
system-prompt extraction, **RAG poisoning** (malicious content planted in the corpus),
multimodal injection (instructions in images).

**Agent-specific risks** (OWASP list): tool abuse & privilege escalation · data exfiltration
via tool calls · **memory poisoning** (malicious data persisted to influence future
sessions) · goal hijacking · excessive autonomy · high-impact action abuse · approval
manipulation (gaming risk scores/thresholds) · cascading failures across multi-agent
systems · **denial-of-wallet** (unbounded loops burning API spend) · supply-chain attacks
via third-party tools/MCP servers.

Plus the non-adversarial failure: **accidental private-data leakage** — a model can leak
data with no attacker involved (over-broad MCP access is a typical path).

## 2. The mental model interviewers reward: source → sink

Don't promise to *detect* every injection — you can't. Analyze the path:

- **Source**: where untrusted content enters (email, webpage, document, tool output,
  retrieved chunk).
- **Sink**: high-impact action it could influence (send data, modify files, call API,
  execute commands).

**Goal: untrusted content never reaches a dangerous sink with enough authority to cause
harm.** Design so that even successful manipulation has bounded impact.

## 3. Defense stack (layered — walk it in order)

1. **Input guardrails** — deterministic pipeline first (regex/classifiers for PII,
   jailbreak patterns); LLM-free by design where possible: fast, cheap, auditable.
2. **Separation of trust** — untrusted content goes in user-role messages, never developer/
   system messages; wrap it in explicit markers (`<untrusted_content source="webpage">`)
   so the model can treat it as data, not instructions.
3. **Structured outputs** — schema-constrained responses shrink the injection surface and
   make output validation mechanical.
4. **Least privilege** — minimum tools per agent; per-tool permission scoping (read-only vs
   write, resource allowlists); separate tool sets per trust level; scoped MCP configs
   (never over-permissioned servers).
5. **HITL for sensitive actions** — classify actions by impact; irreversible/financial/
   externally-visible operations require approval.
6. **Independent verification / dual-LLM pattern** — a verifier model receives only the
   proposed action + policy + evidence, *not* the contaminated context; strongest form: the
   model that reads untrusted content has no tools, and the model with tools never reads raw
   untrusted content.
7. **Memory hygiene** — validate before persisting; never store arbitrary user input in
   long-term memory (poisoning vector); isolate memory per user/tenant.
8. **Output validation** — moderation/toxicity screens, PII redaction on the way out,
   citation/grounding checks.
9. **Trace graders in production** — safety evals run continuously, not just pre-launch.

## 4. Operational boundaries (from production notes)

Three things before an agent ships: **who can trigger it** (allowlist authorization),
**where it can act** (workspace isolation — shell tools path-check and error outside the
workspace), **what it did** (append-only audit log per execution). Add circuit breakers
(fail-max + reset timeout) and per-user/tenant token quotas against abuse and
denial-of-wallet. Skills + open network access is a high-risk exfiltration combo: strict
network allowlists, per-request, for narrowly scoped tasks.

## 5. Compliance quick answers (FDE/enterprise rounds)

- **GDPR**: data deletion, transparency, EU residency → self-hostable observability
  (Langfuse), prompt/response logging with opt-out, PII masking before traces leave.
- **HIPAA / PCI-DSS**: PHI/cardholder isolation; no third-party model calls without BAAs /
  scoping; on-prem or private endpoints for regulated data.
- **SOC 2 / ISO 27001**: audit logs, access control, "why did you say that?" explainability
  surface.
- PII masking approaches: regex (fast, misses context) vs NER models vs LLM-based vs hybrid
  — contextual PII ("my neighbor John from apartment 4B") is the hard case.

## 6. Reliability = safety's twin (error handling & recovery)

From the PRINCE case study: persist workflow state per node (checkpointer) so recovery
resumes from the failed step, not from scratch · retries at both LLM-call and node level ·
LLM fallback chains across providers · feed error context back to the agent so it replans ·
user-initiated retry that skips completed steps. Degradation ladder: retry → fallback model
→ simpler baseline → human. Graceful streaming failure: close with an error event, never
hang.

## 7. Question bank (answer sketches)

- *"Design a secure banking-support chatbot."* — trust separation + strict data access
  controls (RLS/tenant scoping), contextual retrieval from approved corpora only, anonymized
  session memory, PCI-DSS + human fallback, output PII redaction, full audit trail. Lead
  with governance layers.
- *"How do you prevent prompt injection?"* — reframe: you *contain* it. Source–sink analysis,
  trust separation, least-privilege sinks, dual-LLM/verifier for high-impact actions,
  continuous adversarial evals. Detection-only answers are wrong answers.
- *"Your agent has shell access — now what?"* — workspace isolation + path checks, command
  allowlists, sandbox execution, audit log, HITL for destructive ops, quotas.
- *"RAG poisoning?"* — corpus admission control (who can write), source confidence tiers,
  grounding checks at generation, anomaly monitoring on retrieval distributions.
- *"What's different about multi-agent security?"* — every handoff is an injection surface;
  authenticate inter-agent messages, verify provenance, isolate boundaries so one
  compromised agent can't cascade.

## Sources

- notes: [security.md](../notes/security.md) (OWASP agent cheat sheet + source–sink + PRINCE recovery), [prompt-injection.md](../notes/prompt-injection.md) (OWASP injection cheat sheet), [agents-guardrails.md](../notes/agents-guardrails.md)
- librarian wiki: Input Guardrails Pipeline · MCP Server Security Patterns · PII Masking Approaches · Presidio PII Redaction · Production Hardening Patterns
- external: OWASP AI Agent Security Cheat Sheet · OWASP LLM Prompt Injection Prevention Cheat Sheet · martinfowler.com/articles/reliable-llm-bayer.html
- readings: `general/` (Constitutional AI, TruthfulQA)
