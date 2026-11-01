// Observable Plot: marks plus options. It needs a document too, so jsdom again.
import * as Plot from "@observablehq/plot";
import { JSDOM } from "jsdom";
import { data, ORDER, COLOURS, SIZE, savePng } from "./render.mjs";

const rows = data.map((d) => ({ ...d, date: new Date(d.month) }));
const nudge = { "Organic search": 1.3, Referral: -1.3 };  // two line ends land together
const figure = Plot.plot({
  document: new JSDOM("").window.document,
  ...SIZE, marginRight: 100, style: { background: "#fcfcfb", fontFamily: "Helvetica", fontSize: "12px" },
  y: { domain: [0, 60], grid: true, ticks: 6, label: "90-day repeat rate (%)" },
  x: { label: null, ticks: "year", tickFormat: "%Y" },
  color: { domain: ORDER, range: COLOURS, legend: false },
  marks: [
    Plot.ruleY([0], { stroke: "#c3c2b7" }),
    Plot.lineY(rows, { x: "date", y: "rate", stroke: "channel", strokeWidth: 2, tip: true }),
    Plot.text(rows, Plot.selectLast({ x: "date", y: (d) => d.rate + (nudge[d.channel] ?? 0), z: "channel", text: "channel", textAnchor: "start", dx: 6, fill: "#52514e" })),
    Plot.ruleX([new Date("2025-01-01")], { stroke: "#898781" }),
    Plot.text([new Date("2025-01-01")], { x: (d) => d, y: 58, text: () => "Email budget cut", textAnchor: "start", dx: 5, fill: "#52514e" }),
  ],
});
figure.setAttribute("xmlns", "http://www.w3.org/2000/svg");
console.log(figure.tagName, `${figure.querySelectorAll("path").length} paths`);
savePng(figure.outerHTML, "viz-js-observable-plot-repeat-rate.png");
