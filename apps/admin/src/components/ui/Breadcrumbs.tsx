'use client';

/**
 * Breadcrumbs Component
 * مسار التنقل
 */

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { ChevronLeft, Home } from 'lucide-react';
import { useMemo } from 'react';

export interface BreadcrumbItem {
  label: string;
  labelAr?: string;
  href?: string;
  icon?: React.ElementType;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  showHome?: boolean;
  homeLabel?: string;
  homeLabelAr?: string;
  separator?: React.ReactNode;
  className?: string;
  maxItems?: number;
}

// Default route labels (Arabic)
const routeLabels: Record<string, { ar: string; en: string }> = {
  dashboard: { ar: 'لوحة التحكم', en: 'Dashboard' },
  farms: { ar: 'المزارع', en: 'Farms' },
  fields: { ar: 'الحقول', en: 'Fields' },
  diseases: { ar: 'الأمراض', en: 'Diseases' },
  epidemic: { ar: 'مركز الأوبئة', en: 'Epidemic Center' },
  yield: { ar: 'الإنتاجية', en: 'Yield' },
  irrigation: { ar: 'الري', en: 'Irrigation' },
  sensors: { ar: 'المستشعرات', en: 'Sensors' },
  alerts: { ar: 'التنبيهات', en: 'Alerts' },
  support: { ar: 'الدعم', en: 'Support' },
  settings: { ar: 'الإعدادات', en: 'Settings' },
  security: { ar: 'الأمان', en: 'Security' },
  users: { ar: 'المستخدمين', en: 'Users' },
  analytics: { ar: 'التحليلات', en: 'Analytics' },
  profitability: { ar: 'الربحية', en: 'Profitability' },
  satellite: { ar: 'الأقمار الصناعية', en: 'Satellite' },
  'precision-agriculture': { ar: 'الزراعة الدقيقة', en: 'Precision Agriculture' },
  vra: { ar: 'التطبيق المتغير', en: 'VRA' },
  gdd: { ar: 'درجات النمو', en: 'GDD' },
  spray: { ar: 'الرش', en: 'Spray' },
  pivot: { ar: 'الري المحوري', en: 'Pivot' },
  'crop-health': { ar: 'صحة المحصول', en: 'Crop Health' },
  inventory: { ar: 'المخزون', en: 'Inventory' },
  logistics: { ar: 'اللوجستيات', en: 'Logistics' },
  marketplace: { ar: 'السوق', en: 'Marketplace' },
  community: { ar: 'المجتمع', en: 'Community' },
  research: { ar: 'البحوث', en: 'Research' },
  compliance: { ar: 'الامتثال', en: 'Compliance' },
  disasters: { ar: 'الكوارث', en: 'Disasters' },
  lab: { ar: 'المختبر', en: 'Lab' },
};

export default function Breadcrumbs({
  items,
  showHome = true,
  homeLabel = 'Home',
  homeLabelAr = 'الرئيسية',
  separator,
  className = '',
  maxItems = 5,
}: BreadcrumbsProps) {
  const pathname = usePathname();

  // Generate breadcrumbs from pathname if items not provided
  const breadcrumbItems = useMemo((): BreadcrumbItem[] => {
    if (items) return items;

    const pathSegments = pathname?.split('/').filter(Boolean) || [];
    const generatedItems: BreadcrumbItem[] = [];

    pathSegments.forEach((segment, index) => {
      // Skip numeric IDs in breadcrumbs
      if (/^\d+$/.test(segment) || /^[a-f0-9-]{36}$/.test(segment)) {
        return;
      }

      const href = '/' + pathSegments.slice(0, index + 1).join('/');
      const labels = routeLabels[segment];

      generatedItems.push({
        label: labels?.en || segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' '),
        labelAr: labels?.ar,
        href: index === pathSegments.length - 1 ? undefined : href,
      });
    });

    return generatedItems;
  }, [items, pathname]);

  // Add home item
  const allItems: BreadcrumbItem[] = useMemo(() => {
    const homeItem: BreadcrumbItem = {
      label: homeLabel,
      labelAr: homeLabelAr,
      href: '/dashboard',
      icon: Home,
    };

    const finalItems = showHome ? [homeItem, ...breadcrumbItems] : breadcrumbItems;

    // Collapse middle items if too many
    if (finalItems.length > maxItems) {
      const start = finalItems.slice(0, 1);
      const end = finalItems.slice(-(maxItems - 2));
      return [...start, { label: '...', labelAr: '...' }, ...end];
    }

    return finalItems;
  }, [showHome, homeLabel, homeLabelAr, breadcrumbItems, maxItems]);

  if (allItems.length <= 1) {
    return null;
  }

  const defaultSeparator = (
    <ChevronLeft className="w-4 h-4 text-gray-400 dark:text-gray-500 flex-shrink-0" />
  );

  return (
    <nav aria-label="مسار التنقل" className={cn('flex items-center', className)}>
      <ol className="flex items-center flex-wrap gap-1">
        {allItems.map((item, index) => {
          const isLast = index === allItems.length - 1;
          const isEllipsis = item.label === '...';
          const Icon = item.icon;

          return (
            <li key={index} className="flex items-center">
              {index > 0 && <span className="mx-2">{separator || defaultSeparator}</span>}

              {isEllipsis ? (
                <span className="text-sm text-gray-400 dark:text-gray-500 px-1">
                  {item.labelAr || item.label}
                </span>
              ) : item.href && !isLast ? (
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center gap-1.5 text-sm transition-colors',
                    'text-gray-500 dark:text-gray-400 hover:text-sahool-600 dark:hover:text-sahool-400'
                  )}
                >
                  {Icon && <Icon className="w-4 h-4" />}
                  <span>{item.labelAr || item.label}</span>
                </Link>
              ) : (
                <span
                  className={cn(
                    'flex items-center gap-1.5 text-sm',
                    isLast
                      ? 'text-gray-900 dark:text-gray-100 font-medium'
                      : 'text-gray-500 dark:text-gray-400'
                  )}
                  aria-current={isLast ? 'page' : undefined}
                >
                  {Icon && <Icon className="w-4 h-4" />}
                  <span>{item.labelAr || item.label}</span>
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

// Compact breadcrumbs for mobile
export function BreadcrumbsCompact({ className = '' }: { className?: string }) {
  const pathname = usePathname();

  const parentItem = useMemo(() => {
    const segments = pathname?.split('/').filter(Boolean) || [];
    if (segments.length <= 1) return null;

    const parentSegment = segments[segments.length - 2];
    if (!parentSegment) return null;

    const labels = routeLabels[parentSegment];

    return {
      href: '/' + segments.slice(0, -1).join('/'),
      label: labels?.ar || parentSegment,
    };
  }, [pathname]);

  if (!parentItem) return null;

  return (
    <Link
      href={parentItem.href}
      className={cn(
        'inline-flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400 hover:text-sahool-600 dark:hover:text-sahool-400 transition-colors',
        className
      )}
    >
      <ChevronLeft className="w-4 h-4 rotate-180" />
      <span>{parentItem.label}</span>
    </Link>
  );
}
