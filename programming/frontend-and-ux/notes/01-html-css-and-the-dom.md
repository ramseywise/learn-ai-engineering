---
origin: synthesis
sources:
  - "MDN, Document Object Model (DOM) — https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model"
  - "MDN, Populating the page: how browsers work — https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work"
  - "MDN, Semantics (glossary) — https://developer.mozilla.org/en-US/docs/Glossary/Semantics"
  - "MDN, HTML: a good basis for accessibility — https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Accessibility/HTML"
  - "MDN, the button element — https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button"
  - "MDN, Your first form — https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Your_first_form"
  - "MDN, Introduction to the CSS cascade — https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Introduction"
  - "MDN, Specificity — https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity"
  - "MDN, Introduction to the CSS box model — https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Box_model/Introduction"
  - "MDN, Flexbox — https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Flexbox"
  - "MDN, Event bubbling — https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling"
  - "WHATWG, HTML Living Standard: implicit submission — https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#implicit-submission"
  - "MDN, CSS grid layout — https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Grids"
  - "MDN, Using media queries — https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Media_queries/Using"
  - "MDN, prefers-reduced-motion — https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion"
  - "MDN, Introduction to events — https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Events"
  - "MDN, Element.innerHTML — https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML"
concepts: [dom, accessibility-tree, critical-rendering-path, reflow, semantic-html, forms, cascade, specificity, box-model, flexbox, grid, media-queries, event-bubbling, text-content-vs-inner-html]
confidence: high
# high because the note rests on official reference documentation (MDN, WHATWG) and its demos were run in Chromium.
cleaned: 2026-11-02
---
# 1 — HTML, CSS and the DOM

> A browser is an interpreter with a long-running data structure in it, and HTML is the source that builds that structure. Choose the right element and you get keyboard behaviour, form submission and a screen reader's signposts without writing any code. Choose a `div` and you owe all of it by hand. This chapter gives a backend engineer enough of the model to write a page that works and to read a page that doesn't.

---

## What the browser does with your page

You send bytes. The browser [parses them into two trees](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work): the DOM (Document Object Model) from the HTML and the CSSOM, its equivalent for CSS, from the stylesheets. It also builds a third tree that matters here: the accessibility tree, which is what a screen reader reads instead of your pixels. Then it computes styles, lays out boxes, paints them and composites the result, combining separately painted layers into the final image.

```text
 HTML ──parse──▶ DOM ──────┐
                           ├──▶ style ──▶ layout ──▶ paint ──▶ composite
 CSS  ──parse──▶ CSSOM ────┘
                 │
 DOM ────────────┴──▶ accessibility tree ──▶ screen reader, voice control
```

Three consequences follow.

**The DOM is live and the HTML is not.** The [DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model) is a tree of objects your script can read and change, and "View source" shows only what arrived. If a page is wrong, inspect the DOM: open the browser's DevTools (F12, or right-click and choose Inspect) and read the Elements panel, called Inspector in Firefox.

**Scripts can hold up parsing.** A plain `<script>` makes the parser stop and wait while it downloads and runs. That is why script tags traditionally sat at the end of the body. `defer` downloads without stopping the parser and runs the script after parsing finishes, and `async` also downloads alongside parsing but runs as soon as it arrives.

**Changing geometry costs more than changing colour.** Anything that moves a box forces layout to run again, called reflow. An image with no declared size is the classic case, because the text around it jumps when the image arrives. [MDN gives 16.67 ms](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work) as the main-thread budget for smooth animation, which is about 60 frames a second. Streamed text changes geometry too, since each word can move what is below it. This track did not measure what that costs.

