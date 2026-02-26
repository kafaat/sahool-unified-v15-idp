import { test } from "@playwright/test";

/**
 * Placeholder test for CI when backend API is not available.
 * يتم تشغيل هذا الاختبار عندما يتم تخطي اختبارات E2E في CI بسبب عدم توفر الخادم الخلفي.
 *
 * This file is referenced by playwright.config.ts when skipE2E is true.
 * It ensures Playwright exits cleanly (code 0) instead of failing with "No tests found".
 */
test("skipped - backend API not available in CI", () => {
  // Intentionally empty — E2E tests require a running backend API.
  // Set API_AVAILABLE=true in CI to run the full E2E suite.
});
