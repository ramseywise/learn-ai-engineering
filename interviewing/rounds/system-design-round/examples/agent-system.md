# Example: Automated Code Review Agent

## Prompt
"Design an agent that reviews pull requests and posts review comments. It should catch bugs, security issues, and convention violations."

## Step 1: Clarify & scope (3 min)

**Questions I'd ask**:
- Scope: all PRs, or opt-in? Blocking (required approval) or advisory (comments only)?
- Codebase size/languages? Monorepo or multi-repo?
- Existing tooling: CI/CD pipeline? Linters/formatters already in place?
- What does "catch bugs" mean — static analysis level, or deeper semantic understanding?
- Human reviewer still involved, or is this a replacement?
- Latency: must comment before the human reviewer looks, or async is fine?

**Assumptions after clarify**:
- Advisory mode — agent posts comments, human makes approve/reject decision
- Multi-repo, Python + TypeScript
- CI/CD exists (linters, tests already run)
- Agent adds *semantic* review on top of automation — convention violations, security patterns, logic issues
- Must complete within 5 minutes of PR creation

## Step 2: Requirements (2 min)

**Functional**: Read PR diff + surrounding file context, identify issues by severity (blocker/warning/info/nit), post comments on specific lines, skip what linters already catch, learn repo-specific conventions.

**Non-functional**: < 5 min latency, false positive rate < 20% (reviewers will mute a noisy bot), cost < $0.50/PR, no access to secrets/credentials in the code it reads.

## Step 3: Design (15 min)

### Architecture
```
GitHub webhook (PR created/updated)
  → Queue (async processing)
  → PR Analyzer Agent:
      1. Fetch diff + file context (surrounding code, not just changed lines)
      2. Load repo conventions (CLAUDE.md, SANYI.md if exists, linter config)
      3. Consequence-ranked review passes:
         a. Security scan: auth patterns, injection vectors, secrets, trust boundaries
         b. Correctness: schema drift, error handling, null paths
         c. Conventions: hardcoded tunables, naming, pattern violations
         d. Skip: style (linter handles this)
      4. Severity assignment per finding
      5. De-duplicate against existing comments + linter output
      6. Post comments via GitHub API
```

### Key design decisions

**Single agent vs multi-agent**: Single agent with structured passes, not multiple specialized agents. At this scale (one PR at a time), the overhead of multi-agent coordination isn't justified. Each pass is a different prompt template, not a different agent.

**Context strategy**: Don't dump the entire PR into one prompt. For large PRs:
1. Classify files by risk (security-sensitive, interface changes, config changes, tests)
2. Review high-risk files with full surrounding context
3. Skim low-risk files (test fixtures, generated code) with minimal context
4. Token budget: ~8K tokens per file review, max 50K per PR

**Convention learning**: Load `CLAUDE.md` or similar repo-level instruction file as part of the system prompt. If the repo has a `SANYI.md`, review against declared contracts (this is the SANYI review mode). Fallback: infer conventions from the surrounding code (e.g., "all other thresholds in this file are env-driven").

**False positive management**: Track which comments get resolved vs dismissed by reviewers. Over time, weight down finding types that are frequently dismissed. Start conservative (high precision, lower recall).

### Trade-off narrated

**Quality vs speed**: Could run a larger model for deeper analysis but would exceed the 5-min budget on large PRs. Solution: use a fast model (Haiku/small Sonnet) for initial triage, escalate ambiguous findings to a larger model only when confidence is below threshold. Most PRs are small enough that the fast model suffices.

**Full context vs token budget**: Including the entire file for every changed line would blow the context window. Solution: include changed lines + 50 lines of surrounding context + file-level imports/declarations. Accept that some cross-file issues will be missed — flag them as a known limitation rather than trying to load the entire repo.

### Sidecars
- **Eval**: Golden set of 50 PRs with known issues (manually labeled). Run weekly: precision, recall, severity calibration.
- **Feedback loop**: "Was this comment helpful?" reaction on each comment → feeds into eval set and false-positive weighting.
- **Cost tracking**: Token usage per PR, model selection impact on spend.
- **Audit**: Log every review with findings, model used, and token count.

## Step 4: Shortcomings (3 min)

- **Cross-repo context**: Can't see how callers in other repos use the changed interface. Mitigation: flag interface changes as "check downstream consumers" rather than asserting they're broken.
- **False negatives**: Will miss subtle logic bugs that require deep domain knowledge. This is advisory, not a replacement for human review.
- **Convention drift**: If repo conventions change and CLAUDE.md isn't updated, the agent reviews against stale standards. Mitigation: periodically prompt maintainers to update.
- **Gaming**: Developers could learn to write code that passes the agent but is still problematic. Mitigation: rotate prompt templates, add new finding types over time.

## Step 5: Close with measurement (2 min)

**Metrics**: Precision > 80% (< 20% false positive), recall on security findings > 90% (never miss an auth issue), p95 < 5 min, cost < $0.50/PR, reviewer time saved per PR.

**Future**: Convention learning from merged PR history (what do senior reviewers actually flag?), integration with SANYI contract system for automated change-contract enforcement, aggregated codebase-health dashboard from review findings.

---

**Study refs**: [agents guide §1-4](../../../guides/4-agents/interview-guide.md) for workflow vs agent decision; [code-review round](../../code-review-round/) for the review method the agent implements; SANYI wiki pages for contract-based review.
