// npm start: serve the worked solution on http://localhost:5174 for a person to try.

import { resolve } from "node:path";
import { bundle } from "./bundle.ts";
import { createMockServer } from "./mock-server.ts";

const root = resolve(import.meta.dirname, "..");
const target = process.env.TARGET ?? "solutions";
const appJs = resolve(root, `.out/${target}.js`);
await bundle(resolve(root, target, "Chat.tsx"), appJs);
const { server } = createMockServer({ publicDir: resolve(root, "public"), appJs, tickMs: 60 });
const port = Number(process.env.PORT ?? 5174);
server.listen(port, () => console.log(`mock chat (${target}) on http://localhost:${port}`));
