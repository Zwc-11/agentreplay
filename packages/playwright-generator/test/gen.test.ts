import test from "node:test";
import assert from "node:assert/strict";
import { generateTest } from "../src/index.ts";

const graph = {
  id: "g", sessionId: "s", nodes: [],
  edges: [
    { id: "e0", source: "s0", target: "s1", kind: "human-path", command: { kind: "goto", url: "https://x.local" } },
    { id: "e1", source: "s1", target: "s2", kind: "human-path", command: { kind: "fill", role: "textbox", name: "Email", value: "a@b.c" } },
    { id: "e2", source: "s2", target: "s3", kind: "human-path", command: { kind: "click", role: "button", text: "Sign in" } },
    { id: "e3", source: "s3", target: "s4", kind: "human-path", command: { kind: "assertVisible", text: "Dashboard" } },
  ],
} as any;

test("generates runnable Playwright with role-based locators", () => {
  const out = generateTest(graph, "login");
  assert.ok(out.includes('import { test, expect } from "@playwright/test";'));
  assert.ok(out.includes('await page.goto("https://x.local");'));
  assert.ok(out.includes('getByRole("textbox", { name: "Email" }).fill("a@b.c")'));
  assert.ok(out.includes('getByRole("button", { name: "Sign in" }).click()'));
  assert.ok(out.includes('await expect(page.getByText("Dashboard")).toBeVisible();'));
});
