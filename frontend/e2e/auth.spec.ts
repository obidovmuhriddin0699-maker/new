import { expect, test } from "@playwright/test";

import { ADMIN, loginUI, appAlerts } from "./helpers";

test("unauthenticated users are redirected to login", async ({ page }) => {
  await page.goto("/content");
  await expect(page).toHaveURL(/\/login\?next=%2Fcontent/);
});

test("wrong password shows an error", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill(ADMIN.email);
  await page.getByLabel("Parol").fill("wrong-password-123");
  await page.getByRole("button", { name: "Kirish" }).click();
  await expect(appAlerts(page)).toContainText("noto‘g‘ri");
  await expect(page).toHaveURL(/\/login/);
});

test("session token is httpOnly and never exposed to JavaScript", async ({ page, context }) => {
  await loginUI(page);
  const cookie = (await context.cookies()).find((c) => c.name === "mx_session");
  expect(cookie?.httpOnly).toBe(true);
  expect(cookie?.sameSite).toBe("Strict");
  expect(await page.evaluate(() => document.cookie)).not.toContain("mx_session");
  expect(await page.evaluate(() => JSON.stringify(localStorage) + JSON.stringify(sessionStorage))).not.toMatch(/eyJ/);
});

test("login redirect ignores external targets", async ({ page }) => {
  await page.goto("/login?next=//evil.example.com/x");
  await page.getByLabel("Email").fill(ADMIN.email);
  await page.getByLabel("Parol").fill(ADMIN.password);
  await page.getByRole("button", { name: "Kirish" }).click();
  await expect(page).toHaveURL(/localhost:3100\/overview/);
});

test("logout clears the session", async ({ page, context }) => {
  await loginUI(page);
  await page.goto("/settings");
  await expect(page.getByTestId("me-email")).toHaveText(ADMIN.email);
  const before = (await context.cookies()).find((c) => c.name === "mx_session");
  expect(before).toBeDefined();
  await page.getByTestId("logout").click();
  await expect(page).toHaveURL(/\/login/);
  expect((await context.cookies()).find((c) => c.name === "mx_session")).toBeUndefined();

  // A copied cookie no longer works: the token was revoked on the server, not just deleted.
  await context.addCookies([before!]);
  const replay = await page.request.get("/api/backend/auth/me");
  expect(replay.status()).toBe(401);
});

test("security headers are sent by the panel", async ({ page }) => {
  const res = await page.goto("/login");
  const h = res!.headers();
  expect(h["content-security-policy"]).toContain("frame-ancestors 'none'");
  expect(h["x-frame-options"]).toBe("DENY");
  expect(h["strict-transport-security"]).toContain("max-age=");
});

test("proxy blocks cross-site writes, token-leaking routes and bad paths", async ({ page }) => {
  await loginUI(page);
  const evil = await page.request.post("/api/backend/contents", {
    data: { content_type: "POST" },
    headers: { Origin: "https://evil.example.com" },
  });
  expect(evil.status()).toBe(403);
  const noOrigin = await page.request.post("/api/backend/contents", { data: { content_type: "POST" } });
  expect(noOrigin.status()).toBe(403);
  const leak = await page.request.post("/api/backend/auth/login", {
    data: ADMIN,
    headers: { Origin: "http://localhost:3100" },
  });
  expect(leak.status()).toBe(404);
  const traversal = await page.request.get("/api/backend/contents/..%2F..%2Fhealth");
  expect([400, 404]).toContain(traversal.status());
  const loginCsrf = await page.request.post("/api/auth/login", {
    data: ADMIN,
    headers: { Origin: "https://evil.example.com" },
  });
  expect(loginCsrf.status()).toBe(403);
});
