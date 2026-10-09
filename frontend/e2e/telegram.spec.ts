import { expect, test } from "@playwright/test";

import { loginAPI } from "./helpers";

test.beforeEach(async ({ page }) => {
  await page.goto("/login");
  await loginAPI(page);
});

test("telegram page shows status and issues a one-time link code", async ({ page }) => {
  await page.goto("/telegram");
  await expect(page.getByTestId("telegram-linked")).toHaveText("Bog‘lanmagan");
  await page.getByTestId("telegram-code").click();
  await expect(page.getByTestId("telegram-code-value")).toHaveText(/^\/start [0-9A-F]{4}-[0-9A-F]{4}$/);
});
