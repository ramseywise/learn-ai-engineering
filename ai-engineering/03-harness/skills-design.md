---
origin: web-authored
sources:
  - https://developers.openai.com/blog/skills-shell-tips
confidence: high
cleaned: 2026-07-29
---
# Skills Design

> Relocated from `02-context/context-engineering.md` (2026-07-29) — skills are a harness primitive, not a context-composition technique. The *progressive disclosure* mechanism they rely on belongs to context engineering; the design of the skills themselves belongs here.

---

## What a skill is

A packaged procedure the agent loads on demand: a name, a description, and a body of instructions, templates, and examples. Only the name and description stay resident in the context window; the body loads when the task activates it.

That split is why skills work — see [02-context/notes/02](../02-context/notes/02-context-anatomy.md#layer-2--on-demand-knowledge) for the progressive-disclosure mechanism and [02-context/notes/05](../02-context/notes/05-memory-as-context.md#index-plus-detail) for the same pattern applied to memory.

---

## 1. Write descriptions as routing logic

The description is not documentation. It is the routing decision — the only text available when the agent decides whether to load the skill. Write it to answer:

- When should I use this?
- When should I *not* use this?
- What are the outputs and success criteria?

Two constraints pull against each other: **token cost** (descriptions are resident in every window) and **routing precision**. Terse wins.

```markdown
# bad (~45 tokens)
description: |
  This skill handles the complete deployment process to production.
  It covers environment checks, rollback procedures, and post-deploy
  verification. Use this before deploying any code to production.

# good (~9 tokens)
description: Use when deploying to production or rolling back.
```

The bad version spends 5× the tokens to convey the same routing signal. The details it lists belong in the body, which loads only when the skill fires.

---

## 2. Add negative examples and edge cases

Misfires — a skill loading when it shouldn't — cost a full body load plus a wrong-track start. Reduce them explicitly:

```markdown
Don't call this skill when… (and what to do instead).
```

Negative examples are higher-leverage than positive ones, because the positive case is usually obvious from the name and the negative case never is.

---

## 3. Put templates and examples inside the skill

They are effectively free when unused — the body only loads on activation. This makes skills the right home for material too bulky to keep resident.

Especially effective for knowledge-work outputs with a consistent shape:

- Structured reports
- Escalation triage summaries
- Account plans
- Data analysis writeups

A worked example in the body beats a paragraph describing the desired format.

---

## 4. Design for long runs early

Container reuse and compaction are cheaper to build in than to retrofit. A skill that will run for more than a few minutes needs to assume it will be interrupted — write progress to disk, resume from checkpoint. See [02-context/notes/04](../02-context/notes/04-compression-compaction.md#crash-recovery).

---

## 5. For determinism, invoke explicitly

Model-driven routing is probabilistic. When a skill must run, say so:

```markdown
Use the <skill name> skill.
```

The general principle from [02-context/notes/02](../02-context/notes/02-context-anatomy.md#layer-5--deterministic-system): behavior that must be reliable belongs in code or explicit instruction, not in a description hoping to win a routing decision.

---

## 6. Skills plus networking is a high-risk combination

The security tip that is easy to gloss over and hard to fix later.

Skills make procedures more capable. Network access makes exfiltration possible. Together they form a data-exfiltration path — a skill body is instructions the agent follows, and a compromised or injected instruction with network reach can move data out.

Defensible default posture:

- Skills: **allowed**
- Shell: **allowed**
- Network: **enabled only with a minimal allowlist**, per request, for narrowly scoped tasks

Assume tool output is untrusted. Avoid combining open internet access with powerful procedures in consumer-facing flows where users expect strong confirmation controls.

See [02-context/notes/07](../02-context/notes/07-context-failure-modes.md#prompt-injection) and [agents-guardrails.md](agents-guardrails.md).

---

## Working reference

`~/.claude/refs/agent-tools.md` — tool schema rules and the promote-from-bash heuristic; skills and tools face the same description-as-routing-logic problem.
`~/.claude/refs/agent-safety.md` — five protection layers, egress control.
