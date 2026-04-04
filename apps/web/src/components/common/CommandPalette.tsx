'use client';

/**
 * CommandPalette - لوحة الأوامر
 * Global search & navigation modal opened via Ctrl+K / Cmd+K.
 * 48+ commands grouped by Arabic categories with fuzzy search
 * supporting both Arabic and English queries.
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { Search, X, ArrowUp, ArrowDown, CornerDownLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Command {
  id: string;
  title: string;
  titleAr: string;
  icon: string;
  url: string;
  category: string;
  keywords?: string[];
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

// ---------------------------------------------------------------------------
// Command definitions (48+ commands)
// ---------------------------------------------------------------------------

const COMMANDS: Command[] = [
  // نظرة عامة
  { id: 'dashboard', title: 'Dashboard', titleAr: 'لوحة التحكم', icon: '\uD83D\uDCCA', url: '/dashboard', category: 'نظرة عامة', keywords: ['home', 'main', 'الرئيسية'] },

  // إدارة المزرعة
  { id: 'farms', title: 'Farms', titleAr: 'المزارع', icon: '\uD83C\uDFE1', url: '/farms', category: 'إدارة المزرعة', keywords: ['farm', 'مزرعة'] },
  { id: 'fields', title: 'Fields', titleAr: 'الحقول', icon: '\uD83C\uDF3E', url: '/fields', category: 'إدارة المزرعة', keywords: ['field', 'حقل', 'أرض'] },
  { id: 'crops', title: 'Crops', titleAr: 'المحاصيل', icon: '\uD83C\uDF31', url: '/crops', category: 'إدارة المزرعة', keywords: ['crop', 'محصول', 'زراعة'] },
  { id: 'seasons', title: 'Seasons', titleAr: 'المواسم', icon: '\uD83D\uDCC5', url: '/seasons', category: 'إدارة المزرعة', keywords: ['season', 'موسم'] },
  { id: 'inventory', title: 'Inventory', titleAr: 'المخزون', icon: '\uD83D\uDCE6', url: '/inventory', category: 'إدارة المزرعة', keywords: ['inventory', 'stock', 'مخزن'] },
  { id: 'tasks', title: 'Tasks', titleAr: 'المهام', icon: '\u2705', url: '/tasks', category: 'إدارة المزرعة', keywords: ['task', 'مهمة', 'عمل'] },
  { id: 'scouting', title: 'Scouting', titleAr: 'الاستكشاف', icon: '\uD83D\uDD0D', url: '/scouting', category: 'إدارة المزرعة', keywords: ['scout', 'استكشاف', 'مراقبة'] },
  { id: 'seeds', title: 'Seeds', titleAr: 'البذور', icon: '\uD83C\uDF3F', url: '/seeds', category: 'إدارة المزرعة', keywords: ['seed', 'بذرة', 'شتلة'] },

  // الري
  { id: 'irrigation', title: 'Irrigation', titleAr: 'الري', icon: '\uD83D\uDCA7', url: '/irrigation', category: 'الري', keywords: ['water', 'ري', 'ماء', 'سقي'] },
  { id: 'pivot-irrigation', title: 'Pivot Irrigation', titleAr: 'الري المحوري', icon: '\uD83D\uDD04', url: '/irrigation/pivot', category: 'الري', keywords: ['pivot', 'محور', 'مركزي'] },

  // ذكاء المحاصيل
  { id: 'crop-health', title: 'Crop Health', titleAr: 'صحة المحاصيل', icon: '\uD83E\uDE7A', url: '/crop-health', category: 'ذكاء المحاصيل', keywords: ['health', 'صحة'] },
  { id: 'diseases', title: 'Diseases', titleAr: 'الأمراض', icon: '\uD83E\uDDA0', url: '/diseases', category: 'ذكاء المحاصيل', keywords: ['disease', 'مرض', 'آفة'] },
  { id: 'weather', title: 'Weather', titleAr: 'الطقس', icon: '\u26C5', url: '/weather', category: 'ذكاء المحاصيل', keywords: ['weather', 'طقس', 'مناخ', 'حرارة'] },
  { id: 'satellite', title: 'Satellite', titleAr: 'الأقمار الصناعية', icon: '\uD83D\uDEF0\uFE0F', url: '/satellite', category: 'ذكاء المحاصيل', keywords: ['satellite', 'ndvi', 'قمر'] },
  { id: 'yield', title: 'Yield', titleAr: 'الإنتاجية', icon: '\uD83D\uDCC8', url: '/yield', category: 'ذكاء المحاصيل', keywords: ['yield', 'إنتاج', 'حصاد'] },
  { id: 'vision', title: 'Vision', titleAr: 'الرؤية الحاسوبية', icon: '\uD83D\uDC41\uFE0F', url: '/vision', category: 'ذكاء المحاصيل', keywords: ['vision', 'camera', 'كاميرا', 'صورة'] },
  { id: 'epidemic', title: 'Epidemic', titleAr: 'الوبائيات', icon: '\u26A0\uFE0F', url: '/epidemic', category: 'ذكاء المحاصيل', keywords: ['epidemic', 'وباء', 'انتشار'] },
  { id: 'crop-protection', title: 'Crop Protection', titleAr: 'حماية المحاصيل', icon: '\uD83D\uDEE1\uFE0F', url: '/crop-protection', category: 'ذكاء المحاصيل', keywords: ['protection', 'حماية', 'مبيد'] },
  { id: 'terrain', title: 'Terrain', titleAr: 'التضاريس', icon: '\u26F0\uFE0F', url: '/terrain', category: 'ذكاء المحاصيل', keywords: ['terrain', 'تضاريس', 'ارتفاع', 'dem'] },
  { id: 'soil-map', title: 'Soil Map', titleAr: 'خريطة التربة', icon: '\uD83D\uDDFA\uFE0F', url: '/soil-map', category: 'ذكاء المحاصيل', keywords: ['soil', 'تربة', 'خريطة'] },

  // إنترنت الأشياء
  { id: 'iot', title: 'IoT', titleAr: 'إنترنت الأشياء', icon: '\uD83D\uDCF6', url: '/iot', category: 'إنترنت الأشياء', keywords: ['iot', 'أجهزة'] },
  { id: 'sensors', title: 'Sensors', titleAr: 'المستشعرات', icon: '\uD83D\uDCDF', url: '/sensors', category: 'إنترنت الأشياء', keywords: ['sensor', 'مستشعر', 'حساس'] },
  { id: 'equipment', title: 'Equipment', titleAr: 'المعدات', icon: '\uD83D\uDE9C', url: '/equipment', category: 'إنترنت الأشياء', keywords: ['equipment', 'معدة', 'جرار', 'آلة'] },
  { id: 'drone', title: 'Drone', titleAr: 'الطائرات بدون طيار', icon: '\uD83D\uDEE9\uFE0F', url: '/drone', category: 'إنترنت الأشياء', keywords: ['drone', 'طائرة', 'درون'] },
  { id: 'edge-devices', title: 'Edge Devices', titleAr: 'أجهزة الحافة', icon: '\uD83D\uDDA5\uFE0F', url: '/edge-devices', category: 'إنترنت الأشياء', keywords: ['edge', 'حافة', 'jetson'] },
  { id: 'virtual-sensors', title: 'Virtual Sensors', titleAr: 'المستشعرات الافتراضية', icon: '\uD83D\uDD2E', url: '/virtual-sensors', category: 'إنترنت الأشياء', keywords: ['virtual', 'افتراضي'] },

  // الأعمال
  { id: 'marketplace', title: 'Marketplace', titleAr: 'السوق', icon: '\uD83D\uDED2', url: '/marketplace', category: 'الأعمال', keywords: ['market', 'سوق', 'بيع', 'شراء'] },
  { id: 'wallet', title: 'Wallet', titleAr: 'المحفظة', icon: '\uD83D\uDCB3', url: '/wallet', category: 'الأعمال', keywords: ['wallet', 'محفظة', 'رصيد', 'دفع'] },
  { id: 'community', title: 'Community', titleAr: 'المجتمع', icon: '\uD83D\uDC65', url: '/community', category: 'الأعمال', keywords: ['community', 'مجتمع', 'تواصل'] },
  { id: 'logistics', title: 'Logistics', titleAr: 'اللوجستيات', icon: '\uD83D\uDE9A', url: '/logistics', category: 'الأعمال', keywords: ['logistics', 'شحن', 'نقل'] },
  { id: 'market-prices', title: 'Market Prices', titleAr: 'أسعار السوق', icon: '\uD83D\uDCB0', url: '/market-prices', category: 'الأعمال', keywords: ['price', 'سعر', 'أسعار'] },
  { id: 'cooperatives', title: 'Cooperatives', titleAr: 'التعاونيات', icon: '\uD83E\uDD1D', url: '/cooperatives', category: 'الأعمال', keywords: ['cooperative', 'تعاونية', 'جمعية'] },
  { id: 'insurance', title: 'Insurance', titleAr: 'التأمين', icon: '\uD83D\uDEE1\uFE0F', url: '/insurance', category: 'الأعمال', keywords: ['insurance', 'تأمين'] },
  { id: 'traceability', title: 'Traceability', titleAr: 'التتبع', icon: '\uD83D\uDD17', url: '/traceability', category: 'الأعمال', keywords: ['trace', 'تتبع', 'سلسلة'] },

  // التقارير
  { id: 'reports', title: 'Reports', titleAr: 'التقارير', icon: '\uD83D\uDCCB', url: '/reports', category: 'التقارير', keywords: ['report', 'تقرير'] },
  { id: 'analytics', title: 'Analytics', titleAr: 'التحليلات', icon: '\uD83D\uDCCA', url: '/analytics', category: 'التقارير', keywords: ['analytics', 'تحليل', 'إحصائيات'] },
  { id: 'documents', title: 'Documents', titleAr: 'المستندات', icon: '\uD83D\uDCC4', url: '/documents', category: 'التقارير', keywords: ['document', 'مستند', 'ملف'] },
  { id: 'audit', title: 'Audit', titleAr: 'التدقيق', icon: '\uD83D\uDD0E', url: '/audit', category: 'التقارير', keywords: ['audit', 'تدقيق', 'سجل'] },

  // أدوات
  { id: 'copilot', title: 'Copilot', titleAr: 'المساعد الذكي', icon: '\uD83E\uDD16', url: '/copilot', category: 'أدوات', keywords: ['copilot', 'ai', 'ذكاء', 'مساعد'] },
  { id: 'support', title: 'Support', titleAr: 'الدعم', icon: '\uD83D\uDCAC', url: '/support', category: 'أدوات', keywords: ['support', 'help', 'دعم', 'مساعدة'] },
  { id: 'settings', title: 'Settings', titleAr: 'الإعدادات', icon: '\u2699\uFE0F', url: '/settings', category: 'أدوات', keywords: ['settings', 'config', 'إعدادات', 'تفضيلات'] },
];

const CATEGORY_ORDER = [
  'نظرة عامة',
  'إدارة المزرعة',
  'الري',
  'ذكاء المحاصيل',
  'إنترنت الأشياء',
  'الأعمال',
  'التقارير',
  'أدوات',
];

// ---------------------------------------------------------------------------
// Fuzzy search helper
// ---------------------------------------------------------------------------

function fuzzyMatch(text: string, query: string): boolean {
  let qi = 0;
  const lowerText = text.toLowerCase();
  const lowerQuery = query.toLowerCase();
  for (let ti = 0; ti < lowerText.length && qi < lowerQuery.length; ti++) {
    if (lowerText[ti] === lowerQuery[qi]) {
      qi++;
    }
  }
  return qi === lowerQuery.length;
}

function searchCommands(query: string): Command[] {
  if (!query.trim()) return COMMANDS;

  const q = query.trim();
  const qLower = q.toLowerCase();

  return COMMANDS.filter((cmd) => {
    // Exact substring match (highest priority)
    if (cmd.title.toLowerCase().includes(qLower)) return true;
    if (cmd.titleAr.includes(q)) return true;
    if (cmd.category.includes(q)) return true;

    // Keyword match
    if (cmd.keywords?.some((kw) => kw.toLowerCase().includes(qLower) || kw.includes(q))) return true;

    // Fuzzy match on title and titleAr
    if (fuzzyMatch(cmd.title, q)) return true;
    if (fuzzyMatch(cmd.titleAr, q)) return true;

    return false;
  });
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Debounce search input (200ms)
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 200);
    return () => clearTimeout(timer);
  }, [query]);

  const results = useMemo(() => searchCommands(debouncedQuery), [debouncedQuery]);

  // Group results by category in stable order
  const grouped = useMemo(() => {
    const map = new Map<string, Command[]>();
    for (const cmd of results) {
      const list = map.get(cmd.category) ?? [];
      list.push(cmd);
      map.set(cmd.category, list);
    }
    const ordered: { category: string; items: Command[] }[] = [];
    for (const cat of CATEGORY_ORDER) {
      const items = map.get(cat);
      if (items && items.length > 0) {
        ordered.push({ category: cat, items });
      }
    }
    return ordered;
  }, [results]);

  // Flat list for keyboard navigation
  const flatResults = useMemo(() => grouped.flatMap((g) => g.items), [grouped]);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setDebouncedQuery('');
      setSelectedIndex(0);
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

  // Reset selected index when results change
  useEffect(() => {
    setSelectedIndex(0);
  }, [debouncedQuery]);

  // Navigate to selected command
  const navigateTo = useCallback(
    (cmd: Command) => {
      onClose();
      router.push(cmd.url);
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

  // Close on Ctrl+K / Cmd+K while open
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

  // Build running flat index for mapping group items
  let flatIndex = 0;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
      role="dialog"
      aria-modal="true"
      aria-label="لوحة الأوامر"
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
        className="relative w-full max-w-2xl mx-4 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden"
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
            placeholder="ابحث عن أمر أو صفحة..."
            className="flex-1 bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 text-base outline-none"
            aria-label="ابحث عن أمر أو صفحة"
          />
          <kbd className="hidden sm:inline-flex px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-[10px] font-mono text-gray-400 dark:text-gray-500">
            Esc
          </kbd>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-md sm:hidden"
            aria-label="إغلاق"
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
              لا توجد نتائج مطابقة
            </div>
          ) : (
            grouped.map((group) => {
              const groupItems = group.items.map((cmd) => {
                const idx = flatIndex++;
                const isActive = idx === selectedIndex;
                return (
                  <button
                    key={cmd.id}
                    type="button"
                    role="option"
                    aria-selected={isActive}
                    data-active={isActive}
                    onClick={() => navigateTo(cmd)}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm cursor-pointer transition-colors ${
                      isActive
                        ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                    }`}
                  >
                    <span className="text-lg leading-none shrink-0" aria-hidden="true">
                      {cmd.icon}
                    </span>
                    <span className="flex-1 text-right truncate">
                      <span className="font-medium">{cmd.titleAr}</span>
                      <span className="text-gray-400 dark:text-gray-500 mr-2 text-xs">
                        {cmd.title}
                      </span>
                    </span>
                    {isActive && (
                      <CornerDownLeft className="w-3.5 h-3.5 text-gray-400 shrink-0" aria-hidden="true" />
                    )}
                  </button>
                );
              });

              return (
                <div key={group.category}>
                  <div className="px-4 pt-3 pb-1 text-xs font-semibold text-gray-400 dark:text-gray-500 tracking-wider">
                    {group.category}
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
              Ctrl+K
            </kbd>{' '}
            بحث سريع
          </span>
        </div>
      </div>
    </div>
  );
}
