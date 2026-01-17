import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E Testing Configuration
 * إعدادات Playwright لاختبارات E2E
 *
 * @see https://playwright.dev/docs/test-configuration
 */
// Skip E2E tests in CI when backend is not available
// Set SKIP_E2E_TESTS=true or ensure API_AVAILABLE is set to enable E2E tests in CI
const skipE2E =
  process.env.SKIP_E2E_TESTS === "true" ||
  (process.env.CI && !process.env.API_AVAILABLE);

export default defineConfig({
  testDir: "./e2e",

  /* Skip all tests if backend is not available */
  testMatch: skipE2E ? ["no-tests-to-run.spec.ts"] : "**/*.spec.ts",

  /* Run tests in files in parallel */
  fullyParallel: true,

  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,

  /* Retry on CI only */
  retries: process.env.CI ? 1 : 0,

  /* Use 2 workers in CI for faster execution */
  workers: process.env.CI ? 2 : undefined,

  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["json", { outputFile: "test-results/results.json" }],
    ["list"],
  ],

  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000",

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: process.env.CI ? "off" : "on-first-retry",

    /* Take screenshot on failure */
    screenshot: "only-on-failure",

    /* Disable video in CI for faster tests */
    video: process.env.CI ? "off" : "retain-on-failure",

    /* Default timeout for actions */
    actionTimeout: 10000,

    /* Default navigation timeout */
    navigationTimeout: 20000,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1920, height: 1080 },
        // Use new headless mode compatible with modern Chrome
        launchOptions: {
          args: ["--headless=new"],
        },
      },
    },

    {
      name: "firefox",
      use: {
        ...devices["Desktop Firefox"],
        viewport: { width: 1920, height: 1080 },
      },
    },

    {
      name: "webkit",
      use: {
        ...devices["Desktop Safari"],
        viewport: { width: 1920, height: 1080 },
      },
    },

    /* Test against mobile viewports. */
    {
      name: "Mobile Chrome",
      use: { ...devices["Pixel 5"] },
    },
    {
      name: "Mobile Safari",
      use: { ...devices["iPhone 12"] },
    },
  ],

  /* Run your local dev server before starting the tests */
  /* In CI, the server is started by the workflow, so we skip webServer */
  webServer: process.env.CI
    ? undefined
    : {
        command: "npm run dev",
        url: "http://localhost:3000",
        reuseExistingServer: true,
        timeout: 120 * 1000,
      },

  /* Global timeout for each test */
  timeout: 30 * 1000, // 30 seconds

  /* Global timeout for the entire test run */
  globalTimeout: 15 * 60 * 1000, // 15 minutes

  /* Folder for test artifacts such as screenshots, videos, traces, etc. */
  outputDir: "test-results/",

  /* Expect timeout */
  expect: {
    timeout: 10 * 1000,
  },
});
