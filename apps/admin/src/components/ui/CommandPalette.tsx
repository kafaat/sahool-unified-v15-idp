"use client";

/**
 * Command Palette (Cmd+K / Ctrl+K)
 * لوحة الأوامر السريعة للتنقل والبحث
 */

import React, { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Search,
  LayoutDashboard,
  MapPin,
  Bug,
  Droplets,
  Users,
  Settings,
  ShoppingCart,
  Wrench,
  Package,
  CheckSquare,
  Activity,
  Bell,
  TrendingUp,
  Sprout,
  Satellite,
  FlaskConical,
  Shield,
  MessageCircle,
  Plane,
  Mountain,
  Eye,
  Cpu,
  ClipboardList,
} from "lucide-react";

interface CommandItem {
  id: string;
  labelAr: string;
  label: string;
  href: string;
  icon: React.ElementType;
  keywords: string[];
  section: string;
}

const commands: CommandItem[] = [
  { id: "dashboard", labelAr: "لوحة التحكم", label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, keywords: ["home", "main", "رئيسية"], section: "الرئيسية" },
  { id: "farms", labelAr: "المزارع", label: "Farms", href: "/farms", icon: MapPin, keywords: ["field", "حقول", "مزرعة"], section: "العمليات" },
  { id: "diseases", labelAr: "الأمراض", label: "Diseases", href: "/diseases", icon: Bug, keywords: ["pest", "آفات", "مرض"], section: "العمليات" },
  { id: "irrigation", labelAr: "الري", label: "Irrigation", href: "/irrigation", icon: Droplets, keywords: ["water", "مياه", "سقي"], section: "العمليات" },
  { id: "tasks", labelAr: "المهام", label: "Tasks", href: "/tasks", icon: CheckSquare, keywords: ["todo", "عمل", "مهمة"], section: "العمليات" },
  { id: "sensors", labelAr: "المستشعرات", label: "Sensors", href: "/sensors", icon: Activity, keywords: ["iot", "حساس"], section: "المراقبة" },
  { id: "alerts", labelAr: "التنبيهات", label: "Alerts", href: "/alerts", icon: Bell, keywords: ["notification", "تنبيه", "إنذار"], section: "المراقبة" },
  { id: "epidemic", labelAr: "مركز الأوبئة", label: "Epidemic Center", href: "/epidemic", icon: Activity, keywords: ["outbreak", "وباء"], section: "المراقبة" },
  { id: "yield", labelAr: "الإنتاجية", label: "Yield", href: "/yield", icon: TrendingUp, keywords: ["harvest", "محصول", "إنتاج"], section: "المراقبة" },
  { id: "users", labelAr: "المستخدمين", label: "Users", href: "/users", icon: Users, keywords: ["admin", "مستخدم", "إدارة"], section: "الإدارة" },
  { id: "equipment", labelAr: "المعدات", label: "Equipment", href: "/equipment", icon: Wrench, keywords: ["machine", "آلة", "معدة"], section: "الإدارة" },
  { id: "inventory", labelAr: "المخزون", label: "Inventory", href: "/inventory", icon: Package, keywords: ["stock", "مخزن"], section: "الإدارة" },
  { id: "marketplace", labelAr: "السوق", label: "Marketplace", href: "/marketplace", icon: ShoppingCart, keywords: ["sell", "buy", "بيع", "شراء"], section: "الإدارة" },
  { id: "research", labelAr: "البحوث", label: "Research", href: "/research", icon: FlaskConical, keywords: ["study", "بحث", "تجربة"], section: "الإدارة" },
  { id: "compliance", labelAr: "الامتثال", label: "Compliance", href: "/compliance", icon: Shield, keywords: ["globalgap", "معايير"], section: "الإدارة" },
  { id: "crop-health", labelAr: "صحة المحصول", label: "Crop Health", href: "/crop-health", icon: Sprout, keywords: ["ndvi", "نبات", "صحة"], section: "الذكاء" },
  { id: "copilot", labelAr: "المساعد الذكي", label: "AI Copilot", href: "/copilot", icon: MessageCircle, keywords: ["ai", "chat", "ذكاء"], section: "الذكاء" },
  { id: "vision", labelAr: "الرؤية الحاسوبية", label: "Vision", href: "/vision", icon: Eye, keywords: ["yolo", "detect", "كشف"], section: "الذكاء" },
  { id: "drone", labelAr: "الطائرات", label: "Drones", href: "/drone", icon: Plane, keywords: ["uav", "طائرة", "مسيرة"], section: "الذكاء" },
  { id: "terrain", labelAr: "التضاريس", label: "Terrain", href: "/terrain", icon: Mountain, keywords: ["dem", "تضاريس", "ارتفاع"], section: "الذكاء" },
  { id: "edge-devices", labelAr: "أجهزة الحافة", label: "Edge Devices", href: "/edge-devices", icon: Cpu, keywords: ["jetson", "حافة", "جهاز"], section: "الذكاء" },
  { id: "satellite", labelAr: "الأقمار الصناعية", label: "Satellite", href: "/analytics/satellite", icon: Satellite, keywords: ["ndvi", "قمر", "فضاء"], section: "التحليلات" },
  { id: "audit", labelAr: "سجل التدقيق", label: "Audit Trail", href: "/audit", icon: ClipboardList, keywords: ["log", "تدقيق", "سجل"], section: "النظام" },
  { id: "settings", labelAr: "الإعدادات", label: "Settings", href: "/settings", icon: Settings, keywords: ["config", "إعداد", "تكوين"], section: "النظام" },
];

