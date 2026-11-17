# Frontend and UX

Enough of the browser, React, accessibility and usability for a backend, data or AI engineer to build a usable interface or judge one. Three steps and five chapters, the last on what AI interfaces need that ordinary ones don't: streaming, citations, uncertainty, handoff and failure.

**What you should already know.** The [TypeScript track](../typescript/README.md): every example is written in it, and its [unions](../typescript/notes/03-unions-and-narrowing.md), [async](../typescript/notes/06-async.md) and [runtime validation](../typescript/notes/08-runtime-validation-zod.md) notes are used here without being retaught.

## Lecture

Start with the overview deck, [Frontend and UX](slides/frontend-and-ux.pptx) ([PDF](slides/frontend-and-ux.pdf)), on the same examples as the notes. Librarian turns each slide into a flashcard: the title is the question and the takeaway is the rule that answers it.

## The core

A good model behind a bad interface still gives a bad product. People can't see the retrieval or the evals. They see a page that either tells them what's happening or doesn't. So the track keeps asking three questions of any screen: **what state is the system really in, can the person tell by every route they have to the page, and what can they do about it?** The last includes when the answer is wrong or the service has gone away.

There are three steps. The platform is how you express the state, people is how it reaches them, and AI applies both to an answer that arrives a word at a time and might be false. [Chapter 5](notes/05-ai-interfaces.md) is the one with no equivalent elsewhere in this course and gets the most care.

This track is for engineers who don't do frontend full time but keep ending up responsible for one: a demo that became real, an internal tool, a chat over your own documents, or a review of someone else's. The depth is awareness. It won't make you a frontend specialist, and it skips build tooling, routing, server rendering and visual design. It inherits the weakness of its field: much UX advice is expert practice, not experiment, and the experiments on AI interfaces use particular tasks, particular models and crowd workers, so they date quickly and transfer loosely. The chapters say which is which. Nothing in this track was tried with real users, and no screen reader was run.

## Syllabus

One row per step. **Core concepts** are the ideas the step turns on, **Study** is what to read, **Labs** is what to do afterwards, and **Sources** is where to read more. The lab is one streaming chat page against a local mock server, and it needs no API key. How to run it: [practice/README.md](practice/README.md).

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. The platform:** the browser and React | Use the element that already does the job: a `<button>` brings focus, Space and Enter, and a role. A screen is a function of state. Store the least state that can't be computed, and let one `status` field replace a set of booleans. Default to no Effect. | [1 HTML, CSS and the DOM](notes/01-html-css-and-the-dom.md) · [2 React and state](notes/02-react-and-state.md) | [Lab](practice/README.md), exercises 1 and 2, after chapter 2: the stream parser and the state reducer | [MDN Web Docs](https://developer.mozilla.org/) · React, [the Learn section of react.dev](https://react.dev/learn) |
| **2. People:** accessibility and usability | An automated pass is a floor, so then use the keyboard. A screen update isn't an announcement: say what changed, once, in a region that already exists. Under 0.1 s feels instant, past 1 s people notice the wait, and by 10 s attention is going. | [3 Accessibility](notes/03-accessibility.md) · [4 UX principles](notes/04-ux-principles.md) | The ten-minute manual pass from chapter 3, on the lab's page · the lab's axe tests, read for what they can't see | W3C, [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and the [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/) · Nielsen Norman Group, [Usability 101](https://www.nngroup.com/articles/usability-101-introduction-to-usability/) and [the ten heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) |
| **3. AI:** an answer that streams and might be wrong | A stream's 200 means it started, and only a terminal event means it finished. Keep and label partial text. Don't show a citation you haven't checked. Show uncertainty from a signal you actually have, in words, with an action next to it. Keep a route to a person from every finished state. Model output is untrusted input to your page. | [5 AI interfaces](notes/05-ai-interfaces.md) | [Lab](practice/README.md), the remaining exercises, after chapter 5: citations, uncertain answers, 18 failure and answer scenarios, handoff and automated tests | WHATWG, [server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html) · Amershi et al., [Guidelines for Human-AI Interaction](https://doi.org/10.1145/3290605.3300233) · Google PAIR, [People + AI Guidebook](https://pair.withgoogle.com/chapter/errors-failing/) · Nielsen Norman Group, [Explainable AI in chat interfaces](https://www.nngroup.com/articles/explainable-ai/) · the experiments on trust and reliance: [references.md](references.md) |

The notes follow the [full chapter standard](https://github.com/ramseywise/librarian/blob/main/.claude/skills/pillar/references/pillar-layout.md), not the shorter format of the Python modules. There are no frontend drills yet: the [TypeScript drills](../drills/typescript/README.md) are where HTML and CSS problems will go.

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

## Primary texts

- WHATWG, [HTML Living Standard: server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [MDN Web Docs](https://developer.mozilla.org/)
- React, [the Learn section of react.dev](https://react.dev/learn)
- W3C, [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and the [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/)
- Nielsen Norman Group, [Usability 101](https://www.nngroup.com/articles/usability-101-introduction-to-usability/), [the ten heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) and [Explainable AI in chat interfaces](https://www.nngroup.com/articles/explainable-ai/)
- Google PAIR, [People + AI Guidebook](https://pair.withgoogle.com/chapter/errors-failing/)
- Amershi et al., [Guidelines for Human-AI Interaction](https://doi.org/10.1145/3290605.3300233), CHI 2019

The well-known books (Krug's *Don't Make Me Think*, Norman's *The Design of Everyday Things*) were not accessed for this track, and no claim here rests on their contents. Everything cited was read, and [references.md](references.md) says how much of each. The deck is built from [`slides/deck.yaml`](slides/deck.yaml) with `make slides PILLAR=programming/frontend-and-ux`.

## Next

Start with step 1, **The platform**: read [1 HTML, CSS and the DOM](notes/01-html-css-and-the-dom.md), and do the lab's first two exercises once you have read chapter 2.

After step 3 you can build a chat page that tells the truth about its own state. What sits behind that page is in [application patterns](../../generative-ai/07-agentic-applications/notes/06-application-patterns.md), and whether to build it at all is in [scoping an AI product](../../generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product.md).
