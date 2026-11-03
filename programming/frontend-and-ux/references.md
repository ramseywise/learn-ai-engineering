---
origin: curated
sources:
  - https://html.spec.whatwg.org/multipage/server-sent-events.html
  - https://developer.mozilla.org/
  - https://react.dev/learn
  - https://www.w3.org/TR/WCAG22/
  - https://www.w3.org/WAI/ARIA/apg/
  - https://www.nngroup.com/articles/
  - https://pair.withgoogle.com/chapter/errors-failing/
  - https://doi.org/10.1145/3290605.3300233
confidence: high
cleaned: 2026-11-02
---
# References: frontend and UX

Every row here was read for this track, and the "Read" column says how much. "Parts" means the sections a chapter relies on, not the whole work, so don't take a row as a claim about anything beyond those parts. Each page was saved as text. The sections named were read, and independent citation checks then compared each chapter's claims with the saved copies. "Whole paper" means an extraction pass read every page, and the numbers in the chapter were then checked against the paper's text.

Links were checked on 2026-11-03 and returned 200 to an automated request, with two exceptions. The Microsoft copy of Amershi et al. and its DOI now refuse automated requests. The paper was fetched from Microsoft earlier in this work and read in full from that copy.

## Books not accessed

These are the standard books on the subject. They weren't available to read, so no chapter cites their contents.

| Book | Instead, this track read | Would add |
|---|---|---|
| Steve Krug, *Don't Make Me Think* | Nielsen's Usability 101 and the ten heuristics | A longer practical treatment of web usability |
| Don Norman, *The Design of Everyday Things* | Chan on mental models, and PAIR's Mental Models chapter | The fuller account of mental models, affordances and error |

## Pages that couldn't be read

No chapter cites these.

| Page | What happened |
|---|---|
| `https://www.nngroup.com/articles/screen-readers/` | 404 |
| `https://pair.withgoogle.com/guidebook/` and `/guidebook/chapters/errors-and-graceful-failure` | 200 with no readable text, because the page needs script. The `/chapter/` addresses below did work |
| Microsoft's HAX Toolkit | Seen only lightly, so not cited |

## Core papers

