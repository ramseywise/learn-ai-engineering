# Worked Example: 90-Day Sketch — Joining an AI Startup as Staff AI Engineer

## Setup

Company: Series B AI startup building an AI-native CRM for sales teams. ~80 employees, 25 in engineering. You're joining as Staff AI Engineer, reporting to the CTO. The team has shipping velocity but limited eval infrastructure; they've had two quality regressions in the last quarter that reached production.

---

## The sketch

### Days 1–30: Listen and map

**What I'm actually doing:**

Week 1: No code. I'll do 1:1s with every engineer I'll work closely with — not to introduce myself, but to ask: "What's the thing that's blocking you right now that nobody's talking about?" and "What's working better than people give it credit for?" These two questions usually surface the real state of things faster than any documentation.

Week 2: Architecture spelunking. I'll read the last 6 months of PRs, any ADRs or design docs, recent post-mortems on those two production regressions, and the current eval suite (or lack thereof). I want to understand: where is the quality debt concentrated? What's the current eval coverage? What does the path to production look like for model changes?

Week 3-4: Cross-functional interviews. I'll talk to product, sales, and at least two customers if I can arrange it. My specific question: "What does a bad AI output look like to you, and how often do you see it?" This gets me grounded in what quality actually means for this product from the outside.

**What I'll deliver by day 30:**

A one-pager: "What I Observed — First 30 Days." Sections:
- Where quality debt is concentrated (specific, not general)
- Current eval coverage vs what we'd need
- One hypothesis about the most important thing to fix
- Shared for feedback, not declared as a plan

---

### Days 30–60: Ship something small

**What I'm actually doing:**

Based on what I learned in the first 30 days, I'll pick one thing that directly addresses a pain point for the team. In the scenario here — two production regressions with limited eval coverage — my guess is the highest-value move is adding automated eval for the riskiest prompt path. Not a full eval infrastructure overhaul; one critical path, automated, with a CI check.

This is deliberately small:
- It fits inside their current PR process — no new tooling required
- It's reviewable by the team with their existing expertise
- It produces visible signal (did the eval catch anything?) quickly
- It shows I can execute inside their constraints, not around them

**What I'll deliver by day 60:**

Merged: eval coverage for one high-regression-risk path, wired into CI. A short doc explaining what it catches, what it doesn't, and how to extend it.

---

### Days 60–90: Offer one improvement

**What I'm actually doing:**

By now I have enough context to have an opinion about one process or tooling change that would reduce ongoing risk. In this scenario, I'd probably propose a lightweight pre-release eval gate: before any model update ships, a minimum eval suite runs and a threshold must pass.

I'll write this up as a proposal — not a criticism of what they currently do, and not framed as "at my last company we did X." Framed as: "here's the problem I observed, here's one approach to address it, here are the trade-offs."

The proposal gets discussed, not automatically adopted. If they push back or prefer a different approach, that's fine — the goal was to show I can think at that altitude and contribute to how the team operates, not just execute tasks.

**What I'll deliver by day 90:**

A proposal doc: "Pre-Release Eval Gate — Proposal." Status: discussed in eng team meeting, decision recorded, whether adopted or not.

---

### What success looks like at 90 days

- I know who the real decision-makers are in each domain and how they think
- I have genuine relationships with 3–5 people who'll tell me the real problem, not the diplomatic version
- I've shipped one thing that works and that the team is glad exists
- I've proposed one process improvement that was taken seriously, regardless of outcome
- I understand the product well enough to have an independent opinion on one strategic question

---

## How to present this in an interview

When the founder/CTO asks "What would you do in your first 90 days?" — don't deliver this as a monologue. Deliver it as a dialogue:

Start with the frame: "My first instinct is always to listen before proposing. The first month is mostly observation and relationship-building."

Then get specific for their context: "Given what I know about you — that you've had quality regressions in production and limited eval coverage — my hunch is that the most valuable thing I could do in the first 60 days is [specific to their situation]. Does that map to what you'd actually want?"

The question at the end turns it into a conversation, not a pitch. And it gives them an opening to tell you if you've read the situation wrong — which is valuable information.

---

## What would have been weaker

**Hero mode:** "I'd come in and implement a full ML platform with eval infrastructure, CI/CD for models, and observability in the first 90 days." This signals you don't know how long things actually take, or you'll bulldoze existing processes.

**Passive mode:** "I'd spend the first 90 days learning the codebase and meeting the team." This signals you're deferring indefinitely without committing to output.

**Template mode:** "Learn, then ship, then improve." True, but not specific to their situation. Founders have heard this structure; they want to see what it looks like applied to their company.

**Over-promising:** "I'd solve the regression problem." You don't know enough yet to promise that. Showing you know you don't know enough — while demonstrating you have the instincts to find out — is more credible.
