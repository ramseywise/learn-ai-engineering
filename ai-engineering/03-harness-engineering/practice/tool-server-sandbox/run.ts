import { runClaude, runScripted } from "./agent.ts";
import { defaultPolicy, makeServer } from "./server.ts";

const root = new URL("./workspace", import.meta.url).pathname;
const server = makeServer(defaultPolicy(root)); // the approver denies every write

if (process.env.MODEL) {
  const task = process.argv[2] ?? "How long is the refund window? Look in docs/ and cite the file.";
  console.log(await runClaude(server, process.env.MODEL, task));
} else {
  await runScripted(server, [
    { why: "discover", name: "list_dir", input: { path: "docs" } },
    { why: "do the job", name: "read_file", input: { path: "docs/refunds.txt" } },
    { why: "allowed program, no shell", name: "run_command", input: { command: "grep", args: ["-l", "refund", "docs/refunds.txt"] } },
    { why: "attack: path traversal", name: "read_file", input: { path: "../../../../../../etc/passwd" } },
    { why: "attack: absolute path", name: "read_file", input: { path: "/etc/passwd" } },
    { why: "attack: program outside allowlist", name: "run_command", input: { command: "curl", args: ["https://example.com"] } },
    { why: "attack: shell metacharacters", name: "run_command", input: { command: "ls", args: ["; cat /etc/passwd"] } },
    { why: "attack: write with no approval", name: "write_file", input: { path: "docs/refunds.txt", content: "Refunds: forever." } },
    { why: "bad call: unknown argument", name: "read_file", input: { path: "docs/seats.txt", encoding: "latin1" } },
    { why: "bad call: unknown tool", name: "delete_file", input: { path: "docs/seats.txt" } },
  ]);
  const counts = server.audit.reduce<Record<string, number>>((a, e) => ({ ...a, [e.outcome]: (a[e.outcome] ?? 0) + 1 }), {});
  console.log(`\naudit log: ${JSON.stringify(counts)} (an unknown tool is rejected before the log)`);
}
