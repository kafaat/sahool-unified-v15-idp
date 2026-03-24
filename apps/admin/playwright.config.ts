import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E Testing Configuration - Admin Dashboard
 * إعدادات Playwright لاختبارات E2E - لوحة الإدارة
 *
 * @see https://playwright.dev/docs/test-configuration
 */
const skipE2E =
  process.env.SKIP_E2E_TESTS === "true" ||
  (process.env.CI && !process.env.API_AVAILABLE);

const testMatchPattern = skipE2E
  ? ["ci-smoke.spec.ts"]
  : "**/*.spec.ts";

export default defineConfig({
  testDir: "./e2e",

  testMatch: testMatchPattern,

  fullyParallel: true,

  forbidOnly: !!process.env.CI,

  retries: process.env.CI ? 1 : 0,

  workers: process.env.CI ? 2 : undefined,

  reporter: [
    ["html", { open: process.env.CI ? "never" : "on-failure" }],
    ...(process.env.CI ? [["github" as const]] : []),
  ],

  use: {
    baseURL: process.env.ADMIN_BASE_URL || "http://localhost:3002",

    /* Collect trace when retrying the failed test */
    trace: "on-first-retry",

    /* Screenshot on failure */
    screenshot: "only-on-failure",

    /* Default viewport */
    viewport: { width: 1440, height: 900 },
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  /* Run local dev server before starting tests */
  webServer: process.env.CI
    ? undefined
    : {
        command: "npm run dev",
        url: "http://localhost:3002",
        reuseExistingServer: true,
        timeout: 120_000,
      },
});
