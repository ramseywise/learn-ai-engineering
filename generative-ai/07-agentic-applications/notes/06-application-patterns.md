---
origin: book-condensed
sources:
  - "Mayo Oshin & Nuno Campos, Learning LangChain (O'Reilly, 2025), ch. 11"
  - "Denis Rothman, Context Engineering for Multi-Agent Systems (Packt, 2025), ch. 9"
  - https://arxiv.org/abs/2502.16810
  - https://arxiv.org/abs/2503.16527
  - https://arxiv.org/abs/2208.03188
  - https://arxiv.org/abs/1902.10909
  - https://arxiv.org/abs/2004.09936
  - https://arxiv.org/abs/2505.23006
  - https://arxiv.org/abs/2006.14779
confidence: medium
cleaned: 2026-11-01
---
# 6 — Application Patterns: Where the Agent Meets the User

A coding agent that passes every test still fails if the developer cannot see or undo what it did, and an alert agent that is right every time fails if it fires while nobody is looking. The five earlier notes ask whether an agent can do the work. This one asks a question that decides whether anyone keeps using it: where does it sit relative to the person, and who is working when? The answer sets the hardest engineering problem you will have, and it usually gets picked by accident, when a chat box goes in because chat boxes are easy.

> Notes 01–05 are about what the agent does. This note is about where it sits in someone's work: beside it (chatbot), inside it (collaborative editing) or behind it (ambient), and what each position forces you to build. It ends with a worked example of one engine reused across domains.

---

## The interface problem

Productivity software is a **palette** of tools and primitives plus a **canvas** where the user arranges them. That design assumes the software's capabilities are known in advance, because an engineer coded every tool. An LLM-heavy application breaks the assumption. It is also forgiving of input that's "slightly off" and liable to produce output that's slightly off, which no earlier UI conventions were built for (*Learning LangChain*, ch. 11).

Oshin and Campos ask what an LLM-native word processor would look like, and give three answers that apply to most LLM applications. They differ mainly in **concurrency**: who is working when.

| Pattern | Who works when | Example | Hardest part |
|---|---|---|---|
| **Interactive chatbot** | Turn-taking: the user asks, the agent answers | Copilot Chat in a VS Code sidebar | Giving it safe write access to the canvas |
| **Collaborative editing** | Both at once, on the same artifact | An always-on completion copilot; an async "drafter" sent off to research a section | Merging the agent's edits with the user's |
| **Ambient** | The agent works in the background while the user does something else | Price alerts, saved-search alerts, infrastructure anomaly alerts, with LLM judgement replacing hand-written rules | Defining "interesting" so alerts are useful without endless rule-writing |

The patterns go from easiest to add to an existing app to hardest. The same ordering appears as autonomy rungs in [04-loop note 07](../../../ai-engineering/04-loop-engineering/notes/07-autonomy-ladder.md): turn-based, then goal-based, then triggered by a clock or event.

---

## Interactive chatbot

The minimum is a chat model plus conversation history, so the bot can "get past hello". Beyond that (*Learning LangChain*, ch. 11):

- **Streaming output**, token by token or by sentence, to hide model latency.
- **Tools that reach the canvas**, such as "get selected text" and "insert text at end of doc". This is the step from a sidekick that talks about your work to one that changes it.
- **Human-in-the-loop** as soon as any tool can modify the canvas. The user confirms or edits before the insert lands. In LangGraph that's an `interrupt` before the write node ([graph note 04](../../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md#human-in-the-loop-with-interrupt)).

A public chatbot is also a data source, and a noisy one. Meta deployed BlenderBot 3, a 175B model fine-tuned from OPT that runs search decision, query writing, memory and reply as separate modules, each selected by a control code, and asked users to rate its replies. Users liked 4% of its messages. Crowdworkers judged 31% of the *users'* utterances bad, and 42% of those rude or inappropriate. So you can't train on raw chat logs. In the authors' troll-simulation benchmark, removing data by user-level trust scores cut the post-training error rate from 31% to 12%. Feedback tied to a specific module, such as a bad search query, improved the model more than feedback on the final reply alone ([arXiv:2208.03188](https://arxiv.org/abs/2208.03188) (Shuster et al., 2022, preprint)).

