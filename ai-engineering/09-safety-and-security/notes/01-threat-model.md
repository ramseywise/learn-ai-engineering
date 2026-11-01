---
origin: synthesis
sources:
  - https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
  - https://arxiv.org/abs/2302.12173
  - https://genai.owasp.org/llm-top-10/
  - https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications/
  - https://atlas.mitre.org/
  - https://doi.org/10.6028/NIST.AI.100-2e2023
  - https://arxiv.org/abs/2301.13188
  - https://arxiv.org/abs/2403.06634
  - https://arxiv.org/abs/2403.09539
  - https://arxiv.org/abs/2502.07776
  - https://arxiv.org/abs/2506.15674
  - https://arxiv.org/abs/2608.09867
  - https://arxiv.org/abs/2407.20516
  - https://arxiv.org/abs/2308.12833
  - https://arxiv.org/abs/2609.15383
  - https://arxiv.org/abs/2608.25776
confidence: medium
cleaned: 2026-11-01
---

# 1 — The Threat Model

> Before choosing a defence, write down what you are protecting, who can reach it, and which paths connect the two. For an LLM system the decisive question is whether untrusted text can reach both private data and a way out.

A customer writes to a support agent asking why a refund is late, and the agent looks up the order, searches the help centre, reads the customer's last few tickets, and drafts an email. Every one of those steps is a feature, and together they let anyone who can get text into a ticket or a help page address the agent directly. This chapter builds the map you need before you can reason about that: what the system holds, who can reach it, and which combinations of capability turn a mistake into a breach.

We use one system through the whole pillar. **Harbour** is a support agent for an online shop. It can read a retrieved help centre, read the current customer's orders and tickets, and send email. It is small enough to hold in your head, and it has all the properties that make LLM applications hard to secure.

## Why the usual defence does not transfer

SQL injection is a solved problem in the sense that the fix is known. A parameterised query sends the code and the data on separate channels, and the database can't confuse them, because the protocol doesn't allow it. Language models have no such separation. A prompt is one sequence of tokens, and the system prompt, the user's message and the retrieved page are all just positions in that sequence. Roles and delimiters are hints that the model has been trained to respect, and a model that has been trained to respect something can still be persuaded not to.

