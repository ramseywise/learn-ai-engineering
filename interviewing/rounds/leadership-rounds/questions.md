# Leadership Round Questions

## Questions they ask you

### 1. "Walk me through a significant technical decision you owned. What would you change?"

**What they're testing**: Technical judgment, self-awareness, ownership vs blame-shifting.

**Strong response structure**:
- Name the decision clearly (don't bury it in context)
- State what you knew and didn't know at the time
- Own what you'd do differently — not "the team" or "the timeline"
- End with the principle you extracted, not regret

**Study refs**: system-design guide (trade-off method)

---

### 2. "Should we build [feature] or buy [tool]?"

**What they're testing**: Build-vs-buy judgment, cost modeling, strategic thinking about core vs commodity.

**Strong response structure**:
- Clarify: what's the build cost, what's the lock-in cost, what's the strategic value of owning this?
- State your framework explicitly: "I treat X as core and Y as commodity"
- Give an opinion with a reason — not "it depends" without resolution
- Flag what would change your answer

**Study refs**: system-design guide

---

### 3. "What's your view on [model vendor / AI tool the company uses]?"

**What they're testing**: Whether you've done your homework, whether you have vendor-independent judgment.

**Strong response structure**:
- Acknowledge what the vendor does well (don't dismiss)
- Name the specific trade-off or risk you'd watch
- State what eval signal would change your view
- Avoid brand allegiance — show you evaluate on evidence

**Study refs**: evals guide, system-design guide

---

### 4. "What would you do in your first 90 days?"

**What they're testing**: Ambiguity tolerance, learn-before-fix instinct, ability to scope a quick win without overcommitting.

**Strong response structure**:
- First 30 days: listen mode — interviews with cross-functional partners, read existing architecture and decision docs, find the seams
- Days 30–60: one small shippable win that demonstrates you can execute inside their constraints
- Days 60–90: one process or tooling improvement offered, not imposed
- Name what success looks like, not just activities

**Study refs**: study-guide.md (90-day sketch template)

---

### 5. "How do you decide when an AI system is ready for production?"

**What they're testing**: Eval discipline, risk calibration, maturity in AI quality assurance.

**Strong response structure**:
- Start with what failure modes matter (for this product, for these users)
- Name your eval gate: automated evals, human review threshold, shadow mode / canary rollout
- Acknowledge the ongoing nature — prod eval is different from pre-launch eval
- Avoid: "we test it and if it looks good" — that's the answer they're testing against

**Study refs**: evals guide

---

### 6. "Tell me about a time you pushed back on a product decision. What happened?"

**What they're testing**: Whether you can hold a position with evidence, and whether you can let go gracefully when overruled.

**Strong response structure**:
- State the decision and your concern clearly
- Name the evidence or principle behind your pushback (not just intuition)
- Describe how you communicated it — directly, not passive-aggressively
- End with what happened and what you learned, whether you were right or wrong

---

### 7. "What technical bets are you confident in right now? What hype would you push back on?"

**What they're testing**: Intellectual confidence, ability to distinguish signal from noise in fast-moving AI space.

**Strong response structure**:
- Lead with a real opinion, not a hedge — "I think X is durable because..."
- Name a specific hype you're skeptical of and why — not dismissal, but considered doubt
- Show you track evidence, not announcements
- Good bets to have opinions on: long-context vs RAG, agent reliability, model commoditization, eval automation

**Study refs**: system-design guide, evals guide

---

### 8. "How do you handle technical debt in an AI codebase?"

**What they're testing**: Prioritization, honesty about tradeoffs, engineering discipline in a fast-moving context.

**Strong response structure**:
- Distinguish types: model debt (stale prompts, deprecated APIs), eval debt (no coverage), infra debt (no observability)
- State your triage: what blocks shipping vs what compounds silently
- Name one concrete practice you use (scheduled debt sprints, coupling tests to model updates, etc.)
- Avoid: "we document it and prioritize later" without specifics

---

### 9. "How do you work with product when you think the spec is wrong?"

**What they're testing**: Cross-functional collaboration, directness, whether you're a friction generator or a thought partner.

**Strong response structure**:
- Distinguish "wrong" types: technically infeasible, user-problem mismatch, better alternative exists
- State how you bring it up: early, with a proposal, not just a critique
- Show you can commit and execute even if overruled, without passive resistance
- Name what "working well with product" actually looks like in practice

---

### 10. "What would make you leave a role after six months?"

**What they're testing**: Self-awareness, values clarity, whether you've thought seriously about fit.

**Strong response structure**:
- Answer honestly — don't optimize for "right" answer
- Name real deal-breakers: ethics violations, no psychological safety, persistent integrity gaps in product decisions
- Distinguish deal-breakers from difficulties — show you can navigate hard without leaving immediately
- Frame as mutual fit, not a test they're failing

---

## Reverse interview — question bank

The reverse interview is signal, not ceremony. Good questions demonstrate: you've done research, you think at the right altitude, you know what matters for success in this role. Weak questions (perks, growth trajectory, vacation policy) signal you're not operating at leadership level.

---

### For the CTO — technical judgment and trust

**"What's the most expensive technical decision you'd revisit if you could?"**
- What it tells you: Willingness to be honest about mistakes. A good answer shows a real mistake and a specific lesson. A red flag: deflects to team/timeline, or names a trivial decision.
- Green: owns it, names the counterfactual, shows updated thinking
- Red: "we made the right call given the info we had" (no reflection)

**"How do you evaluate model or vendor changes — is there an eval gate?"**
- What it tells you: Eval maturity. Whether they're running on vibes or evidence.
- Green: describes a specific eval suite, threshold, and process for production promotion
- Red: "we test it in staging and see how users respond" — reactive, not principled

**"Where does AI-generated code sit in your review process?"**
- What it tells you: Engineering culture around AI tooling — is it disciplined or chaotic?
- Green: clear policy, code review applies to AI output, someone is accountable
- Red: "we trust developers to manage it themselves" with no structural support

**"What does on-call / incident load actually look like?"**
- What it tells you: Reality of operational burden. Is this a well-run system or a constant fire?
- Green: specific numbers, recent improvements, investment in reliability
- Red: vague, minimizes it, or describes heroics as a feature ("we move fast")

**"What are the hardest parts of the technical roadmap right now?"**
- What it tells you: Honesty about unsolved problems vs polished recruiting pitch
- Green: specific, names real constraints (latency, eval coverage, model reliability at scale)
- Red: "exciting challenges" without naming them

**"How do you decide what goes into the ML platform vs what each team builds themselves?"**
- What it tells you: Platform thinking, centralization vs autonomy tradeoffs
- Green: clear criteria, named pain points that drove the decision
- Red: "we're still figuring that out" is fine if honest, bad if combined with confusion about ownership

---

### For the Head of Product — product judgment and org dynamics

**"How do you decide what not to build?"**
- What it tells you: Whether product has a real prioritization framework or backlogs everything
- Green: names a recent kill, explains the user-problem mismatch, has a process
- Red: "we have a backlog and revisit quarterly" — no active killing

**"Walk me through the last feature you killed and why."**
- What it tells you: Product discipline, willingness to reverse course, honest about sunk costs
- Green: clear story, names the signal that triggered the kill, no defensiveness
- Red: can't name one, or the story is about scope reduction not a real kill

**"How do eng and product disagree here — can you give a recent example?"**
- What it tells you: Psychological safety and intellectual honesty. Whether they have real debates or false harmony.
- Green: names a real disagreement, how it resolved, what each side learned
- Red: "we work really well together" without an example — red flag for culture

**"How do you weight user research vs usage data in product decisions?"**
- What it tells you: Product methodology maturity, comfort with ambiguity vs measurement
- Green: explains when each is appropriate, can name a decision that required both
- Red: "we look at the data" — data-only without qualitative understanding

**"Who is the customer you're building for, and when did that definition last change?"**
- What it tells you: ICP clarity and strategic honesty about pivots or market evolution
- Green: specific, current, willing to say "it shifted from X to Y when we learned..."
- Red: vague answer like "enterprises" or "developers" without segmentation

---

### For the founder / due-diligence questions

**"What's the runway, and what milestone does the next raise depend on?"**
- What it tells you: Financial honesty and whether they're recruiting into a stable or precarious situation
- Green: gives real numbers or range, names the milestone clearly, calm about it
- Red: deflects ("we can't share that"), or the milestone is vague ("continued growth")

**"Who left recently, and why?"**
- What it tells you: Retention signal, leadership honesty, early warning on culture or strategic drift
- Green: honest answer, names the reason, shows what changed (or what didn't and why)
- Red: "everyone's happy here" — no company has zero turnover, denying it is a tell

**"What would make the person in this role fail in the first year?"**
- What it tells you: Self-awareness about role requirements, maturity about failure modes
- Green: specific, honest — names real failure modes (moving too slow, wrong instincts on X, not building trust with Y)
- Red: "we don't expect failure" or generic answers about "culture fit"

**"How has the team's use of AI changed how you hire?"**
- What it tells you: Whether they're thoughtful about AI's effect on skill requirements and team composition
- Green: concrete changes — different bar on certain skills, new evaluation criteria, honest about what they don't know yet
- Red: "AI doesn't change what we look for" — either not using AI or not thinking about second-order effects

**"What's a strategic bet you're making that most investors you talk to are skeptical about?"**
- What it tells you: Intellectual confidence and willingness to be contrarian with reasoning
- Green: names a real bet, gives the thesis, acknowledges the risk
- Red: can't name one, or names something consensus ("we're betting on LLMs being useful")

**"If the current strategy doesn't work, what's the first thing you'd try next?"**
- What it tells you: Contingency thinking, intellectual honesty about risk, board-level clarity
- Green: has a real answer — shows they've thought about it without being crisis-mode about it
- Red: "we're confident in our strategy" — every good founder has considered alternatives

**"How does the board and investors disagree with you right now?"**
- What it tells you: Whether they have independent judgment or are investor-driven
- Green: can name real tension, explains their position, shows it's resolved through dialogue
- Red: "everyone's aligned" — either unrealistic or avoiding the question
