import { spawn } from "node:child_process";
import { realpathSync, existsSync } from "node:fs";
import path from "node:path";

/** Refused by policy. Returned to the model as a tool error, so it can adapt. */
export class Denied extends Error {}

export interface Policy {
  root: string;
  commands: string[];
  timeoutMs: number;
  maxOutputBytes: number;
}

/**
 * Resolves a path inside the jail. realpath runs on the deepest part that exists, so a symlink
 * pointing out of the root is caught, and a new file under a linked folder is too. A prefix
 * check on the raw string catches neither.
 */
export function jail(root: string, requested: string): string {
  const realRoot = realpathSync(root);
  const target = path.resolve(realRoot, requested);
  let probe = target;
  while (!existsSync(probe)) probe = path.dirname(probe);
  const real = path.join(realpathSync(probe), path.relative(probe, target));
  if (real !== realRoot && !real.startsWith(realRoot + path.sep)) throw new Denied(`path escapes the workspace: ${requested}`);
  return real;
}

export interface RunResult { stdout: string; exitCode: number | null; timedOut: boolean; truncated: boolean }

/**
 * Runs an allowlisted binary with an argv array and no shell, so `;`, `|` and `$()` are plain
 * text. The environment is scrubbed: a child cannot read the API key it was never given.
 * This is a teaching boundary and not a security product. See the README for what it misses.
 */
export function runCommand(p: Policy, command: string, args: string[]): Promise<RunResult> {
  if (!p.commands.includes(command)) return Promise.reject(new Denied(`command not allowed: ${command}`));
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: realpathSync(p.root),
      shell: false,
      env: { PATH: process.env.PATH ?? "" },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let out = Buffer.alloc(0);
    let truncated = false;
    let timedOut = false;
    const take = (chunk: Buffer) => {
      if (out.length >= p.maxOutputBytes) {
        truncated = true;
        return;
      }
      const room = p.maxOutputBytes - out.length;
      if (chunk.length > room) truncated = true;
      out = Buffer.concat([out, chunk.subarray(0, room)]);
    };
    child.stdout.on("data", take);
    child.stderr.on("data", take);
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGKILL");
    }, p.timeoutMs);
    child.on("error", (e) => {
      clearTimeout(timer);
      reject(e);
    });
    child.on("close", (exitCode) => {
      clearTimeout(timer);
      resolve({ stdout: out.toString("utf8"), exitCode, timedOut, truncated });
    });
  });
}
