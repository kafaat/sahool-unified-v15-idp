// @ts-nocheck - Temporary fix for lucide-react types with React 19
'use client';

// Modern Glassmorphism Sidebar
// الشريط الجانبي الحديث بتأثير الزجاج

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  MapPin,
  Bug,
  Thermometer,
  Settings,
  Bell,
  LogOut,
  Leaf,
  MessageCircle,
  TrendingUp,
  Activity,
  Cpu,
  Droplets,
  Sprout,
  FileText,
  DollarSign,
  Satellite,
  ChevronDown,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { useState } from 'react';

const navigation = [
  { name: 'لوحة التحكم', href: '/dashboard', icon: LayoutDashboard },
  { name: 'المزارع', href: '/farms', icon: MapPin },
  { name: 'مركز رصد الأوبئة', href: '/epidemic', icon: Activity },
  { name: 'إدارة الأمراض', href: '/diseases', icon: Bug },
  { name: 'حاسبة الإنتاجية', href: '/yield', icon: TrendingUp },
  { name: 'الري الذكي', href: '/irrigation', icon: Droplets },
  { name: 'المستشعرات', href: '/sensors', icon: Cpu },
  { name: 'الطقس والتنبيهات', href: '/alerts', icon: Bell },
  { name: 'الدعم الفني', href: '/support', icon: MessageCircle, badge: 5 },
  { name: 'الإعدادات', href: '/settings', icon: Settings },
];

const precisionAgricultureNav = [
  { name: 'التطبيق المتغير (VRA)', href: '/precision-agriculture/vra', icon: FileText },
  { name: 'درجات النمو (GDD)', href: '/precision-agriculture/gdd', icon: Thermometer },
  { name: 'إدارة الرش', href: '/precision-agriculture/spray', icon: Droplets },
];

const analyticsNav = [
  { name: 'تحليل الربحية', href: '/analytics/profitability', icon: DollarSign },
  { name: 'تحليلات الأقمار', href: '/analytics/satellite', icon: Satellite },
];

