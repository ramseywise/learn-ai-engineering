# Code Review Round — Questions & Model Answers

## Format note
In a code review interview, the "question" is usually the code itself — you're handed a diff/PR and asked to review it. The questions below are either prompts the interviewer gives alongside the code, or follow-up questions after your review. Answers are grounded in the [study guide](study-guide.md) and [sources](sources.md).

---

## Q1: "Review this PR."

**What they're testing**: Do you have a method, or do you just read top-to-bottom?

**Model answer structure**:
1. Read the PR description first — state what the change is supposed to do
2. Scan for the contracts/invariants the touched code declares (types, schemas, auth boundaries)
3. Review in consequence order: security/data → correctness/interfaces → maintainability → style
4. Deliver findings ranked by severity (blocker → warning → info → nit)
5. End with a summary: "I'd approve with [X] addressed, [Y] is a nit"

**Signal**: You narrate your reading order out loud. Interviewer sees your prioritization.

**Study ref**: [README.md](README.md) §The method; [study guide §1](study-guide.md) on review methodology; the SANYI drill (librarian wiki) is a worked version of this exact exercise.

---

## Q2: "The tests pass and it lints clean — approve?"

**What they're testing**: Do you understand the gap between automated checks and human review?

**Model answer**: "Passing checks verify what's *encoded*, not what's *intended*. I'd still look for:
- Contract/convention violations that no test covers — a hardcoded value where there should be a config (the [BN-1 pattern](examples/conventions.md)), a safety check wrapped in a flag
- Missing test cases for edge conditions the author may not have considered
- Interface drift — does this change match what callers expect? (see [correctness examples](examples/correctness.md))
- Security boundaries — auth, tool permissions, trust separation (see [security examples](examples/security.md))

Automation handles syntax and formatting. Human review handles intent, conventions, and consequences."

