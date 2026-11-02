# Worked Example: CTO Judgment Thread — Build vs Buy on Model Serving

## Setup

Company: Series A AI startup, ~30 engineers, building a B2B document intelligence product. Currently using OpenAI GPT-4 for all inference. CTO is probing your judgment on their infrastructure stack.

---

## The thread

**CTO:** We're at the point where our inference costs are starting to matter. How do you think about the build-vs-buy decision for model serving?

**Candidate:** My default starting point is: if the capability isn't core to your competitive differentiation, you rent it rather than build it — because building model serving infrastructure well is genuinely hard and the operational cost is underestimated. But there are a few inflection points where I'd revisit that.

The main one for model serving specifically is cost structure. Hosted APIs are expensive at volume, and the per-token cost doesn't compress the way most infrastructure costs do as you scale. If I look at your usage patterns and see that you're doing high-volume, relatively predictable inference — as opposed to sporadic, high-variance calls — that's when self-hosting starts to make economic sense.

**CTO:** We're probably at that inflection point. What would you actually do?

**Candidate:** I'd want to understand a few things before committing:

First, what's the inference load profile — are you serving synchronous user requests or async batch jobs? For async/batch, self-hosting on spot instances with something like vLLM is much more viable than for low-latency synchronous serving where the tail latency problem gets expensive fast.

Second, what models do you actually need? If you're locked to frontier models (GPT-4-class) because of capability requirements, self-hosting isn't yet an option for the top tier. But if fine-tuned or distilled models can hit your quality bar — and for document intelligence, that's increasingly plausible — then Mistral or Llama variants with vLLM are serious.

Third, do you have the operational capacity for it? Running model serving infrastructure requires someone who owns it. If your platform team is already stretched, you're trading inference cost for engineering cost, which may not be the right trade yet.

**CTO:** What if I told you we've actually experimented with self-hosting Llama 3 8B and the quality isn't there?

**Candidate:** That changes my recommendation substantially. If you've run that experiment and the quality gap is real for your use case, then the self-hosting path requires either accepting worse quality — which you've decided not to — or waiting for a model that closes the gap. That's a bet on a timeline, not an architecture decision.

In that case, I'd focus on cost reduction within the hosted API model: request caching for repeated or similar queries (your document intelligence use case probably has meaningful similarity within customer corpora), prompt compression to reduce token count, and tiering — using cheaper models (GPT-3.5 or 4o-mini class) for classification or routing steps, and frontier models only for the final extraction or generation step.

The thing I'd avoid is treating self-hosting as a solved problem you'll implement "when the models are ready" without a specific capability threshold that triggers the switch. Vague plans to self-host in the future are usually how teams accumulate technical debt on the vendor dependency side — you don't have a migration plan, you have a wish.

**CTO:** That's a fair point. We've talked about tiered routing but haven't implemented it. What would you look for to validate whether the cost savings are real?

**Candidate:** I'd want a shadow-mode evaluation before any production change. Route a sample of real requests through both paths — the current single-tier path and a proposed tiered path with cheap model for a routing/classification step — and measure: 1) final output quality on your existing eval suite, 2) end-to-end latency, 3) actual token cost per request. The quality metric is the gate; if the tiered path degrades quality, the cost savings aren't real, they're a transfer to support and customer success.

The thing I'd be careful about is running this experiment without your eval suite in place first. If you don't have automated eval coverage, the shadow-mode test is subjective and won't hold up to scrutiny. That might be the actual prerequisite.

---

## What this thread demonstrates

- **Starting position with reasons**: "my default is X because Y" — not just an answer, a framework
- **Conditional structure**: "if A is true, I'd move toward B" — shows you're solving their problem, not demonstrating your knowledge
- **Updating on evidence**: When the CTO introduced the Llama 3 experiment result, the candidate immediately incorporated it and changed their recommendation — didn't defend the prior position
- **One step further**: Instead of just accepting the new constraint, surfaced the implication (need a specific threshold for the self-hosting switch, not a vague future plan)
- **Staying grounded in operational reality**: Named the eval prerequisite at the end — shows awareness that the "correct" architecture depends on what's actually in place

## What would have been weaker

- "It depends on a lot of factors" — deferral without resolution
- "We should self-host because it's cheaper" — recommendation without understanding the specific constraints
- "Okay, tiered routing makes sense" — agreeing when the CTO suggested it, without probing whether the prerequisite (eval suite) is in place
- Not updating when the Llama 3 experiment came up — doubling down on the self-hosting recommendation despite new evidence