export default function ModernSidebar() {
  const pathname = usePathname();
  const [precisionExpanded, setPrecisionExpanded] = useState(
    pathname?.startsWith('/precision-agriculture')
  );
  const [analyticsExpanded, setAnalyticsExpanded] = useState(
    pathname?.startsWith('/analytics')
  );

  return (
    <aside className="fixed inset-y-0 right-0 w-64 glass-sidebar flex flex-col z-50 animate-slide-in-right">
      {/* Decorative gradient overlay */}
      <div className="absolute inset-0 gradient-mesh opacity-50 pointer-events-none" />

      {/* Logo Section */}
      <div className="relative h-20 flex items-center justify-center border-b border-gray-200/50 dark:border-gray-700/50">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="relative">
            {/* Glow effect */}
            <div className="absolute inset-0 gradient-sahool rounded-2xl blur-lg opacity-0 group-hover:opacity-70 transition-opacity duration-500" />

            {/* Logo container */}
            <div className="relative w-12 h-12 rounded-2xl gradient-sahool flex items-center justify-center shadow-lg transform group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
              <Leaf className="w-7 h-7 text-white drop-shadow-lg" />
            </div>
          </div>

          <div className="text-right">
            <h1 className="text-2xl font-bold gradient-text">سهول</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              لوحة التحكم
            </p>
          </div>
        </Link>
      </div>

      {/* Navigation Section */}
      <nav className="relative flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navigation.map((item, index) => {
          const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium',
                'transition-all duration-300 group relative overflow-hidden',
                'animate-fade-in',
                isActive
                  ? 'glass-strong text-sahool-700 dark:text-sahool-400 shadow-lg scale-105'
                  : 'text-gray-600 dark:text-gray-300 hover:glass hover:text-gray-900 dark:hover:text-white'
              )}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Active indicator */}
              {isActive && (
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-8 gradient-sahool rounded-l-full animate-scale-in" />
              )}

              {/* Icon with gradient background on hover */}
              <div className={cn(
                'p-2 rounded-lg transition-all duration-300',
                isActive
                  ? 'gradient-sahool shadow-md'
                  : 'bg-gray-100/50 dark:bg-gray-800/50 group-hover:gradient-sahool'
              )}>
                <item.icon className={cn(
                  'w-5 h-5 transition-colors',
                  isActive
                    ? 'text-white'
                    : 'text-gray-400 group-hover:text-white'
                )} />
              </div>

              {/* Label */}
              <span className="flex-1">{item.name}</span>

              {/* Badge */}
              {'badge' in item && item.badge && item.badge > 0 && (
                <span className={cn(
                  "px-2 py-0.5 rounded-full text-xs font-bold",
                  "bg-gradient-to-r from-yellow-400 to-orange-500 text-white",
                  "shadow-lg animate-pulse"
                )}>
                  {item.badge}
                </span>
              )}

              {/* Hover effect overlay */}
              <div className="absolute inset-0 bg-gradient-to-r from-sahool-500/0 via-sahool-500/10 to-sahool-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl" />
            </Link>
          );
        })}

        {/* Precision Agriculture Section */}
        <div className="pt-2 animate-fade-in" style={{ animationDelay: '500ms' }}>
          <button
            onClick={() => setPrecisionExpanded(!precisionExpanded)}
            className={cn(
              'w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium',
              'transition-all duration-300 group relative',
              pathname?.startsWith('/precision-agriculture')
                ? 'glass-strong text-sahool-700 dark:text-sahool-400 shadow-lg'
                : 'text-gray-600 dark:text-gray-300 hover:glass hover:text-gray-900 dark:hover:text-white'
            )}
          >
            <div className={cn(
              'p-2 rounded-lg transition-all duration-300',
              pathname?.startsWith('/precision-agriculture')
                ? 'gradient-sahool shadow-md'
                : 'bg-gray-100/50 dark:bg-gray-800/50 group-hover:gradient-sahool'
            )}>
              <Sprout className={cn(
                'w-5 h-5 transition-colors',
                pathname?.startsWith('/precision-agriculture')
                  ? 'text-white'
                  : 'text-gray-400 group-hover:text-white'
              )} />
            </div>

            <span className="flex-1">الزراعة الدقيقة</span>

            <div className={cn(
              "transition-transform duration-300",
              precisionExpanded && "rotate-180"
            )}>
              <ChevronDown className="w-4 h-4" />
            </div>
          </button>

          {/* Submenu with animation */}
          <div className={cn(
            "overflow-hidden transition-all duration-300",
            precisionExpanded ? "max-h-48 opacity-100 mt-1" : "max-h-0 opacity-0"
          )}>
            <div className="mr-4 space-y-1">
              {precisionAgricultureNav.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm',
                      'transition-all duration-300 group',
                      isActive
                        ? 'glass text-sahool-700 dark:text-sahool-400 font-semibold shadow-md'
                        : 'text-gray-600 dark:text-gray-400 hover:glass hover:text-gray-900 dark:hover:text-white'
                    )}
                  >
                    <item.icon className={cn(
                      'w-4 h-4 transition-colors',
                      isActive
                        ? 'text-sahool-600 dark:text-sahool-400'
                        : 'text-gray-400 group-hover:text-sahool-600'
                    )} />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>

        {/* Analytics Section */}
        <div className="pt-2 animate-fade-in" style={{ animationDelay: '550ms' }}>
          <button
            onClick={() => setAnalyticsExpanded(!analyticsExpanded)}
            className={cn(
              'w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium',
              'transition-all duration-300 group relative',
              pathname?.startsWith('/analytics')
                ? 'glass-strong text-sahool-700 dark:text-sahool-400 shadow-lg'
                : 'text-gray-600 dark:text-gray-300 hover:glass hover:text-gray-900 dark:hover:text-white'
            )}
          >
            <div className={cn(
              'p-2 rounded-lg transition-all duration-300',
              pathname?.startsWith('/analytics')
                ? 'gradient-sahool shadow-md'
                : 'bg-gray-100/50 dark:bg-gray-800/50 group-hover:gradient-sahool'
            )}>
              <TrendingUp className={cn(
                'w-5 h-5 transition-colors',
                pathname?.startsWith('/analytics')
                  ? 'text-white'
                  : 'text-gray-400 group-hover:text-white'
              )} />
            </div>

            <span className="flex-1">التحليلات</span>

            <div className={cn(
              "transition-transform duration-300",
              analyticsExpanded && "rotate-180"
            )}>
              <ChevronDown className="w-4 h-4" />
            </div>
          </button>

          {/* Submenu with animation */}
          <div className={cn(
            "overflow-hidden transition-all duration-300",
            analyticsExpanded ? "max-h-48 opacity-100 mt-1" : "max-h-0 opacity-0"
          )}>
            <div className="mr-4 space-y-1">
              {analyticsNav.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm',
                      'transition-all duration-300 group',
                      isActive
                        ? 'glass text-sahool-700 dark:text-sahool-400 font-semibold shadow-md'
                        : 'text-gray-600 dark:text-gray-400 hover:glass hover:text-gray-900 dark:hover:text-white'
                    )}
                  >
                    <item.icon className={cn(
                      'w-4 h-4 transition-colors',
                      isActive
                        ? 'text-sahool-600 dark:text-sahool-400'
                        : 'text-gray-400 group-hover:text-sahool-600'
                    )} />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </nav>

      {/* User Section */}
      <div className="relative p-4 border-t border-gray-200/50 dark:border-gray-700/50">
        <div className="glass rounded-xl p-3 mb-3 hover:glass-strong transition-all duration-300">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-11 h-11 rounded-xl gradient-sahool flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">م</span>
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-green-500 border-2 border-white dark:border-gray-800 rounded-full animate-pulse" />
            </div>

            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                مدير النظام
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                admin@sahool.io
              </p>
            </div>
          </div>
        </div>

        <button className={cn(
          "w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium",
          "rounded-xl transition-all duration-300 group",
          "text-red-600 dark:text-red-400",
          "hover:glass-strong hover:text-red-700 dark:hover:text-red-300",
          "hover:shadow-lg"
        )}>
          <LogOut className="w-4 h-4 group-hover:rotate-12 transition-transform duration-300" />
          تسجيل الخروج
        </button>
      </div>
    </aside>
  );
}
