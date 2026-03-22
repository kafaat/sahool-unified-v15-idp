"use client";

/**
 * Admin Sidebar Navigation - Enhanced with CRUD Management
 * شريط التنقل الجانبي المحسن مع إدارة CRUD
 *
 * Optimized:
 * - Wrapped in React.memo to avoid re-renders from parent layout changes
 * - Mobile overlay/close button dynamically imported (hidden on desktop)
 * - Icons individually imported from lucide-react (tree-shakeable)
 */

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
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
  CircleDot,
  Menu,
  Users,
  Package,
  CheckSquare,
  Wrench,
  ShoppingCart,
  FlaskConical,
  // Admin-only feature icons
  Shield,
  Target,
  ClipboardList,
  Eye,
  Plane,
  Mountain,
  Radio,
  Search,
  Bot,
  FileCode2,
  CalendarDays,
  CloudSun,
  FileBarChart,
  BarChart3,
  ScanLine,
  TestTubes,
  ArrowLeftRight,
  // P2/P3 feature icons
  Truck,
  Handshake,
  Coins,
  ShieldCheck,
  Layers,
  Wheat,
} from "lucide-react";
import { useAuth } from "@/stores/auth.store";
import dynamic from "next/dynamic";

// Lazy-load mobile drawer overlay -- only needed on small screens after user interaction
const MobileSidebarDrawer = dynamic(
  () => import("@/components/layout/MobileSidebarDrawer"),
  { ssr: false },
);

// Lazy-load mobile close button from the same module
const MobileSidebarCloseButtonLazy = dynamic(
  () =>
    import("@/components/layout/MobileSidebarDrawer").then((mod) => ({
      default: mod.MobileSidebarCloseButton,
    })),
  { ssr: false },
);

// Main navigation sections
const mainNavigation = [
  { name: "لوحة التحكم", href: "/dashboard", icon: LayoutDashboard },
];

// Operations section
const operationsNav = [
  { name: "المزارع", href: "/farms", icon: MapPin },
  { name: "المواسم الزراعية", href: "/seasons", icon: CalendarDays },
  { name: "إدارة الأمراض", href: "/diseases", icon: Bug },
  { name: "الري الذكي", href: "/irrigation", icon: Droplets },
  { name: "المهام", href: "/tasks", icon: CheckSquare },
];

// Monitoring section
const monitoringNav = [
  { name: "المستشعرات", href: "/sensors", icon: Cpu },
  { name: "التنبيهات", href: "/alerts", icon: Bell },
  { name: "الطقس والمناخ", href: "/weather", icon: CloudSun },
  { name: "مركز رصد الأوبئة", href: "/epidemic", icon: Activity },
  { name: "حاسبة الإنتاجية", href: "/yield", icon: TrendingUp },
];

// Management section
const managementNav = [
  { name: "المستخدمون", href: "/users", icon: Users },
  { name: "المعدات", href: "/equipment", icon: Wrench },
  { name: "تتبع الأسطول", href: "/equipment/fleet-tracking", icon: Truck },
  { name: "التعاونيات", href: "/cooperatives", icon: Handshake },
  { name: "المخزون", href: "/inventory", icon: Package },
  { name: "السوق", href: "/marketplace", icon: ShoppingCart },
  { name: "أسعار السوق", href: "/market-prices", icon: Coins },
  { name: "التأمين الزراعي", href: "/insurance", icon: ShieldCheck },
  { name: "البذور والأصناف", href: "/seeds", icon: Wheat },
  { name: "خريطة التربة", href: "/soil-map", icon: Layers },
  { name: "البحوث", href: "/research", icon: FlaskConical },
  { name: "الامتثال", href: "/compliance", icon: Shield },
  { name: "التتبع والتوثيق", href: "/traceability", icon: ScanLine },
];

