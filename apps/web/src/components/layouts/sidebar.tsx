'use client';
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import {
  LayoutDashboard,
  Grid3x3,
  TrendingUp,
  Settings,
  Cloud,
  Signal,
  Sprout,
  Wrench,
  Users,
  ListTodo,
  Wallet,
  DollarSign,
} from 'lucide-react';

interface NavItem {
  nameAr: string;
  name: string;
  href: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  icon: any;
}

const navItems: NavItem[] = [
  {
    nameAr: 'لوحة التحكم',
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    nameAr: 'الحقول',
    name: 'Fields',
    href: '/fields',
    icon: Grid3x3,
  },
  {
    nameAr: 'التحليلات',
    name: 'Analytics',
    href: '/analytics',
    icon: TrendingUp,
  },
  {
    nameAr: 'السوق',
    name: 'Marketplace',
    href: '/marketplace',
    icon: DollarSign,
  },
  {
    nameAr: 'المهام',
    name: 'Tasks',
    href: '/tasks',
    icon: ListTodo,
  },
  {
    nameAr: 'الطقس',
    name: 'Weather',
    href: '/weather',
    icon: Cloud,
  },
  {
    nameAr: 'إنترنت الأشياء',
    name: 'IoT',
    href: '/iot',
    icon: Signal,
  },
  {
    nameAr: 'صحة المحاصيل',
    name: 'Crop Health',
    href: '/crop-health',
    icon: Sprout,
  },
  {
    nameAr: 'المعدات',
    name: 'Equipment',
    href: '/equipment',
    icon: Wrench,
  },
  {
    nameAr: 'المجتمع',
    name: 'Community',
    href: '/community',
    icon: Users,
  },
  {
    nameAr: 'المحفظة',
    name: 'Wallet',
    href: '/wallet',
    icon: Wallet,
  },
  {
    nameAr: 'الإعدادات',
    name: 'Settings',
    href: '/settings',
    icon: Settings,
  },
];

export const Sidebar = React.memo(function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-white border-e border-gray-200 flex flex-col h-full" role="navigation" aria-label="القائمة الجانبية الرئيسية" data-testid="sidebar">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <Link href="/dashboard" className="flex items-center gap-3" data-testid="sidebar-logo">
          <div className="w-10 h-10 bg-sahool-green-600 rounded-lg flex items-center justify-center">
            <div className="w-6 h-6 bg-white rounded-full" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">سهول</h1>
            <p className="text-xs text-gray-500">SAHOOL Platform</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;
            // Generate test ID from href (e.g., "/dashboard" -> "nav-link-dashboard")
            const testId = `nav-link-${item.href.split('/').filter(Boolean).join('-')}`;

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
                  aria-label={`${item.nameAr} - ${item.name}`}
                  data-testid={testId}
                >
                  <Icon
                    className={clsx(
                      'w-5 h-5 flex-shrink-0',
                      isActive ? 'text-sahool-green-600' : 'text-gray-400 group-hover:text-sahool-green-600'
                    )}
                    aria-hidden="true"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium">{item.nameAr}</div>
                    <div className="text-xs opacity-70">{item.name}</div>
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
          <div className="font-medium">الإصدار 17.0.0</div>
          <div>Version 17.0.0</div>
        </div>
      </div>
    </aside>
  );
});