If you came from Python, the [JavaScript for Python developers chapter](../../typescript/notes/01-js-for-python-devs.md) covers the language, and the [event loop section](../../typescript/notes/06-async.md#the-event-loop) explains why long-running script freezes all of this: rendering and your code share one thread.

## Semantic HTML is free behaviour

[Semantics](https://developer.mozilla.org/en-US/docs/Glossary/Semantics) means choosing an element for what it is rather than how it looks. A `<span>` styled large looks like a heading to a sighted reader and is plain text to everyone and everything else. An `<h1>` is a heading to all of them.

The strongest example is a button. MDN's [accessibility introduction](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Accessibility/HTML) compares a `div` with a click handler against a real `<button>`. The button can take keyboard focus and be activated with Space or Enter, and both come with no code. In this block, `getElementById` and `querySelectorAll` look up elements in the DOM, and `.click()` fires a click from script. It runs in Chromium when you run the lab's [`check.sh`](../practice/check.sh), and the output below it is compared with what the browser printed.

```html
<!doctype html>
<div id="fake">Send</div>
<button id="real">Send</button>
<form onsubmit="event.preventDefault(); console.log('form submitted')">
  <label for="q">Your question</label>
  <input id="q">
  <button>Default type</button>
  <button type="button">Plain button</button>
</form>
<script>
  const fake = document.getElementById("fake");
  const real = document.getElementById("real");
  console.log("div can take focus by Tab:", fake.tabIndex >= 0);
  console.log("button can take focus by Tab:", real.tabIndex >= 0);
  console.log("the input knows its label:", document.getElementById("q").labels[0].textContent);
  const [submit, plain] = document.querySelectorAll("form button");
  console.log("button with no type:", submit.type);
  plain.click();
  submit.click();
</script>
```

```text
div can take focus by Tab: false
button can take focus by Tab: true
the input knows its label: Your question
button with no type: submit
form submitted
```

Two details in that block catch people. The script clicks both buttons and "form submitted" prints once, because `type="button"` opts out, while a [`<button>` inside a form submits it by default](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button). So a "Cancel" button with no `type` will send the form. (`preventDefault()` stops the page reloading, and there is more on it below.) And [a `<label for>`](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Your_first_form) does two jobs: it gives the field its name for assistive technology, and clicking it focuses the field. A form also gives you [Enter-to-submit](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#implicit-submission) on most platforms.

The elements worth reaching for first:

| You want | Use | Not |
|----------|-----|-----|
| Do something here | `<button>` | `<div onclick>`, `<a href="#">` |
| Go somewhere | `<a href>` | `<button>` with a redirect |
| Name a field | `<label for>` | `placeholder` alone |
| Structure | `<h1>` to `<h6>` in order, `<main>`, `<nav>`, `<section>` | `<div class="title">` |
| A sequence | `<ol>`, `<ul>` | `<div>` per row |
| A quotation | `<blockquote>` | a styled `<div>` |

The [accessibility chapter](03-accessibility.md) takes this further, including what to do when no element fits.

## CSS: which rule wins

CSS causes more confusion than its size suggests, because three separate questions get mixed up: which rule applies, how big the box is, and where the box goes.

**Which rule applies.** Several rules can set the same property on one element. The [cascade](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Introduction) resolves this in order, and this is the short version of its steps. Origin and importance come first: a page's own rules beat the browser's defaults, and a declaration marked `!important` beats normal ones. Then comes cascade layer (a named group of rules declared with `@layer`, unrelated to painted layers), then [specificity](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity), then source order. Specificity is scored in three columns, IDs (`#only`), classes (`.a`) and types (element names such as `p`), compared left to right, so one ID beats any number of classes. Here is that measured.

```html
<!doctype html>
<style>
  #only { color: rgb(1, 1, 1); }
  .a.b.c.d.e.f { color: rgb(2, 2, 2); }
  p { color: rgb(3, 3, 3); }

  .plain, .border { width: 200px; padding: 20px; border: 5px solid; }
  .border { box-sizing: border-box; }
</style>
<p id="only" class="a b c d e f">which colour?</p>
<div class="plain">x</div>
<div class="border">x</div>
<script>
  const color = getComputedStyle(document.querySelector("p")).color;
  console.log("winner:", color);
  console.log("content-box width on screen:", document.querySelector(".plain").offsetWidth);
  console.log("border-box width on screen:", document.querySelector(".border").offsetWidth);
</script>
```

```text
winner: rgb(1, 1, 1)
content-box width on screen: 250
border-box width on screen: 200
```

**How big the box is.** The last two lines of that output are the [box model](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Box_model/Introduction). By default (`box-sizing: content-box`) `width` sets the content only, and padding and border are added outside it, which is how a `width: 100%` element comes to overflow its parent. Many stylesheets set `box-sizing: border-box` on everything so `width` means the width you see.

**Where the box goes.** Use [flexbox](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Flexbox) to lay things out along one direction, and [grid](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Grids) when rows and columns both matter. We would pick either over floats or absolute positioning for page layout, because content can grow without things colliding. In the block below, `rem` is a multiple of the root font size and `1fr` is one share of the leftover space. `minmax(0, 1fr)` lets that column shrink below the width of its content, which a long token would otherwise prevent. `.caret` is the lab's blinking cursor while an answer streams.

```css
*, *::before, *::after { box-sizing: border-box; }

.actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }

.page {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 20rem;
  gap: 1rem;
}

@media (max-width: 40rem) {
  .page { grid-template-columns: minmax(0, 1fr); }
}

/* Long unbroken tokens, such as a URL in a model's answer, must not widen the page. */
.answer { overflow-wrap: anywhere; }

@media (prefers-reduced-motion: reduce) {
  .caret { animation: none; }
}
```

The two [`@media`](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Media_queries/Using) rules are worth noticing. One responds to the width of the window, the other to a [user's request for less motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion), which exists because animation can cause discomfort for people with vestibular motion disorders. A page reads both like any other input.

## Events and the DOM from script

Handlers receive an event object. `event.target` is the element that was acted on, and [`preventDefault()`](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Events) cancels the browser's built-in response, such as a form's full-page submit. Events also [bubble up through ancestors](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling), so one listener on a container can serve every child, and the block below shows that includes children added later.

The DOM call you must learn to distrust is `innerHTML`. MDN calls it an [injection sink and a common route for cross-site scripting](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML), or XSS: text an attacker controls ends up running as script in your page. It parses a string as markup, and it does so whether or not the string came from someone you trust. The elements counted below look harmless, but an `onerror` attribute on that `<img>` would run its code when the image failed to load. `textContent` writes the same string as characters.

```html
<!doctype html>
<ul id="list"></ul>
<div id="unsafe"></div>
<div id="safe"></div>
<script>
  document.getElementById("list").addEventListener("click", (e) => {
    console.log("one listener on the list, clicked:", e.target.textContent);
  });
  const item = document.createElement("li");
  item.textContent = "added after the listener";
  document.getElementById("list").append(item);
  item.click();

  const reply = '<img src="x"> Your refund is <b>approved</b>';
  document.getElementById("unsafe").innerHTML = reply;
  document.getElementById("safe").textContent = reply;
  console.log("innerHTML made elements:", document.querySelectorAll("#unsafe *").length);
  console.log("textContent made elements:", document.querySelectorAll("#safe *").length);
</script>
```

```text
one listener on the list, clicked: added after the listener
innerHTML made elements: 2
textContent made elements: 0
```

For a page showing model output this is a security boundary and no mere style point, since a model can be talked into writing anything. [Chapter 5](05-ai-interfaces.md#rendering-is-a-security-boundary) follows it through.

## Pitfalls

**A `div` where a control belongs.** *Symptom:* it works with a mouse and nobody on your team notices. Tab skips it, Enter does nothing, and a screen reader says only its text. Use `<button>` or `<a>`.

**A button with no `type` inside a form.** *Symptom:* clicking "Cancel" or "Show more" submits the form or reloads the page. Set `type="button"` on anything that isn't a submit.

**Fighting specificity with `!important`.** *Symptom:* each fix needs a stronger selector than the last, and a one-line colour change breaks something far away. Keep selectors flat, usually one class, and find out why the wrong rule won using the Computed panel in DevTools, which lists every rule and the winner.

**`width: 100%` plus padding.** *Symptom:* a horizontal scrollbar appears and the page sits a few pixels too wide. Set `box-sizing: border-box` globally.

**Images and embeds with no size.** *Symptom:* text jumps as things load, and people tap the wrong thing. Give images `width` and `height`.

**A long token that won't wrap.** *Symptom:* a URL in a chat answer pushes the page wider than a phone. Set `overflow-wrap: anywhere` on the container. The lab has a test for this at 320 px.

## Try it

The exercises below need only a browser. The [lab](../practice/README.md) applies this chapter in a chat page served by a mock server: [`public/style.css`](../practice/public/style.css) is its stylesheet, and `bash check.sh` runs its tests.

1. Open any page you built, press Tab repeatedly and note where focus goes. Can you see it the whole way? Can you reach and activate every control?
2. Predict the printed values, then run this in a browser console on a blank page: create a `div`, set `style.width = "100px"`, `style.padding = "10px"`, append it and read `offsetWidth`. Then set `style.boxSizing = "border-box"` and read it again.
3. A rule `.card .title { color: red }` isn't applying and `#sidebar .title { color: blue }` is. Without running anything, say why, and what the fix is that doesn't add `!important`.

<details>
<summary>Answers</summary>

1. There's no single right answer. Focus should move in reading order and always be visible, and each control should activate from the keyboard. Anywhere it fails is usually a `div` with a click handler, or a stylesheet that removed the focus outline, which [chapter 3](03-accessibility.md#keyboard-and-focus) covers.
2. 120, then 100. By default padding is added to the content width. With `border-box`, the 100 includes the padding.
3. `#sidebar .title` scores one ID and one class, against two classes. The ID column is compared first, so it wins whatever comes later in the file. Remove the ID from the selector, usually by replacing it with a class on the sidebar, so both rules are equal and order decides.

</details>

## Interview checklist

| Question | Answer |
|----------|--------|
| What does a browser build from a page? | A DOM from the HTML, a CSSOM from the CSS and an accessibility tree. Then style, layout, paint and composite. |
| Why choose `<button>` over `<div onclick>`? | Focus, Space and Enter, and form behaviour come built in, and a screen reader announces it as a button. A `div` has none, and you would have to write them all. |
| What does specificity compare? | IDs, then classes, then types, column by column. It only applies after origin, importance and layers, and source order breaks ties. |
| `content-box` against `border-box`? | Whether `width` excludes or includes padding and border. |
| Flexbox or grid? | One direction: flexbox. Rows and columns together: grid. |
| What's wrong with `innerHTML`? | It parses a string as markup, so untrusted text can become elements. Use `textContent` for text. |
| What causes reflow? | Anything that changes geometry, such as added text or an image arriving with no declared size. |

## Next

- [Chapter 2, React and state](02-react-and-state.md): stop writing DOM calls, and describe the page as a function of its state.
- [Chapter 3, accessibility](03-accessibility.md): what the accessibility tree needs from you, and what no automated tool can tell you.
- [TypeScript, modules and tooling](../../typescript/notes/07-modules-and-tooling.md), for how the code reaches the browser at all.
