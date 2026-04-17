'use client';

/**
 * Timeline — reverse-chronological list of field audit events.
 * الجدول الزمني — أحداث تدقيق الحقل مرتّبة من الأحدث
 *
 * RTL note (the "edge case" the spec flagged):
 *  The vertical rail and marker dots sit on a fixed side of each entry,
 *  so their positioning must flip between LTR and RTL. We avoid computing
 *  `start/end` math inline and rely on two Tailwind classes driven by the
 *  `dir` prop — keeps the RTL-specific logic in one place.
 *
 *  There is also an `IntersectionObserver` sentinel at the bottom that
 *  triggers `onLoadMore()` when the list is scrolled near its end. When
 *  the list fits without a scrollbar (e.g. very short trails) the sentinel
 *  never intersects, so parents must ALSO render an explicit "Load more"
 *  button if `hasMore` is true — see FieldAuditHistoryPage for the pattern.
 */

import { useEffect, useRef } from 'react';

import type { FieldAuditEvent } from '../types';
import TimelineEntry from './TimelineEntry';

interface TimelineProps {
  events: FieldAuditEvent[];
  locale: 'ar' | 'en';
  dir: 'ltr' | 'rtl';
  hasMore: boolean;
  isLoadingMore: boolean;
  onLoadMore: () => void;
}

export default function Timeline({
  events,
  locale,
  dir,
  hasMore,
  isLoadingMore,
  onLoadMore,
}: TimelineProps) {
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!hasMore) return;
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting && !isLoadingMore) {
            onLoadMore();
          }
        }
      },
      // rootMargin keeps us from ONLY firing when the sentinel is fully
      // on-screen — trigger a little before so the next page is warm by
      // the time the user reaches it.
      { rootMargin: '200px 0px' },
    );
    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, isLoadingMore, onLoadMore]);

  if (events.length === 0) {
    return (
      <div
        className="rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center text-sm text-gray-500"
        data-testid="timeline-empty"
      >
        {locale === 'ar'
          ? 'لا توجد أحداث تدقيق مُسجَّلة لهذا الحقل حتى الآن.'
          : 'No audit events recorded for this field yet.'}
      </div>
    );
  }

  // The rail is a colored left/right border on the `<ol>` itself; the dots
  // are absolutely positioned inside each `<li>` at the same offset. Flip
  // both with a single class switch driven by `dir`.
  const railClass =
    dir === 'rtl'
      ? 'border-r-2 border-gray-200 pr-6 [&_.timeline-marker]:right-[-7px]'
      : 'border-l-2 border-gray-200 pl-6 [&_.timeline-marker]:left-[-7px]';

  return (
    <div className="space-y-3">
      <ol
        className={`relative ${railClass}`}
        data-testid="timeline"
        aria-label={
          locale === 'ar' ? 'جدول زمني لأحداث التدقيق' : 'Audit events timeline'
        }
      >
        {events.map((event) => (
          <TimelineEntry key={event.id} event={event} locale={locale} />
        ))}
      </ol>

      {hasMore && (
        <div ref={sentinelRef} className="flex justify-center py-4">
          <button
            type="button"
            onClick={onLoadMore}
            disabled={isLoadingMore}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
            data-testid="timeline-load-more"
          >
            {isLoadingMore
              ? locale === 'ar'
                ? 'جاري التحميل...'
                : 'Loading…'
              : locale === 'ar'
                ? 'تحميل المزيد'
                : 'Load more'}
          </button>
        </div>
      )}
    </div>
  );
}