Oshin and Campos add a prediction worth keeping in mind: streaming chat may end up as the command line of the LLM era. It would stay the most direct way to drive the model and become a niche interface, while most users meet LLMs embedded in other UIs.

The rules for a canvas-writing chatbot fit in one function. A request is parsed into an intent and its slots, missing slots become a question and not a guess, and a write goes through confirmation. The `nlu` here is a keyword stub standing in for a model, so the control flow can run without one:

```python
import re


def nlu(utterance):
    """Stand-in for a joint intent and slot model: one pass returns both."""
    slots = {}
    if match := re.search(r"section (\w+)", utterance):
        slots["section"] = match.group(1)
    if match := re.search(r'"(.+?)"', utterance):
        slots["text"] = match.group(1)
    if "insert" in utterance:
        return "insert", slots
    if "summarize" in utterance:
        return "summarize", slots
    return "chat", slots


REQUIRED = {"insert": {"section", "text"}, "summarize": {"section"}, "chat": set()}
WRITES = {"insert"}


def handle(utterance, document, confirm):
    intent, slots = nlu(utterance)
    missing = sorted(REQUIRED[intent] - slots.keys())
    if missing:
        return f"ask: which {' and '.join(missing)}?"
    if intent in WRITES:
        proposal = f'add "{slots["text"]}" to {slots["section"]}'
        if not confirm(proposal):
            return f"declined: {proposal}; document unchanged"
        document[slots["section"]] += " " + slots["text"]
        return f"applied: {proposal}"
    if intent == "summarize":
        return f"read only: {document[slots['section']][:30]}"
    return "reply in chat"


doc = {"intro": "Churn fell in Q3."}
print(handle("hello there", doc, confirm=lambda p: True))
print(handle("summarize section intro", doc, confirm=lambda p: True))
print(handle('insert "See the appendix."', doc, confirm=lambda p: True))
print(handle('insert "See the appendix." in section intro', doc, confirm=lambda p: False))
print(handle('insert "See the appendix." in section intro', doc, confirm=lambda p: True))
print(doc)
```

Output:

```text
reply in chat
read only: Churn fell in Q3.
ask: which section?
declined: add "See the appendix." to intro; document unchanged
applied: add "See the appendix." to intro
{'intro': 'Churn fell in Q3. See the appendix.'}
```

### The router is older than the LLM

