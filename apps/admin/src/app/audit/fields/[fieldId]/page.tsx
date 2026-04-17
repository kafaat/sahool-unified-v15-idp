'use client';

/**
 * Field Audit History Page
 * صفحة سجل تدقيق الحقل
 *
 * Route: /audit/fields/[fieldId]
 * Purpose: bilingual admin view of every audit_log row attached to a
 *          specific field, with filters, diff viewer and state replay.
 *
 * Data flow (intentionally simple — no global store, no react-query):
 *   useFieldAuditTrail  →  events[], loadMore()
 *           │
 *           ├─  <Timeline>      renders events as a reverse-chrono list
 *           │                    with per-entry <DiffViewer>
 *           │
 *           └─  <ReplayView>    uses useReplayedState(events, cutoff)
 *                                to fold newValue forward to any timestamp
 *
 * Why the page owns filter state: the hook needs a stable filter reference
 * to avoid refetch loops (see hooks.ts). We useMemo the filter object so
 * mutating a single field only triggers ONE refetch, not two.
 */

import { useMemo, useState, use } from 'react';
import Link from 'next/link';
import { ArrowLeft, RefreshCw } from 'lucide-react';

import Header from '@/components/layout/Header';
import { getLocale, getDirection } from '@/lib/i18n';
import {
  HistoryFilters,
  ReplayView,
  Timeline,
  useFieldAuditTrail,
  type FieldAuditFilters,
} from '@/features/field-audit-history';

interface PageProps {
  // Next.js 15 App Router: params is a Promise. `React.use()` unwraps it
  // on the client — we do it this way (instead of making the page async)
  // so we can use hooks below.
  params: Promise<{ fieldId: string }>;
}

export default function FieldAuditHistoryPage({ params }: PageProps) {
  const { fieldId } = use(params);
  const locale = getLocale();
  const dir = getDirection(locale);
  const isAr = locale === 'ar';

  const [filters, setFilters] = useState<FieldAuditFilters>({});
  // Memoise so the hook sees the same object reference across renders
  // until the operator actually applies a new filter.
  const stableFilters = useMemo(() => filters, [filters]);

  const {
    events,
    total,
    hasMore,
    isLoading,
    isLoadingMore,
    error,
    loadMore,
    refresh,
  } = useFieldAuditTrail(fieldId, stableFilters);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div className="flex min-w-0 flex-1 items-center gap-3">
            <Link
              href="/audit"
              className="inline-flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
              data-testid="back-to-audit"
            >
              <ArrowLeft size={16} className={dir === 'rtl' ? 'rotate-180' : ''} />
              {isAr ? 'سجل التدقيق' : 'Audit Log'}
            </Link>
          </div>
          <button
            type="button"
            onClick={refresh}
            disabled={isLoading}
            className="inline-flex items-center gap-2 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 disabled:opacity-50"
            data-testid="page-refresh"
          >
            <RefreshCw
              size={14}
              className={isLoading ? 'animate-spin' : ''}
            />
            {isAr ? 'تحديث' : 'Refresh'}
          </button>
        </div>

        <header className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">
            {isAr ? 'سجل تدقيق الحقل' : 'Field Audit History'}
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            {isAr ? 'الحقل' : 'Field'}:{' '}
            <code
              className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs"
              data-testid="field-id-chip"
            >
              {fieldId}
            </code>
            {!isLoading && (
              <span className="ms-3 text-xs text-gray-500">
                {isAr
                  ? `إجمالي الأحداث: ${total}`
                  : `Total events: ${total}`}
              </span>
            )}
          </p>
        </header>

        <div className="space-y-4">
          <HistoryFilters value={filters} onChange={setFilters} locale={locale} />

          {error && (
            <div
              className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-800"
              data-testid="page-error"
            >
              {isAr
                ? 'تعذّر تحميل السجل. حاول تحديث الصفحة.'
                : 'Failed to load history. Try refreshing the page.'}
            </div>
          )}

          {isLoading && events.length === 0 ? (
            <div
              className="rounded-lg border border-gray-200 bg-white p-8 text-center text-sm text-gray-500"
              data-testid="page-loading"
            >
              {isAr ? 'جاري التحميل...' : 'Loading…'}
            </div>
          ) : (
            <Timeline
              events={events}
              locale={locale}
              dir={dir}
              hasMore={hasMore}
              isLoadingMore={isLoadingMore}
              onLoadMore={loadMore}
            />
          )}

          {events.length > 0 && <ReplayView events={events} locale={locale} />}
        </div>
      </main>
    </div>
  );
}
