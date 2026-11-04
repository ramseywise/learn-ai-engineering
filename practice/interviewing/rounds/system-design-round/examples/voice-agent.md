---
units:
  - ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents.md
  - generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md
  - generative-ai/08-eval/notes/15-calibration-against-human-labels.md
  - generative-ai/08-eval/notes/04-graders.md
  - data-science/01-classical-ml/notes/13-automate-review-or-reject.md
  - ai-engineering/05-graph-engineering/notes/08-governance-and-production.md
  - ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation.md
---

# Example: A Voice Agent That Runs and Scores Phone Conversations

## Prompt

"Design a voice agent that conducts thousands of structured phone conversations a day, across several client verticals, and scores each one."

**What the interviewer is checking**: whether you see two systems with different clocks. The call is a real-time loop where milliseconds and interruptions decide the design. The score is an offline measurement whose error has a price and lands on a person. A candidate who spends the whole time on latency has built a nice phone line that produces an unchecked number, and one who only designs the rubric hasn't noticed that a recogniser and an endpointer feed it. Listen also for "who is being scored?" being asked early, since it can change the legal tier of the whole product.

## Step 1: Clarify & scope (3 min)

**Questions I'd ask**:

- Who is scored, and what does the score decide? A staffing screen that advances an applicant is very different from a follow-up survey that nobody acts on one at a time.
- What does a wrong score cost in each direction, and can a person contest it?
- Who reviews, how many calls a week, and do their decisions come back as labels?
- How similar are the verticals? Same flow with a different question list, or different tools and rules?
- Does the agent only ask questions, or does it also act during the call, such as booking a slot or opening a claim?
- Inbound or outbound? What is the phone channel's audio like, and which languages and accents?
- Which countries are the callers in, where may audio go, and how long may it be kept?
- Do we have any human-scored calls today, per vertical?

**Assumptions after clarify**:

- Three fictional verticals to start: a staffing agency screening applicants, an insurer taking first notice of a claim, and a clinic following up after discharge.
- About 5,000 outbound calls a day, 8 minutes each, placed over 10 hours. These are my assumptions, and I'll size from them below.
- One tool can act mid-call (book a slot, open a claim). Everything else happens after the call.
- Scores recommend, and people decide anything consequential. Reviewers exist per vertical, with few labels at first.
- Callers are in the EU, English first.

## Step 2: Requirements (2 min)

**Functional**: place the call, tell the person they're talking to an AI, work through the vertical's required questions, handle interruptions, run tools, end cleanly and resume after a dropped line. After the call: transcribe, score each rubric item with evidence, route to accept or review, and log everything with versions of the script, rubric, models and thresholds.

**Non-functional**: time from end of speech to first audio, stated as a distribution and not an average. Few callers cut off. No action taken twice. Scores calibrated per vertical, with "not enough evidence" as its own outcome. One vertical's config, data and capacity can't affect another's.

**Say out loud**: "This is an agent spine for the call and an ML spine for the score. I'll design them separately, because the call has a deadline and the score doesn't, and the only thing they share is the record of what was said."

## Step 3: Design (15 min)

### Pipeline

```text
Call time, one session per call
  Phone audio, 20 ms frames
    → VAD + endpointer (window chosen by dialogue state)
    → Streaming ASR → dialogue graph: required questions as slots, one at a time
    → LLM → streaming TTS → speaker
    barge-in: cancel the turn's tasks, commit only what was heard
    tools: owned by the call, keyed, outcome written to history
    checkpoint after every turn, so a dropped line can resume

After the call, in a batch queue
  Recording → higher-quality batch ASR → transcript with timestamps
    → Coverage check: was each required question asked and answered?
    → One judge per rubric item, with quoted evidence, or CANNOT_GRADE
    → Veto items and code graders → combined score
    → Calibrate per vertical, with partial pooling
    → Route by prices: accept / human review
    → Reviewer decisions → labels → recalibrate, per-slice gate on any scorer change
```

