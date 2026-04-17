/**
 * Field Audit History API — unit tests for the query-builder and the
 * snake_case → camelCase mapper. These are the two pure functions the
 * whole feature's correctness pivots on; keeping them isolated from
 * fetch() means regressions surface instantly instead of via a flaky
 * integration test.
 */

import { describe, it, expect } from 'vitest';

import { buildTrailQuery, mapBackendPage } from '../api';

describe('buildTrailQuery', () => {
  const FIELD = 'fld-test';

  it('pins the scope via resource_type=field + resource_id', () => {
    // The whole feature pivots on this; without resource_type/resource_id
    // the LOGS endpoint would return every audit row in the tenant.
    const qp = buildTrailQuery(FIELD, {}, { skip: 0, limit: 10 });
    expect(qp.get('resource_type')).toBe('field');
    expect(qp.get('resource_id')).toBe(FIELD);
  });

  it('serialises pagination into skip + limit', () => {
    const qp = buildTrailQuery(FIELD, {}, { skip: 100, limit: 50 });
    expect(qp.get('skip')).toBe('100');
    expect(qp.get('limit')).toBe('50');
  });

  it('omits category when not set (empty filter = no WHERE clause)', () => {
    const qp = buildTrailQuery(FIELD, {}, { skip: 0, limit: 10 });
    expect(qp.has('category')).toBe(false);
  });

  it('omits empty-string filters rather than forwarding them as exact matches', () => {
    // Empty-string from uncontrolled input must NOT become `user_id=` on
    // the wire — audit-service would otherwise try to match the empty
    // user_id which is always zero rows.
    const qp = buildTrailQuery(
      FIELD,
      { userId: '', category: '' },
      { skip: 0, limit: 10 },
    );
    expect(qp.has('user_id')).toBe(false);
    expect(qp.has('category')).toBe(false);
  });

  it('widens endDate to end-of-day UTC so "today" covers the whole day', () => {
    const qp = buildTrailQuery(
      FIELD,
      { startDate: '2026-04-01', endDate: '2026-04-17' },
      { skip: 0, limit: 10 },
    );
    expect(qp.get('start_date')).toBe('2026-04-01T00:00:00Z');
    expect(qp.get('end_date')).toBe('2026-04-17T23:59:59.999Z');
  });

  it('forwards category + userId verbatim', () => {
    const qp = buildTrailQuery(
      FIELD,
      { category: 'field_ops', userId: 'usr_abc' },
      { skip: 0, limit: 10 },
    );
    expect(qp.get('category')).toBe('field_ops');
    expect(qp.get('user_id')).toBe('usr_abc');
  });
});

describe('mapBackendPage', () => {
  it('converts snake_case fields to camelCase', () => {
    const page = mapBackendPage({
      items: [
        {
          id: 'evt-1',
          tenant_id: 't-1',
          seq_num: 42,
          user_id: 'usr_abc',
          action: 'field.updated',
          category: 'field_ops',
          severity: 'info',
          resource_type: 'field',
          resource_id: 'fld-99',
          correlation_id: 'corr-xyz',
          ip_address: '10.0.0.1',
          success: true,
          error_code: null,
          error_message: null,
          details: { reason: 'area recalculated' },
          old_value: { area_ha: 5.0 },
          new_value: { area_ha: 5.2 },
          entry_hash: 'a'.repeat(64),
          created_at: '2026-04-17T10:00:00Z',
        },
      ],
      total: 1,
      skip: 0,
      limit: 50,
      has_more: false,
    });

    expect(page.total).toBe(1);
    expect(page.hasMore).toBe(false);
    expect(page.items[0]).toMatchObject({
      id: 'evt-1',
      tenantId: 't-1',
      seqNum: 42,
      userId: 'usr_abc',
      resourceType: 'field',
      resourceId: 'fld-99',
      correlationId: 'corr-xyz',
      ipAddress: '10.0.0.1',
      entryHash: 'a'.repeat(64),
      createdAt: '2026-04-17T10:00:00Z',
    });
    expect(page.items[0].oldValue).toEqual({ area_ha: 5.0 });
    expect(page.items[0].newValue).toEqual({ area_ha: 5.2 });
  });

  it('coerces null details into an empty object so consumers can skip null checks', () => {
    const page = mapBackendPage({
      items: [
        {
          id: 'evt-1',
          tenant_id: 't-1',
          seq_num: 1,
          user_id: 'u',
          action: 'a',
          category: 'system',
          severity: 'info',
          resource_type: 'field',
          resource_id: 'f',
          correlation_id: null,
          ip_address: null,
          success: true,
          error_code: null,
          error_message: null,
          details: null,
          old_value: null,
          new_value: null,
          entry_hash: 'b'.repeat(64),
          created_at: '2026-04-17T10:00:00Z',
        },
      ],
      total: 1,
      skip: 0,
      limit: 50,
      has_more: false,
    });
    expect(page.items[0].details).toEqual({});
    // old/new preserved as null so DiffViewer can distinguish "empty event"
    // from "no payload".
    expect(page.items[0].oldValue).toBeNull();
    expect(page.items[0].newValue).toBeNull();
  });
});
