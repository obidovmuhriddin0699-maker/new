import { expect, type APIRequestContext, type Page } from "@playwright/test";

export const ADMIN = { email: "admin@example.com", password: "e2e-admin-password-123" };

export function origin(page: Page): Record<string, string> {
  return { Origin: new URL(page.url() === "about:blank" ? "http://localhost:3100" : page.url()).origin };
}

export async function loginUI(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Email").fill(ADMIN.email);
  await page.getByLabel("Parol").fill(ADMIN.password);
  await page.getByRole("button", { name: "Kirish" }).click();
  await expect(page).toHaveURL(/\/overview/);
}

/** Log in through the API (sets the httpOnly cookie in the page's context). */
export async function loginAPI(page: Page) {
  const res = await page.request.post("/api/auth/login", {
    data: ADMIN,
    headers: { Origin: "http://localhost:3100" },
  });
  expect(res.ok()).toBeTruthy();
}

export async function apiCall<T>(request: APIRequestContext, method: "get" | "post" | "patch" | "delete", path: string, data?: unknown): Promise<T> {
  const res = await request[method](`/api/backend/${path}`, {
    data,
    headers: { Origin: "http://localhost:3100" },
  });
  expect(res.ok(), `${method.toUpperCase()} ${path} -> ${res.status()} ${await res.text()}`).toBeTruthy();
  return (res.status() === 204 ? undefined : await res.json()) as T;
}

export type Created = { id: number; version: number; status: string };

export async function createContent(page: Page, topic: string, extra: Record<string, unknown> = {}): Promise<Created> {
  return apiCall<Created>(page.request, "post", "contents", {
    content_type: "POST",
    language: "uz",
    topic,
    hook: "Kichik xona ham keng ko‘rinishi mumkin.",
    caption: `${topic}: ochiq ranglar va tabiiy yorug‘lik xonani kengroq ko‘rsatadi.`,
    cta: "Saqlab qo‘ying.",
    hashtags: ["#interiordesign"],
    ...extra,
  });
}

export async function expectNoHorizontalScroll(page: Page) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
}

/** App alerts only (Next.js adds its own empty role="alert" route announcer). */
export function appAlerts(page: Page) {
  return page.locator('[role="alert"]:not(#__next-route-announcer__)');
}
