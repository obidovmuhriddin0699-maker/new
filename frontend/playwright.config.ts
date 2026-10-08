import { defineConfig, devices } from "@playwright/test";

// E2E: starts the backend (SQLite, Meta dry-run) and the frontend, then checks
// that the page can reach GET /health.
// BACKEND_PYTHON lets you point at a venv interpreter, e.g.
//   PowerShell: $env:BACKEND_PYTHON = "..\backend\.venv\Scripts\python.exe"
const python = process.env.BACKEND_PYTHON ?? "python";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"]],
  use: { baseURL: "http://localhost:3000", trace: "retain-on-failure" },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
  webServer: [
    {
      command: `${python} -m uvicorn app.main:app --port 8000`,
      cwd: "../backend",
      url: "http://localhost:8000/health",
      reuseExistingServer: !process.env.CI,
      env: {
        APP_ENV: "test",
        DATABASE_URL: "sqlite:///./data/e2e.db",
        META_DRY_RUN: "true",
        CORS_ORIGINS: "http://localhost:3000",
      },
      timeout: 60_000,
    },
    {
      command: "npm run start -- --port 3000",
      url: "http://localhost:3000",
      reuseExistingServer: !process.env.CI,
      env: { NEXT_PUBLIC_API_URL: "http://localhost:8000" },
      timeout: 60_000,
    },
  ],
});