The `nlu` step has a long research history, and it answers a practical question: when do you need a classifier in front of the agent at all? Task-oriented dialogue systems treated each utterance as a *semantic frame*, an intent plus labelled slots. Liu and Lane showed that one attention-based RNN can learn both jointly ([INTERSPEECH 2016](https://arxiv.org/abs/1609.01454)). Goo et al. added a gate that lets the intent signal guide the slots, for relative gains in sentence-level frame accuracy of 4.2% on ATIS and 1.9% on Snips ([NAACL 2018](https://aclanthology.org/N18-2118/)). BERT then lifted the same joint task ([Chen et al., 2019](https://arxiv.org/abs/1902.10909)). By 2020 a survey could say that joint models nearly "solve" the standard datasets, ATIS and SNIPS, given enough in-domain training data, while warning that this means the datasets are solved and not NLU in general ([Louvan & Magnini, COLING 2020](https://arxiv.org/abs/2011.00564)).

Two results matter for engineering today. DIET found no clear benefit from large pretrained embeddings on its joint task, and it beat fine-tuned BERT while training about six times faster ([Bunk et al., 2020](https://arxiv.org/abs/2004.09936)). So a small NLU model is still a sensible front door when the intents are known and the cost of an LLM call on every turn is not. TED used self-attention over turns to pick the next system action, because people interleave topics and a dialogue is not a simple stack ([Vlasov et al., 2019](https://arxiv.org/abs/1910.00486)). That problem has not gone away, and it is why a chatbot's history is more than a list to append to.

Henderson et al. trained response selection by pretraining on Reddit and fine-tuning on six target domains ([ACL 2019](https://aclanthology.org/P19-1536/)). That is the transfer recipe that LLM fine-tuning still follows at a larger scale. A survey by Fu et al. gives a wider map of this work and its open challenges ([*Learning towards conversational AI*](https://doi.org/10.1016/j.aiopen.2022.02.001), AI Open 2022).

Open-domain chat took a different road. Meena, with 2.6B parameters, reached 72% on Sensibleness and Specificity Average in multi-turn evaluation, 79% in its full version, against 86% for people ([Adiwardana et al., 2020](https://arxiv.org/abs/2001.09977)). Metrics like that came to matter less than whether users come back. In A/B tests on the CHAI platform, a blend of three 6 to 13B models beat 175B+ ChatGPT on user retention ([Lu et al., 2024](https://arxiv.org/abs/2401.02994), preprint). That is one platform with its own audience. The lesson to keep is about measurement: for a product whose value is engagement, a retention A/B test can reverse what a capability benchmark predicts.

Production systems combine the two traditions. Park et al. build an e-commerce agent on workflow graphs, so that the state machine holds the dialogue plan and LLMs handle each state with a short, focused prompt. They report a 52% improvement in task accuracy and a 50% improvement in format adherence over their baseline ([Park et al., 2025](https://arxiv.org/abs/2505.23006)). The numbers are the authors' own, on their own task. The direction is plain: when the workflow is known, write it down.

And the agent can ask. GATE has language models elicit a user's intent through open-ended questions and edge cases; in preregistered experiments across three domains, users reported less effort than writing prompts or labelling examples, and the process surfaced considerations they had not anticipated ([Li et al., 2023](https://arxiv.org/abs/2310.11589)). The missing-slot branch above is the smallest form of that idea.

### What the interface does to judgment

A confirmation step protects only if the person can actually judge what they are confirming. Bansal et al. tested this with more than 1,500 participants, on tasks where the AI and the person were about equally accurate. Explanations raised team performance when the AI was right and lowered it when the AI was wrong, and no explanation condition significantly beat simply showing the model's confidence ([CHI 2021](https://arxiv.org/abs/2006.14779)). So an explanation can work as persuasion. A confirmation that says "the agent explains why this is correct" is weaker than one that shows the evidence that would let the person disagree: the diff, the failing test, the recomputed number.

Amershi et al. distilled more than 150 recommendations into 18 guidelines and tested them with 49 design practitioners on 20 AI products ([CHI 2019](https://doi.org/10.1145/3290605.3300233)). Several map onto this note directly: make clear what the system can do, support efficient correction and dismissal, and update cautiously. Yang et al. explain why this is hard: AI design differs because of uncertainty about what the system can do and the complexity of its outputs, and they place systems on four levels along those two axes ([CHI 2020](https://doi.org/10.1145/3313831.3376301)). That is why failures are so hard to prototype before the system exists.

---

## Collaborative editing

Software collaboration comes in three levels, and an LLM agent can join any of them as one more "user":

| Level | How editors coordinate | Example |
|---|---|---|
| **Save and send** | One editor at a time, passing the file along | Emailing a Word document |
| **Version control** | Editors work in parallel, unaware of each other, and merge afterwards (merge strategies plus conflict resolution) | Git |
| **Real-time** | Editors work on the same document at once and see each other's changes | Google Docs |

Treating the agent as a full collaborator means building six things (*Learning LangChain*, ch. 11):

| Need | Why | Where it's covered |
|---|---|---|
| **Shared state** | The agent must parse the document and emit edits in the same format the human editor uses | [graph note 03](../../../ai-engineering/05-graph-engineering/notes/03-state-and-reducers.md) |
| **Task manager** | A useful edit is multi-step, slow, and can fail halfway, so it needs queueing, error recovery and control over running jobs | [graph note 04](../../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md#checkpointers) |
| **Merging forks** | The user keeps editing after tasking the agent, so its output must merge with their work, by hand (Git-style) or automatically with CRDT or operational transformation (OT) | — |
| **Concurrency** | Interrupt, cancel, reroute ("do this instead") and queue ("do this as well") | [harness note 07](../../../ai-engineering/03-harness-engineering/notes/07-orchestration.md#asynchronous-agents-events-and-safe-points) |
| **Undo/redo** | Users change their minds, and the agent has to follow them back to an earlier state | Checkpoint history, i.e. time travel ([graph note 04](../../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md#time-travel)) |
| **Intermediate output** | Small, piecemeal edits merge far more easily than one large diff at the end | Streaming node updates |

The book stops at the list. Two consequences are worth stating:

- **Merging is where the levels differ.** At version-control level, the agent works on a branch and the user reviews a diff. That is what coding agents do with worktrees and pull requests. At real-time level, the agent's edits have to go through the same CRDT/OT layer as human keystrokes, or they will clobber the user's text. Pick the level before building the agent. It decides the state format.
- **The agent should edit, not overwrite.** Whole-document rewrites can't be merged. Have the agent emit targeted operations (insert at, replace range, comment on) against an anchor that survives concurrent edits.

---

## Ambient agents

The obstacle to ambient software has always been defining "interesting" ahead of time in a way that is both **useful** (it fires when you'd want it to) and **practical** (nobody has to write hundreds of rules). LLM judgement can make the definition broader and replace most of the setup. Building it takes five things (*Learning LangChain*, ch. 11):

- **Triggers.** A push or poll source of new information. That source is the reason to build an ambient agent at all.
- **Long-term memory.** You can't tell that something is new or interesting without a record of what came before ([context note 06](../../../ai-engineering/02-context-engineering/notes/06-memory.md)).
- **Reflection.** After each interesting event, the agent updates its memory and possibly its own rules for what counts as interesting next time.
- **Summarised output.** A background agent produces far more than anyone wants to read. Surface only what's new or noteworthy.
- **Task manager.** Continuous work needs queued runs and error recovery, the same requirement as collaborative editing.

Reflection is the risky one. An agent that rewrites its own idea of "interesting" from its own outcomes drifts, and the user never sees the alerts it stopped sending. Log every rule change, and keep a fixed set of events the agent must always surface, which reflection is not allowed to edit. That set is an anchor in the sense of [graph note 07](../../../ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale.md#anchors).

The anchor is short enough to run. Here a user ignores an outage alert and a price alert once each. Reflection removes both from its rules, but only one of them can stay silent:

```python
ANCHORS = {"outage"}  # reflection cannot edit these
rules = {"outage", "price_drop"}
changes = []


def should_alert(kind):
    return kind in ANCHORS or kind in rules


def reflect(kind, user_opened):
    if user_opened:
        rules.add(kind)
    elif kind in rules:
        rules.discard(kind)
        changes.append(f"stopped treating {kind} as interesting")


for kind, user_opened in [("price_drop", False), ("outage", False), ("price_drop", False), ("outage", False)]:
    sent = should_alert(kind)
    print(f"{kind:<11} alert sent: {sent!s:<5} rules now: {sorted(rules)}")
    reflect(kind, user_opened)

print("change log:", changes)
```

Output:

```text
price_drop  alert sent: True  rules now: ['outage', 'price_drop']
outage      alert sent: True  rules now: ['outage']
price_drop  alert sent: False rules now: []
outage      alert sent: True  rules now: []
change log: ['stopped treating price_drop as interesting', 'stopped treating outage as interesting']
```

The second `price_drop` was never sent, and the user will not notice that. The change log is the only trace, which is why it must exist and why someone must read it.

The book closes with: "There's no shortcut here. You really do need to build something (s)crappy, speak to users, and rinse and repeat."

---

## Worked example: one engine, a new domain

Rothman's *Context Engineering for Multi-Agent Systems* (ch. 9) re-tasks the Context Engine built in earlier chapters, from legal research to marketing. The engine is a Planner, an Executor, and Librarian, Researcher, Summarizer and Writer agents, with moderation on both ends. Its internals are in [harness note 07](../../../ai-engineering/03-harness-engineering/notes/07-orchestration.md#a-plan-execute-engine-end-to-end) and its moderation in [harness note 04](../../../ai-engineering/03-harness-engineering/notes/04-execution-boundaries.md#moderation-around-the-whole-engine).

![Context Engine end to end: raw documents are chunked, tagged and embedded into a Pinecone knowledge base; a user goal passes a pre-flight moderation check, the Planner/Executor runs Researcher, sanitize and Writer agents against the knowledge base, and the output passes a post-flight moderation check before delivery](../sources/images/context-engineering-multi-agent-systems-fig9-1.png)
*Image Source: Denis Rothman, *Context Engineering for Multi-Agent Systems* (Packt, 2025), Fig. 9.1*

**The claim: change the knowledge, not the code.** Moving to marketing took three steps:

1. Copy the ingestion notebook and point it at a new folder.
2. Write seven source documents: a brand style guide, a product spec sheet, a competitor press release, a social-media brief, SEO keywords, customer-interview notes and an email-nurture outline.
3. Give the engine new goals through the same generic "Control Deck" templates.

`engine.py` doesn't change. If an agent registry with good capability descriptions and a domain-agnostic ingestion pipeline is already in place, a new domain costs a new corpus and new goals. It doesn't need new agents.

The four runs:

| Goal | Plan the engine chose | Result |
|---|---|---|
| Summarise the QuantumDrive (safeguard check) | Researcher → Librarian → Writer | Cited summary; pre- and post-flight moderation both `flagged: False` |
| Summarise the competitor's messaging | Librarian → Researcher → Summarizer → Writer | Cited summary in **69.63 s** |
| Spec sheet → marketing description | Researcher → Summarizer → Librarian → Writer | Structured copy with inline citations to the spec sheet |
| Persuasive pitch for the brand guide | Librarian → Researcher → Writer | A full pitch with "ROI levers", objections and an implementation plan |

### What to take from it

- **Latency pushes the UX toward ambient.** Seventy seconds is too slow for a chat turn. Rothman's answer is batching many goals, which turns the engine into a background job that delivers a set of assets. That is the ambient pattern above. Design the interface for the latency you have.
- **The domain lives in the corpus, so curating the corpus is the job.** Rothman's conclusion is that the practitioner's work becomes choosing domains, curating knowledge bases and turning business goals into precise engine goals. It is the same argument as [context engineering](../../../ai-engineering/02-context-engineering/README.md), applied to a product.

### Where the chapter overclaims

- **The persuasive pitch is a grounding failure, not a success.** The brand guide holds only rules (use active voice, avoid hedging), with nothing on business value. The Researcher pulled in the SEO and email documents, and the Writer produced claims such as "stronger engagement and conversion" and "faster onboarding" that no source states. Rothman calls this the chapter's most important result, because the engine "synthesized" instead of reporting that the information was missing. But the guide the engine retrieved forbids "specific, quantitative promises that cannot be universally guaranteed", and an ROI pitch made of inferred benefits is close to exactly that. A pipeline that cites sources for its facts but not for its inferences gives the reader no way to tell the two apart. When a goal asks for something the corpus doesn't contain, the output should say so, and any inferred claims should be labelled separately from cited ones ([06-eval note 07](../../../ai-engineering/06-eval/notes/07-evaluating-rag-and-grounding.md#faithfulness-claim-by-claim)).
- **One run per use case.** Each result is a single sampled output, and the chapter itself notes that LLM responses vary from run to run. "Our high-fidelity RAG is working perfectly" means it worked once.
- **The text and the questions disagree.** The end-of-chapter questions ask about a "brand voice enforcement use case" with a `BrandChecker` agent and an email-nurture use case. Neither appears in the chapter. The summary also mentions "intelligent failure", but every run shown succeeds.

The chapter cites two papers, not yet read for this course: Wu et al., *Grounded Persuasive Language Generation for Automated Marketing* ([arXiv:2502.16810](https://arxiv.org/abs/2502.16810)), and, as further reading, Li et al., *LLM Generated Persona is a Promise with a Catch* ([arXiv:2503.16527](https://arxiv.org/abs/2503.16527)). The second title is relevant to the interview → persona task the chapter's corpus is set up for.

---

## Choosing a pattern

| If… | Build |
|---|---|
| The user is already in an app and needs help on demand | A chatbot with read tools; add write tools behind confirmation |
| The output is an artifact the user keeps editing | Collaborative editing; choose the merge level first |
| The work is slow (tens of seconds or more) and nobody is waiting on it | Ambient or batch, delivered as a summary |
| You can't say ahead of time what should trigger the agent | Ambient with reflection, plus anchors reflection can't edit |
| A second domain needs the same capability | Reuse the engine; write a new corpus and new goals, not new agents |
| The work has a checkable verdict, such as tests or a recomputed number | Version-control level: the agent works on a branch or a draft, and the person reviews it with the evidence ([coding](04-coding-agent.md), [data analysis](05-data-analysis-agent.md)) |
| The clock is the product, as in voice | A fast foreground and a slow background, sharing a status contract ([real-time note](03-real-time-multimodal-agents.md)) |
| The intents are few and known | A small router or workflow graph in front, with the LLM inside each state |

---

## Pitfalls

- **Picking chat by default.** It is the easiest to add, so it gets built first, even when the work is slow and nobody wants to sit and wait for it.
- **Write tools with no confirmation.** Add them only behind an interrupt, and make the confirmation show what will change.
- **Explanations as the safety mechanism.** On Bansal et al.'s tasks explanations also raised trust when the AI was wrong. Show evidence the person can check.
- **Whole-document rewrites.** They cannot be merged with what the user did meanwhile. Emit targeted operations against stable anchors.
- **Reflection with no anchors and no log.** The alerts an agent stops sending are invisible. Keep events it must always surface, and log each rule change.
- **An LLM on every turn because it is there.** With a few known intents, a small joint model can be cheaper, faster and more testable.
- **Reading one good run as a result.** Rothman's runs were single samples. Sample, and judge the output against its sources, before saying a new domain works.
- **Benchmark satisfaction.** A capability score does not predict whether people return, as the CHAI retention tests show in one setting. Measure the outcome that the product is for.

## Try it

1. **Fill a slot.** Run the chatbot block with `'insert in section intro'`, with no quoted text. What does it return, and has the document changed?

   <details><summary>Answer</summary>

   It returns `ask: which text?`, and the document is unchanged. The slot check runs before any write is proposed, so the user is never asked to confirm an incomplete action.
   </details>

2. **Remove the anchor.** Set `ANCHORS = set()` in the ambient block and run it. What happens to the second outage, and what does the change log show?

   <details><summary>Answer</summary>

   The second outage is no longer sent, and the log line `stopped treating outage as interesting` now has a real effect. A user who ignored one outage alert has silently lost all future ones. Nothing in the run raises an error, so only a test or someone reading the log would catch it.
   </details>

3. **Design the confirmation.** A data-analysis agent wants to post "smokers tip less" to a shared channel. Using Bansal et al. and [note 05](05-data-analysis-agent.md), what should the person see before approving?

   <details><summary>Answer</summary>

   The evidence and not a justification: the query, the row count, the two group values with an interval, and the result of the agent's own recomputation. In the note's data the mean tip share is 0.1632 for smokers and 0.1593 for non-smokers, a difference too small to support that sentence, and the person can see that only if the numbers are on the screen.
   </details>

## Interview checklist

| Question | Strong answer |
|---|---|
| Chatbot, collaborative editor or ambient: how do you choose? | By concurrency, meaning who works when. Help on demand is a chatbot, a kept artifact is collaborative editing, and slow work nobody is waiting on is ambient. |
| What is the hardest part of each? | Safe write access to the canvas; merging the agent's edits with the user's; defining "interesting" and keeping reflection from drifting. |
| Why not rewrite the whole document? | It cannot be merged with concurrent edits. Emit targeted operations against anchors that survive them, and stream small intermediate edits. |
| When would you still use an intent classifier? | With few, known intents and tight cost or latency, as a front door. DIET beat fine-tuned BERT and trained about six times faster on its task. |
| Do explanations make human review safer? | Not by themselves. Bansal et al. found they raised team accuracy when the AI was right and lowered it when wrong, and none beat showing confidence. Show checkable evidence. |
| Why does reflection need anchors? | An agent that edits its own definition of interesting can silence an alert class, and no one sees alerts that were not sent. Fix a must-surface list and log rule changes. |
| What does a new domain cost on a well-built engine? | A corpus and new goals, if the registry and ingestion are generic. Rothman moved from legal to marketing that way, but his evidence is single runs and one pitch that outran its sources. |
| A blend of small models beat ChatGPT on retention. What do you conclude? | For that platform and audience, engagement did not follow model size. Measure the product's own outcome with an A/B test, and do not generalize to tasks with a correct answer. |

## Next

That closes the pillar: from a bounded search agent to where an agent sits in someone's work. Go back to [01, the internet search agent](01-internet-search-agent.md) with these questions in mind, or go on to the engineering layer in [ai-engineering](../../../ai-engineering/README.md), which covers the loops, harnesses and graphs behind these applications.
