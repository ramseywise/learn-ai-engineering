# Lab: a streaming chat that tells the truth about itself

> A small chat page for a made-up help centre, "Harbour", talking to a local mock server that misbehaves on demand. You'll write the stream parser and the state machine, then repair a chat that only works in a demo, until it holds up under citations, uncertain answers, failures, a keyboard and a handoff to a person.

The mock server is the point. It needs no API key, no model runs, and its answers are scripted, so every failure can be repeated on purpose. It also means nothing here says how good a real model's answers are. The harbour, the help-centre text and the answers are all invented for this lab. The tests are written for the worked solution, so they show that the behaviours hold, and not that the design suits people: nobody has used this page in a study. It maps to all five chapters, and most of all to [chapter 5](../notes/05-ai-interfaces.md).

## Run it

You need Node 22.18 or later. The first run installs the dependencies with `npm ci`. The browser tests need Chromium once: `npx playwright-core install chromium`. From this folder:

```bash
bash check.sh              # the worked solution: everything
bash check.sh exercises    # your copy, which fails until you've written it
bash check.sh no-browser   # everything that doesn't need Chromium, and says what it skipped
npm start                  # serve the page at http://localhost:5174 (PORT changes it)
```

`npm start` serves the worked solution, and `TARGET=exercises npm start` serves yours.

```text
ok    typecheck              (tsc --noEmit, 0 errors)
ok    unit tests             (55 of 55 tests pass, target: solutions)
ok    browser tests          (34 of 34 tests pass in headless Chromium, target: solutions)
ok    axe blind spots        (6 of 6 tests pass: planted faults axe does not report)
ok    planted faults         (18 of 18 planted faults caught)
ok    notes' code            (18 blocks run from 5 notes, 16 with output compared, 1 marked no-run, 0 browser blocks not run, 0 failed)
All checks pass. Not run: Safari, Firefox, any screen reader, any test with people.
```

That's Node v22.23.2, with Chromium headless. The last line of that output matters as much as the others.

## What a pass does and doesn't show

| Checked here, by machine | Not checked by anything here |
|---|---|
| Behaviour in headless Chromium: real key presses, real network to the mock server | Safari and Firefox |
| Parser and reducer rules, in Node | A screen reader. The accessibility tree the tests read is not what one speaks |
| axe, in the states the tests visit, as one check among several | People: whether anyone understands the wording, or trusts it the right amount |
| That the tests catch 15 planted faults | Faults nobody thought to plant, and real model behaviour |

axe finds only some problems. Its own README gives "on average 57% of WCAG issues", and that's the vendor's figure. [`tests/fixtures/axe-blind-spots.html`](tests/fixtures/axe-blind-spots.html) is a page axe passes with no violations although people can't use it: a `div` button with no keyboard handler, a link whose name is false, alt text saying "image", and a live region fed one word at a time. `tests/axe-limits.test.ts` checks that axe really does report nothing on it, and that a control page with mechanical faults is reported, so the silence isn't just axe failing to run.

## What you're given

| Path | What it is |
|---|---|
| [`exercises/sse.ts`](exercises/sse.ts) | Stub: the event-stream parser |
| [`exercises/state.ts`](exercises/state.ts) | Stub: the reducer. The types are given, and they are the design |
| [`exercises/Chat.tsx`](exercises/Chat.tsx) | A naive chat that works on the happy path |
| [`server/mock-server.ts`](server/mock-server.ts) | The server, with 18 scenarios chosen per request |
| [`public/`](public/index.html) | The page and its stylesheet |
| [`tests/`](tests/browser.test.ts) | Unit, browser and axe tests, and the planted faults in `mutants.ts` |
| [`solutions/`](solutions/Chat.tsx) | One worked answer. Try the exercises first |
| [`run_notes.ts`](run_notes.ts) | Runs the code blocks in the chapters and compares their output |

The scenarios are `answer`, `slow-start`, `long`, `uncertain`, `no-evidence`, `dangling-citation`, `truncated`, `refusal`, `busy-once`, `busy-always`, `proxy-login-page`, `server-error`, `mid-stream-error`, `dropped`, `clean-eof`, `stalled`, `untrusted` and `handoff-down`.

## Steps

**Exercise 1, the parser (after chapter 2, with chapter 5's streaming section).** Write `exercises/sse.ts` from the [event-stream rules in the HTML standard](https://html.spec.whatwg.org/multipage/server-sent-events.html). No browser is needed:

```bash
TARGET=exercises node --test tests/sse.test.ts
```

**Exercise 2, the state machine.** Write `exercises/state.ts`:

```bash
TARGET=exercises node --test tests/state.test.ts
```

**Exercise 3, the interface (after chapter 5).** Fix `exercises/Chat.tsx`:

```bash
TARGET=exercises node --test tests/browser.test.ts
```

Be ready for what this one is. It's a test-guided rewrite, not a small repair. With correct parser and reducer copied in, 33 of 34 of the browser tests failed at the start, because the naive chat has no status region, no states, no "Ask a person" and only a few scenarios in its menu. Start with the scenario list and the status region, which the rest depend on. The names are in `SCENARIOS` in `server/mock-server.ts`, and you can import `solutions/state.ts` and `solutions/client.ts` if you'd rather not depend on your own exercises yet. Treat the test bodies as the specification and work through them one at a time. They include exact wording, selectors such as `.answer`, and the `?slowMs=` and `?stallMs=` page parameters, so read each test before writing the code for it.

**Exercise 4, walk it yourself.** Run `npm start`, go through every scenario in the menu by keyboard, and read each message aloud. Then try the screen reader exercise in [chapter 5](../notes/05-ai-interfaces.md#try-it), the part no script here can do.

## What the worked solution measured

These are the behaviours that differ, from `tests/axe-limits.test.ts` and `tests/browser.test.ts`. They're counts on one scripted answer, in one browser, and they describe this page.

| Measure | Naive chat | Worked solution |
|---|---|---|
| Changes to a live region during one 25-word answer | 25 | 3 |
| axe rules reported | `color-contrast`, `landmark-one-main`, `page-has-heading-one`, `region` | None, in the states tested |
| Browser tests passing, with correct parser and reducer | 1 of 34 | 34 of 34 |

axe says nothing about the 25 announcements, or about most of those failing tests. Its findings on the naive chat are all markup faults, and those were the cheap ones. A count of live-region changes also isn't a measure of what a screen reader says, since no screen reader was run, and readers can merge or drop updates.

## Questions

1. Why does the mock server have both `dropped` and `clean-eof`, and why must they look alike to the person?
2. The `uncertain` state comes from a retrieval signal, not from the model's own confidence. What would it take to replace that with a real number, and what could go wrong? See [calibration against human labels](../../../generative-ai/08-eval/notes/15-calibration-against-human-labels.md).
3. The stall limit defaults to 45 seconds, three keep-alives at the 15 seconds the spec suggests. What goes wrong if someone doubles the server's keep-alive interval and leaves the limit alone? What if they double the limit instead?
4. Pick three of the planted faults in [`tests/mutants.ts`](tests/mutants.ts). Would axe have caught them? Which test catches each, and what's left that no test here would catch?