// AI & Technology section (admin-only features)
const aiTechNav = [
  { name: "المساعد الذكي", href: "/copilot", icon: Bot },
  { name: "مراجعات الكود", href: "/code-review", icon: FileCode2 },
  { name: "الرؤية الحاسوبية", href: "/vision", icon: Eye },
  { name: "الطائرات المسيّرة", href: "/drone", icon: Plane },
  { name: "أجهزة الحافة", href: "/edge-devices", icon: Radio },
  { name: "تحليل التضاريس", href: "/terrain", icon: Mountain },
  { name: "المستشعرات الافتراضية", href: "/virtual-sensors", icon: Cpu },
  { name: "الاستكشاف الميداني", href: "/scouting", icon: Search },
];

// Audit & Compliance section
const auditNav = [
  { name: "سجل التدقيق", href: "/audit", icon: ClipboardList },
];

// System section
const systemNav = [
  { name: "الدعم الفني", href: "/support", icon: MessageCircle, badge: 5 },
  { name: "الإعدادات", href: "/settings", icon: Settings },
];

const precisionAgricultureNav = [
  {
    name: "التطبيق المتغير (VRA)",
    href: "/precision-agriculture/vra",
    icon: FileText,
  },
  {
    name: "درجات النمو (GDD)",
    href: "/precision-agriculture/gdd",
    icon: Thermometer,
  },
  { name: "إدارة الرش", href: "/precision-agriculture/spray", icon: Droplets },
  { name: "الري المحوري", href: "/precision-agriculture/pivot", icon: CircleDot },
  { name: "وصفات التسميد", href: "/precision-agriculture/fertilizer", icon: FlaskConical },
];

const analyticsNav = [
  { name: "تحليل الربحية", href: "/analytics/profitability", icon: DollarSign },
  { name: "تحليل الغلة العميق", href: "/analytics/yield", icon: BarChart3 },
  { name: "تحليلات الأقمار", href: "/analytics/satellite", icon: Satellite },
  { name: "التقرير الموسمي", href: "/reports/seasonal", icon: FileBarChart },
  { name: "تحليل التربة", href: "/analytics/soil", icon: TestTubes },
  { name: "مقارنة الحقول", href: "/analytics/field-compare", icon: ArrowLeftRight },
  { name: "تنبؤ الإنتاجية", href: "/analytics/yield-forecasting", icon: TrendingUp },
  { name: "تحليل الفجوات", href: "/analytics/gap-analysis", icon: Target },
];

