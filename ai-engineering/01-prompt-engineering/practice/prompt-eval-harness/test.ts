import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { flips, graders, parseLabel, runVariant, wilson, type Case } from "./harness.ts";
import { stub } from "./stub.ts";
import { variants } from "./variants.ts";

const cases: Case[] = JSON.parse(readFileSync(new URL("./cases.json", import.meta.url), "utf8"));

assert.equal(parseLabel('{"label":"bug"}'), "bug");
assert.equal(parseLabel('Sure! {"label":"bug"}'), null, "prose around JSON must fail");
assert.equal(graders.known_label('{"label":"spam"}', cases[0]), "label outside the set: spam");
const [lo, hi] = wilson(6, 12);
assert.ok(lo > 0.25 && lo < 0.3 && hi > 0.7 && hi < 0.75, `wilson ${lo} ${hi}`);

const [bare, format, shots] = await Promise.all(variants.map((v) => runVariant(v, cases, stub)));
assert.equal(bare.byGrader.valid_json, 0, "bare prompt gets no JSON");
assert.ok(format.passRate > bare.passRate);
assert.equal(shots.passRate, 1);
assert.ok(flips(format, shots).fixed.includes("edge-4"), "rule resists the injected instruction");
assert.ok(shots.tokens > format.tokens, "better prompt costs tokens: report it");
console.log("ok: all assertions passed");
