import { expect, test } from "@playwright/test";

import { apiCall, createContent, loginAPI, origin } from "./helpers";

type ContentRead = { id: number; version: number; aspect_ratio: string | null; scheduled_at: string | null };

test.beforeEach(async ({ page }) => {
  await page.goto("/login");
  await loginAPI(page);
});

test("create form sends the aspect ratio allowed for the chosen type", async ({ page }) => {
  await page.goto("/content/new");
  const ratio = page.getByTestId("aspect-ratio");
  await expect(ratio).toHaveValue("4:5"); // POST default

  await page.getByLabel("Turi").selectOption("REELS");
  await expect(ratio).toHaveValue("9:16");
  await expect(ratio.locator("option")).toHaveCount(1);

  await page.getByLabel("Turi").selectOption("POST");
  await expect(ratio).toHaveValue("4:5");
  await ratio.selectOption("1:1");
  const topic = `Format ${Date.now()}`;
  await page.getByLabel("Mavzu").fill(topic);
  await page.getByRole("button", { name: "Saqlash" }).click();
  await expect(page).toHaveURL(/\/content\/\d+$/);

  const id = page.url().split("/").pop();
  const c = await apiCall<ContentRead>(page.request, "get", `contents/${id}`);
  expect(c.aspect_ratio).toBe("1:1");
});

test("edit form changes the aspect ratio", async ({ page }) => {
  const c = await createContent(page, `Tahrir formati ${Date.now()}`, { aspect_ratio: "4:5" });
  await page.goto(`/content/${c.id}?action=edit`);
  await page.getByTestId("edit-aspect-ratio").selectOption("16:9");
  await page.getByRole("button", { name: "Saqlash (yangi versiya)" }).click();
  await expect(page.getByTestId("version")).toHaveText("v2");
  const after = await apiCall<ContentRead>(page.request, "get", `contents/${c.id}`);
  expect(after.aspect_ratio).toBe("16:9");
});

test("?action=edit is ignored when the status is not editable", async ({ page }) => {
  const c = await createContent(page, `Rad ${Date.now()}`);
  await apiCall(page.request, "post", `contents/${c.id}/submit-review`);
  await apiCall(page.request, "post", `contents/${c.id}/reject`, { expected_version: 1 });
  await page.goto(`/content/${c.id}?action=edit`);
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "REJECTED");
  await expect(page.getByTestId("edit-form")).toHaveCount(0);
});

test.describe("schedule time", () => {
  // A browser far from Tashkent: the input must still be read as Tashkent time (UTC+5).
  test.use({ timezoneId: "America/New_York" });

  test("is interpreted as Asia/Tashkent regardless of the browser zone", async ({ page }) => {
    const c = await createContent(page, `Toshkent vaqti ${Date.now()}`);
    await apiCall(page.request, "post", `contents/${c.id}/submit-review`);
    await apiCall(page.request, "post", `contents/${c.id}/approve`, { expected_version: 1 });
    await page.goto(`/content/${c.id}`);
    await page.getByTestId("action-schedule").click();
    await page.getByTestId("schedule-at").fill("2030-01-15T10:00");
    await page.getByTestId("confirm-action").click();
    await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "SCHEDULED");

    const after = await apiCall<ContentRead>(page.request, "get", `contents/${c.id}`);
    expect(new Date(after.scheduled_at!).toISOString()).toBe("2030-01-15T05:00:00.000Z");
  });
});

test("proxy refuses an oversized JSON body with 413", async ({ page }) => {
  const res = await page.request.post("/api/backend/contents", {
    data: { content_type: "POST", caption: "x".repeat(1_100_000) },
    headers: origin(page),
  });
  expect(res.status()).toBe(413);
  // Multi-byte text is measured in bytes, not characters (600k chars = 1.2 MB).
  const wide = await page.request.post("/api/backend/contents", {
    data: { content_type: "POST", caption: "ў".repeat(600_000) },
    headers: origin(page),
  });
  expect(wide.status()).toBe(413);
});
