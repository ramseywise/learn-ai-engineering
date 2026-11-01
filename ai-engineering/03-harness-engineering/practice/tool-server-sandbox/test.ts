import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdtempSync, mkdirSync, readFileSync, symlinkSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Denied, jail, runCommand } from "./sandbox.ts";
import { defaultPolicy, makeServer } from "./server.ts";

const root = mkdtempSync(path.join(tmpdir(), "sandbox-"));
const outside = mkdtempSync(path.join(tmpdir(), "outside-"));
writeFileSync(path.join(outside, "secret.txt"), "secret");
writeFileSync(path.join(root, "a.txt"), "hello\n");
mkdirSync(path.join(root, "sub"));
symlinkSync(outside, path.join(root, "link"));

// The jail
assert.throws(() => jail(root, "../x"), Denied);
assert.throws(() => jail(root, "/etc/passwd"), Denied);
assert.throws(() => jail(root, "link/secret.txt"), Denied, "symlink to outside");
assert.throws(() => jail(root, "link/new.txt"), Denied, "new file through a symlinked folder");
assert.throws(() => jail(root, `../${path.basename(root)}-evil/x`), Denied, "sibling sharing the prefix");
assert.ok(jail(root, "sub/new.txt").endsWith(path.join("sub", "new.txt")));

const policy = { ...defaultPolicy(root), commands: ["ls", "sleep", "yes", "env"], timeoutMs: 300, maxOutputBytes: 1000 };

// Execution limits
await assert.rejects(runCommand(policy, "curl", []), Denied);
const slow = await runCommand(policy, "sleep", ["5"]);
assert.ok(slow.timedOut, "slow command is killed");
const noisy = await runCommand(policy, "yes", []);
assert.ok(noisy.truncated && noisy.stdout.length <= 1000, "output is capped");
process.env.LAB_SECRET = "hunter2";
assert.ok(!(await runCommand(policy, "env", [])).stdout.includes("hunter2"), "environment is scrubbed");
const meta = await runCommand(policy, "ls", ["; touch pwned"]);
assert.notEqual(meta.exitCode, 0);
assert.throws(() => readFileSync(path.join(root, "pwned")), "metacharacters are plain text");

// Tool results
const denyAll = makeServer(policy);
const w: any = await denyAll.call("write_file", { path: "b.txt", content: "x" });
assert.ok(w.isError);
assert.throws(() => readFileSync(path.join(root, "b.txt")), "denied write left no file");
const allow = makeServer(policy, () => true);
assert.ok(!((await allow.call("write_file", { path: "sub/b.txt", content: "x" })) as any).isError);
assert.equal(readFileSync(path.join(root, "sub/b.txt"), "utf8"), "x");
assert.ok(((await allow.call("write_file", { path: "link/x", content: "x" })) as any).isError, "approval does not bypass the jail");
assert.ok(((await denyAll.call("read_file", { path: "a.txt", extra: 1 })) as any).isError);
assert.ok(((await denyAll.call("read_file", { path: 7 })) as any).isError);
assert.ok(denyAll.audit.some((e) => e.outcome === "denied"));

// The wire protocol, end to end against a child process
const here = path.dirname(fileURLToPath(import.meta.url));
const child = spawn("npx", ["tsx", "server.ts"], { cwd: here, stdio: ["pipe", "pipe", "inherit"] });
const send = (m: unknown) => child.stdin.write(JSON.stringify(m) + "\n");
const replies: any[] = [];
const done = new Promise<void>((resolve) => {
  let buf = "";
  child.stdout.on("data", (d) => {
    buf += d;
    const lines = buf.split("\n");
    buf = lines.pop()!;
    for (const l of lines) replies.push(JSON.parse(l));
    if (replies.length === 4) resolve();
  });
});
send({ jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2025-06-18" } });
send({ jsonrpc: "2.0", method: "notifications/initialized" });
send({ jsonrpc: "2.0", id: 2, method: "tools/list" });
send({ jsonrpc: "2.0", id: 3, method: "tools/call", params: { name: "read_file", arguments: { path: "docs/refunds.txt" } } });
send({ jsonrpc: "2.0", id: 4, method: "no/such" });
await done;
child.kill();
assert.equal(replies[0].result.serverInfo.name, "tool-server-sandbox");
assert.equal(replies[1].result.tools.length, 4);
assert.match(replies[2].result.content[0].text, /30 days/);
assert.equal(replies[3].error.code, -32601);

rmSync(root, { recursive: true, force: true });
rmSync(outside, { recursive: true, force: true });
console.log("ok: all assertions passed");
process.exit(0);
