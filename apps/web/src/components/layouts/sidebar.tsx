"use client";
/**
 * Client (Farmer) Sidebar Navigation
 * شريط التنقل الجانبي للعميل (المزارع)
 *
 * This sidebar is for the farmer-facing web app only.
 * Admin-only features (Users, Audit, Copilot, Vision, Drone, Terrain,
 * Edge Devices, Virtual Sensors, Research, Compliance, Scouting)
 * are in the admin portal (apps/admin/).
 *
 * Modeled after John Deere Operations Center, Trimble Ag, and similar
 * agricultural platforms where farmers see only their operational tools.
 *
 * Responsive behaviour:
 * - Desktop (md+): Static sidebar visible in flex layout
 * - Mobile (<md): Hidden by default, shown as a drawer overlay via
 *   the hamburger button in Header. Parent layout passes `isOpen`
 *   and `onClose` props.
 */
import React, { useCallback, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { clsx } from "clsx";
import {
  LayoutDashboard,
  Sprout,
  FileText,
  TrendingUp,
  Settings,
  Building2,
  Package,
  Calendar,
  FileBarChart,
  Droplets,
  Satellite,
  Truck,
  AlertTriangle,
  Bell,
  X,
  MapPin,
  CloudSun,
  ListChecks,
  Wrench,
  Cpu,
  Activity,
  ShoppingCart,
  Users,
  HeartPulse,
  Wallet,
  BarChart3,
  Crosshair,
  Bot,
  HelpCircle,
} from "lucide-react";

interface NavItem {
  labelKey: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface NavGroup {
  groupKey: string;
  items: NavItem[];
}

/**
 * Client/Farmer navigation items grouped by category.
 * Only includes features relevant to farm operations.
 *
 * Removed (admin-only, available in apps/admin/):
 * - Users (إدارة المستخدمين) → admin portal
 * - Research (الأبحاث) → admin portal
 * - Compliance (الامتثال) → admin portal
 */
const navGroups: NavGroup[] = [
  {
    groupKey: "overview",
    items: [
      { labelKey: "dashboard", href: "/dashboard", icon: LayoutDashboard },
    ],
  },
  {
    groupKey: "farmManagement",
    items: [
      { labelKey: "farms", href: "/farms", icon: Building2 },
      { labelKey: "fields", href: "/fields", icon: MapPin },
      { labelKey: "crops", href: "/crops", icon: Sprout },
      { labelKey: "seasons", href: "/seasons", icon: Calendar },
      { labelKey: "inventory", href: "/inventory", icon: Package },
      { labelKey: "tasks", href: "/tasks", icon: ListChecks },
    ],
  },
  {
    groupKey: "waterAndIrrigation",
    items: [
      { labelKey: "irrigation", href: "/irrigation", icon: Droplets },
      { labelKey: "pivotIrrigation", href: "/pivot-irrigation", icon: Droplets },
    ],
  },
  {
    groupKey: "cropIntelligence",
    items: [
      { labelKey: "cropHealth", href: "/crop-health", icon: HeartPulse },
      { labelKey: "weather", href: "/weather", icon: CloudSun },
      { labelKey: "satellite", href: "/satellite", icon: Satellite },
      { labelKey: "yield", href: "/yield", icon: BarChart3 },
      { labelKey: "precisionAgriculture", href: "/precision-agriculture/gdd", icon: Crosshair },
    ],
  },
  {
    groupKey: "iotAndEquipment",
    items: [
      { labelKey: "iot", href: "/iot", icon: Cpu },
      { labelKey: "sensors", href: "/sensors", icon: Activity },
      { labelKey: "equipment", href: "/equipment", icon: Wrench },
    ],
  },
  {
    groupKey: "businessAndCommunity",
    items: [
      { labelKey: "marketplace", href: "/marketplace", icon: ShoppingCart },
      { labelKey: "wallet", href: "/wallet", icon: Wallet },
      { labelKey: "community", href: "/community", icon: Users },
      { labelKey: "logistics", href: "/logistics", icon: Truck },
    ],
  },
  {
    groupKey: "reportsAndDocs",
    items: [
      { labelKey: "reports", href: "/reports", icon: FileBarChart },
      { labelKey: "analytics", href: "/analytics", icon: TrendingUp },
      { labelKey: "documents", href: "/documents", icon: FileText },
    ],
  },
  {
    groupKey: "alertsAndNotifications",
    items: [
      { labelKey: "alerts", href: "/alerts", icon: AlertTriangle },
      { labelKey: "notifications", href: "/notifications", icon: Bell },
      { labelKey: "disasterAssessment", href: "/disaster-assessment", icon: AlertTriangle },
    ],
  },
  {
    groupKey: "tools",
    items: [
      { labelKey: "copilot", href: "/copilot", icon: Bot },
      { labelKey: "support", href: "/support", icon: HelpCircle },
      { labelKey: "settings", href: "/settings", icon: Settings },
    ],
  },
];

interface SidebarProps {
  /** Whether the mobile drawer is open (ignored on md+ viewports) */
  isOpen?: boolean;
  /** Callback to close the mobile drawer */
  onClose?: () => void;
}

export const Sidebar = React.memo(function Sidebar({
  isOpen = false,
  onClose,
}: SidebarProps) {
  const pathname = usePathname();
  const t = useTranslations("nav");
  const tCommon = useTranslations("common");

  // Close drawer when route changes (user navigated)
  useEffect(() => {
    if (isOpen && onClose) {
      onClose();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- only on pathname change
  }, [pathname]);

  // Close drawer on Escape key
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose?.();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  const handleNavClick = useCallback(() => {
    // On mobile, close drawer after clicking a link
    onClose?.();
  }, [onClose]);

  const sidebarContent = (
    <aside
      className={clsx(
        "w-64 bg-white dark:bg-gray-800 border-e border-gray-200 dark:border-gray-700 flex flex-col h-full",
      )}
      data-testid="desktop-sidebar"
      role="navigation"
      aria-label={t("mainNav")}
    >
      {/* Logo + Close button (mobile only) */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-sahool-green-600 rounded-lg flex items-center justify-center">
            <div className="w-6 h-6 bg-white rounded-full" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              {tCommon("appName")}
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">{tCommon("tagline")}</p>
          </div>
        </Link>
        {/* Close button - visible only inside mobile drawer */}
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="md:hidden p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-green-500"
            aria-label={t("closeMenu") || "Close menu"}
          >
            <X className="w-5 h-5" aria-hidden="true" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <div className="space-y-4">
          {navGroups.map((group) => (
            <div key={group.groupKey}>
              {group.groupKey !== "overview" && (
                <div className="px-4 py-1 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                  {t(group.groupKey)}
                </div>
              )}
              <ul className="space-y-0.5">
                {group.items.map((item) => {
                  const isActive =
                    pathname === item.href || pathname.startsWith(`${item.href}/`);
                  const Icon = item.icon;

                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        prefetch={false}
                        onClick={handleNavClick}
                        className={clsx(
                          "flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors",
                          "hover:bg-sahool-green-50 dark:hover:bg-gray-700 group focus:outline-none focus:ring-2 focus:ring-sahool-green-500",
                          isActive
                            ? "bg-sahool-green-100 dark:bg-sahool-green-900/30 text-sahool-green-700 dark:text-sahool-green-400 font-medium"
                            : "text-gray-700 dark:text-gray-300",
                        )}
                        aria-current={isActive ? "page" : undefined}
                        aria-label={t(item.labelKey)}
                      >
                        <Icon
                          className={clsx(
                            "w-5 h-5 flex-shrink-0",
                            isActive
                              ? "text-sahool-green-600 dark:text-sahool-green-400"
                              : "text-gray-400 group-hover:text-sahool-green-600 dark:group-hover:text-sahool-green-400",
                          )}
                          aria-hidden="true"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium">
                            {t(item.labelKey)}
                          </div>
                        </div>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          <div className="font-medium">{t("version")} 16.0.0</div>
        </div>
      </div>
    </aside>
  );

  return (
    <>
      {/* Desktop sidebar - always visible on md+ */}
      <div className="hidden md:block h-full">{sidebarContent}</div>

      {/* Mobile drawer overlay */}
      {isOpen && (
        <div className="md:hidden fixed inset-0 z-40">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/50 transition-opacity"
            onClick={onClose}
            aria-hidden="true"
            data-testid="mobile-drawer-backdrop"
          />
          {/* Drawer panel */}
          <div
            className="fixed inset-y-0 start-0 z-50 w-64 shadow-xl"
            role="dialog"
            aria-modal="true"
            aria-label={t("mainNav")}
            data-testid="mobile-drawer"
          >
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
});
