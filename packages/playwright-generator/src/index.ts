import type { Command, WorkflowGraph } from "@agentreplay/shared-types";

function locator(c: Command): string {
  const name = c.name || c.text;
  if (c.role && name) return `page.getByRole("${c.role}", { name: "${name}" })`;
  if (c.text) return `page.getByText("${c.text}")`;
  return `page.locator("${c.selector}")`;
}

export function commandToLine(c: Command): string {
  switch (c.kind) {
    case "goto":
      return `  await page.goto("${c.url}");`;
    case "fill":
      return `  await ${locator(c)}.fill("${c.value}");`;
    case "click":
      return `  await ${locator(c)}.click();`;
    case "assertVisible":
      return `  await expect(${locator(c)}).toBeVisible();`;
    default:
      return `  // unsupported: ${(c as Command).kind}`;
  }
}

export function generateTest(graph: WorkflowGraph, testName = "recorded workflow"): string {
  const cmds = graph.edges.filter((e) => e.kind === "human-path" && e.command).map((e) => e.command as Command);
  const body = cmds.length ? cmds.map(commandToLine).join("\n") : "  // no actions recorded";
  return `import { test, expect } from "@playwright/test";\n\ntest("${testName}", async ({ page }) => {\n${body}\n});\n`;
}
