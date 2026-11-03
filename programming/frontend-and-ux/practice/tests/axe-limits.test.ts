// What an automated checker can and cannot see, measured on planted faults.
import { after, before, test } from "node:test";
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import type { Browser, Page } from "playwright-core";
import { launch, runAxe } from "./browser-kit.ts";
import { listen, root } from "./helpers.ts";

let browser: Browser;
let page: Page;
const fixture = (name: string) => pathToFileURL(resolve(root, "tests/fixtures", name)).href;

before(async () => {
  browser = await launch();
  page = await browser.newPage();
});
after(() => browser?.close());

test("control: axe does report the mechanical faults", async () => {
  await page.goto(fixture("axe-control.html"));
  const ids = (await runAxe(page)).violations.map((v) => v.id);
  for (const id of ["label", "image-alt", "color-contrast", "button-name", "html-has-lang", "document-title"]) {
    assert.ok(ids.includes(id), `expected ${id} in ${ids.join(", ")}`);
  }
});

test("blind spots: axe reports no violation on this page", async () => {
  await page.goto(fixture("axe-blind-spots.html"));
  const r = await runAxe(page);
  assert.deepEqual(r.violations, []);
});

test("blind spot 1: the fake button does nothing from the keyboard", async () => {
  await page.goto(fixture("axe-blind-spots.html"));
  await page.focus("#fake");
  await page.keyboard.press("Enter");
  await page.keyboard.press("Space");
  assert.equal(await page.locator("#sent").isVisible(), false, "the keyboard did nothing");
  await page.click("#fake");
  assert.equal(await page.locator("#sent").isVisible(), true, "the mouse works");
});

test("blind spot 2: axe accepts a link whose name is false and alt text that says nothing", async () => {
  await page.goto(fixture("axe-blind-spots.html"));
  assert.equal(await page.getByRole("link").textContent(), "Delete my account");
  assert.equal(await page.locator("#chart").getAttribute("alt"), "image");
});

test("blind spot 3: a live region fed word by word still passes", async () => {
  await page.goto(fixture("axe-blind-spots.html"));
  const fed = await page.evaluate(() => (window as unknown as { feed: () => number }).feed());
  assert.equal(fed, 12);
  assert.deepEqual((await runAxe(page)).violations, []);
});

test("the naive chat: axe finds markup faults, and none of the faults in how it behaves", async () => {
  const m = await listen(resolve(root, "tests/fixtures/naive-chat.tsx"));
  try {
    await page.goto(m.url);
    await page.evaluate(() => {
      const w = window as unknown as { __changes: number };
      w.__changes = 0;
      new MutationObserver((records) => { w.__changes += records.length; })
        .observe(document.querySelector('[aria-live]')!, { childList: true, characterData: true, subtree: true });
    });
    await page.fill("textarea", "How do refunds work?");
    await page.getByText("Send", { exact: true }).click();
    await page.getByText("Annual plans can be").waitFor();
    await page.getByText("Send", { exact: true }).waitFor();
    const ids = (await runAxe(page)).violations.map((v) => v.id).sort();
    const changes = await page.evaluate(() => (window as unknown as { __changes: number }).__changes);
    console.log(`axe on the naive chat: ${ids.join(", ")}`);
    console.log(`its live region changed ${changes} times during one answer`);
    assert.ok(ids.includes("color-contrast"), ids.join(", "));
    // A word-by-word live region, a click-only div, an unchecked end of stream and
    // a page that blanks text on failure are all still in there. Axe names none.
    for (const missed of ["label", "button-name", "aria-allowed-role"]) assert.ok(!ids.includes(missed), `${missed} in ${ids.join(", ")}`);
  } finally {
    m.server.closeAllConnections();
    m.server.close();
  }
});
