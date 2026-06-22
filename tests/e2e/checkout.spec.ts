import { expect, test } from "@playwright/test";

test.describe("AgentReplay dashboard", () => {
  test("loads live workflow data, runs an agent, and imports a recording", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: "AgentReplay" })).toBeVisible();
    await expect(page.getByText("Project: checkout-demo")).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole("heading", { name: "Order confirmed" })).toBeVisible({ timeout: 20_000 });

    await page.locator("select").nth(0).selectOption("checkout-flaky");
    await expect(page.getByText("Project: checkout-flaky")).toBeVisible({ timeout: 20_000 });
    await expect(page.getByText("POST /api/checkout -> 500").first()).toBeVisible();
    await expect(page.getByText("network-caused").first()).toBeVisible({ timeout: 20_000 });

    await page.locator("select").nth(1).selectOption("scripted");
    await page.getByRole("button", { name: "Run Agent" }).click();
    await expect(page.getByLabel("Task success: Pass")).toBeVisible({ timeout: 20_000 });
    await expect(page.getByLabel("Step accuracy: 100%")).toBeVisible();

    await page
      .locator('input[type="file"]')
      .setInputFiles("examples/demo-calendar/recordings/event.json");
    await expect(page.getByText("Project: calendar-demo")).toBeVisible({ timeout: 20_000 });
    await expect(page.getByText("Imported 9 events as calendar-demo.")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Calendar" })).toBeVisible();
    await expect(page.getByText(/Design review at 14:00/)).toBeVisible();
    await expect(page.getByRole("button", { name: "8 assertion Event saved" })).toBeVisible();
  });
});
