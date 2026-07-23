# Product & Business Sense — Study Guide

The differentiator round for FDE/DS roles and the hidden rubric everywhere else: FDE loops
weight business judgment + customer empathy at roughly half the evaluation. The skill:
connect every technical choice to a business outcome, in the client's language.

## 1. The framing habit (practice until automatic)

Every design answer opens with: **user → problem → success metric → constraint**. "Reduce
support cost 20% while holding CSAT" beats "build a RAG chatbot" — the second is a solution
looking for a problem. Process > results: interviewers grade how you structure ambiguity,
customize the approach to *this* case, and use them as a resource (listen, ask, adapt) —
not whether you land their pet answer.

## 2. ROI reasoning (have the arithmetic ready)

- **Cost side**: model/API spend per query × volume, infra, eval/annotation labor,
  maintenance; token math on a napkin (tokens/query × $/M tokens × queries/day).
- **Value side**: hours saved × loaded cost, deflection rate × cost-per-ticket, revenue per
  conversion lift, risk avoided (compliance fines, error costs).
- The consulting classic: *"Mistral 7B gives 90% of the accuracy — why still pick it over
  GPT-4?"* → because the last 10% costs 20× and the use case's error tolerance doesn't need
  it. Reverse it when errors are expensive. **ROI, not model maximalism.**
- Build vs buy vs wait: capability gap closing speed, vendor lock-in, data leverage you
  uniquely hold.

## 3. Product sense for AI products

- **Where AI belongs**: high-volume + tolerant-of-review workflows first (drafting, triage,
  summarization); irreversible/high-stakes actions last (see PRINCE's Search → Ask → **Do**
  staging in the [agents guide](../4-agents/interview-guide.md) §9 — trust is earned by phase).
- **Metrics trees**: north star → driver metrics → guardrail metrics. For agents: goal
  completion rate, no-touch rate (fully automated share), escalation rate, time-to-trust;
  guardrails: hallucination rate, complaint rate, cost/interaction.
- **Feedback loops as product**: thumbs-down → eval set → fix → measurable improvement; HITL
  corrections as training data. A product that *learns from operations* is the pitch.
- **Failure UX**: what the user sees on low confidence (abstain, cite, escalate) is a product
  decision, not an afterthought.

## 4. Nonprofit / mission-driven sector specifics

A differentiating lens (and this repo's owner's beat — DSSG platform work):

- **Constraints**: grant-cycle budgets (opex-averse → API bills need caps and
  predictability), volunteer/rotating maintainers (favor boring tech, documentation,
  managed services), donated/free tiers, small-data reality.
- **Success ≠ revenue**: define impact metrics with the org (clients served, caseworker
  hours returned, time-to-service); funders need reportable numbers — build the measurement
  in from day one.
- **Data ethics amplified**: beneficiary PII is high-stakes (immigration status, health,
  benefits); consent and minimization aren't compliance checkboxes but trust with vulnerable
  populations. Bias/fairness checks on anything allocating services.
- **Capacity building over dependency**: hand off runbooks, train staff, prefer solutions
  the org can operate after you leave — the FDE mindset, permanently.

## 5. Stakeholder translation (three audiences, one system)

- **Exec/funder**: outcome, cost, risk, timeline — no architecture.
- **Domain staff**: workflow change, what the tool does/doesn't do, escape hatches.
- **Technical**: the actual design + trade-offs.
Practice the same project as all three pitches (60s each). Consulting-style rounds also
probe: a failure you learned from, adapting when a client rejects your recommendation,
"walk me through disagreeing with a stakeholder."

## 6. Question bank (answer sketches)

- *"Client wants a chatbot — where do you start?"* — don't accept the solution: what problem,
  which users, what volume, what does success look like, what breaks today? Maybe the answer
  is search + three macros, not an agent.
- *"Estimate the ROI of automating X."* — volume × unit time × loaded cost vs build+run
  cost; sensitivity on adoption rate; pilot design to validate before scaling.
- *"The model is 92% accurate — ship it?"* — 8% errors × volume × cost-per-error; error
  *distribution* (harmless vs catastrophic); mitigation UX; then yes/no with conditions.
- *"How do you prioritize the AI roadmap?"* — impact × confidence ÷ effort with guardrail
  metrics as veto; earn trust with a reviewable-output use case first.
- *"A nonprofit asks for an AI intake assistant."* — capacity/PII/budget constraints up
  front; phased rollout with human review; impact metrics for the funder; handoff plan.

## Sources

- notes: [case-interview.md](../../notes/case-interview.md) (business-context tips, consulting-round expectations, ROI examples)
- external (from research doc): FDE loop analyses — case study + customer empathy ≈ 50% of evaluation (Exponent FDE guide, Perspective AI Anthropic/FDE writeups, Sundeep Teki guide — links in `.claude/docs/plans/2026-07-17-interview-kb-consolidation.md`)
- librarian wiki: Agentic KPI Trees · Copilot Learning Loop · VA Product Design Patterns (interaction-level staging)
- related round: [customer-simulation](../../rounds/customer-simulation/README.md) · [leadership-rounds](../../rounds/leadership-rounds/README.md)