**Study ref**: [study guide §1](study-guide.md) — the dangerous class; [evals guide §2](../../guides/6-evals-observability/interview-guide.md) on grader types (what code tests can and can't verify).

---

## Q3: "How do you review a 2,000-line PR?"

**What they're testing**: Pragmatism, communication skills, risk management.

**Model answer**: "First, I'd push back — ask if it can be split into smaller, reviewable units. If it can't (migration, large refactor), I'd:
1. Read the PR description and any linked design doc
2. Identify the high-risk files: entry points, data writes, auth/security boundaries, interface changes
3. Review those thoroughly, in consequence order
4. Skim the rest for convention breaks and obvious issues
5. Timebox style feedback to zero — that's what linters are for
6. Be explicit about what I reviewed deeply vs. skimmed: 'I focused on the auth changes and the new API surface; I skimmed the test fixtures'

The worst thing is pretending you reviewed everything carefully when you didn't."

**Study ref**: Google eng-practices on [CL size](https://google.github.io/eng-practices/review/developer/small-cls.html); [study guide §1](study-guide.md) on scope management.

---

## Q4: "A senior engineer disagrees with your blocker."

**What they're testing**: Conflict resolution, conviction vs. flexibility.

**Model answer**: "I'd restate the *consequence*, not the *rule*. 'My concern is that if [specific scenario], this will [specific bad outcome].' If they have context I'm missing — maybe there's a guard upstream I didn't see — I'd update my assessment. If the risk is real but they want to ship anyway, I'd propose: downgrade to a warning with a follow-up ticket, and document the known risk. I'd never block on taste, only on consequence.

Worth separating two things that are easy to conflate here: how severe the underlying issue is, and whether it blocks *this* merge. Those are two independent axes — the code's severity doesn't change just because we decide to ship anyway; what changes is the merge decision, made consciously, with the risk documented. I'm not lowering my assessment of the bug to placate them; I'm agreeing to accept a known risk for now."

**Study ref**: SANYI severity semantics — severity comes from the layer, not the reviewer's mood. Invariant touched → blocker; tunable made rigid → info. See the [SANYI wiki page](sources.md) violation codes table. Overlap with [behavioral round](../behavioral/).

---

## Q5: "What makes a review comment good?"

**What they're testing**: Communication maturity, empathy.

**Model answer**: A good review comment is:
- **Specific**: points to the exact line and the exact concern
- **Actionable**: includes or suggests the fix, not just the problem
- **Severity-labeled**: blocker, warning, nit — so the author knows what must change vs. what's optional
- **Question-phrased where possible**: "What happens if this input is empty?" invites dialogue; "This is wrong" shuts it down
- **Acknowledges good decisions**: "Nice catch handling the nil case here" — reviewing is mentoring, not gatekeeping

**Study ref**: [study guide §5](study-guide.md) on communication; Google eng-practices on [reviewer comments](https://google.github.io/eng-practices/review/reviewer/comments.html).

---

## Q5b: "How do you distinguish a confirmed bug from a plausible concern during PR review?"

**What they're testing**: Whether you overstate confidence — a common tell of reviewers who pattern-match rather than verify, and a direct risk when reviewing LLM-generated code where plausible-looking claims are cheap to produce. Also tests whether you conflate "how bad" with "how sure" — two independent judgments that are easy to blur under pressure.

**Model answer**: "I separate severity from confidence. Severity describes the consequence if the issue is real — blocker, warning, or nit. Confidence describes how strongly the available evidence supports the claim, independent of severity: a suspected data leak can be high-severity but low-confidence until I've actually traced the path; a misspelled variable is high-confidence but low-severity. Collapsing the two is how reviewers either cry wolf on hunches or bury a serious-but-unconfirmed risk under a nit label.

For confidence specifically, I use three levels:
- **Verified** — I reproduced it, or traced the failure conclusively through the full code path. I state it directly: 'This retries after the external write, so a timeout after success duplicates the side effect.'
- **Supported** — the code path or documented behavior strongly indicates it, but I haven't reproduced it directly (e.g., I'm assuming the downstream API isn't idempotent, based on its docs). I say what's still assumed.
- **Hypothesis** — a plausible failure mechanism, but key context is still missing. For a hypothesis, especially a high-severity one, I explain the mechanism and ask a targeted question or suggest a test instead of presenting it as a confirmed bug: 'This could double-charge if the provider retries — worth checking?' beats asserting 'this double-charges.'

Note that a question isn't a fourth confidence tier — it's how I *communicate* a hypothesis (or any judgment I can't make without more context), not a level of evidence in itself."

**Study ref**: [README.md](README.md) §The method, point 5 (confidence as a second, independent axis from severity); Google eng-practices — [The Standard](https://google.github.io/eng-practices/review/reviewer/standard.html) prioritizes technical facts and data over personal preference, and separates non-blocking nits explicitly; [GitHub Staff Engineer's code review philosophy](https://github.blog/developer-skills/github/how-to-review-code-effectively-a-github-staff-engineers-philosophy/) — good comments cite evidence or reasoning, and uncertain judgments get verified by asking rather than asserting; [Conventional Comments](https://conventionalcomments.org/) — separates `issue` (confirmed problem) from `question` (not sure it's even a problem), and separately labels `blocking`/`non-blocking` — the same two-axis split, arrived at independently.

---

## Q6: "How do you review AI-generated code?" (AIE-specific)

**What they're testing**: Whether you've thought about the 2026 review landscape.

**Model answer**: "AI-generated code has specific failure modes:
- **Hallucinated APIs** — functions/parameters that look right but don't exist (see [ai-generated examples](examples/ai-generated.md))
- **Plausible but wrong logic** — the code reads well but doesn't match the actual intent
- **Missing edge cases** — LLMs optimize for the happy path
- **Convention drift** — each generation is independent, so style/pattern consistency breaks across a PR
- **Over-engineering** — unnecessary abstraction, error handling for impossible cases

My approach: verify behavior against *intent* (not just 'does it read well?'), check every API call against actual docs, insist on test coverage as the safety net, and look for convention drift across the PR. The review skill matters more now, not less — the volume of reviewable code has exploded."

**Study ref**: [study guide §6](study-guide.md) on AI-generated code review; [agents guide §4](../../guides/4-agents/interview-guide.md) on ACI — tool descriptions written for junior devs maps directly to reviewing AI output.

---

## Q7: "Walk me through a time you caught something significant in review."

**What they're testing**: Real experience, storytelling, consequence-awareness.

**Prep**: Have one story ready. Best format:
1. What the change was (one sentence)
2. What looked fine on the surface
3. What you caught and *how* (the method that surfaced it)
4. What the consequence would have been
5. How you communicated it

The ideal story: a small diff that linted clean and tests passed, but violated a convention or invariant. The SANYI drill (a two-line diff adding a hardcoded threshold where all other thresholds are env-driven) is a strong template for this story — shows that your method catches what automation misses.

**Study ref**: [conventions ex.1](examples/conventions.md) walks through this exact pattern; the [Code Review Drill — SANYI](sources.md) wiki page is the full version.

---

## Q8: "What would you check first in an agent/LLM system PR?" (AIE-specific)

**What they're testing**: Whether you know agent-specific security and reliability risks.

**Model answer**: "Agent code has unique review priorities:
1. **Tool permissions** — does this agent/MCP server have minimum necessary access? Over-permissioned tools are the #1 agent security risk (OWASP). Check for wildcard permissions, missing allowlists.
2. **Trust boundaries** — is untrusted content (user input, retrieved docs, tool outputs) separated from system instructions? Look for user content in developer messages.
3. **Irreversible actions** — anything that sends data, modifies external state, or costs money needs HITL or at minimum explicit confirmation.
4. **Memory writes** — is data validated before persisting? Unvalidated memory storage is a poisoning vector.
5. **Error handling** — does a failure in one step cascade or get silently swallowed? Agent loops need explicit recovery paths.
6. **Prompt/config tunables** — are thresholds and prompts changeable without a deploy, or hardcoded in business logic?
7. **Documented safeguards without code backing** — if the system prompt, a doc, or a config comment *claims* a safety behavior exists (an escalation path, a confidence gate, an input/output validator), I go check whether there's an actual deterministic code path enforcing it, or whether it's just a sentence the model can choose to ignore under the right adversarial input. This is the one I'd expect a line-by-line reviewer to miss — the prompt text reads as if the safeguard exists."

**Study ref**: [security guide §3-4](../../guides/7-security-safety/interview-guide.md) on defense stack and operational boundaries; [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html); SANYI Buyi layer for invariants that must be code-enforced.