| Paper | Read | Why | Maps to |
|---|---|---|---|
| Amershi et al., [Guidelines for Human-AI Interaction](https://www.microsoft.com/en-us/research/uploads/prod/2019/01/Guidelines-for-Human-AI-Interaction-camera-ready.pdf), CHI 2019, [doi:10.1145/3290605.3300233](https://doi.org/10.1145/3290605.3300233) | Whole paper | The 18 guidelines, and what the study behind them did and didn't test | 05 |
| Liu, Zhang, Liang, [Evaluating Verifiability in Generative Search Engines](https://arxiv.org/abs/2304.09848), Findings of EMNLP 2023 | Whole paper | How often 2023 citations supported their sentences, and the precision and utility correlation | 05 |
| Kim et al., ["I'm Not Sure, But..."](https://arxiv.org/abs/2405.00623), FAccT 2024 | Whole paper | Hedging wording, reliance and trust, in a pre-registered study | 05 |
| Bansal et al., [Does the Whole Exceed its Parts?](https://arxiv.org/abs/2006.14779), CHI 2021 | Whole paper | Explanations gave no significant net accuracy gain over confidence alone | 05 |
| Buçinca, Malaya, Gajos, [To Trust or to Think](https://arxiv.org/abs/2102.09692), CSCW 2021 | Whole paper | Cognitive forcing on wrong-AI items, and what it cost in ratings | 05 |

## Standards and specifications

| Source | Read | Maps to |
|---|---|---|
| WHATWG, [HTML Living Standard: server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html) | Parts: the `EventSource` interface, parsing an event stream, keep-alive authoring notes | 05, lab parser |
| WHATWG, [HTML Living Standard: implicit submission](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#implicit-submission) | Parts: that section | 01 |
| W3C, [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Parts: the criteria in chapter 3's table, and the contrast ratio definition | 03 |
| W3C, [Understanding WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/): Conformance, Keyboard, Focus Visible, Focus Not Obscured, Target Size, Contrast, Reflow, Name Role Value, Error Identification, Use of Color, Status Messages, [Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) | Parts: intent and definitions of each | 03, 05 |
| W3C, ARIA Authoring Practices: [Read Me First](https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/), [Keyboard Interface](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/), [Accessible Names](https://www.w3.org/WAI/ARIA/apg/practices/names-and-descriptions/), [Disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/) | Parts | 03 |
| W3C WAI, [Selecting Evaluation Tools](https://www.w3.org/WAI/test-evaluate/tools/selecting/), [Involving Users](https://www.w3.org/WAI/test-evaluate/involving-users/) | Parts: what tools can't check, and why people are needed | 03 |

## MDN

| Source | Read | Maps to |
|---|---|---|
| [How browsers work](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work), [DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model), [Semantics](https://developer.mozilla.org/en-US/docs/Glossary/Semantics), [HTML for accessibility](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Accessibility/HTML) | Parts | 01 |
| [button](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button), [Your first form](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Your_first_form), [Events](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Events), [Event bubbling](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling), [innerHTML](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML) | Parts | 01 |
| [Cascade](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Introduction), [Specificity](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity), [Box model](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Box_model/Introduction), [Flexbox](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Flexbox), [CSS grid layout](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Grids), [Media queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Media_queries/Using), [prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) | Parts | 01 |
| [ARIA live regions](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions), [aria-busy](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-busy) | Parts | 03, 05 |
| [Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events), [Using readable streams](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams), [AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController), [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP), [the a element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/a) | Parts | 05 |

## React docs

| Source | Read | Maps to |
|---|---|---|
| [Thinking in React](https://react.dev/learn/thinking-in-react), [State: a component's memory](https://react.dev/learn/state-a-components-memory), [State as a snapshot](https://react.dev/learn/state-as-a-snapshot), [Queueing updates](https://react.dev/learn/queueing-a-series-of-state-updates), [Choosing the state structure](https://react.dev/learn/choosing-the-state-structure), [Sharing state](https://react.dev/learn/sharing-state-between-components) | Parts | 02 |
| [Rendering lists](https://react.dev/learn/rendering-lists), [Preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state), [Extracting state logic into a reducer](https://react.dev/learn/extracting-state-logic-into-a-reducer), [Keeping components pure](https://react.dev/learn/keeping-components-pure) | Parts | 02 |
| [Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects), [You might not need an Effect](https://react.dev/learn/you-might-not-need-an-effect), [Common components](https://react.dev/reference/react-dom/components/common), legacy [Introducing JSX](https://legacy.reactjs.org/docs/introducing-jsx.html) | Parts | 02 |

## Usability and AI design guidance

| Source | Read | Maps to |
|---|---|---|
| Nielsen, [Usability 101](https://www.nngroup.com/articles/usability-101-introduction-to-usability/), [Response Times](https://www.nngroup.com/articles/response-times-3-important-limits/), [Ten Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/), [Test with 5 Users](https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/) | Parts | 04 |
| Sherwin, [Progress Indicators](https://www.nngroup.com/articles/progress-indicators/); Budiu, [Recognition and Recall](https://www.nngroup.com/articles/recognition-and-recall/); Chan, [Mental Models](https://www.nngroup.com/articles/mental-models/); Neusesser and Sunwall, [Error-Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/) | Parts | 04 |
| Chan, [Explainable AI in Chat Interfaces](https://www.nngroup.com/articles/explainable-ai/) | Parts: citations, reasoning traces and disclaimers | 05 |
| Google PAIR, People + AI Guidebook: [Mental Models](https://pair.withgoogle.com/chapter/mental-models/), [Explainability + Trust](https://pair.withgoogle.com/chapter/explainability-trust/), [Feedback + Control](https://pair.withgoogle.com/chapter/feedback-controls/), [Errors + Graceful Failure](https://pair.withgoogle.com/chapter/errors-failing/) | Parts | 05 |

## Tools, surveys and vendor documentation

Vendor and survey figures here are flagged as such where a chapter uses them.

| Source | Read | Maps to |
|---|---|---|
| Deque, [axe-core README](https://github.com/dequelabs/axe-core) | Parts: the 57% figure, and "incomplete" results | 03, lab |
| Playwright, [Snapshot testing](https://playwright.dev/docs/aria-snapshots) | Parts | 03, lab |
| WebAIM, [Million 2026](https://webaim.org/projects/million/), [Screen Reader User Survey #10](https://webaim.org/projects/screenreadersurvey10/) | Parts: the leading failures, and which readers people use | 03 |
| Anthropic, [Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming), [Citations](https://platform.claude.com/docs/en/build-with-claude/citations); OpenAI, [Streaming API responses](https://platform.openai.com/docs/guides/streaming-responses) | Parts: event types, error events, citation shape | 05, lab mock server |
| nginx, [proxy_buffering](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffering) | Parts: that directive | 05 |
| OWASP, [LLM05:2025 Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/) | Parts | 05 |
