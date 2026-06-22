import { test, expect } from "@playwright/test";

// AgentReplay tests itself with Playwright:
// record -> compile graph -> run agent -> detect divergence -> show summary.
test.describe("agentreplay end-to-end", () => {
  test.skip("checkout workflow records, compiles, and surfaces divergence", async ({ page }) => {
    await page.goto("http://localhost:3000");
    await expect(page.getByText("AgentReplay")).toBeVisible();
    // TODO: trigger a scripted run and assert the divergence node renders.
  });
});
