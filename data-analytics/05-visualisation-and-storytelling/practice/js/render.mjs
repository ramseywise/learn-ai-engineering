// Shared helpers: read the data and turn an SVG string into a PNG in sources/images.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { Resvg } from "@resvg/resvg-js";

export const data = JSON.parse(readFileSync(new URL("./repeat_rate.json", import.meta.url)));
export const ORDER = ["Paid social", "Organic search", "Email", "Referral"];
export const COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"];
export const SIZE = { width: 720, height: 400 };

export function savePng(svg, name) {
  const dir = new URL("../../../sources/images/", import.meta.url);
  mkdirSync(dir, { recursive: true });
  const png = new Resvg(svg, {
    background: "#fcfcfb",
    fitTo: { mode: "width", value: 1200 },
    font: { loadSystemFonts: true, defaultFontFamily: "Helvetica" },
  }).render().asPng();
  writeFileSync(new URL(name, dir), png);
  console.log(`saved ${name} (${Math.round(png.length / 1024)} KB)`);
}
