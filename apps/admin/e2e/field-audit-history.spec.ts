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
    // The page now hits `/audit/logs?resource_type=field&resource_id=…`
    // (the LOGS endpoint supports the page's filters; the dedicated
    // RESOURCE_TRAIL endpoint only supports skip/limit). We match on the
    // pathname AND the resource_id query param so a future test that
    // mocks a DIFFERENT field id can coexist without route collision.
    await page.route(
      (url) =>
        url.pathname.endsWith('/audit/logs') &&
        url.searchParams.get('resource_id') === FIELD_ID,
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

// ─────────────────────────────────────────────────────────────────────────
// Deep-link from the general audit page.
// Separate describe block so it can intercept a different backend URL
// (the LOGS list) without interfering with the trail-mocking setup above.
// ─────────────────────────────────────────────────────────────────────────

const FIELD_ROW_ID = 'fld-deeplink-0001';
const NON_FIELD_ROW_ID = 'usr-42';

const GENERAL_AUDIT_FIXTURE = {
  data: [
    {
      id: 'log-1',
      timestamp: '2026-04-17T10:05:00Z',
      user_id: 'usr_admin',
      user_email: 'admin@sahool.io',
      action: 'update',
      resource_type: 'field',
      resource_id: FIELD_ROW_ID,
      ip_address: '10.0.0.1',
      details: {},
      status: 'success' as const,
    },
    {
      id: 'log-2',
      timestamp: '2026-04-17T10:00:00Z',
      user_id: 'usr_admin',
      user_email: 'admin@sahool.io',
      action: 'update',
      resource_type: 'user',
      resource_id: NON_FIELD_ROW_ID,
      ip_address: '10.0.0.1',
      details: {},
      status: 'success' as const,
    },
  ],
  meta: { total: 2, page: 1, limit: 20, totalPages: 1 },
};

test.describe('General /audit page → deep-link to per-field history', () => {
  test.beforeEach(async ({ page }) => {
    await page.route(
      (url) => url.pathname.endsWith('/audit/logs'),
      (route) =>
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(GENERAL_AUDIT_FIXTURE),
        }),
    );
    await page.route(
      (url) => url.pathname.endsWith('/audit/stats'),
      (route) =>
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            total_logs: 2,
            actions_today: 2,
            unique_users: 1,
            failure_rate: 0,
            top_actions: [],
          }),
        }),
    );
  });

  test('renders View-history link only for field rows', async ({ page }) => {
    await page.goto('/audit', { waitUntil: 'networkidle' });
    if (page.url().includes('/login')) {
      test.skip(true, 'admin requires auth in this environment');
    }

    // Field row has the link.
    await expect(
      page.getByTestId(`view-field-history-${FIELD_ROW_ID}`),
    ).toBeVisible();
    // User row does NOT (the render returns null for non-field rows).
    await expect(
      page.getByTestId(`view-field-history-${NON_FIELD_ROW_ID}`),
    ).toHaveCount(0);
  });

  test('clicking the link navigates to /audit/fields/[id]', async ({ page }) => {
    await page.goto('/audit', { waitUntil: 'networkidle' });
    if (page.url().includes('/login')) {
      test.skip(true, 'admin requires auth in this environment');
    }

    const link = page.getByTestId(`view-field-history-${FIELD_ROW_ID}`);
    await expect(link).toHaveAttribute(
      'href',
      `/audit/fields/${FIELD_ROW_ID}`,
    );
  });
});
