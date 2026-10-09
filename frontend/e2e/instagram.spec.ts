import { createHmac } from "node:crypto";

import { expect, test, type Page } from "@playwright/test";

import { loginAPI, origin } from "./helpers";

// Meta is the local fake (backend/tests/fake_meta.py on :8200); nothing reaches instagram.com.
const APP_SECRET = "e2e-app-secret";
const IG_USER_ID = "17841400000000001";

test.describe.configure({ mode: "serial" });

test.beforeEach(async ({ page }) => {
  await page.goto("/login");
  await loginAPI(page);
});

function signedRequest(payload: Record<string, unknown>, secret = APP_SECRET): string {
  const body = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const sig = createHmac("sha256", secret).update(body).digest("base64url");
  return `${sig}.${body}`;
}

async function connect(page: Page) {
  await page.goto("/instagram");
  await page.getByRole("button", { name: "Instagram’ni ulash" }).click();
  // fake authorize -> 302 back to /instagram/callback?code=..&state=..#_ (cross-site redirect)
  await expect(page.getByTestId("oauth-success")).toBeVisible();
}

test("connects an Instagram account through the OAuth redirect", async ({ page }) => {
  await connect(page);
  await expect(page.getByTestId("oauth-success")).toContainText("@muxriddin.design.e2e");
  // The one-time code is removed from the address bar.
  await expect(page).toHaveURL(/\/instagram\/callback$/);

  await page.getByRole("link", { name: "Instagram sahifasiga o‘tish" }).click();
  await expect(page.getByTestId("instagram-status")).toHaveText(/1 ta akkaunt ulangan/);
  const account = page.getByTestId("instagram-account");
  await expect(account).toContainText(IG_USER_ID);
  await expect(account).toContainText("instagram_business_content_publish");
  await expect(page.getByTestId("token-expiry")).toContainText("kun qoldi");

  // The status API never exposes tokens or the app secret.
  const status = await (await page.request.get("/api/backend/instagram/status")).text();
  expect(status).not.toContain("long-");
  expect(status).not.toContain(APP_SECRET);
});

test("a reused callback URL is rejected (state is one-time)", async ({ page }) => {
  await page.goto("/instagram");
  let callbackUrl = "";
  page.on("framenavigated", (frame) => {
    if (frame === page.mainFrame() && frame.url().includes("/instagram/callback?")) callbackUrl = frame.url();
  });
  await page.getByRole("button", { name: "Instagram’ni ulash" }).click();
  await expect(page.getByTestId("oauth-success")).toBeVisible();
  expect(callbackUrl).toContain("state=");

  await page.goto(callbackUrl);
  await expect(page.getByTestId("oauth-error")).toContainText("yaroqsiz");
});

test("user denying consent shows a friendly error", async ({ page }) => {
  await page.route("http://127.0.0.1:8200/oauth/authorize**", (route) =>
    route.continue({ url: `${route.request().url()}&deny=true` }),
  );
  await page.goto("/instagram");
  await page.getByRole("button", { name: "Instagram’ni ulash" }).click();
  await expect(page.getByTestId("oauth-error")).toBeVisible();
  await expect(page.getByTestId("oauth-error")).not.toContainText("access_denied");
});

test("callback without a session goes to login and keeps the flow", async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto("/instagram/callback?code=abc&state=not-a-real-state-123");
  await expect(page).toHaveURL(/\/login\?next=%2Finstagram%2Fcallback%3Fcode%3Dabc/);
  await context.close();
});

test("refresh too early and disconnect", async ({ page }) => {
  await connect(page);
  await page.goto("/instagram");
  const account = page.getByTestId("instagram-account");
  await account.getByRole("button", { name: "Tokenni yangilash" }).click();
  // Meta only refreshes tokens that are at least 24 hours old.
  await expect(account.getByRole("alert")).toContainText("24");

  await account.getByRole("button", { name: "Uzish" }).click();
  await account.getByRole("button", { name: "Ha, uzish" }).click();
  await expect(page.getByTestId("instagram-status")).toHaveText("Ulanmagan");
});

test("Meta deauthorize and data deletion callbacks verify the signature", async ({ page }) => {
  await connect(page);

  const forged = await page.request.post("/api/meta/data-deletion", {
    form: { signed_request: signedRequest({ algorithm: "HMAC-SHA256", user_id: IG_USER_ID }, "wrong-secret") },
  });
  expect(forged.status()).toBe(400);

  const res = await page.request.post("/api/meta/data-deletion", {
    form: { signed_request: signedRequest({ algorithm: "HMAC-SHA256", user_id: IG_USER_ID }) },
  });
  expect(res.status()).toBe(200);
  const { url, confirmation_code } = (await res.json()) as { url: string; confirmation_code: string };
  expect(url).toContain(`/api/meta/data-deletion-status?code=${confirmation_code}`);

  const check = await page.request.get(new URL(url).pathname + new URL(url).search);
  expect(await check.json()).toMatchObject({ confirmation_code, status: "completed" });

  await page.goto("/instagram");
  await expect(page.getByTestId("instagram-status")).toHaveText("Ulanmagan");

  const deauth = await page.request.post("/api/meta/deauthorize", {
    form: { signed_request: signedRequest({ algorithm: "HMAC-SHA256", user_id: IG_USER_ID }) },
    headers: origin(page),
  });
  expect(deauth.status()).toBe(200);
});
