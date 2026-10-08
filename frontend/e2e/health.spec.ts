import { expect, test } from "@playwright/test";

test("frontend shows backend /health status", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "AI Instagram Manager" })).toBeVisible();

  const status = page.getByTestId("backend-status");
  await expect(status).toHaveAttribute("data-status", /^(ok|degraded)$/);
  await expect(status).toContainText("Database");
});

test("page has no horizontal scroll on mobile widths", async ({ page }) => {
  await page.goto("/");
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(0);
});