export default function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Filter commands by query
  const filteredCommands = useMemo(() => {
    if (!query.trim()) return commands;
    const q = query.toLowerCase();
    return commands.filter(
      (cmd) =>
        cmd.labelAr.includes(q) ||
        cmd.label.toLowerCase().includes(q) ||
        cmd.keywords.some((kw) => kw.includes(q)),
    );
  }, [query]);

  // Group by section
  const groupedCommands = useMemo(() => {
    const groups: Record<string, CommandItem[]> = {};
    filteredCommands.forEach((cmd) => {
      if (!groups[cmd.section]) groups[cmd.section] = [];
      groups[cmd.section]!.push(cmd);
    });
    return groups;
  }, [filteredCommands]);

  // Open/close handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
        setQuery("");
        setSelectedIndex(0);
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Focus input on open
  useEffect(() => {
    if (!isOpen) return;
    const timerId = setTimeout(() => inputRef.current?.focus(), 50);
    return () => clearTimeout(timerId);
  }, [isOpen]);

  // Navigate selection
  const handleKeyNav = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((i) => Math.min(i + 1, filteredCommands.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter" && filteredCommands[selectedIndex]) {
        e.preventDefault();
        router.push(filteredCommands[selectedIndex].href);
        setIsOpen(false);
      } else if (e.key === "Escape") {
        setIsOpen(false);
      }
    },
    [filteredCommands, selectedIndex, router],
  );

  // Scroll selected item into view
  useEffect(() => {
    const el = listRef.current?.querySelector(`[data-index="${selectedIndex}"]`);
    el?.scrollIntoView({ block: "nearest" });
  }, [selectedIndex]);

  if (!isOpen) return null;

  let flatIndex = 0;

  return (
    <div className="fixed inset-0 z-[9999]">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => setIsOpen(false)}
      />

      {/* Dialog */}
      <div className="relative max-w-lg w-full mx-auto mt-[15vh]">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden animate-scale-in">
          {/* Search Input */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
            <Search className="w-5 h-5 text-gray-400 flex-shrink-0" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setSelectedIndex(0);
              }}
              onKeyDown={handleKeyNav}
              className="flex-1 bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-400 outline-none text-sm"
              placeholder="ابحث عن صفحة أو أمر..."
              dir="auto"
              aria-label="بحث في لوحة الأوامر"
            />
            <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono text-gray-400 bg-gray-100 dark:bg-gray-700 rounded">
              ESC
            </kbd>
          </div>

          {/* Results */}
          <div
            ref={listRef}
            className="max-h-[50vh] overflow-y-auto py-2"
            role="listbox"
            aria-label="نتائج البحث"
          >
            {filteredCommands.length === 0 ? (
              <div className="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                لا توجد نتائج لـ &quot;{query}&quot;
              </div>
            ) : (
              Object.entries(groupedCommands).map(([section, items]) => (
                <div key={section}>
                  <div className="px-4 py-1.5 text-[10px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                    {section}
                  </div>
                  {items.map((cmd) => {
                    const currentIndex = flatIndex++;
                    const isSelected = currentIndex === selectedIndex;
                    const Icon = cmd.icon;

                    return (
                      <button
                        key={cmd.id}
                        data-index={currentIndex}
                        role="option"
                        aria-selected={isSelected}
                        onClick={() => {
                          router.push(cmd.href);
                          setIsOpen(false);
                        }}
                        onMouseEnter={() => setSelectedIndex(currentIndex)}
                        className={cn(
                          "w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors",
                          isSelected
                            ? "bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300"
                            : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50",
                        )}
                      >
                        <Icon
                          className={cn(
                            "w-4 h-4 flex-shrink-0",
                            isSelected
                              ? "text-sahool-600 dark:text-sahool-400"
                              : "text-gray-400",
                          )}
                        />
                        <span className="flex-1 text-right font-medium">
                          {cmd.labelAr}
                        </span>
                        <span className="text-xs text-gray-400">
                          {cmd.label}
                        </span>
                      </button>
                    );
                  })}
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-[10px] text-gray-400">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">↑↓</kbd>
                للتنقل
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">↵</kbd>
                للفتح
              </span>
            </div>
            <span className="flex items-center gap-1">
              <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">⌘K</kbd>
              للفتح/الإغلاق
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
