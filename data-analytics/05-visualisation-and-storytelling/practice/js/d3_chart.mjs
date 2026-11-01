// D3 in Node: jsdom supplies the document that a browser would.
import { JSDOM } from "jsdom";
import { data, ORDER, COLOURS, SIZE, savePng } from "./render.mjs";
import { drawRepeatChart } from "./repeat_chart.mjs";

const { document } = new JSDOM("<!doctype html><body></body>").window;
const svg = drawRepeatChart(document.body, data, { order: ORDER, colours: COLOURS, ...SIZE });
console.log(`${svg.querySelectorAll("path").length} paths, ${svg.querySelectorAll(".hover circle").length} hover targets`);
savePng(svg.outerHTML, "viz-js-d3-repeat-rate.png");
