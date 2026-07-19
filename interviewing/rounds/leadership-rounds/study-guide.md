# Study Guide — Leadership Rounds

## Per-interviewer preparation framework

### CTO round prep

The CTO is asking: "Would I hire this person to make technical decisions I'd stand behind without supervising them?"

What this means in practice:
- They want **opinions with reasons**, not hedged non-answers. "It depends" is not an opinion.
- They're testing whether your judgment is calibrated or just accumulated opinions.
- They'll often push back on what you say — not to trick you, but to see if you update on evidence or just dig in.

**Prep moves:**
1. Research their stack through job postings, engineering blog, talks. Form a view on one tension they likely face (e.g., "they're using X for model serving — I'd want to know how they're handling latency at scale").
2. Prepare two technology stances: one bet you're confident in, one hype you'd resist. Both with specific reasons.
3. Have an answer to "what would you do differently?" — it should show learning, not blame.
4. Know their eval posture: are they early/ad-hoc, or mature? Tailor how much you push on eval discipline.

**Common failure mode**: Being too agreeable. A CTO who gets no pushback from a candidate worries they'll get no pushback from an employee.

---

### Head of Product round prep

The HoP is asking: "Can engineering-me be a thought partner, or will they just build what I spec?"

What this means in practice:
- They want to see you start from user problems, not from technical implementations.
- "Should we build X?" is almost always actually "what problem are we trying to solve, and is X the right way?"
- They respect engineers who have opinions on product — especially ones grounded in what the engineering enables or constrains.

**Prep moves:**
1. Study their product in detail. Know their core loop, their apparent ICP, their recent launches.
2. Form a view on one product decision they made — what you would have done and why.
3. Practice the "interrogate the problem first" reflex: when you hear a feature request, your first question is always "what user problem does this solve?"
4. Know one example of a feature you'd have killed or scoped differently — with the metric or user signal that drove it.

**Common failure mode**: Switching into "I'll build whatever you need" mode. This reads as low-value, not collaborative.

---

### Founder/CEO round prep

The founder is asking: "Do they actually care about what we're trying to do, and can they operate at multiple layers simultaneously?"

What this means in practice:
- Generic enthusiasm ("I'm excited about AI") is noise. Specific conviction ("I think your bet on X is right because Y") is signal.
- They want to know you can work at the scope of the role, which at a startup means: code + process + strategy, sometimes in the same day.
- They're often testing ambiguity tolerance — startups change, plans change, priorities change.

**Prep moves:**
1. Read their founding story, their public writing, investor letters if available. Know why they started this specifically.
2. Form a genuine view on whether the mission resonates — and why. Surface that view specifically, not generically.
3. Prepare your 90-day sketch (see template below).
4. Know your real deal-breakers before you walk in. Founders respect people who know what they won't do.

**Common failure mode**: Over-pitching alignment. Founders have heard "I've always wanted to work on X" hundreds of times. Show specific knowledge, not generic enthusiasm.

---

## The 90-day sketch template

The 90-day question is really asking: "How do you operate when you start somewhere new?" The failure modes are hero mode (I'll fix everything) and passive mode (I'll just observe).

**Template structure:**

**Days 1–30: Listen and map**
- Interview cross-functional partners (product, design, data, ops) — ask about their biggest friction with engineering
- Read architecture decision records, post-mortems, roadmap docs
- Find the seams: where do things break down silently? What's working better than anyone admits?
- Deliver: one-pager on what I observed and what I'd prioritize — shared for feedback, not declared as a plan

**Days 30–60: Ship something small**
- Pick one thing that unblocks someone else or reduces friction
- Constraint: it must fit inside current processes and be reviewable by the existing team
- Deliver: a merged PR or shipped change that shows I can execute inside their context, not against it

**Days 60–90: Offer one improvement**
- Surface one process or tooling change I'd propose — framed as a proposal, not a criticism
- Tie it to observed pain, not to "how we did it at my last company"
- Deliver: a doc or proposal that gets discussed — whether it's adopted is less important than showing I'm thinking at that altitude

**What success looks like at 90 days:**
- I know who the key decision-makers are and how they think
- I've shipped something that works
- I've built enough trust that people tell me the real problems, not the diplomatic version

---

## Technical judgment thread preparation

Leadership rounds — especially with CTOs — often center on a single deep thread about a technical judgment call. These are not quiz questions. They're a conversation about how you think.

**How to run a judgment thread:**
1. State your starting position clearly: "My default here is X, because..."
2. Name the key variable that changes your answer: "If Y is true, I'd move toward Z instead"
3. Acknowledge the opposing view without dismissing it: "The argument for the other side is..."
4. Show you can update: if they push back with new information, incorporate it — don't defend your original answer for its own sake

**Topics to have considered opinions on:**
- Build-vs-buy for model serving infrastructure
- Hosted models vs self-hosted — when the switch is worth it
- Eval automation: what can be automated, what requires human judgment
- Long-context vs RAG for retrieval use cases
- Agent reliability — what you'd trust agents to do unsupervised today vs in 12 months
- AI-assisted code review — where it helps, where it creates risk

**The two-stance exercise (do this before every leadership round):**
1. "A technical bet I'm confident in right now: _____ because _____"
2. "A hype I'd push back on: _____ because _____ and I'd need _____ to change my view"

---

## Product thinking for engineers

HoP rounds test whether you think in user problems and outcomes, not just in features and implementations.

