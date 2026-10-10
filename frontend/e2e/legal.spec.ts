import { expect, test } from "@playwright/test";

// Meta App Review needs public Privacy Policy and Terms URLs (no login).
test("privacy policy and terms are public", async ({ browser }) => {
  const context = await browser.newContext(); // no session cookie
  const page = await context.newPage();
  await page.goto("/privacy");
  await expect(page).toHaveURL(/\/privacy$/);
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Privacy Policy");
  await expect(page.locator("main")).toContainText("data deletion");
  await expect(page.locator("main")).toContainText("Instagram paroli");
  await page.goto("/terms");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Terms of Service");
  const robots = await (await page.request.get("/robots.txt")).text();
  expect(robots).toContain("Allow: /privacy");
  expect(robots).toContain("Disallow: /");
  await page.goto("/overview");
  await expect(page).toHaveURL(/\/login/); // everything else stays private
  await context.close();
});
