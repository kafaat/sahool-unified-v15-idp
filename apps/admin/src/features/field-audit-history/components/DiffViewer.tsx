'use client';

/**
 * DiffViewer — JSON before/after renderer for a single audit event.
 * مُعاين الفروقات لحدث تدقيق واحد
 *
 * Shows three columns of flat key-by-key diff:
 *   ─ removed keys (present in `oldValue`, absent in `newValue`)
 *   ─ changed keys (present in both, different serialised form)
 *   ─ added   keys (absent in `oldValue`, present in `newValue`)
 *
 * Deliberately shallow: SAHOOL audit events don't nest more than one or
 * two levels in practice (usually flat dicts from model.to_dict()), and a
 * recursive diff obscures the most common case — a single field changed —
 * under a tree of noise. If a value itself is an object, we show the JSON
 * serialisation as-is; readers looking for sub-field diffs can open the
 * "raw" disclosure.
 */

import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface DiffViewerProps {
  oldValue: Record<string, unknown> | null;
  newValue: Record<string, unknown> | null;
  /** Optional locale for the "(raw JSON)" disclosure label. */
  locale?: 'ar' | 'en';
}

type DiffRowKind = 'added' | 'removed' | 'changed';

interface DiffRow {
  key: string;
  kind: DiffRowKind;
  oldSerialised: string | null;
  newSerialised: string | null;
}

function serialise(value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return '[unserialisable]';
  }
}

/** Exported for unit tests. */
export function computeDiff(
  oldValue: Record<string, unknown> | null,
  newValue: Record<string, unknown> | null,
): DiffRow[] {
  const oldObj = oldValue ?? {};
  const newObj = newValue ?? {};
  const keys = new Set<string>([...Object.keys(oldObj), ...Object.keys(newObj)]);
  const rows: DiffRow[] = [];

  for (const key of Array.from(keys).sort()) {
    const hadOld = Object.prototype.hasOwnProperty.call(oldObj, key);
    const hadNew = Object.prototype.hasOwnProperty.call(newObj, key);
    const oldS = hadOld ? serialise(oldObj[key]) : null;
    const newS = hadNew ? serialise(newObj[key]) : null;

    if (hadOld && !hadNew) {
      rows.push({ key, kind: 'removed', oldSerialised: oldS, newSerialised: null });
    } else if (!hadOld && hadNew) {
      rows.push({ key, kind: 'added', oldSerialised: null, newSerialised: newS });
    } else if (oldS !== newS) {
      rows.push({ key, kind: 'changed', oldSerialised: oldS, newSerialised: newS });
    }
    // Identical serialisations are skipped — nothing to show.
  }
  return rows;
}

const KIND_STYLES: Record<DiffRowKind, string> = {
  added: 'bg-green-50 border-green-200 text-green-900',
  removed: 'bg-red-50 border-red-200 text-red-900',
  changed: 'bg-yellow-50 border-yellow-200 text-yellow-900',
};

const KIND_LABEL_AR: Record<DiffRowKind, string> = {
  added: 'مُضاف',
  removed: 'محذوف',
  changed: 'مُغيَّر',
};

const KIND_LABEL_EN: Record<DiffRowKind, string> = {
  added: 'added',
  removed: 'removed',
  changed: 'changed',
};

export default function DiffViewer({
  oldValue,
  newValue,
  locale = 'en',
}: DiffViewerProps) {
  const [showRaw, setShowRaw] = useState(false);
  const rows = computeDiff(oldValue, newValue);

  // An event with NO old_value AND NO new_value has nothing to render —
  // this happens for reads and pure-effect events (e.g. "field.exported").
  // Return a muted placeholder instead of an empty block.
  if (oldValue === null && newValue === null) {
    return (
      <p className="text-sm text-gray-500 italic" data-testid="diff-empty">
        {locale === 'ar'
          ? 'لا توجد تغييرات مُسجَّلة في هذا الحدث'
          : 'No change payload recorded for this event'}
      </p>
    );
  }

  // Both sides present but no shallow differences — reader probably wants
  // to see the raw values anyway (there may be nested changes we didn't
  // expose). Render the raw disclosure open by default.
  const forceRaw = rows.length === 0;
  const rawOpen = forceRaw || showRaw;

  return (
    <div className="space-y-2" data-testid="diff-viewer">
      {rows.length > 0 && (
        <ul className="space-y-1">
          {rows.map((row) => (
            <li
              key={row.key}
              className={`rounded border px-3 py-2 text-sm ${KIND_STYLES[row.kind]}`}
              data-testid={`diff-row-${row.kind}`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono font-semibold">{row.key}</span>
                <span className="text-xs uppercase tracking-wide">
                  {locale === 'ar' ? KIND_LABEL_AR[row.kind] : KIND_LABEL_EN[row.kind]}
                </span>
              </div>
              {row.kind === 'changed' && (
                <div className="mt-1 flex flex-col gap-1 font-mono text-xs">
                  <span className="line-through text-red-700 break-all">
                    {row.oldSerialised}
                  </span>
                  <span className="text-green-700 break-all">
                    {row.newSerialised}
                  </span>
                </div>
              )}
              {row.kind === 'removed' && (
                <div className="mt-1 font-mono text-xs text-red-700 break-all">
                  {row.oldSerialised}
                </div>
              )}
              {row.kind === 'added' && (
                <div className="mt-1 font-mono text-xs text-green-700 break-all">
                  {row.newSerialised}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}

      <button
        type="button"
        className="inline-flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900"
        onClick={() => setShowRaw((v) => !v)}
        aria-expanded={rawOpen}
        data-testid="diff-raw-toggle"
      >
        {rawOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        {locale === 'ar' ? 'عرض JSON الخام' : 'Show raw JSON'}
      </button>

      {rawOpen && (
        <div className="grid grid-cols-1 gap-2 md:grid-cols-2" data-testid="diff-raw">
          <pre className="max-h-60 overflow-auto rounded bg-gray-50 p-2 text-xs text-gray-800">
            <code>{JSON.stringify(oldValue ?? null, null, 2)}</code>
          </pre>
          <pre className="max-h-60 overflow-auto rounded bg-gray-50 p-2 text-xs text-gray-800">
            <code>{JSON.stringify(newValue ?? null, null, 2)}</code>
          </pre>
        </div>
      )}
    </div>
  );
}