export default React.memo(function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [precisionExpanded, setPrecisionExpanded] = useState(
    pathname?.startsWith("/precision-agriculture"),
  );
  const [analyticsExpanded, setAnalyticsExpanded] = useState(
    pathname?.startsWith("/analytics") || pathname?.startsWith("/reports"),
  );
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [pathname]);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isMobileMenuOpen]);

  return (
    <>
      {/* Mobile menu button */}
      <button
        type="button"
        onClick={() => setIsMobileMenuOpen(true)}
        className="fixed top-4 right-4 z-40 p-2 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 lg:hidden"
        aria-label="فتح القائمة"
      >
        <Menu className="w-6 h-6 text-gray-600 dark:text-gray-300" />
      </button>

      {/* Mobile overlay - lazy loaded, only rendered when menu is open */}
      {isMobileMenuOpen && (
        <Suspense fallback={null}>
          <MobileSidebarDrawer onClose={() => setIsMobileMenuOpen(false)} />
        </Suspense>
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 right-0 w-64 bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 flex flex-col z-50 transition-transform duration-300",
          isMobileMenuOpen ? "translate-x-0" : "translate-x-full lg:translate-x-0"
        )}
      >
        {/* Mobile close button - lazy loaded */}
        {isMobileMenuOpen && (
          <Suspense fallback={null}>
            <MobileSidebarCloseButtonLazy onClose={() => setIsMobileMenuOpen(false)} />
          </Suspense>
        )}

        {/* Logo */}
        <div className="h-16 flex items-center justify-center border-b border-gray-100 dark:border-gray-800">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl sahool-gradient flex items-center justify-center">
              <Leaf className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">سهول</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">لوحة التحكم</p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav
          className="flex-1 py-4 px-3 space-y-6 overflow-y-auto"
          aria-label="التنقل الرئيسي"
        >
          {/* Main Section */}
          <div>
            {mainNavigation.map((item) => {
              const isActive =
                pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  aria-current={isActive ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all",
                    isActive
                      ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 border-r-4 border-sahool-600"
                      : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100",
                  )}
                >
                  <item.icon
                    className={cn(
                      "w-5 h-5",
                      isActive ? "text-sahool-600 dark:text-sahool-400" : "text-gray-400 dark:text-gray-500",
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* Operations Section */}
          <div>
            <div className="px-4 mb-2">
              <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                العمليات
              </h3>
            </div>
            {operationsNav.map((item) => {
              const isActive =
                pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  aria-current={isActive ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all",
                    isActive
                      ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 border-r-4 border-sahool-600"
                      : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100",
                  )}
                >
                  <item.icon
                    className={cn(
                      "w-4 h-4",
                      isActive ? "text-sahool-600 dark:text-sahool-400" : "text-gray-400 dark:text-gray-500",
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* Monitoring Section */}
          <div>
            <div className="px-4 mb-2">
              <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                المراقبة
              </h3>
            </div>
            {monitoringNav.map((item) => {
              const isActive =
                pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  aria-current={isActive ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all",
                    isActive
                      ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 border-r-4 border-sahool-600"
                      : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100",
                  )}
                >
                  <item.icon
                    className={cn(
                      "w-4 h-4",
                      isActive ? "text-sahool-600 dark:text-sahool-400" : "text-gray-400 dark:text-gray-500",
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* Management Section */}
          <div>
            <div className="px-4 mb-2">
              <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                الإدارة
              </h3>
            </div>
            {managementNav.map((item) => {
              const isActive =
                pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  aria-current={isActive ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all",
                    isActive
                      ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 border-r-4 border-sahool-600"
                      : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100",
                  )}
                >
                  <item.icon
                    className={cn(
                      "w-4 h-4",
                      isActive ? "text-sahool-600 dark:text-sahool-400" : "text-gray-400 dark:text-gray-500",
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* AI & Technology Section (Admin-Only) */}
          <div>
            <div className="px-4 mb-2">
              <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                الذكاء الاصطناعي والتقنية
              </h3>
            </div>
            {aiTechNav.map((item) => {
              const isActive =
                pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  aria-current={isActive ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all",
                    isActive
                      ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 border-r-4 border-sahool-600"
                      : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100",
                  )}
                >
                  <item.icon
                    className={cn(
                      "w-4 h-4",
                      isActive ? "text-sahool-600 dark:text-sahool-400" : "text-gray-400 dark:text-gray-500",
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* Audit Section */}
          <div>
            <div className="px-4 mb-2">
              <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                التدقيق
              </h3>
            </div>
            {auditNav.map((item) => {
              const isActive =
                pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  aria-current={isActive ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all",
                    isActive
                      ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 border-r-4 border-sahool-600"
                      : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100",
                  )}
                >
                  <item.icon
                    className={cn(
                      "w-4 h-4",
                      isActive ? "text-sahool-600 dark:text-sahool-400" : "text-gray-400 dark:text-gray-500",
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* System Section */}
          <div>
            <div className="px-4 mb-2">
              <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                النظام
              </h3>
            </div>
            {systemNav.map((item) => {
              const isActive =
                pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  aria-current={isActive ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all",
                    isActive
                      ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 border-r-4 border-sahool-600"
                      : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100",
                  )}
                >
                  <item.icon
                    className={cn(
                      "w-4 h-4",
                      isActive ? "text-sahool-600 dark:text-sahool-400" : "text-gray-400 dark:text-gray-500",
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                  {"badge" in item && item.badge && item.badge > 0 && (
                    <span
                      className="mr-auto bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 text-xs px-2 py-0.5 rounded-full"
                      aria-label={`${item.badge} جديد`}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>

          {/* Precision Agriculture Section */}
          <div className="pt-2">
            <button
              type="button"
              onClick={() => setPrecisionExpanded(!precisionExpanded)}
              aria-expanded={precisionExpanded}
              aria-controls="precision-agriculture-menu"
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all",
                pathname?.startsWith("/precision-agriculture")
                  ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300"
                  : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100",
              )}
            >
              <Sprout
                className={cn(
                  "w-5 h-5",
                  pathname?.startsWith("/precision-agriculture")
                    ? "text-sahool-600 dark:text-sahool-400"
                    : "text-gray-400 dark:text-gray-500",
                )}
                aria-hidden="true"
              />
              الزراعة الدقيقة
              {precisionExpanded ? (
                <ChevronDown className="w-4 h-4 mr-auto" aria-hidden="true" />
              ) : (
                <ChevronRight className="w-4 h-4 mr-auto" aria-hidden="true" />
              )}
            </button>
            {precisionExpanded && (
              <div
                id="precision-agriculture-menu"
                className="mr-4 mt-1 space-y-1"
                role="menu"
              >
                {precisionAgricultureNav.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      role="menuitem"
                      aria-current={isActive ? "page" : undefined}
                      className={cn(
                        "flex items-center gap-3 px-4 py-2 rounded-lg text-sm transition-all",
                        isActive
                          ? "bg-sahool-100 dark:bg-sahool-900/40 text-sahool-700 dark:text-sahool-300 font-medium"
                          : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100",
                      )}
                    >
                      <item.icon
                        className={cn(
                          "w-4 h-4",
                          isActive ? "text-sahool-600 dark:text-sahool-400" : "text-gray-400 dark:text-gray-500",
                        )}
                        aria-hidden="true"
                      />
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            )}
          </div>

          {/* Analytics Section */}
          <div className="pt-2">
            <button
              type="button"
              onClick={() => setAnalyticsExpanded(!analyticsExpanded)}
              aria-expanded={analyticsExpanded}
              aria-controls="analytics-menu"
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all",
                pathname?.startsWith("/analytics")
                  ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300"
                  : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100",
              )}
            >
              <TrendingUp
                className={cn(
                  "w-5 h-5",
                  pathname?.startsWith("/analytics")
                    ? "text-sahool-600 dark:text-sahool-400"
                    : "text-gray-400 dark:text-gray-500",
                )}
                aria-hidden="true"
              />
              التحليلات
              {analyticsExpanded ? (
                <ChevronDown className="w-4 h-4 mr-auto" aria-hidden="true" />
              ) : (
                <ChevronRight className="w-4 h-4 mr-auto" aria-hidden="true" />
              )}
            </button>
            {analyticsExpanded && (
              <div
                id="analytics-menu"
                className="mr-4 mt-1 space-y-1"
                role="menu"
              >
                {analyticsNav.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      role="menuitem"
                      aria-current={isActive ? "page" : undefined}
                      className={cn(
                        "flex items-center gap-3 px-4 py-2 rounded-lg text-sm transition-all",
                        isActive
                          ? "bg-sahool-100 dark:bg-sahool-900/40 text-sahool-700 dark:text-sahool-300 font-medium"
                          : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100",
                      )}
                    >
                      <item.icon
                        className={cn(
                          "w-4 h-4",
                          isActive ? "text-sahool-600 dark:text-sahool-400" : "text-gray-400 dark:text-gray-500",
                        )}
                        aria-hidden="true"
                      />
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-gray-100 dark:border-gray-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-full bg-sahool-100 dark:bg-sahool-900/50 flex items-center justify-center">
              <span className="text-sahool-700 dark:text-sahool-300 font-bold">
                {user?.name_ar?.charAt(0) || user?.name?.charAt(0) || "م"}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {user?.name_ar || user?.name || "مدير النظام"}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                {user?.email || "admin@sahool.io"}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={logout}
            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            aria-label="تسجيل الخروج"
          >
            <LogOut className="w-4 h-4" />
            تسجيل الخروج
          </button>
        </div>
      </aside>
    </>
  );
});
