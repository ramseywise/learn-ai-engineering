// Chapter 6: what each charting library costs the browser. Bundles a small entry file for each
// with esbuild, minified, the way a production build would, then gzips it. Versions come from
// package.json, which pins them. Run: npm run sizes
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { gzipSync } from "node:zlib";
import { build } from "esbuild";

const REACT = 'import { createRoot } from "react-dom/client"; import { createElement } from "react";';
const entries = [
  ["react + react-dom (the base of a React app)", ["react", "react-dom"],
    `${REACT} window.x = [createRoot, createElement];`],
  ["plotly.js-dist-min (every chart type)", ["plotly.js-dist-min"],
    'import P from "plotly.js-dist-min"; window.x = P;'],
  ["plotly.js-basic-dist-min (bar, pie, scatter)", ["plotly.js-basic-dist-min"],
    'import P from "plotly.js-basic-dist-min"; window.x = P;'],
  ["echarts, everything", ["echarts"], 'import * as e from "echarts"; window.x = e;'],
  ["echarts, scatter only", ["echarts"], `
    import * as core from "echarts/core"; import { ScatterChart } from "echarts/charts";
    import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";
    import { CanvasRenderer } from "echarts/renderers";
    core.use([ScatterChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);
    window.x = core;`],
  ["recharts scatter + react", ["recharts", "react", "react-dom"], `${REACT}
    import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, Legend } from "recharts";
    window.x = [createRoot, createElement, ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, Legend];`],
  ["d3, everything", ["d3"], 'import * as d from "d3"; window.x = d;'],
  ["d3, scale + axis + selection", ["d3"], `
    import { scaleLinear } from "d3-scale"; import { axisBottom } from "d3-axis"; import { select } from "d3-selection";
    window.x = [scaleLinear, axisBottom, select];`],
  ["vega-embed + vega + vega-lite", ["vega-embed", "vega", "vega-lite"],
    'import embed from "vega-embed"; window.x = embed;'],
  ["leaflet", ["leaflet"], 'import L from "leaflet"; window.x = L;'],
];

const pinned = JSON.parse(readFileSync(new URL("./package.json", import.meta.url))).dependencies;
const results = [];
for (const [name, packages, contents] of entries) {
  const out = await build({
    stdin: { contents, resolveDir: new URL(".", import.meta.url).pathname, loader: "js" },
    bundle: true, minify: true, format: "esm", write: false, logLevel: "error",
    define: { "process.env.NODE_ENV": '"production"' }, platform: "browser",
  });
  const bytes = out.outputFiles[0].contents;
  results.push({
    name, versions: packages.map((p) => `${p}@${pinned[p]}`).join(" "),
    minified_kb: bytes.length / 1024, gzip_kb: gzipSync(bytes, { level: 6 }).length / 1024,
  });
}
console.log(`measured ${new Date().toISOString().slice(0, 10)}, node ${process.version}, esbuild minified, gzip level 6`);
for (const r of results) {
  console.log(`${r.name.padEnd(46)} ${r.minified_kb.toFixed(0).padStart(6)} KB ${r.gzip_kb.toFixed(0).padStart(6)} KB gz`);
}
console.log(Object.entries(pinned).filter(([p]) => !["jsdom", "@resvg/resvg-js"].includes(p)).map(([p, v]) => `${p}@${v}`).join(" "));
const dir = new URL("../output/", import.meta.url);
mkdirSync(dir, { recursive: true });
writeFileSync(new URL("bundle_sizes.json", dir), JSON.stringify(results, null, 1));
