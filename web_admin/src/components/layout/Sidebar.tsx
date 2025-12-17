'use client';

// Admin Sidebar Navigation
// شريط التنقل الجانبي

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
} from 'lucide-react';

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

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 right-0 w-64 bg-white border-l border-gray-200 flex flex-col z-50">
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-gray-100">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl sahool-gradient flex items-center justify-center">
            <Leaf className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">سهول</h1>
            <p className="text-xs text-gray-500">لوحة التحكم</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all',
                isActive
                  ? 'bg-sahool-50 text-sahool-700 border-r-4 border-sahool-600'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <item.icon className={cn('w-5 h-5', isActive ? 'text-sahool-600' : 'text-gray-400')} />
              {item.name}
              {'badge' in item && item.badge && item.badge > 0 && (
                <span className="mr-auto bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="p-4 border-t border-gray-100">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-full bg-sahool-100 flex items-center justify-center">
            <span className="text-sahool-700 font-bold">م</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">مدير النظام</p>
            <p className="text-xs text-gray-500 truncate">admin@sahool.io</p>
          </div>
        </div>
        <button className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors">
          <LogOut className="w-4 h-4" />
          تسجيل الخروج
        </button>
      </div>
    </aside>
  );
}
