# Worked STAR Example: Conflict Resolution

**Prompt**: "Tell me about a conflict with a coworker."

**Story category**: Technical disagreement — steelman, resolution via prototype, relationship intact.

---

## The story

### Situation
> On a production ML pipeline, my colleague — a senior engineer I respected — wanted to switch our
> embedding model from a fine-tuned in-house model to a third-party API for the next release.
> I thought that was the wrong call. We disagreed, and it was blocking a planning decision.

**Annotation**: Two sentences. Establishes stakes (production, next release, planning blocked),
establishes the relationship (senior, respected — not an adversary), and establishes the
disagreement without editorializing about who was right. The interviewer doesn't know yet.

---

### Task
> I owned the evaluation framework and quality benchmarks for that pipeline — so the technical
> merit of the migration was squarely my call to defend or concede.

**Annotation**: One sentence naming the specific responsibility. This is not "I was on the team"
or "I cared about quality" — it names the actual ownership that gave you standing to push back.
Without this, the conflict story is just opinion vs. opinion.

---

### Action
> My first move was to understand his argument before defending mine. He was right that the
> third-party API had higher raw benchmark scores and would eliminate our fine-tuning maintenance
> overhead — real advantages. Where I disagreed was on the distributional shift risk: our use case
> had domain-specific terminology that I wasn't confident the general-purpose model handled well,
> and we had no eval suite covering that domain slice specifically.
>
> Instead of pressing the debate, I proposed we resolve it empirically: I'd build a targeted
> eval set for the domain-specific cases in two days, run both models against it, and we'd
> decide based on that output. He agreed.
>
> The eval took two days. The third-party model performed well on general cases — his point was
> valid there — but degraded meaningfully on the domain slice I was worried about: precision
> dropped from 87% to 61% on the subset.
>
> I presented both results together, including the general-case win. I didn't frame it as "I
> was right." I framed it as: "The API wins on general cases and maintenance overhead. For
> launch, I'd recommend we keep the fine-tuned model on the domain slice and use the API
> elsewhere, with a plan to expand API coverage as we build evals for the remaining subsets."
>
> He agreed immediately — the data resolved it without either of us losing face.

**Annotation**: This is the bulk of the answer — 70% of the total. Several things are working:

1. **Steelman first**: The opening of the Action acknowledges where the other person was right.
   This signals that you can separate your ego from your argument.
2. **"Instead of pressing the debate"**: This phrase signals conflict de-escalation and a
   bias to evidence over argument. Strong signal.
3. **The proposal**: Instead of escalating, you created a resolution mechanism. This is the
   pattern interviewers love — you didn't just push harder, you found a way to let evidence settle it.
4. **Both results presented**: You included the evidence that supported his view. This is
   critical — one-sided presentation would have undermined trust and credibility.
5. **Framing the outcome**: "I didn't frame it as 'I was right.'" This demonstrates social
   intelligence. You protected his credibility while getting to the right outcome.

**Common mistake at Action**: Jumping straight to "I presented my data and convinced him."
That's a much weaker version — it skips the steelman, skips the uncertainty, and skips the
relational intelligence.

---

### Result
> We shipped with the hybrid approach. The domain-specific precision held at 85% on the fine-tuned
> subset. We planned to migrate the remaining subsets as eval coverage expanded, which happened
> over the next two quarters.
>
> More importantly: my colleague and I became each other's go-to for technical review after that
> disagreement. He told our manager that working through it had improved how he thinks about
> pre-migration validation.

**Annotation**: Two things in the Result that matter:

1. **The number**: 85% precision. Not "performance was good." The number makes the outcome real
   and memorable.
2. **The relationship**: "Became each other's go-to." This is required for conflict stories — an
   answer that describes a technical win without mentioning the relationship is incomplete. The
   whole point of the prompt is "can you handle conflict without destroying the relationship."

---

### Reflection
> Since then, I default to "what would resolve this empirically?" as my first question in any
> technical disagreement. If there's no feasible experiment, I separate the components I'm
> confident about from the ones I'm uncertain about, and I present both sides in my argument,
> not just mine.

**Annotation**: Specific behavior, not platitude. "I default to 'what would resolve this
empirically?'" is something you can picture. "I learned to communicate better" is not.

The second sentence shows you've extended the lesson beyond the exact situation — you've
generalized it, which signals genuine learning rather than lesson-learned theater.

---

## What this story is doing (structural summary)

| Component | Signal it sends |
|-----------|----------------|
| Situation (2 sentences) | Stakes established without bias toward your view |
| Task (ownership named) | You had standing to push back — this wasn't opinion vs. opinion |
| Action (steelman first) | You separated ego from argument before pressing your case |
| Action (empirical resolution) | You created a mechanism for resolution, not just an argument |
| Action (both results) | You're honest about evidence that cuts against you |
| Result (number + relationship) | Concrete outcome + relationship strengthened, not just survived |
| Reflection (specific behavior) | You extracted a general principle and act on it |