**The problem-first reflex:**
When a feature is proposed, ask:
- What user problem does this solve?
- How do we know this is the right problem to solve right now?
- What metric moves if we solve it, and by how much?
- What would tell us we solved it wrong?

**Metrics trees:**
Practice decomposing a business outcome into its constituent metrics. Example:
- "Engagement is down" → DAU down? Session length down? Which cohort? Which surface?
- Finding the right node in the tree is the product-thinking skill.

**Feature kill decisions:**
Know one example where you'd have killed or dramatically scoped a feature — and the specific signal that drove it. Good kills: user research showed a different problem, usage data showed nobody used it, cost exceeded value at scale.

**The "should we build X?" reflex:**
Your answer structure should always be:
1. What problem is X solving?
2. Do we know that's the right problem?
3. Is X the right solution, or is there a simpler path?
4. What's the cost of being wrong?

---

## Reverse interview as evaluated signal

The reverse interview is not politeness. It is evaluated. Good questions communicate:
- You've researched the company (questions are specific, not generic)
- You're operating at the right altitude (questions are about strategy, culture, risk — not perks)
- You know what matters for success (questions probe the things that would make you succeed or fail)
- You have standards (you're evaluating them, not just hoping to be chosen)

**Question selection principles:**
- Pick 2–3 per interviewer, not 8 — depth over volume
- Make at least one question specific to something you learned in research ("I read your post about X — how has that thinking evolved?")
- Include at least one due-diligence question (runway, retention, failure mode)
- Avoid questions answered on the company's website — signals you didn't prepare

**The listening move:**
After they answer, reflect it back and probe: "That's interesting — does that mean you're moving toward X?" This is what makes it a conversation instead of a checklist.

---

## Company research checklist

Run this before every leadership-stage interview:

**Engineering signal:**
- [ ] Engineering blog — what are they writing about? What problems are they publicizing?
- [ ] CTO/staff engineers on Twitter/LinkedIn — recent posts, opinions, conference talks
- [ ] Job postings — what's in the stack, what roles are open, what does the posting reveal about their pain points?
- [ ] GitHub (if open source or public repos) — code quality, activity, how they handle issues

**Product signal:**
- [ ] Recent launches (Product Hunt, press, release notes)
- [ ] Customer reviews (G2, Capterra, App Store)
- [ ] Head of Product's background and public writing
- [ ] What problem they claim to solve vs what users say they actually solve

**Business signal:**
- [ ] Funding stage, round size, lead investors (Crunchbase, PitchBook if available)
- [ ] Approximate headcount and growth trajectory (LinkedIn)
- [ ] Recent news — expansions, pivots, layoffs, acquisitions
- [ ] Any public commentary from founders on strategy

**Culture signal:**
- [ ] Glassdoor / Blind — with appropriate skepticism, what are the consistent themes?
- [ ] Levels.fyi — compensation data and reviews from current/former employees
- [ ] LinkedIn — tenure of the team, especially leadership

---

## Due-diligence framework

Before accepting an offer from a startup, you need answers to these questions. The leadership round is your opportunity to get them.

**Runway and milestone:**
- How many months of runway at current burn?
- What milestone triggers the next raise? (Not "continued growth" — what specifically?)
- What's the burn rate and has it changed in the last 6 months?

**Retention:**
- Who left in the last 12 months, especially from leadership?
- What were the stated reasons?
- What's the average tenure of the current engineering team?

**Failure modes:**
- "What would make the person in this role fail in the first year?" — ask directly
- "What's the hardest thing about this job that doesn't show up in the job description?"
- What does the founder do when there's strong internal disagreement?

**Strategic clarity:**
- Is the strategy the same as it was 12 months ago? If not, what changed?
- What's the biggest thing investors and founders disagree on right now?
- What would they try first if the current strategy stopped working?

---

## Practice plan

**Week before the interview:**
1. Do the two-stance exercise for their specific stack and context
2. Write your 90-day sketch for this specific company — not a template, but the actual version for them
3. Prepare 2–3 reverse-interview questions per interviewer (CTO, HoP, founder)
4. Do the company research checklist and write down 3 things you learned that surprised you

**Day before:**
1. Read the engineering blog or CTO's most recent public content
2. Prepare one question that references something specific you found
3. Re-read your 90-day sketch out loud — does it sound like you or like a template?

**Day of:**
1. Know your real deal-breakers — write them down so you evaluate honestly in the moment
2. Have your reverse-interview questions written down (it's fine to reference notes)
3. Give yourself one judgment thread to think about on the way in

---

## Anti-patterns

**No opinions.** "It depends" is not an answer unless it's followed by "...and here's what it depends on and what I'd do in each case." CTO rounds in particular require you to have views.

**Generic mission alignment.** "I've always been passionate about AI" is noise. Know *their* mission and why *specifically* you find it compelling.

**Questions that are on their website.** "What's your product roadmap?" signals you didn't prepare. Same for: "What's your culture like?" "What does the team look like?"

**Treating the reverse interview as optional.** Saying "I think I've covered everything, I don't have questions" reads as disengaged. You always have questions.

**Agreeing under pressure.** When the CTO pushes back on your technical view, capitulating immediately signals you'll do the same in the role. Update when you hear new information; hold your view when it's just pressure.

**The last-company reflex.** "At my previous company, we did X and it worked great" — that's fine once; if it's the answer to everything, it signals you haven't developed independent judgment.

**Underestimating the founder round.** Founders often care the most about whether you're a fit. They're usually the most candid — use that to actually evaluate the opportunity, not just perform alignment.
