import type { Server } from "node:http";
import type { AddressInfo } from "node:net";
import { resolve } from "node:path";
import { bundle } from "../server/bundle.ts";
import { createMockServer, type Stats } from "../server/mock-server.ts";

export const root = resolve(import.meta.dirname, "..");

export async function listen(chatPath: string | null, tickMs = 10): Promise<{ url: string; server: Server; stats: Stats }> {
  const appJs = resolve(root, `.out/test-${process.pid}.js`);
  if (chatPath) await bundle(chatPath, appJs);
  const { server, stats } = createMockServer({ publicDir: resolve(root, "public"), appJs, tickMs });
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  const { port } = server.address() as AddressInfo;
  return { url: `http://127.0.0.1:${port}`, server, stats };
}
