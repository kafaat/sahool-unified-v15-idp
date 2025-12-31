'use client';
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { clsx } from 'clsx';
import {
  LayoutDashboard,
  Users,
  Sprout,
  FileText,
  TrendingUp,
  Settings,
  Building2,
  Package,
  Calendar,
  FileBarChart,
} from 'lucide-react';

interface NavItem {
  labelKey: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItem[] = [
  {
    labelKey: 'dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    labelKey: 'users',
    href: '/dashboard/users',
    icon: Users,
  },
  {
    labelKey: 'farms',
    href: '/dashboard/farms',
    icon: Building2,
  },
  {
    labelKey: 'crops',
    href: '/dashboard/crops',
    icon: Sprout,
  },
  {
    labelKey: 'inventory',
    href: '/dashboard/inventory',
    icon: Package,
  },
  {
    labelKey: 'seasons',
    href: '/dashboard/seasons',
    icon: Calendar,
  },
  {
    labelKey: 'reports',
    href: '/dashboard/reports',
    icon: FileBarChart,
  },
  {
    labelKey: 'documents',
    href: '/dashboard/documents',
    icon: FileText,
  },
  {
    labelKey: 'analytics',
    href: '/dashboard/analytics',
    icon: TrendingUp,
  },
  {
    labelKey: 'settings',
    href: '/dashboard/settings',
    icon: Settings,
  },
];

export const Sidebar = React.memo(function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations('nav');
  const tCommon = useTranslations('common');

  return (
    <aside className="w-64 bg-white border-e border-gray-200 flex flex-col h-full" role="navigation" aria-label={t('mainNav')}>
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-sahool-green-600 rounded-lg flex items-center justify-center">
            <div className="w-6 h-6 bg-white rounded-full" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">{tCommon('appName')}</h1>
            <p className="text-xs text-gray-500">{tCommon('tagline')}</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={clsx(
                    'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                    'hover:bg-sahool-green-50 group focus:outline-none focus:ring-2 focus:ring-sahool-green-500',
                    isActive
                      ? 'bg-sahool-green-100 text-sahool-green-700 font-medium'
                      : 'text-gray-700'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                  aria-label={t(item.labelKey)}
                >
                  <Icon
                    className={clsx(
                      'w-5 h-5 flex-shrink-0',
                      isActive ? 'text-sahool-green-600' : 'text-gray-400 group-hover:text-sahool-green-600'
                    )}
                    aria-hidden="true"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium">{t(item.labelKey)}</div>
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          <div className="font-medium">{t('version')} 17.0.0</div>
        </div>
      </div>
    </aside>
  );
});
