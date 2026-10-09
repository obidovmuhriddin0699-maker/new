import { randomBytes } from "node:crypto";

import { defineConfig, devices } from "@playwright/test";

// E2E runs an isolated stack: backend on :8100 (fresh SQLite DB, mock AI provider,
// migrations + seed) and the production frontend build on :3100. It never touches
// your dev database or a real AI/Meta account (Meta is a local fake on :8200).
//   PowerShell: $env:BACKEND_PYTHON = "..\backend\.venv\Scripts\python.exe"; npm run build; npm run test:e2e
const python = process.env.BACKEND_PYTHON ?? "python";
process.env.E2E_DB ??= `e2e-${Date.now()}.db`;
export const BACKEND_PORT = 8100;
export const FRONTEND_PORT = 3100;
export const FAKE_META_PORT = 8200; // tests/fake_meta.py — stands in for instagram.com / graph.instagram.com
const fakeMeta = `http://127.0.0.1:${FAKE_META_PORT}`;
// Throwaway Fernet key for this run only (urlsafe base64 of 32 random bytes).
process.env.E2E_FERNET_KEY ??= randomBytes(32).toString("base64url") + "=";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  fullyParallel: false,
  workers: 1, // tests share one database
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"]],
  use: { baseURL: `http://localhost:${FRONTEND_PORT}`, trace: "retain-on-failure" },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
  webServer: [
    {
      command: `${python} -m uvicorn tests.fake_meta:app --host 127.0.0.1 --port ${FAKE_META_PORT}`,
      cwd: "../backend",
      url: `${fakeMeta}/docs`,
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      command: `${python} -m alembic upgrade head && ${python} -m app.cli seed && ${python} -m uvicorn app.main:app --port ${BACKEND_PORT}`,
      cwd: "../backend",
      url: `http://localhost:${BACKEND_PORT}/health`,
      reuseExistingServer: false,
      env: {
        APP_ENV: "development",
        DATABASE_URL: `sqlite:///./data/${process.env.E2E_DB}`,
        AI_PROVIDER: "mock",
        AI_JOBS_MODE: "sync",
        META_DRY_RUN: "true",
        META_APP_ID: "e2e-app-id",
        META_APP_SECRET: "e2e-app-secret",
        META_REDIRECT_URI: `http://localhost:${FRONTEND_PORT}/instagram/callback`,
        META_OAUTH_AUTHORIZE_URL: `${fakeMeta}/oauth/authorize`,
        META_OAUTH_TOKEN_URL: `${fakeMeta}/oauth/access_token`,
        META_GRAPH_BASE_URL: fakeMeta,
        TOKEN_ENCRYPTION_KEYS: process.env.E2E_FERNET_KEY,
        PANEL_PUBLIC_URL: `http://localhost:${FRONTEND_PORT}`,
        SEED_ADMIN_EMAIL: "admin@example.com",
        SEED_ADMIN_PASSWORD: "e2e-admin-password-123",
        LOG_LEVEL: "WARNING",
      },
      timeout: 120_000,
    },
    {
      command: `npm run start -- --port ${FRONTEND_PORT}`,
      url: `http://localhost:${FRONTEND_PORT}/login`,
      reuseExistingServer: false,
      env: { BACKEND_URL: `http://localhost:${BACKEND_PORT}` },
      timeout: 120_000,
    },
  ],
});
