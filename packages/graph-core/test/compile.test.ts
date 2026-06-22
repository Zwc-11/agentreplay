import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { compile, humanCommands } from "../src/index.ts";

const here = dirname(fileURLToPath(import.meta.url));
const seed = JSON.parse(readFileSync(join(here, "../../../examples/demo-shop/recordings/checkout.json"), "utf8"));

test("compiles seed into 21 nodes and 16 human actions", () => {
  const g = compile(seed.events, "checkout-demo", "g");
  assert.equal(g.nodes.length, 21);
  assert.equal(humanCommands(g).length, 16);
});

test("first state is Login, last node is an assertion", () => {
  const g = compile(seed.events, "checkout-demo");
  const states = g.nodes.filter((n) => n.kind === "page-state" || n.kind === "assertion");
  assert.equal(states[0].label, "Login");
  assert.equal(states[states.length - 1].kind, "assertion");
});

test("normalize coalesces consecutive input bursts (final value kept)", () => {
  const g = compile(seed.events, "x");
  const fills = humanCommands(g).filter((c) => c.kind === "fill");
  assert.ok(fills.some((c) => c.value === "demo@shop.test"));
});

test("network events become dependency edges + nodes", () => {
  const g = compile(seed.events, "x");
  assert.ok(g.edges.some((e) => e.kind === "network-dependency"));
  assert.ok(g.nodes.some((n) => n.kind === "network"));
});
