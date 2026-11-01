// Prove the hover layer works without a browser: fire the events and read the tooltip.
import assert from "node:assert";
import { JSDOM } from "jsdom";
import { data, ORDER, COLOURS, SIZE } from "./render.mjs";
import { drawRepeatChart } from "./repeat_chart.mjs";

const { window } = new JSDOM("<!doctype html><body></body>");
const svg = drawRepeatChart(window.document.body, data, { order: ORDER, colours: COLOURS, ...SIZE });
const tip = svg.querySelector(".tip");
const first = svg.querySelector(".hover circle");
assert.equal(tip.getAttribute("visibility"), "hidden");
first.dispatchEvent(new window.MouseEvent("mouseover"));
assert.equal(tip.getAttribute("visibility"), "visible");
console.log(tip.textContent);
first.dispatchEvent(new window.MouseEvent("mouseout"));
assert.equal(tip.getAttribute("visibility"), "hidden");
console.log("hover layer ok");
