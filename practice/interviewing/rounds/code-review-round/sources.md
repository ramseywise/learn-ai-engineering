# Code Review Round — Sources

## Internal

| Source | What it covers | Path |
|--------|---------------|------|
| Security & Safety study guide | The invariants you check first: threat model, defense stack, OWASP agent risks | [safety pillar](../../../../ai-engineering/09-safety-and-security/README.md) |
| Agents study guide | Harness conventions, tool design (ACI), SANYI contract discipline | [harness pillar](../../../../ai-engineering/03-harness-engineering/README.md) |
| Evals & Observability study guide | Grader types, trajectory vs outcome — what "tests pass" actually tests | [eval pillar](../../../../generative-ai/08-eval/README.md) |
| Context & Cost study guide | Convention drift, hardcoded tunables, progressive disclosure | [context pillar](../../../../ai-engineering/02-context-engineering/README.md) |
| Agent harness notes | Harness anatomy, OpenClaw 10 principles, enforcement > documentation | [Harness anatomy](../../../../ai-engineering/03-harness-engineering/notes/02-harness-anatomy.md) |

### Librarian wiki (query via `search_wiki`)

| Page | Relevance to code review |
|------|-------------------------|
| Code Review Drill — SANYI | The worked example: two-line diff that lints clean but violates change contract (BN-1 hardcoded tunable) |
| SANYI Change-Contract System | Full contract-based review framework: three layers (Bianyi/Jianyi/Buyi), violation codes, severity semantics |
| Input Guardrails Pipeline | What deterministic input validation looks like — the code you'd check in review |
| MCP Server Security Patterns | Security patterns for tool/server code — common review targets in agent codebases |
| Production Hardening Patterns | Reliability patterns (retries, fallbacks, state persistence) — what production-ready code should have |

## External

### Canonical references

| Source | What it covers | Link |
|--------|---------------|------|
| Google eng-practices — Code Review | The standard: what reviewers look for, how to navigate CLs, speed expectations | [google.github.io/eng-practices](https://google.github.io/eng-practices/review/) |
| Google eng-practices — CL Author's Guide | The other side: how to write reviewable code, respond to feedback | [eng-practices/developer](https://google.github.io/eng-practices/review/developer/) |
| 18F Code Review Interview Guide | Government hiring rubric for code review rounds — evaluation criteria, sample exercises | [guides.18f.gov](https://guides.18f.gov/eng-hiring/interviews/code-review/) |
| Augment Code Review Checklist | 40 questions before you approve — organized by correctness, security, performance, testing | [augmentcode.com](https://www.augmentcode.com/guides/code-review-checklist-40-questions-before-you-approve) |
| GitHub Staff Engineer's code review philosophy | Good-comment traits (specific, cites evidence, proposes a solution) and verifying assumptions by asking rather than asserting | [github.blog](https://github.blog/developer-skills/github/how-to-review-code-effectively-a-github-staff-engineers-philosophy/) |
| Conventional Comments | `issue`/`question`/`suggestion` comment-type taxonomy plus separate `blocking`/`non-blocking` labeling — the severity-vs-confidence split as a community convention | [conventionalcomments.org](https://conventionalcomments.org/) |

### Interview prep

| Source | Focus | Link |
|--------|-------|------|
| Exponent — How to Ace a Code Review Interview | Format walkthrough, what interviewers score, common mistakes | [tryexponent.com](https://www.tryexponent.com/blog/how-to-ace-a-code-review) |
| AlgoCademy — Mastering the Code Review Interview | Comprehensive guide: evaluation areas, practice strategies | [algocademy.com](https://algocademy.com/blog/mastering-the-code-review-interview-a-comprehensive-guide/) |
| IGotAnOffer — Google Code Review Interview | Google-specific format, scoring rubric, worked example | [igotanoffer.com](https://igotanoffer.com/en/advice/google-code-review-interview) |

### Deep dives

| Source | Topic | Link |
|--------|-------|------|
| OWASP AI Agent Security Cheat Sheet | Agent-specific risks: tool abuse, memory poisoning, privilege escalation, DoW | [owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) |
| OWASP Secure Code Review Guide | Security-focused review: injection, auth, crypto, error handling | [owasp.org](https://owasp.org/www-project-code-review-guide/) |
| Dr. Michaela Greiler — Code Reviews at Google | How Google's review process actually works — speed, lightweight, culture | [michaelagreiler.com](https://www.michaelagreiler.com/code-reviews-at-google/) |
| GetDX — Code Review Checklist | Structured checklist with security, performance, and testing sections | [getdx.com](https://getdx.com/blog/code-review-checklist/) |

## Practice material

- **OSS PRs**: Pick any active repo (Next.js, FastAPI, LangChain), find a merged PR with review comments, review the diff blind, then compare your findings with the actual review thread.
- **SANYI drill**: The librarian wiki's Code Review Drill — SANYI page has a real two-line diff with a full contract-based review walkthrough. Best single practice artifact for the method.
- **Own codebase**: Review recent commits in workspace repos against their `CLAUDE.md` conventions and `SANYI.md` contracts — practice finding convention drift in familiar code.
