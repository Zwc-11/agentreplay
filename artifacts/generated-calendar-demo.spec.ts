import { test, expect } from "@playwright/test";

test("recorded workflow", async ({ page }) => {
  await page.getByRole("button", { name: "New event" }).click();
  await page.getByRole("textbox", { name: "Event title" }).click();
  await page.getByRole("textbox", { name: "Event title" }).fill("Design review");
  await page.getByRole("textbox", { name: "Start time" }).click();
  await page.getByRole("textbox", { name: "Start time" }).fill("14:00");
  await page.getByRole("button", { name: "Save event" }).click();
  await expect(page.getByText("Event saved")).toBeVisible();
});
