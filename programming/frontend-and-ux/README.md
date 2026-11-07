# Frontend and UX

> Enough of the browser, React, accessibility and usability for a backend, data or AI engineer to build a usable interface or judge one, and a chapter on what AI interfaces need that ordinary ones don't: streaming, citations, uncertainty, handoff and failure.
> Study deck: [frontend-and-ux.pptx](slides/frontend-and-ux.pptx), which librarian turns into flashcards (source: [deck.yaml](slides/deck.yaml)).
> Jump to: [Reading order](#reading-order) · [Builds on and feeds into](#builds-on-and-feeds-into) · [Rules of thumb](#rules-of-thumb) · [Layout](#layout) · [Setup](#setup) · [Primary texts](#primary-texts)

---

## What this is

A good model behind a bad interface still gives a bad product. People can't see the retrieval or the evals. They see a page that either tells them what's happening or doesn't. This track is for engineers who don't do frontend full time but keep ending up responsible for one: a demo that became real, an internal tool, a chat over your own documents, or a review of someone else's. The depth is awareness. It won't make you a frontend specialist, and it skips build tooling, routing, server rendering and visual design.

It sits after the [TypeScript track](../typescript/README.md), which teaches the language and async, and links back to it instead of restating it. Chapters 1 to 4 are the general groundwork. [Chapter 5](notes/05-ai-interfaces.md) is the one with no equivalent elsewhere in this course and gets the most care. It inherits the weakness of its field: much UX advice is expert practice, not experiment, and the experiments on AI interfaces use particular tasks, particular models and crowd workers, so they date quickly and transfer loosely. The chapters say which is which. Nothing in this track was tried with real users, and no screen reader was run.

The mental model has three questions. What state is the system really in? Can the person tell, by every route they have to the page? And what can they do about it, including when the answer is wrong or the service has gone away? Chapters 1 and 2 are how you express the state, 3 and 4 are how it reaches people, and 5 applies all of it to an answer that arrives a word at a time and might be false.

## Reading order

The notes follow the [full chapter standard](https://github.com/ramseywise/librarian/blob/main/.claude/skills/pillar/references/pillar-layout.md), not the shorter format of the Python modules.

**The platform**

| # | Note | You can… |
|---|---|---|
| 01 | [HTML, CSS and the DOM](notes/01-html-css-and-the-dom.md) | Say what the browser does with a page, pick the element that brings its behaviour for free, work out which CSS rule wins, and spot an injection sink |
| 02 | [React and state](notes/02-react-and-state.md) | Model a screen as a function of state, make impossible states unrepresentable, and tell when an Effect is the wrong tool |

**People**

| # | Note | You can… |
|---|---|---|
| 03 | [Accessibility](notes/03-accessibility.md) | Do a ten-minute manual pass, measure contrast, announce changes with a live region, and say what automated tools can't see |
| 04 | [UX principles](notes/04-ux-principles.md) | Review a screen with the heuristics and the three response-time limits, write an error message, and read "five users" correctly |

**AI**

| # | Note | You can… |
|---|---|---|
| 05 | [AI interfaces](notes/05-ai-interfaces.md) | Parse a stream and classify how it failed, check citations before showing them, show uncertainty honestly, hand off to a person with context, and treat model output as untrusted |

**Lab:** [a streaming chat page against a local mock server](practice/README.md), with citations, uncertain answers, 18 failure and answer scenarios, handoff and automated tests. Exercises 1 and 2 fit after chapter 2, and the rest after chapter 5. It needs no API key.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [TypeScript: JS for Python developers](../typescript/notes/01-js-for-python-devs.md) | The language every example here is written in |
| [TypeScript: unions and narrowing](../typescript/notes/03-unions-and-narrowing.md) | Chapter 2's state model is a discriminated union |
| [TypeScript: async](../typescript/notes/06-async.md) | Promises, `fetch` and `AbortController`, used here without being retaught |
| [TypeScript: modules and tooling](../typescript/notes/07-modules-and-tooling.md) | How the lab's bundle and `tsc` fit together |
| [TypeScript: runtime validation](../typescript/notes/08-runtime-validation-zod.md) | The types stop at the network, which is where a stream's events come from |
| [TypeScript for AI apps](../typescript/notes/09-typescript-for-ai-apps.md) | The server side of streaming, and this track is the part the user sees |
| [Computer science: networks](../computer-science/notes/06-networks.md) | Why chunks don't respect message boundaries |
| [Software design: testing strategy](../software-design/notes/05-testing-strategy.md) | The lab's planted faults are mutation testing by hand |

**Feeds into**

| Chapter | Why |
|---|---|
| [Application patterns](../../generative-ai/07-agentic-applications/notes/06-application-patterns.md) | Chat, collaborative editing and ambient agents, and what an interface does to judgment |
| [Scoping an AI product](../../generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product.md) | Whether to build the interface at all, and for whom |
| [Real-time multimodal agents](../../generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md) | Where the latency limits get tighter |
| [Agentic search, persistence and streaming](../../generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming.md) | What framework streams produce, and what this track's client has to consume |
| [Generation for RAG](../../generative-ai/02-rag-retrieval/notes/06-generation-for-rag.md) | The plumbing behind citations |
| [Backend: reliability under load](../backend-and-system-design/notes/07-reliability-under-load.md) | The server side of the timeouts, retries and refusals this client has to show |
| [Calibration against human labels](../../generative-ai/08-eval/notes/15-calibration-against-human-labels.md) | What it takes before a confidence number deserves to be shown |
| [Support agent observability](../../generative-ai/06-observability/notes/05-support-agent-observability.md) | Measuring whether handoffs and fallbacks do what you hoped |
| [Autonomy ladder](../../ai-engineering/04-loop-engineering/notes/07-autonomy-ladder.md) | The human side of escalation |
| [Durable execution and interrupts](../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md) | An agent pausing for approval, which is a handoff going the other way |
| [Threat model](../../ai-engineering/09-safety-and-security/notes/01-threat-model.md) and [prompt injection](../../ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks.md) | Why model output is untrusted before it reaches the page |

## Rules of thumb

- Use the element that already does the job. A `<button>` brings focus, Space and Enter, and a role. A `div` brings none.
- Derive what you can. Store the least state that can't be computed, and make one `status` field replace a set of booleans.
- Default to no Effect. Handlers respond to events, and rendering computes from state.
- An automated pass is a floor. It finds some problems, and it can't tell you whether the page is usable. Then use the keyboard.
- A screen update isn't an announcement. Say what changed, once, in a region that already exists.
- Under 0.1 s feels instant, past 1 s people notice the wait, and by 10 s attention is going, so show progress and offer a way out.
- A stream's 200 means it started. Only a terminal event means it finished.
- Treat a clean close with no terminal event as a failure, and keep and label the partial text.
- Don't show a citation you haven't checked, and don't take one as proof the answer is true.
- Show uncertainty from a signal you actually have, in words, with an action next to it.
- Keep a route to a person from every finished state, including a complete answer, and let it fail visibly too.
- Model output is untrusted input to your page: render it as text, allow-list URL schemes, and set a Content Security Policy.

## Layout

```
frontend-and-ux/
├── README.md
├── references.md
├── notes/                 01–05
└── practice/
    ├── README.md          the lab: what to do and what it measured
    ├── check.sh           runs everything (solutions by default)
    ├── run_notes.ts       runs the code blocks in the notes and compares their output
    ├── server/            the mock server, with one scenario per failure
    ├── public/            the page and its stylesheet
    ├── app/               the entry point the bundle starts from
    ├── exercises/         stubs for the parser and reducer, and a naive chat to fix
    ├── solutions/         the worked parser, reducer, client and chat
    └── tests/             unit, browser, axe and planted-fault tests
```

## Setup

You need Node 22.18 or later, which runs the TypeScript directly. `bash practice/check.sh` installs its few dependencies the first time, and no API key is needed. The browser tests need Chromium, once: from `practice/`, run `npx playwright-core install chromium`. Without it, `bash check.sh no-browser` runs the rest and says what it skipped.

The notes' code blocks are small and most run on their own in Node. Blocks of HTML run in Chromium under `run_notes.ts`, and the chapters' expected output is compared with what they print.

## Primary texts

- WHATWG, [HTML Living Standard: server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [MDN Web Docs](https://developer.mozilla.org/)
- React, [the Learn section of react.dev](https://react.dev/learn)
- W3C, [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and the [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/)
- Nielsen Norman Group, [Usability 101](https://www.nngroup.com/articles/usability-101-introduction-to-usability/), [the ten heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) and [Explainable AI in chat interfaces](https://www.nngroup.com/articles/explainable-ai/)
- Google PAIR, [People + AI Guidebook](https://pair.withgoogle.com/chapter/errors-failing/)
- Amershi et al., [Guidelines for Human-AI Interaction](https://doi.org/10.1145/3290605.3300233), CHI 2019

The well-known books (Krug's *Don't Make Me Think*, Norman's *The Design of Everyday Things*) were not accessed for this track, and no claim here rests on their contents. Everything cited was read, and [references.md](references.md) says how much of each.
