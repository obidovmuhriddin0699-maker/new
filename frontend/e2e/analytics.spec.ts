import { expect, test, type Page } from "@playwright/test";

import { apiCall, createContent, expectNoHorizontalScroll, loginAPI } from "./helpers";

// Insights come from the local fake Meta (backend/tests/fake_meta.py): fixed values,
// and the account window deliberately lacks total_interactions.
test.describe.configure({ mode: "serial" });

function jpeg(): Buffer {
  const sof = Buffer.from([0xff, 0xc0, 0x00, 0x11, 0x08, 0x05, 0x46, 0x04, 0x38, 0x03, 0x01, 0x22, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01]);
  return Buffer.concat([Buffer.from([0xff, 0xd8]), sof, Buffer.alloc(32), Buffer.from([0xff, 0xd9])]);
}

async function connect(page: Page) {
  await page.goto("/instagram");
  const status = page.getByTestId("instagram-status");
  await expect(status).toBeVisible();
  if ((await status.textContent())?.includes("Ulanmagan")) {
    await page.getByRole("button", { name: "Instagram’ni ulash" }).click();
    await expect(page.getByTestId("oauth-success")).toBeVisible();
  }
}

async function publishOne(page: Page, topic: string) {
  const c = await createContent(page, topic, { aspect_ratio: "4:5" });
  const up = await page.request.post(`/api/backend/contents/${c.id}/assets/upload?expected_version=1`, {
    data: jpeg(),
    headers: { Origin: "http://localhost:3100", "Content-Type": "application/octet-stream" },
  });
  expect(up.status()).toBe(201);
  await apiCall(page.request, "post", `contents/${c.id}/submit-review`);
  await apiCall(page.request, "post", `contents/${c.id}/approve`, { expected_version: 2 });
  const r = await apiCall<{ status: string }>(page.request, "post", `contents/${c.id}/publish`, { expected_version: 2 });
  expect(r.status).toBe("published");
  return c;
}

test.beforeEach(async ({ page }) => {
  await page.goto("/login");
  await loginAPI(page);
  await connect(page);
});

test("sync shows real values and dashes for what Meta did not return", async ({ page }) => {
  const topic = `Statistika ${Date.now()}`;
  await publishOne(page, topic);
  await page.goto("/analytics");
  await page.getByTestId("analytics-sync").click();
  await expect(page.getByTestId("analytics-message")).toContainText("Yangilandi");

  const stats = page.getByTestId("account-stats");
  await expect(stats).toBeVisible();
  await expect(page.getByTestId("metric-reach")).toHaveText(/3\D?100/);
  await expect(page.getByTestId("metric-total_interactions")).toHaveText("—");
  await expect(stats).toContainText("Meta qaytarmagan: total_interactions");

  const row = page.getByTestId("content-stats").locator("tr", { hasText: topic });
  await expect(row).toContainText("420");
  await expect(row).toContainText("12.14%"); // 51 / 420, only because Meta returned both
  await expectNoHorizontalScroll(page);
});

test("weekly analyst report is created honestly", async ({ page }) => {
  await page.goto("/analytics");
  await page.getByTestId("create-report").click();
  const report = page.getByTestId("report");
  await expect(report).toBeVisible();
  await expect(page.getByTestId("report-summary")).not.toBeEmpty();
  await expect(page.getByTestId("report-recommendations")).toBeVisible();
});
