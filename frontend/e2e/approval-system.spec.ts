import { expect, test } from "@playwright/test";

import { apiCall, createContent, expectNoHorizontalScroll, loginAPI } from "./helpers";

test.beforeEach(async ({ page }) => {
  await page.goto("/login");
  await loginAPI(page);
});

async function approved(page: import("@playwright/test").Page, topic: string) {
  const c = await createContent(page, `${topic} ${Date.now()}`);
  await apiCall(page.request, "post", `contents/${c.id}/submit-review`);
  await apiCall(page.request, "post", `contents/${c.id}/approve`, { expected_version: 1 });
  return c;
}

test("readiness checklist is honest about blockers", async ({ page }) => {
  const c = await approved(page, "Tayyorlik");
  await page.goto(`/content/${c.id}`);
  await expect(page.getByTestId("readiness-approval")).toHaveAttribute("data-ok", "true");
  await expect(page.getByTestId("readiness-media")).toHaveAttribute("data-ok", "false");
  await expect(page.getByTestId("readiness-publisher")).toHaveAttribute("data-ok", "true");
  await expect(page.getByTestId("readiness")).toContainText("Hali nashrga tayyor emas");
  await expectNoHorizontalScroll(page);
});

test("diff shows what changed since the approved version", async ({ page }) => {
  const c = await approved(page, "Diff");
  await apiCall(page.request, "patch", `contents/${c.id}`, { expected_version: 1, caption: "Butunlay yangi caption" });
  await page.goto(`/content/${c.id}`);
  const diff = page.getByTestId("diff");
  await expect(diff).toContainText("v1 (oxirgi tasdiqlangan versiya) → v2");
  await expect(diff).toContainText("+ Butunlay yangi caption");
});

test("revoke approval returns content to review", async ({ page }) => {
  const c = await approved(page, "Revoke");
  await page.goto(`/content/${c.id}`);
  await page.getByTestId("action-revoke").click();
  await page.getByTestId("confirm-action").click();
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "READY_FOR_REVIEW");
  await expect(page.getByTestId("readiness-approval")).toHaveAttribute("data-ok", "false");
});

test("request edit with AI rework creates a new version for review", async ({ page }) => {
  const r = await apiCall<{ content_id: number }>(page.request, "post", "ai/generate-caption", { topic: "Yorug‘lik", submit_for_review: true });
  await page.goto(`/content/${r.content_id}`);
  await page.getByTestId("action-request-edit").click();
  await expect(page.getByTestId("ai-rework")).toBeChecked();
  await page.getByLabel("Izoh (ixtiyoriy)").fill("Qisqaroq va aniqroq qiling");
  await page.getByTestId("confirm-action").click();
  await expect(page.getByTestId("version")).toHaveText("v2");
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "READY_FOR_REVIEW");
  await expect(page.getByTestId("approvals")).toContainText("Tahrir so‘ralgan");
});

test("approvals page lists the queue and the decision history", async ({ page }) => {
  const c = await createContent(page, `Navbatda ${Date.now()}`);
  await apiCall(page.request, "post", `contents/${c.id}/submit-review`);
  await approved(page, "Tarixda"); // ensure at least one decision exists in this test
  await page.goto("/approvals");
  await expect(page.getByTestId("approval-queue")).toContainText("Navbatda");
  await page.getByRole("tab", { name: "Qarorlar tarixi" }).click();
  await expect(page.getByTestId("approval-log")).toContainText("Tasdiqlangan");
  await expectNoHorizontalScroll(page);
});
