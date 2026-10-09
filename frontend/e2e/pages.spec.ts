import { expect, test } from "@playwright/test";

import { expectNoHorizontalScroll, loginAPI, appAlerts } from "./helpers";

const PAGES: [string, string][] = [
  ["/overview", "Umumiy ko‘rinish"],
  ["/content", "Kontent navbati"],
  ["/approvals", "Tasdiqlar"],
  ["/content/new", "Qo‘lda kontent yaratish"],
  ["/ai", "AI Studio"],
  ["/calendar", "Kalendar"],
  ["/media", "Media kutubxona"],
  ["/instagram", "Instagram akkaunt"],
  ["/analytics", "Analitika"],
  ["/telegram", "Telegram"],
  ["/ai-settings", "AI sozlamalari"],
  ["/brand", "Brend sozlamalari"],
  ["/logs", "Tizim loglari"],
  ["/settings", "Sozlamalar"],
];

test.beforeEach(async ({ page }) => {
  await page.goto("/login");
  await loginAPI(page);
});

for (const [path, heading] of PAGES) {
  test(`page ${path} renders`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(path);
    await expect(page.getByRole("heading", { level: 1, name: heading })).toBeVisible();
    await page.waitForLoadState("networkidle");
    await expect(appAlerts(page)).toHaveCount(0);
    await expectNoHorizontalScroll(page);
    expect(errors).toEqual([]);
  });
}

test("navigation works on mobile and desktop", async ({ page, isMobile }) => {
  await page.goto("/overview");
  if (isMobile) {
    await page.getByRole("button", { name: "Menyuni ochish" }).click();
    await page.getByRole("dialog").getByRole("link", { name: "Kalendar" }).click();
  } else {
    await page.getByRole("navigation").getByRole("link", { name: "Kalendar" }).click();
  }
  await expect(page).toHaveURL(/\/calendar/);
});

test("brand settings save", async ({ page }) => {
  await page.goto("/brand");
  const field = page.getByLabel("Soha");
  await field.fill("Interior design studio");
  await page.getByRole("button", { name: "Saqlash" }).click();
  await expect(page.getByText("Saqlandi.")).toBeVisible();
});

test("system log shows audit events", async ({ page }) => {
  await page.goto("/logs");
  await page.getByPlaceholder("Amal (masalan CONTENT_APPROVED)").fill("SEED_APPLIED");
  await expect(page.getByTestId("log-list")).toContainText("SEED_APPLIED");
});
