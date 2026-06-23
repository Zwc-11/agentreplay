import { expect, test } from "@playwright/test";

// End-to-end against the built dashboard in offline (bundled-demo) mode.
test.describe("AgentReplay dashboard", () => {
  test("loads, renders the human-vs-agent workflow, and the metrics", async ({ page }) => {
    await page.goto("/");

    // global app bar
    await expect(page.getByText("AgentReplay").first()).toBeVisible();

    // workflow view: graph panel + step-level metrics render from the bundled fixture
    await expect(page.getByText("Workflow Graph")).toBeVisible();
    await expect(page.getByText("Step accuracy", { exact: true })).toBeVisible();
    await expect(page.getByText("First divergence", { exact: true })).toBeVisible();
  });

  test("benchmark tab shows the per-driver table", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Benchmark" }).click();

    await expect(page.getByText("Per-driver metrics")).toBeVisible();
    await expect(page.getByText("scripted").first()).toBeVisible();
    await expect(page.getByText("divergent").first()).toBeVisible();
    await expect(page.getByText("Failure categories")).toBeVisible();
  });
});
