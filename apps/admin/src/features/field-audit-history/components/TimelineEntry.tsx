'use client';

/**
 * TimelineEntry — single audit event row inside the timeline.
 * صف واحد في الجدول الزمني
 *
 * Rendered as a `<li>` so the parent can be a semantic `<ol>` — screen
 * readers announce the ordinal position, which helps blind operators
 * orient themselves in a long trail.
 */

import { useState } from 'react';
import { ChevronDown, ChevronRight, Check, X, AlertTriangle } from 'lucide-react';

import type { FieldAuditEvent } from '../types';
import DiffViewer from './DiffViewer';

interface TimelineEntryProps {
  event: FieldAuditEvent;
  locale: 'ar' | 'en';
  /** Controls whether the diff panel is open on first render. Useful in
   *  tests (force-open) and for the "expand all" toolbar action later. */
  defaultOpen?: boolean;
}

function formatTimestamp(iso: string, locale: 'ar' | 'en'): string {
  // `new Date(garbage)` never throws — it silently returns an Invalid
  // Date whose getTime() is NaN. toLocaleString() on that yields the
  // literal string "Invalid Date", which would show up untranslated
  // in the timeline. Check NaN explicitly and fall back to the raw
  // ISO string so operators at least see the original value. A
  // try/catch is kept around toLocaleString for the rare
  // RangeError that a pathological locale option can raise.
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  try {
    return d.toLocaleString(locale === 'ar' ? 'ar-SA' : 'en-GB', {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return iso;
  }
}

const SEVERITY_BADGE: Record<string, string> = {
  critical: 'bg-red-100 text-red-800 border-red-300',
  error: 'bg-red-100 text-red-800 border-red-300',
  warning: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  info: 'bg-blue-100 text-blue-800 border-blue-300',
  debug: 'bg-gray-100 text-gray-800 border-gray-300',
};

export default function TimelineEntry({
  event,
  locale,
  defaultOpen = false,
}: TimelineEntryProps) {
  const [open, setOpen] = useState(defaultOpen);

  const severityClass = SEVERITY_BADGE[event.severity] ?? SEVERITY_BADGE.info;
  const isAr = locale === 'ar';

  return (
    <li
      className="relative py-4"
      data-testid={`timeline-entry-${event.id}`}
      data-seq-num={event.seqNum}
    >
      {/* Marker dot — positioned by the parent's RTL-aware layout so we
          don't duplicate the direction logic here. */}
      <span
        aria-hidden="true"
        className={`timeline-marker absolute top-5 h-3 w-3 rounded-full border-2 border-white shadow ${
          event.success ? 'bg-green-500' : 'bg-red-500'
        }`}
      />

      <div className="pe-2 ps-6 sm:ps-8">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="flex w-full items-start justify-between gap-3 rounded-md border border-gray-200 bg-white p-3 text-start transition hover:border-gray-300 hover:bg-gray-50"
          aria-expanded={open}
          data-testid="timeline-entry-toggle"
        >
          <div className="flex min-w-0 flex-1 flex-col gap-1">
            <div className="flex items-center gap-2">
              {event.success ? (
                <Check size={16} className="text-green-600 shrink-0" />
              ) : (
                <X size={16} className="text-red-600 shrink-0" />
              )}
              <span className="font-mono text-sm font-semibold text-gray-900 break-all">
                {event.action}
              </span>
              <span
                className={`rounded-full border px-2 py-0.5 text-xs font-medium ${severityClass}`}
              >
                {event.severity}
              </span>
              <span className="rounded-full border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs text-gray-700">
                {event.category}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-600">
              <time dateTime={event.createdAt}>
                {formatTimestamp(event.createdAt, locale)}
              </time>
              <span className="inline-flex items-center gap-1">
                <span className="font-medium">
                  {isAr ? 'المستخدم' : 'user'}:
                </span>
                <span className="font-mono">{event.userId}</span>
              </span>
              {event.ipAddress && (
                <span className="inline-flex items-center gap-1">
                  <span className="font-medium">IP:</span>
                  <span className="font-mono">{event.ipAddress}</span>
                </span>
              )}
              <span className="inline-flex items-center gap-1">
                <span className="font-medium">seq:</span>
                <span className="font-mono">{event.seqNum}</span>
              </span>
            </div>
            {event.errorMessage && (
              <div className="flex items-start gap-1 text-xs text-red-700">
                <AlertTriangle size={12} className="mt-0.5 shrink-0" />
                <span className="break-words">{event.errorMessage}</span>
              </div>
            )}
          </div>
          <span className="shrink-0 text-gray-400">
            {open ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
          </span>
        </button>

        {open && (
          <div className="mt-2 rounded-md border border-gray-200 bg-gray-50 p-3">
            <DiffViewer
              oldValue={event.oldValue}
              newValue={event.newValue}
              locale={locale}
            />
            {Object.keys(event.details).length > 0 && (
              <div className="mt-3 border-t border-gray-200 pt-3">
                <p className="mb-1 text-xs font-semibold text-gray-700">
                  {isAr ? 'تفاصيل إضافية' : 'Details'}
                </p>
                <pre className="max-h-40 overflow-auto rounded bg-white p-2 text-xs text-gray-800">
                  <code>{JSON.stringify(event.details, null, 2)}</code>
                </pre>
              </div>
            )}
            {/* Hash footer — copyable so compliance can cross-check the chain
                without hunting through DevTools. */}
            <div className="mt-3 border-t border-gray-200 pt-2 font-mono text-[10px] text-gray-500 break-all">
              hash: {event.entryHash}
            </div>
          </div>
        )}
      </div>
    </li>
  );
}
