import { expect, test } from "@playwright/test";

import { apiCall, createContent, expectNoHorizontalScroll, loginAPI } from "./helpers";

test.beforeEach(async ({ page }) => {
  await page.goto("/login");
  await loginAPI(page);
});

test("AI Studio generates a carousel draft (mock provider)", async ({ page }) => {
  await page.goto("/ai");
  await page.getByRole("tab", { name: "Karusel" }).click();
  await page.locator('input[name="topic"]').fill("Minimalist yotoqxona");
  await page.getByTestId("ai-generate").click();
  await expect(page.getByTestId("ai-result")).toBeVisible();
  await expect(page.getByTestId("quality-report")).toContainText("Tekshiruvdan o‘tdi");
  await page.getByTestId("ai-result-link").click();
  await expect(page.getByTestId("slides")).toContainText("Slayd 1");
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "DRAFT");
});

test("regenerate creates a new version for review", async ({ page }) => {
  const r = await apiCall<{ content_id: number }>(page.request, "post", "ai/generate-caption", { topic: "Yorug‘lik", submit_for_review: true });
  await page.goto(`/content/${r.content_id}`);
  await page.getByTestId("action-regenerate").click();
  await page.getByTestId("confirm-action").click();
  await expect(page.getByTestId("version")).toHaveText("v2");
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "READY_FOR_REVIEW");
});

test("scheduled content appears in the calendar with actions", async ({ page }) => {
  const c = await createContent(page, `Kalendar ${Date.now()}`);
  await apiCall(page.request, "post", `contents/${c.id}/submit-review`);
  await apiCall(page.request, "post", `contents/${c.id}/approve`, { expected_version: 1 });
  const when = new Date(Date.now() + 2 * 3600 * 1000).toISOString();
  await apiCall(page.request, "post", `contents/${c.id}/schedule`, { scheduled_at: when });

  await page.goto("/calendar");
  await page.getByRole("tab", { name: "Hafta" }).click();
  const item = page.getByTestId("calendar-item").filter({ hasText: "Kalendar" }).first();
  await expect(item).toBeVisible();
  await item.click();
  await expect(page.getByTestId("calendar-selected")).toContainText("Rejalashtirilgan");
  await page.getByRole("link", { name: "Ko‘rish" }).click();
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "SCHEDULED");
});

test("overview shows counters without invented analytics", async ({ page }) => {
  await page.goto("/overview");
  await expect(page.getByTestId("stat-total")).toBeVisible();
  await expect(page.getByTestId("stat-reach")).toContainText("Ma’lumot yo‘q");
  await expect(page.getByTestId("backend-status")).toHaveAttribute("data-status", /^(ok|degraded)$/);
  await expectNoHorizontalScroll(page);
});
