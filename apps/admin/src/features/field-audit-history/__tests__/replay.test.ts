/**
 * Replay hook — unit tests that don't need React Testing Library.
 *
 * useReplayedState is a pure useMemo; we exercise it by calling the
 * underlying logic through a tiny wrapper that bypasses React. If the
 * hook ever becomes side-effectful we'll move these to a component test.
 */

import { describe, it, expect } from 'vitest';
import { renderHook } from '@testing-library/react';

import { useReplayedState } from '../hooks';
import type { FieldAuditEvent } from '../types';

function ev(overrides: Partial<FieldAuditEvent>): FieldAuditEvent {
  return {
    id: 'id',
    tenantId: 't',
    seqNum: 0,
    userId: 'u',
    action: 'a',
    category: 'field_ops',
    severity: 'info',
    resourceType: 'field',
    resourceId: 'f',
    correlationId: null,
    ipAddress: null,
    success: true,
    errorCode: null,
    errorMessage: null,
    details: {},
    oldValue: null,
    newValue: null,
    entryHash: 'a'.repeat(64),
    createdAt: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

describe('useReplayedState', () => {
  it('returns null when no cutoff is provided', () => {
    const { result } = renderHook(() => useReplayedState([], null));
    expect(result.current).toBeNull();
  });

  it('applies newValue fields forward in chronological order', () => {
    // Events arrive reverse-chronologically from the UI; the hook must
    // re-sort ascending before folding them.
    const events: FieldAuditEvent[] = [
      ev({
        id: '3',
        seqNum: 3,
        createdAt: '2026-03-01T00:00:00Z',
        newValue: { status: 'active', area_ha: 5.2 },
      }),
      ev({
        id: '2',
        seqNum: 2,
        createdAt: '2026-02-01T00:00:00Z',
        newValue: { area_ha: 5.2 },
      }),
      ev({
        id: '1',
        seqNum: 1,
        createdAt: '2026-01-01T00:00:00Z',
        newValue: { status: 'draft', area_ha: 5.0 },
      }),
    ];

    const { result } = renderHook(() =>
      useReplayedState(events, '2026-03-15T00:00:00Z'),
    );
    expect(result.current?.eventsApplied).toBe(3);
    expect(result.current?.state).toEqual({ status: 'active', area_ha: 5.2 });
  });

  it('stops folding at the cutoff — events after are ignored', () => {
    const events: FieldAuditEvent[] = [
      ev({
        id: '1',
        seqNum: 1,
        createdAt: '2026-01-01T00:00:00Z',
        newValue: { status: 'draft' },
      }),
      ev({
        id: '2',
        seqNum: 2,
        createdAt: '2026-02-01T00:00:00Z',
        newValue: { status: 'active' },
      }),
    ];

    const { result } = renderHook(() =>
      useReplayedState(events, '2026-01-15T00:00:00Z'),
    );
    expect(result.current?.eventsApplied).toBe(1);
    expect(result.current?.state).toEqual({ status: 'draft' });
  });

  it('removes keys that match an oldValue on a delete-only event', () => {
    const events: FieldAuditEvent[] = [
      ev({
        id: '1',
        seqNum: 1,
        createdAt: '2026-01-01T00:00:00Z',
        newValue: { tag: 'x', other: 'y' },
      }),
      ev({
        id: '2',
        seqNum: 2,
        createdAt: '2026-02-01T00:00:00Z',
        oldValue: { tag: 'x' },
        newValue: null,
      }),
    ];

    const { result } = renderHook(() =>
      useReplayedState(events, '2026-03-01T00:00:00Z'),
    );
    expect(result.current?.state).toEqual({ other: 'y' });
  });

  it('flags partial=true when no events could be applied', () => {
    const { result } = renderHook(() => useReplayedState([], '2026-01-01T00:00:00Z'));
    expect(result.current?.partial).toBe(true);
    expect(result.current?.eventsApplied).toBe(0);
  });

  it('returns null for an unparseable cutoff', () => {
    const { result } = renderHook(() => useReplayedState([], 'not-a-date'));
    expect(result.current).toBeNull();
  });
});