Greshake et al. made the consequence precise in [arXiv:2302.12173](https://arxiv.org/abs/2302.12173) (Greshake et al., AISec@CCS 2023). They argue that LLM-integrated applications blur the line between data and instructions, and they name **indirect prompt injection**: an attacker who never talks to the model plants a prompt in data it is likely to retrieve. They demonstrated this against real systems including Bing's GPT-4 chat and code-completion engines, and they describe processing a retrieved prompt as being like arbitrary code execution, since it can manipulate the application's functionality and control how other APIs are called.

That framing changes the design question. You can't ask "how do I stop the model following instructions in this text?", because no current technique gives a guarantee. You ask "if the model does follow them, what can happen?" The answer to the second question is something you control, in ordinary code, outside the model. This is the idea the whole pillar rests on.

The attack catalogue and prompt-level defences are in [Adversarial prompting](../../01-prompt-engineering/notes/10-adversarial-prompting.md), and they are worth reading first if the terms are new. This chapter is about the system around the model.

## Draw the system first

A threat model starts as a picture. You draw the components, mark where data crosses from one trust level to another, and list what is worth stealing or breaking. Here is Harbour.

```text
              UNTRUSTED                 |            TRUSTED
                                        |
 customer message  --------------+      |
 help-centre page  ----(retrieval)--+   |
 past ticket text  ----(tool)----+  |   |
                                 v  v   |
                           +-------------------+     +------------------+
                           |       model       |<--->|  system prompt   |
                           +-------------------+     +------------------+
                              |            |    |
                     tool call|            |    |
                              v            v    |
                       orders / tickets   send_email ---> the outside world
                       (private data)     (way out)  |
                                                     |
 every box the model's output reaches is reached by whatever the model read
```

Three things stand out once it is on paper. Past tickets look internal, but a customer wrote them, so they sit on the untrusted side. The help centre may be editable by more people than the team assumes, including vendors, contractors, and anyone who can file a public comment. And the arrow out of the model isn't one arrow: it fans out to everything the model can call, so whatever influenced the model can reach all of those.

[Execution boundaries](../../03-harness-engineering/notes/04-execution-boundaries.md#trust-zones) gives a useful trust table for this step. The row people miss is tool inputs, which are composed by the model and therefore semi-trusted. Validate them as you would validate a request from the public internet.

For each component, write down four things:

| Question | Harbour's answer |
|---|---|
| **Assets:** what would hurt to lose? | Customer PII, order history, the ability to send mail from the company's domain, refund authority |
| **Actors:** who wants them or can break them by accident? | A fraudster, a curious customer, a competitor, a vendor with help-centre access, an honest user with an odd request |
| **Entry points:** where does text get in? | Chat, email body, attachments, help-centre pages, past tickets, tool results, images |
| **Exits:** how can information leave? | Outgoing email, the chat reply, links and images rendered in it, logs, a third-party tool API |

## The lethal trifecta

Most of what can go seriously wrong reduces to a single test, which Simon Willison named [the lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) in 2025. The three capabilities are access to private data, exposure to untrusted content, and the ability to communicate externally. An agent that combines all three can be tricked into reading the data and sending it to an attacker.

The value of the idea is that it is a structural check on the design, not a judgement about the model. A system lacking any one leg can still misbehave, but it can't do this particular thing. So the check can be run in code against a list of tools, before anything ships.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Tool:
    name: str
    reads_private: bool = False      # returns data the attacker should not have
    reads_untrusted: bool = False    # returns text an outsider can influence
    sends_external: bool = False     # moves data outside the trust boundary

def trifecta(tools):
    legs = {
        "private data": [t.name for t in tools if t.reads_private],
        "untrusted content": [t.name for t in tools if t.reads_untrusted],
        "external communication": [t.name for t in tools if t.sends_external],
    }
    return legs, all(legs.values())

harbour = [
    Tool("search_help_centre", reads_untrusted=True),
    Tool("get_orders", reads_private=True),
    Tool("get_tickets", reads_private=True, reads_untrusted=True),
    Tool("send_email", sends_external=True),
]

for label, tools in [
    ("full agent", harbour),
    ("no email tool", [t for t in harbour if t.name != "send_email"]),
    ("no tickets or help centre",
     [t for t in harbour if not t.reads_untrusted]),
]:
    legs, lethal = trifecta(tools)
    print(f"{label:27} lethal={lethal}")
    for leg, names in legs.items():
        print(f"    {leg:24} {names}")
```

Output:

```text
full agent                  lethal=True
    private data             ['get_orders', 'get_tickets']
    untrusted content        ['search_help_centre', 'get_tickets']
    external communication   ['send_email']
no email tool               lethal=False
    private data             ['get_orders', 'get_tickets']
    untrusted content        ['search_help_centre', 'get_tickets']
    external communication   []
no tickets or help centre   lethal=False
    private data             ['get_orders']
    untrusted content        []
    external communication   ['send_email']
```


Look at the last configuration: removing the untrusted tools breaks the trifecta in this check, and yet the customer's own message is still untrusted text. The tool list should really have an entry for the chat input itself. A correct model of Harbour must include every entry point from the worksheet, and this is the most common way a check like this gives false comfort. The practical moves to break the trifecta are also rarely this clean, so [chapter 2](02-prompt-injection-and-jailbreaks.md) develops patterns that keep all three capabilities while separating them in time or by process.

The trifecta covers exfiltration, which is the most common high-severity outcome. It doesn't cover integrity. An agent with untrusted input and a refund tool can lose money without private data or an external channel. So generalise the test: **for every consequential action, can untrusted text cause it?** Exfiltration is the case where the consequential action is "send data out".

## Rating the paths

Once you know the paths, you need to rank them, because you won't fix them all at once. Security teams have many scoring systems. For a first pass, it is enough to enumerate source, sink and whether a human or a control sits between them, then rank by severity of the sink.

```python
from itertools import product

sources = {"customer_message": "untrusted", "help_page": "untrusted",
           "past_ticket": "untrusted", "system_prompt": "trusted"}

sinks = {  # severity 1-3, and whether a control already gates the action
    "reply_to_this_customer": (1, False),
    "render_link_in_chat":    (2, False),
    "send_email":             (3, True),   # requires human approval
    "issue_refund":           (3, False),
}

rows = []
for (src, trust), (sink, (severity, gated)) in product(sources.items(), sinks.items()):
    if trust == "trusted":
        continue
    # A gate does not remove the path. It reduces the exposure.
    rows.append((severity * (1 if gated else 2), src, sink, "gated" if gated else "OPEN"))

for score, src, sink, state in sorted(rows, reverse=True)[:6]:
    print(f"{score}  {src:17} -> {sink:23} {state}")
print(f"\n{len(rows)} untrusted paths in total")
```

Output:

```text
6  past_ticket       -> issue_refund            OPEN
6  help_page         -> issue_refund            OPEN
6  customer_message  -> issue_refund            OPEN
4  past_ticket       -> render_link_in_chat     OPEN
4  help_page         -> render_link_in_chat     OPEN
4  customer_message  -> render_link_in_chat     OPEN

12 untrusted paths in total
```


The arithmetic here is deliberately crude and the weights are ours, chosen to order this example rather than taken from a standard. What matters is the shape of the output. The top of the list is an ungated, high-severity action reachable from every untrusted source, and that is the first fix. A list of twelve paths is also a useful thing in itself, because it makes the system's exposure visible to someone who thought they had "a chatbot".

## Shared vocabularies

You don't need to invent categories, and using the published ones makes your threat model readable to a security team. Four are worth knowing, and they do different jobs.

**OWASP Top 10 for LLM Applications** ([2025 list](https://genai.owasp.org/llm-top-10/)) is a checklist of application-level risks: prompt injection (LLM01), sensitive information disclosure (LLM02), supply chain (LLM03), data and model poisoning (LLM04), improper output handling (LLM05), excessive agency (LLM06), system prompt leakage (LLM07), vector and embedding weaknesses (LLM08), misinformation (LLM09) and unbounded consumption (LLM10). Walk Harbour through it and each one turns into a concrete question. LLM05 asks whether the chat UI renders a link the model wrote. LLM06 asks whether the agent really needs a refund tool. LLM10 asks what stops a single user burning your whole budget, which connects to the [cost envelope](../../03-harness-engineering/notes/04-execution-boundaries.md#cost-envelope).

**OWASP Top 10 for Agentic Applications** ([2026 edition](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications/)) does the same for systems that plan and act, and its concerns include goal hijacking, tool misuse, memory poisoning and trust between agents. [Execution boundaries](../../03-harness-engineering/notes/04-execution-boundaries.md#the-agentic-risk-map) maps a similar list of agentic risks onto harness controls.

**[MITRE ATLAS](https://atlas.mitre.org/)** is written in the form of ATT&CK: adversary tactics and techniques against ML systems, plus case studies. Use it when you want to describe how an attack proceeds in steps, or when you need to talk to a security operations team that already thinks this way.

**NIST AI 100-2** ([the 2023 edition we hold](https://doi.org/10.6028/NIST.AI.100-2e2023) and the [2025 update](https://csrc.nist.gov/pubs/ai/100/2/e2025/final)) is a taxonomy for the whole field. It sorts attacks on models by what they do: **evasion** (changing an input to change the output), **poisoning** (corrupting training data or the model), **privacy** (extracting data or the model itself), and **abuse** (for generative AI, turning the system to a purpose it wasn't meant for, including through indirect injection). Its value is the clean separation of goals, which prevents a discussion from sliding between "our model said something rude" and "someone copied our weights".

## Data security and privacy

Privacy failures are the threats most likely to reach you without an adversary. Several separate channels leak.

**Retrieval leaks across users.** If Harbour's vector index holds all customers' tickets and filters results after retrieval, or relies on the model not to mention other customers, then any phrasing that retrieves the wrong row exposes it. OWASP lists this as a vector and embedding weakness (LLM08). The fix belongs in the query. Access control is a filter on what the retriever may return for this caller, and it is applied before the model sees anything.

```python
DOCS = [
    {"id": "t1", "owner": "ana",  "text": "Refund for order 118 is delayed"},
    {"id": "t2", "owner": "ben",  "text": "Refund to card ending 4242 failed"},
    {"id": "h1", "owner": None,   "text": "Refunds take five working days"},
]

def score(query, text):
    q, t = set(query.lower().split()), set(text.lower().split())
    return len(q & t)

def search_unsafe(query, k=2):
    # Trusts the model or the prompt to hide other people's rows.
    return sorted(DOCS, key=lambda d: -score(query, d["text"]))[:k]

def search_scoped(query, caller, k=2):
    # The caller comes from the authenticated session, never from the model.
    allowed = [d for d in DOCS if d["owner"] in (None, caller)]
    return sorted(allowed, key=lambda d: -score(query, d["text"]))[:k]

q = "refund to card failed"
print("unsafe:", [d["id"] for d in search_unsafe(q)])
print("scoped:", [d["id"] for d in search_scoped(q, caller="ana")])
```

Output:

```text
unsafe: ['t2', 't1']
scoped: ['t1', 'h1']
```


The comment in `search_scoped` is the load-bearing line. If the caller's identity is a tool argument the model fills in, then an injection can simply set it to someone else. Identity has to come from the session.

**Reasoning traces leak.** It is natural to assume a model's internal reasoning is private. [arXiv:2506.15674](https://arxiv.org/abs/2506.15674) (Green et al., EMNLP 2025) tests this for reasoning models acting as personal agents and finds that traces frequently contain sensitive user data, which can be extracted through injection or leak accidentally into the output. Raising the reasoning budget amplifies the leakage in the traces even as the final answers become more cautious. So traces are a data store with the same sensitivity as the input, and they need the same retention and access rules. They can also be a target in their own right: [arXiv:2608.09867](https://arxiv.org/abs/2608.09867) (Panfilov et al., 2026-08, preprint) studies recovering hidden reasoning from proprietary APIs that return it only in encrypted form.

**Logs leak.** Traces, evaluation exports and fine-tuning datasets copy every sensitive value they touch into systems with wider access than production. Redact before logging, and treat a trace store as production data. [Chapter 6](06-incident-response.md) returns to what to retain.

**Models leak what they were trained on.** [arXiv:2301.13188](https://arxiv.org/abs/2301.13188) (Carlini et al., USENIX Security 2023) extracted over a hundred near-copies of training images from Stable Diffusion, largely from images duplicated many times in the data, and found diffusion models less private than GANs on the same data. The lesson for a team fine-tuning on customer data is that a fine-tuned model is a derivative of that data, and should inherit its access rules. Deleting a record from the source doesn't delete it from the weights. [arXiv:2407.20516](https://arxiv.org/abs/2407.20516) (Liu et al., 2024-07, preprint) surveys machine unlearning in generative AI, and reading it is the fastest way to see that this is a research area, not a feature you can rely on.

**Shared infrastructure leaks.** Prompt caching makes cached prompts faster, so response time depends on what somebody else recently sent. [arXiv:2502.07776](https://arxiv.org/abs/2502.07776) (Gu et al., ICML 2025) audited real APIs with a statistical timing test and detected global cache sharing across users at seven providers. For your own system, ask whether a cache is scoped per user or organisation. Do not assume this, and check the provider's documentation.

**The model itself is an asset.** [arXiv:2403.06634](https://arxiv.org/abs/2403.06634) (Carlini et al., ICML 2024) showed that an attacker with only API access can recover the embedding projection layer of production models, at under $20 for two OpenAI models and an estimated under $2,000 for gpt-3.5-turbo, and that providers added defences after disclosure. [arXiv:2403.09539](https://arxiv.org/abs/2403.09539) (Finlayson et al., 2024-03, preprint) starts from the observation that most models' outputs lie in a low-dimensional subspace, and shows how much non-public information follows from a small number of queries, costing under $1,000 for gpt-3.5-turbo. If you host a proprietary model, full logprobs and logit bias are part of your attack surface. If you are a typical API customer, this is mainly a reason to know that "API access only" is a weaker boundary than it sounds.

## Supply chain

Your system also trusts code and data that other people wrote. OWASP files this under LLM03 and LLM04. The main paths are:

- **Model weights.** A `.ckpt` is a Python pickle and can execute code on load, while `.safetensors` holds only tensors. Pin a hash, and load the safer format.
- **Datasets.** A training set or fine-tuning file you didn't build may be poisoned. NIST's poisoning class covers this.
- **MCP servers and plugins.** Installing one adds both a code dependency and new text the model will read as tool descriptions. [Chapter 4](04-tool-and-execution-sandboxing.md) builds a pin check for this.
- **Skills and memories an agent writes for itself.** This is the newest path and it runs inside your own trust boundary. [arXiv:2608.25776](https://arxiv.org/abs/2608.25776) (Wu et al., 2026-08, preprint) plants malicious skills in the library of self-evolving coding agents, and measures how often the agent writes new malicious skills of its own. Across six models and 153 SWE-bench Verified tasks that rate ranged from 20.3% to 41.8%, and libraries ended with 4.9 to 9.0 times as many malicious skills as were planted. After the planted ones were removed, the highest retained rate at round five was still 68%. Its counter-prompt defence cut the rate to at most 6.7%, as reported by the authors. So cleaning up after a poisoned artefact isn't one deletion, a point we return to in [chapter 6](06-incident-response.md).

## Misuse: when your user is the threat

So far the adversary has been attacking your users or you. Sometimes your user is the adversary, and your product is the tool. [arXiv:2308.12833](https://arxiv.org/abs/2308.12833) (Mozes et al., 2023-08, preprint) organises this space into threats (fraud, impersonation, malware generation and so on), prevention measures, and the vulnerabilities of those measures, and it is a good structured starting point.

Per-request refusal isn't the entire answer. [arXiv:2609.15383](https://arxiv.org/abs/2609.15383) (Russinovich et al., 2026-09, preprint) measures what they call capability laundering: a less capable model splits a harmful task into subproblems that each look harmless, consults an aligned frontier model on each, and combines the answers. Unlike a jailbreak, no single response is harmful, so a per-response filter sees nothing wrong. In their CyBench evaluation, Gemma-4-31B recovered 8 of 14 candidate tasks using GPT-5.5 as a consultant. The design conclusion is that some risks are visible only across many requests, which pushes defence toward account-level monitoring, the topic of [chapter 6](06-incident-response.md).

## Safety without an attacker

Not every failure has an adversary. An honest user asks Harbour about a medical refund and gets confident, wrong policy advice. A polite customer gets worse service than another with a different name. An agent with a refund tool over-refunds because of a bug in its retrieval. The same worksheet handles these: replace "actor" with "ordinary use" and keep the assets and paths. [Chapter 3](03-guardrail-models.md) treats the harm and fairness side, and [Failure modes and guardrails](../../04-loop-engineering/notes/09-failure-modes-and-guardrails.md) covers the operational accidents of loops.

## Writing it down

A threat model that lives in somebody's head expires when they change teams. A useful one is a page, kept next to the code and revised whenever a tool is added.

```text
System: Harbour          Owner: support-platform          Reviewed: 2026-11-01

Assets        customer PII; order history; company mail domain; refund authority
Entry points  chat; email body and attachments; help pages; past tickets; images
Exits         email; chat reply incl. rendered links; logs; vendor tool APIs
Trifecta      PRESENT (tickets + orders + email)

Path                               Severity  Control             Status
help page -> send_email            high      human approval      gated
ticket    -> issue_refund          high      none                FIX FIRST
any       -> rendered link         medium    allow-list          planned
caller id set by model             high      session identity    done

Assumptions   model will follow injected text sometimes
              provider cache scope: per organisation (checked in provider docs)
Next review   when any tool or data source is added
```

The assumption line is the honest part. It tells the reader which defences are designed to work even when the model is fooled, and it is what the next chapter will take as its premise.

## Pitfalls

- **Modelling tools and forgetting the input.** The user's message is an untrusted source too, so removing a retrieval tool doesn't remove the leg.
- **Treating internal data as trusted.** Tickets, CRM notes and wikis are often written by outsiders or copied from them.
- **Letting the model supply identity.** A `user_id` argument the model fills in is a request for someone else's data.
- **Filtering results after retrieval, or in the prompt.** Access control must happen before the model sees the row.
- **Assuming hidden reasoning is private.** Traces can hold the same data as the input and must be stored accordingly.
- **Writing the threat model once.** Each new tool can complete a trifecta that wasn't there yesterday.
- **Treating a list as a model.** OWASP tells you what to ask. Only your diagram tells you the answer.

## Try it

1. Add `Tool("chat_input", reads_untrusted=True)` to the third configuration of `trifecta`. What does the check report now, and which two changes could make it not lethal?
2. In the path ranking, set `issue_refund`'s gate to `True`. What is now at the top of the list? What does this tell you about the limit of fixing the top row only?
3. In `search_scoped`, change the design so that `caller` is taken from a tool argument the model provides. Describe the injection this enables, without writing it.
4. Pick an application you use at work and write the one-page threat model from the template above. How many paths did you not know about before you wrote it?

<details><summary>Answers</summary>

1. It reports `lethal=True` if `send_email` is present, since orders supply private data, chat input supplies untrusted content and email is the exit. Removing email, or removing all private-data tools, makes it non-lethal.
2. `render_link_in_chat` takes over at score 4, with the now-gated refund and email paths at 3 below it. A gate lowers a path without removing it, and medium-severity ungated exits become the new priority. A rendered link is also an exit that can carry data in its URL, so it deserves more than its severity suggests.
3. Any retrieved text could cause the model to pass another customer's identifier, and the retriever would obediently return that customer's rows. The scoping is now only as strong as the model's resistance to injection, which is what we assumed was unreliable.
4. There's no single answer. Most people find at least one source they had considered internal that outsiders can write to.

</details>

## Interview questions

| Question | Answer |
|---|---|
| Why is prompt injection unlike SQL injection? | SQL has a protocol-level separation of code and data, so parameterised queries remove the bug class. A prompt is one token sequence, and roles are only trained conventions, so no equivalent guarantee exists. |
| What is the lethal trifecta? | Access to private data, exposure to untrusted content and the ability to communicate externally. Together they let injected text steal data, and removing any one prevents that specific outcome. |
| What does the trifecta leave out? | Integrity. An agent with untrusted input and a refund or delete tool can do damage with no private data or exit. Generalise to: can untrusted text cause any consequential action? |
| How do you enforce access control in RAG? | Filter by the authenticated caller inside the retriever, before the model sees results. The caller comes from the session and is never a model-supplied argument. |
| OWASP LLM Top 10 or MITRE ATLAS, which do you use? | OWASP as an application checklist, ATLAS to describe the steps of an attack, often when working with a security team. NIST AI 100-2 gives the taxonomy behind both. |
| Are reasoning traces safe to log freely? | No. Green et al. found they frequently contain sensitive user data, more so with larger reasoning budgets. Give them the same retention and access rules as the input. |
| What makes misuse hard to catch per request? | Capability laundering splits a harmful task into harmless-looking subtasks, so no single response is harmful. Detection needs a view across requests. |

## Next

The threat model assumes the model will sometimes follow injected text. [Prompt injection and jailbreaks](02-prompt-injection-and-jailbreaks.md) explains why that assumption holds and how to build a system that is safe under it.
