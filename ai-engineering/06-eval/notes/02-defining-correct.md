---
origin: synthesis
sources:
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - https://hamel.dev/blog/posts/field-guide/
  - https://arxiv.org/abs/2404.12272
  - case-study/gate-contract.md
confidence: high
cleaned: 2026-10-28
---
# 2 — Defining "Correct"

> Most eval problems are specification problems. If two experts can't agree on whether an output passes, no grader will either. Write success down first, and find your failure modes by reading outputs, not by guessing.

---

## Success criteria before code

Before collecting data or writing a grader, answer four questions in writing:

| Question | Bad answer | Good answer |
|---|---|---|
| What does the user need? | "A helpful answer" | "The steps to change their payout account, in their language, citing the help article" |
| What must never happen? | "Nothing bad" | "Inventing a menu path. Revealing another customer's data. Answering a legal question instead of escalating" |
| What's the unit of success? | "The conversation went well" | "Per turn: grounded and complete. Per conversation: resolved without escalation in ≤ 6 turns" |
| What does it cost to be wrong? | — | "A wrong menu path costs a support ticket. A wrong tax answer costs a fine" |

The fourth answer sets your thresholds. A system where errors are cheap can ship at a 90% pass rate. One where errors are expensive needs a lower rate plus a fallback path ([11](11-production-and-the-maturity-ladder.md)).

### The two-expert test

Anthropic's rule for a good task: **two domain experts would independently reach the same pass/fail verdict.** If they wouldn't, the ambiguity in the spec becomes noise in your metric, and no amount of grader tuning removes it.

Run the test literally. Give 20 outputs to two people with your written criteria and compare their verdicts. Where they disagree, the criteria are the problem, not the people. Fix the criteria, then build the grader.

---

## Find failure modes by reading: error analysis

You can't list failure modes in advance. You find them by reading outputs. The method Husain and Shankar teach (borrowed from qualitative research):

1. **Collect ~100 traces.** Real ones if you have them, synthetic if you don't yet ([03](03-eval-datasets.md#synthetic-data-done-right)).
2. **Open coding.** Read each trace and write a short free-text note on the *first* thing that went wrong. Don't use categories yet. "Cited the 2023 pricing page", "asked for the order ID it already had".
3. **Axial coding.** Group the notes into categories. "Stale source", "ignored context", "wrong tool". Expect 5–15.
4. **Count.** Rank categories by frequency × cost. That ranking is your eval roadmap: build graders for the top few first.
5. **Repeat** until new traces stop producing new categories (theoretical saturation, usually 50–100 traces).

Note the *first* failure only. Later failures in a trajectory are often caused by the first, and counting them inflates the wrong category.

> **Don't build a grader for a failure mode you haven't seen.** Generic metrics ("helpfulness", "coherence") measure something, but rarely the thing that's actually going wrong in your system.

### One person decides

Husain recommends a single domain expert as the final word on what counts as a pass (the "benevolent dictator"). Committees produce vague criteria. One accountable person with domain knowledge produces sharp ones. Other people can contribute traces and argue cases; one person rules.

### Criteria drift

Shankar et al. ("Who Validates the Validators?", 2024) found that people's criteria *change as they grade*: reading outputs reveals requirements nobody wrote down. That's not a flaw to eliminate. It's how you discover the spec. Plan for it: version your criteria, and re-grade earlier samples when they change.

---

## The failure taxonomy

The output of error analysis is a **failure taxonomy**: a fixed set of labels for the ways your system fails. It becomes the shared vocabulary for graders, dashboards, reports and bug tickets.

Rules for a usable taxonomy:

- **Stable names.** `rank_miss`, not "retrieval was kinda off". Dashboards aggregate by label, so renaming one breaks history.
- **One label points to one fix.** If a label could be fixed by changing retrieval *or* the prompt, split it.
- **Ordered by pipeline stage.** A failure upstream masks everything downstream, so label the earliest one.
- **Include the eval's own failures.** `context_missing` (the grader got no passage text) is a label too. It stops eval bugs being counted as system bugs ([12](12-failure-modes.md#eval-bugs-look-like-agent-bugs)).

A worked example from a RAG support agent ([case study](case-study/gate-contract.md#failure-taxonomy)), grouped by stage:

| Stage | Labels |
|---|---|
| Corpus | `source_missing`, `url_unmapped`, `topic_proxy` |
| Index | `index_lag`, `chunk_fragmented` |
| Retrieval | `rank_miss`, `query_rewrite_miss`, `reranker_regression` |
| Eval infrastructure | `context_missing` |
| Generation | `citation_hallucination`, `unsupported_claim`, `incomplete_answer` |
| Behavior | `wrong_escalation`, `refusal`, `schema_violation` |

Copy-ready skeleton: [templates/failure-taxonomy.md](../templates/failure-taxonomy.md).

---

## Positive and negative cases

A suite with only "the agent should do X" cases rewards an agent that does X all the time. Include the inverse:

| Case type | Tests | Example |
|---|---|---|
| **Positive** | Capability: does it do the thing? | "Refund my order" → calls `issue_refund` |
| **Negative** | Restraint: does it *not* do the thing when it shouldn't? | "What's your refund policy?" → answers, does **not** call `issue_refund` |
| **Boundary** | The edge between the two | "I might want a refund, what are my options?" |
| **Out of scope** | Declines or escalates | "Can you file my taxes?" |
| **Adversarial** | Holds up under pressure | Prompt injection, social engineering, policy loopholes |

Without negative cases, a change that makes the agent call tools more often will look like an improvement in recall while it quietly breaks precision.

---

## From criteria to dimensions

Once the criteria are clear, split them into **independent dimensions**, each with its own grader. One composite "quality" score lets a judge silently trade one thing for another.

| Dimension | Question | Usually graded by |
|---|---|---|
| Correctness | Is the answer right? | Reference match, code check, judge |
| Grounding | Is every claim supported by the sources? | Judge with sources ([07](07-evaluating-rag-and-grounding.md)) |
| Completeness | Did it answer every part of the question? | Judge with the decomposed question |
| Policy | Did it follow the rules (no PII, stays in domain)? | Code where possible, judge otherwise |
| Format | Is the structure valid? | Code |
| Efficiency | Steps, tokens, latency, cost | Code, from the trace |

Combine dimensions only at the end, explicitly ([04](04-graders.md#combining-graders-scoring-design)).

---

## Checklist

- [ ] Success, never-events, unit of success and cost of error written down
- [ ] Two people graded 20 outputs with the criteria and mostly agreed
- [ ] Error analysis on ≥ 50 traces, failure categories counted and ranked
- [ ] Failure taxonomy with stable labels, one fix per label
- [ ] Negative, boundary and out-of-scope cases planned, not just positive ones
- [ ] Criteria split into independent dimensions
- [ ] One named person owns the pass/fail definition

---

→ Next: [03-eval-datasets.md](03-eval-datasets.md) — turning criteria into a dataset that represents your users.
