import { expect, test } from "@playwright/test";

import { createContent, expectNoHorizontalScroll, loginAPI, appAlerts } from "./helpers";

test.beforeEach(async ({ page }) => {
  await page.goto("/login");
  await loginAPI(page);
});

test("review, approve — never publishes", async ({ page }) => {
  const c = await createContent(page, `Approve oqimi ${Date.now()}`);
  await page.goto(`/content/${c.id}`);
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "DRAFT");

  await page.getByTestId("action-submit").click();
  await page.getByTestId("confirm-action").click();
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "READY_FOR_REVIEW");

  await page.getByTestId("action-approve").click();
  await expect(page.getByTestId("confirm-panel")).toContainText("1-versiyani");
  await page.getByTestId("confirm-action").click();
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "APPROVED");
  await expect(page.getByText("Tasdiqlash nashr qilmaydi")).toBeVisible();
  // Approving never publishes: publishing is a separate, explicitly confirmed action.
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "APPROVED");
  await expect(page.getByTestId("publish-start")).toBeVisible();
  await expect(page.getByTestId("approvals")).toContainText("v1 · Tasdiqlangan");
  await expectNoHorizontalScroll(page);
});

test("editing approved content creates v2 and requires a new approval", async ({ page, request }) => {
  const c = await createContent(page, `Tahrir oqimi ${Date.now()}`);
  const headers = { Origin: "http://localhost:3100" };
  await page.request.post(`/api/backend/contents/${c.id}/submit-review`, { headers });
  await page.request.post(`/api/backend/contents/${c.id}/approve`, { headers, data: { expected_version: 1 } });
  void request;

  await page.goto(`/content/${c.id}`);
  await page.getByTestId("action-edit").click();
  await expect(page.getByTestId("edit-form")).toContainText("oldingi tasdiq bekor bo‘ladi");
  await page.locator('textarea[name="caption"]').fill("Yangilangan caption matni — ikkinchi versiya.");
  await page.getByRole("button", { name: "Saqlash (yangi versiya)" }).click();

  await expect(page.getByTestId("version")).toHaveText("v2");
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "READY_FOR_REVIEW");
  await expect(page.getByTestId("caption")).toContainText("ikkinchi versiya");
  await expect(page.getByTestId("approvals")).toContainText("bekor qilingan");
});

test("reject is terminal", async ({ page }) => {
  const c = await createContent(page, `Rad etish ${Date.now()}`);
  await page.request.post(`/api/backend/contents/${c.id}/submit-review`, { headers: { Origin: "http://localhost:3100" } });
  await page.goto(`/content/${c.id}`);
  await page.getByTestId("action-reject").click();
  await page.getByLabel("Izoh (ixtiyoriy)").fill("Mavzu mos emas");
  await page.getByTestId("confirm-action").click();
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "REJECTED");
  await expect(page.getByTestId("action-approve")).toHaveCount(0);
  await expect(page.getByTestId("action-edit")).toHaveCount(0);
});

test("stale version is refused with a friendly message", async ({ page }) => {
  const c = await createContent(page, `Eskirgan versiya ${Date.now()}`);
  const headers = { Origin: "http://localhost:3100" };
  await page.request.post(`/api/backend/contents/${c.id}/submit-review`, { headers });
  await page.goto(`/content/${c.id}`);
  await expect(page.getByTestId("version")).toHaveText("v1"); // reviewer is looking at v1
  // Someone else edits meanwhile:
  await page.request.patch(`/api/backend/contents/${c.id}`, { headers, data: { expected_version: 1, caption: "Boshqa tahrir" } });
  await page.getByTestId("action-approve").click();
  await page.getByTestId("confirm-action").click();
  await expect(appAlerts(page)).toContainText("siz ko‘rgandan keyin o‘zgargan");
  // Nothing was approved; the page now shows v2 for a fresh review.
  await expect(page.getByTestId("version")).toHaveText("v2");
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "READY_FOR_REVIEW");
});

test("content queue lists and filters", async ({ page }) => {
  const c = await createContent(page, `Navbat ${Date.now()}`);
  await page.goto("/content?status=DRAFT");
  await expect(page.getByTestId("content-list")).toContainText(`Navbat`);
  await page.getByTestId("content-item").filter({ hasText: String(c.id) }).count();
  await expectNoHorizontalScroll(page);
});
