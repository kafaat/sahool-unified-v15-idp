/**
 * Field Audit History — React hooks
 * خطافات React لسجل تدقيق الحقل
 */

'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { fieldAuditHistoryApi } from './api';
import type {
  FieldAuditEvent,
  FieldAuditFilters,
  FieldAuditTrailPage,
  ReplayedState,
} from './types';

const DEFAULT_PAGE_SIZE = 50;

/** State shape returned by `useFieldAuditTrail`. */
export interface UseFieldAuditTrailResult {
  events: FieldAuditEvent[];
  total: number;
  hasMore: boolean;
  isLoading: boolean;
  /** Distinguishes the initial load spinner from the "loading next page"
   *  state that the infinite-scroll sentinel needs to render differently. */
  isLoadingMore: boolean;
  error: string | null;
  /** Load the next page and append it to `events`. Safe to call while a
   *  previous page load is in flight — subsequent calls will no-op. */
  loadMore: () => void;
  /** Reset pagination and reload the first page with the current filters. */
  refresh: () => void;
}

/** Paginated trail loader with infinite-scroll semantics.
 *
 *  Changing the `filters` object (by reference) triggers a full reset —
 *  we can't merge filtered-and-unfiltered pages because the trail is
 *  sorted by created_at and the newly-filtered page might overlap with
 *  previously-loaded unfiltered pages. Parents should memoise the filter
 *  object if they want to avoid needless re-fetches. */
export function useFieldAuditTrail(
  fieldId: string,
  filters: FieldAuditFilters,
  pageSize = DEFAULT_PAGE_SIZE,
): UseFieldAuditTrailResult {
  const [events, setEvents] = useState<FieldAuditEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [skip, setSkip] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Guards against race conditions: when a filter change triggers a reload
  // while a previous page request is still in flight, we must ignore the
  // stale response. Incrementing the counter on every (re)fetch-trigger
  // tags in-flight requests; only the latest tag is allowed to commit.
  const requestCounter = useRef(0);

  const fetchPage = useCallback(
    async (nextSkip: number, append: boolean) => {
      const myTag = ++requestCounter.current;
      if (append) {
        setIsLoadingMore(true);
      } else {
        setIsLoading(true);
      }
      setError(null);

      let page: FieldAuditTrailPage;
      try {
        page = await fieldAuditHistoryApi.getFieldTrail(
          fieldId,
          filters,
          { skip: nextSkip, limit: pageSize },
        );
      } catch (err) {
        if (myTag === requestCounter.current) {
          setError(err instanceof Error ? err.message : 'Unknown error');
          setIsLoading(false);
          setIsLoadingMore(false);
        }
        return;
      }

      if (myTag !== requestCounter.current) {
        // A newer request superseded this one; discard.
        return;
      }

      setEvents((prev) => (append ? [...prev, ...page.items] : page.items));
      setTotal(page.total);
      setHasMore(page.hasMore);
      setSkip(nextSkip + page.items.length);
      setIsLoading(false);
      setIsLoadingMore(false);
    },
    [fieldId, filters, pageSize],
  );

  useEffect(() => {
    // Full reset whenever fieldId or filters change.
    setEvents([]);
    setSkip(0);
    fetchPage(0, false);
  }, [fetchPage]);

  const loadMore = useCallback(() => {
    if (isLoadingMore || isLoading || !hasMore) return;
    fetchPage(skip, true);
  }, [fetchPage, hasMore, isLoading, isLoadingMore, skip]);

  const refresh = useCallback(() => {
    setEvents([]);
    setSkip(0);
    fetchPage(0, false);
  }, [fetchPage]);

  return {
    events,
    total,
    hasMore,
    isLoading,
    isLoadingMore,
    error,
    loadMore,
    refresh,
  };
}

// ─────────────────────────────────────────────────────────────────────────
// Replay — reconstruct field state at timestamp T.
// ─────────────────────────────────────────────────────────────────────────

/** Reconstruct the field's state as of `asOf` by applying every event's
 *  `newValue` in chronological order up to that point.
 *
 *  Caveats worth knowing before trusting the result:
 *   * This is a FORWARD merge of `newValue` fields. Events that recorded
 *     only an `oldValue` (deletes) remove matching keys from the state.
 *   * If retention has truncated events older than the cutoff the result
 *     is flagged `partial: true`. The hook does not fetch pre-retention
 *     snapshots — that's a separate archive lookup out of scope here.
 *   * The result is computed client-side from the events already loaded
 *     via `useFieldAuditTrail`; the parent is responsible for making sure
 *     `events` spans the requested cutoff (loadMore until earliest <= cutoff). */
export function useReplayedState(
  events: FieldAuditEvent[],
  asOf: string | null,
): ReplayedState | null {
  return useMemo(() => {
    if (!asOf) return null;

    const cutoff = Date.parse(asOf);
    if (Number.isNaN(cutoff)) return null;

    // Sort ascending in-place on a copy — the UI typically holds events
    // reverse-chronologically.
    const sorted = [...events].sort(
      (a, b) => Date.parse(a.createdAt) - Date.parse(b.createdAt),
    );

    const state: Record<string, unknown> = {};
    let applied = 0;

    for (const event of sorted) {
      const t = Date.parse(event.createdAt);
      if (t > cutoff) break;

      if (event.newValue && typeof event.newValue === 'object') {
        for (const [key, value] of Object.entries(event.newValue)) {
          state[key] = value;
        }
      } else if (event.oldValue && !event.newValue) {
        // Delete event — drop any keys present in oldValue.
        for (const key of Object.keys(event.oldValue)) {
          delete state[key];
        }
      }
      applied += 1;
    }

    // Best-effort "partial" detection: if we didn't apply any event and
    // the list is empty, we can't know whether the field simply predates
    // our trail or whether retention ate the history — flag for operator
    // attention either way.
    const partial = applied === 0 || events.length === 0;

    return {
      asOf,
      eventsApplied: applied,
      partial,
      state,
    };
  }, [events, asOf]);
}
