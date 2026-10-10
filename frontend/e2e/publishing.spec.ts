import { expect, test, type Page } from "@playwright/test";

import { apiCall, createContent, expectNoHorizontalScroll, loginAPI } from "./helpers";

// Publishing runs the real code path against the local fake Meta (backend/tests/fake_meta.py).
test.describe.configure({ mode: "serial" });

// A minimal JPEG our backend validator accepts (SOI + SOF0 1080x1350 + EOI).
function jpeg(): Buffer {
  const sof = Buffer.from([0xff, 0xc0, 0x00, 0x11, 0x08, 0x05, 0x46, 0x04, 0x38, 0x03, 0x01, 0x22, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01]);
  return Buffer.concat([Buffer.from([0xff, 0xd8]), sof, Buffer.alloc(32), Buffer.from([0xff, 0xd9])]);
}

async function ensureInstagramConnected(page: Page) {
  await page.goto("/instagram");
  const status = page.getByTestId("instagram-status");
  await expect(status).toBeVisible();
  if ((await status.textContent())?.includes("Ulanmagan")) {
    await page.getByRole("button", { name: "Instagram’ni ulash" }).click();
    await expect(page.getByTestId("oauth-success")).toBeVisible();
  }
}

test.beforeEach(async ({ page }) => {
  await page.goto("/login");
  await loginAPI(page);
  await ensureInstagramConnected(page);
});

test("upload media, approve, preview and publish exactly once", async ({ page }) => {
  const c = await createContent(page, `Nashr ${Date.now()}`, { aspect_ratio: "4:5" });
  await page.goto(`/content/${c.id}`);
  await page.getByTestId("media-file").setInputFiles({ name: "photo.jpg", mimeType: "image/jpeg", buffer: jpeg() });
  await expect(page.getByTestId("asset")).toHaveCount(1);
  await expect(page.getByTestId("version")).toHaveText("v2"); // media change = new version

  await apiCall(page.request, "post", `contents/${c.id}/submit-review`);
  await apiCall(page.request, "post", `contents/${c.id}/approve`, { expected_version: 2 });
  await page.reload();
  await expect(page.getByTestId("readiness")).toContainText("Nashrga tayyor");

  await page.getByTestId("publish-preview").click();
  const plan = page.getByTestId("publish-plan");
  await expect(plan).toContainText("image_url=https://media.e2e.example/media/");
  await expect(plan).toContainText("media_publish");
  await expect(page.getByTestId("publish-caption")).toContainText("#interiordesign");

  await page.getByTestId("publish-start").click();
  await expect(page.getByTestId("publish-confirm")).toContainText("v2");
  await page.getByTestId("publish-confirm-button").click();
  await expect(page.getByTestId("publish-result")).toContainText("nashr qilindi");
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "PUBLISHED");
  await expect(page.getByTestId("permalink")).toHaveAttribute("href", /instagram\.com\/p\/E2E/);
  await expect(page.getByTestId("publish-start")).toHaveCount(0);

  // The same version can never be published twice.
  const again = await page.request.post(`/api/backend/contents/${c.id}/publish`, {
    data: { expected_version: 2 },
    headers: { Origin: "http://localhost:3100" },
  });
  expect(again.status()).toBe(409);
  await expectNoHorizontalScroll(page);
});

test("uploaded media is publicly served for Meta (no session)", async ({ page, browser }) => {
  const c = await createContent(page, `Media ${Date.now()}`, { aspect_ratio: "4:5" });
  const res = await page.request.post(`/api/backend/contents/${c.id}/assets/upload?expected_version=1`, {
    data: jpeg(),
    headers: { Origin: "http://localhost:3100", "Content-Type": "application/octet-stream" },
  });
  expect(res.status()).toBe(201);
  const url: string = (await res.json()).assets[0].public_url;
  const name = url.split("/").pop();

  const anonymous = await browser.newContext();
  const file = await anonymous.request.get(`/media/${name}`);
  expect(file.status()).toBe(200);
  expect(file.headers()["content-type"]).toBe("image/jpeg");
  expect((await file.body()).equals(jpeg())).toBeTruthy();
  expect((await anonymous.request.get("/media/not-a-real-file.jpg")).status()).toBe(404);
  await anonymous.close();
});

test("not-ready content is refused before anything reaches Meta", async ({ page }) => {
  const c = await createContent(page, `Mediasiz ${Date.now()}`, { aspect_ratio: "4:5" });
  await apiCall(page.request, "post", `contents/${c.id}/submit-review`);
  await apiCall(page.request, "post", `contents/${c.id}/approve`, { expected_version: 1 });
  await page.goto(`/content/${c.id}`);
  await page.getByTestId("publish-start").click();
  await page.getByTestId("publish-confirm-button").click();
  await expect(page.getByTestId("publish-result")).toContainText("Media");
  await expect(page.getByTestId("status-badge").first()).toHaveAttribute("data-status", "FAILED");
});

test("instagram page shows quota and unsupported features honestly", async ({ page }) => {
  await page.goto("/instagram");
  await page.getByTestId("check-limit").first().click();
  await expect(page.getByTestId("publishing-limit").first()).toContainText("/ 100");
  await expect(page.getByTestId("capabilities")).toContainText("Not supported by current Meta API");
});
