// Do the browser tests have teeth? Break the worked solution one way at a time and
// require the named test to fail. Each fault is one a real chat UI ships with.
import { spawnSync } from "node:child_process";
import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { root } from "./helpers.ts";

type Mutant = { fault: string; file: string; find: string; replace: string; test: string };

const MUTANTS: Mutant[] = [
  { fault: "answer text inside a live region", file: "Chat.tsx",
    find: '<div className="answer">', replace: '<div className="answer" aria-live="polite">',
    test: "streaming is not announced word by word" },
  { fault: "status region only added once there is news", file: "Chat.tsx",
    find: '<p role="status" className="status">', replace: '<p className={live.status === "idle" ? "" : "status"} role={live.status === "idle" ? undefined : "status"}>',
    test: "the status region exists, empty, before anything happens" },
  { fault: "model output rendered as HTML", file: "Chat.tsx",
    find: "return <>{parts}</>;", replace: "return <span dangerouslySetInnerHTML={{ __html: text }} />;",
    test: "model output cannot run script, load an image or make a link" },
  { fault: "citation URLs not checked", file: "Chat.tsx",
    find: "const href = safeHref(c.url, location.href);", replace: "const href = c.url;",
    test: "a javascript: citation is shown as text, not as a link" },
  { fault: "every retrieved source listed, cited or not", file: "Chat.tsx",
    find: "const cited = citedSources(exchange.text, exchange.citations);", replace: "const cited = exchange.citations;",
    test: "a complete answer: words, sources, status and an accessible page" },
  { fault: "citation markers never checked", file: "state.ts",
    find: "danglingMarkers(body.text, body.citations).length > 0 || markers(body.text).length === 0", replace: "false",
    test: "a citation marker with no source is marked unverified" },
  { fault: "Stop hides the answer but leaves the request running", file: "Chat.tsx",
    find: "abortRef.current?.abort();\n    inputRef.current?.focus(); // the Stop", replace: 'dispatch({ type: "stopped", id: live.status === "idle" ? "" : live.id });\n    inputRef.current?.focus(); // the Stop',
    test: "Stop keeps the partial text, reaches the server and returns focus" },
  { fault: "focus left on a button that changes meaning", file: "Chat.tsx",
    find: "inputRef.current?.focus(); // the Stop button is about to mean Send", replace: "",
    test: "Stop keeps the partial text, reaches the server and returns focus" },
  { fault: "Send leaves focus on the button that became Stop", file: "Chat.tsx",
    find: "of Enter or Space would stop the answer the person just asked for.\n    inputRef.current?.focus();", replace: "of Enter or Space would stop the answer the person just asked for.",
    test: "Send and Stop are real buttons: Space and Enter work when they have focus" },
  { fault: "earlier answers vanish from the page", file: "Chat.tsx",
    find: "{history.map((h) => <Turn key={h.id} exchange={h} streaming={false} />)}", replace: "",
    test: "handoff sends the context, returns a reference and says what was shared" },
  { fault: "Retry offered on an error that retrying cannot fix", file: "Chat.tsx",
    find: 'live.status === "error" ? live.retryable :', replace: 'live.status === "error" ? true :',
    test: "an error that retrying cannot fix offers no Retry" },
  { fault: "Stop is a div with a click handler", file: "Chat.tsx",
    find: '<button type="button" onClick={stop}>Stop</button>', replace: '<div role="button" tabIndex={0} onClick={stop}>Stop</div>',
    test: "Send and Stop are real buttons: Space and Enter work when they have focus" },
  { fault: "scroll always follows the stream", file: "Chat.tsx",
    find: "(followRef.current || wasAtBottom)", replace: "true",
    test: "the page follows the stream, until the reader scrolls away" },
  { fault: "handoff drops the answer", file: "Chat.tsx",
    find: "answer: live.text,", replace: 'answer: "",',
    test: "handoff sends the context, returns a reference and says what was shared" },
  { fault: "clean end of stream treated as success", file: "client.ts",
    find: 'else fail("dropped", true); // clean EOF', replace: 'else dispatch({ type: "done", id, stop: "end", evidence: "strong" }); // clean EOF',
    test: "a dropped connection and a clean end with no terminal event both fail visibly" },
  { fault: "no stall watchdog", file: "client.ts",
    find: "}, stallMs);", replace: "}, 3_600_000);",
    test: "a silent connection is given up on" },
  { fault: "keep-alives ignored by the watchdog", file: "client.ts",
    find: "feedWatchdog(); // any byte, including a keep-alive comment, proves life", replace: "if (value && value.length > 20) feedWatchdog();",
    test: "a slow first token gets a second message, and keep-alives hold off the watchdog" },
  { fault: "content type not checked", file: "client.ts",
    find: '!(res.headers.get("content-type") ?? "").startsWith("text/event-stream") || !res.body', replace: "!res.body",
    test: "a proxy's HTML page sent as a 200 is not rendered as an answer" },
];

const work = resolve(root, ".out/mutants");
rmSync(work, { recursive: true, force: true });
mkdirSync(work, { recursive: true });
let survived = 0;
for (const [i, m] of MUTANTS.entries()) {
  const dir = resolve(work, String(i));
  cpSync(resolve(root, "solutions"), dir, { recursive: true });
  const path = resolve(dir, m.file);
  const source = readFileSync(path, "utf8");
  if (!source.includes(m.find)) {
    console.error(`stale mutant, text not found: ${m.fault}`);
    process.exit(2);
  }
  writeFileSync(path, source.replace(m.find, m.replace));
  const name = m.test.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const r = spawnSync(process.execPath, ["--test", "--test-reporter=tap", `--test-name-pattern=^${name}$`, "tests/browser.test.ts"], {
    cwd: root, encoding: "utf8",
    env: { ...process.env, APP_ENTRY: resolve(dir, "Chat.tsx"), STEP_TIMEOUT_MS: "3000" },
  });
  const ran = /^# pass (\d+)/m.exec(r.stdout)![1]! !== "0" || /^# fail [1-9]/m.test(r.stdout);
  const caught = r.status !== 0 && ran;
  if (!caught) survived++;
  console.log(`${caught ? "caught  " : "SURVIVED"}  ${m.fault}`);
}
console.log(`${MUTANTS.length - survived} of ${MUTANTS.length} planted faults caught`);
process.exit(survived ? 1 : 0);
