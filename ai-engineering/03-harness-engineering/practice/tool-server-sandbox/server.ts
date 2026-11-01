import { mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { createInterface } from "node:readline";
import { pathToFileURL } from "node:url";
import { Denied, jail, runCommand, type Policy } from "./sandbox.ts";

/**
 * An MCP-shaped tool server: JSON-RPC 2.0 over stdio with `initialize`, `tools/list` and
 * `tools/call`, hand-written so every boundary is visible. A tool failure is a normal result with
 * `isError: true`, which the model can read and act on. A protocol failure is a JSON-RPC error.
 */
export interface Tool {
  name: string;
  description: string;
  inputSchema: { type: "object"; properties: Record<string, unknown>; required: string[]; additionalProperties: false };
  /** A write changes the world, so it needs an approver as well as a valid path. */
  write?: boolean;
  handler: (input: any) => Promise<string> | string;
}

export function makeTools(policy: Policy): Tool[] {
  return [
    {
      name: "read_file",
      description: "Read a UTF-8 text file in the workspace. Paths are relative to the workspace root.",
      inputSchema: { type: "object", properties: { path: { type: "string" } }, required: ["path"], additionalProperties: false },
      handler: ({ path: p }) => {
        const text = readFileSync(jail(policy.root, p), "utf8");
        const cap = policy.maxOutputBytes;
        return text.length > cap ? `${text.slice(0, cap)}\n[truncated: ${text.length - cap} more characters. Narrow your read.]` : text;
      },
    },
    {
      name: "list_dir",
      description: "List the entries of a workspace folder. Use before read_file when you do not know a name.",
      inputSchema: { type: "object", properties: { path: { type: "string" } }, required: ["path"], additionalProperties: false },
      handler: ({ path: p }) => readdirSync(jail(policy.root, p)).sort().join("\n"),
    },
    {
      name: "write_file",
      description: "Create or overwrite a workspace file. Requires approval.",
      inputSchema: {
        type: "object",
        properties: { path: { type: "string" }, content: { type: "string" } },
        required: ["path", "content"],
        additionalProperties: false,
      },
      write: true,
      handler: ({ path: p, content }) => {
        const target = jail(policy.root, p);
        mkdirSync(path.dirname(target), { recursive: true });
        writeFileSync(target, content);
        return `wrote ${Buffer.byteLength(content)} bytes to ${p}`;
      },
    },
    {
      name: "run_command",
      description: `Run one allowlisted program with arguments. No shell. Allowed: ${policy.commands.join(", ")}.`,
      inputSchema: {
        type: "object",
        properties: { command: { type: "string" }, args: { type: "array", items: { type: "string" } } },
        required: ["command", "args"],
        additionalProperties: false,
      },
      handler: async ({ command, args }) => {
        const r = await runCommand(policy, command, args);
        if (r.timedOut) throw new Denied(`timed out after ${policy.timeoutMs} ms`);
        return `${r.stdout}${r.truncated ? "\n[output truncated]" : ""}\n[exit ${r.exitCode}]`;
      },
    },
  ];
}

/** Rejects unknown keys and wrong types before a handler runs. */
export function validate(tool: Tool, input: any): string | null {
  if (typeof input !== "object" || input === null) return "arguments must be an object";
  const props = tool.inputSchema.properties as Record<string, { type: string; items?: { type: string } }>;
  for (const key of tool.inputSchema.required) if (!(key in input)) return `missing argument: ${key}`;
  for (const [k, v] of Object.entries(input)) {
    const spec = props[k];
    if (!spec) return `unknown argument: ${k}`;
    if (spec.type === "array") {
      if (!Array.isArray(v) || v.some((x) => typeof x !== spec.items!.type)) return `${k} must be an array of ${spec.items!.type}`;
    } else if (typeof v !== spec.type) return `${k} must be a ${spec.type}`;
  }
  return null;
}

export type Approver = (tool: string, input: unknown) => boolean;
export interface AuditEntry { tool: string; input: unknown; outcome: "ok" | "denied" | "error" }

export function makeServer(policy: Policy, approve: Approver = () => false) {
  const tools = makeTools(policy);
  const audit: AuditEntry[] = [];

  async function call(name: string, input: unknown) {
    const text = (t: string, isError = false) => ({ content: [{ type: "text", text: t }], ...(isError ? { isError: true } : {}) });
    const tool = tools.find((t) => t.name === name);
    if (!tool) return text(`unknown tool: ${name}. Available: ${tools.map((t) => t.name).join(", ")}`, true);
    const bad = validate(tool, input);
    if (bad) {
      audit.push({ tool: name, input, outcome: "denied" });
      return text(bad, true);
    }
    if (tool.write && !approve(name, input)) {
      audit.push({ tool: name, input, outcome: "denied" });
      return text("denied: this write needs approval and did not get it. Do not retry it.", true);
    }
    try {
      const out = await tool.handler(input);
      audit.push({ tool: name, input, outcome: "ok" });
      return text(out);
    } catch (e: any) {
      audit.push({ tool: name, input, outcome: e instanceof Denied ? "denied" : "error" });
      return text(e instanceof Denied ? `denied: ${e.message}` : `error: ${e.code ?? e.message}`, true);
    }
  }

  async function handle(msg: any) {
    const reply = (result: unknown) => ({ jsonrpc: "2.0", id: msg.id, result });
    switch (msg.method) {
      case "initialize":
        return reply({
          protocolVersion: msg.params?.protocolVersion ?? "2025-06-18",
          capabilities: { tools: {} },
          serverInfo: { name: "tool-server-sandbox", version: "0.1.0" },
        });
      case "notifications/initialized":
        return null;
      case "tools/list":
        return reply({ tools: tools.map(({ name, description, inputSchema }) => ({ name, description, inputSchema })) });
      case "tools/call":
        return reply(await call(msg.params?.name, msg.params?.arguments ?? {}));
      default:
        return msg.id === undefined ? null : { jsonrpc: "2.0", id: msg.id, error: { code: -32601, message: `method not found: ${msg.method}` } };
    }
  }
  return { handle, call, tools, audit };
}

export const defaultPolicy = (root: string): Policy => ({
  root,
  commands: ["ls", "wc", "grep"],
  timeoutMs: 2000,
  maxOutputBytes: 4000,
});

// Run directly, it serves over stdio: `npx tsx server.ts`. Writes stay denied.
if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  const server = makeServer(defaultPolicy(new URL("./workspace", import.meta.url).pathname));
  for await (const line of createInterface({ input: process.stdin })) {
    if (!line.trim()) continue;
    const out = await server.handle(JSON.parse(line));
    if (out) process.stdout.write(JSON.stringify(out) + "\n");
  }
}
