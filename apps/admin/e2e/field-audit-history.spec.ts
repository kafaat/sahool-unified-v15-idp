import { test, expect } from '@playwright/test';

/**
 * Field Audit History — CI smoke tests
 * اختبارات تدخين — سجل تدقيق الحقل
 *
 * These tests intercept the audit-service call so the suite can run in
 * CI with no backend (same posture as ci-smoke.spec.ts). A full
 * integration test against a live audit-service belongs in the
 * tests/e2e/ tree, not here.
 */

const FIELD_ID = 'fld-e2e-test-0001';
const PAGE_URL = `/audit/fields/${FIELD_ID}`;

// Two events representing a realistic audit_log sample — enough to exercise
// the Timeline, DiffViewer, filter panel and replay view without pulling in
// a fixture file.
const FIXTURE_PAGE = {
  items: [
    {
      id: 'evt-2',
      tenant_id: 't-1',
      seq_num: 2,
      user_id: 'usr_admin',
      action: 'field.boundary.updated',
      category: 'field_ops',
      severity: 'info',
      resource_type: 'field',
      resource_id: FIELD_ID,
      correlation_id: null,
      ip_address: '10.0.0.2',
      success: true,
      error_code: null,
      error_message: null,
      details: { note: 'corrected north edge' },
      old_value: { area_ha: 5.0 },
      new_value: { area_ha: 5.2 },
      entry_hash: 'a'.repeat(64),
      created_at: '2026-04-17T10:05:00Z',
    },
    {
      id: 'evt-1',
      tenant_id: 't-1',
      seq_num: 1,
      user_id: 'usr_admin',
      action: 'field.created',
      category: 'field_ops',
      severity: 'info',
      resource_type: 'field',
      resource_id: FIELD_ID,
      correlation_id: null,
      ip_address: '10.0.0.1',
      success: true,
      error_code: null,
      error_message: null,
      details: {},
      old_value: null,
      new_value: { area_ha: 5.0, status: 'draft' },
      entry_hash: 'b'.repeat(64),
      created_at: '2026-04-17T09:00:00Z',
    },
  ],
  total: 2,
  skip: 0,
  limit: 50,
  has_more: false,
};

test.describe('Field Audit History — static rendering with mocked backend', () => {
  test.beforeEach(async ({ page }) => {
    // Intercept both direct-service and Kong-proxied shapes of the URL.
    // The admin app's config points at SERVICE_URLS.audit + the contract
    // path; in CI that resolves to something like
    //   http://localhost:8114/api/v1/audit/resources/field/<id>/trail
    // but the same page also works behind Kong at /api/v1/audit/... —
    // intercept both so neither environment breaks the test.
    await page.route(
      (url) => url.pathname.endsWith(`/audit/resources/field/${FIELD_ID}/trail`),
      (route) =>
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(FIXTURE_PAGE),
        }),
    );
  });

  test('renders the field id + total events and the two timeline entries', async ({
    page,
  }) => {
    await page.goto(PAGE_URL, { waitUntil: 'networkidle' });

    // The page might redirect unauthenticated users to /login; if so we
    // skip the assertion rather than fail. This mirrors ci-smoke's posture.
    if (page.url().includes('/login')) {
      test.skip(true, 'admin requires auth in this environment');
    }

    await expect(page.getByTestId('field-id-chip')).toHaveText(FIELD_ID);

    // Two entries + a load-more sentinel absence (has_more=false).
    await expect(page.getByTestId(`timeline-entry-evt-1`)).toBeVisible();
    await expect(page.getByTestId(`timeline-entry-evt-2`)).toBeVisible();
    await expect(page.getByTestId('timeline-load-more')).toHaveCount(0);
  });

  test('expanding a changed event reveals the diff viewer', async ({ page }) => {
    await page.goto(PAGE_URL, { waitUntil: 'networkidle' });
    if (page.url().includes('/login')) {
      test.skip(true, 'admin requires auth in this environment');
    }

    const entry = page.getByTestId('timeline-entry-evt-2');
    await entry.getByTestId('timeline-entry-toggle').click();

    // area_ha changed 5.0 → 5.2 → exactly one "changed" row.
    await expect(entry.getByTestId('diff-row-changed')).toHaveCount(1);
    await expect(entry.getByTestId('diff-row-changed')).toContainText('area_ha');
  });

  test('filters panel submits and stays mounted', async ({ page }) => {
    await page.goto(PAGE_URL, { waitUntil: 'networkidle' });
    if (page.url().includes('/login')) {
      test.skip(true, 'admin requires auth in this environment');
    }

    const filters = page.getByTestId('history-filters');
    await expect(filters).toBeVisible();

    await filters.getByTestId('filter-category').selectOption('field_ops');
    await filters.getByTestId('filters-apply').click();

    // After apply the panel is still there and "clear all" becomes available.
    await expect(filters.getByTestId('filters-clear')).toBeVisible();
  });

  test('replay view appears when events are loaded', async ({ page }) => {
    await page.goto(PAGE_URL, { waitUntil: 'networkidle' });
    if (page.url().includes('/login')) {
      test.skip(true, 'admin requires auth in this environment');
    }

    await expect(page.getByTestId('replay-view')).toBeVisible();
  });
});
