// Vega-Lite: describe the chart as JSON, compile it to Vega, ask Vega for an SVG string.
import * as vl from "vega-lite";
import * as vega from "vega";
import { data, ORDER, COLOURS, SIZE, savePng } from "./render.mjs";

const spec = {
  $schema: "https://vega.github.io/schema/vega-lite/v6.json",
  width: SIZE.width - 150, height: SIZE.height - 90, background: "#fcfcfb",
  config: { view: { stroke: null }, axis: { gridColor: "#e1e0d9", domainColor: "#c3c2b7", labelColor: "#52514e" } },
  data: { values: data },
  layer: [
    {
      mark: { type: "line", strokeWidth: 2 },
      encoding: {
        x: { field: "month", type: "temporal", title: null, scale: { type: "utc" },
             axis: { format: "%Y", tickCount: "year", grid: false } },
        y: { field: "rate", type: "quantitative", title: "90-day repeat rate (%)", scale: { domain: [0, 60] } },
        color: { field: "channel", type: "nominal", title: null, sort: ORDER,
                 scale: { domain: ORDER, range: COLOURS }, legend: { orient: "top" } },
        tooltip: [{ field: "channel" }, { field: "month", type: "temporal" }, { field: "rate" }],
      },
    },
    { mark: { type: "rule", color: "#898781" }, data: { values: [{ cut: "2025-01-01" }] },
      encoding: { x: { field: "cut", type: "temporal", scale: { type: "utc" } } } },
    { mark: { type: "text", align: "left", dx: 5, dy: -150, color: "#52514e" },
      data: { values: [{ cut: "2025-01-01", label: "Email budget cut" }] },
      encoding: { x: { field: "cut", type: "temporal", scale: { type: "utc" } }, text: { field: "label" } } },
  ],
};
const compiled = vl.compile(spec).spec;
console.log(`${compiled.marks.length} Vega mark groups, ${compiled.scales.length} scales, ${compiled.axes.length} axes, ${compiled.legends.length} legend`);
const view = new vega.View(vega.parse(compiled), { renderer: "none" });
savePng(await view.toSVG(), "viz-js-vega-lite-repeat-rate.png");
