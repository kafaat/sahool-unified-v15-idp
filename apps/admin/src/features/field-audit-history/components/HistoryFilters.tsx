'use client';

/**
 * HistoryFilters — filter panel for the Field Audit History page.
 * لوحة التصفية لسجل تدقيق الحقل
 *
 * Keeps the filter state local until the operator hits Apply. We avoid
 * debounced live-apply here because the trail query hits audit-service
 * directly (no admin-app cache) and fires on every keystroke would hit
 * the rate-limit fast on a field with many events.
 */

import { useState, useEffect } from 'react';
import { Filter, X as XIcon } from 'lucide-react';

import type { FieldAuditFilters } from '../types';

interface HistoryFiltersProps {
  value: FieldAuditFilters;
  onChange: (next: FieldAuditFilters) => void;
  locale: 'ar' | 'en';
}

/** The full canonical category set from audit_log's chk_category CHECK
 *  constraint. Kept in sync with:
 *    * apps/services/audit-service/migrations/001_create_audit_log.sql
 *    * apps/services/audit-retention-worker/src/policies.py KNOWN_CATEGORIES
 *  Filtering by an unlisted category would silently match zero rows
 *  (audit-service does an exact equality check), so any new category in
 *  the DB constraint MUST be added here too — and vice-versa. */
const CATEGORIES: readonly string[] = [
  'authentication',
  'authorization',
  'configuration',
  'catalog',
  'kubernetes',
  'field_ops',
  'billing',
  'compliance',
  'security',
  'data',
  'system',
  'user_management',
  'code_change',
] as const;

export default function HistoryFilters({
  value,
  onChange,
  locale,
}: HistoryFiltersProps) {
  const [draft, setDraft] = useState<FieldAuditFilters>(value);
  const isAr = locale === 'ar';

  // Keep local draft in sync when the parent resets filters (e.g. via "clear").
  useEffect(() => {
    setDraft(value);
  }, [value]);

  const apply = () => onChange(draft);
  const clear = () => {
    const empty: FieldAuditFilters = {};
    setDraft(empty);
    onChange(empty);
  };
  const hasAny =
    Boolean(draft.category) ||
    Boolean(draft.userId) ||
    Boolean(draft.startDate) ||
    Boolean(draft.endDate);

  return (
    <section
      className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
      data-testid="history-filters"
    >
      <header className="mb-3 flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-gray-900">
          <Filter size={16} />
          {isAr ? 'تصفية' : 'Filters'}
        </h2>
        {hasAny && (
          <button
            type="button"
            onClick={clear}
            className="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-gray-900"
            data-testid="filters-clear"
          >
            <XIcon size={12} />
            {isAr ? 'مسح الكل' : 'Clear all'}
          </button>
        )}
      </header>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-gray-700">{isAr ? 'التصنيف' : 'Category'}</span>
          <select
            value={draft.category ?? ''}
            onChange={(e) =>
              setDraft({ ...draft, category: e.target.value || undefined })
            }
            className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
            data-testid="filter-category"
          >
            <option value="">{isAr ? 'الكل' : 'All'}</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span className="text-gray-700">
            {isAr ? 'معرّف المستخدم' : 'User ID'}
          </span>
          <input
            type="text"
            value={draft.userId ?? ''}
            onChange={(e) =>
              setDraft({ ...draft, userId: e.target.value || undefined })
            }
            placeholder={isAr ? 'مثال: usr_...' : 'e.g. usr_…'}
            className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
            data-testid="filter-user-id"
          />
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span className="text-gray-700">{isAr ? 'من' : 'From'}</span>
          <input
            type="date"
            value={draft.startDate ?? ''}
            onChange={(e) =>
              setDraft({ ...draft, startDate: e.target.value || undefined })
            }
            className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
            data-testid="filter-start-date"
          />
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span className="text-gray-700">{isAr ? 'إلى' : 'To'}</span>
          <input
            type="date"
            value={draft.endDate ?? ''}
            onChange={(e) =>
              setDraft({ ...draft, endDate: e.target.value || undefined })
            }
            className="rounded-md border border-gray-300 px-2 py-1.5 text-sm"
            data-testid="filter-end-date"
          />
        </label>
      </div>

      <div className="mt-3 flex justify-end">
        <button
          type="button"
          onClick={apply}
          className="rounded-md bg-blue-600 px-4 py-1.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700"
          data-testid="filters-apply"
        >
          {isAr ? 'تطبيق' : 'Apply'}
        </button>
      </div>
    </section>
  );
}
