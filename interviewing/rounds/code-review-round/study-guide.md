# Code Review Round — Study Guide

## Knowledge areas

### 1. Review methodology
What to know: a systematic, repeatable approach to reviewing code — not "read it and see if it looks right."

| Concept | Key point | Where to study |
|---------|-----------|---------------|
| Consequence-ranked reading | Security → correctness → maintainability → style | [README.md](README.md) §The method |
| Orient before judging | Understand intent (PR desc, contracts) before evaluating code | Google eng-practices: [The Standard](https://google.github.io/eng-practices/review/reviewer/standard.html) |
| The dangerous class | Changes that look innocent line-by-line but violate conventions | [conventions ex.1](examples/conventions.md) (SANYI BN-1 pattern); librarian wiki: Code Review Drill — SANYI |
| Contract-based review | Review the diff against declared contracts, not against taste | Librarian wiki: [SANYI Change-Contract System](sources.md) — three layers, violation codes, severity semantics |
| Scope management | When to push back on PR size, how to review large PRs | [questions.md](questions.md) Q3; Google eng-practices on [small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) |

### 2. Security & data boundaries (review first)
The highest-consequence review area. Interviewers watch whether you check these before anything else.

| Concept | What to look for | Example / source |
|---------|-----------------|-----------------|
| Auth/authz | Missing or inconsistent permission checks, role escalation | [security ex.3](examples/security.md) — decorator removal drops auth boundary |
| Input validation | Untrusted input reaching SQL, shell, file paths, template rendering | [security notes](../../notes/security.md) |
| Tool over-permissioning | Wildcard commands, write access where read suffices, credentials in metadata | [security ex.1](examples/security.md) — over-permissioned MCP tool config |
| Trust boundary violation | Untrusted content in system messages, retrieved docs as instructions | [security ex.2](examples/security.md) — untrusted content in system message |
| Memory poisoning | Unvalidated writes to persistent memory, no sanitization or TTL | [ai-generated ex.3](examples/ai-generated.md) — unvalidated memory writes |
| Irreversible operations | Deletes, writes, financial transactions without confirmation/audit | [correctness ex.2](examples/correctness.md) — swallowed error in agent loop |
| Source-sink analysis | Untrusted content → dangerous sink with authority = harm | [security guide §2](../../guides/7-security-safety/interview-guide.md) — the mental model interviewers reward |

### 3. Correctness & interfaces
The second review pass — does the code do what it claims?

| Concept | What to look for | Example / source |
|---------|-----------------|-----------------|
| Tool schema drift | Tool signature changed but schema not updated — agent can't call it | [correctness ex.1](examples/correctness.md) — agent breaks on missing parameter |
| Swallowed errors in loops | Agent receives fake success, compounds false signal across turns | [correctness ex.2](examples/correctness.md) — silent failure + denial-of-wallet |
| Schema/signature drift | Changed function signatures without updating all callers | [correctness ex.3](examples/correctness.md) — `name` → `firstName`/`lastName` |
| Cross-usage schema consistency | When a diff touches a *shared* schema/type, grep the whole repo for other usages — not just the diff's own callers, which is all a diff-scoped read naturally shows you | Parallax PR-review spec §18.2 — a downstream serializer can silently drop a renamed field on a shared response type with zero visible callers in the diff itself |
| Missing circuit breakers | No error counter, no max retries — failing tool causes infinite loop | [correctness ex.2](examples/correctness.md); [agents guide §5](../../guides/4-agents/interview-guide.md) |
| API contracts | Request/response shape matches documentation and callers' expectations | [correctness ex.3](examples/correctness.md) |
| Edge cases | Boundary values, off-by-one, unicode, timezone, large inputs | — |

### 4. Maintainability & conventions
Third pass — will the next person understand and safely modify this code?

| Concept | What to look for | Example / source |
|---------|-----------------|-----------------|
| Hardcoded tunables | Magic numbers, thresholds, URLs that should be config | [conventions ex.1](examples/conventions.md) — SANYI BN-1 pattern |
| Prompts hardcoded in code | Prompt strings inlined instead of in a loadable/swappable layer | [conventions ex.2](examples/conventions.md) — prompt moved from config to class attribute |
| Eval threshold changes | Quality bar lowered without calibration evidence or version bump | [conventions ex.3](examples/conventions.md) — pass threshold halved |
| Convention drift | Breaking established patterns without justification | SANYI Bianyi layer; [conventions ex.1](examples/conventions.md) |
| Test/eval quality | Tests exist, test the right things, break when the code breaks | [evals guide §2](../../guides/6-evals-observability/interview-guide.md) — grader types and calibration |
| Enforcement > documentation | Constraints in linters/types/CI, not prose docs agents ignore | [agent-harness notes](../../../ai-engineering/03-harness/agent-harness.md) — "encode invariants, don't micromanage implementations" |

### 5. Communication & feedback
Often weighted as heavily as technical skill in senior/staff rounds.

| Skill | How to demonstrate | Where to study |
|-------|-------------------|---------------|
| Severity labeling | Every comment is blocker / warning / nit — interviewer sees your calibration | SANYI severity semantics: invariant → blocker; entropy → warning; tunable → info |
| Severity vs. confidence | Two independent axes: consequence sets severity, evidence strength sets confidence (verified / supported / hypothesis) — a high-severity finding can still be low-confidence, and vice versa | [README.md](README.md) §The method, point 5; [questions.md](questions.md) Q5b; [Conventional Comments](https://conventionalcomments.org/) — `issue` vs `question`, labeled separately from `blocking`/`non-blocking` |
| Question framing | "What happens if X?" > "This is wrong" — a question is how you communicate a hypothesis, not a confidence tier of its own. Careful: a question can also just be an accusation in disguise ("Why did you use threads here when there's obviously no benefit?") — the goal is genuinely deferring to the author's context, not softened blame | [questions.md](questions.md) Q5, Q5b; [GitHub Staff Engineer's review philosophy](https://github.blog/developer-skills/github/how-to-review-code-effectively-a-github-staff-engineers-philosophy/) — dedicated "Ask questions" section, author has the most context; Google eng-practices on [reviewer comments](https://google.github.io/eng-practices/review/reviewer/comments.html) — comment on the code, not the developer (its own worked example rewrites an accusatory *question* into a direct, code-focused *statement* — question-phrasing isn't the point there, courtesy is) |
| Acknowledging good work | Call out smart decisions — shows you're not just hunting for problems | — |
| Proposing fixes | Don't just flag — suggest the mechanical fix or link the pattern | All examples include fix suggestions |
| Knowing when to stop | Don't flag pre-existing debt; don't nit style the linter handles | SANYI Debt baseline: "report news, not history" |

### 6. AI-generated code review (AIE-specific)
Increasingly tested — the volume of code to review has exploded.

| Concept | What to look for | Example / source |
|---------|-----------------|-----------------|
| Hallucinated APIs | Parameters/methods that look plausible but don't exist | [ai-generated ex.1](examples/ai-generated.md) — `normalize=True` on OpenAI embeddings |
| RAG quality blind spots | No relevance filtering, no attribution, no token budget | [ai-generated ex.2](examples/ai-generated.md) — "works in demo, fails in production" pipeline |
| Unvalidated memory writes | User input persisted without sanitization — poisoning vector | [ai-generated ex.3](examples/ai-generated.md) — OWASP bad example pattern |
| Intent vs. appearance | Code reads well but doesn't match the actual requirement | [ai-generated ex.1](examples/ai-generated.md) — `encoding_format` / return type mismatch |
| Convention drift | Each generation is independent — patterns diverge across a PR | [agents guide §4](../../guides/4-agents/interview-guide.md) — ACI principles apply to reviewing LLM output |
| Test coverage as safety net | Verify behavior, not just readability | [evals guide](../../guides/6-evals-observability/interview-guide.md) — trajectory vs outcome grading |
| Documented safeguards without code backing | A system prompt or doc claims a safety behavior (escalation path, input/output validation, confidence gate) — check whether it's backed by an actual deterministic code path, or exists only as a sentence the model can choose to ignore | Parallax PR-review spec §19.7 — same failure mode as a SANYI Buyi-invariant violation, just applied to an invariant nobody declared yet |

## Practice plan

1. **Weekly**: Review 2 merged OSS PRs blind (Next.js, FastAPI, or LangChain). Compare your findings with actual review comments.
2. **SANYI drill**: Work through the librarian wiki's Code Review Drill — SANYI page. It's the single best practice artifact for the contract-based method.
3. **Time yourself**: 5 min orientation (PR desc, contracts, file conventions) → 15 min deep review (consequence-ranked) → 5 min written summary with severity labels. Practice until the ordering is automatic.
4. **Prepare one story**: A time you caught something significant that automation missed. Use the [example 5](examples/) pattern as a template: small diff, lints clean, tests pass, convention violated.
5. **Know your linter boundary**: Be able to say "I wouldn't flag this in review — that's what the formatter handles" and explain why that's a maturity signal.
6. **Agent code review**: Practice reviewing tool permission configs, trust boundary handling, and memory validation in agent PRs. Use the OWASP Agent Security cheat sheet's good/bad examples.
7. **Read**: Google [eng-practices](https://google.github.io/eng-practices/review/) for the canonical approach; [Exponent guide](https://www.tryexponent.com/blog/how-to-ace-a-code-review) for interview-specific format and scoring; the [security guide](../../guides/7-security-safety/interview-guide.md) for the invariants you check first.
