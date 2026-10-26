import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  reporter: [["html", { outputFolder: "playwright-report", open: "never" }], ["list"]],
  use: {
    baseURL: "http://localhost:5173",
    testIdAttribute: "data-test",
    screenshot: "only-on-failure",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "setup",
      testMatch: /auth\.setup\.js/,
    },
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"], storageState: "e2e/.auth/admin.json" },
      dependencies: ["setup"],
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"], storageState: "e2e/.auth/admin.json" },
      dependencies: ["setup"],
    },
  ],
  webServer: [
    {
      command: "npm run seed && npm run dev",
      cwd: "../api",
      port: 3000,
      timeout: 120_000,
      reuseExistingServer: !process.env.CI,
      env: {
        PUERTO: "3000",
        MONGODB_CNX: "mongodb://127.0.0.1:27017/app-usuarios-e2e",
        JWT_SECRET: "secreto-e2e-suficientemente-largo",
        JWT_EXPIRA: "4h",
      },
    },
    {
      command: "npm run dev",
      port: 5173,
      timeout: 120_000,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
