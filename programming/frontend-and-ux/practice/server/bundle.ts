// Compile the React app into one browser file. The output folder is .out
// because the repo's root .gitignore ignores build/ and dist/.

import { build } from "esbuild";
import { resolve } from "node:path";

export async function bundle(chatPath: string, outfile: string): Promise<void> {
  await build({
    entryPoints: [resolve(import.meta.dirname, "../app/main.tsx")],
    bundle: true,
    outfile,
    format: "esm",
    target: "es2022",
    jsx: "automatic",
    // Development React: StrictMode double-runs and key warnings are the point.
    define: { "process.env.NODE_ENV": '"development"' },
    alias: { "@chat": resolve(chatPath) },
    logLevel: "silent",
  });
}
