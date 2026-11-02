// Run: node --test group-by.test.ts   (Node 22.18+ strips types natively)
import { test } from "node:test";
import assert from "node:assert/strict";
import { groupBy } from "./group-by.ts";

type Order = { id: number; status: "open" | "paid"; total: number };
const orders: Order[] = [
  { id: 1, status: "open", total: 10 },
  { id: 2, status: "paid", total: 25 },
  { id: 3, status: "open", total: 5 },
];

test("groups by a string key, keeping input order", () => {
  const byStatus = groupBy(orders, (o) => o.status);
  assert.deepEqual(byStatus.open.map((o) => o.id), [1, 3]);
  assert.deepEqual(byStatus.paid.map((o) => o.id), [2]);
});

test("works with number keys", () => {
  assert.deepEqual(groupBy([1, 2, 3, 4], (n) => n % 2), { 0: [2, 4], 1: [1, 3] });
});

test("empty input gives an empty object", () => {
  assert.deepEqual(groupBy([], (x: number) => x), {});
});

test("does not mutate the input", () => {
  const copy = structuredClone(orders);
  groupBy(orders, (o) => o.status);
  assert.deepEqual(orders, copy);
});
