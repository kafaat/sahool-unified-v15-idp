'use client';

/**
 * Global Search — البحث الشامل
 * Ctrl+K / Cmd+K opens search modal
 * Searches: fields, tasks, alerts, crops, equipment, reports
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { Search, X, ArrowUp, ArrowDown, CornerDownLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SearchResult {
  id: string;
  type: 'field' | 'task' | 'alert' | 'crop' | 'equipment' | 'report';
  title: string;
  titleAr: string;
  subtitle?: string;
  icon: string;
  url: string;
  relevance: number;
}

interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
}

// ---------------------------------------------------------------------------
// Static mock data
// ---------------------------------------------------------------------------

const MOCK_DATA: SearchResult[] = [
  // Fields
  { id: 'f1', type: 'field', title: 'Wheat Field', titleAr: 'حقل القمح', subtitle: '5.2 هكتار', icon: '\uD83C\uDF3E', url: '/fields/f1', relevance: 1 },
  { id: 'f2', type: 'field', title: 'Palm Orchard', titleAr: 'بستان النخيل', subtitle: '3.0 هكتار', icon: '\uD83C\uDF34', url: '/fields/f2', relevance: 0.9 },
  { id: 'f3', type: 'field', title: 'Tomato Greenhouse', titleAr: 'بيت محمي طماطم', subtitle: '1.5 هكتار', icon: '\uD83C\uDF45', url: '/fields/f3', relevance: 0.8 },
  { id: 'f4', type: 'field', title: 'Barley Field', titleAr: 'حقل الشعير', subtitle: '4.0 هكتار', icon: '\uD83C\uDF3E', url: '/fields/f4', relevance: 0.7 },
  // Tasks
  { id: 't1', type: 'task', title: 'Irrigate Field 3', titleAr: 'ري حقل 3', subtitle: 'قيد الانتظار', icon: '\u2705', url: '/tasks/t1', relevance: 1 },
  { id: 't2', type: 'task', title: 'Soil Testing Field 1', titleAr: 'فحص تربة حقل 1', subtitle: 'مكتمل', icon: '\u2705', url: '/tasks/t2', relevance: 0.8 },
  { id: 't3', type: 'task', title: 'Fertilizer Application', titleAr: 'تسميد الحقل', subtitle: 'قيد التنفيذ', icon: '\u2705', url: '/tasks/t3', relevance: 0.7 },
  // Alerts
  { id: 'a1', type: 'alert', title: 'Low NDVI', titleAr: 'NDVI منخفض', subtitle: 'حقل 2', icon: '\u26A0\uFE0F', url: '/alerts/a1', relevance: 1 },
  { id: 'a2', type: 'alert', title: 'Frost Warning', titleAr: 'تحذير صقيع', subtitle: 'جميع الحقول', icon: '\u26A0\uFE0F', url: '/alerts/a2', relevance: 0.9 },
  { id: 'a3', type: 'alert', title: 'Pest Detected', titleAr: 'آفة مكتشفة', subtitle: 'حقل 1', icon: '\u26A0\uFE0F', url: '/alerts/a3', relevance: 0.85 },
  // Crops
  { id: 'c1', type: 'crop', title: 'Winter Wheat', titleAr: 'قمح شتوي', subtitle: 'مرحلة التفريع', icon: '\uD83C\uDF31', url: '/crops/c1', relevance: 1 },
  { id: 'c2', type: 'crop', title: 'Date Palm', titleAr: 'نخيل التمر', subtitle: 'مرحلة الإثمار', icon: '\uD83C\uDF31', url: '/crops/c2', relevance: 0.9 },
  { id: 'c3', type: 'crop', title: 'Tomato', titleAr: 'طماطم', subtitle: 'مرحلة الإزهار', icon: '\uD83C\uDF31', url: '/crops/c3', relevance: 0.8 },
  // Equipment
  { id: 'e1', type: 'equipment', title: 'Tractor JD-5075', titleAr: 'جرار JD-5075', subtitle: 'نشط', icon: '\uD83D\uDE9C', url: '/equipment/e1', relevance: 1 },
  { id: 'e2', type: 'equipment', title: 'Center Pivot #2', titleAr: 'محور مركزي #2', subtitle: 'صيانة', icon: '\uD83D\uDE9C', url: '/equipment/e2', relevance: 0.9 },
  { id: 'e3', type: 'equipment', title: 'Drone DJI Agras', titleAr: 'طائرة DJI Agras', subtitle: 'نشط', icon: '\uD83D\uDE9C', url: '/equipment/e3', relevance: 0.8 },
  // Reports
  { id: 'r1', type: 'report', title: 'Monthly Yield Report', titleAr: 'تقرير الإنتاج الشهري', subtitle: 'مارس 2026', icon: '\uD83D\uDCCA', url: '/reports/r1', relevance: 1 },
  { id: 'r2', type: 'report', title: 'Water Usage Report', titleAr: 'تقرير استهلاك المياه', subtitle: 'الربع الأول', icon: '\uD83D\uDCCA', url: '/reports/r2', relevance: 0.9 },
];

const TYPE_LABELS: Record<SearchResult['type'], string> = {
  field: 'الحقول',
  task: 'المهام',
  alert: 'التنبيهات',
  crop: 'المحاصيل',
  equipment: 'المعدات',
  report: 'التقارير',
};

const TYPE_ORDER: SearchResult['type'][] = ['field', 'task', 'alert', 'crop', 'equipment', 'report'];

// ---------------------------------------------------------------------------
// Search helper
// ---------------------------------------------------------------------------

function searchMock(query: string): SearchResult[] {
  if (!query.trim()) return MOCK_DATA;

  const q = query.toLowerCase().trim();
  return MOCK_DATA
    .filter(
      (item) =>
        item.title.toLowerCase().includes(q) ||
        item.titleAr.includes(q) ||
        (item.subtitle && item.subtitle.includes(q)) ||
        item.type.includes(q),
    )
    .sort((a, b) => b.relevance - a.relevance);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function GlobalSearch({ isOpen, onClose }: GlobalSearchProps) {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Debounce search input (300ms)
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  const results = useMemo(() => searchMock(debouncedQuery), [debouncedQuery]);

  // Group results by type in a stable order
  const grouped = useMemo(() => {
    const map = new Map<SearchResult['type'], SearchResult[]>();
    for (const r of results) {
      const list = map.get(r.type) ?? [];
      list.push(r);
      map.set(r.type, list);
    }
    const ordered: { type: SearchResult['type']; label: string; items: SearchResult[] }[] = [];
    for (const t of TYPE_ORDER) {
      const items = map.get(t);
      if (items && items.length > 0) {
        ordered.push({ type: t, label: TYPE_LABELS[t], items });
      }
    }
    return ordered;
  }, [results]);

  // Flat list for keyboard navigation
  const flatResults = useMemo(() => grouped.flatMap((g) => g.items), [grouped]);

  // Reset state when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setDebouncedQuery('');
      setSelectedIndex(0);
      // Focus input after mount
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [isOpen]);

  // Scroll selected item into view
  useEffect(() => {
    if (!listRef.current) return;
    const active = listRef.current.querySelector('[data-active="true"]');
    if (active) {
      active.scrollIntoView({ block: 'nearest' });
    }
  }, [selectedIndex]);

  // Navigate to selected result
  const navigateTo = useCallback(
    (result: SearchResult) => {
      onClose();
      router.push(result.url);
    },
    [onClose, router],
  );

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((prev) => (prev + 1) % Math.max(flatResults.length, 1));
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => (prev - 1 + flatResults.length) % Math.max(flatResults.length, 1));
          break;
        case 'Enter':
          e.preventDefault();
          if (flatResults[selectedIndex]) {
            navigateTo(flatResults[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
      }
    },
    [flatResults, selectedIndex, navigateTo, onClose],
  );

  // Reset selected index when results change
  useEffect(() => {
    setSelectedIndex(0);
  }, [debouncedQuery]);

  // Global Ctrl+K / Cmd+K shortcut
  useEffect(() => {
    function handleGlobalKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) {
          onClose();
        }
      }
    }
    document.addEventListener('keydown', handleGlobalKey);
    return () => document.removeEventListener('keydown', handleGlobalKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Build a running flat index for mapping group items to flat index
  let flatIndex = 0;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
      role="dialog"
      aria-modal="true"
      aria-label="البحث الشامل"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        dir="rtl"
        className="relative w-full max-w-xl mx-4 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden"
        onKeyDown={handleKeyDown}
      >
        {/* Search Input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <Search className="w-5 h-5 text-gray-400 shrink-0" aria-hidden="true" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="ابحث في كل شيء..."
            className="flex-1 bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 text-base outline-none"
            aria-label="ابحث في كل شيء"
          />
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-md"
            aria-label="إغلاق البحث"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results */}
        <div
          ref={listRef}
          className="max-h-[50vh] overflow-y-auto overscroll-contain py-2"
          role="listbox"
          aria-label="نتائج البحث"
        >
          {flatResults.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-400 dark:text-gray-500 text-sm">
              لا توجد نتائج
            </div>
          ) : (
            grouped.map((group) => {
              const groupItems = group.items.map((item) => {
                const idx = flatIndex++;
                const isActive = idx === selectedIndex;
                return (
                  <button
                    key={item.id}
                    type="button"
                    role="option"
                    aria-selected={isActive}
                    data-active={isActive}
                    onClick={() => navigateTo(item)}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm cursor-pointer transition-colors ${
                      isActive
                        ? 'bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                    }`}
                  >
                    <span className="text-lg leading-none shrink-0" aria-hidden="true">
                      {item.icon}
                    </span>
                    <span className="flex-1 text-right truncate">
                      <span className="font-medium">{item.titleAr}</span>
                      {item.subtitle && (
                        <span className="text-gray-400 dark:text-gray-500 mr-2">
                          — {item.subtitle}
                        </span>
                      )}
                    </span>
                  </button>
                );
              });

              return (
                <div key={group.type}>
                  <div className="px-4 pt-3 pb-1 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                    {group.label}
                  </div>
                  {groupItems}
                </div>
              );
            })
          )}
        </div>

        {/* Footer hints */}
        <div className="flex items-center justify-between gap-4 px-4 py-2.5 border-t border-gray-200 dark:border-gray-700 text-[11px] text-gray-400 dark:text-gray-500">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1">
              <CornerDownLeft className="w-3 h-3" aria-hidden="true" />
              للانتقال
            </span>
            <span className="inline-flex items-center gap-1">
              <ArrowUp className="w-3 h-3" aria-hidden="true" />
              <ArrowDown className="w-3 h-3" aria-hidden="true" />
              للتنقل
            </span>
          </div>
          <span>
            <kbd className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-[10px] font-mono">
              Esc
            </kbd>{' '}
            إغلاق
          </span>
        </div>
      </div>
    </div>
  );
}