### Key trade-offs narrated

**Cascade or speech-to-speech**: the options are [a streaming cascade or one model](../../../../../ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents.md#two-architectures). Speech-to-speech reacts faster and keeps tone. I'd take the cascade, and I'd compromise latency for the transcript, because the score needs an audit trail, tools are natural and standard guards work. It also means I'm not reading emotion from voice, which I'd want to avoid anyway (see below). Revisit this as those models gain tool support.

**The latency budget, and the line a server can't fix**: [write the budget down](../../../../../ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents.md#spending-the-latency-budget) per stage. Streaming saves more than a faster model. Waiting for the caller to finish is the line that matters, and in the [lab's running loop](../../../../../ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents.md#finding-the-end-of-speech) it was bigger than the planning placeholder: on 200 generated calls with stub stages at mixed 10 to 30 dB SNR, a 400 ms silence window gave a 520 ms median wait and 855 ms median to first audio, p95 1431 ms.

**One silence window can't serve a structured call**: this is where the prompt's "structured" pays off. The agent knows it just asked for a policy number, or an open question about experience, so the dialogue sets the window. In that lab, on generated audio that isn't speech with pause lengths we chose, a fixed 300 ms cut off every digit string and 900 ms added about a second to every turn, while 300 ms with 900 ms after a digit question got each case its own trade-off. Halving the window also isn't free: from 400 to 200 ms, calls where the agent talked over the person went from 8.5% to 31.0%. The percentages describe the generator, so tune on your own calls, per vertical. An applicant thinking aloud pauses longer than someone confirming a date. [Semantic turn detection](../../../../../generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md#streaming-voice-perception-replacing-vad--asr) is the next step once silence alone stops being enough.

**Cut-offs damage the score, not only the call**: an endpointer that cuts someone off produces a shorter answer, and the judge then scores that answer as if it were all they had to say. So cut-off rate belongs in the score's evaluation, not just the telephony dashboard. Record overlaps and re-prompts, and let reviewers see them.

**Barge-in with a tool in flight**: the [state machine](../../../../../ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents.md#interruption-is-a-state-machine) commits only what was heard. Cancel the turn's tasks, but the tool belongs to the call. Cancelling your request doesn't undo the server. In the lab's replay (40 generated calls, a tool taking an assumed 3 to 6 s), cancelling everything paid a refund 2.10 times per call, and an [idempotency key](../../../../../ai-engineering/03-harness-engineering/notes/03-tool-design.md#write-operation-safety) brought that to 1.00 while the agent still retried in every call. Only a surviving tool got 1.00 and no retries. I'd do both, since a dropped line can also cause a retry. A [non-blocking tool that reports back through events](../../../../../ai-engineering/03-harness-engineering/notes/03-tool-design.md#asynchronous-tool-interfaces) keeps the conversation moving meanwhile.

**Structure lives in the graph, not the prompt**: required questions are slots in a [small graph](../../../../../ai-engineering/05-graph-engineering/notes/05-topology-patterns.md), so code knows what's been covered, and the LLM only phrases the next question and understands the reply. A prompt that says "ask all eight" can't be tested for coverage. [Checkpoints](../../../../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md#checkpointers) give a dropped call a place to resume from. Read back any value you'll act on, as [the note's pitfalls](../../../../../ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents.md#pitfalls) say.

**Verticals are configuration**: [one agent core, many tenants](../../../../../ai-engineering/05-graph-engineering/notes/08-governance-and-production.md#one-agent-core-many-tenants). Script, rubric, tools, thresholds and limits are versioned per client, and a call pins its version at the start. Per-tenant budgets and admission limits sit at a gateway, so one client's calling campaign can't starve another's. A script change needs its own canary, because it changes what the rubric can see.

**Capacity, with no running hot**: 5,000 × 8 minutes over 10 hours is about 67 calls at once on average, on my assumed numbers. Campaigns bunch up, so I'd plan for several times that, and a real peak factor comes from the client's dialling plan. The [queueing rule of thumb](../../../../../generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md#paradigm-1-the-cascaded-pipeline) in the real-time note is total latency about idle latency × 1/(1 − utilization), so 2× at 50% load and 5× at 80%, and silence detection doesn't queue. So keep model stages well under full load for live calls, and shape outbound dialling to the capacity, which you can do because you place the calls. Scoring runs in a separate queue that can lag by hours and shouldn't take capacity from live calls.

**Scoring: one judge per criterion, and evidence first**: use [one judge per rubric item](../../../../../generative-ai/08-eval/notes/05-llm-as-judge.md#writing-the-judge-prompt), each quoting the transcript, and [binary items](../../../../../generative-ai/08-eval/notes/04-graders.md#binary-vs-scales) where you can. Code graders handle anything computable, such as whether the required disclosure was said. A [veto item](../../../../../generative-ai/08-eval/notes/04-graders.md#veto-items) covers what no total can offset. A rubric item whose question was never asked is [not a low score](../../../../../generative-ai/08-eval/notes/15-calibration-against-human-labels.md#not-enough-evidence-is-not-a-low-score). Scoring it as zero measures the agent's coverage and reports it as the person's. This is the mistake I'd most want to avoid, because it looks like a normal number.

**Calibration before trust**: [measure judges against human labels](../../../../../generative-ai/08-eval/notes/15-calibration-against-human-labels.md#the-procedure), and [correct the pass rate](../../../../../generative-ai/08-eval/notes/15-calibration-against-human-labels.md#correcting-the-pass-rate) rather than reporting the raw one. Verticals differ and most have few labels, so one threshold fits the biggest and a threshold per vertical chases noise. [Partial pooling](../../../../../generative-ai/08-eval/notes/15-calibration-against-human-labels.md#a-correction-per-vertical) sits between them. In that note's lab, on six generated verticals with 6 to 120 labels each and offsets of standard deviation 1.0, the three smallest averaged 0.047 regret under one threshold, 0.033 alone and 0.025 shrunk. A scorer change also clears a per-slice gate, since in the same lab accuracy rose 3.2 points overall while one vertical fell 27.5.

**Recognition error flows into the score**: batch ASR after the call can use a slower, better model than the live one, because nothing is waiting. Then [evaluate the scorer on machine transcripts as well as clean ones](../../../../../ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents.md#measuring-recognition-honestly), and track critical terms, per accent and channel. If one accent gets more recognition errors, it can get lower scores for the same answers. That is a fairness problem you can measure, and an average will hide it.

**Automate or review, from prices**: [price each route](../../../../../data-science/01-classical-ml/notes/13-automate-review-or-reject.md#price-each-route-and-the-thresholds-follow), and the thresholds follow, given [calibrated scores](../../../../../data-science/01-classical-ml/notes/13-automate-review-or-reject.md#calibration-is-the-precondition). Size the review band to [what reviewers can clear](../../../../../data-science/01-classical-ml/notes/13-automate-review-or-reject.md#when-the-queue-is-full). Prices differ by vertical: a wrong score that drops an applicant isn't the same as a wrong score on a survey.

**The legal tier comes from the use**: under [the EU AI Act risk tiers](../../../../../ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation.md#the-eu-ai-act-risk-tiers-applied-to-harbour), hiring is an Annex III use, so the staffing vertical is high-risk even if the other two aren't. People must be told they're talking to an AI. Detecting emotion from voice raises the tier by itself, which is one more reason to score only on the words. Keep [audio only as long as needed and in the right region](../../../../../ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation.md#data-residency-find-the-real-data-flow), and [decide retention up front](../../../../../generative-ai/08-eval/notes/08-tracing-and-observability.md#privacy-and-retention). Whether the tiers bind on a given client needs legal review. I'd say that out loud and design for the strict case.

### Sidecars

- **Eval set per vertical**: [production frequencies for the headline, rare costly cases in their own slices](../../../../../generative-ai/08-eval/notes/03-eval-datasets.md#coverage-and-balance), recorded from your own channel. [Clean read speech predicts little](../../../../../ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents.md#pitfalls).
- **Simulated callers**: scripted callers who pause, cough, interrupt and change their answers, run through the whole loop before a script or model ships, and [graded by state](../../../../../generative-ai/08-eval/notes/06-evaluating-agents.md#grade-the-outcome-by-state-not-by-words): did the required slots get filled, did the booking happen once.
- **Rollout**: new models and scripts go through [shadow and canary](../../../../../data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring.md#shadow-and-canary), per vertical.

## Step 4: Shortcomings (3 min)

- **Reviewers only see the queue.** Reviewers see what the router sent them, so [sample outside the queue](../../../../../generative-ai/08-eval/notes/11-production-and-the-maturity-ladder.md#sampling-live-traffic) or the accepted pile goes unchecked.
- **Scores drift when the script changes.** A reworded question can move scores with nobody having changed. [Keep calibration current](../../../../../generative-ai/08-eval/notes/15-calibration-against-human-labels.md#keep-it-calibrated), and treat a script version as a slice.
- **The score hides what the channel did.** A bad line, a cut-off or a language mismatch can all read as a weak answer. CANNOT_GRADE and a re-contact path help, but they don't remove it.
- **Tone is gone.** A cascade scores words only. That's a choice, and some verticals may ask for more.
- **The evidence here is generated.** The lab's audio isn't speech and its pipeline stages are timed stubs, so its numbers show what to measure and which way things move. They are not targets.
- **Topics the course doesn't teach yet.** I'd raise these and say my understanding is thin: phone-channel audio such as narrowband codecs, detecting voicemail and answering machines (which also pollutes the score), consent to record per jurisdiction, removing the agent's own voice from the line (the lab assumes this is done), and dialler pacing.

## Step 5: Close with measurement (2 min)

**Metrics**:

- Call: [time to first audio](../../../../../ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems.md#a-scorecard-for-the-whole-pillar) p50 and p95, how often callers repeat themselves, how often the agent talks over them, cut-offs from a sampled review, and task completion.
- Recognition: WER with one normaliser, and critical-term recall, per accent and channel.
- Actions: duplicate tool calls, which should be zero, and outcomes that never reached the person.
- Score: agreement with humans and corrected pass rate per vertical, CANNOT_GRADE rate, and the gap in scores between machine and clean transcripts.
- Review: queue size and age, overturn rate, and [drift](../../../../../generative-ai/08-eval/notes/11-production-and-the-maturity-ladder.md#drift).
- Money: cost per completed call, at live and batch rates, and the cost of wrong routes at the agreed prices.

**Future improvements**:

- A trained VAD and semantic turn detection, compared on cut-offs at the same latency.
- Speech-to-speech for low-stakes verticals, once tool support and an audit track hold up.
- Pausing at barge-in onset, and resuming if it turns out to be a cough.
- Adaptive follow-up questions, with the rubric still bound to what was asked.

---

**Study refs**: [Speech and voice agents](../../../../../ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents.md); [Real-time multimodal agents](../../../../../generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md); [Calibration against human labels](../../../../../generative-ai/08-eval/notes/15-calibration-against-human-labels.md); [Graders](../../../../../generative-ai/08-eval/notes/04-graders.md); [Automate, review or reject](../../../../../data-science/01-classical-ml/notes/13-automate-review-or-reject.md); [Governance and production](../../../../../ai-engineering/05-graph-engineering/notes/08-governance-and-production.md). Run the lab with `uv run voice_stream_lab.py` from `ai-engineering/08-multimodal-engineering/practice/`.
