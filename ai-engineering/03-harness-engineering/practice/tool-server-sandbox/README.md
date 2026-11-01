# Lab: a tool server with sandboxing

Language: TypeScript. Supports [Tool design](../../notes/03-tool-design.md) and
[Execution boundaries](../../notes/04-execution-boundaries.md).

A model's tool call is untrusted input, because retrieved text can talk the model into almost
anything. This lab builds the boundary that holds anyway: a small tool server speaking MCP-shaped
JSON-RPC over stdio, with a path jail that resolves symlinks, a command allowlist with no shell, a
scrubbed environment, a kill timer, output caps, an approval gate on writes, and an audit log. A
blocked call comes back as a tool error the model can read.

## Run it (offline, no key)

```bash
npx tsx run.ts     # a scripted agent does its job, then tries each attack
npx tsx test.ts    # the assertions, including a symlink escape and the stdio protocol
npx tsx server.ts  # serve over stdio; send it one JSON-RPC message per line
```

Real output with the scripted agent:

```text
RUN_OUTPUT
```

## What this boundary does not stop

This is a teaching boundary. It has no network or filesystem isolation at the OS level, so an
allowlisted program can read anything its own arguments reach (`grep` on an absolute path works),
and it can use the network if it knows how. There is also a race between the jail check and the file
open. For untrusted code, run the server in a container or microVM with no network, as
[Execution boundaries](../../notes/04-execution-boundaries.md) describes. Exercise 2 closes the
`grep` gap.

## Swap in a real model

```bash
npm install                                 # installs @anthropic-ai/sdk
export ANTHROPIC_API_KEY=...                # or: ant auth login
MODEL=claude-opus-5-5 npx tsx run.ts "How long is the refund window? Look in docs/ and cite the file."
```

`agent.ts` holds a manual tool loop capped at 8 turns, returning every result in one message. Writes
stay denied unless you pass an approver to `makeServer`.

To serve real MCP clients, this server's message shapes follow the protocol, but it omits batching,
cancellation and capability negotiation. For production, register the same handlers with the
official `@modelcontextprotocol/sdk` server and keep `sandbox.ts` as it is.

## Exercises

1. Run `grep` with the argument `/etc/passwd` through `run_command`. Does it get blocked? Say why.
2. Close that gap: give each allowlisted program a validator that passes path-like arguments through
   `jail`. What breaks in the scripted plan?
3. Make the denial message for a write vaguer ("not allowed"). What would a model be likely to do
   next, and why does the exact wording matter?
