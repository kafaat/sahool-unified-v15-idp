'use client';

/**
 * ReplayView — reconstruct and display the field's state at a chosen timestamp.
 * عرض الإعادة — إعادة بناء حالة الحقل عند وقت معيّن
 *
 * This is NOT a snapshot from archive — it's a forward-applied merge of the
 * `newValue` fields on the events currently loaded in the hook. The UI
 * communicates that distinction via a muted "based on N events" counter
 * and a yellow "partial" warning when the events list doesn't cover the
 * cutoff (e.g. because retention truncated earlier events).
 */

import { useState } from 'react';
import { History, AlertTriangle } from 'lucide-react';

import type { FieldAuditEvent } from '../types';
import { useReplayedState } from '../hooks';

interface ReplayViewProps {
  events: FieldAuditEvent[];
  locale: 'ar' | 'en';
}

export default function ReplayView({ events, locale }: ReplayViewProps) {
  const [cutoff, setCutoff] = useState<string>('');
  const isAr = locale === 'ar';

  // Pass `null` for an empty cutoff so the hook skips the computation
  // entirely — prevents re-sorting events[] on every keystroke before
  // the user has committed a value.
  const replayed = useReplayedState(events, cutoff || null);

  return (
    <section
      className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
      data-testid="replay-view"
    >
      <header className="mb-3 flex items-center gap-2">
        <History size={16} className="text-gray-600" />
        <h2 className="text-sm font-semibold text-gray-900">
          {isAr ? 'إعادة بناء الحالة' : 'Replay field state'}
        </h2>
      </header>

      <div className="flex flex-col gap-3 md:flex-row md:items-end">
        <label className="flex flex-1 flex-col gap-1 text-sm">
          <span className="text-gray-700">
            {isAr ? 'الحالة كما في' : 'State as of'}
          </span>
          <input
            type="datetime-local"
            value={cutoff}
            onChange={(e) => setCutoff(e.target.value)}
            className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
            data-testid="replay-cutoff"
          />
        </label>
        {replayed && (
          <p className="text-xs text-gray-500">
            {isAr
              ? `مبني على ${replayed.eventsApplied} حدث`
              : `Based on ${replayed.eventsApplied} event${
                  replayed.eventsApplied === 1 ? '' : 's'
                }`}
          </p>
        )}
      </div>

      {replayed && replayed.partial && (
        <div
          className="mt-3 flex items-start gap-2 rounded-md border border-yellow-300 bg-yellow-50 p-2 text-xs text-yellow-900"
          data-testid="replay-partial-warning"
        >
          <AlertTriangle size={14} className="mt-0.5 shrink-0" />
          <span>
            {isAr
              ? 'هذه إعادة بناء جزئية — قد تكون الأحداث الأقدم محذوفة بسبب سياسة الاحتفاظ.'
              : 'Partial reconstruction — earlier events may have been removed by retention.'}
          </span>
        </div>
      )}

      {replayed && (
        <pre
          className="mt-3 max-h-80 overflow-auto rounded bg-gray-50 p-3 text-xs text-gray-800"
          data-testid="replay-state"
        >
          <code>{JSON.stringify(replayed.state, null, 2)}</code>
        </pre>
      )}
    </section>
  );
}
