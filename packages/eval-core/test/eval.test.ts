import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { compile, humanCommands } from "../../graph-core/src/index.ts";
import { computeMetrics, detectDivergence } from "../src/index.ts";

const here = dirname(fileURLToPath(import.meta.url));
const seed = JSON.parse(readFileSync(join(here, "../../../examples/demo-shop/recordings/checkout.json"), "utf8"));

const AD = { kind: "click", selector: ".promo-ad", role: "link", name: "Special offer" } as const;

test("divergent agent diverges at step 13 (wrong-element)", () => {
  const human = humanCommands(compile(seed.events, "x"));
  const agent = [...human.slice(0, 13), AD];
  assert.equal(detectDivergence(human, agent), 13);
  const m = computeMetrics(human, agent, false);
  assert.equal(m.divergenceStep, 13);
  assert.equal(m.failureCategory, "wrong-element");
  assert.equal(m.wrongClickCount, 1);
  assert.equal(m.stepAccuracy, Math.round((13 / 16) * 10000) / 10000);
});

test("a 4xx/5xx near divergence is classified network-caused", () => {
  const human = humanCommands(compile(seed.events, "x"));
  const agent = [...human.slice(0, 13), AD];
  const m = computeMetrics(human, agent, false, [{ status: 500 }]);
  assert.equal(m.failureCategory, "network-caused");
  assert.equal(m.networkCausedFailure, true);
});

test("matching paths -> no divergence, full accuracy", () => {
  const human = humanCommands(compile(seed.events, "x"));
  const m = computeMetrics(human, human, true);
  assert.equal(m.divergenceStep, null);
  assert.equal(m.stepAccuracy, 1);
  assert.equal(m.failureCategory, null);
});
